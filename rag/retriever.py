from pathlib import Path
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from memory.vector_memory import VectorMemory


class Retriever:
    """Retrieve relevant Docker docs from FAISS."""

    def __init__(self, doc_dir: Path, memory_dir: Path):
        self.doc_dir = doc_dir
        self.memory_dir = memory_dir
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.memory = VectorMemory(memory_dir / "docker.index", memory_dir / "docker.meta")
        self._ensure_index()

    def _ensure_index(self) -> None:
        if self.memory.load():
            return
        from rag.ingest_docs import ingest
        ingest(self.doc_dir, self.memory_dir)
        self.memory.load()

    def retrieve(self, query: str, top_k: int = 4) -> List[str]:
        embedding = self.model.encode([query], convert_to_numpy=True)
        return self.memory.search(np.array(embedding), top_k)
