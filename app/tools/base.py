"""
Base tool interface.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """Abstract base class for agent tools."""
    
    name: str = "base_tool"
    description: str = "Base tool interface"
    
    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        """
        Execute the tool.
        
        Returns:
            Tool execution result as string
        """
        pass
    
    def __call__(self, *args, **kwargs) -> str:
        """Allow tool to be called directly."""
        return self.run(*args, **kwargs)
    
    def get_info(self) -> Dict[str, str]:
        """Get tool information."""
        return {
            "name": self.name,
            "description": self.description
        }
