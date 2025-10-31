"""
Calculator tool for mathematical operations.
"""
import re
from typing import Any
from app.tools.base import BaseTool
from app.utils import logger


class CalculatorTool(BaseTool):
    """Simple calculator tool for basic math operations."""
    
    name = "calculator"
    description = "Performs basic mathematical calculations. Input should be a mathematical expression like '2 + 2' or '5 * 3'."
    
    def run(self, expression: str) -> str:
        """
        Evaluate mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
        
        Returns:
            Result of the calculation
        """
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Security: Only allow safe mathematical operations
            if not self._is_safe_expression(expression):
                return "Error: Invalid expression. Only basic math operations are allowed."
            
            # Evaluate the expression
            result = eval(expression, {"__builtins__": {}}, {})
            
            logger.info(f"Calculator: {expression} = {result}")
            return f"Result: {result}"
        
        except Exception as e:
            error_msg = f"Error calculating '{expression}': {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def _is_safe_expression(self, expression: str) -> bool:
        """
        Check if expression contains only safe mathematical operations.
        
        Args:
            expression: Expression to validate
        
        Returns:
            True if safe, False otherwise
        """
        # Allow only numbers, basic operators, parentheses, and whitespace
        safe_pattern = r'^[\d\s\+\-\*\/\(\)\.\%\*\*]+$'
        return bool(re.match(safe_pattern, expression))
