from io import BytesIO

import pytest

from app.agent_core import get_response, get_vstore, load_document_into_knowledgebase


pytestmark = pytest.mark.integration


def test_ingest_and_ask():
    bio = BytesIO(b"LangJu is building an AI Agent demo. It supports RAG.")
    bio.name = "note.txt"
    load_document_into_knowledgebase(bio)
    docs = get_vstore().similarity_search("LangJu AI Agent RAG", k=4)
    assert docs
    assert all(isinstance(doc.get("text"), str) and doc["text"].strip() for doc in docs)
    assert all(isinstance(doc.get("source"), str) and doc["source"] for doc in docs)
    assert all(
        isinstance(doc.get("chunk"), int) and not isinstance(doc["chunk"], bool)
        for doc in docs
    )
    assert any(doc["chunk"] == 0 for doc in docs)
    out = get_response("What is this project about?", backend="openai")
    assert isinstance(out, str)
