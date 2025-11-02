
**AI 研究助理（混合式 LLM Agent）**
- 自研端到端 AI Agent：本地（Ollama + Qwen2）与云端（OpenAI GPT）双后端可互换，通过统一封装实现动态路由。
- 实现 RAG 检索增强：支持 PDF/TXT/DOCX 解析与分块，基于 Chroma/FAISS + SentenceTransformers 的向量检索与上下文注入。
- 设计 Agent 编排（工具调用 + 记忆 + 反思 Prompt），集成缓存、Token 统计与结构化日志，提升稳定性和可观测性。
- 交付产品化接口：Streamlit 聊天界面 + FastAPI REST（/chat, /ingest），提供 Docker 一键部署能力。
- 结果：在实验阶段通过本地 Qwen2 替代云端调用显著降低 Token 成本；1k+ 文档块检索平均延迟 < 1s；完成可用于面试展示的演示系统。

**技术栈：** Python、smolagents、LangChain、LiteLLM、OpenAI/Ollama、ChromaDB、FAISS、SentenceTransformers、Streamlit、FastAPI、Docker
