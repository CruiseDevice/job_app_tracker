"""
AI Agent Framework

A comprehensive framework for building autonomous AI agents with:
- Tool support
- Memory management (conversation + semantic)
- ReAct pattern for reasoning and acting
- Cost tracking and monitoring
"""

from agents_framework.core.base_agent import BaseAgent, AgentConfig, AgentResponse
from agents_framework.memory.agent_memory import (
    ConversationMemory,
    SemanticMemory,
    AgentMemoryManager,
)
# Note: base_tools.py uses legacy Tool API and is not compatible with LangGraph
# from agents_framework.tools.base_tools import (
#     DatabaseTools,
#     EmailTools,
#     AnalyticsTools,
#     UtilityTools,
#     create_standard_toolset,
# )
from agents_framework.core.example_agent import JobAnalystAgent, create_job_analyst_agent

__version__ = "0.1.0"

__all__ = [
    # Core
    "BaseAgent",
    "AgentConfig",
    "AgentResponse",
    # Memory
    "ConversationMemory",
    "SemanticMemory",
    "AgentMemoryManager",
    # Example Agent
    "JobAnalystAgent",
    "create_job_analyst_agent",
]
