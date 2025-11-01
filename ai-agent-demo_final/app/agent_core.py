import yaml
from .models.model_wrapper import ModelWrapper
from .memory.short_term import ShortTermMemory
from .memory.vector_store import VectorStore, VectorStoreConfig
from .tools.web_search import web_search_tool

with open("app/config/settings.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

memory = ShortTermMemory()
# Lazy-initialize VectorStore to avoid heavy imports and model downloads at module
# import time (helps tests and CI where FAISS/sentence-transformers may be absent).
_vstore = None


def get_vstore() -> VectorStore:
    global _vstore
    if _vstore is None:
        cfg = VectorStoreConfig(
            backend=CFG.get("rag", {}).get("vector_db", "faiss"),
            collection_name=CFG.get("rag", {}).get("collection_name", "langju_docs"),
        )
        _vstore = VectorStore(cfg)
    return _vstore


def get_response(query: str, backend: str = "openai") -> str:
    # 1) Retrieve context from Vector DB
    vstore = get_vstore()
    docs = vstore.similarity_search(query, k=CFG.get("rag", {}).get("top_k", 4))
    context = "\n\n".join([d.get("text", "") for d in docs])

    # 2) Build system prompt
    system = (
        "You are LangJu's AI Research Assistant. "
        "Use the provided CONTEXT when relevant. "
        "Be concise, structured, and explain which tool or context you used."
    )

    # 3) Optional tool
    if "search " in query.lower() or "google" in query.lower():
        snippet = web_search_tool(query)
        context += f"\n\n[WEB_SEARCH]\n{snippet}"

    # 4) Call model
    model = ModelWrapper(backend=backend)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"},
    ]
    answer = model.chat(messages)

    # 5) Save to memory
    memory.add({"user": query, "assistant": answer})
    return answer


def load_document_into_knowledgebase(file_obj) -> None:
    vstore = get_vstore()
    vstore.add_file(file_obj)
