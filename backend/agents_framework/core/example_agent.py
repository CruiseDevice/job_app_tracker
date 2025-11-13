"""
Example Agent Implementation

Demonstrates how to create a custom agent using the base agent framework.
This agent helps analyze job applications and provides insights.
"""

import logging
from typing import List

from langchain.tools import Tool

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager

logger = logging.getLogger(__name__)


class JobAnalystAgent(BaseAgent):
    """
    Example agent that analyzes job applications and provides insights.

    This agent demonstrates:
    - How to extend BaseAgent
    - How to register custom tools
    - How to define a system prompt
    - How to use the agent with memory
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Job Analyst",
            description="Analyzes job applications and provides insights on application strategy",
            model="gpt-4o-mini",
            temperature=0.1,
            max_iterations=5,
            verbose=True,
            enable_memory=True,
            memory_k=10,
        )

        # Store database manager
        self.db_manager = db_manager

        # Initialize memory manager
        self.memory_manager = AgentMemoryManager(
            agent_name="job_analyst",
            max_conversation_messages=20,
            enable_semantic=True
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("Job Analyst Agent initialized")

    def _register_tools(self) -> None:
        """Register tools specific to this agent"""

        # Tool 1: Get application insights
        def get_insights(query: str = "") -> str:
            """Analyze all applications and provide strategic insights."""
            try:
                applications = self.db_manager.get_all_applications()

                if not applications:
                    return "No applications to analyze. Start by adding some job applications!"

                # Calculate metrics
                total = len(applications)
                statuses = {}
                companies = set()
                positions = set()

                for app in applications:
                    statuses[app.status] = statuses.get(app.status, 0) + 1
                    companies.add(app.company)
                    positions.add(app.position)

                # Generate insights
                insights = f"📊 Job Search Insights:\n\n"
                insights += f"Total Applications: {total}\n"
                insights += f"Companies Applied: {len(companies)}\n"
                insights += f"Different Positions: {len(positions)}\n\n"

                insights += "Status Distribution:\n"
                for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    insights += f"  • {status.capitalize()}: {count} ({percentage:.1f}%)\n"

                # Calculate response rate
                responded = sum(count for status, count in statuses.items()
                                if status in ['screening', 'interview', 'assessment', 'offer'])
                response_rate = (responded / total) * 100 if total > 0 else 0

                insights += f"\n📈 Response Rate: {response_rate:.1f}%\n"

                # Provide recommendations
                insights += "\n💡 Recommendations:\n"

                if response_rate < 10:
                    insights += "  • Your response rate is low. Consider tailoring your applications more carefully.\n"
                elif response_rate > 30:
                    insights += "  • Great response rate! You're doing well.\n"

                if len(companies) < total * 0.5:
                    insights += "  • You're applying to the same companies multiple times. Diversify your targets.\n"

                return insights

            except Exception as e:
                logger.error(f"Error getting insights: {e}")
                return f"Error generating insights: {str(e)}"

        self.add_tool(
            name="get_application_insights",
            func=get_insights,
            description="Analyze all job applications and provide strategic insights about the job search."
        )

        # Tool 2: Find stale applications
        def find_stale_applications(days_str: str = "14") -> str:
            """Find applications with no updates in specified days."""
            try:
                from datetime import datetime, timedelta

                days = int(days_str) if days_str else 14
                applications = self.db_manager.get_all_applications()

                if not applications:
                    return "No applications to check."

                cutoff_date = datetime.now() - timedelta(days=days)
                stale = []

                for app in applications:
                    if app.status in ['applied', 'screening']:  # Only check active statuses
                        if app.application_date < cutoff_date:
                            days_old = (datetime.now() - app.application_date).days
                            stale.append((app, days_old))

                if not stale:
                    return f"No stale applications found (older than {days} days)."

                result = f"Found {len(stale)} stale applications (>{ days} days old):\n\n"
                for app, age in sorted(stale, key=lambda x: x[1], reverse=True)[:10]:
                    result += f"• {app.company} - {app.position}\n"
                    result += f"  Applied {age} days ago (Status: {app.status})\n"
                    result += f"  Consider: Send a follow-up email\n\n"

                return result

            except ValueError:
                return "Invalid input. Please provide number of days (e.g., '14')"
            except Exception as e:
                logger.error(f"Error finding stale applications: {e}")
                return f"Error: {str(e)}"

        self.add_tool(
            name="find_stale_applications",
            func=find_stale_applications,
            description="Find job applications that haven't been updated in a while and may need follow-up. Input: number of days (default: 14)."
        )

        # Tool 3: Get top companies
        def get_top_companies(limit_str: str = "5") -> str:
            """Get the companies you've applied to most."""
            try:
                limit = int(limit_str) if limit_str else 5
                applications = self.db_manager.get_all_applications()

                if not applications:
                    return "No applications to analyze."

                company_counts = {}
                for app in applications:
                    company_counts[app.company] = company_counts.get(app.company, 0) + 1

                sorted_companies = sorted(company_counts.items(), key=lambda x: x[1], reverse=True)

                result = f"Top {min(limit, len(sorted_companies))} Companies:\n\n"
                for i, (company, count) in enumerate(sorted_companies[:limit], 1):
                    result += f"{i}. {company}: {count} application(s)\n"

                return result

            except ValueError:
                return "Invalid input. Please provide a number (e.g., '5')"
            except Exception as e:
                return f"Error: {str(e)}"

        self.add_tool(
            name="get_top_companies",
            func=get_top_companies,
            description="Get the list of companies you've applied to most frequently. Input: number of companies to show (default: 5)."
        )

    def get_system_prompt(self) -> str:
        """Define the agent's personality and capabilities"""
        return """You are a Job Application Analyst Agent, an expert in helping job seekers optimize their application strategy.

Your role is to:
1. Analyze job application data and provide actionable insights
2. Identify patterns and trends in the job search process
3. Suggest improvements to increase success rates
4. Recommend follow-up actions for pending applications
5. Help users understand their job search metrics

You have access to tools that allow you to:
- Analyze application statistics and trends
- Find applications that need follow-up
- Identify the most frequently targeted companies
- Calculate success rates and response rates

When responding:
- Be encouraging and supportive
- Provide specific, actionable recommendations
- Use data to back up your suggestions
- Keep responses concise and focused
- Use emojis sparingly for emphasis

Always try to use the available tools to get real data before making recommendations.
"""


def create_job_analyst_agent(db_manager) -> JobAnalystAgent:
    """Factory function to create a Job Analyst Agent"""
    return JobAnalystAgent(db_manager)
