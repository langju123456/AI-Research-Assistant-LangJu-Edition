
**AI Research Assistant (Hybrid LLM Agent)**
- Built an end-to-end AI Agent product that runs on both local (Ollama + Qwen2) and cloud (OpenAI GPT) backends, with interchangeable routing via a unified model wrapper.
- Implemented RAG pipeline (Chroma/FAISS + SentenceTransformers) supporting PDF/TXT/DOCX ingestion, document chunking, top-k retrieval, and context injection.
- Engineered agent orchestration (tools + memory + reflection prompts) using smolagents/LangChain; added caching, token tracking, and structured logging.
- Delivered a production-ready interface: Streamlit chat UI for demo and FastAPI REST endpoints (/chat, /ingest) for integration; packaged with Docker for one-command deployment.
- Outcome: Reduced cloud token cost in experimentation by shifting to local Qwen2 via Ollama; achieved <1s average retrieval latency on 1k+ chunks; shipped a demo used in stakeholder interviews.

**Tech:** Python, smolagents, LangChain, LiteLLM, OpenAI/Ollama, ChromaDB, FAISS, SentenceTransformers, Streamlit, FastAPI, Docker
