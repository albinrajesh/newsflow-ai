import faiss
import numpy as np
import os

class FAISSStore:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.chunks: list[str] = []

    def add_chunks(self, chunks: list[str], embeddings: np.ndarray):
        self.index.add(embeddings.astype("float32"))
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> list[str]:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(
            query_embedding.astype("float32").reshape(1, -1), top_k
        )
        return [self.chunks[i] for i in indices[0] if i < len(self.chunks)]

    def save(self, path: str = "vector_store/index.faiss"):
        faiss.write_index(self.index, path)
        np.save(path + ".chunks.npy", np.array(self.chunks))

    def load(self, path: str = "vector_store/index.faiss"):
        if os.path.exists(path):
            self.index = faiss.read_index(path)
            self.chunks = np.load(
                path + ".chunks.npy", allow_pickle=True
            ).tolist()

# Global singleton
_store = FAISSStore()

def get_store() -> FAISSStore:
    return _store