"""
Agent orchestration core for AI Research Assistant.
"""
from typing import List, Dict, Optional, Any
import re
from app.models import get_model, BaseModel
from app.memory import ConversationMemory
from app.tools import (
    BaseTool,
    CalculatorTool,
    WebSearchTool,
    SummarizerTool,
    DocumentRetrieverTool
)
from app.config import MAX_ITERATIONS, TEMPERATURE
from app.utils import logger


class ResearchAgent:
    """Main agent for orchestrating research tasks."""
    
    def __init__(
        self,
        model: Optional[BaseModel] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[ConversationMemory] = None,
        max_iterations: int = None
    ):
        """
        Initialize research agent.
        
        Args:
            model: Language model instance
            tools: List of available tools
            memory: Conversation memory instance
            max_iterations: Maximum reasoning iterations
        """
        self.model = model or get_model()
        self.memory = memory or ConversationMemory()
        self.max_iterations = max_iterations or MAX_ITERATIONS
        
        # Initialize tools
        if tools is None:
            self.tools = self._initialize_default_tools()
        else:
            self.tools = tools
        
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        logger.info(f"Initialized ResearchAgent with {len(self.tools)} tools")
    
    def _initialize_default_tools(self) -> List[BaseTool]:
        """Initialize default tool set."""
        return [
            CalculatorTool(),
            WebSearchTool(),
            SummarizerTool(model=self.model),
            DocumentRetrieverTool(),
        ]
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt with available tools."""
        tool_descriptions = "\n".join([
            f"- {tool.name}: {tool.description}"
            for tool in self.tools
        ])
        
        return f"""You are a helpful AI research assistant with access to various tools.

Available tools:
{tool_descriptions}

To use a tool, format your response as:
Action: <tool_name>
Input: <tool_input>

After receiving the tool result, you can continue reasoning or provide a final answer.
When you have a final answer, format it as:
Final Answer: <your answer>

Always think step by step and use tools when appropriate."""
    
    def _parse_action(self, text: str) -> Optional[Dict[str, str]]:
        """
        Parse action from agent response.
        
        Args:
            text: Agent response text
        
        Returns:
            Dict with 'action' and 'input' or None
        """
        # Look for Action and Input patterns
        action_match = re.search(r'Action:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        input_match = re.search(r'Input:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        
        if action_match and input_match:
            return {
                'action': action_match.group(1).strip(),
                'input': input_match.group(1).strip()
            }
        
        return None
    
    def _parse_final_answer(self, text: str) -> Optional[str]:
        """
        Parse final answer from agent response.
        
        Args:
            text: Agent response text
        
        Returns:
            Final answer or None
        """
        match = re.search(r'Final Answer:\s*(.+)', text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def run(self, query: str, use_memory: bool = True) -> str:
        """
        Run agent on query with tool use and reasoning.
        
        Args:
            query: User query
            use_memory: Whether to use conversation memory
        
        Returns:
            Agent's final answer
        """
        if use_memory:
            self.memory.add_user_message(query)
        
        system_prompt = self._get_system_prompt()
        conversation = [{"role": "system", "content": system_prompt}]
        
        if use_memory and len(self.memory) > 1:
            # Add recent conversation context (excluding current query)
            for msg in self.memory.get_messages()[:-1]:
                conversation.append(msg)
        
        conversation.append({"role": "user", "content": query})
        
        iteration = 0
        intermediate_steps = []
        
        while iteration < self.max_iterations:
            iteration += 1
            logger.debug(f"Agent iteration {iteration}/{self.max_iterations}")
            
            try:
                # Get agent response
                response = self.model.chat(conversation, temperature=TEMPERATURE)
                logger.debug(f"Agent response: {response[:200]}...")
                
                # Check for final answer
                final_answer = self._parse_final_answer(response)
                if final_answer:
                    logger.info(f"Agent reached final answer in {iteration} iterations")
                    if use_memory:
                        self.memory.add_assistant_message(final_answer)
                    return final_answer
                
                # Parse and execute action
                action = self._parse_action(response)
                if action:
                    tool_name = action['action']
                    tool_input = action['input']
                    
                    if tool_name not in self.tool_map:
                        observation = f"Error: Unknown tool '{tool_name}'. Available tools: {', '.join(self.tool_map.keys())}"
                    else:
                        logger.info(f"Executing tool: {tool_name} with input: {tool_input[:50]}...")
                        tool = self.tool_map[tool_name]
                        observation = tool.run(tool_input)
                    
                    intermediate_steps.append({
                        'action': tool_name,
                        'input': tool_input,
                        'observation': observation
                    })
                    
                    # Add observation to conversation
                    conversation.append({"role": "assistant", "content": response})
                    conversation.append({
                        "role": "user",
                        "content": f"Observation: {observation}\n\nContinue reasoning or provide final answer."
                    })
                else:
                    # No clear action or final answer, treat response as final answer
                    logger.info(f"No action parsed, treating response as final answer")
                    if use_memory:
                        self.memory.add_assistant_message(response)
                    return response
            
            except Exception as e:
                error_msg = f"Error during agent execution: {str(e)}"
                logger.error(error_msg)
                return f"I encountered an error: {str(e)}"
        
        # Max iterations reached
        logger.warning(f"Agent reached max iterations ({self.max_iterations})")
        fallback_response = "I've thought about this extensively but couldn't reach a definitive answer. Let me provide what I found:\n\n"
        
        if intermediate_steps:
            for step in intermediate_steps:
                fallback_response += f"- Used {step['action']}: {step['observation'][:200]}...\n"
        else:
            fallback_response += "No intermediate results were generated."
        
        if use_memory:
            self.memory.add_assistant_message(fallback_response)
        
        return fallback_response
    
    def chat(self, message: str) -> str:
        """
        Simple chat without tool use.
        
        Args:
            message: User message
        
        Returns:
            Assistant response
        """
        self.memory.add_user_message(message)
        
        messages = [
            {"role": "system", "content": "You are a helpful AI research assistant."}
        ]
        messages.extend(self.memory.get_messages())
        
        response = self.model.chat(messages, temperature=TEMPERATURE)
        self.memory.add_assistant_message(response)
        
        return response
    
    def reset_memory(self):
        """Reset conversation memory."""
        self.memory.clear()
        logger.info("Agent memory reset")
    
    def get_tool_info(self) -> List[Dict[str, str]]:
        """Get information about available tools."""
        return [tool.get_info() for tool in self.tools]
