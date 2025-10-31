# AI Research Assistant - LangJu Edition

A local + cloud hybrid AI Agent powered by Qwen2 & GPT-4, supporting:
- ✅ RAG document retrieval
- 🧠 Context memory
- 🌐 Tool use (web search, calculator, summarizer)
- 💬 Streamlit chat interface
- ⚙️ Ollama / OpenAI interchangeable backend

## Features

### 🤖 Intelligent Agent
- Multi-step reasoning with tool selection
- Automatic tool orchestration
- Context-aware responses

### 📚 RAG (Retrieval-Augmented Generation)
- Upload and index documents
- Semantic search with vector embeddings
- Grounded, factual responses

### 💾 Memory Management
- Conversation history tracking
- Sliding window context
- Session persistence

### 🔧 Built-in Tools
- **Calculator**: Perform mathematical calculations
- **Web Search**: Search the internet for information
- **Summarizer**: Summarize long documents
- **Document Retriever**: Retrieve relevant information from your knowledge base

### 🌐 Flexible Backend
- **Ollama**: Run models locally (Qwen2, Llama2, etc.)
- **OpenAI**: Use cloud-based GPT models
- Easy switching between providers

## Project Structure

```
app/
  main.py            # Streamlit UI
  agent_core.py      # Agent orchestration
  tools/             # Tool implementations
    calculator.py
    web_search.py
    summarizer.py
    document_retriever.py
  memory/            # Memory + vector store wrappers
    conversation.py
    vector_store.py
  models/            # Model wrappers (OpenAI/Ollama)
    openai_model.py
    ollama_model.py
  utils/             # Token tracking, caching, logging
  config/            # Settings and env template
data/
  sample_docs/       # Example documents for RAG
  embeddings/        # Local vector DB cache
tests/
  test_agent.py      # Unit tests
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/langju123456/AI-Research-Assistant-LangJu-Edition.git
   cd AI-Research-Assistant-LangJu-Edition
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp app/config/.env.template .env
   # Edit .env with your API keys and settings
   ```

## Usage

### Running with Ollama (Local)

1. **Install and start Ollama**
   ```bash
   # Install from https://ollama.ai
   ollama pull qwen2:latest
   ollama serve
   ```

2. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

### Running with OpenAI (Cloud)

1. **Set your API key in `.env`**
   ```
   OPENAI_API_KEY=your_key_here
   DEFAULT_PROVIDER=openai
   ```

2. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

## Configuration

Edit `.env` file to customize:

```env
# Model provider
DEFAULT_PROVIDER=ollama  # or 'openai'
OLLAMA_MODEL=qwen2:latest
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI (optional)
OPENAI_API_KEY=your_key_here

# Agent settings
MAX_ITERATIONS=10
TEMPERATURE=0.7
MAX_TOKENS=2000

# Vector database
VECTOR_DB_PATH=data/embeddings/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Web search (optional)
SERPAPI_KEY=your_serpapi_key_here
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ --cov=app --cov-report=html
```

## Example Usage

### Basic Chat
```python
from app.agent_core import ResearchAgent

agent = ResearchAgent()
response = agent.chat("What is machine learning?")
print(response)
```

### Using Tools
```python
# The agent automatically selects and uses tools
response = agent.run("What is 25 * 34 + 17?")  # Uses calculator
response = agent.run("Search for latest AI news")  # Uses web search
```

### RAG with Documents
```python
from app.tools import DocumentRetrieverTool

# Add documents
retriever = DocumentRetrieverTool()
retriever.add_documents([
    "AI is transforming healthcare...",
    "Machine learning enables..."
])

# Agent will automatically retrieve relevant docs
response = agent.run("Tell me about AI in healthcare")
```

## Features in Detail

### Tool System
Tools are modular and extensible. Each tool implements the `BaseTool` interface:
- `run()`: Execute the tool
- `name`: Tool identifier
- `description`: What the tool does

### Memory System
- **ConversationMemory**: Maintains chat history with configurable sliding window
- **VectorStore**: Stores and retrieves document embeddings using ChromaDB

### Model Abstraction
Unified interface for different LLM providers:
- Easy switching between local and cloud models
- Consistent API across providers
- Token usage tracking

## Development

### Adding a New Tool

1. Create a new file in `app/tools/`
2. Inherit from `BaseTool`
3. Implement the `run()` method
4. Register in `ResearchAgent.__init__`

Example:
```python
from app.tools.base import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something useful"
    
    def run(self, input: str) -> str:
        # Your implementation
        return "Result"
```

### Adding a New Model Provider

1. Create a new file in `app/models/`
2. Inherit from `BaseModel`
3. Implement required methods
4. Update `get_model()` factory

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
- Verify model is pulled: `ollama list`

### Vector Store Errors
- Install dependencies: `pip install chromadb sentence-transformers`
- Clear existing DB: Delete `data/embeddings/chroma_db/`

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Ollama](https://ollama.ai/) and [OpenAI](https://openai.com/)
- Vector store by [ChromaDB](https://www.trychroma.com/)
- Embeddings from [Sentence Transformers](https://www.sbert.net/)
