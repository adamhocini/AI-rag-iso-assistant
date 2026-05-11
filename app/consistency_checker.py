import re
from typing import Any, Dict, List


DOCUMENT_REFERENCE_PATTERN = re.compile(
    r"\\b([A-Z]{2,}-[A-Z]+-\\d{3}|[A-Z]{2}-[A-Z]{3}-\\d{4}-\\d{3}|[A-Z]{2}-\\d{3})\\b"
)

VERSION_MENTION_PATTERN = re.compile(
    r"\\b([A-Z]{2,}-[A-Z]+-\\d{3}|[A-Z]{2}-[A-Z]{3}-\\d{4}-\\d{3}|[A-Z]{2}-\\d{3})\\s+(?:en\\s+)?version\\s+([0-9]+(?:\\.[0-9]+)?)\\b",
    re.IGNORECASE,
)


def build_reference_version_index(results: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Construit un index des versions actuelles connues à partir des métadonnées.

    Exemple :
    {
        "FP-ACH-001": "1.1",
        "PROC-AUD-001": "1.0"
    }
    """

    index = {}

    for result in results:
        metadata = result.get("metadata", {})
        reference = metadata.get("reference")
        version = metadata.get("version")

        if reference and version:
            index[reference] = version

    return index


def detect_version_mentions(text: str) -> List[Dict[str, str]]:
    """
    Détecte les mentions explicites de version dans un texte.

    Exemple détecté :
    FP-ACH-001 version 1.0
    """

    mentions = []

    for match in VERSION_MENTION_PATTERN.finditer(text):
        reference = match.group(1).upper()
        mentioned_version = match.group(2)

        mentions.append(
            {
                "reference": reference,
                "mentioned_version": mentioned_version,
                "matched_text": match.group(0),
            }
        )

    return mentions


def detect_version_inconsistencies(
    relevant_results: List[Dict[str, Any]],
) -> List[str]:
    """
    Détecte les incohérences simples de version.

    On compare :
    - une version mentionnée dans un extrait ;
    - la version actuelle connue dans les métadonnées indexées.

    Cette version MVP fonctionne uniquement si le document de référence
    est présent dans les résultats pertinents.
    """

    version_index = build_reference_version_index(relevant_results)
    alerts = []
    seen_alerts = set()

    for result in relevant_results:
        source_metadata = result.get("metadata", {})
        source_reference = source_metadata.get("reference", "Source inconnue")
        text = result.get("text", "")

        mentions = detect_version_mentions(text)

        for mention in mentions:
            referenced_document = mention["reference"]
            mentioned_version = mention["mentioned_version"]
            current_version = version_index.get(referenced_document)

            if not current_version:
                continue

            if mentioned_version != current_version:
                alert = (
                    f"Incohérence de version détectée : l'extrait issu de "
                    f"{source_reference} mentionne {referenced_document} "
                    f"en version {mentioned_version}, alors que la version "
                    f"actuelle indexée est {current_version}."
                )

                if alert not in seen_alerts:
                    alerts.append(alert)
                    seen_alerts.add(alert)

    return alerts
