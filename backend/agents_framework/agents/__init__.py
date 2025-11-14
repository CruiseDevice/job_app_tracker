"""
Specialized AI Agents

Collection of specialized agents for different tasks.
"""

from agents_framework.agents.email_analyst_agent import (
    EmailAnalystAgent,
    create_email_analyst_agent,
)
from agents_framework.agents.application_manager_agent import (
    ApplicationManagerAgent,
    create_application_manager_agent,
)

__all__ = [
    "EmailAnalystAgent",
    "create_email_analyst_agent",
    "ApplicationManagerAgent",
    "create_application_manager_agent",
]
