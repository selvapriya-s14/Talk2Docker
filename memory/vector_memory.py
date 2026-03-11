from pathlib import Path
from typing import List, Tuple
import pickle
import faiss
import numpy as np


class VectorMemory:
    """FAISS-backed vector memory with metadata storage."""

    def __init__(self, index_path: Path, meta_path: Path):
        self.index_path = index_path
        self.meta_path = meta_path
        self.index = None
        self.texts: List[str] = []

    def save(self) -> None:
        if self.index is None:
            return
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.texts, f)

    def load(self) -> bool:
        if not self.index_path.exists() or not self.meta_path.exists():
            return False
        self.index = faiss.read_index(str(self.index_path))
        with open(self.meta_path, "rb") as f:
            self.texts = pickle.load(f)
        return True

    def build(self, embeddings: np.ndarray, texts: List[str]) -> None:
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.texts = texts

    def search(self, query_embedding: np.ndarray, top_k: int) -> List[str]:
        if self.index is None:
            return []
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.texts):
                continue
            results.append(self.texts[idx])
        return results
