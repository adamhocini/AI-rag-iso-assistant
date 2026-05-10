import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.vector_store import search_similar_chunks


def main() -> None:
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Quels documents prouvent qu'un audit interne a été réalisé ?"

    print(f"Question : {query}")
    print()

    results = search_similar_chunks(
        query_text=query,
        n_results=5,
    )

    if not results:
        print("Aucun résultat trouvé.")
        return

    print("Chunks les plus proches :")
    print("-------------------------")

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print(f"\nRésultat {index}")
        print(f"Score similarité : {result['similarity_score']:.3f}")
        print(f"Distance         : {result['distance']:.3f}")
        print(f"Chunk ID         : {result['chunk_id']}")
        print(f"Document         : {metadata['reference']} - {metadata['titre']}")
        print(f"Version          : {metadata['version']}")
        print(f"Statut           : {metadata['statut']}")
        print(f"Type             : {metadata['type_document']}")
        print(f"Processus        : {metadata['processus']}")
        print()
        print("Extrait :")
        print(result["text"][:700].replace("\n", " "))
        print("-" * 80)


if __name__ == "__main__":
    main()
