"""
Email Analyst Agent

Advanced AI agent for analyzing job-related emails with intelligent reasoning.
Uses ReAct pattern to determine email sentiment, urgency, and match to applications.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager
from agents_framework.memory.vector_memory import RAGMemoryManager

logger = logging.getLogger(__name__)


class EmailAnalystAgent(BaseAgent):
    """
    Email Analyst Agent - Analyzes job-related emails with intelligent reasoning.

    Capabilities:
    - Sentiment analysis (positive, negative, neutral)
    - Urgency detection (high, medium, low)
    - Action item extraction
    - Company and position identification
    - Email categorization (interview, rejection, offer, etc.)
    - Smart email-to-job matching
    - Follow-up recommendations
    """

    def __init__(self, db_manager, email_processor=None):
        # Create agent configuration
        config = AgentConfig(
            name="Email Analyst",
            description="Analyzes job-related emails to extract insights, determine urgency, and match to applications",
            model="gpt-4o-mini",
            temperature=0.1,
            max_iterations=8,
            verbose=True,
            enable_memory=True,
            memory_k=15,
        )

        # Store dependencies
        self.db_manager = db_manager
        self.email_processor = email_processor

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="email_analyst",
            max_conversation_messages=30,
            enable_semantic=True
        )

        # RAG memory for learning from past email analyses
        self.rag_memory = RAGMemoryManager(
            agent_name="email_analyst",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Email Analyst Agent initialized with advanced capabilities")

    def _register_tools(self) -> None:
        """Register email analysis tools"""

        # Tool 1: Analyze Email Sentiment
        def analyze_sentiment(email_text: str) -> str:
            """
            Analyze the sentiment and tone of an email to determine if it's positive, negative, or neutral.
            Input should be the email content (subject + body).
            """
            try:
                email_lower = email_text.lower()

                # Positive indicators (good news)
                positive_indicators = {
                    'congratulations': 3,
                    'pleased to inform': 3,
                    'excited to': 2,
                    'offer': 3,
                    'selected': 3,
                    'impressed': 2,
                    'next steps': 2,
                    'move forward': 2,
                    'advancing': 2,
                    'delighted': 2,
                    'happy to': 2,
                    'would like to schedule': 2,
                    'invitation': 2,
                }

                # Negative indicators (rejection, bad news)
                negative_indicators = {
                    'unfortunately': 3,
                    'regret to inform': 3,
                    'not selected': 3,
                    'decided not to': 3,
                    'not moving forward': 3,
                    'other candidates': 2,
                    'unable to': 2,
                    'at this time': 2,
                    'position has been filled': 3,
                    'no longer': 2,
                    'withdrawn': 2,
                }

                # Urgency indicators
                urgent_indicators = {
                    'urgent': 3,
                    'asap': 3,
                    'immediate': 2,
                    'deadline': 2,
                    'time-sensitive': 2,
                    'respond by': 2,
                    'by end of day': 2,
                    'within 24': 2,
                }

                # Calculate scores
                positive_score = sum(score for phrase, score in positive_indicators.items() if phrase in email_lower)
                negative_score = sum(score for phrase, score in negative_indicators.items() if phrase in email_lower)
                urgency_score = sum(score for phrase, score in urgent_indicators.items() if phrase in email_lower)

                # Determine sentiment
                if negative_score > positive_score + 2:
                    sentiment = "NEGATIVE (Likely rejection or bad news)"
                    confidence = min(95, 60 + (negative_score * 5))
                elif positive_score > negative_score + 2:
                    sentiment = "POSITIVE (Likely good news - interview/offer)"
                    confidence = min(95, 60 + (positive_score * 5))
                else:
                    sentiment = "NEUTRAL (Informational or unclear)"
                    confidence = 50

                # Determine urgency level
                if urgency_score >= 5:
                    urgency = "HIGH - Requires immediate attention"
                elif urgency_score >= 2:
                    urgency = "MEDIUM - Respond within 24-48 hours"
                else:
                    urgency = "LOW - No immediate action needed"

                # Build response
                result = "📊 EMAIL SENTIMENT ANALYSIS\n\n"
                result += f"Sentiment: {sentiment}\n"
                result += f"Confidence: {confidence}%\n"
                result += f"Urgency Level: {urgency}\n\n"

                result += "Indicators Found:\n"
                if positive_score > 0:
                    result += f"  ✅ Positive signals: {positive_score} points\n"
                if negative_score > 0:
                    result += f"  ❌ Negative signals: {negative_score} points\n"
                if urgency_score > 0:
                    result += f"  ⚡ Urgency signals: {urgency_score} points\n"

                return result

            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                return f"Error analyzing sentiment: {str(e)}"

        self.add_tool(
            name="analyze_email_sentiment",
            func=analyze_sentiment,
            description="Analyze the sentiment and urgency of an email. Determines if email is positive (interview/offer), negative (rejection), or neutral. Also assesses urgency level. Input should be the email text."
        )

        # Tool 2: Extract Action Items
        def extract_action_items(email_text: str) -> str:
            """
            Extract action items and next steps from an email.
            Input should be the email content.
            """
            try:
                # Action patterns
                action_patterns = [
                    r'(?:please|kindly|could you)\s+([^.!?]{10,100})',
                    r'(?:need you to|ask you to|would like you to)\s+([^.!?]{10,100})',
                    r'(?:schedule|confirm|reply|respond|submit|send|complete|review|prepare|provide)\s+([^.!?]{10,100})',
                    r'(?:by|before|within)\s+(\d+\s+(?:days?|hours?|weeks?))[^.!?]{0,50}',
                ]

                actions = []
                for pattern in action_patterns:
                    matches = re.finditer(pattern, email_text, re.IGNORECASE)
                    for match in matches:
                        action = match.group(0).strip()
                        if len(action) > 15 and action not in actions:
                            actions.append(action)

                if not actions:
                    return "No explicit action items found in email."

                result = f"📋 EXTRACTED ACTION ITEMS ({len(actions)})\n\n"
                for i, action in enumerate(actions[:7], 1):
                    result += f"{i}. {action}\n"

                if len(actions) > 7:
                    result += f"\n... and {len(actions) - 7} more actions"

                return result

            except Exception as e:
                logger.error(f"Error extracting actions: {e}")
                return f"Error extracting action items: {str(e)}"

        self.add_tool(
            name="extract_action_items",
            func=extract_action_items,
            description="Extract action items, tasks, and next steps from an email. Identifies what needs to be done and any deadlines. Input should be the email text."
        )

        # Tool 3: Categorize Email
        def categorize_email(email_text: str) -> str:
            """
            Categorize the email type based on content.
            Input should be the email text (subject + body).
            """
            try:
                text_lower = email_text.lower()

                # Category patterns
                categories = {
                    'INTERVIEW_INVITE': ['interview', 'schedule', 'meet with', 'speak with', 'chat with', 'call with'],
                    'REJECTION': ['unfortunately', 'not selected', 'decided not to', 'not moving forward', 'other candidates'],
                    'OFFER': ['offer', 'offer letter', 'compensation', 'start date', 'accept the offer'],
                    'ASSESSMENT': ['coding challenge', 'technical test', 'take-home', 'assessment', 'assignment'],
                    'SCREENING': ['phone screen', 'initial call', 'quick call', 'brief conversation'],
                    'FOLLOW_UP': ['following up', 'checking in', 'wanted to reach out', 'touching base'],
                    'CONFIRMATION': ['received your application', 'thank you for applying', 'application received'],
                    'STATUS_UPDATE': ['update on', 'status of', 'regarding your application', 'checking on'],
                }

                # Find matching categories
                matches = {}
                for category, keywords in categories.items():
                    count = sum(1 for keyword in keywords if keyword in text_lower)
                    if count > 0:
                        matches[category] = count

                if not matches:
                    return "CATEGORY: GENERAL (Unable to determine specific category)\nNo clear category indicators found."

                # Get top category
                top_category = max(matches.items(), key=lambda x: x[1])
                category_name = top_category[0].replace('_', ' ').title()

                result = f"📁 EMAIL CATEGORY\n\n"
                result += f"Primary Category: {category_name}\n"
                result += f"Confidence: {min(95, 50 + (top_category[1] * 15))}%\n\n"

                if len(matches) > 1:
                    result += "Other potential categories:\n"
                    for cat, score in sorted(matches.items(), key=lambda x: x[1], reverse=True)[1:3]:
                        result += f"  - {cat.replace('_', ' ').title()}\n"

                return result

            except Exception as e:
                logger.error(f"Error categorizing email: {e}")
                return f"Error categorizing email: {str(e)}"

        self.add_tool(
            name="categorize_email",
            func=categorize_email,
            description="Categorize the email type (e.g., interview invite, rejection, offer, assessment, screening, etc.). Input should be the email text."
        )

        # Tool 4: Extract Company and Position
        def extract_company_position(email_text: str) -> str:
            """
            Extract company name and job position from email.
            Input should be the email text.
            """
            try:
                # Common patterns for company names
                company_patterns = [
                    r'(?:at|from|with|join)\s+([A-Z][A-Za-z\s&.]+?)(?:\s+(?:for|as|regarding|about))',
                    r'([A-Z][A-Za-z\s&.]+?)\s+(?:team|recruiting|talent|hiring)',
                ]

                # Common patterns for positions
                position_patterns = [
                    r'(?:for the|for our|as a|as an)\s+([A-Za-z\s]+(?:Engineer|Developer|Manager|Analyst|Designer|Scientist|Lead|Architect))',
                    r'(?:position|role|opening):\s*([A-Za-z\s]+)',
                ]

                companies = []
                positions = []

                # Extract companies
                for pattern in company_patterns:
                    matches = re.findall(pattern, email_text)
                    for match in matches:
                        company = match.strip()
                        if 5 <= len(company) <= 40 and company not in companies:
                            companies.append(company)

                # Extract positions
                for pattern in position_patterns:
                    matches = re.findall(pattern, email_text, re.IGNORECASE)
                    for match in matches:
                        position = match.strip()
                        if 5 <= len(position) <= 50 and position not in positions:
                            positions.append(position)

                result = "🏢 EXTRACTED INFORMATION\n\n"

                if companies:
                    result += f"Company: {companies[0]}\n"
                    if len(companies) > 1:
                        result += f"  (Also mentioned: {', '.join(companies[1:3])})\n"
                else:
                    result += "Company: Not clearly identified\n"

                if positions:
                    result += f"Position: {positions[0]}\n"
                    if len(positions) > 1:
                        result += f"  (Also mentioned: {', '.join(positions[1:3])})\n"
                else:
                    result += "Position: Not clearly identified\n"

                return result

            except Exception as e:
                logger.error(f"Error extracting company/position: {e}")
                return f"Error extracting information: {str(e)}"

        self.add_tool(
            name="extract_company_position",
            func=extract_company_position,
            description="Extract company name and job position mentioned in the email. Input should be the email text."
        )

        # Tool 5: Find Matching Applications
        def find_matching_applications(search_query: str) -> str:
            """
            Search for job applications that match the email content (by company or position).
            Input should be a search query (company name or position).
            """
            try:
                all_apps = self.db_manager.get_all_applications()

                if not all_apps:
                    return "No job applications found in database."

                query_lower = search_query.lower()
                matches = []

                for app in all_apps:
                    company_match = query_lower in app.company.lower()
                    position_match = query_lower in app.position.lower()

                    if company_match or position_match:
                        match_score = 0
                        if company_match:
                            match_score += 2
                        if position_match:
                            match_score += 1

                        matches.append((app, match_score))

                if not matches:
                    return f"No applications found matching '{search_query}'"

                # Sort by match score
                matches.sort(key=lambda x: x[1], reverse=True)

                result = f"🎯 MATCHING APPLICATIONS ({len(matches)})\n\n"
                for app, score in matches[:5]:
                    result += f"✓ {app.company} - {app.position}\n"
                    result += f"  Status: {app.status} | Applied: {app.application_date}\n"
                    if app.notes:
                        result += f"  Notes: {app.notes[:80]}...\n"
                    result += "\n"

                if len(matches) > 5:
                    result += f"... and {len(matches) - 5} more matches"

                return result

            except Exception as e:
                logger.error(f"Error finding matches: {e}")
                return f"Error finding matching applications: {str(e)}"

        self.add_tool(
            name="find_matching_applications",
            func=find_matching_applications,
            description="Search for job applications in the database that match a company name or position title. Input should be the company name or position to search for."
        )

        # Tool 6: Recommend Follow-up Action
        def recommend_followup(email_category: str) -> str:
            """
            Recommend appropriate follow-up action based on email category.
            Input should be the email category (e.g., 'interview_invite', 'rejection', 'offer').
            """
            try:
                category_lower = email_category.lower().replace(' ', '_')

                recommendations = {
                    'interview_invite': {
                        'action': 'CONFIRM INTERVIEW',
                        'timeline': 'Within 24 hours',
                        'steps': [
                            'Reply confirming your availability',
                            'Prepare questions about the role',
                            'Research the company and interviewers',
                            'Review your resume and the job description',
                        ]
                    },
                    'rejection': {
                        'action': 'SEND THANK YOU & REQUEST FEEDBACK',
                        'timeline': 'Within 48 hours (optional)',
                        'steps': [
                            'Send a gracious thank-you note',
                            'Request constructive feedback (politely)',
                            'Express continued interest in the company',
                            'Update application status to "rejected"',
                        ]
                    },
                    'offer': {
                        'action': 'REVIEW & RESPOND',
                        'timeline': 'Within deadline (typically 1 week)',
                        'steps': [
                            'Review all offer details carefully',
                            'Research market salary for the role',
                            'Prepare questions or negotiation points',
                            'Respond by the deadline with decision or questions',
                        ]
                    },
                    'assessment': {
                        'action': 'COMPLETE ASSESSMENT',
                        'timeline': 'As specified in email',
                        'steps': [
                            'Note the deadline clearly',
                            'Block out sufficient time to complete',
                            'Prepare your development environment',
                            'Submit before the deadline',
                        ]
                    },
                    'screening': {
                        'action': 'SCHEDULE & PREPARE',
                        'timeline': 'Within 24 hours',
                        'steps': [
                            'Confirm your availability',
                            'Prepare elevator pitch',
                            'Research the company',
                            'Prepare questions to ask',
                        ]
                    },
                }

                rec = recommendations.get(category_lower, {
                    'action': 'RESPOND APPROPRIATELY',
                    'timeline': 'Within 24-48 hours',
                    'steps': ['Read the email carefully', 'Determine what action is needed', 'Respond professionally']
                })

                result = f"💡 FOLLOW-UP RECOMMENDATION\n\n"
                result += f"Recommended Action: {rec['action']}\n"
                result += f"Timeline: {rec['timeline']}\n\n"
                result += "Steps:\n"
                for i, step in enumerate(rec['steps'], 1):
                    result += f"  {i}. {step}\n"

                return result

            except Exception as e:
                logger.error(f"Error recommending follow-up: {e}")
                return f"Error generating recommendation: {str(e)}"

        self.add_tool(
            name="recommend_followup",
            func=recommend_followup,
            description="Recommend appropriate follow-up action based on email category. Input should be the email category (interview_invite, rejection, offer, assessment, screening, etc.)."
        )

    def get_system_prompt(self) -> str:
        """Define the agent's role and capabilities"""
        return """You are an Email Analyst Agent, an expert in analyzing job-related emails and providing actionable insights.

Your role is to:
1. Analyze email sentiment (positive, negative, neutral) and urgency
2. Extract action items and deadlines from emails
3. Categorize emails (interview, rejection, offer, assessment, etc.)
4. Identify company names and job positions mentioned
5. Match emails to existing job applications in the database
6. Recommend appropriate follow-up actions

You have access to powerful tools for:
- Sentiment analysis to determine if email is good/bad news
- Action item extraction to identify what needs to be done
- Email categorization to determine the email type
- Company and position extraction from email text
- Application matching to find related jobs in the database
- Follow-up recommendations based on email type

When analyzing an email:
1. First, use analyze_email_sentiment to understand the tone and urgency
2. Use categorize_email to determine what type of email it is
3. Use extract_company_position to identify the company and role
4. Use find_matching_applications to see if we have this application in our database
5. Use extract_action_items to identify what needs to be done
6. Use recommend_followup to suggest next steps

Always provide:
- Clear, actionable insights
- Specific recommendations with timelines
- Confidence levels for your analysis
- Well-reasoned explanations for your conclusions

Be thorough but concise. Focus on helping the user take the right action at the right time.
"""

    async def analyze_email(
        self,
        subject: str,
        body: str,
        sender: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze an email and provide comprehensive insights.

        Args:
            subject: Email subject line
            body: Email body content
            sender: Email sender address
            metadata: Optional metadata about the email

        Returns:
            Dictionary with analysis results
        """
        try:
            # Prepare email content
            email_content = f"Subject: {subject}\n\n{body}"

            if sender:
                email_content = f"From: {sender}\n{email_content}"

            # Create analysis request
            query = f"""Analyze this job-related email and provide comprehensive insights:

{email_content}

Please:
1. Determine the sentiment and urgency
2. Identify the email category
3. Extract company and position information
4. Find matching job applications if any
5. Extract action items
6. Recommend appropriate follow-up

Provide a structured analysis with actionable recommendations."""

            # Run the agent
            response = await self.run(query, context=metadata)

            # Store the analysis in memory for future reference
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Analyzed email from {sender} about {subject}: {response.output[:200]}",
                    category="email_analysis",
                    tags=[sender.split('@')[1] if '@' in sender else 'unknown', subject[:30]],
                )

            return {
                'success': response.success,
                'analysis': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in analyze_email: {e}")
            return {
                'success': False,
                'analysis': '',
                'error': str(e),
            }


def create_email_analyst_agent(db_manager, email_processor=None) -> EmailAnalystAgent:
    """Factory function to create Email Analyst Agent"""
    return EmailAnalystAgent(db_manager, email_processor)
