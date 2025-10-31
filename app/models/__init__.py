"""
Model factory for creating LLM instances.
"""
from typing import Optional
from app.models.base import BaseModel
from app.models.openai_model import OpenAIModel, OPENAI_AVAILABLE
from app.models.ollama_model import OllamaModel
from app.config import DEFAULT_PROVIDER
from app.utils import logger


def get_model(provider: str = None, model_name: str = None, **kwargs) -> BaseModel:
    """
    Factory function to get model instance.
    
    Args:
        provider: Model provider ('openai' or 'ollama')
        model_name: Specific model name
        **kwargs: Additional parameters for model initialization
    
    Returns:
        Model instance
    
    Raises:
        ValueError: If provider is invalid or unavailable
    """
    provider = (provider or DEFAULT_PROVIDER).lower()
    
    if provider == "openai":
        if not OPENAI_AVAILABLE:
            raise ValueError("OpenAI is not available. Install with: pip install openai")
        
        model_name = model_name or "gpt-4"
        logger.info(f"Creating OpenAI model: {model_name}")
        return OpenAIModel(model_name=model_name, **kwargs)
    
    elif provider == "ollama":
        logger.info(f"Creating Ollama model: {model_name or 'default'}")
        return OllamaModel(model_name=model_name, **kwargs)
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'ollama'")


__all__ = ['BaseModel', 'OpenAIModel', 'OllamaModel', 'get_model']
