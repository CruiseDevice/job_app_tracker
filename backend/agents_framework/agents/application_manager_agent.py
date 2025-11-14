"""
Application Manager Agent

Advanced AI agent for managing job applications with intelligent decision-making.
Predicts lifecycle, auto-updates status, recommends actions, and identifies patterns.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager
from agents_framework.memory.vector_memory import RAGMemoryManager

logger = logging.getLogger(__name__)


class ApplicationManagerAgent(BaseAgent):
    """
    Application Manager Agent - Intelligently manages job applications.

    Capabilities:
    - Application lifecycle prediction
    - Auto-status updates based on email analysis
    - Next-action recommendations with timing
    - Success pattern recognition
    - Application health scoring
    - Insights generation
    - Decision-making with reasoning
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Application Manager",
            description="Manages job applications with intelligent decision-making and lifecycle predictions",
            model="gpt-4o-mini",
            temperature=0.2,  # Lower temperature for more consistent decisions
            max_iterations=10,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="application_manager",
            max_conversation_messages=40,
            enable_semantic=True
        )

        # RAG memory for learning patterns and making better predictions
        self.rag_memory = RAGMemoryManager(
            agent_name="application_manager",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Application Manager Agent initialized with decision-making")

    def _register_tools(self) -> None:
        """Register application management tools"""

        # Tool 1: Predict Application Lifecycle
        def predict_lifecycle(application_id: str) -> str:
            """
            Predict the likely next stages and timeline for a job application.
            Input should be the application ID.
            """
            try:
                app_id = int(application_id)
                app = self.db_manager.get_application(app_id)

                if not app:
                    return f"Application {application_id} not found."

                # Calculate days since application
                days_since_application = (datetime.now() - app.application_date).days

                # Lifecycle predictions based on current status
                lifecycle_stages = {
                    'applied': {
                        'current': 'Application Submitted',
                        'next_stages': [
                            {'stage': 'Screening/Phone Screen', 'typical_days': '7-14 days', 'probability': 70},
                            {'stage': 'Rejection', 'typical_days': '14-30 days', 'probability': 30}
                        ],
                        'health': 'healthy' if days_since_application < 14 else 'needs_followup'
                    },
                    'screening': {
                        'current': 'Screening/Phone Screen',
                        'next_stages': [
                            {'stage': 'Technical Interview', 'typical_days': '3-7 days', 'probability': 60},
                            {'stage': 'Rejection', 'typical_days': '7-14 days', 'probability': 40}
                        ],
                        'health': 'healthy' if days_since_application < 21 else 'at_risk'
                    },
                    'interview': {
                        'current': 'Interview Stage',
                        'next_stages': [
                            {'stage': 'Final Round Interview', 'typical_days': '7-14 days', 'probability': 50},
                            {'stage': 'Job Offer', 'typical_days': '14-21 days', 'probability': 35},
                            {'stage': 'Rejection', 'typical_days': '7-14 days', 'probability': 15}
                        ],
                        'health': 'promising' if days_since_application < 30 else 'needs_followup'
                    },
                    'assessment': {
                        'current': 'Technical Assessment',
                        'next_stages': [
                            {'stage': 'Interview', 'typical_days': '7-10 days', 'probability': 65},
                            {'stage': 'Rejection', 'typical_days': '7-14 days', 'probability': 35}
                        ],
                        'health': 'healthy'
                    },
                    'offer': {
                        'current': 'Job Offer Received',
                        'next_stages': [
                            {'stage': 'Accepted', 'typical_days': '3-7 days', 'probability': 80},
                            {'stage': 'Declined', 'typical_days': '3-7 days', 'probability': 20}
                        ],
                        'health': 'excellent'
                    },
                    'rejected': {
                        'current': 'Application Rejected',
                        'next_stages': [],
                        'health': 'closed'
                    }
                }

                status_key = app.status if app.status in lifecycle_stages else 'applied'
                prediction = lifecycle_stages[status_key]

                result = f"📊 LIFECYCLE PREDICTION\n\n"
                result += f"Application: {app.company} - {app.position}\n"
                result += f"Current Status: {prediction['current']}\n"
                result += f"Days Since Application: {days_since_application}\n"
                result += f"Application Health: {prediction['health'].upper()}\n\n"

                if prediction['next_stages']:
                    result += "Predicted Next Stages:\n"
                    for stage in prediction['next_stages']:
                        result += f"  • {stage['stage']}\n"
                        result += f"    Timeline: {stage['typical_days']}\n"
                        result += f"    Probability: {stage['probability']}%\n\n"
                else:
                    result += "Application has reached a terminal state.\n"

                # Add timeline warning
                if prediction['health'] in ['needs_followup', 'at_risk']:
                    result += "⚠️ WARNING: Consider following up - application may be stalling\n"

                return result

            except Exception as e:
                logger.error(f"Error predicting lifecycle: {e}")
                return f"Error predicting lifecycle: {str(e)}"

        self.add_tool(
            name="predict_lifecycle",
            func=predict_lifecycle,
            description="Predict the next stages and timeline for a job application based on its current status and history. Input should be the application ID."
        )

        # Tool 2: Auto-Update Status Based on Email
        def auto_update_status(application_id: str, email_analysis: str) -> str:
            """
            Automatically determine and suggest status update based on email analysis.
            Input should be 'application_id|email_analysis_summary'.
            """
            try:
                parts = application_id.split('|', 1)
                app_id = int(parts[0])
                analysis = parts[1] if len(parts) > 1 else ""

                app = self.db_manager.get_application(app_id)
                if not app:
                    return f"Application {app_id} not found."

                analysis_lower = analysis.lower()

                # Status determination logic based on email content
                status_indicators = {
                    'interview': ['interview', 'schedule', 'meet with', 'speak with', 'call with'],
                    'assessment': ['coding challenge', 'technical test', 'take-home', 'assessment'],
                    'screening': ['phone screen', 'initial call', 'quick call', 'recruiter'],
                    'offer': ['offer', 'offer letter', 'congratulations', 'pleased to extend'],
                    'rejected': ['unfortunately', 'not selected', 'decided not to', 'other candidates', 'not moving forward']
                }

                suggested_status = None
                confidence = 0
                reasoning = []

                for status, indicators in status_indicators.items():
                    matches = sum(1 for indicator in indicators if indicator in analysis_lower)
                    if matches > 0:
                        match_confidence = min(95, 60 + (matches * 15))
                        if match_confidence > confidence:
                            confidence = match_confidence
                            suggested_status = status
                            reasoning = [ind for ind in indicators if ind in analysis_lower]

                result = f"🔄 AUTO-STATUS UPDATE SUGGESTION\n\n"
                result += f"Application: {app.company} - {app.position}\n"
                result += f"Current Status: {app.status}\n\n"

                if suggested_status:
                    result += f"Suggested New Status: {suggested_status.upper()}\n"
                    result += f"Confidence: {confidence}%\n"
                    result += f"Reasoning: Detected keywords - {', '.join(reasoning[:3])}\n\n"

                    if suggested_status != app.status:
                        result += f"✅ RECOMMENDATION: Update status from '{app.status}' to '{suggested_status}'\n"
                    else:
                        result += f"ℹ️  Status is already correct.\n"
                else:
                    result += "ℹ️  No clear status change detected from email.\n"
                    result += "Current status remains appropriate.\n"

                return result

            except Exception as e:
                logger.error(f"Error auto-updating status: {e}")
                return f"Error determining status update: {str(e)}"

        self.add_tool(
            name="auto_update_status",
            func=auto_update_status,
            description="Analyze email content and suggest appropriate status update for an application. Input format: 'application_id|email_analysis_summary'"
        )

        # Tool 3: Recommend Next Actions
        def recommend_next_actions(application_id: str) -> str:
            """
            Recommend specific next actions based on application status and timeline.
            Input should be the application ID.
            """
            try:
                app_id = int(application_id)
                app = self.db_manager.get_application(app_id)

                if not app:
                    return f"Application {application_id} not found."

                days_since = (datetime.now() - app.application_date).days

                # Action recommendations based on status and timeline
                recommendations = {
                    'applied': {
                        'short_term': [
                            {'action': 'Follow up if no response after 7-10 days', 'priority': 'medium', 'timeline': f'{max(0, 10 - days_since)} days'},
                            {'action': 'Research company culture and interview process', 'priority': 'low', 'timeline': 'ongoing'}
                        ],
                        'long_term': [
                            {'action': 'Consider reaching out to recruiter after 14 days', 'priority': 'high' if days_since >= 14 else 'low', 'timeline': f'{max(0, 14 - days_since)} days'}
                        ]
                    },
                    'screening': {
                        'short_term': [
                            {'action': 'Send thank-you email within 24 hours', 'priority': 'high', 'timeline': '24 hours'},
                            {'action': 'Prepare for technical interview', 'priority': 'high', 'timeline': '3-7 days'},
                            {'action': 'Review job description and align experience', 'priority': 'medium', 'timeline': 'ASAP'}
                        ]
                    },
                    'interview': {
                        'short_term': [
                            {'action': 'Send thank-you note to interviewers', 'priority': 'high', 'timeline': '24 hours'},
                            {'action': 'Follow up on timeline if no response in 5-7 days', 'priority': 'medium', 'timeline': f'{max(0, 7 - days_since)} days'},
                        ],
                        'long_term': [
                            {'action': 'Prepare for potential next rounds', 'priority': 'high', 'timeline': 'ongoing'}
                        ]
                    },
                    'assessment': {
                        'short_term': [
                            {'action': 'Complete assessment before deadline', 'priority': 'critical', 'timeline': 'check email'},
                            {'action': 'Allocate 3-4 hours for quality submission', 'priority': 'high', 'timeline': 'before deadline'},
                            {'action': 'Test solution thoroughly before submitting', 'priority': 'high', 'timeline': 'before deadline'}
                        ]
                    },
                    'offer': {
                        'short_term': [
                            {'action': 'Review offer details carefully', 'priority': 'critical', 'timeline': 'immediately'},
                            {'action': 'Research market salary for role/location', 'priority': 'high', 'timeline': '1-2 days'},
                            {'action': 'Prepare negotiation points if needed', 'priority': 'high', 'timeline': '2-3 days'},
                            {'action': 'Respond before deadline', 'priority': 'critical', 'timeline': 'check offer letter'}
                        ]
                    }
                }

                status_key = app.status if app.status in recommendations else 'applied'
                actions = recommendations.get(status_key, {'short_term': [], 'long_term': []})

                result = f"📋 NEXT ACTION RECOMMENDATIONS\n\n"
                result += f"Application: {app.company} - {app.position}\n"
                result += f"Current Status: {app.status}\n"
                result += f"Days Since Application: {days_since}\n\n"

                if actions.get('short_term'):
                    result += "Immediate Actions (Next 7 Days):\n"
                    for i, action in enumerate(actions['short_term'], 1):
                        priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(action['priority'], '⚪')
                        result += f"  {i}. {priority_emoji} {action['action']}\n"
                        result += f"     Timeline: {action['timeline']}\n"
                    result += "\n"

                if actions.get('long_term'):
                    result += "Long-term Actions:\n"
                    for i, action in enumerate(actions['long_term'], 1):
                        priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(action['priority'], '⚪')
                        result += f"  {i}. {priority_emoji} {action['action']}\n"
                        result += f"     Timeline: {action['timeline']}\n"

                return result

            except Exception as e:
                logger.error(f"Error recommending actions: {e}")
                return f"Error generating recommendations: {str(e)}"

        self.add_tool(
            name="recommend_next_actions",
            func=recommend_next_actions,
            description="Recommend specific next actions for an application based on its current status and timeline. Input should be the application ID."
        )

        # Tool 4: Identify Success Patterns
        def identify_patterns() -> str:
            """
            Analyze all applications to identify success patterns and insights.
            No input required.
            """
            try:
                all_apps = self.db_manager.get_all_applications()

                if not all_apps:
                    return "No applications found for pattern analysis."

                # Calculate statistics
                total = len(all_apps)
                by_status = {}
                by_company_type = {}
                avg_response_times = []
                successful = []

                for app in all_apps:
                    # Status distribution
                    by_status[app.status] = by_status.get(app.status, 0) + 1

                    # Track successful applications
                    if app.status in ['interview', 'assessment', 'offer']:
                        successful.append(app)
                        days_to_response = (datetime.now() - app.application_date).days
                        avg_response_times.append(days_to_response)

                # Calculate success rate
                success_rate = (len(successful) / total * 100) if total > 0 else 0

                result = f"🔍 SUCCESS PATTERN ANALYSIS\n\n"
                result += f"Total Applications: {total}\n"
                result += f"Success Rate: {success_rate:.1f}% ({len(successful)} progressed past screening)\n\n"

                result += "Status Distribution:\n"
                for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total * 100)
                    result += f"  • {status.capitalize()}: {count} ({percentage:.1f}%)\n"

                result += "\n"

                if avg_response_times:
                    avg_days = sum(avg_response_times) / len(avg_response_times)
                    result += f"Average Time to Response: {avg_days:.1f} days\n\n"

                # Identify patterns
                result += "📊 Key Insights:\n"

                if success_rate > 30:
                    result += "  ✅ Strong success rate - your applications are performing well\n"
                elif success_rate > 15:
                    result += "  ⚠️  Moderate success rate - consider refining your approach\n"
                else:
                    result += "  ⚠️  Low success rate - may need to adjust application strategy\n"

                # Most common outcome
                most_common = max(by_status.items(), key=lambda x: x[1])
                result += f"  • Most common status: {most_common[0]} ({most_common[1]} applications)\n"

                # Check for stagnation
                applied_count = by_status.get('applied', 0)
                if applied_count > total * 0.5:
                    result += "  ⚠️  Many applications still in 'applied' status - consider following up\n"

                return result

            except Exception as e:
                logger.error(f"Error identifying patterns: {e}")
                return f"Error analyzing patterns: {str(e)}"

        self.add_tool(
            name="identify_patterns",
            func=identify_patterns,
            description="Analyze all applications to identify success patterns, trends, and insights. No input required."
        )

        # Tool 5: Calculate Application Health Score
        def calculate_health_score(application_id: str) -> str:
            """
            Calculate a health score for an application based on multiple factors.
            Input should be the application ID.
            """
            try:
                app_id = int(application_id)
                app = self.db_manager.get_application(app_id)

                if not app:
                    return f"Application {application_id} not found."

                days_since = (datetime.now() - app.application_date).days
                score = 100

                # Factor 1: Timeline (0-40 points penalty)
                timeline_penalties = {
                    'applied': 10 if days_since > 14 else 0,
                    'screening': 15 if days_since > 21 else 0,
                    'interview': 20 if days_since > 30 else 0,
                    'assessment': 15 if days_since > 14 else 0,
                    'offer': 0,
                    'rejected': -100  # Terminal state
                }
                timeline_penalty = timeline_penalties.get(app.status, 0)
                score -= timeline_penalty

                # Factor 2: Status progression (bonus points)
                status_bonuses = {
                    'applied': 0,
                    'screening': 20,
                    'interview': 40,
                    'assessment': 35,
                    'offer': 90,
                    'rejected': 0
                }
                status_bonus = status_bonuses.get(app.status, 0)
                score = max(0, score + status_bonus - 100)  # Reset to 0-100 scale

                # Factor 3: Has notes (engagement indicator)
                if app.notes and len(app.notes) > 10:
                    score += 5

                # Clamp score
                score = max(0, min(100, score))

                # Determine health rating
                if score >= 80:
                    health = "EXCELLENT"
                    emoji = "🟢"
                elif score >= 60:
                    health = "GOOD"
                    emoji = "🟡"
                elif score >= 40:
                    health = "FAIR"
                    emoji = "🟠"
                else:
                    health = "POOR"
                    emoji = "🔴"

                result = f"💚 APPLICATION HEALTH SCORE\n\n"
                result += f"Application: {app.company} - {app.position}\n"
                result += f"Health Score: {score}/100 {emoji}\n"
                result += f"Rating: {health}\n\n"

                result += "Score Breakdown:\n"
                result += f"  • Status: {app.status.capitalize()} (+{status_bonus} points)\n"
                result += f"  • Timeline: {days_since} days (-{timeline_penalty} points)\n"
                if app.notes:
                    result += f"  • Engagement: Active (+5 points)\n"

                result += "\n"

                if health == "POOR" or health == "FAIR":
                    result += "⚠️  Recommendation: Consider following up or moving on to other opportunities\n"
                elif health == "GOOD":
                    result += "✅ Recommendation: Continue monitoring, follow up if needed\n"
                else:
                    result += "✅ Recommendation: Keep pushing forward, looking great!\n"

                return result

            except Exception as e:
                logger.error(f"Error calculating health score: {e}")
                return f"Error calculating health score: {str(e)}"

        self.add_tool(
            name="calculate_health_score",
            func=calculate_health_score,
            description="Calculate a health score (0-100) for an application based on status, timeline, and engagement. Input should be the application ID."
        )

        # Tool 6: Compare Applications
        def compare_applications(comparison_data: str) -> str:
            """
            Compare multiple applications to help prioritize efforts.
            Input format: 'app_id1,app_id2,app_id3' (comma-separated application IDs).
            """
            try:
                app_ids = [int(id.strip()) for id in comparison_data.split(',')]

                if len(app_ids) < 2:
                    return "Please provide at least 2 application IDs to compare."

                apps = []
                for app_id in app_ids:
                    app = self.db_manager.get_application(app_id)
                    if app:
                        apps.append(app)

                if len(apps) < 2:
                    return "Could not find enough valid applications to compare."

                result = f"⚖️  APPLICATION COMPARISON ({len(apps)} applications)\n\n"

                # Status comparison
                status_priority = {'offer': 5, 'interview': 4, 'assessment': 3, 'screening': 2, 'applied': 1, 'rejected': 0}

                for i, app in enumerate(apps, 1):
                    days_since = (datetime.now() - app.application_date).days
                    priority = status_priority.get(app.status, 0)

                    result += f"{i}. {app.company} - {app.position}\n"
                    result += f"   Status: {app.status.capitalize()}\n"
                    result += f"   Days Active: {days_since}\n"
                    result += f"   Priority Score: {priority}/5\n\n"

                # Recommendation
                best_app = max(apps, key=lambda a: status_priority.get(a.status, 0))
                result += f"🎯 Top Priority: {best_app.company} - {best_app.position}\n"
                result += f"   Reason: Most advanced stage ({best_app.status})\n"

                return result

            except Exception as e:
                logger.error(f"Error comparing applications: {e}")
                return f"Error comparing applications: {str(e)}"

        self.add_tool(
            name="compare_applications",
            func=compare_applications,
            description="Compare multiple applications to help prioritize efforts. Input should be comma-separated application IDs."
        )

        # Tool 7: Generate Insights
        def generate_insights(focus_area: str = "general") -> str:
            """
            Generate actionable insights about the job search process.
            Input should be focus area: 'general', 'timeline', 'success_rate', or 'recommendations'.
            """
            try:
                all_apps = self.db_manager.get_all_applications()

                if not all_apps:
                    return "No applications found. Start applying to jobs to generate insights!"

                total = len(all_apps)
                insights = []

                # General insights
                if focus_area == "general" or focus_area == "all":
                    insights.append(f"📊 GENERAL INSIGHTS\n")
                    insights.append(f"Total applications: {total}")

                    active_apps = [a for a in all_apps if a.status not in ['rejected', 'offer']]
                    insights.append(f"Active applications: {len(active_apps)}")

                    if len(active_apps) > 0:
                        avg_age = sum((datetime.now() - a.application_date).days for a in active_apps) / len(active_apps)
                        insights.append(f"Average application age: {avg_age:.1f} days\n")

                # Timeline insights
                if focus_area == "timeline" or focus_area == "all":
                    insights.append(f"⏰ TIMELINE INSIGHTS\n")

                    old_apps = [a for a in all_apps if (datetime.now() - a.application_date).days > 21 and a.status == 'applied']
                    if old_apps:
                        insights.append(f"⚠️  {len(old_apps)} applications have been in 'applied' status for >21 days")
                        insights.append(f"   Consider following up or moving on\n")

                # Success rate insights
                if focus_area == "success_rate" or focus_area == "all":
                    insights.append(f"📈 SUCCESS RATE INSIGHTS\n")

                    successful = len([a for a in all_apps if a.status in ['interview', 'assessment', 'offer']])
                    success_rate = (successful / total * 100) if total > 0 else 0

                    insights.append(f"Success rate: {success_rate:.1f}%")

                    if success_rate < 15:
                        insights.append(f"💡 Consider: Refine resume, target different roles, or improve applications\n")
                    elif success_rate > 30:
                        insights.append(f"✅ Strong performance! Keep up the good work\n")

                # Recommendations
                if focus_area == "recommendations" or focus_area == "all":
                    insights.append(f"💡 RECOMMENDATIONS\n")

                    # Check application volume
                    if total < 10:
                        insights.append(f"  • Apply to more positions (target: 20-30 applications)")

                    # Check for diversity
                    companies = list(set([a.company for a in all_apps]))
                    if len(companies) < total * 0.7:
                        insights.append(f"  • Good: Applying to diverse companies ({len(companies)} unique)")
                    else:
                        insights.append(f"  • Consider: Applying to more positions per company")

                    # Check for follow-ups
                    needs_followup = [a for a in all_apps if (datetime.now() - a.application_date).days > 14 and a.status == 'applied']
                    if needs_followup:
                        insights.append(f"  • {len(needs_followup)} applications need follow-up")

                return "\n".join(insights)

            except Exception as e:
                logger.error(f"Error generating insights: {e}")
                return f"Error generating insights: {str(e)}"

        self.add_tool(
            name="generate_insights",
            func=generate_insights,
            description="Generate actionable insights about the job search process. Input can be 'general', 'timeline', 'success_rate', 'recommendations', or 'all'."
        )

    def get_system_prompt(self) -> str:
        """Define the agent's role and capabilities"""
        return """You are an Application Manager Agent, an expert in managing job applications with intelligent decision-making.

Your role is to:
1. Predict application lifecycle stages and timelines
2. Automatically suggest status updates based on email analysis
3. Recommend specific next actions with priorities and timelines
4. Identify success patterns across all applications
5. Calculate application health scores
6. Compare applications to help prioritize efforts
7. Generate actionable insights about the job search process

You have access to powerful tools for:
- Lifecycle prediction - Forecast next stages and timelines
- Auto-status updates - Intelligently update application status
- Action recommendations - Suggest specific next steps with timing
- Pattern recognition - Identify what's working and what's not
- Health scoring - Evaluate application viability (0-100 scale)
- Application comparison - Help prioritize multiple opportunities
- Insight generation - Provide strategic guidance

When managing an application:
1. First, use predict_lifecycle to understand where the application stands
2. Use calculate_health_score to assess its viability
3. Use recommend_next_actions to determine what to do next
4. If analyzing an email, use auto_update_status to suggest status changes

When providing strategic guidance:
1. Use identify_patterns to understand overall performance
2. Use generate_insights to provide actionable recommendations
3. Use compare_applications when deciding between opportunities

Always provide:
- Clear, actionable recommendations
- Specific timelines and priorities
- Data-driven insights
- Honest assessments of application health
- Strategic guidance for job search optimization

Be proactive in identifying issues (stalled applications, missed follow-ups) and opportunities (strong applications, positive patterns).
Focus on helping the user optimize their job search for maximum success.
"""

    async def manage_application(
        self,
        application_id: int,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Comprehensively manage a job application.

        Args:
            application_id: The application ID to manage
            context: Optional context (e.g., recent email analysis)

        Returns:
            Dictionary with management insights
        """
        try:
            query = f"""Provide comprehensive management insights for application ID {application_id}.

Please:
1. Predict the lifecycle and next stages
2. Calculate the health score
3. Recommend specific next actions
4. Provide strategic guidance

"""
            if context:
                query += f"\nAdditional context: {context}"

            response = await self.run(query)

            # Store the analysis
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Managed application {application_id}: {response.output[:200]}",
                    category="application_management",
                    tags=[f"app_{application_id}", "management"],
                )

            return {
                'success': response.success,
                'insights': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error managing application: {e}")
            return {
                'success': False,
                'insights': '',
                'error': str(e),
            }

    async def analyze_portfolio(self) -> Dict[str, Any]:
        """
        Analyze the entire application portfolio for insights.

        Returns:
            Dictionary with portfolio analysis
        """
        try:
            query = """Analyze my entire job application portfolio and provide strategic insights.

Please:
1. Use identify_patterns to understand overall performance
2. Use generate_insights for all focus areas
3. Identify the strongest and weakest applications
4. Provide strategic recommendations for improvement

Be thorough and actionable in your analysis."""

            response = await self.run(query)

            # Store the analysis
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Portfolio analysis: {response.output[:200]}",
                    category="portfolio_analysis",
                    tags=["portfolio", "strategy"],
                )

            return {
                'success': response.success,
                'analysis': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {
                'success': False,
                'analysis': '',
                'error': str(e),
            }


def create_application_manager_agent(db_manager) -> ApplicationManagerAgent:
    """Factory function to create Application Manager Agent"""
    return ApplicationManagerAgent(db_manager)
