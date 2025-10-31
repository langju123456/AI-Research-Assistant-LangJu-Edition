 🤖 AI Research Assistant — LangJu Edition

A local + cloud hybrid AI Agent powered by Qwen2 & GPT-4, supporting:
- ✅ RAG document retrieval
- 🧠 Context memory
- 🌐 Tool use (web search, calculator, summarizer)
- 💬 Streamlit chat interface
- ⚙️ Ollama / OpenAI interchangeable backend

## ⚙️ Tech Stack
- Python 3.11
- smolagents / LangChain
- LiteLLM / OpenAI API
- FAISS / ChromaDB
- Streamlit / FastAPI

## 🚀 Run Locally
```bash
pip install -r requirements.txt
ollama serve &
streamlit run app/main.py
