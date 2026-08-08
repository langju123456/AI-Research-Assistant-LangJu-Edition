from collections.abc import Mapping
import sys
from pathlib import Path
import unicodedata
# flake8: noqa: E402

# Ensure repository root is on sys.path so `import app...` works when this file
# is executed directly (Streamlit runs scripts as __main__). This prevents
# ModuleNotFoundError: No module named 'app' in environments where the
# current working directory isn't the project root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent_core import get_structured_response, load_document_into_knowledgebase


RESEARCH_RESPONSE_KEYS = {
    "answer",
    "sources",
    "grounding_status",
    "warnings",
}
GROUNDING_STATUSES = {
    "verified_sources",
    "incomplete_lineage",
    "no_verified_sources",
}


def _is_safe_source_name(source: object) -> bool:
    if not isinstance(source, str) or not source or len(source) > 120:
        return False
    if source != " ".join(source.split()).strip() or "/" in source or "\\" in source:
        return False
    return not any(
        ord(character) <= 0x1F
        or 0x7F <= ord(character) <= 0x9F
        or unicodedata.category(character) == "Cf"
        for character in source
    )


def _is_structured_response(payload: object) -> bool:
    if not isinstance(payload, Mapping) or set(payload) != RESEARCH_RESPONSE_KEYS:
        return False
    if not isinstance(payload["answer"], str):
        return False
    if (
        not isinstance(payload["grounding_status"], str)
        or payload["grounding_status"] not in GROUNDING_STATUSES
    ):
        return False
    if not isinstance(payload["warnings"], list) or not all(
        isinstance(warning, str) for warning in payload["warnings"]
    ):
        return False
    if not isinstance(payload["sources"], list):
        return False
    return all(
        isinstance(source, Mapping)
        and set(source) == {"source", "chunk"}
        and _is_safe_source_name(source["source"])
        and isinstance(source["chunk"], int)
        and not isinstance(source["chunk"], bool)
        and source["chunk"] >= 0
        for source in payload["sources"]
    )


def render_payload(st, role: str, payload: object) -> None:
    if isinstance(payload, str):
        st.write(payload)
        return

    if role != "assistant" or not _is_structured_response(payload):
        st.text("Unsupported message payload.")
        return

    st.write(payload["answer"])
    st.text(f"Grounding status: {payload['grounding_status']}")
    if payload["sources"]:
        st.text("Sources made available to the model:")
        for source in payload["sources"]:
            st.text(f"- {source['source']} (chunk {source['chunk']})")
    for warning in payload["warnings"]:
        st.text(f"Warning: {warning}")


def render_history(st, history: list[tuple[str, object]]) -> None:
    for role, payload in history:
        with st.chat_message(role):
            render_payload(st, role, payload)


def submit_query(
    history: list[tuple[str, object]],
    query: str,
    backend: str,
):
    history.append(("user", query))
    response = get_structured_response(query, backend=backend)
    history.append(("assistant", response))
    return response


def run_app(st=None) -> None:
    if st is None:
        import streamlit as st

    st.set_page_config(page_title="LangJu AI Research Assistant", page_icon="🤖")
    st.title("🤖 LangJu AI Research Assistant")
    st.caption("Local (Ollama) + Cloud (OpenAI) hybrid — RAG + Tools + Memory")

    with st.sidebar:
        st.header("📄 Knowledge Base")
        uploaded = st.file_uploader(
            "Upload PDF/TXT/DOCX",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
        )
        if uploaded:
            for uploaded_file in uploaded:
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    load_document_into_knowledgebase(uploaded_file)
            st.success("Documents indexed.")

        st.divider()
        st.header("⚙️ Settings")
        backend = st.selectbox("Backend", ["openai", "ollama"])
        st.session_state["backend"] = backend

    if "history" not in st.session_state:
        st.session_state.history = []

    render_history(st, st.session_state.history)
    prompt = st.chat_input("Ask me anything about your docs or the web…")

    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = submit_query(
                    st.session_state.history,
                    prompt,
                    st.session_state.get("backend", "openai"),
                )
                render_payload(st, "assistant", response)


if __name__ == "__main__":
    run_app()
