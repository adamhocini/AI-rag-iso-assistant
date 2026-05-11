import os
from typing import Dict, List

import requests
from dotenv import load_dotenv


load_dotenv()


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")


def get_ollama_model() -> str:
    return os.getenv("OLLAMA_MODEL", "llama3.2:3b").strip()


def is_ollama_available() -> bool:
    """
    Vérifie rapidement si le service Ollama local répond.

    On interroge /api/tags, qui liste les modèles disponibles.
    """

    base_url = get_ollama_base_url()

    try:
        response = requests.get(
            f"{base_url}/api/tags",
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def build_ollama_rag_prompt(
    question: str,
    sources: List[Dict],
    extracts: List[Dict],
    alerts: List[str],
    confidence_label: str,
    confidence_score: float,
) -> str:
    """
    Construit un prompt RAG strict pour un modèle local Ollama.

    Les modèles locaux peuvent halluciner plus facilement.
    Le prompt est donc volontairement très cadré.
    """

    sources_text = []

    for source in sources:
        sources_text.append(
            f"- Référence : {source['reference']}\n"
            f"  Titre : {source['titre']}\n"
            f"  Version : {source['version']}\n"
            f"  Statut : {source['statut']}\n"
            f"  Type : {source['type_document']}\n"
            f"  Processus : {source['processus']}\n"
        )

    extracts_text = []

    for index, extract in enumerate(extracts, start=1):
        extracts_text.append(
            f"### EXTRAIT {index}\n"
            f"Référence : {extract['reference']}\n"
            f"Titre : {extract['titre']}\n"
            f"Score de similarité : {extract['similarity_score']:.3f}\n"
            f"Texte :\n{extract['text']}\n"
        )

    alerts_text = "\n".join(f"- {alert}" for alert in alerts) if alerts else "Aucune alerte documentaire détectée."

    prompt = f"""
Tu es un assistant IA RAG spécialisé dans une documentation qualité ISO fictive.

IMPORTANT :
- RAG signifie Retrieval-Augmented Generation.
- Tu ne dois pas inventer.
- Tu dois répondre uniquement à partir des extraits fournis.
- Tu ne dois pas utiliser de connaissances externes.
- Si les extraits ne permettent pas de répondre, dis : "Je ne peux pas répondre de manière fiable avec les documents disponibles."
- Cite explicitement les références documentaires utilisées.
- Si un document a un statut différent de "Validé", signale-le dans les points de vigilance.
- Ne dis jamais que l'IA remplace un auditeur ou une validation humaine.

Question utilisateur :
{question}

Niveau de confiance calculé par le système :
{confidence_label} ({confidence_score:.2f})

Sources disponibles :
{chr(10).join(sources_text) if sources_text else "Aucune source suffisamment pertinente."}

Alertes documentaires :
{alerts_text}

Extraits autorisés :
{chr(10).join(extracts_text) if extracts_text else "Aucun extrait suffisamment pertinent."}

Format de réponse obligatoire :

## Réponse synthétique
Réponds clairement à la question en quelques phrases.

## Sources utilisées
Liste les références utilisées avec leur titre.

## Points de vigilance
Mentionne les documents en révision, les limites ou les éléments à vérifier.

## Limites
Explique ce qui ne peut pas être affirmé avec certitude.
"""

    return prompt.strip()


def generate_answer_with_ollama(prompt: str) -> str:
    """
    Appelle l'API locale Ollama pour générer une réponse.
    """

    base_url = get_ollama_base_url()
    model = get_ollama_model()

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 8192
        }
    }

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        data = response.json()

        answer = data.get("response", "").strip()

        if not answer:
            raise RuntimeError("Ollama a répondu sans champ 'response' exploitable.")

        return answer

    except requests.RequestException as error:
        raise RuntimeError(f"Erreur lors de l'appel Ollama : {error}") from error
