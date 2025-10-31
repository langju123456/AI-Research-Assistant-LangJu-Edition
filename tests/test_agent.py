"""
Tests for the AI Research Agent.
"""
import pytest
from app.agent_core import ResearchAgent
from app.models.base import BaseModel
from app.memory import ConversationMemory
from app.tools import CalculatorTool, SummarizerTool
from typing import List, Dict


class MockModel(BaseModel):
    """Mock model for testing."""
    
    def __init__(self):
        self.responses = []
        self.call_count = 0
    
    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        if self.responses:
            return self.responses.pop(0)
        return "Mock response"
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        self.call_count += 1
        if self.responses:
            return self.responses.pop(0)
        return "Mock chat response"
    
    def get_embedding(self, text: str) -> List[float]:
        return [0.1] * 384


class TestConversationMemory:
    """Test conversation memory."""
    
    def test_add_message(self):
        """Test adding messages to memory."""
        memory = ConversationMemory(max_messages=5)
        
        memory.add_user_message("Hello")
        memory.add_assistant_message("Hi there!")
        
        assert len(memory) == 2
        messages = memory.get_messages()
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
    
    def test_max_messages(self):
        """Test message limit."""
        memory = ConversationMemory(max_messages=3)
        
        for i in range(5):
            memory.add_user_message(f"Message {i}")
        
        assert len(memory) == 3
        messages = memory.get_messages()
        assert messages[0]["content"] == "Message 2"
    
    def test_clear(self):
        """Test clearing memory."""
        memory = ConversationMemory()
        memory.add_user_message("Test")
        memory.clear()
        
        assert len(memory) == 0


class TestCalculatorTool:
    """Test calculator tool."""
    
    def test_basic_calculation(self):
        """Test basic math operations."""
        calc = CalculatorTool()
        
        result = calc.run("2 + 2")
        assert "4" in result
        
        result = calc.run("10 * 5")
        assert "50" in result
    
    def test_invalid_expression(self):
        """Test invalid expressions."""
        calc = CalculatorTool()
        
        result = calc.run("import os")
        assert "Error" in result or "Invalid" in result
    
    def test_complex_expression(self):
        """Test complex math."""
        calc = CalculatorTool()
        
        result = calc.run("(10 + 5) * 2")
        assert "30" in result


class TestSummarizerTool:
    """Test summarizer tool."""
    
    def test_simple_summarize(self):
        """Test simple summarization."""
        summarizer = SummarizerTool()
        
        text = "This is a test. " * 50
        result = summarizer.run(text, max_length=20)
        
        assert len(result) > 0
        assert len(result) < len(text)
    
    def test_empty_text(self):
        """Test with empty text."""
        summarizer = SummarizerTool()
        
        result = summarizer.run("")
        assert "Error" in result


class TestResearchAgent:
    """Test research agent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        assert agent.model == mock_model
        assert len(agent.tools) > 0
        assert isinstance(agent.memory, ConversationMemory)
    
    def test_chat(self):
        """Test simple chat."""
        mock_model = MockModel()
        mock_model.responses = ["Hello! How can I help you?"]
        
        agent = ResearchAgent(model=mock_model)
        response = agent.chat("Hi")
        
        assert len(response) > 0
        assert len(agent.memory) == 2  # user + assistant
    
    def test_reset_memory(self):
        """Test memory reset."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        agent.chat("Test message")
        assert len(agent.memory) > 0
        
        agent.reset_memory()
        assert len(agent.memory) == 0
    
    def test_tool_info(self):
        """Test getting tool information."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        tool_info = agent.get_tool_info()
        assert len(tool_info) > 0
        assert all("name" in info and "description" in info for info in tool_info)


class TestToolParsing:
    """Test action and answer parsing."""
    
    def test_parse_action(self):
        """Test parsing actions from agent response."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        text = "Action: calculator\nInput: 2 + 2"
        action = agent._parse_action(text)
        
        assert action is not None
        assert action["action"] == "calculator"
        assert action["input"] == "2 + 2"
    
    def test_parse_final_answer(self):
        """Test parsing final answers."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        text = "Let me think... Final Answer: The result is 42"
        answer = agent._parse_final_answer(text)
        
        assert answer is not None
        assert "42" in answer
    
    def test_no_action(self):
        """Test when no action is present."""
        mock_model = MockModel()
        agent = ResearchAgent(model=mock_model)
        
        text = "Just a regular response"
        action = agent._parse_action(text)
        
        assert action is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
