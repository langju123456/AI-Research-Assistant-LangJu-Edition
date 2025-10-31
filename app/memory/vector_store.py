"""
Vector store wrapper for document retrieval.
"""
from typing import List, Dict, Optional, Any
from pathlib import Path
from app.config import VECTOR_DB_PATH, EMBEDDING_MODEL
from app.utils import logger

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False
    logger.warning("Vector store dependencies not installed. Install with: pip install chromadb sentence-transformers")


class VectorStore:
    """Vector database wrapper for semantic search."""
    
    def __init__(self, collection_name: str = "documents", db_path: str = None, embedding_model: str = None):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the collection
            db_path: Path to database directory
            embedding_model: Name of embedding model
        """
        if not VECTOR_STORE_AVAILABLE:
            raise ImportError("Vector store dependencies required. Install with: pip install chromadb sentence-transformers")
        
        self.db_path = db_path or VECTOR_DB_PATH
        self.embedding_model_name = embedding_model or EMBEDDING_MODEL
        self.collection_name = collection_name
        
        # Initialize ChromaDB
        Path(self.db_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document embeddings for RAG"}
        )
        
        logger.info(f"Initialized vector store: {collection_name} at {self.db_path}")
    
    def add_documents(self, documents: List[str], metadata: List[Dict] = None, ids: List[str] = None):
        """
        Add documents to vector store.
        
        Args:
            documents: List of document texts
            metadata: Optional list of metadata dicts
            ids: Optional list of document IDs
        """
        if not documents:
            return
        
        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadata or [{}] * len(documents),
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to vector store")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
        
        Returns:
            List of result dictionaries with 'document', 'metadata', and 'distance'
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0.0,
                    'id': results['ids'][0][i] if results['ids'] else None
                })
        
        logger.debug(f"Found {len(formatted_results)} results for query")
        return formatted_results
    
    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
    
    def count(self) -> int:
        """Get number of documents in collection."""
        return self.collection.count()
    
    def clear(self):
        """Clear all documents from collection."""
        # Delete and recreate collection
        self.delete_collection()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Document embeddings for RAG"}
        )
        logger.info("Cleared all documents from vector store")
