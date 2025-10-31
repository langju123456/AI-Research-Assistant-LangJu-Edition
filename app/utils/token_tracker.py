"""
Token tracking utilities for monitoring API usage.
"""
from typing import Dict, Optional
from dataclasses import dataclass, field
from app.utils.logger import logger


@dataclass
class TokenUsage:
    """Track token usage for API calls."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    def update(self, prompt: int = 0, completion: int = 0):
        """Update token counts."""
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens = self.prompt_tokens + self.completion_tokens
    
    def reset(self):
        """Reset all counters."""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def __str__(self):
        return f"Tokens(prompt={self.prompt_tokens}, completion={self.completion_tokens}, total={self.total_tokens})"


class TokenTracker:
    """Global token usage tracker."""
    
    def __init__(self):
        self.session_usage = TokenUsage()
        self.total_usage = TokenUsage()
    
    def track(self, prompt_tokens: int = 0, completion_tokens: int = 0, session_only: bool = False):
        """
        Track token usage.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            session_only: If True, only track in session (not total)
        """
        self.session_usage.update(prompt_tokens, completion_tokens)
        if not session_only:
            self.total_usage.update(prompt_tokens, completion_tokens)
        
        logger.debug(f"Token usage - Session: {self.session_usage}, Total: {self.total_usage}")
    
    def get_session_usage(self) -> TokenUsage:
        """Get current session usage."""
        return self.session_usage
    
    def get_total_usage(self) -> TokenUsage:
        """Get total usage."""
        return self.total_usage
    
    def reset_session(self):
        """Reset session usage."""
        self.session_usage.reset()
        logger.info("Session token usage reset")
    
    def reset_all(self):
        """Reset all usage counters."""
        self.session_usage.reset()
        self.total_usage.reset()
        logger.info("All token usage reset")


# Global tracker instance
token_tracker = TokenTracker()
