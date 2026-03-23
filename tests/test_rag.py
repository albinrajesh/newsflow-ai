from ingestion.ingest import ingest_file
from rag.pipeline import run_rag

def test_rag_returns_chunks():
    ingest_file()
    result = run_rag("What is retrieval augmented generation?")
    assert "chunks" in result
    assert len(result["chunks"]) > 0
    assert isinstance(result["chunks"][0], str)