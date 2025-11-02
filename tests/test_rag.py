from io import BytesIO
from app.agent_core import load_document_into_knowledgebase, get_response


def test_ingest_and_ask():
    bio = BytesIO(b"LangJu is building an AI Agent demo. It supports RAG.")
    bio.name = "note.txt"
    load_document_into_knowledgebase(bio)
    out = get_response("What is this project about?", backend="openai")
    assert isinstance(out, str)
