from pathlib import Path
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from memory.vector_memory import VectorMemory


def load_documents(doc_dir: Path) -> List[str]:
    texts: List[str] = []
    for path in doc_dir.rglob("*.txt"):
        texts.append(path.read_text(encoding="utf-8"))
    return texts


def split_texts(texts: List[str], chunk_size: int = 800) -> List[str]:
    chunks: List[str] = []
    for text in texts:
        start = 0
        while start < len(text):
            chunks.append(text[start : start + chunk_size])
            start += chunk_size
    return chunks


def ingest(doc_dir: Path, memory_dir: Path) -> None:
    docs = load_documents(doc_dir)
    chunks = split_texts(docs)
    if not chunks:
        raise RuntimeError("No documents found to ingest.")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, convert_to_numpy=True)

    index_path = memory_dir / "docker.index"
    meta_path = memory_dir / "docker.meta"
    memory = VectorMemory(index_path, meta_path)
    memory.build(np.array(embeddings), chunks)
    memory.save()


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    ingest(base / "rag" / "docker_docs", base / "memory")
