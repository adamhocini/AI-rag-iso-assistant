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

    Objectif :
    - limiter les hallucinations ;
    - éviter les formulations trop catégoriques ;
    - imposer la citation des sources ;
    - respecter les statuts documentaires.
    """

    sources_text = []

    for source in sources:
        sources_text.append(
            f"- Référence : {source['reference']}\n"
            f"  Titre : {source['titre']}\n"
            f"  Version : {source['version']}\n"
            f"  Statut : {source['statut']}\n"
            f"  Date de validation : {source['date_validation']}\n"
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
Tu es un assistant IA RAG spécialisé dans l'analyse d'une documentation qualité ISO fictive.

CONTEXTE :
- RAG signifie Retrieval-Augmented Generation.
- Tu aides à analyser des documents qualité fictifs.
- Tu ne remplaces jamais un auditeur, un responsable qualité ou une validation humaine.

RÈGLES ABSOLUES :
1. Réponds uniquement avec les sources et extraits fournis.
2. N'utilise aucune connaissance externe.
3. N'invente aucun document, aucune référence, aucune date, aucune preuve.
4. Si les extraits ne suffisent pas, dis clairement ce qui manque.
5. Cite les références exactes utilisées, par exemple PROC-AUD-001 ou CR-AUD-2025-001.
6. Ne cite pas une source si elle n'aide pas réellement à répondre à la question.
7. Ne donne jamais un niveau de certitude supérieur au niveau calculé par le système.
8. Ne dis jamais que l'IA remplace une validation humaine.

RÈGLES SUR LES STATUTS DOCUMENTAIRES :
- Un document au statut "Validé" peut être utilisé comme source applicable dans le cadre du PoC.
- Un document au statut "En révision" peut être consulté, mais ne doit pas être présenté comme pleinement applicable.
- Un document au statut "En révision" ne doit PAS être décrit comme "obsolète", "invalide" ou "non valide", sauf si un extrait le dit explicitement.
- Formulation correcte pour un document "En révision" :
  "Le document est en révision ; il ne doit pas être utilisé comme seule référence applicable sans validation humaine."
- Si une contradiction de version est mentionnée dans les extraits, signale-la comme point de vigilance.

STYLE DE RÉPONSE :
- Réponds en français.
- Sois clair, précis et prudent.
- Ne sois pas trop long.
- Ne répète pas tous les extraits.
- Préfère une réponse métier exploitable.
- Utilise des puces si cela améliore la lisibilité.

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

FORMAT DE RÉPONSE OBLIGATOIRE :

## Réponse synthétique
Réponds directement à la question à partir des extraits.

## Sources utilisées
Liste uniquement les références réellement utilisées avec leur titre.

## Points de vigilance
Mentionne :
- les documents en révision ;
- les contradictions de version ;
- les preuves manquantes ;
- les limites d'interprétation.

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
            "temperature": 0.1,
            "top_p": 0.8,
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
