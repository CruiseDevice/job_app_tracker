"""
Base Tools for AI Agents

Provides reusable tools that agents can use to interact with the system.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
import json

from langchain.tools import Tool

logger = logging.getLogger(__name__)


class DatabaseTools:
    """Tools for interacting with the database"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_all_applications_tool(self) -> Tool:
        """Get all job applications"""

        def _get_applications(query: str = "") -> str:
            """Get all job applications from database. Use empty string for all applications."""
            try:
                applications = self.db.get_all_applications()

                if not applications:
                    return "No job applications found in database."

                # Format applications as readable text
                result = f"Found {len(applications)} job applications:\n\n"
                for app in applications[:10]:  # Limit to 10 for context
                    result += f"- {app.company} - {app.position} (Status: {app.status})\n"
                    result += f"  Applied: {app.application_date}\n"
                    if app.notes:
                        result += f"  Notes: {app.notes[:100]}...\n"
                    result += "\n"

                if len(applications) > 10:
                    result += f"... and {len(applications) - 10} more applications"

                return result

            except Exception as e:
                logger.error(f"Error getting applications: {e}")
                return f"Error retrieving applications: {str(e)}"

        return Tool(
            name="get_all_applications",
            func=_get_applications,
            description="Get all job applications from the database. Returns a list of applications with company, position, status, and dates."
        )

    def get_application_by_id_tool(self) -> Tool:
        """Get specific application by ID"""

        def _get_application(application_id: str) -> str:
            """Get a specific job application by ID."""
            try:
                app_id = int(application_id)
                app = self.db.get_application(app_id)

                if not app:
                    return f"Application with ID {app_id} not found."

                # Format full application details
                result = f"Application Details:\n"
                result += f"ID: {app.id}\n"
                result += f"Company: {app.company}\n"
                result += f"Position: {app.position}\n"
                result += f"Status: {app.status}\n"
                result += f"Applied: {app.application_date}\n"
                result += f"Location: {app.location or 'Not specified'}\n"
                result += f"Salary: {app.salary_range or 'Not specified'}\n"

                if app.job_url:
                    result += f"Job URL: {app.job_url}\n"

                if app.notes:
                    result += f"Notes: {app.notes}\n"

                return result

            except ValueError:
                return f"Invalid application ID: {application_id}. Please provide a numeric ID."
            except Exception as e:
                logger.error(f"Error getting application: {e}")
                return f"Error retrieving application: {str(e)}"

        return Tool(
            name="get_application_by_id",
            func=_get_application,
            description="Get detailed information about a specific job application by its ID. Input should be the numeric application ID."
        )

    def update_application_status_tool(self) -> Tool:
        """Update application status"""

        def _update_status(input_str: str) -> str:
            """Update application status. Input format: 'application_id,new_status' (e.g., '5,interview')"""
            try:
                parts = input_str.split(",")
                if len(parts) != 2:
                    return "Invalid input. Format: 'application_id,new_status' (e.g., '5,interview')"

                app_id = int(parts[0].strip())
                new_status = parts[1].strip()

                # Valid statuses
                valid_statuses = ["applied", "screening", "interview", "assessment", "offer", "rejected", "accepted"]
                if new_status not in valid_statuses:
                    return f"Invalid status. Valid statuses: {', '.join(valid_statuses)}"

                # Update status
                success = self.db.update_application_status(app_id, new_status)

                if success:
                    return f"Successfully updated application {app_id} status to '{new_status}'"
                else:
                    return f"Failed to update application {app_id}. Application may not exist."

            except ValueError:
                return "Invalid input. First part must be a numeric ID."
            except Exception as e:
                logger.error(f"Error updating status: {e}")
                return f"Error updating status: {str(e)}"

        return Tool(
            name="update_application_status",
            func=_update_status,
            description="Update the status of a job application. Input format: 'application_id,new_status'. Valid statuses: applied, screening, interview, assessment, offer, rejected, accepted."
        )

    def search_applications_tool(self) -> Tool:
        """Search applications by company or position"""

        def _search_applications(query: str) -> str:
            """Search for job applications by company name or position title."""
            try:
                all_apps = self.db.get_all_applications()

                if not all_apps:
                    return "No job applications found in database."

                query_lower = query.lower()
                matches = [
                    app for app in all_apps
                    if query_lower in app.company.lower() or query_lower in app.position.lower()
                ]

                if not matches:
                    return f"No applications found matching '{query}'"

                result = f"Found {len(matches)} applications matching '{query}':\n\n"
                for app in matches[:10]:
                    result += f"- ID {app.id}: {app.company} - {app.position} (Status: {app.status})\n"
                    result += f"  Applied: {app.application_date}\n\n"

                if len(matches) > 10:
                    result += f"... and {len(matches) - 10} more matches"

                return result

            except Exception as e:
                logger.error(f"Error searching applications: {e}")
                return f"Error searching applications: {str(e)}"

        return Tool(
            name="search_applications",
            func=_search_applications,
            description="Search for job applications by company name or position title. Input should be the search query (e.g., 'Google' or 'Software Engineer')."
        )


class EmailTools:
    """Tools for email analysis and interaction"""

    def __init__(self, email_processor):
        self.email_processor = email_processor

    def analyze_email_sentiment_tool(self) -> Tool:
        """Analyze email sentiment"""

        def _analyze_sentiment(email_text: str) -> str:
            """Analyze the sentiment and tone of an email."""
            try:
                # Simple sentiment analysis (can be enhanced with actual NLP)
                email_lower = email_text.lower()

                # Positive indicators
                positive_words = ["congratulations", "pleased", "excited", "offer", "selected", "impressed", "next steps"]
                negative_words = ["unfortunately", "regret", "not selected", "decided not to", "not moving forward"]
                urgent_words = ["urgent", "asap", "immediate", "deadline", "time-sensitive"]

                positive_count = sum(1 for word in positive_words if word in email_lower)
                negative_count = sum(1 for word in negative_words if word in email_lower)
                urgent_count = sum(1 for word in urgent_words if word in email_lower)

                # Determine sentiment
                if negative_count > positive_count:
                    sentiment = "Negative (likely rejection)"
                elif positive_count > negative_count:
                    sentiment = "Positive (likely good news)"
                else:
                    sentiment = "Neutral (informational)"

                urgency = "High urgency" if urgent_count > 0 else "Normal priority"

                result = f"Email Sentiment Analysis:\n"
                result += f"Sentiment: {sentiment}\n"
                result += f"Urgency: {urgency}\n"
                result += f"Positive indicators: {positive_count}\n"
                result += f"Negative indicators: {negative_count}\n"

                return result

            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                return f"Error analyzing email sentiment: {str(e)}"

        return Tool(
            name="analyze_email_sentiment",
            func=_analyze_sentiment,
            description="Analyze the sentiment and urgency of an email. Input should be the email text or subject line."
        )

    def extract_action_items_tool(self) -> Tool:
        """Extract action items from email"""

        def _extract_actions(email_text: str) -> str:
            """Extract action items and next steps from an email."""
            try:
                email_lower = email_text.lower()

                # Action indicators
                action_patterns = [
                    "please", "could you", "can you", "need you to", "would you",
                    "schedule", "confirm", "reply", "respond", "submit", "send",
                    "complete", "review", "prepare", "provide"
                ]

                actions = []
                lines = email_text.split("\n")

                for line in lines:
                    line_lower = line.lower()
                    if any(pattern in line_lower for pattern in action_patterns):
                        actions.append(line.strip())

                if not actions:
                    return "No explicit action items found in email."

                result = f"Extracted Action Items ({len(actions)}):\n\n"
                for i, action in enumerate(actions[:5], 1):
                    result += f"{i}. {action}\n"

                return result

            except Exception as e:
                logger.error(f"Error extracting actions: {e}")
                return f"Error extracting action items: {str(e)}"

        return Tool(
            name="extract_action_items",
            func=_extract_actions,
            description="Extract action items and next steps from an email. Input should be the email text."
        )


class AnalyticsTools:
    """Tools for analytics and insights"""

    def __init__(self, db_manager):
        self.db = db_manager

    def get_application_statistics_tool(self) -> Tool:
        """Get application statistics"""

        def _get_statistics(query: str = "") -> str:
            """Get statistics about job applications."""
            try:
                all_apps = self.db.get_all_applications()

                if not all_apps:
                    return "No applications to analyze."

                # Calculate statistics
                total = len(all_apps)
                statuses = {}
                companies = set()

                for app in all_apps:
                    statuses[app.status] = statuses.get(app.status, 0) + 1
                    companies.add(app.company)

                result = f"Job Application Statistics:\n\n"
                result += f"Total Applications: {total}\n"
                result += f"Unique Companies: {len(companies)}\n\n"
                result += f"Status Breakdown:\n"

                for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    result += f"  {status}: {count} ({percentage:.1f}%)\n"

                # Calculate success rate
                positive_statuses = ["interview", "assessment", "offer", "accepted"]
                positive_count = sum(count for status, count in statuses.items() if status in positive_statuses)
                success_rate = (positive_count / total) * 100 if total > 0 else 0

                result += f"\nInterview/Offer Rate: {success_rate:.1f}%\n"

                return result

            except Exception as e:
                logger.error(f"Error getting statistics: {e}")
                return f"Error calculating statistics: {str(e)}"

        return Tool(
            name="get_application_statistics",
            func=_get_statistics,
            description="Get comprehensive statistics about job applications including total count, status breakdown, and success rates."
        )


class UtilityTools:
    """General utility tools"""

    @staticmethod
    def get_current_datetime_tool() -> Tool:
        """Get current date and time"""

        def _get_datetime(query: str = "") -> str:
            """Get the current date and time."""
            now = datetime.now()
            return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}\nDay: {now.strftime('%A')}"

        return Tool(
            name="get_current_datetime",
            func=_get_datetime,
            description="Get the current date and time. Useful for calculating time-sensitive information."
        )

    @staticmethod
    def calculate_days_since_tool() -> Tool:
        """Calculate days since a date"""

        def _calculate_days(date_str: str) -> str:
            """Calculate days since a given date. Input format: YYYY-MM-DD"""
            try:
                from datetime import datetime
                given_date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                now = datetime.now()
                delta = now - given_date
                days = delta.days

                return f"Days since {date_str}: {days} days ({days // 7} weeks)"

            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-01-15)"
            except Exception as e:
                return f"Error calculating days: {str(e)}"

        return Tool(
            name="calculate_days_since",
            func=_calculate_days,
            description="Calculate the number of days since a given date. Input format: YYYY-MM-DD (e.g., 2024-01-15)."
        )


def create_standard_toolset(db_manager, email_processor=None) -> List[Tool]:
    """
    Create a standard set of tools for agents.

    Args:
        db_manager: Database manager instance
        email_processor: Optional email processor instance

    Returns:
        List of Tool objects
    """
    tools = []

    # Database tools
    db_tools = DatabaseTools(db_manager)
    tools.extend([
        db_tools.get_all_applications_tool(),
        db_tools.get_application_by_id_tool(),
        db_tools.update_application_status_tool(),
        db_tools.search_applications_tool(),
    ])

    # Email tools (if processor available)
    if email_processor:
        email_tools = EmailTools(email_processor)
        tools.extend([
            email_tools.analyze_email_sentiment_tool(),
            email_tools.extract_action_items_tool(),
        ])

    # Analytics tools
    analytics_tools = AnalyticsTools(db_manager)
    tools.append(analytics_tools.get_application_statistics_tool())

    # Utility tools
    tools.extend([
        UtilityTools.get_current_datetime_tool(),
        UtilityTools.calculate_days_since_tool(),
    ])

    logger.info(f"Created standard toolset with {len(tools)} tools")
    return tools
