import hashlib

import chromadb

from src.chunker import Chunk


class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "claude_docs"):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chunks(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = hashlib.sha256(
                f"{chunk.metadata['source_url']}_{chunk.metadata['chunk_index']}".encode()
            ).hexdigest()
            ids.append(chunk_id)
            documents.append(chunk.text)
            metadatas.append(chunk.metadata)

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if self.collection.count() == 0:
            return []

        results = self.collection.query(query_texts=[query], n_results=min(top_k, self.collection.count()))

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return output

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
