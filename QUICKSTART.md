# Quick Start Guide

Get started with AI Research Assistant in under 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Git
- (Optional) Ollama installed for local models
- (Optional) OpenAI API key for cloud models

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/langju123456/AI-Research-Assistant-LangJu-Edition.git
cd AI-Research-Assistant-LangJu-Edition

# Run the quick start script
chmod +x run.sh
./run.sh
```

The script will:
1. Create a virtual environment
2. Install all dependencies
3. Create .env file from template
4. Launch the Streamlit UI

### Option 2: Manual Setup

```bash
# Clone and navigate
git clone https://github.com/langju123456/AI-Research-Assistant-LangJu-Edition.git
cd AI-Research-Assistant-LangJu-Edition

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp app/config/.env.template .env
# Edit .env with your settings

# Run the application
streamlit run app/main.py
```

## Configuration

Edit the `.env` file to customize your setup:

### For Local Models (Ollama)

```env
DEFAULT_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:latest
```

**Note:** Make sure Ollama is running:
```bash
ollama pull qwen2:latest
ollama serve
```

### For Cloud Models (OpenAI)

```env
DEFAULT_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
```

## Usage Examples

### 1. Web Interface (Streamlit)

```bash
streamlit run app/main.py
```

Then open http://localhost:8501 in your browser.

**Features:**
- Interactive chat interface
- Document upload for RAG
- Model provider selection
- Token usage monitoring
- Conversation management

### 2. Command Line Demo

```bash
python examples/basic_usage.py
```

This demonstrates:
- Basic chat functionality
- Tool usage (calculator, summarizer)
- Memory management
- Agent reasoning

### 3. Python API

```python
from app.agent_core import ResearchAgent
from app.models import get_model

# Initialize with Ollama
model = get_model(provider="ollama", model_name="qwen2:latest")
agent = ResearchAgent(model=model)

# Simple chat
response = agent.chat("Hello, what can you do?")
print(response)

# Use tools automatically
response = agent.run("What is 25 * 34?")  # Uses calculator
print(response)

# RAG with documents
from app.tools import DocumentRetrieverTool
retriever = DocumentRetrieverTool()
retriever.add_documents([
    "AI is transforming healthcare through...",
    "Machine learning enables computers to..."
])

response = agent.run("Tell me about AI in healthcare")
print(response)
```

## Common Tasks

### Upload Documents for RAG

1. Launch the Streamlit UI
2. Use the sidebar "Upload documents for RAG" section
3. Select one or more `.txt`, `.md`, or `.pdf` files
4. Click "Process Documents"
5. Documents are now searchable by the agent

### Switch Between Models

In the Streamlit UI:
1. Use the "Model Provider" dropdown in sidebar
2. Select "ollama" or "openai"
3. Enter the model name
4. The change takes effect on the next message

Via code:
```python
# Ollama
model = get_model(provider="ollama", model_name="llama2")

# OpenAI
model = get_model(provider="openai", model_name="gpt-4")

agent = ResearchAgent(model=model)
```

### Clear Conversation History

In UI:
- Click "🗑️ Clear Conversation" button in sidebar

Via code:
```python
agent.reset_memory()
```

### Monitor Token Usage

In UI:
- View "Token Usage" section in sidebar
- Shows session and total tokens

Via code:
```python
from app.utils import token_tracker

usage = token_tracker.get_session_usage()
print(f"Tokens used: {usage.total_tokens}")
```

## Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/test_agent.py -v
```

## Troubleshooting

### "No module named 'app'"

Make sure you're in the project root directory and the virtual environment is activated.

### Ollama Connection Error

1. Verify Ollama is running: `ollama list`
2. Check the URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
3. Test the connection: `curl http://localhost:11434/api/tags`

### OpenAI API Error

1. Verify your API key is set in `.env`
2. Check you have credits/usage quota
3. Ensure the model name is correct (e.g., "gpt-4", "gpt-3.5-turbo")

### Vector Store Error

Install the required dependencies:
```bash
pip install chromadb sentence-transformers
```

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

## Next Steps

1. **Try the examples**: Run `python examples/basic_usage.py`
2. **Upload documents**: Add your own documents for RAG
3. **Customize tools**: Add new tools in `app/tools/`
4. **Experiment with models**: Try different Ollama models
5. **Read the docs**: Check `STRUCTURE.md` for architecture details

## Getting Help

- **Documentation**: See `README.md` and `STRUCTURE.md`
- **Examples**: Check `examples/` directory
- **Tests**: Look at `tests/test_agent.py` for usage patterns
- **Issues**: Report bugs on GitHub

## Features Checklist

- ✅ Intelligent agent with multi-step reasoning
- ✅ Tool use (calculator, web search, summarizer, RAG)
- ✅ Conversation memory with context
- ✅ RAG with document upload and retrieval
- ✅ Dual backend (Ollama + OpenAI)
- ✅ Token usage tracking
- ✅ Web UI with Streamlit
- ✅ Comprehensive tests
- ✅ Example scripts and documentation

Enjoy using AI Research Assistant! 🧠✨
