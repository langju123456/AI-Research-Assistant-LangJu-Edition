"""
OpenAI model wrapper.
"""
from typing import List, Dict, Any, Optional
from app.models.base import BaseModel
from app.config import OPENAI_API_KEY, TEMPERATURE, MAX_TOKENS
from app.utils import logger, token_tracker

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Install with: pip install openai")


class OpenAIModel(BaseModel):
    """OpenAI GPT model wrapper."""
    
    def __init__(self, model_name: str = "gpt-4", api_key: str = None):
        """
        Initialize OpenAI model.
        
        Args:
            model_name: Model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')
            api_key: OpenAI API key (uses config if not provided)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library is required. Install with: pip install openai")
        
        self.model_name = model_name
        self.api_key = api_key or OPENAI_API_KEY
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI model: {model_name}")
    
    def generate(self, prompt: str, temperature: float = None, max_tokens: int = None, **kwargs) -> str:
        """Generate text from prompt."""
        temperature = temperature or TEMPERATURE
        max_tokens = max_tokens or MAX_TOKENS
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Track token usage
            usage = response.usage
            token_tracker.track(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = None, max_tokens: int = None, **kwargs) -> str:
        """Chat completion with message history."""
        temperature = temperature or TEMPERATURE
        max_tokens = max_tokens or MAX_TOKENS
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Track token usage
            usage = response.usage
            token_tracker.track(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    def get_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Get text embedding."""
        try:
            response = self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
