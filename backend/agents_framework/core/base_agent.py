"""
Base Agent Class for AI Agents

This module provides the foundation for all AI agents in the system.
It includes tool support, memory management, and ReAct pattern implementation.
"""

import logging
import uuid
import time
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, StructuredTool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel
from langgraph.prebuilt import create_react_agent

# Import monitoring systems
from ..monitoring.performance_monitor import global_performance_monitor, AgentMetrics
from ..monitoring.cost_tracker import global_cost_tracker, TokenUsage
from ..monitoring.structured_logger import StructuredLogger, create_log_context

logger = logging.getLogger(__name__)
structured_logger = StructuredLogger(__name__)


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

        # Initialize LLM with callbacks for token tracking
        self.llm = self._initialize_llm()

        # Initialize tools
        self.tools: List[Any] = []
        self._register_tools()

        # Initialize memory
        self.conversation_history: List[Union[HumanMessage, AIMessage, SystemMessage]] = []

        # Initialize agent executor (LangGraph compiled graph)
        self.agent_executor = None
        self._initialize_agent()

        # Tracking (deprecated - use monitoring systems)
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.execution_count = 0

        # Monitoring integration
        self.performance_monitor = global_performance_monitor
        self.cost_tracker = global_cost_tracker

        logger.info(f"✅ Agent '{self.name}' initialized with {len(self.tools)} tools")
        structured_logger.info(
            f"Agent initialized: {self.name}",
            context=create_log_context(agent_name=self.name),
            tools_count=len(self.tools),
            model=self.config.model
        )

    def _initialize_llm(self) -> BaseLanguageModel:
        """Initialize the language model"""
        return ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
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
        # Create a tool using the @tool decorator
        tool_func = tool(func)
        # Override the name and description if they don't match
        tool_func.name = name
        tool_func.description = description
        self.tools.append(tool_func)
        logger.debug(f"Tool '{name}' added to agent '{self.name}'")

    def _initialize_agent(self) -> None:
        """Initialize the ReAct agent with tools using LangGraph"""
        if not self.tools:
            logger.warning(f"Agent '{self.name}' has no tools registered")
            return

        # Create ReAct agent using LangGraph
        # LangGraph's create_react_agent returns a compiled graph
        self.agent_executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
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
        # Generate execution ID for tracking
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        # Create log context
        log_context = create_log_context(
            agent_name=self.name,
            correlation_id=context.get('correlation_id') if context else None
        )

        # Start performance monitoring
        self.performance_monitor.start_execution(
            agent_name=self.name,
            execution_id=execution_id,
            context=context
        )

        try:
            self.execution_count += 1
            logger.info(f"🤖 Agent '{self.name}' starting execution #{self.execution_count}")
            logger.debug(f"Input: {input_text}")

            structured_logger.info(
                f"Agent execution started",
                context=log_context,
                execution_id=execution_id,
                input_length=len(input_text),
                has_context=context is not None
            )

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

            # Track tokens and costs
            input_tokens = len(enhanced_input.split()) * 1.3  # Rough estimate
            output_tokens = 0
            tool_calls_count = 0

            # Run agent if executor is available
            if self.agent_executor:
                result = await self.agent_executor.ainvoke({"messages": [HumanMessage(content=enhanced_input)]})
                # LangGraph returns messages in the result
                messages = result.get("messages", [])
                if messages:
                    output = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
                else:
                    output = ""
                intermediate_steps = []

                # Count tool calls from messages
                tool_calls_count = sum(1 for msg in messages if hasattr(msg, 'tool_calls') and msg.tool_calls)
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

            # Estimate output tokens
            output_tokens = len(output.split()) * 1.3

            # Track costs
            cost_usage = self.cost_tracker.track_usage(
                agent_name=self.name,
                model=self.config.model,
                input_tokens=int(input_tokens),
                output_tokens=int(output_tokens)
            )

            # Update legacy tracking
            self.total_tokens_used += int(input_tokens + output_tokens)
            self.total_cost += cost_usage.total_cost

            # Add to memory
            self.add_message_to_memory(AIMessage(content=output))

            # Calculate execution time
            execution_time = time.time() - start_time

            # End performance monitoring
            metrics = self.performance_monitor.end_execution(
                execution_id=execution_id,
                success=True,
                tokens_used=int(input_tokens + output_tokens),
                cost=cost_usage.total_cost,
                tool_calls=tool_calls_count
            )

            # Create response
            response = AgentResponse(
                output=output,
                agent_name=self.name,
                success=True,
                intermediate_steps=intermediate_steps,
                metadata={
                    "execution_count": self.execution_count,
                    "execution_id": execution_id,
                    "tools_used": tool_calls_count,
                    "context_provided": context is not None,
                    "tokens_used": int(input_tokens + output_tokens),
                    "cost": cost_usage.total_cost,
                    "execution_time": execution_time,
                },
            )

            logger.info(f"✅ Agent '{self.name}' completed successfully")
            logger.debug(f"Output: {output[:200]}...")

            structured_logger.log_agent_execution(
                agent_name=self.name,
                action="run",
                success=True,
                duration=execution_time,
                context=log_context,
                tokens=int(input_tokens + output_tokens),
                cost=cost_usage.total_cost,
                tool_calls=tool_calls_count
            )

            return response

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Agent '{self.name}' execution failed: {e}", exc_info=True)

            # End performance monitoring with error
            self.performance_monitor.end_execution(
                execution_id=execution_id,
                success=False,
                error=str(e)
            )

            structured_logger.error(
                f"Agent execution failed",
                error=e,
                context=log_context,
                execution_id=execution_id,
                duration=execution_time
            )

            response = AgentResponse(
                output="",
                agent_name=self.name,
                success=False,
                error=str(e),
                metadata={
                    "execution_count": self.execution_count,
                    "execution_id": execution_id,
                    "execution_time": execution_time,
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
