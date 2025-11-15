"""
Application Manager Agent

Advanced AI agent for managing application lifecycle with intelligent decision-making.
Uses ReAct pattern to predict stages, update status, and provide next-action recommendations.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
import json

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager
from agents_framework.memory.vector_memory import RAGMemoryManager

logger = logging.getLogger(__name__)


class ApplicationManagerAgent(BaseAgent):
    """
    Application Manager Agent - Manages application lifecycle with intelligent predictions.

    Capabilities:
    - Application lifecycle prediction
    - Auto-status updates based on emails and patterns
    - Next-action recommendation system
    - Insights and pattern recognition
    - Success probability estimation
    - Timeline predictions
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Application Manager Agent",
            description="Manages application lifecycle with intelligent predictions and recommendations",
            model="gpt-4o-mini",
            temperature=0.2,  # Lower for more consistent predictions
            max_iterations=10,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="application_manager_agent",
            max_conversation_messages=40,
            enable_semantic=True
        )

        # RAG memory for learning from application patterns
        self.rag_memory = RAGMemoryManager(
            agent_name="application_manager_agent",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Application Manager Agent initialized with lifecycle prediction capabilities")

    def _register_tools(self) -> None:
        """Register application management tools"""

        # Tool 1: Predict Lifecycle Stage
        def predict_lifecycle_stage(application_data: str) -> str:
            """
            Predict the next lifecycle stage based on current application data.
            Input should be: 'job_id|current_status|days_elapsed|last_activity|company_type'
            """
            try:
                parts = application_data.split('|')
                if len(parts) < 5:
                    return "Error: Please provide data in format: job_id|current_status|days_elapsed|last_activity|company_type"

                job_id = parts[0].strip()
                current_status = parts[1].strip().lower()
                days_elapsed = int(parts[2].strip())
                last_activity = parts[3].strip()
                company_type = parts[4].strip()

                # Lifecycle progression patterns
                lifecycle_stages = {
                    'applied': {
                        'next_stages': ['screening', 'phone_screen', 'rejected', 'ghosted'],
                        'typical_timeline': '5-14 days',
                        'success_indicators': ['email received', 'recruiter reached out', 'screening scheduled'],
                        'warning_indicators': ['no response after 14 days', 'auto-rejection email']
                    },
                    'screening': {
                        'next_stages': ['phone_screen', 'technical', 'rejected'],
                        'typical_timeline': '3-7 days',
                        'success_indicators': ['positive feedback', 'next round scheduled'],
                        'warning_indicators': ['long delay', 'generic responses']
                    },
                    'phone_screen': {
                        'next_stages': ['technical', 'onsite', 'rejected'],
                        'typical_timeline': '3-10 days',
                        'success_indicators': ['technical interview scheduled', 'positive rapport'],
                        'warning_indicators': ['no follow-up', 'concerns raised']
                    },
                    'technical': {
                        'next_stages': ['onsite', 'final_round', 'rejected', 'offer'],
                        'typical_timeline': '5-14 days',
                        'success_indicators': ['all answers correct', 'positive feedback', 'onsite scheduled'],
                        'warning_indicators': ['struggled with questions', 'no feedback']
                    },
                    'onsite': {
                        'next_stages': ['offer', 'final_round', 'rejected'],
                        'typical_timeline': '7-21 days',
                        'success_indicators': ['team enthusiasm', 'hiring manager interested', 'quick follow-up'],
                        'warning_indicators': ['mixed signals', 'long delay', 'budget concerns mentioned']
                    },
                    'final_round': {
                        'next_stages': ['offer', 'rejected'],
                        'typical_timeline': '3-10 days',
                        'success_indicators': ['compensation discussion', 'reference checks', 'background check'],
                        'warning_indicators': ['still interviewing others', 'long decision timeline']
                    },
                }

                stage_info = lifecycle_stages.get(current_status, None)

                result = "📊 LIFECYCLE PREDICTION ANALYSIS\n\n"
                result += f"Current Stage: {current_status.upper()}\n"
                result += f"Days Elapsed: {days_elapsed}\n"
                result += f"Company Type: {company_type}\n"
                result += f"Last Activity: {last_activity}\n\n"

                if stage_info:
                    result += f"📈 Next Possible Stages:\n"
                    for stage in stage_info['next_stages']:
                        result += f"  • {stage.replace('_', ' ').title()}\n"

                    result += f"\n⏰ Typical Timeline: {stage_info['typical_timeline']}\n\n"

                    result += "✅ Success Indicators to Watch:\n"
                    for indicator in stage_info['success_indicators']:
                        result += f"  • {indicator}\n"

                    result += "\n⚠️ Warning Signs:\n"
                    for indicator in stage_info['warning_indicators']:
                        result += f"  • {indicator}\n"

                    # Predictions based on elapsed time
                    result += "\n🔮 Prediction:\n"
                    if current_status == 'applied' and days_elapsed > 14:
                        result += "  • High likelihood of being ghosted or overlooked\n"
                        result += "  • Recommendation: Send follow-up or move on\n"
                    elif current_status in ['phone_screen', 'technical', 'onsite'] and days_elapsed > 21:
                        result += "  • Application likely stalled or position filled\n"
                        result += "  • Recommendation: Politely inquire about status\n"
                    else:
                        result += "  • Application progressing within normal timeline\n"
                        result += "  • Recommendation: Continue monitoring\n"
                else:
                    result += "⚠️ Unknown stage. Cannot provide prediction.\n"

                return result

            except Exception as e:
                logger.error(f"Error predicting lifecycle stage: {e}")
                return f"Error predicting lifecycle: {str(e)}"

        # Tool 2: Recommend Next Actions
        def recommend_next_actions(application_context: str) -> str:
            """
            Recommend specific next actions based on application state.
            Input should be: 'status|days_since_activity|last_interaction_type|sentiment'
            """
            try:
                parts = application_context.split('|')
                if len(parts) < 4:
                    return "Error: Please provide data in format: status|days_since_activity|last_interaction_type|sentiment"

                status = parts[0].strip().lower()
                days_since = int(parts[1].strip())
                last_interaction = parts[2].strip()
                sentiment = parts[3].strip().lower()

                result = "📋 NEXT ACTION RECOMMENDATIONS\n\n"
                result += f"Current Status: {status.upper()}\n"
                result += f"Days Since Last Activity: {days_since}\n"
                result += f"Last Interaction: {last_interaction}\n"
                result += f"Sentiment: {sentiment.upper()}\n\n"

                # Action recommendations based on context
                actions = []

                if status == 'applied':
                    if days_since >= 7:
                        actions.append({
                            'priority': 'high',
                            'action': 'Send Follow-up Email',
                            'why': 'Week has passed since application',
                            'template': 'Express continued interest and inquire about timeline'
                        })
                    if days_since >= 14:
                        actions.append({
                            'priority': 'medium',
                            'action': 'Connect with Hiring Manager on LinkedIn',
                            'why': '2 weeks with no response',
                            'template': 'Send personalized connection request with brief note'
                        })

                elif status in ['phone_screen', 'technical', 'onsite']:
                    if last_interaction == 'interview' and days_since >= 1:
                        actions.append({
                            'priority': 'high',
                            'action': 'Send Thank You Note',
                            'why': 'Post-interview courtesy and reinforcement',
                            'template': 'Reference specific conversation points and express enthusiasm'
                        })
                    if days_since >= 7:
                        actions.append({
                            'priority': 'high',
                            'action': 'Request Status Update',
                            'why': 'Week since last contact',
                            'template': 'Politely inquire about timeline and next steps'
                        })

                elif status == 'offer':
                    actions.append({
                        'priority': 'critical',
                        'action': 'Negotiate Compensation',
                        'why': 'Offers are typically negotiable',
                        'template': 'Research market rates and prepare counter-offer'
                    })
                    actions.append({
                        'priority': 'high',
                        'action': 'Request Offer in Writing',
                        'why': 'Protect yourself with documentation',
                        'template': 'Politely ask for formal written offer letter'
                    })

                # Sentiment-based actions
                if sentiment == 'negative' or sentiment == 'concerning':
                    actions.append({
                        'priority': 'medium',
                        'action': 'Prepare Alternative Options',
                        'why': 'Negative signals detected',
                        'template': 'Continue applying to other positions as backup'
                    })

                # Format output
                if actions:
                    for i, action in enumerate(actions, 1):
                        result += f"🎯 Action {i}: {action['action']} [{action['priority'].upper()}]\n"
                        result += f"   Why: {action['why']}\n"
                        result += f"   Template: {action['template']}\n\n"
                else:
                    result += "✅ No immediate actions required. Continue monitoring.\n"

                return result

            except Exception as e:
                logger.error(f"Error recommending next actions: {e}")
                return f"Error generating recommendations: {str(e)}"

        # Tool 3: Analyze Application Patterns
        def analyze_application_patterns(applications_data: str) -> str:
            """
            Analyze patterns across multiple applications to identify insights.
            Input should be JSON string with list of applications.
            """
            try:
                # Parse applications data
                applications = json.loads(applications_data)

                result = "🔍 APPLICATION PATTERNS ANALYSIS\n\n"

                total_apps = len(applications)
                if total_apps == 0:
                    return "No applications to analyze"

                # Count by status
                status_counts = {}
                company_types = {}
                avg_response_time = []

                for app in applications:
                    status = app.get('status', 'unknown')
                    company_type = app.get('company_type', 'unknown')
                    response_days = app.get('response_days', None)

                    status_counts[status] = status_counts.get(status, 0) + 1
                    company_types[company_type] = company_types.get(company_type, 0) + 1

                    if response_days is not None:
                        avg_response_time.append(response_days)

                # Status breakdown
                result += f"📊 Status Breakdown (Total: {total_apps}):\n"
                for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_apps) * 100
                    result += f"  • {status.title()}: {count} ({percentage:.1f}%)\n"

                # Success metrics
                result += "\n📈 Success Metrics:\n"
                interviews = status_counts.get('phone_screen', 0) + status_counts.get('technical', 0) + status_counts.get('onsite', 0)
                offers = status_counts.get('offer', 0)

                if total_apps > 0:
                    interview_rate = (interviews / total_apps) * 100
                    offer_rate = (offers / total_apps) * 100
                    result += f"  • Interview Rate: {interview_rate:.1f}%\n"
                    result += f"  • Offer Rate: {offer_rate:.1f}%\n"

                # Response time
                if avg_response_time:
                    avg_days = sum(avg_response_time) / len(avg_response_time)
                    result += f"\n⏰ Average Response Time: {avg_days:.1f} days\n"

                # Company types
                result += "\n🏢 Company Type Distribution:\n"
                for company_type, count in sorted(company_types.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_apps) * 100
                    result += f"  • {company_type.title()}: {count} ({percentage:.1f}%)\n"

                # Insights
                result += "\n💡 Key Insights:\n"
                if interview_rate < 10:
                    result += "  ⚠️ Low interview rate - consider improving resume or targeting\n"
                if interview_rate > 20:
                    result += "  ✅ Strong interview rate - good application quality\n"
                if offer_rate > 5:
                    result += "  🎉 Excellent offer conversion - keep doing what you're doing!\n"

                ghosted = status_counts.get('ghosted', 0)
                if ghosted > total_apps * 0.3:
                    result += "  ⚠️ High ghosting rate - consider following up more actively\n"

                return result

            except json.JSONDecodeError:
                return "Error: Invalid JSON format for applications data"
            except Exception as e:
                logger.error(f"Error analyzing patterns: {e}")
                return f"Error analyzing patterns: {str(e)}"

        # Tool 4: Estimate Success Probability
        def estimate_success_probability(application_signals: str) -> str:
            """
            Estimate the probability of success based on various signals.
            Input should be: 'status|response_time|sentiment|recruiter_engagement|company_size|role_match'
            """
            try:
                parts = application_signals.split('|')
                if len(parts) < 6:
                    return "Error: Please provide data in format: status|response_time|sentiment|recruiter_engagement|company_size|role_match"

                status = parts[0].strip().lower()
                response_time = int(parts[1].strip())
                sentiment = parts[2].strip().lower()
                engagement = parts[3].strip().lower()
                company_size = parts[4].strip().lower()
                role_match = int(parts[5].strip())

                # Calculate probability score (0-100)
                score = 50  # Start at neutral

                # Status-based scoring
                status_scores = {
                    'applied': 0,
                    'screening': 10,
                    'phone_screen': 20,
                    'technical': 40,
                    'onsite': 60,
                    'final_round': 75,
                    'offer': 95
                }
                score += status_scores.get(status, 0)

                # Response time (faster is better)
                if response_time <= 3:
                    score += 10
                elif response_time <= 7:
                    score += 5
                elif response_time > 14:
                    score -= 10

                # Sentiment
                if sentiment == 'very positive':
                    score += 15
                elif sentiment == 'positive':
                    score += 10
                elif sentiment == 'neutral':
                    score += 0
                elif sentiment == 'negative':
                    score -= 15

                # Recruiter engagement
                if engagement == 'high':
                    score += 10
                elif engagement == 'medium':
                    score += 5
                elif engagement == 'low':
                    score -= 5

                # Role match
                score += (role_match - 50) // 5  # Adjust based on match percentage

                # Ensure score is within bounds
                score = max(0, min(100, score))

                # Determine success level
                if score >= 80:
                    level = "Very High"
                    color = "🟢"
                elif score >= 60:
                    level = "High"
                    color = "🟡"
                elif score >= 40:
                    level = "Moderate"
                    color = "🟠"
                else:
                    level = "Low"
                    color = "🔴"

                result = "🎯 SUCCESS PROBABILITY ESTIMATE\n\n"
                result += f"{color} Probability Score: {score}/100\n"
                result += f"Success Level: {level}\n\n"

                result += "📊 Contributing Factors:\n"
                result += f"  • Current Stage: {status.title()}\n"
                result += f"  • Response Speed: {response_time} days\n"
                result += f"  • Sentiment: {sentiment.title()}\n"
                result += f"  • Recruiter Engagement: {engagement.title()}\n"
                result += f"  • Role Match: {role_match}%\n\n"

                result += "💡 Interpretation:\n"
                if score >= 80:
                    result += "  Excellent chances! Stay engaged and prepare for offer negotiation.\n"
                elif score >= 60:
                    result += "  Strong position! Continue demonstrating value and enthusiasm.\n"
                elif score >= 40:
                    result += "  Moderate chances. Focus on standing out in next interactions.\n"
                else:
                    result += "  Lower probability. Consider backup options and improve weak areas.\n"

                return result

            except Exception as e:
                logger.error(f"Error estimating success probability: {e}")
                return f"Error estimating probability: {str(e)}"

        # Tool 5: Get Application Insights
        def get_application_insights(job_id: str) -> str:
            """
            Get comprehensive insights for a specific application.
            Input should be the job_id (string or number).
            """
            try:
                # Fetch application data from database
                query = "SELECT * FROM job_applications WHERE id = ?"
                result = self.db_manager.execute_query(query, (job_id,))

                if not result:
                    return f"No application found with job_id: {job_id}"

                app = result[0]

                output = "🔍 APPLICATION INSIGHTS\n\n"
                output += f"📌 Application ID: {job_id}\n"
                output += f"🏢 Company: {app.get('company', 'N/A')}\n"
                output += f"💼 Position: {app.get('position', 'N/A')}\n"
                output += f"📊 Status: {app.get('status', 'N/A')}\n"
                output += f"📅 Applied: {app.get('date_applied', 'N/A')}\n\n"

                # Calculate days elapsed
                if app.get('date_applied'):
                    try:
                        applied_date = datetime.fromisoformat(app['date_applied'])
                        days_elapsed = (datetime.now() - applied_date).days
                        output += f"⏰ Days Elapsed: {days_elapsed}\n\n"
                    except:
                        pass

                output += "💡 Insights:\n"
                output += "  • Monitor for status updates\n"
                output += "  • Track communication patterns\n"
                output += "  • Prepare for next stage\n"

                return output

            except Exception as e:
                logger.error(f"Error getting application insights: {e}")
                return f"Error retrieving insights: {str(e)}"

        # Register all tools
        self.register_tool(
            name="predict_lifecycle_stage",
            func=predict_lifecycle_stage,
            description="Predict the next lifecycle stage based on current application data"
        )

        self.register_tool(
            name="recommend_next_actions",
            func=recommend_next_actions,
            description="Recommend specific next actions based on application state"
        )

        self.register_tool(
            name="analyze_application_patterns",
            func=analyze_application_patterns,
            description="Analyze patterns across multiple applications to identify insights"
        )

        self.register_tool(
            name="estimate_success_probability",
            func=estimate_success_probability,
            description="Estimate the probability of success based on various signals"
        )

        self.register_tool(
            name="get_application_insights",
            func=get_application_insights,
            description="Get comprehensive insights for a specific application"
        )

        logger.info(f"✅ Registered {len(self.tools)} tools for Application Manager Agent")


def create_application_manager_agent(db_manager):
    """Factory function to create an Application Manager Agent"""
    return ApplicationManagerAgent(db_manager)
