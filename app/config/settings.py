"""
Configuration settings for the AI Research Assistant.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"

# Ensure directories exist
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "logs").mkdir(exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Ollama settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2:latest")

# Model provider
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "ollama").lower()

# Vector database settings
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(EMBEDDINGS_DIR / "chroma_db"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Agent settings
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))

# Web search
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
