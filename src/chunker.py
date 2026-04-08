from dataclasses import dataclass

from src.loader import Document


@dataclass
class Chunk:
    text: str
    metadata: dict


def split_text(document: Document, chunk_size: int = 500, overlap: int = 100) -> list[Chunk]:
    text = document.content
    if not text:
        return []

    if len(text) <= chunk_size:
        return [Chunk(text=text, metadata={"source_url": document.url, "chunk_index": 0})]

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]

        chunks.append(Chunk(
            text=chunk_text,
            metadata={"source_url": document.url, "chunk_index": index},
        ))

        start += chunk_size - overlap
        index += 1

    return chunks
