import re
from typing import Any, Dict, List


# Références documentaires acceptées dans notre corpus fictif :
# - MQ-001
# - FP-ACH-001
# - REG-AC-001
# - PROC-DOC-001
# - PROC-AUD-001
# - PROC-NC-001
# - PROC-RISK-001
# - CR-AUD-2025-001
DOCUMENT_REFERENCE_REGEX = r"(?:MQ-\d{3}|FP-[A-Z]+-\d{3}|REG-[A-Z]+-\d{3}|PROC-[A-Z]+-\d{3}|CR-[A-Z]+-\d{4}-\d{3})"

VERSION_MENTION_PATTERN = re.compile(
    rf"\b({DOCUMENT_REFERENCE_REGEX})\s+(?:en\s+)?version\s+([0-9]+(?:\.[0-9]+)?)\b",
    re.IGNORECASE,
)


def normalize_reference(reference: str) -> str:
    """
    Normalise une référence documentaire.
    """

    return reference.strip().upper()


def normalize_version(version: str) -> str:
    """
    Normalise une version documentaire.
    """

    return version.strip()


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
            index[normalize_reference(reference)] = normalize_version(version)

    return index


def detect_version_mentions(text: str) -> List[Dict[str, str]]:
    """
    Détecte les mentions explicites de version dans un texte.

    Exemple détecté :
    FP-ACH-001 version 1.0
    FP-ACH-001 en version 1.0
    """

    mentions = []

    for match in VERSION_MENTION_PATTERN.finditer(text):
        reference = normalize_reference(match.group(1))
        mentioned_version = normalize_version(match.group(2))

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

    Limite actuelle :
    la version actuelle doit être présente dans les résultats analysés.
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
