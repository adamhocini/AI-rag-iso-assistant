import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.consistency_checker import (
    detect_version_mentions,
    detect_version_inconsistencies,
)


def main() -> None:
    sample_text = (
        "Le compte rendu mentionne la fiche processus achats "
        "FP-ACH-001 version 1.0, alors que la version actuelle est différente."
    )

    print("Test détection des mentions de version")
    print("--------------------------------------")
    mentions = detect_version_mentions(sample_text)
    print(mentions)

    print()
    print("Test détection des incohérences")
    print("-------------------------------")

    fake_results = [
        {
            "metadata": {
                "reference": "CR-AUD-2025-001",
                "version": "1.0",
            },
            "text": sample_text,
        },
        {
            "metadata": {
                "reference": "FP-ACH-001",
                "version": "1.1",
            },
            "text": "# Fiche processus achats",
        },
    ]

    alerts = detect_version_inconsistencies(fake_results)

    if not alerts:
        print("Aucune alerte détectée.")
    else:
        for alert in alerts:
            print(f"- {alert}")


if __name__ == "__main__":
    main()
