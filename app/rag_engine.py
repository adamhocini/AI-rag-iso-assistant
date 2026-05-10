from dataclasses import dataclass
from typing import Any, Dict, List

from app.vector_store import search_similar_chunks


MIN_RELEVANCE_SCORE = 0.45
DEFAULT_TOP_K = 5


@dataclass
class RagResponse:
    """
    Représente une réponse RAG structurée.

    Pour l'instant, la réponse est générée sans LLM.
    Elle s'appuie uniquement sur les chunks retrouvés.
    """

    question: str
    answer: str
    sources: List[Dict[str, Any]]
    relevant_extracts: List[Dict[str, Any]]
    alerts: List[str]
    limitations: List[str]
    confidence_label: str
    confidence_score: float


def filter_relevant_results(
    results: List[Dict[str, Any]],
    min_score: float = MIN_RELEVANCE_SCORE,
) -> List[Dict[str, Any]]:
    """
    Conserve uniquement les résultats suffisamment proches de la question.

    Le seuil est volontairement simple pour le MVP.
    """

    return [
        result for result in results
        if result["similarity_score"] >= min_score
    ]


def build_sources(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Construit une liste de sources uniques à partir des chunks retrouvés.

    Plusieurs chunks peuvent venir du même document.
    On évite donc d'afficher 3 fois la même source.
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

    Pour le MVP, on vérifie surtout le statut documentaire.
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

    Le score prend en compte :
    - le meilleur score de similarité ;
    - la moyenne des similarités ;
    - le nombre de sources distinctes ;
    - le statut des documents ;
    - la présence d'alertes documentaires.

    Le but n'est pas d'obtenir une vérité mathématique,
    mais un indicateur lisible pour un utilisateur métier.
    """

    if not relevant_results:
        return 0.0, "Très faible"

    similarity_scores = [
        result["similarity_score"]
        for result in relevant_results
    ]

    best_score = max(similarity_scores)
    average_score = sum(similarity_scores) / len(similarity_scores)

    # Base principale : pertinence documentaire
    confidence_score = (best_score * 0.65) + (average_score * 0.25)

    # Bonus limité si plusieurs sources distinctes confirment la réponse
    if len(sources) >= 3:
        confidence_score += 0.07
    elif len(sources) == 2:
        confidence_score += 0.04
    elif len(sources) == 1:
        confidence_score += 0.02

    # Pénalité si certains documents ne sont pas validés
    non_validated_sources = [
        source for source in sources
        if source["statut"].lower() != "validé"
    ]

    confidence_score -= min(len(non_validated_sources) * 0.12, 0.30)

    # Pénalité supplémentaire en cas d'alerte documentaire
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
    question: str,
    relevant_results: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    alerts: List[str],
) -> str:
    """
    Génère une réponse simple sans LLM.

    Cette réponse n'est pas encore rédigée de manière intelligente.
    Elle sert à vérifier que le pipeline RAG fonctionne.
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
) -> RagResponse:
    """
    Point d'entrée principal du moteur RAG.

    1. Recherche les chunks proches de la question.
    2. Filtre les résultats faibles.
    3. Construit les sources.
    4. Détecte les alertes.
    5. Calcule un score de confiance simple.
    6. Produit une réponse structurée sans LLM.
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

    limitations = [
        "Cette réponse est générée sans LLM pour valider le pipeline RAG.",
        "Le score de confiance est approximatif dans cette version MVP.",
        "Les extraits doivent être validés par un humain avant usage en audit réel.",
    ]

    confidence_score, confidence_label = compute_simple_confidence(
        relevant_results=relevant_results,
        sources=sources,
        alerts=alerts,
    )

    answer = build_answer_without_llm(
        question=question,
        relevant_results=relevant_results,
        sources=sources,
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
    )
