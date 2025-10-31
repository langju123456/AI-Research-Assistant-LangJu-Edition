"""
Document retrieval tool for RAG.
"""
from typing import List, Dict, Optional
from app.tools.base import BaseTool
from app.memory import VectorStore, VECTOR_STORE_AVAILABLE
from app.utils import logger


class DocumentRetrieverTool(BaseTool):
    """Tool for retrieving relevant documents from vector store."""
    
    name = "document_retriever"
    description = "Retrieves relevant documents from the knowledge base. Input should be a search query."
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize document retriever.
        
        Args:
            vector_store: Vector store instance
        """
        self.vector_store = vector_store
        
        if vector_store is None and VECTOR_STORE_AVAILABLE:
            try:
                self.vector_store = VectorStore()
            except Exception as e:
                logger.warning(f"Could not initialize vector store: {e}")
    
    def run(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant documents.
        
        Args:
            query: Search query
            n_results: Number of documents to retrieve
        
        Returns:
            Formatted retrieval results
        """
        if self.vector_store is None:
            return "Error: Vector store not available. Check configuration."
        
        try:
            # Check if vector store has documents
            count = self.vector_store.count()
            if count == 0:
                return "No documents in knowledge base. Please add documents first."
            
            # Search for relevant documents
            results = self.vector_store.search(query, n_results=n_results)
            
            if not results:
                return f"No relevant documents found for query: '{query}'"
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                doc = result['document']
                distance = result.get('distance', 0)
                metadata = result.get('metadata', {})
                
                formatted_results.append(
                    f"Document {i} (relevance: {1 - distance:.2f}):\n{doc}\n"
                    f"Metadata: {metadata}"
                )
            
            logger.info(f"Retrieved {len(results)} documents for query: '{query}'")
            return "\n\n".join(formatted_results)
        
        except Exception as e:
            error_msg = f"Error retrieving documents: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None):
        """
        Add documents to vector store.
        
        Args:
            documents: List of document texts
            metadata: Optional metadata for each document
        """
        if self.vector_store is None:
            logger.error("Cannot add documents: Vector store not available")
            return
        
        try:
            self.vector_store.add_documents(documents, metadata=metadata)
            logger.info(f"Added {len(documents)} documents to knowledge base")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
