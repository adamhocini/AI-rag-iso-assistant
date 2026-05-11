import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()


def is_openai_configured() -> bool:
    """
    Vérifie si une clé OpenAI est disponible.

    On garde cette vérification pour éviter que l'application plante
    si l'utilisateur n'a pas encore configuré sa clé.
    """

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(api_key)


def build_rag_prompt(
    question: str,
    sources: List[Dict],
    extracts: List[Dict],
    alerts: List[str],
    confidence_label: str,
    confidence_score: float,
) -> str:
    """
    Construit le prompt envoyé au LLM.

    Le prompt impose des règles strictes :
    - répondre uniquement avec les extraits fournis ;
    - citer les références documentaires ;
    - signaler les limites ;
    - ne pas inventer si les sources sont insuffisantes.
    """

    sources_text = []

    for source in sources:
        sources_text.append(
            f"- {source['reference']} | {source['titre']} | "
            f"version {source['version']} | statut {source['statut']} | "
            f"type {source['type_document']} | processus {source['processus']}"
        )

    extracts_text = []

    for index, extract in enumerate(extracts, start=1):
        extracts_text.append(
            f"[EXTRAIT {index}]\n"
            f"Référence : {extract['reference']}\n"
            f"Titre : {extract['titre']}\n"
            f"Score de similarité : {extract['similarity_score']:.3f}\n"
            f"Texte :\n{extract['text']}\n"
        )

    alerts_text = "\n".join(f"- {alert}" for alert in alerts) if alerts else "Aucune alerte détectée."

    prompt = f"""
Tu es un assistant IA spécialisé dans l'analyse d'une documentation qualité ISO fictive.

Règles obligatoires :
1. Réponds uniquement à partir des sources et extraits fournis.
2. Ne complète pas avec des connaissances externes.
3. Si les sources ne permettent pas de répondre, dis clairement que la réponse n'est pas fiable.
4. Cite les références documentaires utilisées, par exemple PROC-AUD-001 ou CR-AUD-2025-001.
5. Mentionne les alertes documentaires si un document est en révision, obsolète ou non validé.
6. N'affirme jamais qu'une IA remplace un auditeur ou une validation humaine.
7. Structure ta réponse avec les sections :
   - Réponse synthétique
   - Sources utilisées
   - Points de vigilance
   - Limites

Question utilisateur :
{question}

Niveau de confiance calculé par le système :
{confidence_label} ({confidence_score:.2f})

Sources disponibles :
{chr(10).join(sources_text) if sources_text else "Aucune source suffisamment pertinente."}

Alertes documentaires :
{alerts_text}

Extraits documentaires :
{chr(10).join(extracts_text) if extracts_text else "Aucun extrait suffisamment pertinent."}
"""

    return prompt.strip()


def generate_answer_with_openai(prompt: str) -> str:
    """
    Appelle l'API OpenAI pour générer une réponse.

    Le modèle est configurable avec OPENAI_MODEL dans .env.
    """

    if not is_openai_configured():
        raise RuntimeError(
            "OPENAI_API_KEY est vide. La génération LLM est désactivée."
        )

    model = os.getenv("OPENAI_MODEL", "gpt-5.5").strip()

    client = OpenAI()

    try:
        response = client.responses.create(
            model=model,
            input=prompt,
        )

        return response.output_text.strip()

    except OpenAIError as error:
        raise RuntimeError(f"Erreur lors de l'appel OpenAI : {error}") from error
