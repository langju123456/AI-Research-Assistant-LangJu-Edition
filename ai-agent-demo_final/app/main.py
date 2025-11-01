import sys
from pathlib import Path
# flake8: noqa: E402

# Ensure repository root is on sys.path so `import app...` works when this file
# is executed directly (Streamlit runs scripts as __main__). This prevents
# ModuleNotFoundError: No module named 'app' in environments where the
# current working directory isn't the project root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.agent_core import get_response, load_document_into_knowledgebase


st.set_page_config(page_title="LangJu AI Research Assistant", page_icon="🤖")

st.title("🤖 LangJu AI Research Assistant")

st.caption("Local (Ollama) + Cloud (OpenAI) hybrid — RAG + Tools + Memory")


# Sidebar: upload docs

with st.sidebar:

    st.header("📄 Knowledge Base")

    uploaded = st.file_uploader(
        "Upload PDF/TXT/DOCX", type=["pdf", "txt", "docx"], accept_multiple_files=True
    )

    if uploaded:

        for f in uploaded:

            with st.spinner(f"Indexing {f.name}..."):

                load_document_into_knowledgebase(f)

        st.success("Documents indexed.")

    st.divider()

    st.header("⚙️ Settings")

    backend = st.selectbox("Backend", ["openai", "ollama"])

    st.session_state["backend"] = backend


# Chat UI

if "history" not in st.session_state:

    st.session_state.history = []


for role, content in st.session_state.history:

    with st.chat_message(role):

        st.write(content)


prompt = st.chat_input("Ask me anything about your docs or the web…")


if prompt:

    st.session_state.history.append(("user", prompt))

    with st.chat_message("user"):

        st.write(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            resp = get_response(
                prompt, backend=st.session_state.get("backend", "openai")
            )

            st.write(resp)

            st.session_state.history.append(("assistant", resp))
