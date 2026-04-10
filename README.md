A **local + cloud hybrid AI Agent** powered by **Qwen2 (Ollama)** & **GPT (OpenAI)**.  
Includes **RAG**, **memory**, **tool use**, **Streamlit UI**, **FastAPI REST API**, and **Docker** support.

---

## ⚙️ Tech Stack
Python 3.11 · smolagents · LangChain · LiteLLM ·  
Chroma / FAISS · SentenceTransformers · Streamlit · FastAPI · Docker  

---

## 🧱 Project Structure

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
```

## 🧠 Features Summary
✅ RAG (Retrieval-Augmented Generation)  
✅ Hybrid backend: Ollama (local) & OpenAI (cloud)  
✅ Streamlit UI + FastAPI RESTful API  
✅ Embedding with SentenceTransformers  
✅ Memory, logging, and vector caching  
✅ One-command Docker deployment  

---
## 🧭 System Architecture (架构总览)

```
                ┌────────────────────────────────────┐
                │           Streamlit 前端 UI         │
                │────────────────────────────────────│
                │  📄 文件上传 (st.file_uploader)     │
                │  💬 聊天输入框 (st.chat_input)      │
                │  📤 发送到 FastAPI /chat 接口       │
                └────────────────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────┐
               │          FastAPI 后端 (app.server) │
               │────────────────────────────────────│
               │ 🔧 接口1: /ingest (文档入库)        │
               │ 🔧 接口2: /chat (智能问答)          │
               │                                    │
               │ 内部逻辑：                         │
               │ 1️⃣ 读取 .env 中的 OPENAI_API_KEY    │
               │ 2️⃣ 加载 settings.yaml (模型配置)     │
               │ 3️⃣ 调用 agent_core.py 处理请求       │
               │ 4️⃣ 调用模型生成回答                 │
               └────────────────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────┐
               │           agent_core.py 模块        │
               │────────────────────────────────────│
               │ 🧠 核心功能：                       │
               │   - 模型路由 (OpenAI / Ollama)     │
               │   - 向量搜索 (FAISS / Chroma)       │
               │   - RAG 检索增强                    │
               │   - 生成最终响应                    │
               └────────────────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────┐
               │        模型层 (LLM Backend)        │
               │────────────────────────────────────│
               │ 🤖 可选：                           │
               │  - OpenAI GPT (线上调用)            │
               │  - Ollama 本地模型 (Qwen2 / Llama)  │
               │                                    │
               │ 🌐 配置：settings.yaml               │
               │ backend: openai / ollama            │
               │ model_id: gpt-4o-mini / qwen2:7b    │
               └────────────────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────┐
               │          向量数据库 (FAISS/Chroma) │
               │────────────────────────────────────│
               │ 📚 存储用户上传的文档向量嵌入       │
               │ 🔍 相似度检索供 RAG 使用            │
               └────────────────────────────────────┘
```

### 🔗 Data & Call Flow（调用链）
1. **Streamlit** 接收输入/上传 → 调用 **FastAPI** `/chat` 或 `/ingest`。  
2. **FastAPI** 转交给 `agent_core.py`：读取 `.env`、`settings.yaml`、路由到模型。  
3. **agent_core** 从 `data/embeddings/`（FAISS/Chroma）检索相关片段 → 组织上下文。  
4. **模型（OpenAI/Ollama）** 生成答案 → 通过 **FastAPI** 返回 → **Streamlit** 展示。

### 📁 File Map（关键文件映射）
| Path | Purpose |
|------|---------|
| `app/server.py` | FastAPI 服务入口（/chat, /ingest） |
| `app/main.py` | Streamlit 前端入口 |
| `app/agent_core.py` | Agent 逻辑：RAG、工具、模型调用 |
| `app/memory/vector_store.py` | FAISS/Chroma + 解析与分块 |
| `app/config/settings.yaml` | 配置模型与向量库 |
| `.env` | 私密密钥（OPENAI_API_KEY 等，不提交 Git） |

---

## 🚀 Run Locally (Streamlit Web UI)

```bash
# 1️⃣ Create environment
python -m venv .venv && .\.venv\Scripts\activate   # (Windows PowerShell)


## 🧑‍💻 Developer quick start (Windows PowerShell)

If you're developing locally on Windows, use the included `run_dev.ps1` helper to create/activate the virtualenv, set PYTHONPATH to the repo root, and start Streamlit:

```powershell
# from repository root
.\run_dev.ps1            # start dev server
.\run_dev.ps1 -Reinstall # (optional) reinstall dependencies first
```

Manual steps (equivalent):

```powershell
# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Run Streamlit interface
streamlit run app/main.py
```

🧩 功能说明：
- 📄 上传 PDF / TXT / DOCX 文件 → 自动分块并嵌入向量数据库  

Notes:
- If you see `ModuleNotFoundError: No module named 'app'`, make sure you ran the commands from the repository root and that the venv is activated (or use `run_dev.ps1`).
- If Streamlit errors with `UnicodeDecodeError` when reading `.py` files, convert the affected files to UTF-8 (VS Code: Reopen with Encoding → Save with Encoding → UTF-8).

## 🛠 Troubleshooting / FAQ

Q: I get `ModuleNotFoundError: No module named 'app'` when running Streamlit or tests. What do I do?

- Cause: Python's import search path (`sys.path`) doesn't include the repository root or you ran the script from the wrong folder.
- Quick fixes:
  - Run commands from the repository root.
  - Use the provided `run_dev.ps1` which sets `PYTHONPATH` for you.
  - Or run with the venv Python directly: `.\.venv\Scripts\python -m streamlit run app/main.py`.

Q: `UnicodeDecodeError: 'utf-8' codec can't decode bytes ...` reading my .py files.

- Cause: Some source files are saved in a non-UTF-8 encoding (e.g., GBK/ANSI on Windows).
- Fix:
  - In VS Code: Reopen with Encoding → choose `Chinese (GBK)` to verify content, then Save with Encoding → `UTF-8` (no BOM).
  - Or use the included script `scripts/ensure_utf8.py` to rewrite `.py` files under `app/` as UTF-8.

Q: `& .\.venv\Scripts\Activate.ps1` fails with a security error (script execution is disabled).

- Cause: PowerShell ExecutionPolicy blocks running scripts.
- Options:
  - Recommended: don't run Activate.ps1; use the venv Python directly: `.\.venv\Scripts\python -m pytest -q`.
  - Temporarily allow scripts in the current terminal: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` then activate.

Q: CI fails installing packages like `faiss` or `sentence-transformers`.

- Cause: Some packages need native binaries or conda-based installs and fail on GitHub runners.
- Fixes:
  - Use a minimal test dependency set in CI (we install only pytest/pydantic/requests by default).
  - For full integration tests, use a dedicated runner with conda or an Ubuntu image that supports those libs, or mark heavy tests to run in a separate job.

## 🔍 How to inspect failing CI runs (GitHub Actions)

1. Go to your repository on GitHub and click the "Actions" tab.
2. Select the workflow run that failed (they are grouped by workflow name and commit/PR).
3. Click the failing job (e.g., `test`, `checks`, or `integration`).
4. Expand the step that's marked with a red ❌ to see the console log and exact error output. The log contains the stdout/stderr from the runner.

Tips:
- Look at the first failing step; often an install step or a test command fails and subsequent steps are skipped.
- For dependency install failures, copy the failing command from the log and try to reproduce locally (use the same Python version/conda env).
- If a job is flaky (network or remote model download), re-run the workflow from the GitHub UI using "Re-run jobs".



- 💬 侧边栏选择后端（Ollama 或 OpenAI）  
- 🧠 具备记忆功能、上下文检索与工具调用  

---

## 🧩 FastAPI (REST API Server)

```bash
uvicorn app.server:app --reload --port 8000
```

**Chat endpoint**
```bash
curl -X POST http://localhost:8000/chat   -H "Content-Type: application/json"   -d '{"prompt":"Explain RAG in one sentence","backend":"openai"}'
```

**Ingest a document**
```bash
curl -X POST http://localhost:8000/ingest -F "file=@data/sample_docs/intro.txt"
```

💡 `/chat` → 输入 prompt 获取智能回复  
💡 `/ingest` → 上传文档至向量库（Chroma 或 FAISS）  

---

## 🧠 RAG / Vector DB Configuration

在 `app/config/settings.yaml` 文件中配置向量数据库参数：
```yaml
rag:
  vector_db: faiss   # 可选：chroma 或 faiss
  collection_name: langju_docs
  top_k: 4
```

说明：
- **Chroma** → 存储路径：`data/embeddings/chroma`
- **FAISS** → 存储路径：`data/embeddings/faiss`
- 默认使用 **SentenceTransformers** 嵌入模型：`all-MiniLM-L6-v2`
- 支持 PDF、DOCX、TXT 文档解析与分块（900 字符 / 150 重叠）

---

## 🔁 Switching Backend (Ollama ↔ OpenAI)

| 模式 | 后端 | 启动方式 |
|------|------|-----------|
| 本地模型 | Ollama (Qwen2:7b) | `ollama serve &` → 侧边栏选择 Ollama |
| 云端模型 | OpenAI GPT | 设置环境变量 `OPENAI_API_KEY` |

PowerShell 设置示例：
```powershell
$env:OPENAI_API_KEY = "sk-xxxxxx"
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t langju/ai-agent-demo .

# Run container
docker run -p 8000:8000 -v ${PWD}/data:/app/data langju/ai-agent-demo
```

说明：
- Web UI: http://localhost:8501  
- API: http://localhost:8000  
- 数据持久化：挂载 `data/` 目录保存嵌入向量  


