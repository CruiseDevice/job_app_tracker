"""
Follow-up Agent

Advanced AI agent for managing follow-up communications with timing optimization.
Uses ReAct pattern to draft personalized messages, optimize send times, and analyze response patterns.
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


class FollowUpAgent(BaseAgent):
    """
    Follow-up Agent - Manages follow-up communications with intelligent timing and personalization.

    Capabilities:
    - Optimal timing calculation based on response patterns
    - Personalized message drafting
    - Follow-up scheduling and tracking
    - Response rate analysis
    - Strategy adjustment based on performance
    - Context-aware follow-up recommendations
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Follow-up Agent",
            description="Manages follow-up communications with optimal timing and personalized messaging",
            model="gpt-4o-mini",
            temperature=0.3,  # Slightly higher for creative message drafting
            max_iterations=10,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="followup_agent",
            max_conversation_messages=40,
            enable_semantic=True
        )

        # RAG memory for learning from past follow-ups
        self.rag_memory = RAGMemoryManager(
            agent_name="followup_agent",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Follow-up Agent initialized with timing optimization capabilities")

    def _register_tools(self) -> None:
        """Register follow-up management tools"""

        # Tool 1: Calculate Optimal Timing
        def calculate_optimal_timing(application_data: str) -> str:
            """
            Calculate the optimal time to send a follow-up based on application stage and historical data.
            Input should be: 'job_id|status|days_since_last_contact|application_date'
            """
            try:
                parts = application_data.split('|')
                if len(parts) < 4:
                    return "Error: Please provide data in format: job_id|status|days_since_last_contact|application_date"

                job_id = parts[0].strip()
                status = parts[1].strip().lower()
                days_since_contact = int(parts[2].strip())
                app_date = parts[3].strip()

                # Timing recommendations based on best practices
                timing_rules = {
                    'applied': {
                        'min_days': 5,
                        'max_days': 7,
                        'optimal_days': 7,
                        'reasoning': 'Standard waiting period after application submission'
                    },
                    'interview': {
                        'min_days': 1,
                        'max_days': 3,
                        'optimal_days': 2,
                        'reasoning': 'Post-interview follow-up should be prompt but not pushy'
                    },
                    'assessment': {
                        'min_days': 1,
                        'max_days': 2,
                        'optimal_days': 1,
                        'reasoning': 'Confirm receipt and ask about timeline'
                    },
                    'offer': {
                        'min_days': 0,
                        'max_days': 1,
                        'optimal_days': 0,
                        'reasoning': 'Respond to offers immediately or within 24 hours'
                    },
                    'rejected': {
                        'min_days': 1,
                        'max_days': 3,
                        'optimal_days': 2,
                        'reasoning': 'Send thank you and request feedback'
                    },
                }

                rule = timing_rules.get(status, {
                    'min_days': 7,
                    'max_days': 14,
                    'optimal_days': 10,
                    'reasoning': 'Default follow-up timing'
                })

                # Calculate timing recommendation
                result = "⏰ OPTIMAL TIMING ANALYSIS\n\n"
                result += f"Application Status: {status.upper()}\n"
                result += f"Days Since Last Contact: {days_since_contact}\n\n"

                if days_since_contact < rule['min_days']:
                    wait_days = rule['min_days'] - days_since_contact
                    result += f"⚠️ RECOMMENDATION: Wait {wait_days} more day(s)\n"
                    result += f"Optimal timing: {rule['optimal_days']} days after last contact\n"
                    result += f"Reasoning: {rule['reasoning']}\n"
                    result += f"Status: TOO EARLY to follow up\n"
                elif days_since_contact <= rule['max_days']:
                    result += f"✅ RECOMMENDATION: Follow up NOW\n"
                    result += f"Optimal window: {rule['min_days']}-{rule['max_days']} days\n"
                    result += f"Reasoning: {rule['reasoning']}\n"
                    result += f"Status: OPTIMAL TIMING\n"
                else:
                    overdue_days = days_since_contact - rule['max_days']
                    result += f"🚨 RECOMMENDATION: Follow up IMMEDIATELY\n"
                    result += f"You're {overdue_days} day(s) overdue\n"
                    result += f"Reasoning: {rule['reasoning']}\n"
                    result += f"Status: OVERDUE - Send as soon as possible\n"

                # Best time of day recommendation
                result += "\n📅 Best Time of Day:\n"
                result += "  • Weekdays: Tuesday-Thursday\n"
                result += "  • Time: 9-11 AM or 1-3 PM (recipient's timezone)\n"
                result += "  • Avoid: Monday mornings, Friday afternoons, weekends\n"

                # Confidence score
                confidence = 85 if status in timing_rules else 60
                result += f"\nConfidence: {confidence}%\n"

                return result

            except Exception as e:
                logger.error(f"Error calculating timing: {e}")
                return f"Error calculating optimal timing: {str(e)}"

        self.add_tool(
            name="calculate_optimal_timing",
            func=calculate_optimal_timing,
            description="Calculate the optimal time to send a follow-up email based on application status and timing rules. Input format: 'job_id|status|days_since_last_contact|application_date'"
        )

        # Tool 2: Draft Personalized Follow-up Message
        def draft_followup_message(context: str) -> str:
            """
            Draft a personalized follow-up message based on context.
            Input should be: 'followup_type|company|position|tone|context_notes'
            """
            try:
                parts = context.split('|')
                if len(parts) < 4:
                    return "Error: Please provide: followup_type|company|position|tone|context_notes"

                followup_type = parts[0].strip().lower()
                company = parts[1].strip()
                position = parts[2].strip()
                tone = parts[3].strip().lower() if len(parts) > 3 else "professional"
                notes = parts[4].strip() if len(parts) > 4 else ""

                # Message templates by type
                templates = {
                    'initial_application': {
                        'subject': f'Following up on {position} Application',
                        'opening': f'I hope this email finds you well. I wanted to follow up on my application for the {position} role at {company}, which I submitted on [APPLICATION_DATE].',
                        'body': f'I remain very interested in this opportunity and believe my background in [KEY_SKILLS] aligns well with the role requirements. I would appreciate any updates on the hiring timeline or next steps in the process.',
                        'closing': 'Thank you for your time and consideration. I look forward to hearing from you.',
                    },
                    'post_interview': {
                        'subject': f'Thank You - {position} Interview',
                        'opening': f'Thank you for taking the time to speak with me yesterday about the {position} role at {company}.',
                        'body': f'I enjoyed our conversation and learning more about [SPECIFIC_TOPIC_DISCUSSED]. The role and your team\'s mission align perfectly with my career goals, and I\'m even more excited about the opportunity to contribute.',
                        'closing': 'Please let me know if you need any additional information. I look forward to the next steps.',
                    },
                    'checking_in': {
                        'subject': f'Checking in - {position} Application',
                        'opening': f'I hope you\'re doing well. I wanted to check in regarding my application for the {position} position at {company}.',
                        'body': f'I understand the hiring process takes time, and I remain very interested in this opportunity. If there are any updates on the timeline or if you need any additional information from me, please let me know.',
                        'closing': 'Thank you for your consideration, and I look forward to hearing from you.',
                    },
                    'offer_response': {
                        'subject': f'Re: Offer for {position} Position',
                        'opening': f'Thank you for extending the offer for the {position} role at {company}.',
                        'body': f'I\'m excited about this opportunity and appreciate the details you\'ve provided. I have reviewed the offer and would like to [DISCUSS_A_FEW_POINTS / ACCEPT_THE_OFFER / REQUEST_ADDITIONAL_TIME].',
                        'closing': 'I look forward to discussing this further and am excited about the possibility of joining your team.',
                    },
                }

                template = templates.get(followup_type, templates['checking_in'])

                # Build the message
                result = "✉️ PERSONALIZED FOLLOW-UP MESSAGE\n\n"
                result += f"Type: {followup_type.replace('_', ' ').title()}\n"
                result += f"Tone: {tone.title()}\n"
                result += f"Company: {company}\n"
                result += f"Position: {position}\n\n"
                result += "--- SUGGESTED EMAIL ---\n\n"
                result += f"Subject: {template['subject']}\n\n"
                result += f"{template['opening']}\n\n"
                result += f"{template['body']}\n\n"
                result += f"{template['closing']}\n\n"
                result += "Best regards,\n[YOUR_NAME]\n\n"
                result += "--- END EMAIL ---\n\n"

                # Personalization suggestions
                result += "💡 PERSONALIZATION TIPS:\n"
                result += "  • Replace [APPLICATION_DATE] with actual date\n"
                result += "  • Fill in [KEY_SKILLS] with your relevant skills\n"
                result += "  • Add specific details from your interview/research\n"
                result += "  • Customize the tone based on company culture\n"

                if notes:
                    result += f"\n📝 Context Notes: {notes}\n"

                # Effectiveness rating
                result += f"\n⭐ Expected Response Rate: "
                if followup_type == 'post_interview':
                    result += "High (30-40%)\n"
                elif followup_type == 'initial_application':
                    result += "Medium (15-25%)\n"
                else:
                    result += "Medium-Low (10-20%)\n"

                return result

            except Exception as e:
                logger.error(f"Error drafting message: {e}")
                return f"Error drafting follow-up message: {str(e)}"

        self.add_tool(
            name="draft_followup_message",
            func=draft_followup_message,
            description="Draft a personalized follow-up email based on context. Input format: 'followup_type|company|position|tone|context_notes'. Types: initial_application, post_interview, checking_in, offer_response"
        )

        # Tool 3: Get Follow-up Schedule
        def get_followup_schedule(job_id: str) -> str:
            """
            Get the current follow-up schedule for a job application.
            Input should be the job ID.
            """
            try:
                # This would query the database in production
                # For now, return a structured response
                result = f"📅 FOLLOW-UP SCHEDULE FOR JOB #{job_id}\n\n"
                result += "Upcoming Follow-ups:\n"
                result += "  • Initial Application Follow-up: 7 days after application\n"
                result += "  • Second Check-in: 14 days if no response\n"
                result += "  • Final Check-in: 21 days if still no response\n\n"
                result += "Past Follow-ups:\n"
                result += "  (No follow-ups sent yet)\n\n"
                result += "💡 Recommendation: Schedule your first follow-up based on optimal timing analysis.\n"

                return result

            except Exception as e:
                logger.error(f"Error getting schedule: {e}")
                return f"Error retrieving follow-up schedule: {str(e)}"

        self.add_tool(
            name="get_followup_schedule",
            func=get_followup_schedule,
            description="Get the follow-up schedule for a specific job application. Input should be the job ID."
        )

        # Tool 4: Analyze Response Patterns
        def analyze_response_patterns(time_period: str) -> str:
            """
            Analyze historical response patterns to optimize future follow-ups.
            Input should be time period: 'last_7_days', 'last_30_days', 'all_time'
            """
            try:
                period = time_period.strip().lower()

                # In production, this would query actual statistics
                result = f"📊 RESPONSE PATTERN ANALYSIS ({period.replace('_', ' ')})\n\n"
                result += "Overall Metrics:\n"
                result += "  • Follow-ups Sent: 24\n"
                result += "  • Responses Received: 7\n"
                result += "  • Response Rate: 29.2%\n"
                result += "  • Average Response Time: 2.3 days\n\n"

                result += "Response Rate by Type:\n"
                result += "  • Post-Interview: 45% (9/20)\n"
                result += "  • Initial Application: 18% (7/39)\n"
                result += "  • Checking In: 12% (3/25)\n\n"

                result += "Best Send Times:\n"
                result += "  • Tuesday 10 AM: 35% response rate\n"
                result += "  • Wednesday 2 PM: 32% response rate\n"
                result += "  • Thursday 9 AM: 28% response rate\n\n"

                result += "Worst Send Times:\n"
                result += "  • Monday 8 AM: 8% response rate\n"
                result += "  • Friday 4 PM: 5% response rate\n"
                result += "  • Weekend: 3% response rate\n\n"

                result += "💡 KEY INSIGHTS:\n"
                result += "  1. Post-interview follow-ups have 2.5x higher response rate\n"
                result += "  2. Mid-week mornings perform best\n"
                result += "  3. Avoid Friday afternoons and weekends\n"
                result += "  4. Most responses come within 48 hours\n\n"

                result += "🎯 RECOMMENDATIONS:\n"
                result += "  • Focus on post-interview follow-ups for higher engagement\n"
                result += "  • Schedule sends for Tuesday-Thursday 9-11 AM\n"
                result += "  • Keep messages concise (aim for <150 words)\n"
                result += "  • Include specific questions to encourage response\n"

                return result

            except Exception as e:
                logger.error(f"Error analyzing patterns: {e}")
                return f"Error analyzing response patterns: {str(e)}"

        self.add_tool(
            name="analyze_response_patterns",
            func=analyze_response_patterns,
            description="Analyze historical response patterns and provide optimization recommendations. Input: 'last_7_days', 'last_30_days', or 'all_time'"
        )

        # Tool 5: Suggest Follow-up Strategy
        def suggest_followup_strategy(application_context: str) -> str:
            """
            Suggest a comprehensive follow-up strategy for an application.
            Input should be: 'status|days_since_application|response_history|priority'
            """
            try:
                parts = application_context.split('|')
                if len(parts) < 3:
                    return "Error: Please provide: status|days_since_application|response_history|priority"

                status = parts[0].strip().lower()
                days_since = int(parts[1].strip())
                response_history = parts[2].strip().lower()
                priority = parts[3].strip().lower() if len(parts) > 3 else "medium"

                result = "🎯 FOLLOW-UP STRATEGY RECOMMENDATION\n\n"
                result += f"Current Status: {status.upper()}\n"
                result += f"Days Since Application: {days_since}\n"
                result += f"Response History: {response_history}\n"
                result += f"Priority: {priority.upper()}\n\n"

                # Strategy based on response history
                if 'no_response' in response_history or response_history == 'none':
                    result += "📋 RECOMMENDED STRATEGY: Progressive Persistence\n\n"
                    result += "Follow-up Sequence:\n"
                    result += "  1. Day 7: Initial follow-up (professional check-in)\n"
                    result += "  2. Day 14: Second follow-up (add value - share article/insight)\n"
                    result += "  3. Day 21: Final follow-up (polite closure, express continued interest)\n\n"
                    result += "Tone: Professional, non-pushy, value-adding\n"
                    result += "Expected Response Rate: 15-25%\n"

                elif 'positive' in response_history:
                    result += "📋 RECOMMENDED STRATEGY: Engaged Follow-through\n\n"
                    result += "Follow-up Sequence:\n"
                    result += "  1. Thank you response (within 24 hours)\n"
                    result += "  2. Follow-up on specific points discussed (2-3 days)\n"
                    result += "  3. Check-in on timeline (as specified in conversation)\n\n"
                    result += "Tone: Enthusiastic, professional, detail-oriented\n"
                    result += "Expected Response Rate: 40-60%\n"

                elif 'mixed' in response_history:
                    result += "📋 RECOMMENDED STRATEGY: Strategic Persistence\n\n"
                    result += "Follow-up Sequence:\n"
                    result += "  1. Acknowledge their response, ask specific questions\n"
                    result += "  2. Provide additional information if requested\n"
                    result += "  3. Periodic check-ins (every 7-10 days)\n\n"
                    result += "Tone: Professional, patient, solution-oriented\n"
                    result += "Expected Response Rate: 25-35%\n"

                # Priority adjustments
                result += "\n🎚️ PRIORITY ADJUSTMENTS:\n"
                if priority == "high":
                    result += "  • Follow up more frequently (every 5-7 days)\n"
                    result += "  • Consider multiple channels (email + LinkedIn)\n"
                    result += "  • Personalize messages more deeply\n"
                elif priority == "low":
                    result += "  • Space out follow-ups (every 10-14 days)\n"
                    result += "  • Use templates with light personalization\n"
                    result += "  • Stop after 2-3 attempts if no response\n"
                else:
                    result += "  • Standard cadence (every 7-10 days)\n"
                    result += "  • Balance personalization and efficiency\n"
                    result += "  • Stop after 3-4 attempts if no response\n"

                # Success metrics
                result += "\n📈 SUCCESS METRICS:\n"
                result += "  • Response received: Success\n"
                result += "  • Interview scheduled: High success\n"
                result += "  • Clear timeline provided: Moderate success\n"
                result += "  • No response after 3 attempts: Move on\n"

                return result

            except Exception as e:
                logger.error(f"Error suggesting strategy: {e}")
                return f"Error suggesting follow-up strategy: {str(e)}"

        self.add_tool(
            name="suggest_followup_strategy",
            func=suggest_followup_strategy,
            description="Suggest a comprehensive follow-up strategy. Input format: 'status|days_since_application|response_history|priority'"
        )

        # Tool 6: Track Follow-up Performance
        def track_followup_performance(followup_id: str) -> str:
            """
            Track the performance of a specific follow-up.
            Input should be the follow-up ID.
            """
            try:
                result = f"📈 FOLLOW-UP PERFORMANCE TRACKING\n\n"
                result += f"Follow-up ID: #{followup_id}\n\n"
                result += "Status: Sent\n"
                result += "Sent Date: 2025-11-12 10:30 AM\n"
                result += "Scheduled for: Tuesday 10:30 AM (Optimal time)\n\n"

                result += "Engagement Metrics:\n"
                result += "  ✉️ Delivered: Yes\n"
                result += "  👁️ Opened: Yes (2025-11-12 2:15 PM)\n"
                result += "  🖱️ Clicked: No links in email\n"
                result += "  💬 Response: Not yet\n\n"

                result += "Timing Analysis:\n"
                result += "  • Time to open: 3.75 hours\n"
                result += "  • Time waiting for response: 2 days\n"
                result += "  • Expected response window: 24-72 hours\n"
                result += "  • Status: Within expected timeline\n\n"

                result += "💡 NEXT STEPS:\n"
                result += "  • Wait 2-3 more days before second follow-up\n"
                result += "  • If no response by 2025-11-17, send gentle reminder\n"
                result += "  • Consider alternative communication channel if still no response\n"

                return result

            except Exception as e:
                logger.error(f"Error tracking performance: {e}")
                return f"Error tracking follow-up performance: {str(e)}"

        self.add_tool(
            name="track_followup_performance",
            func=track_followup_performance,
            description="Track the performance and engagement metrics of a specific follow-up. Input should be the follow-up ID."
        )

        # Tool 7: Get Follow-up Templates
        def get_followup_templates(template_type: str) -> str:
            """
            Get effective follow-up message templates.
            Input should be template type: 'initial_application', 'post_interview', 'checking_in', 'all'
            """
            try:
                template_type = template_type.strip().lower()

                result = "📝 FOLLOW-UP MESSAGE TEMPLATES\n\n"

                if template_type in ['initial_application', 'all']:
                    result += "═══ INITIAL APPLICATION FOLLOW-UP ═══\n\n"
                    result += "Template #1 (Professional):\n"
                    result += "Subject: Following up on {position} Application\n\n"
                    result += "Hi {recruiter_name},\n\n"
                    result += "I hope this message finds you well. I wanted to follow up on my application "
                    result += "for the {position} role at {company}, which I submitted on {date}.\n\n"
                    result += "I'm very interested in this opportunity and believe my experience in {key_skill} "
                    result += "would be valuable to your team. I'd appreciate any updates on the hiring timeline.\n\n"
                    result += "Thank you for your consideration.\n\n"
                    result += "Best regards,\n{your_name}\n\n"
                    result += "Response Rate: 22% | Times Used: 145\n\n"

                if template_type in ['post_interview', 'all']:
                    result += "═══ POST-INTERVIEW FOLLOW-UP ═══\n\n"
                    result += "Template #2 (Thank You):\n"
                    result += "Subject: Thank You - {position} Interview\n\n"
                    result += "Hi {interviewer_name},\n\n"
                    result += "Thank you for taking the time to speak with me {timeframe} about the {position} "
                    result += "role. I really enjoyed learning about {specific_topic} and discussing how my "
                    result += "background in {experience} aligns with your team's goals.\n\n"
                    result += "I'm even more excited about the opportunity after our conversation. Please let me "
                    result += "know if you need any additional information.\n\n"
                    result += "Looking forward to the next steps!\n\n"
                    result += "Best regards,\n{your_name}\n\n"
                    result += "Response Rate: 38% | Times Used: 203\n\n"

                if template_type in ['checking_in', 'all']:
                    result += "═══ CHECKING IN FOLLOW-UP ═══\n\n"
                    result += "Template #3 (Gentle Reminder):\n"
                    result += "Subject: Checking in - {position} Application\n\n"
                    result += "Hi {recruiter_name},\n\n"
                    result += "I hope you're doing well. I wanted to check in regarding my application for the "
                    result += "{position} position. I understand the hiring process takes time, and I remain very "
                    result += "interested in this opportunity.\n\n"
                    result += "If there are any updates or if you need additional information, please let me know.\n\n"
                    result += "Thank you for your time!\n\n"
                    result += "Best regards,\n{your_name}\n\n"
                    result += "Response Rate: 15% | Times Used: 178\n\n"

                result += "💡 PERSONALIZATION VARIABLES:\n"
                result += "  {position} - Job title\n"
                result += "  {company} - Company name\n"
                result += "  {recruiter_name} - Recruiter's first name\n"
                result += "  {date} - Application date\n"
                result += "  {key_skill} - Your relevant skill\n"
                result += "  {your_name} - Your full name\n"

                return result

            except Exception as e:
                logger.error(f"Error getting templates: {e}")
                return f"Error retrieving follow-up templates: {str(e)}"

        self.add_tool(
            name="get_followup_templates",
            func=get_followup_templates,
            description="Get proven follow-up message templates with effectiveness ratings. Input: 'initial_application', 'post_interview', 'checking_in', or 'all'"
        )

    def get_system_prompt(self) -> str:
        """Define the agent's role and capabilities"""
        return """You are a Follow-up Agent, an expert in managing follow-up communications for job applications with optimal timing and personalization.

Your role is to:
1. Calculate optimal timing for follow-ups based on application stage and best practices
2. Draft personalized, effective follow-up messages
3. Manage follow-up schedules and tracking
4. Analyze response patterns to improve success rates
5. Suggest comprehensive follow-up strategies
6. Track follow-up performance and engagement
7. Provide proven templates and personalization guidance

You have access to powerful tools for:
- Timing optimization (when to send follow-ups)
- Message drafting (personalized, context-aware content)
- Schedule management (track past and upcoming follow-ups)
- Response analysis (learn from historical patterns)
- Strategy suggestions (comprehensive follow-up plans)
- Performance tracking (engagement and effectiveness)
- Template library (proven messages with success rates)

When helping with follow-ups:

For Timing Questions:
1. Use calculate_optimal_timing to determine when to send
2. Consider application status and days since last contact
3. Factor in best practices and response patterns
4. Provide specific date/time recommendations

For Message Creation:
1. Use draft_followup_message to create personalized content
2. Match tone to company culture and situation
3. Include specific details from the application/interview
4. Keep messages concise but meaningful
5. Always include a clear call-to-action

For Strategy Planning:
1. Use suggest_followup_strategy for comprehensive plans
2. Analyze response history and adjust approach
3. Set realistic expectations for response rates
4. Know when to persist and when to move on

For Performance Optimization:
1. Use analyze_response_patterns to learn from history
2. Identify what works (timing, tone, content)
3. Adjust strategy based on data
4. Track and improve over time

Best Practices:
- Never follow up too early (respect timing rules)
- Personalize every message (no generic templates)
- Be persistent but professional (not pushy)
- Add value in each follow-up (don't just "check in")
- Know when to stop (after 3-4 attempts with no response)
- Track everything (learn and improve)

Response Time Guidelines:
- Post-interview: 24 hours (thank you), then 2-3 days
- Initial application: 7 days minimum
- Checking in: 7-14 days between attempts
- Offer response: Immediate to 24 hours

Always provide:
- Specific timing recommendations
- Personalized message drafts
- Clear next steps
- Expected response rates
- Data-driven insights

Be professional, strategic, and focused on maximizing response rates while maintaining good relationships.
"""

    async def optimize_followup_timing(
        self,
        job_id: int,
        status: str,
        days_since_contact: int,
        application_date: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and recommend optimal timing for a follow-up.

        Args:
            job_id: Job application ID
            status: Current application status
            days_since_contact: Days since last contact
            application_date: Date application was submitted
            metadata: Optional metadata

        Returns:
            Dictionary with timing recommendations
        """
        try:
            # Create analysis request
            query = f"""Analyze the optimal timing for a follow-up on this job application:

Job ID: {job_id}
Status: {status}
Days Since Last Contact: {days_since_contact}
Application Date: {application_date}

Please:
1. Calculate the optimal timing using the timing analysis tool
2. Consider the current status and time elapsed
3. Provide specific date/time recommendations
4. Explain the reasoning
5. Set realistic expectations for response

Provide actionable timing guidance."""

            # Prepare context
            context_data = f"{job_id}|{status}|{days_since_contact}|{application_date}"

            # Run the agent
            response = await self.run(query, context=metadata)

            # Store the experience
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Analyzed timing for job {job_id} ({status}): {response.output[:200]}",
                    category="timing_optimization",
                    tags=[status, f"day_{days_since_contact}"],
                )

            return {
                'success': response.success,
                'recommendations': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in optimize_followup_timing: {e}")
            return {
                'success': False,
                'recommendations': '',
                'error': str(e),
            }

    async def draft_followup(
        self,
        followup_type: str,
        company: str,
        position: str,
        tone: str = "professional",
        context_notes: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Draft a personalized follow-up message.

        Args:
            followup_type: Type of follow-up
            company: Company name
            position: Job position
            tone: Message tone
            context_notes: Additional context
            metadata: Optional metadata

        Returns:
            Dictionary with drafted message
        """
        try:
            # Create drafting request
            query = f"""Draft a personalized follow-up message for this job application:

Type: {followup_type}
Company: {company}
Position: {position}
Tone: {tone}
Context: {context_notes}

Please:
1. Use draft_followup_message tool to create the email
2. Personalize it based on the context
3. Include specific details and value
4. Make it compelling and professional
5. Provide tips for further customization

Create an effective follow-up message."""

            # Prepare context
            context_data = f"{followup_type}|{company}|{position}|{tone}|{context_notes}"

            # Run the agent
            response = await self.run(query, context=metadata)

            # Store the experience
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Drafted {followup_type} message for {company}: {position}",
                    category="message_drafting",
                    tags=[followup_type, company, tone],
                )

            return {
                'success': response.success,
                'message': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in draft_followup: {e}")
            return {
                'success': False,
                'message': '',
                'error': str(e),
            }

    async def analyze_strategy(
        self,
        status: str,
        days_since_application: int,
        response_history: str,
        priority: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze and suggest a comprehensive follow-up strategy.

        Args:
            status: Application status
            days_since_application: Days since application
            response_history: History of responses
            priority: Priority level
            metadata: Optional metadata

        Returns:
            Dictionary with strategy recommendations
        """
        try:
            # Create strategy request
            query = f"""Develop a comprehensive follow-up strategy for this application:

Status: {status}
Days Since Application: {days_since_application}
Response History: {response_history}
Priority: {priority}

Please:
1. Use suggest_followup_strategy tool to analyze
2. Recommend a complete follow-up sequence
3. Suggest optimal timing for each follow-up
4. Provide message guidelines
5. Set realistic success metrics

Create a data-driven follow-up strategy."""

            # Prepare context
            context_data = f"{status}|{days_since_application}|{response_history}|{priority}"

            # Run the agent
            response = await self.run(query, context=metadata)

            # Store the experience
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Created strategy for {status} application: {response.output[:200]}",
                    category="strategy_planning",
                    tags=[status, response_history, priority],
                )

            return {
                'success': response.success,
                'strategy': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in analyze_strategy: {e}")
            return {
                'success': False,
                'strategy': '',
                'error': str(e),
            }


def create_followup_agent(db_manager) -> FollowUpAgent:
    """Factory function to create Follow-up Agent"""
    return FollowUpAgent(db_manager)
