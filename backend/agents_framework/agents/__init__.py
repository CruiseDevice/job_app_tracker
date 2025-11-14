"""
Specialized AI Agents

Collection of specialized agents for different tasks.
"""

from agents_framework.agents.email_analyst_agent import (
    EmailAnalystAgent,
    create_email_analyst_agent,
)
from agents_framework.agents.followup_agent import (
    FollowUpAgent,
    create_followup_agent,
)
from agents_framework.agents.resume_writer_agent import (
    ResumeWriterAgent,
    create_resume_writer_agent,
)
from agents_framework.agents.analytics_agent import (
    AnalyticsAgent,
    create_analytics_agent,
)

__all__ = [
    "EmailAnalystAgent",
    "create_email_analyst_agent",
    "FollowUpAgent",
    "create_followup_agent",
    "ResumeWriterAgent",
    "create_resume_writer_agent",
    "AnalyticsAgent",
    "create_analytics_agent",
]
