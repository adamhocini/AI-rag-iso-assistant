import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.logger import log_rag_interaction
from app.rag_engine import ask_rag


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def parse_arguments() -> tuple[str, bool, bool, bool]:
    """
    Récupère la question et détecte les options.
    """

    args = sys.argv[1:]

    use_ollama = "--ollama" in args
    use_openai = "--llm" in args
    no_log = "--no-log" in args

    args = [
        arg for arg in args
        if arg not in ["--ollama", "--llm", "--no-log"]
    ]

    if args:
        question = " ".join(args)
    else:
        question = "Quels documents prouvent qu'un audit interne a été réalisé ?"

    return question, use_openai, use_ollama, no_log


def format_generation_mode(mode: str) -> str:
    if mode == "ollama":
        return "Réponse générée avec Ollama local."
    if mode == "openai":
        return "Réponse générée avec OpenAI API."
    return "Réponse générée sans LLM."


def main() -> None:
    question, use_openai, use_ollama, no_log = parse_arguments()

    if use_openai and use_ollama:
        print("Erreur : utilise soit --llm, soit --ollama, mais pas les deux en même temps.")
        sys.exit(1)

    response = ask_rag(
        question=question,
        use_openai=use_openai,
        use_ollama=use_ollama,
    )

    if not no_log:
        log_path = log_rag_interaction(response)
    else:
        log_path = None

    print_section("Question")
    print(response.question)

    print_section("Intention détectée")
    print(f"{response.detected_intent_label} ({response.detected_intent})")

    print_section("Mode de génération")
    print(format_generation_mode(response.generation_mode))

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
                f"| score : {source['best_similarity_score']:.3f} "
                f"| score ajusté : {source.get('best_adjusted_score', source['best_similarity_score']):.3f} "
                f"| bonus intention : {source.get('intent_bonus', 0.0):.3f}"
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
                f"| score ajusté : {extract.get('adjusted_score', extract['similarity_score']):.3f} "
                f"| bonus intention : {extract.get('intent_bonus', 0.0):.3f} "
                f"| chunk : {extract['chunk_id']}"
            )
            print("-" * 80)
            print(extract["text"][:900].replace("\n", " "))

    print_section("Extraits envoyés au LLM")

    if not response.context_extracts:
        print("Aucun extrait transmis au générateur.")
    else:
        for index, extract in enumerate(response.context_extracts, start=1):
            print(
                f"{index}. {extract['reference']} "
                f"| score : {extract['similarity_score']:.3f} "
                f"| score ajusté : {extract.get('adjusted_score', extract['similarity_score']):.3f} "
                f"| bonus intention : {extract.get('intent_bonus', 0.0):.3f} "
                f"| chunk : {extract['chunk_id']}"
            )

    print_section("Alertes")

    if not response.alerts:
        print("Aucune alerte documentaire détectée.")
    else:
        for alert in response.alerts:
            print(f"- {alert}")

    print_section("Limites de la réponse")

    for limitation in response.limitations:
        print(f"- {limitation}")

    print_section("Journalisation")

    if log_path:
        print(f"Interaction enregistrée dans : {log_path}")
    else:
        print("Journalisation désactivée pour cette exécution.")


if __name__ == "__main__":
    main()
