import asyncio
import numpy as np
from vector_store.embedder import embed
from vector_store.store import get_store

class VectorService:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.store = get_store()

    async def reload(self):
        async with self.lock:
            self.store.load()

    async def add_documents(self, chunks: list[str]):
        async with self.lock:
            # Re-load to make sure we have the latest version before adding
            self.store.load()
            
            embeddings = embed(chunks)
            if isinstance(embeddings, list):
                embeddings = np.array(embeddings)
            
            self.store.add_chunks(chunks, embeddings)
            self.store.save()
            # Force a re-load to ensure singleton instance index is fully synced
            self.store.load()

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        try:
            # Always ensure store is loaded before search to avoid staleness
            self.store.load()
            
            query_embeddings = embed([query])
            query_embedding = np.array(query_embeddings[0])
            
            results = self.store.search(query_embedding, top_k=top_k)
            return [str(res) for res in results]
        except Exception as e:
            print(f"[Retriever] Error during search: {e}")
            return []

vector_service = VectorService()

def retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    Synchronous retrieval matching original local behavior, routed via singleton.
    """
    return vector_service.retrieve(query, top_k)