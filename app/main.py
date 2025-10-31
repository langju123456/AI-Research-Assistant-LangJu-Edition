"""
Streamlit UI for AI Research Assistant.
"""
import streamlit as st
from pathlib import Path
from app.agent_core import ResearchAgent
from app.models import get_model
from app.memory import ConversationMemory, VectorStore, VECTOR_STORE_AVAILABLE
from app.config import DEFAULT_PROVIDER, OLLAMA_MODEL
from app.utils import logger, token_tracker
import sys

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant - LangJu Edition",
    page_icon="🧠",
    layout="wide"
)

# Title and description
st.title("🧠 AI Research Assistant - LangJu Edition")
st.markdown("*Powered by Qwen2 & GPT-4 with RAG, Memory, and Tool Use*")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Model provider selection
provider = st.sidebar.selectbox(
    "Model Provider",
    ["ollama", "openai"],
    index=0 if DEFAULT_PROVIDER == "ollama" else 1
)

model_name = None
if provider == "openai":
    model_name = st.sidebar.text_input("Model Name", value="gpt-4")
elif provider == "ollama":
    model_name = st.sidebar.text_input("Model Name", value=OLLAMA_MODEL)

# Advanced settings
with st.sidebar.expander("Advanced Settings"):
    use_memory = st.checkbox("Use Conversation Memory", value=True)
    use_rag = st.checkbox("Use RAG (if documents loaded)", value=True)
    show_intermediate = st.checkbox("Show Tool Usage", value=False)

# Initialize session state
if 'agent' not in st.session_state:
    try:
        model = get_model(provider=provider, model_name=model_name)
        st.session_state.agent = ResearchAgent(model=model)
        st.session_state.messages = []
        logger.info("Agent initialized successfully")
    except Exception as e:
        st.error(f"Error initializing agent: {e}")
        st.stop()

# Document upload section
st.sidebar.header("📚 Knowledge Base")
uploaded_files = st.sidebar.file_uploader(
    "Upload documents for RAG",
    accept_multiple_files=True,
    type=['txt', 'md', 'pdf']
)

if uploaded_files and VECTOR_STORE_AVAILABLE:
    if st.sidebar.button("Process Documents"):
        try:
            from app.tools import DocumentRetrieverTool
            
            documents = []
            metadata = []
            
            for file in uploaded_files:
                content = file.read().decode('utf-8', errors='ignore')
                documents.append(content)
                metadata.append({"filename": file.name})
            
            # Add to vector store
            retriever = DocumentRetrieverTool()
            retriever.add_documents(documents, metadata=metadata)
            
            st.sidebar.success(f"✅ Processed {len(documents)} documents")
            logger.info(f"Loaded {len(documents)} documents into knowledge base")
        
        except Exception as e:
            st.sidebar.error(f"Error processing documents: {e}")
            logger.error(f"Document processing error: {e}")

# Sample documents section
st.sidebar.markdown("---")
if st.sidebar.button("Load Sample Documents"):
    try:
        from app.tools import DocumentRetrieverTool
        
        sample_docs = [
            "AI and machine learning are transforming various industries by enabling computers to learn from data and make intelligent decisions.",
            "Natural language processing (NLP) allows machines to understand and generate human language, powering chatbots and virtual assistants.",
            "Retrieval-Augmented Generation (RAG) combines information retrieval with text generation for more accurate and grounded responses.",
        ]
        
        retriever = DocumentRetrieverTool()
        retriever.add_documents(sample_docs)
        
        st.sidebar.success("✅ Loaded sample documents")
        logger.info("Loaded sample documents")
    
    except Exception as e:
        st.sidebar.error(f"Error loading samples: {e}")

# Clear memory button
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state.agent.reset_memory()
    st.session_state.messages = []
    st.sidebar.success("Conversation cleared!")

# Token usage display
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Token Usage")
session_usage = token_tracker.get_session_usage()
st.sidebar.metric("Session Tokens", session_usage.total_tokens)
st.sidebar.caption(f"Prompt: {session_usage.prompt_tokens} | Completion: {session_usage.completion_tokens}")

# Main chat interface
st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.run(prompt, use_memory=use_memory)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                logger.error(f"Chat error: {e}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    AI Research Assistant - LangJu Edition | 
    Supports: RAG • Context Memory • Tool Use • Local & Cloud Models
    </div>
    """,
    unsafe_allow_html=True
)

# Info section in expander
with st.expander("ℹ️ About"):
    st.markdown("""
    ### Features
    - 🧠 **Smart Agent**: Uses reasoning and tool selection
    - 📚 **RAG**: Retrieval-Augmented Generation for grounded responses
    - 💬 **Memory**: Maintains conversation context
    - 🔧 **Tools**: Calculator, Web Search, Summarizer, Document Retriever
    - 🌐 **Flexible Backend**: Switch between Ollama (local) and OpenAI (cloud)
    
    ### Available Tools
    """)
    
    for tool_info in st.session_state.agent.get_tool_info():
        st.markdown(f"**{tool_info['name']}**: {tool_info['description']}")
    
    st.markdown("""
    ### Usage Tips
    1. Upload documents to enable RAG
    2. Ask complex questions that may require tools
    3. Use conversation memory for context-aware responses
    4. Monitor token usage in the sidebar
    """)
