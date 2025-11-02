from __future__ import annotations
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

import pickle

PERSIST_DIR = Path("data/embeddings")
CHROMA_DIR = PERSIST_DIR / "chroma"
FAISS_DIR = PERSIST_DIR / "faiss"
FAISS_INDEX_FILE = FAISS_DIR / "index.faiss"
FAISS_META_FILE = FAISS_DIR / "meta.pkl"


def _chunk_text(
    text: str,
    chunk_size: int = 900,
    overlap: int = 150,
    max_chunks: int = 20000,  # 安全上限，避免 OOM
) -> list[str]:
    """Robust chunker to avoid OOM or infinite loops.

    Guarantees:
    - overlap < chunk_size
    - start 单调递增
    - 命中 max_chunks 时提早停止
    """
    if not isinstance(text, str):
        # 兜底转换成字符串
        try:
            text = str(text)
        except Exception:
            text = ""

    # 负/异常参数兜底
    if chunk_size <= 0:
        chunk_size = 900
    if overlap < 0:
        overlap = 0
    if overlap >= chunk_size:
        overlap = chunk_size // 5  # 保证推进

    n = len(text)
    chunks: list[str] = []
    start = 0
    safety = 0

    while start < n and len(chunks) < max_chunks:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])

        # 计算下一段起点（确保严格前进）
        next_start = start + (chunk_size - overlap)
        if next_start <= start:  # 理论上不会发生，但保险
            next_start = start + chunk_size
        start = next_start

        safety += 1
        if safety > max_chunks + 5:  # 双保险
            break

    return chunks


def _read_file(file_obj):
    name = getattr(file_obj, "name", "upload")
    suffix = Path(name).suffix.lower()

    # PDF
    if suffix == ".pdf":
        from pypdf import PdfReader

        file_obj.seek(0)
        reader = PdfReader(file_obj)
        pages = []
        for p in reader.pages:
            txt = p.extract_text() or ""
            if isinstance(txt, bytes):
                txt = txt.decode("utf-8", errors="ignore")
            pages.append(txt)
        return "\n".join(pages), name

    # DOCX
    if suffix == ".docx":
        from docx import Document

        file_obj.seek(0)
        doc = Document(file_obj)
        return "\n".join(p.text or "" for p in doc.paragraphs), name

    # 纯文本 / 其他
    file_obj.seek(0)
    raw = file_obj.read()
    if isinstance(raw, bytes):
        try:
            text = raw.decode("utf-8")
        except Exception:
            text = raw.decode(errors="ignore")
    else:
        text = str(raw)
    return text, name


@dataclass
class VectorStoreConfig:
    backend: str = "faiss"  # "chroma" or "faiss"
    collection_name: str = "langju_docs"
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


class VectorStore:
    def __init__(self, cfg: Optional[VectorStoreConfig] = None):
        self.cfg = cfg or VectorStoreConfig()
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        # Defer heavy imports and model loading until actually needed.
        self.chroma_client = None
        self.collection = None
        self.index = None
        self.meta_list = []
        self.embedder = None  # lazy-loaded SentenceTransformer
        self._faiss_module = None  # placeholder for faiss module
        # Do not initialize backends now; initialize on demand in methods.

    # ------------------ Chroma ------------------
    def _init_chroma(self):
        # Lazy import of chromadb and embedding functions to avoid expensive
        # imports during module import; only load when chroma backend is used.
        from chromadb.utils import embedding_functions
        import chromadb

        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.cfg.model_name
        )
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.cfg.collection_name,
            embedding_function=ef,
        )

    def _chroma_add(self, texts: List[str], metadatas: List[Dict]):
        # Ensure collection initialized
        if self.collection is None:
            self._init_chroma()
        ids = [f"doc_{len(metadatas)}_{i}" for i in range(len(texts))]
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)

    def _chroma_search(self, query: str, k: int) -> List[Dict]:
        # Ensure collection initialized
        if self.collection is None:
            self._init_chroma()
        res = self.collection.query(query_texts=[query], n_results=k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        out = []
        for t, m in zip(docs, metas):
            out.append({"text": t, **(m or {})})
        return out

    # ------------------ FAISS ------------------
    def _init_faiss(self):
        # Lazy import faiss and sentence_transformers only when FAISS is used.
        import faiss
        from sentence_transformers import SentenceTransformer

        self._faiss_module = faiss
        self.embedder = SentenceTransformer(self.cfg.model_name)
        if FAISS_INDEX_FILE.exists() and FAISS_META_FILE.exists():
            self.index = faiss.read_index(str(FAISS_INDEX_FILE))
            with open(FAISS_META_FILE, "rb") as f:
                self.meta_list = pickle.load(f)
        else:
            self.index = None
            self.meta_list = []

    def _faiss_add(self, texts: List[str], metadatas: List[Dict]):
        # Ensure faiss and embedder are initialized lazily
        if self.embedder is None:
            # load embedder and faiss
            self._init_faiss()

        embs = self.embedder.encode(
            texts, convert_to_numpy=True, show_progress_bar=False
        )
        if self.index is None:
            d = embs.shape[1]
            self.index = self._faiss_module.IndexFlatIP(d)
        # normalize for cosine similarity via inner product
        self._faiss_module.normalize_L2(embs)
        self.index.add(embs)
        self.meta_list.extend([{"text": t, **m} for t, m in zip(texts, metadatas)])
        self._faiss_module.write_index(self.index, str(FAISS_INDEX_FILE))
        with open(FAISS_META_FILE, "wb") as f:
            pickle.dump(self.meta_list, f)

    def _faiss_search(self, query: str, k: int) -> List[Dict]:
        if self.index is None:
            return []
        if self.embedder is None:
            self._init_faiss()
        q = self.embedder.encode(
            [query], convert_to_numpy=True, show_progress_bar=False
        )
        self._faiss_module.normalize_L2(q)
        D, indices = self.index.search(q, min(k, len(self.meta_list)))
        idxs = indices[0].tolist()
        out = [self.meta_list[i] for i in idxs if i >= 0 and i < len(self.meta_list)]
        return out

    # ------------------ Public API ------------------
    def add_file(self, file_obj) -> None:
        text, name = _read_file(file_obj)
        chunks = _chunk_text(text)
        metas = [{"source": name, "chunk": i} for i, _ in enumerate(chunks)]
        if self.cfg.backend == "chroma":
            self._chroma_add(chunks, metas)
        else:
            self._faiss_add(chunks, metas)

    def similarity_search(self, query: str, k: int = 4) -> List[Dict]:
        if self.cfg.backend == "chroma":
            return self._chroma_search(query, k)
        return self._faiss_search(query, k)
