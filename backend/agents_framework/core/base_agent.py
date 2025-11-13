"""
Base Agent Class for AI Agents

This module provides the foundation for all AI agents in the system.
It includes tool support, memory management, and ReAct pattern implementation.
"""

import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel

logger = logging.getLogger(__name__)


class AgentConfig:
    """Configuration for an agent"""

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_iterations: int = 10,
        max_execution_time: Optional[float] = None,
        verbose: bool = True,
        enable_memory: bool = True,
        memory_k: int = 10,  # Number of messages to keep in memory
    ):
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.max_execution_time = max_execution_time
        self.verbose = verbose
        self.enable_memory = enable_memory
        self.memory_k = memory_k


class AgentResponse:
    """Structured response from an agent"""

    def __init__(
        self,
        output: str,
        agent_name: str,
        success: bool = True,
        intermediate_steps: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.output = output
        self.agent_name = agent_name
        self.success = success
        self.intermediate_steps = intermediate_steps or []
        self.metadata = metadata or {}
        self.error = error
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "output": self.output,
            "agent_name": self.agent_name,
            "success": self.success,
            "intermediate_steps": self.intermediate_steps,
            "metadata": self.metadata,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Features:
    - Tool support with LangChain tools
    - Memory management (conversation history)
    - ReAct pattern for reasoning and acting
    - Structured output
    - Error handling and logging
    - Cost tracking
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.description = config.description

        # Initialize LLM
        self.llm = self._initialize_llm()

        # Initialize tools
        self.tools: List[Tool] = []
        self._register_tools()

        # Initialize memory
        self.conversation_history: List[Union[HumanMessage, AIMessage, SystemMessage]] = []

        # Initialize agent executor
        self.agent_executor: Optional[AgentExecutor] = None
        self._initialize_agent()

        # Tracking
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.execution_count = 0

        logger.info(f"✅ Agent '{self.name}' initialized with {len(self.tools)} tools")

    def _initialize_llm(self) -> BaseLanguageModel:
        """Initialize the language model"""
        return ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            model_kwargs={"response_format": {"type": "text"}},
        )

    @abstractmethod
    def _register_tools(self) -> None:
        """
        Register tools that this agent can use.
        Subclasses must implement this method.
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Subclasses must implement this method.
        """
        pass

    def add_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        return_direct: bool = False
    ) -> None:
        """Add a tool to the agent's toolkit"""
        tool = Tool(
            name=name,
            func=func,
            description=description,
            return_direct=return_direct,
        )
        self.tools.append(tool)
        logger.debug(f"Tool '{name}' added to agent '{self.name}'")

    def _initialize_agent(self) -> None:
        """Initialize the ReAct agent with tools"""
        if not self.tools:
            logger.warning(f"Agent '{self.name}' has no tools registered")
            return

        # Create ReAct prompt template
        template = '''Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}'''

        prompt = PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
            },
        )

        # Create ReAct agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.config.verbose,
            max_iterations=self.config.max_iterations,
            max_execution_time=self.config.max_execution_time,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

    def add_message_to_memory(self, message: Union[HumanMessage, AIMessage, SystemMessage]) -> None:
        """Add a message to conversation memory"""
        if not self.config.enable_memory:
            return

        self.conversation_history.append(message)

        # Keep only last K messages to avoid context overflow
        if len(self.conversation_history) > self.config.memory_k * 2:  # *2 for human+ai pairs
            self.conversation_history = self.conversation_history[-self.config.memory_k * 2:]

    def get_memory_context(self) -> str:
        """Get conversation history as context string"""
        if not self.config.enable_memory or not self.conversation_history:
            return ""

        context_parts = ["Previous conversation:"]
        for msg in self.conversation_history[-6:]:  # Last 3 exchanges
            if isinstance(msg, HumanMessage):
                context_parts.append(f"Human: {msg.content}")
            elif isinstance(msg, AIMessage):
                context_parts.append(f"Assistant: {msg.content}")

        return "\n".join(context_parts)

    def clear_memory(self) -> None:
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info(f"Memory cleared for agent '{self.name}'")

    async def run(
        self,
        input_text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Run the agent with the given input.

        Args:
            input_text: The question or task for the agent
            context: Optional context dictionary with additional information

        Returns:
            AgentResponse object with the agent's output
        """
        try:
            self.execution_count += 1
            logger.info(f"🤖 Agent '{self.name}' starting execution #{self.execution_count}")
            logger.debug(f"Input: {input_text}")

            # Add context to input if provided
            enhanced_input = input_text
            if context:
                context_str = "\n\nContext:\n" + "\n".join(
                    [f"- {k}: {v}" for k, v in context.items()]
                )
                enhanced_input = input_text + context_str

            # Add memory context
            memory_context = self.get_memory_context()
            if memory_context:
                enhanced_input = memory_context + "\n\n" + enhanced_input

            # Add to memory
            self.add_message_to_memory(HumanMessage(content=input_text))

            # Run agent if executor is available
            if self.agent_executor:
                result = await self.agent_executor.ainvoke({"input": enhanced_input})
                output = result.get("output", "")
                intermediate_steps = result.get("intermediate_steps", [])
            else:
                # Fallback to direct LLM call if no tools
                system_prompt = self.get_system_prompt()
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=enhanced_input)
                ]
                response = await self.llm.ainvoke(messages)
                output = response.content
                intermediate_steps = []

            # Add to memory
            self.add_message_to_memory(AIMessage(content=output))

            # Create response
            response = AgentResponse(
                output=output,
                agent_name=self.name,
                success=True,
                intermediate_steps=intermediate_steps,
                metadata={
                    "execution_count": self.execution_count,
                    "tools_used": len(intermediate_steps),
                    "context_provided": context is not None,
                },
            )

            logger.info(f"✅ Agent '{self.name}' completed successfully")
            logger.debug(f"Output: {output[:200]}...")

            return response

        except Exception as e:
            logger.error(f"❌ Agent '{self.name}' execution failed: {e}", exc_info=True)

            response = AgentResponse(
                output="",
                agent_name=self.name,
                success=False,
                error=str(e),
                metadata={
                    "execution_count": self.execution_count,
                },
            )

            return response

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.name,
            "description": self.description,
            "execution_count": self.execution_count,
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "tools_count": len(self.tools),
            "tools": [tool.name for tool in self.tools],
            "memory_size": len(self.conversation_history),
        }

    def __repr__(self) -> str:
        return f"<Agent '{self.name}' with {len(self.tools)} tools>"
