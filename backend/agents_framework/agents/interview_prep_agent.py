"""
Interview Prep Agent

This agent helps job seekers prepare for interviews with:
- Company and interviewer research
- Interview question generation
- STAR format answer preparation
- Mock interview practice
- Interview tips and strategies

Author: AI Agent Framework
Date: 2025-11-14
"""

import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from langchain_core.tools import tool

from ..core.base_agent import BaseAgent, AgentConfig, AgentResponse
from ..memory.agent_memory import AgentMemoryManager
from ..memory.vector_memory import RAGMemoryManager


class InterviewPrepAgent(BaseAgent):
    """
    Interview Prep Agent that helps candidates prepare for job interviews.

    Features:
    - Company and role research
    - Interview question generation (behavioral, technical, situational)
    - STAR format answer preparation
    - Mock interview practice sessions
    - Interview tips and strategies
    - Interviewer background research (when available)
    """

    def __init__(self, db_manager):
        """
        Initialize Interview Prep Agent.

        Args:
            db_manager: Database manager instance for data access
        """
        # Configure agent with appropriate settings
        config = AgentConfig(
            name="Interview Prep Agent",
            description="Helps candidates prepare for job interviews with research, questions, and practice",
            model="gpt-4o-mini",
            temperature=0.2,  # Balanced between analytical and creative
            max_iterations=12,
            enable_memory=True,
            memory_k=20
        )

        self.db_manager = db_manager

        # Initialize memory systems
        self.conversation_memory = AgentMemoryManager(
            agent_name="interview_prep",
            max_conversation_messages=30,
            enable_semantic=True
        )

        self.rag_memory = RAGMemoryManager(
            agent_name="interview_prep",
            persist_directory="./data/chroma"
        )

        # Track interview prep sessions
        self.prep_sessions = []

        super().__init__(config)

    def get_system_prompt(self) -> str:
        """
        Define the agent's role and capabilities.

        Returns:
            str: System prompt defining agent behavior
        """
        return """You are an expert Interview Prep Agent specialized in helping job candidates prepare for interviews.

Your responsibilities:
1. Research companies, roles, and interviewers to provide contextual insights
2. Generate relevant interview questions (behavioral, technical, situational)
3. Help candidates structure answers using the STAR format (Situation, Task, Action, Result)
4. Conduct mock interview practice sessions
5. Provide interview tips, strategies, and best practices
6. Analyze job descriptions to identify key interview focus areas

Your approach:
- Be thorough and detailed in research
- Generate questions that match the role level and industry
- Provide constructive feedback on answers
- Emphasize preparation and confidence-building
- Consider company culture when giving advice
- Use evidence-based interview techniques

When generating questions:
- Mix behavioral ("Tell me about a time..."), technical, and situational questions
- Align questions with the job description and company
- Include both common and role-specific questions
- Provide context for why each question might be asked

When helping with STAR answers:
- Guide the candidate to structure their response clearly
- Help identify strong examples from their experience
- Ensure answers are concise but complete
- Focus on quantifiable results when possible

Always be encouraging, supportive, and professional."""

    def _register_tools(self) -> None:
        """Register all tools available to the Interview Prep Agent."""

        # Tool 1: Research company
        @tool
        def research_company(company_name: str, job_description: str = "") -> str:
            """
            Research a company to provide interview context.

            Provides information about company culture, values, recent news,
            and how to align interview answers with company priorities.

            Args:
                company_name: Name of the company
                job_description: Optional job description for role-specific insights

            Returns:
                str: Company research summary with interview tips
            """
            try:
                # In a real implementation, this would call APIs or web scraping
                # For now, we'll provide a framework that can be extended

                research = {
                    "company": company_name,
                    "research_date": datetime.now().isoformat(),
                    "insights": []
                }

                # Basic company analysis based on name patterns and common knowledge
                company_lower = company_name.lower()

                # Industry detection
                if any(tech in company_lower for tech in ['google', 'microsoft', 'amazon', 'apple', 'meta', 'facebook']):
                    research["industry"] = "Big Tech"
                    research["insights"].append("Focus on scalability, innovation, and technical excellence")
                    research["insights"].append("Expect behavioral questions using STAR format")
                    research["insights"].append("Technical depth is crucial - prepare for system design")
                elif any(fin in company_lower for fin in ['bank', 'capital', 'finance', 'goldman', 'morgan']):
                    research["industry"] = "Finance"
                    research["insights"].append("Emphasize attention to detail and risk management")
                    research["insights"].append("Be prepared to discuss market knowledge")
                elif any(startup in company_lower for startup in ['startup', 'labs', 'ai']):
                    research["industry"] = "Startup/Innovation"
                    research["insights"].append("Highlight adaptability and entrepreneurial mindset")
                    research["insights"].append("Show ability to work with ambiguity")
                else:
                    research["industry"] = "General"
                    research["insights"].append("Research company values on their website")

                # General interview tips
                research["insights"].extend([
                    "Review the company's mission statement and values",
                    "Prepare questions about company culture and growth",
                    "Research recent company news and achievements",
                    "Understand the company's products/services thoroughly"
                ])

                # Role-specific insights from job description
                if job_description:
                    jd_lower = job_description.lower()
                    if "senior" in jd_lower or "lead" in jd_lower:
                        research["insights"].append("Prepare examples of leadership and mentorship")
                    if "team" in jd_lower:
                        research["insights"].append("Emphasize collaboration and communication skills")
                    if "python" in jd_lower or "java" in jd_lower or "javascript" in jd_lower:
                        research["insights"].append("Prepare for coding challenges and technical discussions")

                # Format output
                output = f"""
COMPANY RESEARCH: {company_name}
Industry: {research['industry']}
Research Date: {research['research_date']}

KEY INSIGHTS FOR INTERVIEW PREPARATION:
"""
                for i, insight in enumerate(research["insights"], 1):
                    output += f"{i}. {insight}\n"

                output += """
RECOMMENDED PREPARATION:
- Review company website, particularly About Us and Careers sections
- Check recent news articles about the company
- Look up company reviews on Glassdoor for interview insights
- Connect with current employees on LinkedIn if possible
- Prepare 3-5 thoughtful questions about the role and company

Note: This is a general research framework. For specific, up-to-date information,
please conduct additional research on the company's website and news sources.
"""

                return output.strip()

            except Exception as e:
                return f"Error researching company: {str(e)}"

        # Tool 2: Generate interview questions
        @tool
        def generate_interview_questions(
            job_title: str,
            job_description: str = "",
            company_name: str = "",
            question_type: str = "mixed"
        ) -> str:
            """
            Generate relevant interview questions based on role and company.

            Args:
                job_title: The job position title
                job_description: Full job description text
                company_name: Name of the company
                question_type: Type of questions - "behavioral", "technical", "situational", or "mixed"

            Returns:
                str: List of interview questions with context
            """
            try:
                questions = {
                    "role": job_title,
                    "company": company_name,
                    "type": question_type,
                    "questions": []
                }

                # Common behavioral questions (STAR format)
                behavioral_questions = [
                    {
                        "question": "Tell me about a time when you faced a significant challenge at work. How did you handle it?",
                        "focus": "Problem-solving and resilience",
                        "tip": "Use STAR format - highlight your specific actions and measurable results"
                    },
                    {
                        "question": "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                        "focus": "Interpersonal skills and conflict resolution",
                        "tip": "Show empathy and focus on positive outcomes"
                    },
                    {
                        "question": "Give an example of a goal you set and how you achieved it.",
                        "focus": "Goal-setting and achievement",
                        "tip": "Emphasize planning, execution, and results"
                    },
                    {
                        "question": "Tell me about a time when you failed. What did you learn?",
                        "focus": "Self-awareness and growth mindset",
                        "tip": "Be honest, focus on lessons learned and how you improved"
                    },
                    {
                        "question": "Describe a time when you had to adapt to a significant change at work.",
                        "focus": "Adaptability and flexibility",
                        "tip": "Show how you embraced change and made it work"
                    }
                ]

                # Technical/role-specific questions based on job title
                technical_questions = []
                title_lower = job_title.lower()
                desc_lower = job_description.lower() if job_description else ""

                if "engineer" in title_lower or "developer" in title_lower:
                    technical_questions = [
                        {
                            "question": "Walk me through your process for debugging a complex issue in production.",
                            "focus": "Technical problem-solving",
                            "tip": "Demonstrate systematic thinking and tools knowledge"
                        },
                        {
                            "question": "How do you ensure code quality in your projects?",
                            "focus": "Best practices and quality assurance",
                            "tip": "Mention testing, code reviews, and standards"
                        },
                        {
                            "question": "Describe a technically challenging project you worked on.",
                            "focus": "Technical depth and complexity handling",
                            "tip": "Explain the challenge, your approach, and the outcome"
                        }
                    ]
                elif "manager" in title_lower or "lead" in title_lower:
                    technical_questions = [
                        {
                            "question": "How do you prioritize tasks and projects for your team?",
                            "focus": "Leadership and prioritization",
                            "tip": "Discuss frameworks and stakeholder management"
                        },
                        {
                            "question": "Tell me about a time you had to give difficult feedback to a team member.",
                            "focus": "People management",
                            "tip": "Show empathy while maintaining accountability"
                        },
                        {
                            "question": "How do you measure team success?",
                            "focus": "Metrics and performance management",
                            "tip": "Balance quantitative metrics with team health"
                        }
                    ]
                elif "analyst" in title_lower or "data" in title_lower:
                    technical_questions = [
                        {
                            "question": "Walk me through how you would approach analyzing a new dataset.",
                            "focus": "Analytical methodology",
                            "tip": "Show structured thinking and attention to data quality"
                        },
                        {
                            "question": "Describe a time when your analysis led to a significant business decision.",
                            "focus": "Business impact",
                            "tip": "Quantify the impact and show business acumen"
                        },
                        {
                            "question": "How do you ensure the accuracy of your analyses?",
                            "focus": "Quality assurance and validation",
                            "tip": "Discuss verification methods and peer review"
                        }
                    ]
                else:
                    technical_questions = [
                        {
                            "question": f"What makes you qualified for this {job_title} role?",
                            "focus": "Relevant experience and skills",
                            "tip": "Connect your experience directly to job requirements"
                        },
                        {
                            "question": "What is your greatest professional strength?",
                            "focus": "Self-awareness and value proposition",
                            "tip": "Provide specific examples that demonstrate the strength"
                        }
                    ]

                # Situational questions
                situational_questions = [
                    {
                        "question": "If you noticed a colleague was struggling with their workload, what would you do?",
                        "focus": "Teamwork and initiative",
                        "tip": "Show willingness to help while respecting boundaries"
                    },
                    {
                        "question": "How would you handle a situation where you disagreed with your manager's decision?",
                        "focus": "Professional disagreement and communication",
                        "tip": "Emphasize respectful communication and understanding"
                    },
                    {
                        "question": "What would you do if you realized you couldn't meet a deadline?",
                        "focus": "Time management and communication",
                        "tip": "Show proactive communication and problem-solving"
                    }
                ]

                # Company-specific questions
                company_questions = [
                    {
                        "question": f"Why do you want to work at {company_name or 'our company'}?",
                        "focus": "Company fit and motivation",
                        "tip": "Research the company and connect your values to theirs"
                    },
                    {
                        "question": "Where do you see yourself in 5 years?",
                        "focus": "Career goals and long-term fit",
                        "tip": "Align your goals with potential growth at the company"
                    },
                    {
                        "question": "What questions do you have for us?",
                        "focus": "Engagement and interest",
                        "tip": "Prepare thoughtful questions about role, team, and company"
                    }
                ]

                # Select questions based on type
                if question_type == "behavioral":
                    questions["questions"] = behavioral_questions
                elif question_type == "technical":
                    questions["questions"] = technical_questions + situational_questions[:1]
                elif question_type == "situational":
                    questions["questions"] = situational_questions
                else:  # mixed
                    questions["questions"] = (
                        behavioral_questions[:3] +
                        technical_questions[:3] +
                        situational_questions[:2] +
                        company_questions
                    )

                # Format output
                output = f"""
INTERVIEW QUESTIONS FOR: {job_title}
Company: {company_name or 'General'}
Question Type: {question_type.title()}
Total Questions: {len(questions['questions'])}

"""
                for i, q in enumerate(questions["questions"], 1):
                    output += f"""
QUESTION {i}:
{q['question']}

Focus Area: {q['focus']}
Tip: {q['tip']}
{'=' * 80}
"""

                output += """
GENERAL INTERVIEW TIPS:
1. Use the STAR format for behavioral questions (Situation, Task, Action, Result)
2. Be specific with examples - use "I" not "we" to highlight your contributions
3. Quantify results when possible (percentages, timelines, impact)
4. Keep answers concise (1-2 minutes per question)
5. Ask clarifying questions if needed
6. Practice your answers out loud before the interview
"""

                return output.strip()

            except Exception as e:
                return f"Error generating questions: {str(e)}"

        # Tool 3: STAR format answer preparation
        @tool
        def prepare_star_answer(
            question: str,
            experience_summary: str = ""
        ) -> str:
            """
            Help structure an answer using the STAR format (Situation, Task, Action, Result).

            Args:
                question: The interview question to answer
                experience_summary: Optional brief summary of relevant experience

            Returns:
                str: STAR format template and guidance
            """
            try:
                output = f"""
STAR FORMAT ANSWER PREPARATION
Question: {question}

The STAR format is a structured way to answer behavioral interview questions:

S - SITUATION (Set the context)
   - Where and when did this happen?
   - Who was involved?
   - What was the background/context?
   - Keep it brief but clear

T - TASK (Describe your responsibility)
   - What was your specific role?
   - What was the goal or challenge?
   - What were you trying to accomplish?
   - Make your responsibility clear

A - ACTION (Explain what you did)
   - What specific steps did you take?
   - What skills did you use?
   - Why did you choose this approach?
   - Use "I" not "we" to highlight your contribution
   - This should be the longest part (50-60% of your answer)

R - RESULT (Share the outcome)
   - What happened as a result of your actions?
   - What did you accomplish?
   - What did you learn?
   - Quantify when possible (%, $, time saved, etc.)
   - Include positive outcomes even if the project didn't fully succeed

EXAMPLE STAR ANSWER STRUCTURE:
{'=' * 80}
[SITUATION - 15-20 seconds]
"In my previous role as [position] at [company], we were facing [context/challenge]..."

[TASK - 10-15 seconds]
"As the [your role], I was responsible for [specific responsibility/goal]..."

[ACTION - 45-60 seconds]
"I approached this by:
 1. First, I [specific action]...
 2. Then, I [specific action]...
 3. Finally, I [specific action]...
The key decision I made was [important choice] because [reasoning]..."

[RESULT - 20-30 seconds]
"As a result, we achieved [specific outcome]. This led to [impact],
which resulted in [quantifiable benefit like 30% improvement, $50K savings, etc.].
I learned [key lesson] which I've applied to [future situations]."
{'=' * 80}

YOUR ANSWER PREPARATION:
"""
                if experience_summary:
                    output += f"""
Based on your experience: {experience_summary}

Suggested STAR Structure:
"""
                else:
                    output += """
To prepare your answer, think about:
"""

                output += """
1. SITUATION: Think of a specific example from your experience
   - [ ] Identify the context and timeframe
   - [ ] Note who was involved
   - [ ] Set up the challenge or opportunity

2. TASK: Define your responsibility
   - [ ] What was your specific role?
   - [ ] What were you trying to achieve?
   - [ ] Why was this important?

3. ACTION: Detail your specific steps
   - [ ] List 3-5 specific actions you took
   - [ ] Explain your decision-making process
   - [ ] Highlight skills you used
   - [ ] Use "I" to show your contribution

4. RESULT: Quantify the outcome
   - [ ] What was the measurable impact?
   - [ ] What did stakeholders say?
   - [ ] What did you learn?
   - [ ] How did it benefit the organization?

TIPS FOR STRONG STAR ANSWERS:
✓ Be specific - generic answers don't stand out
✓ Focus on YOUR actions, not the team's
✓ Quantify results with numbers, percentages, or timelines
✓ Keep it concise (1.5-2 minutes total)
✓ Practice out loud to ensure smooth delivery
✓ Have 5-7 STAR stories prepared that cover different competencies
✓ End on a positive note, even if the project had challenges

COMMON MISTAKES TO AVOID:
✗ Being too vague ("we did some work...")
✗ Taking too long on situation/task (get to action quickly)
✗ Not highlighting YOUR specific contribution
✗ Forgetting to mention the result
✗ Not quantifying the impact
✗ Making up or exaggerating stories
"""

                return output.strip()

            except Exception as e:
                return f"Error preparing STAR answer: {str(e)}"

        # Tool 4: Mock interview practice
        @tool
        def conduct_mock_interview(
            job_title: str,
            focus_area: str = "general",
            difficulty: str = "medium"
        ) -> str:
            """
            Conduct a mock interview practice session.

            Args:
                job_title: The job position being prepared for
                focus_area: Area to focus on - "behavioral", "technical", "company-fit", or "general"
                difficulty: Difficulty level - "entry", "medium", or "senior"

            Returns:
                str: Mock interview questions and practice framework
            """
            try:
                session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

                output = f"""
MOCK INTERVIEW PRACTICE SESSION
Session ID: {session_id}
Position: {job_title}
Focus Area: {focus_area.title()}
Difficulty Level: {difficulty.title()}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}

{'=' * 80}
INTERVIEW SIMULATION
{'=' * 80}

INSTRUCTIONS:
This is a practice session to help you prepare. Answer each question as if
you were in a real interview. After each answer, reflect on:
- Did you use the STAR format (for behavioral questions)?
- Were you specific with examples?
- Did you quantify results?
- Was your answer concise (1-2 minutes)?

"""
                # Select questions based on focus and difficulty
                question_count = 5 if difficulty == "entry" else 7 if difficulty == "medium" else 10

                if focus_area == "behavioral":
                    practice_questions = [
                        "Tell me about yourself and your background.",
                        "Describe a time when you had to learn something new quickly.",
                        "Tell me about a time when you had to work under pressure.",
                        "Give me an example of when you showed leadership.",
                        "Describe a time when you received critical feedback. How did you respond?",
                        "Tell me about a time when you had to make a difficult decision.",
                        "Describe a situation where you had to persuade others.",
                        "Tell me about a time when you went above and beyond your job responsibilities.",
                        "Describe a time when you had to deal with ambiguity.",
                        "Tell me about your greatest professional achievement."
                    ]
                elif focus_area == "technical":
                    practice_questions = [
                        f"Walk me through your most complex project as a {job_title}.",
                        "How do you stay updated with industry trends and technologies?",
                        "Describe your problem-solving process when facing a technical challenge.",
                        "What tools and technologies are you most proficient in?",
                        "How do you approach code review / quality assurance?",
                        "Explain a technical concept to someone non-technical.",
                        "What's the most interesting technical challenge you've solved?",
                        "How do you balance technical debt with new feature development?",
                        "Describe your experience with [relevant technology from job description].",
                        "What's your approach to testing and debugging?"
                    ]
                elif focus_area == "company-fit":
                    practice_questions = [
                        "Why are you interested in this position?",
                        "What do you know about our company?",
                        "Why are you looking to leave your current role?",
                        "What are you looking for in your next opportunity?",
                        "How do you align with our company values?",
                        "Where do you see yourself in 3-5 years?",
                        "What makes you a good fit for our team?",
                        "What concerns do you have about this role?",
                        "What questions do you have for us?",
                        "Why should we hire you?"
                    ]
                else:  # general
                    practice_questions = [
                        "Tell me about yourself.",
                        "What are your greatest strengths?",
                        "What is your biggest weakness?",
                        "Tell me about a time when you faced a significant challenge.",
                        "Describe your ideal work environment.",
                        "How do you handle stress and pressure?",
                        "What motivates you?",
                        "Tell me about a time when you worked in a team.",
                        "Where do you see yourself in 5 years?",
                        "Why are you interested in this role?"
                    ]

                selected_questions = practice_questions[:question_count]

                for i, question in enumerate(selected_questions, 1):
                    output += f"""
QUESTION {i}/{question_count}:
{question}

[Take time to prepare your answer using STAR format if applicable]
[Speak your answer out loud - aim for 1-2 minutes]
[Record or write notes on your answer]

SELF-EVALUATION CHECKLIST:
□ Did I answer the question directly?
□ Did I use a specific example?
□ Did I explain my actions clearly?
□ Did I mention the result/impact?
□ Was my answer concise and well-structured?
□ Did I speak confidently and clearly?

{'=' * 80}
"""

                output += """
POST-INTERVIEW REFLECTION:

Rate your overall performance (1-10): ____

What went well:
1.
2.
3.

Areas for improvement:
1.
2.
3.

Questions to practice more:


Additional notes:


NEXT STEPS:
1. Review your answers and refine them
2. Practice the questions you struggled with
3. Record yourself answering to improve delivery
4. Schedule another mock interview in 2-3 days
5. Get feedback from a friend or mentor if possible

Remember: The goal is improvement, not perfection. Each practice session
makes you more confident and prepared for the real interview!
"""

                return output.strip()

            except Exception as e:
                return f"Error conducting mock interview: {str(e)}"

        # Tool 5: Interview tips and strategies
        @tool
        def get_interview_tips(
            interview_stage: str = "general",
            role_level: str = "mid"
        ) -> str:
            """
            Provide interview tips and strategies based on interview stage and role level.

            Args:
                interview_stage: Stage of interview - "phone-screen", "technical", "behavioral",
                               "panel", "final", or "general"
                role_level: Role level - "entry", "mid", "senior", or "executive"

            Returns:
                str: Comprehensive interview tips and strategies
            """
            try:
                output = f"""
INTERVIEW TIPS & STRATEGIES
Interview Stage: {interview_stage.title()}
Role Level: {role_level.title()}
{'=' * 80}

"""
                # General tips for all interviews
                output += """
UNIVERSAL INTERVIEW BEST PRACTICES:

BEFORE THE INTERVIEW:
✓ Research the company thoroughly (website, news, social media)
✓ Review the job description and match your experience to requirements
✓ Prepare 5-7 STAR stories covering different competencies
✓ Prepare thoughtful questions for the interviewer
✓ Test your tech setup (for virtual interviews)
✓ Plan your outfit and arrive/login 10 minutes early
✓ Review your resume and be ready to discuss everything on it
✓ Get a good night's sleep and eat before the interview

DURING THE INTERVIEW:
✓ Make a strong first impression (smile, eye contact, firm handshake/greeting)
✓ Listen carefully to questions before answering
✓ Ask for clarification if needed
✓ Use the STAR format for behavioral questions
✓ Be specific with examples and quantify results
✓ Show enthusiasm for the role and company
✓ Take brief pauses to think before complex answers
✓ Be honest - don't exaggerate or lie
✓ Keep answers concise (1-2 minutes typically)
✓ Ask thoughtful questions when given the opportunity

AFTER THE INTERVIEW:
✓ Send a thank-you email within 24 hours
✓ Reference specific topics discussed in the interview
✓ Reiterate your interest and key qualifications
✓ Reflect on what went well and what to improve
✓ Follow up appropriately based on their timeline

"""
                # Stage-specific tips
                if interview_stage == "phone-screen":
                    output += """
PHONE SCREEN SPECIFIC TIPS:
- This is usually 20-30 minutes with a recruiter
- Focus on your background, motivation, and basic qualifications
- Be ready to discuss salary expectations
- Have your resume in front of you for reference
- Be in a quiet location with good phone service
- Speak clearly and at a moderate pace
- Common questions: "Tell me about yourself", "Why this role?", "Salary expectations?"
- Goal: Get invited to the next round

"""
                elif interview_stage == "technical":
                    output += """
TECHNICAL INTERVIEW SPECIFIC TIPS:
- Practice coding problems on platforms like LeetCode, HackerRank
- Think out loud - explain your reasoning
- Ask clarifying questions about requirements
- Consider edge cases and error handling
- Discuss trade-offs in your approach
- Test your code with examples
- Be open to hints and feedback
- Know your resume's technical details deeply
- Review fundamental concepts (algorithms, data structures, system design)
- For system design: start with requirements, then high-level design, then details

"""
                elif interview_stage == "behavioral":
                    output += """
BEHAVIORAL INTERVIEW SPECIFIC TIPS:
- Use STAR format for every answer
- Prepare stories covering: leadership, conflict, failure, achievement, teamwork
- Be honest about challenges and what you learned
- Show self-awareness and growth mindset
- Quantify your impact with specific metrics
- Focus on YOUR actions, not just the team's
- Practice your stories out loud before the interview
- Have examples ready for: problem-solving, communication, adaptability, leadership
- Stay positive even when discussing challenges or failures

"""
                elif interview_stage == "panel":
                    output += """
PANEL INTERVIEW SPECIFIC TIPS:
- Make eye contact with all panel members, not just who asked the question
- Get everyone's names and roles at the start
- Address the questioner but engage everyone
- Pay attention to each person's reaction
- Take notes on who asked what
- Be consistent in your answers
- Don't get flustered by different questioning styles
- Some may play "good cop/bad cop" - stay calm
- Thank each person individually at the end
- Send individual thank-you emails if possible

"""
                elif interview_stage == "final":
                    output += """
FINAL INTERVIEW SPECIFIC TIPS:
- Usually with senior leadership or hiring manager
- Be ready for higher-level strategic questions
- Show you've researched the company deeply
- Demonstrate how you'll add value
- Be prepared to discuss compensation and start date
- Ask about next steps and timeline
- Show confidence without arrogance
- Reiterate your strong interest in the role
- Have insightful questions about company direction, team goals
- This is often more conversational - be yourself

"""

                # Role-level specific tips
                output += f"""
TIPS FOR {role_level.upper()} LEVEL ROLES:

"""
                if role_level == "entry":
                    output += """
- Emphasize your eagerness to learn and grow
- Highlight relevant coursework, projects, internships
- Show enthusiasm and cultural fit
- Discuss transferable skills from other experiences
- Be honest about what you don't know, but show willingness to learn
- Ask about training and mentorship opportunities
- Focus on your potential and work ethic
- Bring energy and fresh perspectives

"""
                elif role_level == "mid":
                    output += """
- Demonstrate your track record of results
- Show both technical skills and soft skills
- Provide examples of independence and initiative
- Discuss how you've mentored or helped others
- Show you can work with minimal supervision
- Balance confidence with humility
- Ask about growth opportunities and career path
- Highlight your ability to manage complex projects

"""
                elif role_level == "senior":
                    output += """
- Emphasize leadership and strategic thinking
- Discuss your impact on business outcomes
- Show evidence of mentoring and team development
- Demonstrate industry expertise and thought leadership
- Discuss how you've influenced company direction
- Show you can manage ambiguity and complexity
- Ask strategic questions about company vision
- Highlight your network and industry connections
- Be ready to discuss your management philosophy

"""
                elif role_level == "executive":
                    output += """
- Focus on business strategy and vision
- Discuss transformational changes you've led
- Show evidence of P&L responsibility
- Demonstrate board-level communication skills
- Discuss your leadership philosophy and values
- Show cultural and organizational impact
- Ask about board dynamics and company challenges
- Highlight your network at the executive level
- Be prepared for extensive background checks
- Discuss your approach to building and scaling teams

"""
                # Common pitfalls
                output += """
COMMON INTERVIEW MISTAKES TO AVOID:

❌ Arriving late or unprepared
❌ Badmouthing previous employers or colleagues
❌ Being too modest or too boastful
❌ Giving yes/no answers instead of detailed responses
❌ Not asking any questions
❌ Checking phone or appearing distracted
❌ Being dishonest or exaggerating achievements
❌ Not knowing basic information about the company
❌ Rambling or going off-topic
❌ Focusing on what you want instead of what you offer
❌ Appearing desperate or disinterested
❌ Not following up with a thank-you note

BODY LANGUAGE TIPS:

✓ Maintain good eye contact (but don't stare)
✓ Sit up straight with open posture
✓ Use hand gestures naturally when speaking
✓ Smile genuinely and show enthusiasm
✓ Nod to show you're listening
✓ Avoid fidgeting, crossing arms, or looking at phone
✓ Match the interviewer's energy level
✓ Take a confident stance when entering/exiting

HANDLING DIFFICULT QUESTIONS:

"What's your biggest weakness?"
→ Choose a real weakness but show how you're working on it
→ Example: "I tend to take on too much, but I'm learning to delegate more effectively"

"Why did you leave your last job?"
→ Stay positive, focus on what you're seeking, not what you're leaving
→ Never badmouth previous employers

"Where do you see yourself in 5 years?"
→ Show ambition aligned with the company's growth
→ Demonstrate you've thought about your career path

"Do you have any questions for us?"
→ ALWAYS have questions prepared
→ Ask about team dynamics, challenges, success metrics, growth opportunities
→ Avoid asking about salary/benefits in early rounds

Remember: Interviews are a two-way street. You're evaluating them as much as
they're evaluating you. Be authentic, prepared, and confident!
"""

                return output.strip()

            except Exception as e:
                return f"Error providing interview tips: {str(e)}"

        # Tool 6: Analyze job description for interview prep
        @tool
        def analyze_job_for_interview(job_description: str, job_title: str = "") -> str:
            """
            Analyze a job description to identify key interview focus areas and requirements.

            Args:
                job_description: The full job description text
                job_title: Optional job title

            Returns:
                str: Analysis of key skills, requirements, and interview focus areas
            """
            try:
                analysis = {
                    "job_title": job_title,
                    "required_skills": [],
                    "preferred_skills": [],
                    "key_responsibilities": [],
                    "interview_focus_areas": [],
                    "questions_to_prepare": []
                }

                jd_lower = job_description.lower()

                # Extract required skills (common patterns)
                skill_patterns = {
                    "programming": ["python", "java", "javascript", "c++", "go", "rust", "ruby"],
                    "frameworks": ["react", "angular", "vue", "django", "flask", "spring", "node"],
                    "databases": ["sql", "postgresql", "mysql", "mongodb", "redis", "dynamodb"],
                    "cloud": ["aws", "azure", "gcp", "cloud", "kubernetes", "docker"],
                    "tools": ["git", "jira", "jenkins", "ci/cd", "agile", "scrum"],
                    "soft_skills": ["leadership", "communication", "teamwork", "problem-solving", "analytical"]
                }

                found_skills = {}
                for category, skills in skill_patterns.items():
                    found_skills[category] = [skill for skill in skills if skill in jd_lower]

                # Determine seniority level
                seniority = "mid"
                if any(level in jd_lower for level in ["senior", "lead", "principal", "staff"]):
                    seniority = "senior"
                elif any(level in jd_lower for level in ["junior", "entry", "associate"]):
                    seniority = "entry"

                # Build analysis
                output = f"""
JOB DESCRIPTION ANALYSIS FOR INTERVIEW PREPARATION
Position: {job_title or "Not specified"}
Seniority Level: {seniority.title()}
Analysis Date: {datetime.now().strftime("%Y-%m-%d")}

{'=' * 80}
TECHNICAL SKILLS TO PREPARE:
"""

                for category, skills in found_skills.items():
                    if skills:
                        output += f"\n{category.upper().replace('_', ' ')}:\n"
                        for skill in skills:
                            output += f"  • {skill.title()}\n"

                # Generate interview focus areas
                output += f"""
{'=' * 80}
KEY INTERVIEW FOCUS AREAS:

"""

                focus_areas = []

                if found_skills["programming"]:
                    focus_areas.append("Technical coding ability - expect coding challenges or technical discussions")
                    analysis["questions_to_prepare"].append("Explain your most complex coding project")

                if found_skills["cloud"]:
                    focus_areas.append("Cloud architecture and scalability - be ready to discuss system design")
                    analysis["questions_to_prepare"].append("How do you design scalable systems?")

                if "leadership" in jd_lower or seniority == "senior":
                    focus_areas.append("Leadership and mentorship - prepare examples of leading projects or people")
                    analysis["questions_to_prepare"].append("Tell me about a time you led a team")

                if "team" in jd_lower or "collaboration" in jd_lower:
                    focus_areas.append("Teamwork and collaboration - show examples of cross-functional work")
                    analysis["questions_to_prepare"].append("Describe working with a difficult team member")

                if "agile" in jd_lower or "scrum" in jd_lower:
                    focus_areas.append("Agile methodology - be familiar with agile/scrum processes")
                    analysis["questions_to_prepare"].append("Describe your experience with agile development")

                # Add focus areas to output
                for i, area in enumerate(focus_areas, 1):
                    output += f"{i}. {area}\n"

                # Questions to prepare
                output += f"""
{'=' * 80}
QUESTIONS YOU SHOULD PREPARE FOR:

Based on this job description, expect questions about:
"""

                standard_questions = [
                    f"Why are you interested in this {job_title or 'position'}?",
                    "What relevant experience do you have for this role?",
                    "How do you stay current with industry trends?"
                ]

                all_questions = analysis["questions_to_prepare"] + standard_questions

                for i, question in enumerate(all_questions, 1):
                    output += f"\n{i}. {question}"

                # Preparation recommendations
                output += f"""

{'=' * 80}
RECOMMENDED PREPARATION STEPS:

1. SKILL REVIEW:
   - Review and practice with the technical skills mentioned
   - Prepare specific examples of using these technologies
   - Be ready to discuss projects in detail

2. STAR STORIES:
   - Prepare 5-7 STAR format stories covering:
     * Technical problem-solving
     * Leadership or initiative
     * Collaboration and teamwork
     * Handling pressure or deadlines
     * Learning and adaptation

3. COMPANY RESEARCH:
   - Study the company's products/services
   - Understand their market and competitors
   - Review recent news and company updates
   - Align your answers with company values

4. QUESTIONS TO ASK:
   - About the team structure and dynamics
   - About typical projects and challenges
   - About growth and learning opportunities
   - About success metrics for the role

5. PRACTICE:
   - Do mock interviews with the generated questions
   - Practice coding if it's a technical role
   - Review your resume and be ready to discuss each point
   - Time yourself to keep answers concise

Remember: The job description is a wish list. You don't need to match everything
perfectly. Focus on your strengths and how they align with the role's key requirements.
"""

                return output.strip()

            except Exception as e:
                return f"Error analyzing job description: {str(e)}"

        # Tool 7: Get interview preparation checklist
        @tool
        def get_interview_checklist(interview_date: str = "", interview_type: str = "general") -> str:
            """
            Generate a comprehensive interview preparation checklist.

            Args:
                interview_date: Date of interview in YYYY-MM-DD format
                interview_type: Type of interview - "phone", "video", "in-person", "technical", or "general"

            Returns:
                str: Detailed preparation checklist with timeline
            """
            try:
                # Calculate days until interview
                days_until = None
                if interview_date:
                    try:
                        interview_dt = datetime.strptime(interview_date, "%Y-%m-%d")
                        days_until = (interview_dt - datetime.now()).days
                    except:
                        pass

                output = f"""
INTERVIEW PREPARATION CHECKLIST
Interview Type: {interview_type.title()}
"""

                if interview_date:
                    output += f"Interview Date: {interview_date}\n"
                    if days_until is not None:
                        output += f"Days Until Interview: {days_until}\n"
                        if days_until < 0:
                            output += "⚠️  Interview date has passed!\n"
                        elif days_until == 0:
                            output += "🎯 Interview is TODAY!\n"
                        elif days_until <= 2:
                            output += "⏰ Interview is soon - prioritize high-impact preparation!\n"

                output += f"""
{'=' * 80}

PREPARATION TIMELINE:
"""

                # Create timeline based on days until interview
                if days_until and days_until > 0:
                    if days_until >= 7:
                        output += """
1 WEEK BEFORE:
□ Research the company thoroughly
□ Analyze the job description
□ Identify required skills and prepare examples
□ Start preparing STAR stories
□ Review your resume in detail
□ Set up informational interviews with current employees (if possible)

3-5 DAYS BEFORE:
□ Practice answering common interview questions
□ Conduct mock interviews
□ Prepare questions to ask the interviewer
□ Review technical skills if applicable
□ Research the interviewers on LinkedIn
□ Plan your outfit

"""
                    if days_until >= 2:
                        output += """
2 DAYS BEFORE:
□ Do final mock interview practice
□ Review your STAR stories
□ Prepare specific examples for key competencies
□ Research recent company news
□ Test technology for virtual interviews
□ Confirm interview time and location/link

"""
                    if days_until >= 1:
                        output += """
1 DAY BEFORE:
□ Review notes on company and role
□ Practice your 2-minute "tell me about yourself"
□ Prepare your questions for the interviewer
□ Plan your route/test video setup
□ Prepare documents (resume copies, portfolio, references)
□ Get good rest

"""

                output += """
DAY OF INTERVIEW:
□ Eat a good meal before the interview
□ Dress appropriately
□ Arrive/log in 10-15 minutes early
□ Bring/have ready: resume copies, notepad, pen, water
□ Review your notes one final time
□ Take a few deep breaths to calm nerves
□ Smile and be confident!

"""

                # Type-specific checklists
                if interview_type == "video":
                    output += """
VIDEO INTERVIEW SPECIFIC CHECKLIST:
□ Test camera, microphone, and speakers
□ Check internet connection stability
□ Find a quiet, well-lit location
□ Set up professional background
□ Close unnecessary programs/browser tabs
□ Silence phone and notifications
□ Have the interview link ready in advance
□ Test the video platform beforehand
□ Position camera at eye level
□ Dress professionally (full outfit, not just top half)
□ Have notes nearby but don't read from them
□ Look at the camera when speaking, not the screen

"""
                elif interview_type == "in-person":
                    output += """
IN-PERSON INTERVIEW SPECIFIC CHECKLIST:
□ Plan route and transportation
□ Account for traffic/delays
□ Bring physical copies of resume (3-5)
□ Bring portfolio if relevant
□ Prepare professional outfit
□ Bring notepad and pen
□ Have interviewer contact info for emergencies
□ Know parking/building entry details
□ Bring mints/gum (use before, not during)
□ Arrive 10-15 minutes early
□ Turn off phone before entering
□ Prepare for firm handshake and eye contact

"""
                elif interview_type == "phone":
                    output += """
PHONE INTERVIEW SPECIFIC CHECKLIST:
□ Find quiet location with good cell service
□ Have resume and notes in front of you
□ Have company research notes ready
□ Use headphones for better audio
□ Charge phone fully
□ Have backup phone number ready
□ Eliminate background noise
□ Stand or sit up straight (helps voice projection)
□ Smile while talking (it changes your tone)
□ Take notes during the call
□ Have water nearby

"""
                elif interview_type == "technical":
                    output += """
TECHNICAL INTERVIEW SPECIFIC CHECKLIST:
□ Review data structures and algorithms
□ Practice coding problems on LeetCode/HackerRank
□ Prepare for system design questions
□ Review your past projects in detail
□ Be ready to explain technical decisions
□ Practice thinking out loud while coding
□ Review fundamental computer science concepts
□ Prepare questions about technical stack
□ Have code examples ready to share
□ Review job description technical requirements
□ Practice on whiteboard or coding platform
□ Know time/space complexity analysis

"""
                # General preparation checklist
                output += f"""
{'=' * 80}
CONTENT PREPARATION CHECKLIST:

RESEARCH:
□ Company mission, values, and culture
□ Company products/services
□ Recent company news and developments
□ Competitors and market position
□ Interviewer backgrounds (LinkedIn)
□ Company reviews on Glassdoor

MATERIALS:
□ Resume (updated and proofread)
□ Cover letter (if applicable)
□ Portfolio or work samples
□ References list (formatted)
□ List of questions for interviewer
□ Notepad and pen

STORIES & EXAMPLES:
□ 2-minute "Tell me about yourself"
□ Why you want this job
□ Why you're leaving current role
□ Leadership example
□ Teamwork example
□ Conflict resolution example
□ Failure/learning example
□ Achievement example
□ Technical challenge example
□ Innovation/creativity example

QUESTIONS TO ASK:
□ About team dynamics and culture
□ About day-to-day responsibilities
□ About success metrics
□ About challenges in the role
□ About growth opportunities
□ About next steps in process
(Prepare 5-7 questions, ask 2-3)

LOGISTICS:
□ Confirm date, time, and location/link
□ Know interviewer names and titles
□ Understand interview format and duration
□ Have contact information for any issues
□ Plan travel time with buffer
□ Prepare backup plan for technology issues

{'=' * 80}
FINAL CHECKLIST (Last Hour):

□ Use restroom
□ Check appearance (hair, outfit, etc.)
□ Silence all devices
□ Have water available
□ Review key points about company and role
□ Practice your introduction
□ Take deep breaths to calm nerves
□ Remind yourself of your qualifications
□ Adopt a confident posture
□ SMILE and be yourself!

AFTER THE INTERVIEW:
□ Send thank-you email within 24 hours
□ Reference specific discussion points
□ Reiterate interest in role
□ Take notes on questions asked
□ Reflect on what went well
□ Identify areas to improve
□ Follow up appropriately per their timeline

Remember: Preparation reduces anxiety and increases confidence.
You've got this! 🎯
"""

                return output.strip()

            except Exception as e:
                return f"Error generating checklist: {str(e)}"

        # Register all tools
        self.add_tool(
            name="research_company",
            func=research_company,
            description="Research a company to provide interview preparation context and insights"
        )

        self.add_tool(
            name="generate_interview_questions",
            func=generate_interview_questions,
            description="Generate relevant interview questions based on role, company, and question type"
        )

        self.add_tool(
            name="prepare_star_answer",
            func=prepare_star_answer,
            description="Help structure answers using STAR format (Situation, Task, Action, Result)"
        )

        self.add_tool(
            name="conduct_mock_interview",
            func=conduct_mock_interview,
            description="Conduct a mock interview practice session with relevant questions"
        )

        self.add_tool(
            name="get_interview_tips",
            func=get_interview_tips,
            description="Provide interview tips and strategies based on stage and role level"
        )

        self.add_tool(
            name="analyze_job_for_interview",
            func=analyze_job_for_interview,
            description="Analyze job description to identify key interview focus areas"
        )

        self.add_tool(
            name="get_interview_checklist",
            func=get_interview_checklist,
            description="Generate comprehensive interview preparation checklist with timeline"
        )

    # High-level methods for common workflows

    async def prepare_for_interview(
        self,
        job_id: int = None,
        company_name: str = "",
        job_title: str = "",
        job_description: str = "",
        interview_date: str = "",
        interview_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Comprehensive interview preparation workflow.

        Args:
            job_id: Optional job application ID from database
            company_name: Company name
            job_title: Job position title
            job_description: Full job description
            interview_date: Interview date (YYYY-MM-DD)
            interview_type: Type of interview

        Returns:
            dict: Comprehensive interview preparation plan
        """
        try:
            # If job_id provided, fetch from database
            if job_id and self.db_manager:
                job = self.db_manager.get_job_application(job_id)
                if job:
                    company_name = company_name or job.get("company", "")
                    job_title = job_title or job.get("position", "")
                    job_description = job_description or job.get("job_description", "")

            # Build comprehensive preparation query
            query = f"""
I need to prepare for an interview for the position of {job_title} at {company_name}.

Interview Date: {interview_date or "Not specified"}
Interview Type: {interview_type}

Please help me prepare by:
1. Researching the company and providing interview insights
2. Analyzing the job description to identify focus areas
3. Generating relevant interview questions I should prepare for
4. Providing a preparation checklist with timeline

Job Description:
{job_description[:1000] if job_description else "Not provided"}
"""

            # Run agent
            response = await self.run(query, context={
                "job_id": job_id,
                "company": company_name,
                "position": job_title,
                "interview_date": interview_date,
                "interview_type": interview_type
            })

            # Store in memory for future reference
            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Prepared interview for {job_title} at {company_name}: {response.output[:500]}",
                    category="interview_preparation",
                    tags=[company_name, job_title, interview_type]
                )

            return {
                "success": response.success,
                "preparation_plan": response.output,
                "metadata": {
                    "company": company_name,
                    "position": job_title,
                    "interview_date": interview_date,
                    "interview_type": interview_type,
                    **response.metadata
                },
                "error": response.error
            }

        except Exception as e:
            return {
                "success": False,
                "preparation_plan": "",
                "metadata": {},
                "error": str(e)
            }

    async def generate_practice_questions(
        self,
        job_title: str,
        company_name: str = "",
        job_description: str = "",
        question_type: str = "mixed",
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Generate interview practice questions.

        Args:
            job_title: Job position title
            company_name: Company name
            job_description: Job description
            question_type: Type of questions to generate
            difficulty: Difficulty level

        Returns:
            dict: Generated questions with guidance
        """
        try:
            query = f"""
Generate {question_type} interview questions for a {job_title} position at {company_name}.
Difficulty level: {difficulty}

{f"Job Description: {job_description[:500]}" if job_description else ""}

Provide a comprehensive set of questions that would be relevant for this role.
"""

            response = await self.run(query, context={
                "job_title": job_title,
                "company": company_name,
                "question_type": question_type,
                "difficulty": difficulty
            })

            return {
                "success": response.success,
                "questions": response.output,
                "metadata": {
                    "job_title": job_title,
                    "question_type": question_type,
                    "difficulty": difficulty,
                    **response.metadata
                },
                "error": response.error
            }

        except Exception as e:
            return {
                "success": False,
                "questions": "",
                "metadata": {},
                "error": str(e)
            }

    async def practice_star_answer(
        self,
        question: str,
        experience_context: str = ""
    ) -> Dict[str, Any]:
        """
        Help prepare a STAR format answer for a specific question.

        Args:
            question: The interview question
            experience_context: Optional context about relevant experience

        Returns:
            dict: STAR answer framework and guidance
        """
        try:
            query = f"""
Help me prepare a STAR format answer for this interview question:
"{question}"

{f"Relevant experience context: {experience_context}" if experience_context else ""}

Provide a detailed STAR framework and tips for answering this question effectively.
"""

            response = await self.run(query, context={
                "question": question,
                "experience_context": experience_context
            })

            return {
                "success": response.success,
                "star_framework": response.output,
                "metadata": {
                    "question": question,
                    **response.metadata
                },
                "error": response.error
            }

        except Exception as e:
            return {
                "success": False,
                "star_framework": "",
                "metadata": {},
                "error": str(e)
            }

    async def start_mock_interview(
        self,
        job_title: str,
        focus_area: str = "general",
        difficulty: str = "medium"
    ) -> Dict[str, Any]:
        """
        Start a mock interview practice session.

        Args:
            job_title: Job position
            focus_area: Area to focus practice on
            difficulty: Difficulty level

        Returns:
            dict: Mock interview questions and framework
        """
        try:
            query = f"""
I want to practice for a {job_title} interview.
Focus area: {focus_area}
Difficulty: {difficulty}

Please conduct a mock interview with me, providing questions and evaluation criteria.
"""

            response = await self.run(query, context={
                "job_title": job_title,
                "focus_area": focus_area,
                "difficulty": difficulty,
                "session_type": "mock_interview"
            })

            # Track session
            session = {
                "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "job_title": job_title,
                "focus_area": focus_area,
                "difficulty": difficulty,
                "date": datetime.now().isoformat(),
                "questions": response.output
            }
            self.prep_sessions.append(session)

            return {
                "success": response.success,
                "mock_interview": response.output,
                "session_id": session["session_id"],
                "metadata": {
                    "job_title": job_title,
                    "focus_area": focus_area,
                    "difficulty": difficulty,
                    **response.metadata
                },
                "error": response.error
            }

        except Exception as e:
            return {
                "success": False,
                "mock_interview": "",
                "session_id": None,
                "metadata": {},
                "error": str(e)
            }


def create_interview_prep_agent(db_manager) -> InterviewPrepAgent:
    """
    Factory function to create an Interview Prep Agent instance.

    Args:
        db_manager: Database manager for data access

    Returns:
        InterviewPrepAgent: Configured agent instance
    """
    return InterviewPrepAgent(db_manager)
