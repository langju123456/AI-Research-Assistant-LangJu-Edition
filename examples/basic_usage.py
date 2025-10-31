#!/usr/bin/env python3
"""
Example script demonstrating AI Research Assistant usage.
Run with: python examples/basic_usage.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent_core import ResearchAgent
from app.models.base import BaseModel
from typing import List, Dict


class MockModel(BaseModel):
    """Mock model for demonstration (no API key required)."""
    
    def generate(self, prompt: str, **kwargs) -> str:
        return "This is a mock response. To use a real model, configure Ollama or OpenAI in .env"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        last_msg = messages[-1]["content"]
        
        # Simulate intelligent responses based on content
        if "calculate" in last_msg.lower() or any(op in last_msg for op in ["+", "-", "*", "/"]):
            return "Action: calculator\nInput: 2 + 2"
        elif "search" in last_msg.lower():
            return "Action: web_search\nInput: latest AI news"
        else:
            return f"Final Answer: I understand you asked: '{last_msg}'. This is a mock response. Configure a real model in .env to get actual AI responses."
    
    def get_embedding(self, text: str) -> List[float]:
        return [0.1] * 384


def main():
    print("🧠 AI Research Assistant - Example Usage\n")
    
    # Initialize agent with mock model (no API key needed)
    print("Initializing agent with mock model...")
    mock_model = MockModel()
    agent = ResearchAgent(model=mock_model)
    
    print(f"✅ Agent initialized with {len(agent.tools)} tools:\n")
    for tool in agent.get_tool_info():
        print(f"  • {tool['name']}: {tool['description']}")
    
    print("\n" + "="*60)
    print("Example 1: Simple Chat")
    print("="*60 + "\n")
    
    response = agent.chat("Hello, what can you do?")
    print(f"User: Hello, what can you do?")
    print(f"Assistant: {response}\n")
    
    print("="*60)
    print("Example 2: Using Calculator Tool")
    print("="*60 + "\n")
    
    response = agent.run("What is 15 * 23?")
    print(f"User: What is 15 * 23?")
    print(f"Assistant: {response}\n")
    
    print("="*60)
    print("Example 3: Direct Tool Usage")
    print("="*60 + "\n")
    
    from app.tools import CalculatorTool, SummarizerTool
    
    calc = CalculatorTool()
    result = calc.run("(100 + 50) * 2")
    print(f"Calculator: (100 + 50) * 2 = {result}")
    
    summarizer = SummarizerTool()
    text = """
    Artificial Intelligence has revolutionized many industries. Machine learning algorithms 
    can now perform tasks that previously required human intelligence. Deep learning models 
    have achieved remarkable success in image recognition, natural language processing, and 
    game playing. The future of AI looks promising with advances in generalized intelligence 
    and ethical AI development.
    """
    summary = summarizer.run(text, max_length=30)
    print(f"\nSummarizer output: {summary[:150]}...\n")
    
    print("="*60)
    print("Example 4: Memory Usage")
    print("="*60 + "\n")
    
    print(f"Current memory length: {len(agent.memory)} messages")
    
    agent.chat("My name is Alice")
    agent.chat("What's my name?")
    
    print(f"After conversation, memory has {len(agent.memory)} messages")
    print(f"Recent context:\n{agent.memory.get_recent_context(4)}\n")
    
    print("="*60)
    print("\n✅ Examples completed!")
    print("\nTo use with real models:")
    print("  1. Configure .env with your API keys")
    print("  2. Use get_model() without mock")
    print("  3. Run: streamlit run app/main.py\n")


if __name__ == "__main__":
    main()
