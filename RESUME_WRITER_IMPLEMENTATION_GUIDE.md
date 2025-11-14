# Resume Writer Agent - Implementation Guide

This guide shows exactly how to create the Resume Writer Agent following the established patterns in your codebase.

---

## File Structure to Create

```
backend/agents_framework/agents/
├── resume_writer_agent.py          (Main agent class)

backend/api/routes/
└── agents.py                        (Add Resume Writer endpoints to existing file)

backend/tests/
├── test_resume_writer_agent.py     (Test suite)

frontend/src/components/Agents/ResumeWriter/
├── ResumeWriterDashboard.tsx        (Main dashboard)
├── ResumeInputCard.tsx              (Resume input section)
├── JobDescriptionCard.tsx           (Job description input)
├── ResumeAnalysisCard.tsx           (Analysis results)
├── TailorCard.tsx                   (Tailoring interface)
└── ImprovementSuggestionsCard.tsx   (Suggestions display)
```

---

## Step 1: Create the Agent Class

**File: `backend/agents_framework/agents/resume_writer_agent.py`**

```python
"""
Resume Writer Agent

Advanced AI agent for resume optimization and job-specific tailoring.
Uses ReAct pattern to analyze, improve, and customize resumes.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager
from agents_framework.memory.vector_memory import RAGMemoryManager

logger = logging.getLogger(__name__)


class ResumeWriterAgent(BaseAgent):
    """
    Resume Writer Agent - Analyzes and optimizes resumes with AI.
    
    Capabilities:
    - Parse and extract resume sections
    - Tailor resume to specific job descriptions
    - Check ATS (Applicant Tracking System) compatibility
    - Suggest improvements and optimizations
    - Generate cover letter openings
    - Format and export recommendations
    - Learn from successful resumes
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Resume Writer",
            description="Analyzes, optimizes, and tailors resumes for job applications",
            model="gpt-4o-mini",
            temperature=0.3,  # Moderate - mix of analysis and creativity
            max_iterations=10,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="resume_writer",
            max_conversation_messages=40,
            enable_semantic=True
        )

        # RAG memory for storing successful resume patterns
        self.rag_memory = RAGMemoryManager(
            agent_name="resume_writer",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Resume Writer Agent initialized with optimization capabilities")

    def _register_tools(self) -> None:
        """Register resume analysis and optimization tools"""

        # Tool 1: Parse Resume Structure
        def parse_resume_sections(resume_text: str) -> str:
            """
            Parse and extract structured sections from resume text.
            Input should be the full resume content.
            """
            try:
                # Identify common resume sections
                sections = {
                    'contact': '',
                    'summary': '',
                    'experience': '',
                    'skills': '',
                    'education': '',
                    'certifications': '',
                    'projects': '',
                    'other': ''
                }
                
                text_lower = resume_text.lower()
                
                # Simple pattern matching for sections
                section_keywords = {
                    'contact': ['contact', 'phone', 'email', 'location', 'address'],
                    'summary': ['summary', 'professional summary', 'profile', 'objective'],
                    'experience': ['experience', 'work history', 'employment'],
                    'skills': ['skills', 'technical skills', 'competencies'],
                    'education': ['education', 'degree', 'university', 'school'],
                    'certifications': ['certification', 'license', 'credential'],
                    'projects': ['projects', 'portfolio', 'achievements']
                }
                
                # Find section boundaries
                found_sections = {}
                for section, keywords in section_keywords.items():
                    for keyword in keywords:
                        if keyword in text_lower:
                            found_sections[section] = True
                            break
                
                result = "📄 RESUME STRUCTURE ANALYSIS\n\n"
                result += f"Found {len(found_sections)} sections:\n\n"
                
                for section in found_sections:
                    result += f"✓ {section.replace('_', ' ').title()}\n"
                
                result += "\n📋 SECTION RECOMMENDATIONS:\n"
                missing = [s for s in sections if s not in found_sections]
                if missing:
                    result += f"Missing sections: {', '.join([m.title() for m in missing[:3]])}\n"
                
                result += "\n💡 Consider adding missing sections for completeness.\n"
                
                return result

            except Exception as e:
                logger.error(f"Error parsing resume: {e}")
                return f"Error parsing resume: {str(e)}"

        self.add_tool(
            name="parse_resume_sections",
            func=parse_resume_sections,
            description="Parse and extract structured sections from resume text. Identifies contact, summary, experience, skills, education, certifications, and projects."
        )

        # Tool 2: Tailor Resume to Job
        def tailor_resume_to_job(resume_text: str, job_description: str) -> str:
            """
            Tailor resume content to match a specific job description.
            Input format: Full resume text and job description.
            """
            try:
                result = "🎯 RESUME TAILORING ANALYSIS\n\n"
                
                # Keywords matching
                resume_lower = resume_text.lower()
                job_lower = job_description.lower()
                
                # Extract common keywords (simple approach)
                resume_words = set(resume_lower.split())
                job_words = set(job_lower.split())
                
                matching_words = resume_words & job_words
                missing_skills = job_words - resume_words
                
                # Calculate match percentage
                if job_words:
                    match_percentage = (len(matching_words) / len(job_words)) * 100
                else:
                    match_percentage = 0
                
                result += f"🔍 Keyword Match: {match_percentage:.1f}%\n"
                result += f"   Found {len(matching_words)} matching keywords\n"
                result += f"   Missing {len(missing_skills)} keywords\n\n"
                
                result += "💡 TAILORING RECOMMENDATIONS:\n\n"
                result += "1. Reorder experience bullets to emphasize job-relevant achievements\n"
                result += "2. Add missing keywords naturally throughout your resume\n"
                result += "3. Highlight skills that directly match job requirements\n"
                result += "4. Quantify achievements when possible\n"
                result += "5. Use industry terminology from job description\n\n"
                
                result += "⚠️ CRITICAL KEYWORDS NOT FOUND:\n"
                if missing_skills:
                    for skill in list(missing_skills)[:5]:
                        if len(skill) > 3:  # Skip short words
                            result += f"   - {skill.title()}\n"
                
                return result

            except Exception as e:
                logger.error(f"Error tailoring resume: {e}")
                return f"Error tailoring resume: {str(e)}"

        self.add_tool(
            name="tailor_resume_to_job",
            func=tailor_resume_to_job,
            description="Tailor resume content to match a specific job description by identifying missing keywords and suggesting improvements."
        )

        # Tool 3: Check ATS Compatibility
        def check_ats_compatibility(resume_text: str) -> str:
            """
            Check resume for ATS (Applicant Tracking System) compatibility.
            Input should be the resume content.
            """
            try:
                result = "🤖 ATS COMPATIBILITY ANALYSIS\n\n"
                
                # Check for ATS-unfriendly elements
                issues = []
                text_lower = resume_text.lower()
                
                # Check for common ATS blockers
                if any(marker in text_lower for marker in ['image', 'logo', 'graphic', 'pic']):
                    issues.append(("Images/Graphics", "⚠️ CRITICAL - ATS can't parse images"))
                
                if resume_text.count('[') > 5 or resume_text.count('{') > 5:
                    issues.append(("Special Characters", "⚠️ CRITICAL - Too many special characters"))
                
                # Check for good ATS practices
                positives = []
                if any(marker in resume_text for marker in ['•', '-', '*']):
                    positives.append("✓ Uses standard bullet points")
                
                if '\n' in resume_text:
                    positives.append("✓ Good line breaks for parsing")
                
                word_count = len(resume_text.split())
                if 400 < word_count < 800:
                    positives.append("✓ Appropriate length (400-800 words)")
                else:
                    issues.append(("Length", f"⚠️ Resume is {word_count} words (ideal: 400-800)"))
                
                # Calculate compatibility score
                total_checks = len(issues) + len(positives)
                score = (len(positives) / total_checks * 100) if total_checks > 0 else 50
                
                result += f"📊 ATS Compatibility Score: {score:.0f}%\n\n"
                
                if positives:
                    result += "✅ GOOD PRACTICES:\n"
                    for positive in positives:
                        result += f"   {positive}\n"
                    result += "\n"
                
                if issues:
                    result += "⚠️ ISSUES TO FIX:\n"
                    for issue, details in issues:
                        result += f"   • {details}\n"
                    result += "\n"
                
                result += "💡 ATS TIPS:\n"
                result += "   • Use standard fonts (Arial, Calibri, Times New Roman)\n"
                result += "   • Avoid tables and complex formatting\n"
                result += "   • Use clear section headers\n"
                result += "   • Include relevant keywords naturally\n"
                result += "   • Save as PDF or Word (.docx)\n"
                
                return result

            except Exception as e:
                logger.error(f"Error checking ATS compatibility: {e}")
                return f"Error checking ATS compatibility: {str(e)}"

        self.add_tool(
            name="check_ats_compatibility",
            func=check_ats_compatibility,
            description="Check resume for ATS (Applicant Tracking System) compatibility. Identifies potential parsing issues and provides optimization recommendations."
        )

        # Tool 4: Suggest Improvements
        def suggest_improvements(resume_text: str, focus_area: str = "general") -> str:
            """
            Suggest specific improvements to resume content.
            Input should be resume text and optional focus area (general, impact, keywords, format).
            """
            try:
                result = "💡 RESUME IMPROVEMENT SUGGESTIONS\n\n"
                result += f"Focus Area: {focus_area.title()}\n\n"
                
                if focus_area.lower() in ['general', 'impact']:
                    result += "📈 IMPACT OPTIMIZATION:\n"
                    result += "1. Start each bullet with strong action verbs:\n"
                    result += "   ✗ Responsible for managing project\n"
                    result += "   ✓ Spearheaded project delivering 40% revenue increase\n"
                    result += "2. Quantify every achievement where possible\n"
                    result += "3. Focus on results, not just responsibilities\n"
                    result += "4. Use specific metrics: %, $, time saved, users impacted\n\n"
                
                if focus_area.lower() in ['general', 'keywords']:
                    result += "🔑 KEYWORD OPTIMIZATION:\n"
                    result += "1. Mirror language from job description\n"
                    result += "2. Include technical skills naturally\n"
                    result += "3. Add relevant industry certifications\n"
                    result += "4. Use LinkedIn role titles consistently\n\n"
                
                if focus_area.lower() in ['general', 'format']:
                    result += "📐 FORMAT OPTIMIZATION:\n"
                    result += "1. Limit to one page if less than 5 years experience\n"
                    result += "2. Use consistent date formatting\n"
                    result += "3. Order roles by relevance (not always chronological)\n"
                    result += "4. Maintain 0.5-1 inch margins\n"
                    result += "5. Use 10-12pt readable font\n\n"
                
                result += "⚡ QUICK WINS:\n"
                result += "• Add a professional summary if missing\n"
                result += "• Create skills section matching job requirements\n"
                result += "• Include relevant certifications/awards\n"
                result += "• Add LinkedIn URL or portfolio link\n"
                
                return result

            except Exception as e:
                logger.error(f"Error generating suggestions: {e}")
                return f"Error generating suggestions: {str(e)}"

        self.add_tool(
            name="suggest_improvements",
            func=suggest_improvements,
            description="Suggest specific improvements to resume content. Focus areas: general, impact, keywords, format."
        )

        # Tool 5: Generate Cover Letter Opening
        def generate_cover_letter_opening(company: str, position: str, 
                                         resume_summary: str, tone: str = "professional") -> str:
            """
            Generate compelling cover letter opening based on resume and job context.
            Input: company name, position, brief resume summary, and tone preference.
            """
            try:
                result = "✉️ COVER LETTER OPENING\n\n"
                result += f"Company: {company}\n"
                result += f"Position: {position}\n"
                result += f"Tone: {tone.title()}\n\n"
                result += "--- SUGGESTED OPENING ---\n\n"
                
                if tone.lower() == "enthusiastic":
                    result += f"Dear Hiring Manager,\n\n"
                    result += f"I am excited to apply for the {position} position at {company}. "
                    result += "With my proven track record in [relevant expertise] and passion for [company focus], "
                    result += f"I am confident I can drive significant impact on your team.\n"
                elif tone.lower() == "casual":
                    result += f"Hi [Hiring Manager Name],\n\n"
                    result += f"I came across the {position} opening at {company} and I'm genuinely excited about the opportunity. "
                    result += "Here's why I think we'd be a great fit...\n"
                else:  # professional
                    result += f"Dear Hiring Manager,\n\n"
                    result += f"I am writing to express my strong interest in the {position} position at {company}. "
                    result += "With [X years] of experience in [relevant field] and a demonstrated ability to [key achievement], "
                    result += "I am well-positioned to contribute to your team's success.\n"
                
                result += "\n--- PERSONALIZATION TIPS ---\n\n"
                result += "• Research the company's recent news and mention it\n"
                result += "• Connect your experience directly to their needs\n"
                result += "• Use the hiring manager's name if possible\n"
                result += "• Show enthusiasm for the specific role\n"
                result += "• Keep opening to 2-3 sentences\n"
                
                return result

            except Exception as e:
                logger.error(f"Error generating cover letter: {e}")
                return f"Error generating cover letter: {str(e)}"

        self.add_tool(
            name="generate_cover_letter_opening",
            func=generate_cover_letter_opening,
            description="Generate compelling cover letter opening for a specific job application. Input: company, position, resume summary, tone (professional/casual/enthusiastic)."
        )

        # Tool 6: Compare with Best Practices
        def compare_with_best_practices(resume_section: str, section_type: str = "experience") -> str:
            """
            Compare resume section against industry best practices.
            Input should be the resume section content and section type.
            """
            try:
                result = f"📊 BEST PRACTICES COMPARISON - {section_type.upper()}\n\n"
                
                best_practices = {
                    'experience': {
                        'format': '• Company | Role | Dates',
                        'bullets': '3-5 achievement-focused bullets per role',
                        'metrics': 'Include %, $, time, or scale',
                        'verbs': 'Start with strong action verbs',
                        'example': '✓ Led team of 5 to redesign onboarding, reducing setup time by 60%'
                    },
                    'skills': {
                        'format': 'Organized by category or proficiency',
                        'presentation': 'Keywords relevant to target role',
                        'count': '5-15 key skills',
                        'specificity': 'Include version numbers where relevant',
                        'example': '✓ Python 3.9, Machine Learning (TensorFlow, PyTorch), Data Analysis'
                    },
                    'education': {
                        'format': 'Degree | Institution | Graduation Date',
                        'details': 'GPA if 3.5+, relevant coursework, honors',
                        'relevance': 'Include projects or thesis if relevant',
                        'order': 'Most recent first',
                        'example': '✓ B.S. Computer Science | Stanford University | May 2023 | GPA: 3.8'
                    }
                }
                
                if section_type.lower() in best_practices:
                    practices = best_practices[section_type.lower()]
                    result += "✅ BEST PRACTICES:\n"
                    for key, value in practices.items():
                        result += f"   • {key.title()}: {value}\n"
                else:
                    result += "Standard formatting recommendations:\n"
                    result += "   • Clear section headers\n"
                    result += "   • Consistent date formatting\n"
                    result += "   • Achievement-focused content\n"
                    result += "   • Quantifiable results\n"
                
                result += f"\n💡 To optimize your {section_type} section:\n"
                result += "1. Ensure format matches industry standards\n"
                result += "2. Focus on achievements and impact\n"
                result += "3. Include measurable results\n"
                result += "4. Use consistent formatting\n"
                result += "5. Tailor to job description\n"
                
                return result

            except Exception as e:
                logger.error(f"Error comparing practices: {e}")
                return f"Error comparing practices: {str(e)}"

        self.add_tool(
            name="compare_with_best_practices",
            func=compare_with_best_practices,
            description="Compare resume section against industry best practices. Section types: experience, skills, education."
        )

    def get_system_prompt(self) -> str:
        """Define the agent's role and capabilities"""
        return """You are a Resume Writer Agent, an expert in creating, optimizing, and tailoring resumes for job applications.

Your role is to:
1. Analyze resume structure and content
2. Tailor resumes to specific job descriptions
3. Ensure ATS (Applicant Tracking System) compatibility
4. Suggest improvements and optimizations
5. Generate compelling cover letter openings
6. Compare resumes against industry best practices
7. Provide actionable recommendations

You have access to powerful tools for:
- Resume section parsing and analysis
- Job-specific tailoring
- ATS compatibility checking
- Improvement suggestions (impact, keywords, format)
- Cover letter opening generation
- Best practices comparison

When helping with resume optimization:

For Resume Analysis:
1. Parse the resume structure using parse_resume_sections
2. Identify missing sections and content gaps
3. Assess overall completeness

For Job-Specific Tailoring:
1. Use tailor_resume_to_job to match job requirements
2. Identify keywords and skills to emphasize
3. Suggest content reordering

For ATS Optimization:
1. Use check_ats_compatibility to identify issues
2. Recommend format improvements
3. Suggest font and structure changes

For Content Improvement:
1. Use suggest_improvements for specific areas
2. Recommend stronger action verbs
3. Help quantify achievements

For Cover Letters:
1. Use generate_cover_letter_opening to create compelling starts
2. Match tone to company culture
3. Personalize content

For Best Practices:
1. Use compare_with_best_practices for specific sections
2. Ensure industry standards compliance
3. Improve presentation

Always provide:
- Specific, actionable recommendations
- Examples of good vs. bad formatting
- Quantifiable improvements where possible
- ATS-friendly formatting advice
- Job-match analysis with percentages
- Priority order for improvements

Be thorough but practical. Focus on maximum impact for job application success."""

    async def analyze_resume(
        self,
        resume_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a resume and provide comprehensive insights.
        """
        try:
            query = f"""Analyze this resume comprehensively:

{resume_text}

Please:
1. Parse the resume structure
2. Assess completeness
3. Identify improvement opportunities
4. Check formatting for ATS compatibility
5. Provide top 3 priorities for improvement

Provide detailed, actionable analysis."""

            response = await self.run(query, context=metadata)

            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Analyzed resume: {response.output[:200]}",
                    category="resume_analysis",
                    tags=["analysis", "structure"]
                )

            return {
                'success': response.success,
                'analysis': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in analyze_resume: {e}")
            return {
                'success': False,
                'analysis': '',
                'error': str(e),
            }

    async def tailor_resume(
        self,
        resume_text: str,
        job_description: str,
        company: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tailor a resume to a specific job description.
        """
        try:
            query = f"""Tailor this resume to match the job description:

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Please:
1. Identify keyword matches and gaps
2. Suggest content reordering
3. Recommend section emphasis
4. Provide specific bullet point improvements
5. Calculate match percentage

Provide specific, actionable tailoring recommendations."""

            response = await self.run(query, context=metadata)

            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Tailored resume for {company}: {response.output[:200]}",
                    category="resume_tailoring",
                    tags=[company, "tailoring"]
                )

            return {
                'success': response.success,
                'recommendations': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in tailor_resume: {e}")
            return {
                'success': False,
                'recommendations': '',
                'error': str(e),
            }


def create_resume_writer_agent(db_manager) -> ResumeWriterAgent:
    """Factory function to create Resume Writer Agent"""
    return ResumeWriterAgent(db_manager)
```

---

## Step 2: Add API Routes

**Add to: `backend/api/routes/agents.py`**

```python
# Add these imports at the top
from agents_framework.agents.resume_writer_agent import create_resume_writer_agent

# Add these request/response models
class ResumeAnalysisRequest(BaseModel):
    """Request for resume analysis"""
    resume_text: str = Field(..., description="Full resume content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class ResumeTailorRequest(BaseModel):
    """Request for resume tailoring"""
    resume_text: str = Field(..., description="Full resume content")
    job_description: str = Field(..., description="Job description to tailor to")
    company: str = Field("", description="Company name")
    metadata: Optional[Dict[str, Any]] = Field(None)

class ResumeResponse(BaseModel):
    """Response from resume agent"""
    success: bool
    analysis: Optional[str] = None
    recommendations: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Add these endpoints before the "Future agent endpoints" comment
@router.post("/resume-writer/analyze", response_model=ResumeResponse)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    db: DatabaseManager = Depends(get_db)
):
    """Analyze resume and provide comprehensive optimization recommendations"""
    try:
        logger.info("📄 Resume Writer: Analyzing resume")
        
        agent = create_resume_writer_agent(db)
        result = await agent.analyze_resume(
            resume_text=request.resume_text,
            metadata=request.metadata
        )
        
        logger.info(f"✅ Resume analysis {'successful' if result['success'] else 'failed'}")
        return ResumeResponse(**result)
        
    except Exception as e:
        logger.error(f"❌ Error in resume analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")

@router.post("/resume-writer/tailor", response_model=ResumeResponse)
async def tailor_resume(
    request: ResumeTailorRequest,
    db: DatabaseManager = Depends(get_db)
):
    """Tailor resume to specific job description"""
    try:
        logger.info(f"✂️ Resume Writer: Tailoring resume for {request.company}")
        
        agent = create_resume_writer_agent(db)
        result = await agent.tailor_resume(
            resume_text=request.resume_text,
            job_description=request.job_description,
            company=request.company,
            metadata=request.metadata
        )
        
        logger.info(f"✅ Resume tailoring {'successful' if result['success'] else 'failed'}")
        
        return ResumeResponse(
            success=result['success'],
            recommendations=result.get('recommendations', ''),
            metadata=result.get('metadata'),
            error=result.get('error')
        )
        
    except Exception as e:
        logger.error(f"❌ Error in resume tailoring: {e}")
        raise HTTPException(status_code=500, detail=f"Error tailoring resume: {str(e)}")

@router.get("/resume-writer/stats", response_model=AgentStatsResponse)
async def get_resume_writer_stats(db: DatabaseManager = Depends(get_db)):
    """Get Resume Writer Agent statistics"""
    try:
        logger.info("📊 Resume Writer: Getting agent statistics")
        
        agent = create_resume_writer_agent(db)
        stats = agent.get_stats()
        
        return AgentStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"❌ Error getting agent stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
```

---

## Step 3: Create Tests

**File: `backend/tests/test_resume_writer_agent.py`**

```python
"""Test suite for Resume Writer Agent"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager
from agents_framework.agents.resume_writer_agent import create_resume_writer_agent

SAMPLE_RESUME = """
JOHN DOE
john.doe@email.com | (555) 123-4567 | LinkedIn.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced Software Engineer with 5+ years building scalable web applications.

EXPERIENCE
Senior Software Engineer | Tech Corp | 2021 - Present
- Led development of microservices architecture handling 1M+ daily users
- Mentored team of 4 junior developers

Software Engineer | StartUp Inc | 2018 - 2021
- Built React frontend for mobile application
- Implemented PostgreSQL database optimization

SKILLS
Python, JavaScript, React, PostgreSQL, AWS, Docker

EDUCATION
B.S. Computer Science | State University | 2018
"""

SAMPLE_JOB_DESC = """
Senior Backend Engineer | TechCorp

Requirements:
- 5+ years backend development experience
- Python proficiency
- Microservices architecture experience
- AWS expertise
- Team leadership experience
- PostgreSQL and database optimization
"""

class ResumeWriterTests:
    def __init__(self):
        self.db = DatabaseManager()
        self.agent = create_resume_writer_agent(self.db)
        self.passed = 0
        self.failed = 0

    def log_test(self, name: str, passed: bool, message: str = ""):
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if message:
            print(f"   {message}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    async def test_resume_analysis(self):
        """Test resume analysis"""
        print("\n🧪 Testing resume analysis...")
        
        result = await self.agent.analyze_resume(SAMPLE_RESUME)
        passed = result['success'] and 'analysis' in result
        
        self.log_test("Resume analysis", passed, f"Success: {result['success']}")

    async def test_resume_tailoring(self):
        """Test resume tailoring to job description"""
        print("\n🧪 Testing resume tailoring...")
        
        result = await self.agent.tailor_resume(
            resume_text=SAMPLE_RESUME,
            job_description=SAMPLE_JOB_DESC,
            company="TechCorp"
        )
        
        passed = result['success'] and 'recommendations' in result
        self.log_test("Resume tailoring", passed, f"Success: {result['success']}")

    async def test_agent_initialization(self):
        """Test agent initializes with required tools"""
        print("\n🧪 Testing agent initialization...")
        
        expected_tools = [
            'parse_resume_sections',
            'tailor_resume_to_job',
            'check_ats_compatibility',
            'suggest_improvements',
            'generate_cover_letter_opening',
            'compare_with_best_practices'
        ]
        
        tool_names = [tool.name for tool in self.agent.tools]
        passed = all(tool in tool_names for tool in expected_tools)
        
        self.log_test(
            "Agent initialization",
            passed,
            f"Tools: {len(self.agent.tools)}/{len(expected_tools)}"
        )

    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Resume Writer Agent Test Suite")
        print("=" * 60)
        
        await self.test_agent_initialization()
        await self.test_resume_analysis()
        await self.test_resume_tailoring()
        
        print("\n" + "=" * 60)
        print(f"✅ Passed: {self.passed} | ❌ Failed: {self.failed}")
        print("=" * 60)
        
        return self.failed == 0

async def main():
    tests = ResumeWriterTests()
    success = await tests.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 4: Create Frontend Components

**File: `frontend/src/components/Agents/ResumeWriter/ResumeWriterDashboard.tsx`**

```typescript
import React, { useState } from 'react';
import ResumeInputCard from './ResumeInputCard';
import JobDescriptionCard from './JobDescriptionCard';
import ResumeAnalysisCard from './ResumeAnalysisCard';
import TailorCard from './TailorCard';

const ResumeWriterDashboard: React.FC = () => {
  const [resume, setResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [tailoringResult, setTailoringResult] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'analyze' | 'tailor'>('analyze');
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    if (!resume) {
      alert('Please paste a resume');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_text: resume }),
      });

      if (!response.ok) throw new Error('Analysis failed');
      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error analyzing resume');
    } finally {
      setLoading(false);
    }
  };

  const handleTailor = async () => {
    if (!resume || !jobDescription) {
      alert('Please provide both resume and job description');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/agents/resume-writer/tailor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: resume,
          job_description: jobDescription,
        }),
      });

      if (!response.ok) throw new Error('Tailoring failed');
      const data = await response.json();
      setTailoringResult(data);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Error tailoring resume');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-4xl">📄</span>
            <h1 className="text-3xl font-bold text-gray-900">Resume Writer Agent</h1>
          </div>
          <p className="text-gray-600">AI-powered resume optimization and job-specific tailoring</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              activeTab === 'analyze'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-200'
            }`}
          >
            📊 Analyze Resume
          </button>
          <button
            onClick={() => setActiveTab('tailor')}
            className={`px-6 py-2 rounded-lg font-medium transition ${
              activeTab === 'tailor'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-700 border border-gray-200'
            }`}
          >
            ✂️ Tailor to Job
          </button>
        </div>

        {/* Content */}
        {activeTab === 'analyze' ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ResumeInputCard resume={resume} setResume={setResume} onAnalyze={handleAnalyze} loading={loading} />
            {analysisResult && <ResumeAnalysisCard data={analysisResult} />}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <ResumeInputCard resume={resume} setResume={setResume} onAnalyze={() => {}} loading={false} />
            <JobDescriptionCard jobDescription={jobDescription} setJobDescription={setJobDescription} />
            {tailoringResult && <TailorCard data={tailoringResult} />}
            <button
              onClick={handleTailor}
              disabled={loading}
              className="lg:col-span-3 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400"
            >
              {loading ? 'Tailoring...' : 'Tailor Resume to Job'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeWriterDashboard;
```

---

## Step 5: Update Agent Exports

**Update: `backend/agents_framework/agents/__init__.py`**

```python
"""Specialized AI Agents"""

from agents_framework.agents.email_analyst_agent import (
    EmailAnalystAgent,
    create_email_analyst_agent,
)

from agents_framework.agents.resume_writer_agent import (
    ResumeWriterAgent,
    create_resume_writer_agent,
)

__all__ = [
    "EmailAnalystAgent",
    "create_email_analyst_agent",
    "ResumeWriterAgent",
    "create_resume_writer_agent",
]
```

---

## Implementation Checklist

- [ ] Create `resume_writer_agent.py` with agent class
- [ ] Register 6 tools in `_register_tools()`
- [ ] Implement `get_system_prompt()` method
- [ ] Add `analyze_resume()` public method
- [ ] Add `tailor_resume()` public method
- [ ] Add API routes to `agents.py`
- [ ] Create Pydantic request/response models
- [ ] Create test file with test cases
- [ ] Create frontend dashboard component
- [ ] Create supporting frontend components (input cards, results cards)
- [ ] Update `agents/__init__.py` exports
- [ ] Test locally before deployment

---

## Testing the Resume Writer Agent

```bash
# Run tests
python backend/tests/test_resume_writer_agent.py

# Start backend
cd backend
python main.py

# API will be available at:
# POST http://localhost:8000/api/agents/resume-writer/analyze
# POST http://localhost:8000/api/agents/resume-writer/tailor
# GET http://localhost:8000/api/agents/resume-writer/stats
```

---

## Key Differences from Other Agents

1. **Temperature**: 0.3 (balance between analysis and creativity for suggestions)
2. **Iteration count**: 10 (more iterations for complex resume analysis)
3. **Tool count**: 6 tools (parsing, tailoring, ATS check, improvements, cover letter, best practices)
4. **Memory usage**: Stores resume patterns and successful tailoring strategies
5. **Focus**: Content improvement vs. communication management

