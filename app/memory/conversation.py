"""
Conversation memory management.
"""
from typing import List, Dict, Optional
from collections import deque
from app.utils import logger


class ConversationMemory:
    """Manages conversation history with sliding window."""
    
    def __init__(self, max_messages: int = 10):
        """
        Initialize conversation memory.
        
        Args:
            max_messages: Maximum number of messages to retain
        """
        self.max_messages = max_messages
        self.messages: deque = deque(maxlen=max_messages)
        logger.debug(f"Initialized conversation memory with max_messages={max_messages}")
    
    def add_message(self, role: str, content: str):
        """
        Add a message to history.
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        message = {"role": role, "content": content}
        self.messages.append(message)
        logger.debug(f"Added {role} message to memory")
    
    def add_user_message(self, content: str):
        """Add user message."""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str):
        """Add assistant message."""
        self.add_message("assistant", content)
    
    def add_system_message(self, content: str):
        """Add system message."""
        self.add_message("system", content)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in history."""
        return list(self.messages)
    
    def clear(self):
        """Clear all messages."""
        self.messages.clear()
        logger.debug("Cleared conversation memory")
    
    def get_recent_context(self, n: int = 5) -> str:
        """
        Get recent conversation as formatted string.
        
        Args:
            n: Number of recent messages to include
        
        Returns:
            Formatted conversation string
        """
        recent = list(self.messages)[-n:]
        context = []
        for msg in recent:
            role = msg['role'].capitalize()
            content = msg['content']
            context.append(f"{role}: {content}")
        return "\n".join(context)
    
    def __len__(self) -> int:
        """Get number of messages."""
        return len(self.messages)
    
    def __str__(self) -> str:
        """String representation."""
        return f"ConversationMemory({len(self.messages)} messages)"
