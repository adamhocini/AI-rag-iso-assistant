import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.chunker import create_chunks
from app.document_loader import load_documents
from app.vector_store import add_chunks_to_collection, get_collection_count, reset_collection


def main() -> None:
    documents_dir = PROJECT_ROOT / "data" / "documents"

    print("Chargement des documents...")
    documents = load_documents(documents_dir)

    print(f"Documents chargés : {len(documents)}")

    print("Découpage en chunks...")
    chunks = create_chunks(
        documents=documents,
        max_chars=1200,
        overlap_chars=200,
    )

    print(f"Chunks créés : {len(chunks)}")

    print("Réinitialisation de la base vectorielle...")
    reset_collection()

    print("Ajout des chunks dans ChromaDB...")
    inserted_count = add_chunks_to_collection(chunks)

    print(f"Chunks insérés : {inserted_count}")
    print(f"Chunks présents dans ChromaDB : {get_collection_count()}")

    print()
    print("Ingestion terminée avec succès.")


if __name__ == "__main__":
    main()
