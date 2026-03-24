from vector_store.embedder import embed
from vector_store.store import get_store

def retrieve(query: str, top_k: int = 3) -> list[str]:
    """
    Synchronous retrieval to match local FAISS/SentenceTransformer behavior.
    This prevents the 'coroutine never awaited' warnings.
    """
    try:
        # 1. Get and load the store
        store = get_store()
        store.load()
        
        # 2. Generate embedding (Local models are sync)
        # Ensure your embed function returns a list of vectors
        query_embeddings = embed([query])
        query_embedding = query_embeddings[0]
        
        # 3. Perform the search
        results = store.search(query_embedding, top_k=top_k)
        
        # 4. Format results as strings for the LLM
        return [str(res) for res in results]
        
    except Exception as e:
        print(f"[Retriever] Error during search: {e}")
        return []