import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag_engine import ask_rag


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Quels documents prouvent qu'un audit interne a été réalisé ?"

    response = ask_rag(question)

    print_section("Question")
    print(response.question)

    print_section("Réponse")
    print(response.answer)

    print_section("Niveau de confiance")
    print(f"{response.confidence_label} ({response.confidence_score:.2f})")

    print_section("Sources utilisées")

    if not response.sources:
        print("Aucune source suffisamment pertinente.")
    else:
        for index, source in enumerate(response.sources, start=1):
            print(
                f"{index}. {source['reference']} - {source['titre']} "
                f"| v{source['version']} "
                f"| {source['statut']} "
                f"| {source['type_document']} "
                f"| score max : {source['best_similarity_score']:.3f}"
            )

    print_section("Extraits pertinents")

    if not response.relevant_extracts:
        print("Aucun extrait suffisamment pertinent.")
    else:
        for index, extract in enumerate(response.relevant_extracts, start=1):
            print()
            print(
                f"Extrait {index} | {extract['reference']} "
                f"| score : {extract['similarity_score']:.3f} "
                f"| chunk : {extract['chunk_id']}"
            )
            print("-" * 80)
            print(extract["text"][:900].replace("\n", " "))

    print_section("Alertes")

    if not response.alerts:
        print("Aucune alerte documentaire détectée.")
    else:
        for alert in response.alerts:
            print(f"- {alert}")

    print_section("Limites de la réponse")

    for limitation in response.limitations:
        print(f"- {limitation}")


if __name__ == "__main__":
    main()
