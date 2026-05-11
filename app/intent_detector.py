from typing import Dict, List


INTENT_GENERAL = "question_generale"
INTENT_DOCUMENT_VALIDITY = "validite_documentaire"
INTENT_AUDIT_EVIDENCE = "preuve_audit"
INTENT_AUDIT_CHECKLIST = "checklist_audit"
INTENT_BUSINESS_PROCEDURE = "procedure_metier"
INTENT_INCONSISTENCY = "incoherence_documentaire"


INTENT_LABELS = {
    INTENT_GENERAL: "Question générale",
    INTENT_DOCUMENT_VALIDITY: "Validité documentaire",
    INTENT_AUDIT_EVIDENCE: "Preuve d'audit",
    INTENT_AUDIT_CHECKLIST: "Checklist d'audit",
    INTENT_BUSINESS_PROCEDURE: "Procédure métier",
    INTENT_INCONSISTENCY: "Incohérence documentaire",
}


INTENT_KEYWORDS: Dict[str, List[str]] = {
    INTENT_DOCUMENT_VALIDITY: [
        "valide",
        "validité",
        "validé",
        "encore valide",
        "applicable",
        "obsolète",
        "en révision",
        "version",
        "date de validation",
        "à jour",
        "mise à jour",
    ],
    INTENT_AUDIT_EVIDENCE: [
        "prouve",
        "preuve",
        "preuves",
        "audit réalisé",
        "audit interne réalisé",
        "documents prouvent",
        "éléments prouvent",
        "compte rendu",
        "constats",
        "documents consultés",
    ],
    INTENT_AUDIT_CHECKLIST: [
        "checklist",
        "check-list",
        "liste de contrôle",
        "prépare une checklist",
        "préparer une checklist",
        "points de contrôle",
        "audit du processus",
        "auditer",
    ],
    INTENT_INCONSISTENCY: [
        "incohérence",
        "incohérences",
        "contradiction",
        "contradictions",
        "écart entre",
        "différence entre",
        "pas cohérent",
        "version différente",
        "conflit",
    ],
    INTENT_BUSINESS_PROCEDURE: [
        "procédure",
        "comment gérer",
        "comment traiter",
        "gestion des non-conformités",
        "non-conformité",
        "non conformités",
        "risques",
        "gestion documentaire",
        "processus achats",
    ],
}


def normalize_question(question: str) -> str:
    """
    Normalise simplement la question pour faciliter la détection par mots-clés.
    """

    return question.lower().strip()


def detect_intent(question: str) -> str:
    """
    Détecte une intention simple à partir de mots-clés.

    Cette approche est volontairement simple pour le MVP.
    Elle n'utilise pas de LLM afin de rester explicable et déterministe.
    """

    normalized_question = normalize_question(question)

    # Ordre important :
    # Certaines questions contiennent le mot "procédure",
    # mais l'intention peut être la validité ou l'incohérence.
    priority_order = [
        INTENT_INCONSISTENCY,
        INTENT_DOCUMENT_VALIDITY,
        INTENT_AUDIT_CHECKLIST,
        INTENT_AUDIT_EVIDENCE,
        INTENT_BUSINESS_PROCEDURE,
    ]

    for intent in priority_order:
        keywords = INTENT_KEYWORDS[intent]

        for keyword in keywords:
            if keyword in normalized_question:
                return intent

    return INTENT_GENERAL


def get_intent_label(intent: str) -> str:
    """
    Retourne un libellé lisible pour l'utilisateur.
    """

    return INTENT_LABELS.get(intent, INTENT_LABELS[INTENT_GENERAL])


def get_intent_context_preferences(intent: str) -> Dict[str, List[str]]:
    """
    Retourne des préférences documentaires simples selon l'intention.

    Ces préférences servent à ajuster la sélection des chunks envoyés au LLM.
    """

    if intent == INTENT_DOCUMENT_VALIDITY:
        return {
            "required_references": [
                "PROC-RISK-001",
                "PROC-DOC-001",
            ],
            "preferred_references": [
                "PROC-DOC-001",
                "REG-AC-001",
            ],
            "preferred_types": [
                "Procédure",
                "Registre",
                "Manuel qualité",
            ],
            "preferred_terms": [
                "statut",
                "validé",
                "validation",
                "révision",
                "obsolète",
                "applicable",
                "version",
                "date de validation",
            ],
        }

    if intent == INTENT_AUDIT_EVIDENCE:
        return {
            "required_references": [
                "CR-AUD-2025-001",
                "PROC-AUD-001",
            ],
            "preferred_references": [
                "CR-AUD-2025-001",
                "PROC-AUD-001",
                "REG-AC-001",
            ],
            "preferred_types": [
                "Compte rendu d'audit",
                "Procédure",
                "Registre",
            ],
            "preferred_terms": [
                "audit",
                "preuve",
                "preuves",
                "compte rendu",
                "documents consultés",
                "constats",
                "actions correctives",
            ],
        }

    if intent == INTENT_AUDIT_CHECKLIST:
        return {
            "required_references": [
                "PROC-AUD-001",
                "FP-ACH-001",
            ],
            "preferred_references": [
                "PROC-AUD-001",
                "FP-ACH-001",
                "PROC-NC-001",
                "REG-AC-001",
            ],
            "preferred_types": [
                "Procédure",
                "Fiche processus",
                "Registre",
            ],
            "preferred_terms": [
                "checklist",
                "points de contrôle",
                "preuves attendues",
                "documents applicables",
                "audit",
                "processus achats",
            ],
        }

    if intent == INTENT_INCONSISTENCY:
        return {
            "required_references": [
                "CR-AUD-2025-001",
                "FP-ACH-001",
            ],
            "preferred_references": [
                "CR-AUD-2025-001",
                "FP-ACH-001",
                "REG-AC-001",
                "PROC-DOC-001",
            ],
            "preferred_types": [
                "Compte rendu d'audit",
                "Fiche processus",
                "Registre",
                "Procédure",
            ],
            "preferred_terms": [
                "version",
                "différence",
                "alerte",
                "écart",
                "en révision",
                "en retard",
                "non disponible",
                "obsolète",
            ],
        }

    if intent == INTENT_BUSINESS_PROCEDURE:
        return {
            "required_references": [],
            "preferred_references": [
                "PROC-NC-001",
                "PROC-DOC-001",
                "PROC-RISK-001",
                "PROC-AUD-001",
                "FP-ACH-001",
            ],
            "preferred_types": [
                "Procédure",
                "Fiche processus",
                "Manuel qualité",
            ],
            "preferred_terms": [
                "objet",
                "traitement",
                "responsable",
                "clôture",
                "preuve",
                "documents associés",
            ],
        }

    return {
        "required_references": [],
        "preferred_references": [],
        "preferred_types": [],
        "preferred_terms": [],
    }
