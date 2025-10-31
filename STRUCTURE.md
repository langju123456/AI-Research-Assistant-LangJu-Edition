# Project Structure Documentation

This document explains the organization and purpose of each component in the AI Research Assistant project.

## Directory Structure

```
AI-Research-Assistant-LangJu-Edition/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # Streamlit web interface
│   ├── agent_core.py      # Core agent orchestration logic
│   │
│   ├── config/            # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py    # Application settings and environment variables
│   │   └── .env.template  # Template for environment configuration
│   │
│   ├── memory/            # Memory and context management
│   │   ├── __init__.py
│   │   ├── conversation.py    # Conversation history tracking
│   │   └── vector_store.py    # Vector database for RAG
│   │
│   ├── models/            # LLM provider wrappers
│   │   ├── __init__.py
│   │   ├── base.py        # Abstract base model interface
│   │   ├── ollama_model.py    # Ollama (local) model wrapper
│   │   └── openai_model.py    # OpenAI (cloud) model wrapper
│   │
│   ├── tools/             # Agent tool implementations
│   │   ├── __init__.py
│   │   ├── base.py        # Base tool interface
│   │   ├── calculator.py  # Mathematical calculations
│   │   ├── document_retriever.py  # RAG document retrieval
│   │   ├── summarizer.py  # Text summarization
│   │   └── web_search.py  # Internet search capability
│   │
│   └── utils/             # Utility modules
│       ├── __init__.py
│       ├── cache.py       # Caching for API responses
│       ├── logger.py      # Logging configuration
│       └── token_tracker.py   # Token usage tracking
│
├── data/                  # Data storage
│   ├── embeddings/        # Vector database storage (ChromaDB)
│   │   └── .gitkeep
│   └── sample_docs/       # Example documents for RAG
│       ├── ai_introduction.txt
│       └── rag_overview.txt
│
├── examples/              # Example usage scripts
│   └── basic_usage.py     # Demonstration of basic functionality
│
├── tests/                 # Unit tests
│   ├── __init__.py
│   └── test_agent.py      # Core agent tests
│
├── logs/                  # Application logs (ignored by git)
│
├── .gitignore            # Git ignore patterns
├── LICENSE               # MIT License
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
└── run.sh               # Quick start script
```

## Component Details

### app/main.py
The Streamlit-based web interface providing:
- Interactive chat interface
- Document upload for RAG
- Model provider selection (Ollama/OpenAI)
- Token usage monitoring
- Conversation management

### app/agent_core.py
Core agent orchestration implementing:
- Tool selection and execution
- Multi-step reasoning loop
- Action/observation parsing
- Conversation memory integration
- Maximum iteration handling

### app/config/
Configuration management:
- `settings.py`: Loads and validates environment variables
- `.env.template`: Template for user configuration
- Manages API keys, model settings, and application parameters

### app/memory/
Memory and context management:
- `conversation.py`: Sliding window conversation history
- `vector_store.py`: ChromaDB wrapper for document embeddings and semantic search

### app/models/
LLM provider abstractions:
- `base.py`: Abstract interface for all model providers
- `ollama_model.py`: Local model support (Qwen2, Llama2, etc.)
- `openai_model.py`: Cloud-based GPT models
- Factory pattern for easy provider switching

### app/tools/
Modular tool system:
- `base.py`: Abstract tool interface
- `calculator.py`: Safe mathematical expression evaluation
- `document_retriever.py`: RAG-based document search
- `summarizer.py`: Extractive and abstractive summarization
- `web_search.py`: Internet search (SerpAPI or DuckDuckGo)

### app/utils/
Utility functions:
- `logger.py`: Structured logging with file and console handlers
- `token_tracker.py`: Track API token usage and costs
- `cache.py`: File-based caching with TTL support

### data/
Data storage:
- `embeddings/`: Vector database persistence
- `sample_docs/`: Example documents demonstrating RAG

### tests/
Unit tests using pytest:
- Memory management tests
- Tool functionality tests
- Agent orchestration tests
- Action/answer parsing tests

## Key Design Patterns

### 1. Abstract Base Classes
- `BaseModel`: Unified interface for different LLM providers
- `BaseTool`: Consistent tool interface for extensibility

### 2. Factory Pattern
- `get_model()`: Creates appropriate model instance based on configuration

### 3. Strategy Pattern
- Tools can be swapped and extended without modifying core agent logic

### 4. Dependency Injection
- Agent accepts custom models, tools, and memory instances

## Extension Points

### Adding a New Tool
1. Create new file in `app/tools/`
2. Inherit from `BaseTool`
3. Implement `run()` method
4. Add to agent's tool list

### Adding a New Model Provider
1. Create new file in `app/models/`
2. Inherit from `BaseModel`
3. Implement required methods (`generate`, `chat`, `get_embedding`)
4. Update `get_model()` factory function

### Customizing Memory
1. Extend `ConversationMemory` or `VectorStore`
2. Inject custom instance into agent

## Configuration

Key environment variables (in `.env`):
- `DEFAULT_PROVIDER`: 'ollama' or 'openai'
- `OLLAMA_MODEL`: Model name for Ollama
- `OPENAI_API_KEY`: API key for OpenAI
- `VECTOR_DB_PATH`: Path to vector database
- `MAX_ITERATIONS`: Agent reasoning loop limit
- `TEMPERATURE`: Model temperature parameter

## Development Workflow

1. **Setup**: `pip install -r requirements.txt`
2. **Configure**: Copy `.env.template` to `.env` and edit
3. **Test**: `pytest tests/ -v`
4. **Run**: `streamlit run app/main.py`
5. **Example**: `python examples/basic_usage.py`

## Dependencies

Core dependencies:
- `streamlit`: Web interface
- `python-dotenv`: Environment configuration
- `requests`: HTTP client
- `chromadb`: Vector database
- `sentence-transformers`: Text embeddings
- `openai`: OpenAI API client (optional)
- `pytest`: Testing framework
