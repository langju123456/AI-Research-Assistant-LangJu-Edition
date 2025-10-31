# 🤖 AI Research Assistant — LangJu Edition  
> 本地 + 云端混合 AI Agent：支持 Ollama(Qwen2) 与 OpenAI(GPT) 模型互换；  
> 集成 RAG 文档检索、短期记忆、工具调用、Streamlit 前端、FastAPI API、Docker 部署。  

A **local + cloud hybrid AI Agent** powered by **Qwen2 (Ollama)** & **GPT (OpenAI)**.  
Includes **RAG**, **memory**, **tool use**, **Streamlit UI**, **FastAPI REST API**, and **Docker** support.

---

## ⚙️ Tech Stack
Python 3.11 · smolagents · LangChain · LiteLLM ·  
Chroma / FAISS · SentenceTransformers · Streamlit · FastAPI · Docker  

---

## 🚀 Run Locally (Streamlit Web UI)

```bash
# 1️⃣ Create environment
python -m venv .venv && .\.venv\Scripts\activate   # (Windows PowerShell)

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run Streamlit interface
streamlit run app/main.py
🧩 功能说明：

📄 上传 PDF / TXT / DOCX 文件 → 自动分块并嵌入向量数据库

💬 侧边栏选择后端（Ollama 或 OpenAI）

🧠 具备记忆功能、上下文检索与工具调用

🧩 FastAPI (REST API Server)
bash
Copy code
# 启动 API 服务
uvicorn app.server:app --reload --port 8000
Chat endpoint

bash
Copy code
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Explain RAG in one sentence","backend":"ollama"}'
Ingest a document

bash
Copy code
curl -X POST http://localhost:8000/ingest -F "file=@data/sample_docs/intro.txt"
💡 /chat → 输入 prompt 获取智能回复
💡 /ingest → 上传文档至向量库（Chroma 或 FAISS）

🧠 RAG / Vector DB Configuration
在 app/config/settings.yaml 文件中配置向量数据库参数：

yaml
Copy code
rag:
  vector_db: chroma   # 可选：chroma 或 faiss
  collection_name: langju_docs
  top_k: 4
说明：

Chroma → 存储路径：data/embeddings/chroma

FAISS → 存储路径：data/embeddings/faiss

默认使用 SentenceTransformers 嵌入模型：all-MiniLM-L6-v2

支持 PDF、DOCX、TXT 文档解析与分块（900 字符 / 150 重叠）

🔁 Switching Backend (Ollama ↔ OpenAI)
模式	后端	启动方式
本地模型	Ollama (Qwen2:7b)	ollama serve & → 侧边栏选择 Ollama
云端模型	OpenAI GPT-4 / GPT-4o-mini	设置环境变量 OPENAI_API_KEY

PowerShell 设置示例：

powershell
Copy code
$env:OPENAI_API_KEY = "sk-xxxxxx"
🐳 Docker Deployment
bash
Copy code
# Build image
docker build -t langju/ai-agent-demo .

# Run container
docker run -p 8000:8000 -v ${PWD}/data:/app/data langju/ai-agent-demo
说明：

Web UI: http://localhost:8501

API: http://localhost:8000

数据持久化：挂载 data/ 目录保存嵌入向量

🧱 Project Structure
bash
Copy code
ai-agent-demo/
│
├── app/
│   ├── main.py             # Streamlit Web UI
│   ├── server.py           # FastAPI REST API
│   ├── agent_core.py       # Agent orchestration logic
│   ├── models/             # Model wrappers (Ollama/OpenAI)
│   ├── memory/             # Vector store + memory modules
│   ├── tools/              # Tool implementations
│   └── config/settings.yaml
│
├── data/
│   ├── sample_docs/
│   └── embeddings/
│
├── tests/
│   └── test_agent.py
│
├── Dockerfile
├── requirements.txt
├── RESUME_EN.md / RESUME_CN.md
└── README.md
🧠 Features Summary
✅ RAG (Retrieval-Augmented Generation)
✅ Hybrid backend: Ollama (local) & OpenAI (cloud)
✅ Streamlit UI + FastAPI RESTful API
✅ Embedding with SentenceTransformers
✅ Memory, logging, and vector caching
✅ One-command Docker deployment

✨ Author
Lang Ju (AI Engineer)
GitHub: langju | LinkedIn: langju
