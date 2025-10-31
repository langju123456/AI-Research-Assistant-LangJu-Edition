"""
Base model interface for LLM providers.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseModel(ABC):
    """Abstract base class for LLM models."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat completion with message history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional generation parameters
        
        Returns:
            Assistant's response
        """
        pass
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """
        Get text embedding.
        
        Args:
            text: Input text
        
        Returns:
            Embedding vector
        """
        pass
