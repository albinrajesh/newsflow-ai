import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(texts: list[str]) -> np.ndarray:
    return model.encode(texts, convert_to_numpy=True)