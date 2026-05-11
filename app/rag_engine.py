from dataclasses import dataclass
from typing import Any, Dict, List

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
DEFAULT_TOP_K = 5


@dataclass
class RagResponse:
    """
    Représente une réponse RAG structurée.
    """

    question: str
    answer: str
    sources: List[Dict[str, Any]]
    relevant_extracts: List[Dict[str, Any]]
    alerts: List[str]
    limitations: List[str]
    confidence_label: str
    confidence_score: float
    generation_mode: str


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


def build_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Construit une liste de sources uniques à partir des chunks retrouvés.
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
            }
        else:
            current_best = unique_sources[reference]["best_similarity_score"]
            unique_sources[reference]["best_similarity_score"] = max(
                current_best,
                result["similarity_score"],
            )

    return list(unique_sources.values())


def build_extracts(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prépare les extraits pertinents à afficher à l'utilisateur.
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

    Modes disponibles :
    - sans LLM ;
    - OpenAI API ;
    - Ollama local.
    """

    raw_results = search_similar_chunks(
        query_text=question,
        n_results=top_k,
    )

    relevant_results = filter_relevant_results(
        results=raw_results,
        min_score=min_score,
    )

    sources = build_sources(relevant_results)
    extracts = build_extracts(relevant_results)
    alerts = detect_document_alerts(sources)

    confidence_score, confidence_label = compute_simple_confidence(
        relevant_results=relevant_results,
        sources=sources,
        alerts=alerts,
    )

    limitations = [
        "Le score de confiance est approximatif dans cette version MVP.",
        "Les extraits doivent être validés par un humain avant usage en audit réel.",
        "L'assistant ne remplace pas un auditeur, un responsable qualité ou une validation documentaire officielle.",
    ]

    generation_mode = "sans_llm"

    if use_ollama and relevant_results:
        if is_ollama_available():
            prompt = build_ollama_rag_prompt(
                question=question,
                sources=sources,
                extracts=extracts,
                alerts=alerts,
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

    elif use_openai and relevant_results:
        if is_openai_configured():
            prompt = build_rag_prompt(
                question=question,
                sources=sources,
                extracts=extracts,
                alerts=alerts,
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
        alerts=alerts,
        limitations=limitations,
        confidence_label=confidence_label,
        confidence_score=confidence_score,
        generation_mode=generation_mode,
    )
