"""
Job Hunter Agent - Autonomous Job Search and Matching

This agent handles:
- Autonomous job searching across multiple platforms
- Job-to-preference matching with intelligent ranking
- Company research and analysis
- Job recommendations based on user profile
"""

import json
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from langchain_core.messages import SystemMessage

from ..core.base_agent import BaseAgent, AgentConfig, AgentResponse
from ...database import DatabaseManager


class JobHunterAgent(BaseAgent):
    """
    Job Hunter Agent for autonomous job search and matching.

    Uses ReAct pattern to:
    1. Search job boards based on user preferences
    2. Match jobs to user profile and preferences
    3. Research companies for better recommendations
    4. Provide ranked job recommendations
    """

    def __init__(
        self,
        db_manager: DatabaseManager,
        config: Optional[AgentConfig] = None
    ):
        """Initialize Job Hunter Agent."""
        self.db_manager = db_manager
        super().__init__(config or AgentConfig(
            agent_name="job_hunter",
            model="gpt-4o-mini",
            temperature=0.3,  # Lower temperature for more focused job searches
            max_iterations=15,
            enable_memory=True
        ))

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Job Hunter Agent."""
        return """You are an expert Job Hunter Agent specializing in finding and matching job opportunities.

Your responsibilities:
1. Search for jobs across multiple platforms based on user preferences
2. Analyze job postings to extract key information (title, company, location, salary, requirements)
3. Match jobs to user preferences and profile using intelligent ranking
4. Research companies to provide additional context
5. Provide comprehensive job recommendations with reasoning

When analyzing jobs:
- Extract all relevant details (title, company, location, salary range, experience level)
- Identify required and preferred qualifications
- Assess company culture and benefits
- Calculate match score based on user preferences
- Provide clear reasoning for recommendations

Use the available tools to:
- Search job boards (LinkedIn, Indeed, Glassdoor, etc.)
- Extract job details from postings
- Match jobs to user preferences
- Research companies
- Get user profile and preferences

Always provide actionable recommendations with clear reasoning."""

    def _register_tools(self) -> List:
        """Register tools for the Job Hunter Agent."""

        @tool
        def search_linkedin_jobs(
            keywords: str,
            location: str = "",
            experience_level: str = "",
            job_type: str = ""
        ) -> str:
            """
            Search for jobs on LinkedIn.

            Args:
                keywords: Job title or keywords to search for (e.g., "Software Engineer", "Data Scientist")
                location: Location for the job search (e.g., "San Francisco, CA", "Remote")
                experience_level: Experience level filter (e.g., "Entry level", "Mid-Senior level", "Director")
                job_type: Job type filter (e.g., "Full-time", "Contract", "Internship")

            Returns:
                JSON string with job listings from LinkedIn
            """
            # Simulated LinkedIn job search
            # In production, this would use LinkedIn API or web scraping
            jobs = [
                {
                    "id": f"linkedin_{i}",
                    "platform": "LinkedIn",
                    "title": f"{keywords} - {experience_level or 'Mid-Senior level'}",
                    "company": f"Tech Company {i}",
                    "location": location or "San Francisco, CA",
                    "job_type": job_type or "Full-time",
                    "experience_level": experience_level or "Mid-Senior level",
                    "posted_date": "2 days ago",
                    "salary_range": "$120K - $180K",
                    "description": f"Looking for a talented {keywords} to join our growing team. Must have experience with modern tech stack.",
                    "requirements": [
                        "3+ years of experience",
                        "Strong problem-solving skills",
                        "Team collaboration experience"
                    ],
                    "benefits": [
                        "Health insurance",
                        "401k matching",
                        "Remote work options"
                    ],
                    "url": f"https://linkedin.com/jobs/view/{i}"
                }
                for i in range(1, 4)
            ]

            return json.dumps({
                "success": True,
                "platform": "LinkedIn",
                "query": {
                    "keywords": keywords,
                    "location": location,
                    "experience_level": experience_level,
                    "job_type": job_type
                },
                "total_results": len(jobs),
                "jobs": jobs
            }, indent=2)

        @tool
        def search_indeed_jobs(
            keywords: str,
            location: str = "",
            salary_min: int = 0,
            job_type: str = ""
        ) -> str:
            """
            Search for jobs on Indeed.

            Args:
                keywords: Job title or keywords to search for
                location: Location for the job search
                salary_min: Minimum salary filter (in thousands, e.g., 100 for $100K)
                job_type: Job type filter (e.g., "fulltime", "contract", "parttime")

            Returns:
                JSON string with job listings from Indeed
            """
            # Simulated Indeed job search
            jobs = [
                {
                    "id": f"indeed_{i}",
                    "platform": "Indeed",
                    "title": f"{keywords} Position",
                    "company": f"Company {chr(65+i)}",
                    "location": location or "Remote",
                    "job_type": job_type or "Full-time",
                    "posted_date": f"{i} days ago",
                    "salary_range": f"${salary_min}K - ${salary_min + 50}K" if salary_min > 0 else "Competitive",
                    "description": f"We are seeking an experienced {keywords} to contribute to our innovative projects.",
                    "requirements": [
                        "Bachelor's degree or equivalent",
                        "Relevant experience in the field",
                        "Excellent communication skills"
                    ],
                    "url": f"https://indeed.com/viewjob?jk={i}"
                }
                for i in range(1, 4)
            ]

            return json.dumps({
                "success": True,
                "platform": "Indeed",
                "query": {
                    "keywords": keywords,
                    "location": location,
                    "salary_min": salary_min,
                    "job_type": job_type
                },
                "total_results": len(jobs),
                "jobs": jobs
            }, indent=2)

        @tool
        def search_glassdoor_jobs(
            keywords: str,
            location: str = "",
            company_rating_min: float = 0.0
        ) -> str:
            """
            Search for jobs on Glassdoor with company ratings.

            Args:
                keywords: Job title or keywords to search for
                location: Location for the job search
                company_rating_min: Minimum company rating filter (0.0 - 5.0)

            Returns:
                JSON string with job listings from Glassdoor including company ratings
            """
            # Simulated Glassdoor job search
            jobs = [
                {
                    "id": f"glassdoor_{i}",
                    "platform": "Glassdoor",
                    "title": f"{keywords}",
                    "company": f"Rated Company {i}",
                    "location": location or "New York, NY",
                    "company_rating": round(3.5 + (i * 0.3), 1),
                    "company_reviews": 100 + (i * 50),
                    "posted_date": f"{i * 2} days ago",
                    "salary_estimate": "$100K - $150K (Glassdoor est.)",
                    "description": f"Join our team as a {keywords} and make an impact.",
                    "pros": [
                        "Great work-life balance",
                        "Competitive compensation",
                        "Learning opportunities"
                    ],
                    "cons": [
                        "Fast-paced environment",
                        "High expectations"
                    ],
                    "url": f"https://glassdoor.com/job-listing/{i}"
                }
                for i in range(1, 3)
                if (3.5 + (i * 0.3)) >= company_rating_min
            ]

            return json.dumps({
                "success": True,
                "platform": "Glassdoor",
                "query": {
                    "keywords": keywords,
                    "location": location,
                    "company_rating_min": company_rating_min
                },
                "total_results": len(jobs),
                "jobs": jobs
            }, indent=2)

        @tool
        def extract_job_details(job_description: str) -> str:
            """
            Extract structured details from a job description.

            Args:
                job_description: Raw job description text

            Returns:
                JSON string with extracted job details
            """
            # Simple extraction using regex patterns
            # In production, this would use NLP/LLM for better extraction

            details = {
                "required_skills": [],
                "preferred_skills": [],
                "experience_years": None,
                "education_required": None,
                "responsibilities": [],
                "tech_stack": [],
                "benefits": []
            }

            # Extract experience years
            exp_match = re.search(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', job_description, re.IGNORECASE)
            if exp_match:
                details["experience_years"] = int(exp_match.group(1))

            # Extract education
            edu_patterns = ['bachelor', 'master', 'phd', 'degree']
            for pattern in edu_patterns:
                if re.search(pattern, job_description, re.IGNORECASE):
                    details["education_required"] = pattern.capitalize()
                    break

            # Extract common tech skills
            tech_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes']
            for tech in tech_keywords:
                if re.search(rf'\b{tech}\b', job_description, re.IGNORECASE):
                    details["tech_stack"].append(tech.upper() if len(tech) <= 4 else tech.capitalize())

            # Extract benefits
            benefit_keywords = ['insurance', '401k', 'remote', 'pto', 'vacation', 'bonus', 'equity']
            for benefit in benefit_keywords:
                if re.search(rf'\b{benefit}\b', job_description, re.IGNORECASE):
                    details["benefits"].append(benefit.capitalize())

            return json.dumps(details, indent=2)

        @tool
        def get_user_preferences(user_id: int = 1) -> str:
            """
            Get user's job search preferences from the database.

            Args:
                user_id: User ID to get preferences for (default: 1)

            Returns:
                JSON string with user preferences
            """
            # Mock user preferences - in production, fetch from database
            preferences = {
                "user_id": user_id,
                "preferred_roles": [
                    "Software Engineer",
                    "Backend Developer",
                    "Full Stack Engineer"
                ],
                "preferred_locations": [
                    "San Francisco, CA",
                    "Remote",
                    "New York, NY"
                ],
                "preferred_industries": [
                    "Technology",
                    "FinTech",
                    "SaaS"
                ],
                "salary_min": 120000,
                "salary_max": 200000,
                "job_type": ["Full-time", "Contract"],
                "experience_level": "Mid-Senior level",
                "required_benefits": [
                    "Health insurance",
                    "Remote work",
                    "401k"
                ],
                "skills": [
                    "Python",
                    "JavaScript",
                    "React",
                    "Node.js",
                    "PostgreSQL",
                    "AWS"
                ],
                "years_experience": 5,
                "education": "Bachelor's degree",
                "work_authorization": "US Citizen",
                "willing_to_relocate": False,
                "remote_preference": "Remote or Hybrid"
            }

            return json.dumps(preferences, indent=2)

        @tool
        def calculate_job_match_score(
            job_data: str,
            user_preferences: str
        ) -> str:
            """
            Calculate how well a job matches user preferences.

            Args:
                job_data: JSON string with job details
                user_preferences: JSON string with user preferences

            Returns:
                JSON string with match score and breakdown
            """
            try:
                job = json.loads(job_data)
                prefs = json.loads(user_preferences)

                score_breakdown = {
                    "title_match": 0,
                    "location_match": 0,
                    "salary_match": 0,
                    "skills_match": 0,
                    "experience_match": 0,
                    "benefits_match": 0,
                    "company_rating": 0
                }

                # Title match (30 points)
                job_title = job.get("title", "").lower()
                for preferred_role in prefs.get("preferred_roles", []):
                    if preferred_role.lower() in job_title:
                        score_breakdown["title_match"] = 30
                        break
                    elif any(word in job_title for word in preferred_role.lower().split()):
                        score_breakdown["title_match"] = 15

                # Location match (20 points)
                job_location = job.get("location", "").lower()
                for preferred_loc in prefs.get("preferred_locations", []):
                    if preferred_loc.lower() in job_location or job_location in preferred_loc.lower():
                        score_breakdown["location_match"] = 20
                        break

                # Salary match (20 points)
                salary_range = job.get("salary_range", "")
                if salary_range and prefs.get("salary_min"):
                    # Simple parsing - extract numbers from salary range
                    numbers = re.findall(r'\d+', salary_range.replace(',', ''))
                    if numbers:
                        job_salary = int(numbers[0]) * 1000
                        if job_salary >= prefs["salary_min"]:
                            score_breakdown["salary_match"] = 20
                        elif job_salary >= prefs["salary_min"] * 0.8:
                            score_breakdown["salary_match"] = 10

                # Skills match (15 points)
                job_desc = job.get("description", "").lower()
                user_skills = [skill.lower() for skill in prefs.get("skills", [])]
                matched_skills = [skill for skill in user_skills if skill in job_desc]
                if user_skills:
                    score_breakdown["skills_match"] = int((len(matched_skills) / len(user_skills)) * 15)

                # Experience match (10 points)
                job_exp_level = job.get("experience_level", "").lower()
                pref_exp_level = prefs.get("experience_level", "").lower()
                if pref_exp_level in job_exp_level or job_exp_level in pref_exp_level:
                    score_breakdown["experience_match"] = 10

                # Benefits match (5 points)
                job_benefits = job.get("benefits", [])
                required_benefits = prefs.get("required_benefits", [])
                if job_benefits and required_benefits:
                    matched_benefits = [b for b in required_benefits if any(jb.lower() in b.lower() for jb in job_benefits)]
                    score_breakdown["benefits_match"] = int((len(matched_benefits) / len(required_benefits)) * 5)

                # Company rating bonus (10 points)
                company_rating = job.get("company_rating", 0)
                if company_rating >= 4.0:
                    score_breakdown["company_rating"] = 10
                elif company_rating >= 3.5:
                    score_breakdown["company_rating"] = 5

                total_score = sum(score_breakdown.values())

                return json.dumps({
                    "total_score": total_score,
                    "score_breakdown": score_breakdown,
                    "match_level": "Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Fair" if total_score >= 40 else "Poor",
                    "matched_skills": matched_skills if 'matched_skills' in locals() else [],
                    "recommendation": "Highly recommended - great match!" if total_score >= 80 else
                                    "Good match - worth applying" if total_score >= 60 else
                                    "Moderate match - consider if interested" if total_score >= 40 else
                                    "Low match - may not align with preferences"
                }, indent=2)

            except Exception as e:
                return json.dumps({
                    "error": f"Failed to calculate match score: {str(e)}",
                    "total_score": 0
                }, indent=2)

        @tool
        def research_company(company_name: str) -> str:
            """
            Research a company to provide additional context.

            Args:
                company_name: Name of the company to research

            Returns:
                JSON string with company research data
            """
            # Simulated company research
            # In production, this would fetch from Glassdoor, LinkedIn, Crunchbase, etc.

            company_data = {
                "company_name": company_name,
                "industry": "Technology",
                "size": "500-1000 employees",
                "founded": "2015",
                "headquarters": "San Francisco, CA",
                "rating": 4.2,
                "total_reviews": 234,
                "culture_values": [
                    "Innovation",
                    "Collaboration",
                    "Work-life balance"
                ],
                "pros": [
                    "Great benefits and compensation",
                    "Talented team and learning opportunities",
                    "Flexible work arrangements",
                    "Cutting-edge technology stack"
                ],
                "cons": [
                    "Fast-paced environment can be demanding",
                    "Some organizational changes recently",
                    "Limited upward mobility in some teams"
                ],
                "ceo_rating": 4.5,
                "recommend_to_friend": "85%",
                "business_outlook": "Positive",
                "funding": "Series C - $150M raised",
                "key_investors": [
                    "Sequoia Capital",
                    "Andreessen Horowitz"
                ],
                "recent_news": [
                    "Launched new product line in Q4 2024",
                    "Expanded to European market",
                    "Received industry award for innovation"
                ],
                "tech_stack": [
                    "Python",
                    "React",
                    "AWS",
                    "Kubernetes",
                    "PostgreSQL"
                ],
                "interview_difficulty": "Medium",
                "interview_process": "Phone screen → Technical assessment → Team interview → Final round"
            }

            return json.dumps(company_data, indent=2)

        @tool
        def save_job_recommendation(
            job_data: str,
            match_score: int,
            user_id: int = 1
        ) -> str:
            """
            Save a job recommendation to the database.

            Args:
                job_data: JSON string with job details
                match_score: Match score (0-100)
                user_id: User ID to save for

            Returns:
                Success message with saved job ID
            """
            try:
                job = json.loads(job_data)
                # In production, save to database
                # For now, return success message

                return json.dumps({
                    "success": True,
                    "message": f"Saved job recommendation: {job.get('title')} at {job.get('company')}",
                    "job_id": job.get("id"),
                    "match_score": match_score,
                    "saved_at": datetime.now().isoformat()
                }, indent=2)
            except Exception as e:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to save recommendation: {str(e)}"
                }, indent=2)

        return [
            search_linkedin_jobs,
            search_indeed_jobs,
            search_glassdoor_jobs,
            extract_job_details,
            get_user_preferences,
            calculate_job_match_score,
            research_company,
            save_job_recommendation
        ]

    async def search_jobs(
        self,
        keywords: str,
        location: str = "",
        platforms: List[str] = None,
        filters: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        Search for jobs across multiple platforms.

        Args:
            keywords: Job search keywords
            location: Location filter
            platforms: List of platforms to search (default: all)
            filters: Additional filters (experience_level, job_type, salary_min, etc.)

        Returns:
            AgentResponse with job search results
        """
        if platforms is None:
            platforms = ["LinkedIn", "Indeed", "Glassdoor"]

        filters = filters or {}

        query = f"""Search for '{keywords}' jobs in '{location or 'any location'}' on {', '.join(platforms)}.

Apply these filters if relevant: {json.dumps(filters)}

For each job found:
1. Extract job details
2. Get user preferences
3. Calculate match score
4. Research the company
5. Save high-quality recommendations (match score >= 60)

Provide a comprehensive summary of the best job matches."""

        return await self.run(query)

    async def get_recommendations(
        self,
        user_id: int = 1,
        limit: int = 10
    ) -> AgentResponse:
        """
        Get personalized job recommendations for a user.

        Args:
            user_id: User ID to get recommendations for
            limit: Maximum number of recommendations

        Returns:
            AgentResponse with ranked job recommendations
        """
        query = f"""Get personalized job recommendations for user {user_id}.

Steps:
1. Get user preferences
2. Search for jobs matching their preferences on all platforms
3. Calculate match scores for all jobs
4. Research top companies
5. Return top {limit} recommendations ranked by match score

Provide detailed reasoning for each recommendation."""

        return await self.run(query)


def create_job_hunter_agent(db_manager: DatabaseManager) -> JobHunterAgent:
    """
    Factory function to create a Job Hunter Agent instance.

    Args:
        db_manager: Database manager instance

    Returns:
        Configured JobHunterAgent instance
    """
    return JobHunterAgent(db_manager=db_manager)
