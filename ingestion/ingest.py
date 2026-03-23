from ingestion.chunker import chunk_text
from vector_store.embedder import embed
from vector_store.store import get_store

def ingest_file(path: str = "ingestion/sample_data/sample.txt"):
    with open(path, "r") as f:
        text = f.read()

    chunks = chunk_text(text)
    embeddings = embed(chunks)
    store = get_store()
    store.add_chunks(chunks, embeddings)
    store.save()
    print(f"Ingestion complete — {len(chunks)} chunks stored")

if __name__ == "__main__":
    ingest_file()