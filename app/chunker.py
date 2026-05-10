from dataclasses import dataclass
from typing import Dict, List

from app.document_loader import QualityDocument


@dataclass
class DocumentChunk:
    """
    Représente un morceau de document prêt à être indexé dans une base vectorielle.

    text     : contenu textuel du chunk
    metadata : métadonnées du document d'origine + informations du chunk
    """

    text: str
    metadata: Dict[str, str]


def normalize_text(text: str) -> str:
    """
    Nettoie légèrement le texte sans modifier le sens du document.
    """

    lines = [line.rstrip() for line in text.splitlines()]
    cleaned_text = "\n".join(lines).strip()

    return cleaned_text


def split_into_paragraphs(text: str) -> List[str]:
    """
    Découpe le texte en paragraphes simples.

    On utilise les lignes vides comme séparation logique.
    """

    paragraphs = []

    for block in text.split("\n\n"):
        block = block.strip()

        if block:
            paragraphs.append(block)

    return paragraphs


def get_overlap_text(text: str, overlap_chars: int) -> str:
    """
    Récupère la fin d'un chunk pour créer un chevauchement avec le chunk suivant.
    """

    if overlap_chars <= 0:
        return ""

    if len(text) <= overlap_chars:
        return text

    return text[-overlap_chars:].strip()


def chunk_text(
    text: str,
    max_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[str]:
    """
    Découpe un texte en chunks.

    La stratégie est volontairement simple pour le MVP :
    - on découpe d'abord en paragraphes ;
    - on regroupe les paragraphes jusqu'à atteindre max_chars ;
    - on ajoute un overlap pour conserver le contexte entre deux chunks.
    """

    if max_chars <= 0:
        raise ValueError("max_chars doit être supérieur à 0.")

    if overlap_chars < 0:
        raise ValueError("overlap_chars ne peut pas être négatif.")

    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars doit être inférieur à max_chars.")

    normalized_text = normalize_text(text)
    paragraphs = split_into_paragraphs(normalized_text)

    chunks = []
    current_parts = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        if paragraph_length > max_chars:
            if current_parts:
                chunk = "\n\n".join(current_parts).strip()
                chunks.append(chunk)

                overlap = get_overlap_text(chunk, overlap_chars)
                current_parts = [overlap] if overlap else []
                current_length = len(overlap)

            start = 0

            while start < paragraph_length:
                end = start + max_chars
                part = paragraph[start:end].strip()

                if part:
                    chunks.append(part)

                start = end - overlap_chars

            current_parts = []
            current_length = 0

            continue

        projected_length = current_length + paragraph_length + 2

        if current_parts and projected_length > max_chars:
            chunk = "\n\n".join(current_parts).strip()
            chunks.append(chunk)

            overlap = get_overlap_text(chunk, overlap_chars)
            current_parts = [overlap] if overlap else []
            current_length = len(overlap)

        current_parts.append(paragraph)
        current_length += paragraph_length + 2

    if current_parts:
        chunk = "\n\n".join(current_parts).strip()
        chunks.append(chunk)

    return chunks


def create_chunks_for_document(
    document: QualityDocument,
    max_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[DocumentChunk]:
    """
    Crée les chunks d'un document qualité en conservant ses métadonnées.
    """

    raw_chunks = chunk_text(
        text=document.content,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )

    document_chunks = []
    chunk_total = len(raw_chunks)

    for index, chunk in enumerate(raw_chunks, start=1):
        metadata = document.metadata.copy()

        chunk_id = f"{metadata['reference']}::chunk_{index:03d}"

        metadata["chunk_id"] = chunk_id
        metadata["chunk_index"] = str(index)
        metadata["chunk_total"] = str(chunk_total)

        document_chunks.append(
            DocumentChunk(
                text=chunk,
                metadata=metadata,
            )
        )

    return document_chunks


def create_chunks(
    documents: List[QualityDocument],
    max_chars: int = 1200,
    overlap_chars: int = 200,
) -> List[DocumentChunk]:
    """
    Crée les chunks pour une liste complète de documents.
    """

    all_chunks = []

    for document in documents:
        document_chunks = create_chunks_for_document(
            document=document,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )

        all_chunks.extend(document_chunks)

    return all_chunks
