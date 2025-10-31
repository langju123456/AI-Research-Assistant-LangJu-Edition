"""
Ollama model wrapper for local LLM support.
"""
from typing import List, Dict, Any, Optional
import requests
from app.models.base import BaseModel
from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, TEMPERATURE, MAX_TOKENS
from app.utils import logger, token_tracker


class OllamaModel(BaseModel):
    """Ollama local model wrapper."""
    
    def __init__(self, model_name: str = None, base_url: str = None):
        """
        Initialize Ollama model.
        
        Args:
            model_name: Model identifier (e.g., 'qwen2:latest', 'llama2')
            base_url: Ollama server URL
        """
        self.model_name = model_name or OLLAMA_MODEL
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip('/')
        
        # Verify Ollama is running
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"Initialized Ollama model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama at {self.base_url}: {e}")
    
    def generate(self, prompt: str, temperature: float = None, max_tokens: int = None, **kwargs) -> str:
        """Generate text from prompt."""
        temperature = temperature or TEMPERATURE
        max_tokens = max_tokens or MAX_TOKENS
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False,
                    **kwargs
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # Estimate token usage (Ollama doesn't always provide this)
            if 'eval_count' in result:
                token_tracker.track(
                    prompt_tokens=result.get('prompt_eval_count', 0),
                    completion_tokens=result.get('eval_count', 0)
                )
            
            return result['response']
        
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None, **kwargs) -> str:
        """Chat completion with message history."""
        temperature = temperature or TEMPERATURE
        max_tokens = max_tokens or MAX_TOKENS
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": False,
                    **kwargs
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            # Track token usage if available
            if 'eval_count' in result:
                token_tracker.track(
                    prompt_tokens=result.get('prompt_eval_count', 0),
                    completion_tokens=result.get('eval_count', 0)
                )
            
            return result['message']['content']
        
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result['embedding']
        
        except Exception as e:
            logger.error(f"Ollama embedding error: {e}")
            raise
