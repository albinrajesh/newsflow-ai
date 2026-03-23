from vector_store.embedder import embed
from vector_store.store import get_store

def retrieve(query: str, top_k: int = 3) -> list[str]:
    store = get_store()
    store.load()
    query_embedding = embed([query])[0]
    return store.search(query_embedding, top_k=top_k)