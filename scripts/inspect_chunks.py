import sys
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.document_loader import load_documents
from app.chunker import create_chunks


def main() -> None:
    documents_dir = PROJECT_ROOT / "data" / "documents"

    documents = load_documents(documents_dir)

    chunks = create_chunks(
        documents=documents,
        max_chars=1200,
        overlap_chars=200,
    )

    print(f"Nombre de documents chargés : {len(documents)}")
    print(f"Nombre total de chunks      : {len(chunks)}")
    print()

    chunks_by_reference = Counter(
        chunk.metadata["reference"]
        for chunk in chunks
    )

    print("Nombre de chunks par document :")
    print("--------------------------------")

    for reference, count in sorted(chunks_by_reference.items()):
        print(f"- {reference} : {count} chunk(s)")

    print()
    print("Exemple de chunk :")
    print("------------------")

    first_chunk = chunks[0]

    print(f"Chunk ID    : {first_chunk.metadata['chunk_id']}")
    print(f"Document    : {first_chunk.metadata['reference']} - {first_chunk.metadata['titre']}")
    print(f"Version     : {first_chunk.metadata['version']}")
    print(f"Statut      : {first_chunk.metadata['statut']}")
    print(f"Processus   : {first_chunk.metadata['processus']}")
    print(f"Fichier     : {first_chunk.metadata['source_file']}")
    print(f"Taille      : {len(first_chunk.text)} caractères")
    print()

    print("Texte du chunk :")
    print("----------------")
    print(first_chunk.text[:1000])


if __name__ == "__main__":
    main()
