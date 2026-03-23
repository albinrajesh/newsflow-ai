from ingestion.chunker import chunk_text

def test_chunker_basic():
    text = " ".join(["word"] * 700)
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(c.split()) <= 300 for c in chunks)

def test_chunker_overlap():
    text = " ".join([str(i) for i in range(400)])
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    
    # chunk 2 should start at word 250 (300 - 50 overlap)
    second_chunk_start = int(chunks[1].split()[0])
    assert second_chunk_start == 250

    # chunk 2 should contain words from the end of chunk 1
    chunk1_words = set(chunks[0].split())
    chunk2_words = set(chunks[1].split())
    overlap_words = chunk1_words & chunk2_words
    assert len(overlap_words) == 50  # exactly 50 words overlap