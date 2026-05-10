import os
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from dotenv import load_dotenv

from app.chunker import DocumentChunk


load_dotenv()

DEFAULT_VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
COLLECTION_NAME = "iso_quality_documents"


def get_chroma_client(vector_db_path: str = DEFAULT_VECTOR_DB_PATH):
    """
    Crée un client ChromaDB persistant.

    Persistant signifie que la base vectorielle est stockée sur disque,
    dans le dossier data/vector_store.
    """

    path = Path(vector_db_path)
    path.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(path))


def reset_collection(
    collection_name: str = COLLECTION_NAME,
    vector_db_path: str = DEFAULT_VECTOR_DB_PATH,
):
    """
    Supprime puis recrée la collection ChromaDB.

    Pour le MVP, c'est pratique : à chaque ingestion,
    on repart d'une base propre pour éviter les doublons.
    """

    client = get_chroma_client(vector_db_path)

    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def get_collection(
    collection_name: str = COLLECTION_NAME,
    vector_db_path: str = DEFAULT_VECTOR_DB_PATH,
):
    """
    Récupère la collection existante, ou la crée si elle n'existe pas.
    """

    client = get_chroma_client(vector_db_path)

    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def add_chunks_to_collection(chunks: List[DocumentChunk]) -> int:
    """
    Ajoute les chunks dans ChromaDB.

    ChromaDB va transformer chaque texte en embedding,
    puis stocker :
    - l'identifiant du chunk ;
    - le texte du chunk ;
    - les métadonnées ;
    - le vecteur d'embedding.
    """

    if not chunks:
        return 0

    collection = get_collection()

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk.metadata["chunk_id"])
        documents.append(chunk.text)
        metadatas.append(chunk.metadata)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    return len(chunks)


def search_similar_chunks(
    query_text: str,
    n_results: int = 5,
) -> List[Dict[str, Any]]:
    """
    Recherche les chunks les plus proches d'une question utilisateur.
    """

    collection = get_collection()

    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    formatted_results = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        similarity_score = max(0.0, 1.0 - float(distance))

        formatted_results.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": float(distance),
                "similarity_score": similarity_score,
            }
        )

    return formatted_results


def get_collection_count() -> int:
    """
    Retourne le nombre de chunks stockés dans la collection.
    """

    collection = get_collection()
    return collection.count()
