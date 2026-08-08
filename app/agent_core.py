from collections.abc import Mapping
from pathlib import Path
from typing import Literal, TypedDict
import unicodedata

import yaml

from .memory.short_term import ShortTermMemory
from .memory.vector_store import VectorStore, VectorStoreConfig
from .models.model_wrapper import ModelWrapper
from .tools.web_search import web_search_tool


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "config" / "settings.yaml"

with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

memory = ShortTermMemory()
# Lazy-initialize VectorStore to avoid heavy imports and model downloads at module
# import time (helps tests and CI where FAISS/sentence-transformers may be absent).
_vstore = None


class SourceRef(TypedDict):
    source: str
    chunk: int


GroundingStatus = Literal[
    "verified_sources",
    "incomplete_lineage",
    "no_verified_sources",
]


class ResearchResponse(TypedDict):
    answer: str
    sources: list[SourceRef]
    grounding_status: GroundingStatus
    warnings: list[str]


class _VerifiedEvidence(TypedDict):
    text: str
    source: str
    chunk: int


INVALID_LINEAGE_WARNING = (
    "Some retrieved context was excluded because its source lineage was incomplete."
)
IDENTITY_COLLISION_WARNING = (
    "Some retrieved context was excluded because a source identity matched "
    "conflicting content."
)
WEB_CONTEXT_WARNING = (
    "Web search context is unverified and is not included in verified sources."
)
NO_VERIFIED_SOURCES_WARNING = (
    "No verified document sources were available for this response."
)


def get_vstore() -> VectorStore:
    global _vstore
    if _vstore is None:
        cfg = VectorStoreConfig(
            backend=CFG.get("rag", {}).get("vector_db", "faiss"),
            collection_name=CFG.get("rag", {}).get("collection_name", "langju_docs"),
        )
        _vstore = VectorStore(cfg)
    return _vstore


def _normalize_source_name(source: object) -> str | None:
    if not isinstance(source, str):
        return None

    basename = source.replace("\\", "/").rsplit("/", 1)[-1]
    safe_name = "".join(
        character
        for character in basename
        if not (
            ord(character) <= 0x1F
            or 0x7F <= ord(character) <= 0x9F
            or unicodedata.category(character) == "Cf"
        )
    )
    safe_name = " ".join(safe_name.split()).strip()[:120].strip()
    return safe_name or None


def _normalize_retrieval_records(
    records: object,
) -> tuple[list[_VerifiedEvidence], list[str], bool]:
    candidates: list[_VerifiedEvidence] = []
    warnings: list[str] = []
    seen_evidence: set[tuple[str, int, str]] = set()
    incomplete_lineage = False

    if not isinstance(records, list):
        records = []

    for record in records:
        if not isinstance(record, Mapping):
            continue

        text = record.get("text")
        if not isinstance(text, str):
            continue

        normalized_text = text.strip()
        if not normalized_text:
            continue

        source = _normalize_source_name(record.get("source"))
        chunk = record.get("chunk")
        valid_chunk = isinstance(chunk, int) and not isinstance(chunk, bool) and chunk >= 0
        if source is None or not valid_chunk:
            incomplete_lineage = True
            if INVALID_LINEAGE_WARNING not in warnings:
                warnings.append(INVALID_LINEAGE_WARNING)
            continue

        evidence_key = (source, chunk, normalized_text)
        if evidence_key in seen_evidence:
            continue
        seen_evidence.add(evidence_key)
        candidates.append(
            {"text": normalized_text, "source": source, "chunk": chunk}
        )

    texts_by_public_key: dict[tuple[str, int], set[str]] = {}
    for evidence in candidates:
        public_key = (evidence["source"], evidence["chunk"])
        texts_by_public_key.setdefault(public_key, set()).add(evidence["text"])

    collision_keys = {
        key for key, texts in texts_by_public_key.items() if len(texts) > 1
    }
    if collision_keys:
        incomplete_lineage = True
        warnings.append(IDENTITY_COLLISION_WARNING)

    verified = [
        evidence
        for evidence in candidates
        if (evidence["source"], evidence["chunk"]) not in collision_keys
    ]
    return verified, warnings, incomplete_lineage


def _run_research_request(query: str, backend: str) -> ResearchResponse:
    vstore = get_vstore()
    docs = vstore.similarity_search(query, k=CFG.get("rag", {}).get("top_k", 4))
    evidence, warnings, incomplete_lineage = _normalize_retrieval_records(docs)
    context = "\n\n".join(item["text"] for item in evidence)

    # 2) Build system prompt
    system = (
        "You are LangJu's AI Research Assistant. "
        "Use the provided CONTEXT when relevant. "
        "Be concise, structured, and explain which tool or context you used."
    )

    lowered_query = query.lower()
    trigger_search = "search " in lowered_query or "google" in lowered_query
    if trigger_search:
        snippet = web_search_tool(query)
        context += f"\n\n[WEB_SEARCH]\n{snippet}"
        incomplete_lineage = True
        warnings.append(WEB_CONTEXT_WARNING)

    # 4) Call model
    model = ModelWrapper(backend=backend)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION:\n{query}"},
    ]
    answer = model.chat(messages)

    memory.add({"user": query, "assistant": answer})

    sources: list[SourceRef] = [
        {"source": item["source"], "chunk": item["chunk"]} for item in evidence
    ]
    if incomplete_lineage:
        grounding_status: GroundingStatus = "incomplete_lineage"
    elif sources:
        grounding_status = "verified_sources"
    else:
        grounding_status = "no_verified_sources"
        warnings.append(NO_VERIFIED_SOURCES_WARNING)

    return {
        "answer": answer,
        "sources": sources,
        "grounding_status": grounding_status,
        "warnings": warnings,
    }


def get_structured_response(
    query: str,
    backend: str = "openai",
) -> ResearchResponse:
    return _run_research_request(query, backend)


def get_response(query: str, backend: str = "openai") -> str:
    return _run_research_request(query, backend)["answer"]


def load_document_into_knowledgebase(file_obj) -> None:
    vstore = get_vstore()
    vstore.add_file(file_obj)
    ##
