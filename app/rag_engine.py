from dataclasses import dataclass
from typing import Any, Dict, List

from app.consistency_checker import detect_version_inconsistencies

from app.intent_detector import (
    detect_intent,
    get_intent_context_preferences,
    get_intent_label,
)
from app.llm_client import (
    build_rag_prompt,
    generate_answer_with_openai,
    is_openai_configured,
)
from app.ollama_client import (
    build_ollama_rag_prompt,
    generate_answer_with_ollama,
    is_ollama_available,
)
from app.vector_store import search_similar_chunks


MIN_RELEVANCE_SCORE = 0.45
DEFAULT_TOP_K = 6
MAX_CONTEXT_CHUNKS = 3
CONTEXT_SCORE_MARGIN = 0.12


@dataclass
class RagResponse:
    """
    Représente une réponse RAG structurée.
    """

    question: str
    answer: str
    sources: List[Dict[str, Any]]
    relevant_extracts: List[Dict[str, Any]]
    context_extracts: List[Dict[str, Any]]
    alerts: List[str]
    limitations: List[str]
    confidence_label: str
    confidence_score: float
    generation_mode: str
    detected_intent: str
    detected_intent_label: str


def filter_relevant_results(
    results: List[Dict[str, Any]],
    min_score: float = MIN_RELEVANCE_SCORE,
) -> List[Dict[str, Any]]:
    """
    Conserve uniquement les résultats suffisamment proches de la question.
    """

    return [
        result for result in results
        if result["similarity_score"] >= min_score
    ]


def compute_intent_bonus(
    result: Dict[str, Any],
    intent_preferences: Dict[str, List[str]],
) -> float:
    """
    Calcule un petit bonus métier selon l'intention détectée.

    Ce bonus n'écrase pas le score vectoriel.
    Il sert seulement à départager des chunks proches.
    """

    metadata = result["metadata"]
    text = result["text"].lower()

    bonus = 0.0

    if metadata.get("reference") in intent_preferences.get("preferred_references", []):
        bonus += 0.08

    if metadata.get("type_document") in intent_preferences.get("preferred_types", []):
        bonus += 0.04

    preferred_terms = intent_preferences.get("preferred_terms", [])

    matched_terms = [
        term for term in preferred_terms
        if term.lower() in text
    ]

    bonus += min(len(matched_terms) * 0.015, 0.06)

    return min(bonus, 0.16)


def add_intent_adjusted_scores(
    results: List[Dict[str, Any]],
    detected_intent: str,
) -> List[Dict[str, Any]]:
    """
    Ajoute un score ajusté par intention à chaque résultat.
    """

    intent_preferences = get_intent_context_preferences(detected_intent)

    adjusted_results = []

    for result in results:
        result_copy = result.copy()
        intent_bonus = compute_intent_bonus(result_copy, intent_preferences)
        adjusted_score = result_copy["similarity_score"] + intent_bonus

        result_copy["intent_bonus"] = intent_bonus
        result_copy["adjusted_score"] = min(adjusted_score, 1.0)

        adjusted_results.append(result_copy)

    return adjusted_results


def select_context_results(
    relevant_results: List[Dict[str, Any]],
    detected_intent: str,
    max_context_chunks: int = MAX_CONTEXT_CHUNKS,
    score_margin: float = CONTEXT_SCORE_MARGIN,
) -> List[Dict[str, Any]]:
    """
    Sélectionne les chunks réellement envoyés au LLM.

    La sélection utilise :
    - le score vectoriel ;
    - un bonus simple selon l'intention détectée ;
    - des références obligatoires selon certains cas métier.

    Exemple :
    pour une preuve d'audit, on veut inclure si possible :
    - CR-AUD-2025-001, car c'est la preuve métier ;
    - PROC-AUD-001, car c'est la règle d'audit.
    """

    if not relevant_results:
        return []

    intent_preferences = get_intent_context_preferences(detected_intent)
    required_references = intent_preferences.get("required_references", [])

    adjusted_results = add_intent_adjusted_scores(
        results=relevant_results,
        detected_intent=detected_intent,
    )

    sorted_results = sorted(
        adjusted_results,
        key=lambda result: result["adjusted_score"],
        reverse=True,
    )

    selected_results = []

    # 1. Inclure d'abord les références requises si elles existent
    for required_reference in required_references:
        matching_results = [
            result for result in sorted_results
            if result["metadata"]["reference"] == required_reference
        ]

        if matching_results:
            best_match = max(
                matching_results,
                key=lambda result: result["adjusted_score"],
            )

            if best_match not in selected_results:
                selected_results.append(best_match)

    # 2. Compléter avec les meilleurs résultats ajustés
    best_adjusted_score = sorted_results[0]["adjusted_score"]
    min_context_score = max(
        MIN_RELEVANCE_SCORE,
        best_adjusted_score - score_margin,
    )

    for result in sorted_results:
        if len(selected_results) >= max_context_chunks:
            break

        if result in selected_results:
            continue

        if result["adjusted_score"] >= min_context_score:
            selected_results.append(result)

    # 3. Si le contexte est encore vide ou trop faible, ajouter le meilleur résultat
    if not selected_results and sorted_results:
        selected_results.append(sorted_results[0])

    return selected_results[:max_context_chunks]


def build_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Construit une liste de sources uniques à partir des chunks fournis.
    """

    unique_sources = {}

    for result in results:
        metadata = result["metadata"]
        reference = metadata["reference"]

        if reference not in unique_sources:
            unique_sources[reference] = {
                "reference": metadata["reference"],
                "titre": metadata["titre"],
                "version": metadata["version"],
                "statut": metadata["statut"],
                "date_validation": metadata["date_validation"],
                "proprietaire": metadata["proprietaire"],
                "processus": metadata["processus"],
                "type_document": metadata["type_document"],
                "source_file": metadata["source_file"],
                "best_similarity_score": result["similarity_score"],
                "best_adjusted_score": result.get("adjusted_score", result["similarity_score"]),
                "intent_bonus": result.get("intent_bonus", 0.0),
            }
        else:
            current_best = unique_sources[reference]["best_similarity_score"]
            current_best_adjusted = unique_sources[reference]["best_adjusted_score"]

            unique_sources[reference]["best_similarity_score"] = max(
                current_best,
                result["similarity_score"],
            )

            unique_sources[reference]["best_adjusted_score"] = max(
                current_best_adjusted,
                result.get("adjusted_score", result["similarity_score"]),
            )

            unique_sources[reference]["intent_bonus"] = max(
                unique_sources[reference]["intent_bonus"],
                result.get("intent_bonus", 0.0),
            )

    return list(unique_sources.values())


def build_extracts(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prépare les extraits à afficher ou à transmettre au LLM.
    """

    extracts = []

    for result in results:
        metadata = result["metadata"]

        extracts.append(
            {
                "chunk_id": result["chunk_id"],
                "reference": metadata["reference"],
                "titre": metadata["titre"],
                "similarity_score": result["similarity_score"],
                "adjusted_score": result.get("adjusted_score", result["similarity_score"]),
                "intent_bonus": result.get("intent_bonus", 0.0),
                "text": result["text"],
            }
        )

    return extracts


def detect_document_alerts(sources: List[Dict[str, Any]]) -> List[str]:
    """
    Détecte des alertes documentaires simples.
    """

    alerts = []

    for source in sources:
        statut = source["statut"].lower()
        reference = source["reference"]
        titre = source["titre"]

        if statut != "validé":
            alerts.append(
                f"Attention : le document {reference} - {titre} a le statut "
                f"'{source['statut']}'. Il ne doit pas être utilisé comme seule "
                "référence applicable sans validation humaine."
            )

    return alerts


def compute_simple_confidence(
    relevant_results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    alerts: List[str],
) -> tuple[float, str]:
    """
    Calcule un score de confiance simple et prudent.
    """

    if not relevant_results:
        return 0.0, "Très faible"

    similarity_scores = [
        result["similarity_score"]
        for result in relevant_results
    ]

    best_score = max(similarity_scores)
    average_score = sum(similarity_scores) / len(similarity_scores)

    confidence_score = (best_score * 0.65) + (average_score * 0.25)

    if len(sources) >= 3:
        confidence_score += 0.07
    elif len(sources) == 2:
        confidence_score += 0.04
    elif len(sources) == 1:
        confidence_score += 0.02

    non_validated_sources = [
        source for source in sources
        if source["statut"].lower() != "validé"
    ]

    confidence_score -= min(len(non_validated_sources) * 0.12, 0.30)
    confidence_score -= min(len(alerts) * 0.08, 0.20)

    confidence_score = max(0.0, min(confidence_score, 0.95))

    if confidence_score >= 0.75:
        label = "Élevé"
    elif confidence_score >= 0.55:
        label = "Moyen"
    elif confidence_score >= 0.35:
        label = "Faible"
    else:
        label = "Très faible"

    return confidence_score, label


def build_answer_without_llm(
    relevant_results: List[Dict[str, Any]],
    alerts: List[str],
) -> str:
    """
    Génère une réponse simple sans LLM.
    """

    if not relevant_results:
        return (
            "Je ne peux pas répondre de manière fiable avec les documents "
            "disponibles. Aucun extrait suffisamment pertinent n'a été trouvé."
        )

    top_result = relevant_results[0]
    top_metadata = top_result["metadata"]

    answer_parts = []

    answer_parts.append(
        "J'ai trouvé des éléments documentaires pertinents dans le corpus qualité."
    )

    answer_parts.append(
        f"La source la plus pertinente est {top_metadata['reference']} - "
        f"{top_metadata['titre']}."
    )

    if top_metadata["statut"].lower() != "validé":
        answer_parts.append(
            f"Cependant, ce document a le statut '{top_metadata['statut']}', "
            "ce qui impose une validation humaine avant de l'utiliser comme "
            "référence applicable."
        )

    answer_parts.append(
        "Les extraits affichés ci-dessous doivent être utilisés comme base de "
        "réponse, mais cette version ne réalise pas encore de synthèse avancée "
        "par LLM."
    )

    if alerts:
        answer_parts.append(
            "Une ou plusieurs alertes documentaires ont été détectées."
        )

    return " ".join(answer_parts)


def ask_rag(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    min_score: float = MIN_RELEVANCE_SCORE,
    use_openai: bool = False,
    use_ollama: bool = False,
) -> RagResponse:
    """
    Point d'entrée principal du moteur RAG.
    """

    detected_intent = detect_intent(question)
    detected_intent_label = get_intent_label(detected_intent)

    raw_results = search_similar_chunks(
        query_text=question,
        n_results=top_k,
    )

    relevant_results = filter_relevant_results(
        results=raw_results,
        min_score=min_score,
    )

    context_results = select_context_results(
        relevant_results=relevant_results,
        detected_intent=detected_intent,
    )

    sources = build_sources(
        add_intent_adjusted_scores(
            results=relevant_results,
            detected_intent=detected_intent,
        )
    )

    context_sources = build_sources(context_results)

    extracts = build_extracts(
        add_intent_adjusted_scores(
            results=relevant_results,
            detected_intent=detected_intent,
        )
    )

    context_extracts = build_extracts(context_results)

    document_alerts = detect_document_alerts(sources)
    version_alerts = detect_version_inconsistencies(relevant_results)
    alerts = document_alerts + version_alerts

    context_document_alerts = detect_document_alerts(context_sources)
    context_version_alerts = detect_version_inconsistencies(context_results)
    context_alerts = context_document_alerts + context_version_alerts

    confidence_score, confidence_label = compute_simple_confidence(
        relevant_results=relevant_results,
        sources=sources,
        alerts=alerts,
    )

    limitations = [
        "Le score de confiance est approximatif dans cette version MVP.",
        "Les extraits doivent être validés par un humain avant usage en audit réel.",
        "L'assistant ne remplace pas un auditeur, un responsable qualité ou une validation documentaire officielle.",
        f"Intention détectée : {detected_intent_label}.",
        f"{len(context_extracts)} extrait(s) ont été transmis au générateur sur {len(extracts)} extrait(s) pertinent(s) affiché(s).",
    ]

    generation_mode = "sans_llm"

    if use_ollama and context_results:
        if is_ollama_available():
            prompt = build_ollama_rag_prompt(
                question=question,
                sources=context_sources,
                extracts=context_extracts,
                alerts=context_alerts,
                confidence_label=confidence_label,
                confidence_score=confidence_score,
            )

            try:
                answer = generate_answer_with_ollama(prompt)
                generation_mode = "ollama"
            except RuntimeError as error:
                answer = (
                    build_answer_without_llm(
                        relevant_results=relevant_results,
                        alerts=alerts,
                    )
                    + f" Génération Ollama indisponible : {error}"
                )
                limitations.append("La génération Ollama a échoué, réponse sans LLM utilisée.")
        else:
            answer = build_answer_without_llm(
                relevant_results=relevant_results,
                alerts=alerts,
            )
            limitations.append(
                "La génération Ollama a été demandée, mais le service Ollama local ne répond pas."
            )

    elif use_openai and context_results:
        if is_openai_configured():
            prompt = build_rag_prompt(
                question=question,
                sources=context_sources,
                extracts=context_extracts,
                alerts=context_alerts,
                confidence_label=confidence_label,
                confidence_score=confidence_score,
            )

            try:
                answer = generate_answer_with_openai(prompt)
                generation_mode = "openai"
            except RuntimeError as error:
                answer = (
                    build_answer_without_llm(
                        relevant_results=relevant_results,
                        alerts=alerts,
                    )
                    + f" Génération OpenAI indisponible : {error}"
                )
                limitations.append("La génération OpenAI a échoué, réponse sans LLM utilisée.")
        else:
            answer = build_answer_without_llm(
                relevant_results=relevant_results,
                alerts=alerts,
            )
            limitations.append(
                "La génération OpenAI a été demandée, mais OPENAI_API_KEY n'est pas configurée."
            )

    else:
        answer = build_answer_without_llm(
            relevant_results=relevant_results,
            alerts=alerts,
        )

    return RagResponse(
        question=question,
        answer=answer,
        sources=sources,
        relevant_extracts=extracts,
        context_extracts=context_extracts,
        alerts=alerts,
        limitations=limitations,
        confidence_label=confidence_label,
        confidence_score=confidence_score,
        generation_mode=generation_mode,
        detected_intent=detected_intent,
        detected_intent_label=detected_intent_label,
    )
