import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


load_dotenv()


DEFAULT_LOGS_PATH = os.getenv("LOGS_PATH", "./logs/rag_interactions.csv")


def get_log_path() -> Path:
    """
    Retourne le chemin du fichier de journalisation.
    """

    path = Path(DEFAULT_LOGS_PATH)

    if path.suffix.lower() != ".csv":
        path = path.parent / "rag_interactions.csv"

    path.parent.mkdir(parents=True, exist_ok=True)

    return path


def serialize_sources(sources: list[dict[str, Any]]) -> str:
    """
    Transforme les sources en chaîne courte exploitable dans un CSV.
    """

    if not sources:
        return ""

    return " | ".join(
        f"{source.get('reference')} v{source.get('version')} [{source.get('statut')}]"
        for source in sources
    )


def serialize_alerts(alerts: list[str]) -> str:
    """
    Transforme les alertes en chaîne CSV.
    """

    if not alerts:
        return ""

    return " | ".join(alerts)


def ensure_log_file_exists(log_path: Path) -> None:
    """
    Crée le fichier CSV avec ses en-têtes s'il n'existe pas encore.
    """

    if log_path.exists():
        return

    headers = [
        "timestamp",
        "question",
        "detected_intent",
        "detected_intent_label",
        "generation_mode",
        "confidence_label",
        "confidence_score",
        "sources",
        "alerts",
        "extract_count",
        "context_extract_count",
        "answer",
    ]

    with log_path.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()


def log_rag_interaction(response: Any) -> Path:
    """
    Journalise une interaction RAG.
    """

    log_path = get_log_path()
    ensure_log_file_exists(log_path)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "question": response.question,
        "detected_intent": response.detected_intent,
        "detected_intent_label": response.detected_intent_label,
        "generation_mode": response.generation_mode,
        "confidence_label": response.confidence_label,
        "confidence_score": f"{response.confidence_score:.2f}",
        "sources": serialize_sources(response.sources),
        "alerts": serialize_alerts(response.alerts),
        "extract_count": len(response.relevant_extracts),
        "context_extract_count": len(response.context_extracts),
        "answer": response.answer.replace("\n", " ").strip(),
    }

    with log_path.open(mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())
        writer.writerow(row)

    return log_path
