from rag.retriever import retrieve

def run_rag(query: str) -> dict:
    chunks = retrieve(query)
    return {"query": query, "chunks": chunks}