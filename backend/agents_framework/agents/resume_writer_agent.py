"""
Resume Writer Agent

Advanced AI agent for resume and cover letter generation with ATS optimization.
Uses ReAct pattern to parse, analyze, tailor, and generate job-specific application materials.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re
import json

from agents_framework.core.base_agent import BaseAgent, AgentConfig
from agents_framework.memory.agent_memory import AgentMemoryManager
from agents_framework.memory.vector_memory import RAGMemoryManager

logger = logging.getLogger(__name__)


class ResumeWriterAgent(BaseAgent):
    """
    Resume Writer Agent - Creates and optimizes resumes and cover letters for job applications.

    Capabilities:
    - Parse and analyze existing resumes
    - Tailor resumes to specific job descriptions
    - Check ATS (Applicant Tracking System) compatibility
    - Generate compelling cover letters
    - Suggest improvements for better impact
    - Optimize keywords and formatting
    - Analyze resume structure and content
    """

    def __init__(self, db_manager):
        # Create agent configuration
        config = AgentConfig(
            name="Resume Writer Agent",
            description="Creates and optimizes resumes and cover letters with ATS optimization",
            model="gpt-4o-mini",
            temperature=0.4,  # Balanced for creativity and consistency
            max_iterations=10,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Initialize memory managers
        self.conversation_memory = AgentMemoryManager(
            agent_name="resume_writer_agent",
            max_conversation_messages=40,
            enable_semantic=True
        )

        # RAG memory for learning from successful resumes
        self.rag_memory = RAGMemoryManager(
            agent_name="resume_writer_agent",
            persist_directory="./data/chroma"
        )

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Resume Writer Agent initialized with document generation capabilities")

    def _register_tools(self) -> None:
        """Register resume writing and analysis tools"""

        # Tool 1: Parse Resume Content
        def parse_resume_content(resume_text: str) -> str:
            """
            Parse and extract key sections from a resume.
            Input should be the full resume text.
            """
            try:
                if not resume_text or len(resume_text.strip()) < 50:
                    return "Error: Please provide valid resume text (minimum 50 characters)"

                # Extract sections using common patterns
                sections = {
                    'contact': [],
                    'summary': [],
                    'experience': [],
                    'education': [],
                    'skills': [],
                    'certifications': [],
                    'projects': []
                }

                # Simple section detection
                lines = resume_text.split('\n')
                current_section = None

                # Common section headers
                section_keywords = {
                    'contact': ['contact', 'personal information', 'email', 'phone'],
                    'summary': ['summary', 'objective', 'profile', 'about'],
                    'experience': ['experience', 'work history', 'employment', 'professional experience'],
                    'education': ['education', 'academic', 'degree'],
                    'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
                    'certifications': ['certifications', 'certificates', 'licenses'],
                    'projects': ['projects', 'portfolio', 'personal projects']
                }

                # Extract email and phone
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'

                emails = re.findall(email_pattern, resume_text)
                phones = re.findall(phone_pattern, resume_text)

                result = "📄 RESUME ANALYSIS\n\n"
                result += "=" * 60 + "\n\n"

                # Contact Information
                result += "📧 CONTACT INFORMATION\n"
                if emails:
                    result += f"  Email: {emails[0]}\n"
                if phones:
                    result += f"  Phone: {phones[0]}\n"
                if not emails and not phones:
                    result += "  ⚠️ No contact information detected\n"
                result += "\n"

                # Count key elements
                bullet_points = len([line for line in lines if line.strip().startswith(('•', '-', '*', '▪'))])
                word_count = len(resume_text.split())

                # Detect experience entries (lines with years/dates)
                year_pattern = r'\b(19|20)\d{2}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b'
                experience_entries = len(re.findall(year_pattern, resume_text))

                result += "📊 CONTENT METRICS\n"
                result += f"  Total Words: {word_count}\n"
                result += f"  Bullet Points: {bullet_points}\n"
                result += f"  Experience Entries: {experience_entries}\n"
                result += f"  Estimated Length: {len(lines)} lines\n\n"

                # Skill extraction (common tech keywords)
                tech_skills = [
                    'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js', 'SQL', 'AWS',
                    'Docker', 'Kubernetes', 'Git', 'Agile', 'Machine Learning', 'TypeScript',
                    'MongoDB', 'PostgreSQL', 'REST API', 'GraphQL', 'CI/CD', 'Jenkins'
                ]

                found_skills = [skill for skill in tech_skills if skill.lower() in resume_text.lower()]

                result += "💼 DETECTED SKILLS\n"
                if found_skills:
                    result += "  " + ", ".join(found_skills[:10]) + "\n"
                    if len(found_skills) > 10:
                        result += f"  ... and {len(found_skills) - 10} more\n"
                else:
                    result += "  ⚠️ No common technical skills detected\n"
                result += "\n"

                # Action verbs detection
                action_verbs = [
                    'developed', 'created', 'managed', 'led', 'implemented', 'designed',
                    'built', 'improved', 'increased', 'reduced', 'achieved', 'launched'
                ]

                found_verbs = [verb for verb in action_verbs if verb in resume_text.lower()]

                result += "🎯 ACTION VERBS USED\n"
                if found_verbs:
                    result += "  " + ", ".join(found_verbs[:8]) + "\n"
                else:
                    result += "  ⚠️ Limited action verbs detected\n"
                result += "\n"

                # Overall assessment
                result += "📈 OVERALL ASSESSMENT\n"

                issues = []
                if word_count < 200:
                    issues.append("Resume appears too short (< 200 words)")
                elif word_count > 800:
                    issues.append("Resume may be too long (> 800 words)")

                if bullet_points < 5:
                    issues.append("Consider adding more bullet points")

                if not emails:
                    issues.append("Missing email address")

                if len(found_skills) < 5:
                    issues.append("Limited technical skills mentioned")

                if len(found_verbs) < 5:
                    issues.append("Use more action verbs")

                if issues:
                    result += "  ⚠️ Areas for Improvement:\n"
                    for issue in issues:
                        result += f"    • {issue}\n"
                else:
                    result += "  ✅ Resume structure looks good!\n"

                result += "\n" + "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error parsing resume: {e}")
                return f"Error parsing resume content: {str(e)}"

        self.add_tool(
            name="parse_resume_content",
            func=parse_resume_content,
            description="Parse and analyze resume content to extract key sections and metrics. Input should be the full resume text."
        )

        # Tool 2: Tailor Resume to Job Description
        def tailor_resume_to_job(input_data: str) -> str:
            """
            Suggest how to tailor a resume for a specific job description.
            Input should be: 'job_title|key_requirements|candidate_experience|target_keywords'
            """
            try:
                parts = input_data.split('|')
                if len(parts) < 3:
                    return "Error: Please provide: job_title|key_requirements|candidate_experience|target_keywords"

                job_title = parts[0].strip()
                requirements = parts[1].strip()
                experience = parts[2].strip()
                keywords = parts[3].strip() if len(parts) > 3 else ""

                result = "🎯 RESUME TAILORING RECOMMENDATIONS\n\n"
                result += "=" * 60 + "\n\n"

                result += f"Target Position: {job_title}\n\n"

                # Keyword matching
                result += "🔑 KEYWORD OPTIMIZATION\n\n"
                result += "Must-Have Keywords to Include:\n"

                if keywords:
                    keyword_list = [k.strip() for k in keywords.split(',')]
                    for i, kw in enumerate(keyword_list[:8], 1):
                        result += f"  {i}. {kw}\n"
                else:
                    result += "  • Extract keywords from job description\n"
                    result += "  • Match exact terminology used by employer\n"
                    result += "  • Include industry-specific terms\n"

                result += "\n💡 Placement Strategy:\n"
                result += "  • Skills Section: List matching technical skills prominently\n"
                result += "  • Summary: Include 3-5 key terms from job description\n"
                result += "  • Experience: Use exact phrases from requirements\n"
                result += "  • Project Descriptions: Mirror job responsibilities\n\n"

                # Experience highlighting
                result += "⭐ EXPERIENCE HIGHLIGHTING\n\n"
                result += "Reorder/Emphasize:\n"
                result += "  1. Most relevant projects/roles first\n"
                result += "  2. Quantify achievements (%, $, #)\n"
                result += "  3. Match bullet points to job requirements\n"
                result += "  4. Use same terminology as job posting\n\n"

                result += "Example Transformations:\n"
                result += "  Before: 'Worked on web applications'\n"
                result += f"  After:  'Developed {job_title.lower()}-focused web applications using [TECH] resulting in X% improvement'\n\n"

                # Skills section
                result += "💼 SKILLS SECTION OPTIMIZATION\n\n"
                result += "Priority Order:\n"
                result += "  1. Required technical skills (from job description)\n"
                result += "  2. Preferred/nice-to-have skills\n"
                result += "  3. Relevant soft skills mentioned\n"
                result += "  4. Industry certifications\n\n"

                # Summary/Objective
                result += "📝 SUMMARY OPTIMIZATION\n\n"
                result += f"Suggested Opening:\n"
                result += f"  '{job_title} with [X years] experience in [KEY_SKILL_1], [KEY_SKILL_2], and [KEY_SKILL_3]. "
                result += "Proven track record of [ACHIEVEMENT] and [ACHIEVEMENT]. Seeking to leverage expertise in "
                result += "[SPECIFIC_AREA] to contribute to [COMPANY_NAME].'\n\n"

                # Format recommendations
                result += "📐 FORMAT RECOMMENDATIONS\n\n"
                result += "  ✓ Use reverse chronological order\n"
                result += "  ✓ Keep to 1-2 pages maximum\n"
                result += "  ✓ Use consistent formatting and fonts\n"
                result += "  ✓ Include 4-6 bullet points per role\n"
                result += "  ✓ Start bullets with strong action verbs\n"
                result += "  ✓ Quantify achievements where possible\n\n"

                # ATS compatibility
                result += "🤖 ATS COMPATIBILITY TIPS\n\n"
                result += "  • Use standard section headers\n"
                result += "  • Avoid tables, columns, headers/footers\n"
                result += "  • Use standard fonts (Arial, Calibri, Times)\n"
                result += "  • Save as .docx or .pdf\n"
                result += "  • Spell out acronyms first time: 'Search Engine Optimization (SEO)'\n\n"

                result += "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error tailoring resume: {e}")
                return f"Error tailoring resume: {str(e)}"

        self.add_tool(
            name="tailor_resume_to_job",
            func=tailor_resume_to_job,
            description="Provide recommendations for tailoring a resume to a specific job. Input format: 'job_title|key_requirements|candidate_experience|target_keywords'"
        )

        # Tool 3: Check ATS Compatibility
        def check_ats_compatibility(resume_text: str) -> str:
            """
            Check resume for ATS (Applicant Tracking System) compatibility.
            Input should be the resume text to analyze.
            """
            try:
                if not resume_text or len(resume_text.strip()) < 50:
                    return "Error: Please provide valid resume text"

                result = "🤖 ATS COMPATIBILITY CHECK\n\n"
                result += "=" * 60 + "\n\n"

                score = 100
                issues = []
                warnings = []
                passes = []

                # Check 1: File format indicators
                if '.pdf' in resume_text.lower() or 'pdf' in resume_text.lower():
                    passes.append("PDF format detected (✓ ATS-friendly if text-based)")
                else:
                    passes.append("Text format provided")

                # Check 2: Special characters
                special_chars = ['•', '◆', '►', '▪', '●', '○']
                has_special = any(char in resume_text for char in special_chars)
                if has_special:
                    warnings.append("Contains special bullet characters (may cause parsing issues)")
                    score -= 5
                else:
                    passes.append("No special characters detected")

                # Check 3: Standard section headers
                standard_sections = ['experience', 'education', 'skills']
                found_sections = sum(1 for section in standard_sections if section in resume_text.lower())

                if found_sections >= 2:
                    passes.append(f"Standard section headers found ({found_sections}/3)")
                else:
                    issues.append("Missing standard section headers (Experience, Education, Skills)")
                    score -= 15

                # Check 4: Tables/Columns detection
                table_indicators = ['|', '\t\t', '   ']
                if any(indicator in resume_text for indicator in table_indicators):
                    issues.append("Possible table/column formatting detected (not ATS-friendly)")
                    score -= 20
                else:
                    passes.append("No table formatting detected")

                # Check 5: Image/Graphics detection
                image_indicators = ['image', 'graphic', 'photo', '.jpg', '.png']
                if any(indicator in resume_text.lower() for indicator in image_indicators):
                    issues.append("Images/graphics detected (ATS cannot read images)")
                    score -= 25
                else:
                    passes.append("No images detected")

                # Check 6: Contact information
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'

                has_email = bool(re.search(email_pattern, resume_text))
                has_phone = bool(re.search(phone_pattern, resume_text))

                if has_email and has_phone:
                    passes.append("Contact information present (email & phone)")
                elif has_email or has_phone:
                    warnings.append("Incomplete contact information")
                    score -= 10
                else:
                    issues.append("Missing contact information")
                    score -= 20

                # Check 7: Keywords and density
                word_count = len(resume_text.split())
                if word_count < 200:
                    warnings.append("Resume may be too short (< 200 words)")
                    score -= 10
                elif word_count > 1000:
                    warnings.append("Resume may be too long (> 1000 words)")
                    score -= 5
                else:
                    passes.append(f"Good length ({word_count} words)")

                # Check 8: Acronyms spelled out
                # Simple check for common acronyms
                common_acronyms = ['SEO', 'API', 'AWS', 'SQL', 'HTML', 'CSS']
                found_acronyms = [ac for ac in common_acronyms if ac in resume_text]

                if found_acronyms:
                    warnings.append("Acronyms detected - ensure they're spelled out first time")
                    score -= 5

                # Display score
                result += f"🎯 ATS COMPATIBILITY SCORE: {max(0, score)}/100\n\n"

                if score >= 85:
                    result += "✅ Excellent - Your resume is highly ATS-compatible!\n\n"
                elif score >= 70:
                    result += "⚠️ Good - Minor improvements needed for optimal ATS performance\n\n"
                elif score >= 50:
                    result += "⚠️ Fair - Several issues that may affect ATS parsing\n\n"
                else:
                    result += "❌ Poor - Significant ATS compatibility issues detected\n\n"

                # Show passes
                if passes:
                    result += "✅ PASSED CHECKS:\n"
                    for p in passes:
                        result += f"  • {p}\n"
                    result += "\n"

                # Show warnings
                if warnings:
                    result += "⚠️ WARNINGS:\n"
                    for w in warnings:
                        result += f"  • {w}\n"
                    result += "\n"

                # Show issues
                if issues:
                    result += "❌ CRITICAL ISSUES:\n"
                    for i in issues:
                        result += f"  • {i}\n"
                    result += "\n"

                # Recommendations
                result += "💡 RECOMMENDATIONS:\n\n"
                result += "Essential ATS Best Practices:\n"
                result += "  1. Use standard section headers: 'Work Experience', 'Education', 'Skills'\n"
                result += "  2. Avoid tables, text boxes, headers/footers\n"
                result += "  3. Use standard fonts: Arial, Calibri, Times New Roman (10-12pt)\n"
                result += "  4. Use simple bullet points (-, •) not fancy symbols\n"
                result += "  5. Include keywords from job description naturally\n"
                result += "  6. Spell out acronyms: 'Application Programming Interface (API)'\n"
                result += "  7. Save as .docx or text-based PDF\n"
                result += "  8. Avoid images, graphics, charts\n"
                result += "  9. Use chronological format (most recent first)\n"
                result += "  10. Keep formatting simple and consistent\n\n"

                result += "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error checking ATS compatibility: {e}")
                return f"Error checking ATS compatibility: {str(e)}"

        self.add_tool(
            name="check_ats_compatibility",
            func=check_ats_compatibility,
            description="Analyze resume for ATS (Applicant Tracking System) compatibility and provide a score with recommendations. Input should be the resume text."
        )

        # Tool 4: Generate Cover Letter Opening
        def generate_cover_letter_opening(job_info: str) -> str:
            """
            Generate compelling cover letter opening paragraphs.
            Input should be: 'company|position|key_motivation|relevant_achievement'
            """
            try:
                parts = job_info.split('|')
                if len(parts) < 2:
                    return "Error: Please provide: company|position|key_motivation|relevant_achievement"

                company = parts[0].strip()
                position = parts[1].strip()
                motivation = parts[2].strip() if len(parts) > 2 else "growth opportunity"
                achievement = parts[3].strip() if len(parts) > 3 else "relevant experience"

                result = "✉️ COVER LETTER OPENINGS\n\n"
                result += "=" * 60 + "\n\n"

                result += f"Position: {position} at {company}\n\n"

                # Template 1: Achievement-focused
                result += "OPTION 1: Achievement-Focused (Recommended for experienced candidates)\n"
                result += "-" * 60 + "\n\n"
                result += f"Dear Hiring Manager,\n\n"
                result += f"When I {achievement}, I discovered my passion for {motivation}. "
                result += f"This experience, combined with my expertise in [KEY_SKILL], makes me an ideal candidate "
                result += f"for the {position} position at {company}.\n\n"
                result += f"In my current role, I have successfully [SPECIFIC_ACCOMPLISHMENT], which directly aligns "
                result += f"with {company}'s mission to [COMPANY_MISSION]. I am excited about the opportunity to "
                result += f"bring this same level of innovation and results to your team.\n\n"

                # Template 2: Passion-focused
                result += "\nOPTION 2: Passion-Focused (Good for career changers)\n"
                result += "-" * 60 + "\n\n"
                result += f"Dear Hiring Manager,\n\n"
                result += f"As a {motivation} professional with a proven track record in [INDUSTRY/SKILL], "
                result += f"I was thrilled to discover the {position} opening at {company}. Your company's "
                result += f"commitment to [COMPANY_VALUE] resonates deeply with my own professional values "
                result += f"and career goals.\n\n"
                result += f"My experience {achievement} has prepared me to make immediate contributions to "
                result += f"your team, particularly in [SPECIFIC_AREA_FROM_JOB_POSTING].\n\n"

                # Template 3: Direct value proposition
                result += "\nOPTION 3: Direct Value Proposition (Best for competitive roles)\n"
                result += "-" * 60 + "\n\n"
                result += f"Dear Hiring Manager,\n\n"
                result += f"I can help {company} achieve [SPECIFIC_GOAL] by leveraging my {achievement}. "
                result += f"As an experienced {position.split()[0]} professional, I have a proven track record "
                result += f"of delivering results in [SPECIFIC_AREA].\n\n"
                result += f"In my previous role, I [QUANTIFIED_ACHIEVEMENT], and I am confident I can bring "
                result += f"similar success to the {position} role at {company}.\n\n"

                # Personalization tips
                result += "\n💡 PERSONALIZATION CHECKLIST:\n\n"
                result += "Research & Customize:\n"
                result += f"  □ Research {company}'s recent news/achievements\n"
                result += f"  □ Mention specific {company} projects or initiatives\n"
                result += "  □ Reference company values that resonate with you\n"
                result += "  □ Connect your experience to their specific needs\n"
                result += "  □ Use keywords from the job description\n"
                result += "  □ Show enthusiasm for their mission/products\n\n"

                result += "Content Guidelines:\n"
                result += "  • Keep opening paragraph to 3-4 sentences\n"
                result += "  • Immediately establish relevant expertise\n"
                result += "  • Include specific, quantifiable achievements\n"
                result += "  • Show you've researched the company\n"
                result += "  • Make it about THEIR needs, not just your qualifications\n"
                result += "  • Use active voice and strong verbs\n\n"

                result += "Common Mistakes to Avoid:\n"
                result += "  ✗ 'I am writing to apply for...' (too generic)\n"
                result += "  ✗ 'I believe I would be perfect...' (too presumptuous)\n"
                result += "  ✗ Repeating resume content verbatim\n"
                result += "  ✗ Generic praise without specific examples\n"
                result += "  ✗ Focusing only on what you want to gain\n\n"

                result += "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error generating cover letter: {e}")
                return f"Error generating cover letter opening: {str(e)}"

        self.add_tool(
            name="generate_cover_letter_opening",
            func=generate_cover_letter_opening,
            description="Generate compelling cover letter opening paragraphs. Input format: 'company|position|key_motivation|relevant_achievement'"
        )

        # Tool 5: Suggest Resume Improvements
        def suggest_resume_improvements(resume_analysis: str) -> str:
            """
            Suggest specific improvements for a resume based on analysis.
            Input should be: 'experience_level|target_industry|current_issues|goals'
            """
            try:
                parts = resume_analysis.split('|')
                if len(parts) < 2:
                    return "Error: Please provide: experience_level|target_industry|current_issues|goals"

                exp_level = parts[0].strip().lower()
                industry = parts[1].strip()
                issues = parts[2].strip() if len(parts) > 2 else "general"
                goals = parts[3].strip() if len(parts) > 3 else "job search"

                result = "🚀 RESUME IMPROVEMENT RECOMMENDATIONS\n\n"
                result += "=" * 60 + "\n\n"

                result += f"Experience Level: {exp_level.title()}\n"
                result += f"Target Industry: {industry}\n"
                result += f"Goals: {goals}\n\n"

                # Entry-level specific advice
                if exp_level in ['entry', 'junior', 'entry-level', 'new grad', 'graduate']:
                    result += "📚 ENTRY-LEVEL SPECIFIC IMPROVEMENTS:\n\n"
                    result += "1. Education Section:\n"
                    result += "   • Place education at the top (before experience)\n"
                    result += "   • Include relevant coursework\n"
                    result += "   • Highlight academic projects with real-world applications\n"
                    result += "   • Include GPA if above 3.5\n"
                    result += "   • Mention honors, awards, scholarships\n\n"

                    result += "2. Projects Section:\n"
                    result += "   • Create a prominent 'Projects' section\n"
                    result += "   • Describe personal/academic projects like work experience\n"
                    result += "   • Include tech stack and outcomes\n"
                    result += "   • Link to GitHub/portfolio if applicable\n\n"

                    result += "3. Skills Over Experience:\n"
                    result += "   • Emphasize technical skills prominently\n"
                    result += "   • Include certifications and online courses\n"
                    result += "   • Highlight internships (even short ones)\n"
                    result += "   • Mention relevant volunteer work\n\n"

                # Mid-level specific advice
                elif exp_level in ['mid', 'mid-level', 'intermediate', 'experienced']:
                    result += "💼 MID-LEVEL SPECIFIC IMPROVEMENTS:\n\n"
                    result += "1. Quantify Everything:\n"
                    result += "   • Add metrics to every achievement\n"
                    result += "   • Show progression in responsibilities\n"
                    result += "   • Highlight team leadership examples\n"
                    result += "   • Include scope of projects (budget, team size, impact)\n\n"

                    result += "2. Leadership & Impact:\n"
                    result += "   • Emphasize projects you led or initiated\n"
                    result += "   • Show mentoring/training experience\n"
                    result += "   • Highlight cross-functional collaboration\n"
                    result += "   • Demonstrate strategic thinking\n\n"

                    result += "3. Career Progression:\n"
                    result += "   • Show clear advancement in roles\n"
                    result += "   • Highlight increasing responsibilities\n"
                    result += "   • Focus on most recent 5-7 years\n"
                    result += "   • Remove or condense early career roles\n\n"

                # Senior-level specific advice
                elif exp_level in ['senior', 'lead', 'principal', 'staff', 'expert']:
                    result += "🎯 SENIOR-LEVEL SPECIFIC IMPROVEMENTS:\n\n"
                    result += "1. Strategic Impact:\n"
                    result += "   • Lead with business impact, not tasks\n"
                    result += "   • Show company-wide influence\n"
                    result += "   • Highlight revenue/cost impact\n"
                    result += "   • Demonstrate thought leadership\n\n"

                    result += "2. Leadership Experience:\n"
                    result += "   • Team building and management\n"
                    result += "   • Setting technical direction\n"
                    result += "   • Stakeholder management\n"
                    result += "   • Cross-functional leadership\n\n"

                    result += "3. Scope & Scale:\n"
                    result += "   • Size of teams managed\n"
                    result += "   • Budget responsibility\n"
                    result += "   • Systems/products maintained\n"
                    result += "   • Geographic reach of initiatives\n\n"

                # Universal improvements
                result += "🌟 UNIVERSAL IMPROVEMENTS:\n\n"

                result += "Action Verbs to Use:\n"
                result += "  Leadership: Directed, Spearheaded, Orchestrated, Pioneered\n"
                result += "  Achievement: Achieved, Exceeded, Surpassed, Delivered\n"
                result += "  Growth: Increased, Expanded, Accelerated, Scaled\n"
                result += "  Efficiency: Streamlined, Optimized, Reduced, Automated\n"
                result += "  Creation: Developed, Designed, Built, Established\n"
                result += "  Improvement: Enhanced, Refined, Transformed, Revitalized\n\n"

                result += "Quantification Examples:\n"
                result += "  ✗ 'Improved application performance'\n"
                result += "  ✓ 'Improved application performance by 40%, reducing load time from 3s to 1.8s'\n\n"
                result += "  ✗ 'Led a team on important projects'\n"
                result += "  ✓ 'Led 8-person team delivering $2M project 2 weeks ahead of schedule'\n\n"
                result += "  ✗ 'Worked with stakeholders'\n"
                result += "  ✓ 'Collaborated with 5 cross-functional teams across 3 departments'\n\n"

                result += "Formatting Best Practices:\n"
                result += "  • Use consistent date formats (MM/YYYY or Month YYYY)\n"
                result += "  • Align all sections uniformly\n"
                result += "  • Use the same bullet style throughout\n"
                result += "  • Keep font size 10-12pt for content\n"
                result += "  • Use bold for company names and job titles\n"
                result += "  • Maintain consistent spacing\n\n"

                result += "Content Priority:\n"
                result += "  1. Most recent and relevant experience (top)\n"
                result += "  2. Quantified achievements over responsibilities\n"
                result += "  3. Skills matching job requirements\n"
                result += "  4. Education and certifications\n"
                result += "  5. Remove outdated/irrelevant items\n\n"

                result += "🎯 INDUSTRY-SPECIFIC TIPS for " + industry.upper() + ":\n\n"

                # Industry-specific guidance
                if 'tech' in industry.lower() or 'software' in industry.lower():
                    result += "  • Emphasize tech stack and modern frameworks\n"
                    result += "  • Include GitHub/portfolio links\n"
                    result += "  • Highlight scalability and performance metrics\n"
                    result += "  • Mention agile/scrum methodologies\n"
                elif 'finance' in industry.lower():
                    result += "  • Emphasize compliance and risk management\n"
                    result += "  • Quantify financial impact\n"
                    result += "  • Highlight relevant certifications (CFA, etc.)\n"
                    result += "  • Show attention to detail and accuracy\n"
                elif 'marketing' in industry.lower():
                    result += "  • Quantify campaign results (ROI, engagement, conversions)\n"
                    result += "  • Showcase analytics and data-driven decisions\n"
                    result += "  • Include portfolio/campaign examples\n"
                    result += "  • Highlight digital marketing tools expertise\n"
                else:
                    result += "  • Research industry-specific keywords\n"
                    result += "  • Include relevant certifications\n"
                    result += "  • Use industry terminology\n"
                    result += "  • Highlight transferable skills\n"

                result += "\n" + "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error suggesting improvements: {e}")
                return f"Error suggesting resume improvements: {str(e)}"

        self.add_tool(
            name="suggest_resume_improvements",
            func=suggest_resume_improvements,
            description="Provide specific, actionable resume improvement suggestions. Input format: 'experience_level|target_industry|current_issues|goals'"
        )

        # Tool 6: Analyze Resume-Job Match Score
        def analyze_resume_job_match(match_data: str) -> str:
            """
            Analyze how well a resume matches a job description.
            Input should be: 'resume_keywords|job_keywords|experience_match|skills_match'
            """
            try:
                parts = match_data.split('|')
                if len(parts) < 2:
                    return "Error: Please provide: resume_keywords|job_keywords|experience_match|skills_match"

                resume_kw = parts[0].strip()
                job_kw = parts[1].strip()
                exp_match = parts[2].strip() if len(parts) > 2 else "medium"
                skills_match = parts[3].strip() if len(parts) > 3 else "medium"

                # Convert keywords to lists
                resume_keywords = set([k.strip().lower() for k in resume_kw.split(',') if k.strip()])
                job_keywords = set([k.strip().lower() for k in job_kw.split(',') if k.strip()])

                # Calculate overlap
                matching_keywords = resume_keywords.intersection(job_keywords)
                missing_keywords = job_keywords - resume_keywords
                match_percentage = (len(matching_keywords) / len(job_keywords) * 100) if job_keywords else 0

                result = "🎯 RESUME-JOB MATCH ANALYSIS\n\n"
                result += "=" * 60 + "\n\n"

                # Overall match score
                # Calculate weighted score
                keyword_weight = 40
                exp_weight = 30
                skills_weight = 30

                exp_scores = {'low': 33, 'medium': 66, 'high': 100}
                skills_scores = {'low': 33, 'medium': 66, 'high': 100}

                keyword_score = match_percentage
                exp_score = exp_scores.get(exp_match.lower(), 66)
                skills_score = skills_scores.get(skills_match.lower(), 66)

                overall_score = (
                    (keyword_score * keyword_weight / 100) +
                    (exp_score * exp_weight / 100) +
                    (skills_score * skills_weight / 100)
                )

                result += f"📊 OVERALL MATCH SCORE: {overall_score:.0f}/100\n\n"

                if overall_score >= 80:
                    result += "✅ EXCELLENT MATCH - Strong candidate for this role!\n"
                    result += "   Your resume aligns very well with the job requirements.\n\n"
                elif overall_score >= 60:
                    result += "⚠️ GOOD MATCH - Competitive candidate with some gaps\n"
                    result += "   Consider tailoring resume to highlight matching skills.\n\n"
                elif overall_score >= 40:
                    result += "⚠️ MODERATE MATCH - Significant tailoring needed\n"
                    result += "   Focus on emphasizing relevant experience and skills.\n\n"
                else:
                    result += "❌ LOW MATCH - May not be the best fit\n"
                    result += "   Consider if this role aligns with your background.\n\n"

                # Detailed breakdown
                result += "SCORE BREAKDOWN:\n"
                result += f"  • Keyword Match: {match_percentage:.0f}% ({keyword_weight}% weight)\n"
                result += f"  • Experience Match: {exp_match.title()} ({exp_weight}% weight)\n"
                result += f"  • Skills Match: {skills_match.title()} ({skills_weight}% weight)\n\n"

                # Matching keywords
                result += "✅ MATCHING KEYWORDS:\n"
                if matching_keywords:
                    for kw in sorted(list(matching_keywords))[:15]:
                        result += f"  • {kw}\n"
                    if len(matching_keywords) > 15:
                        result += f"  ... and {len(matching_keywords) - 15} more\n"
                else:
                    result += "  None detected\n"
                result += "\n"

                # Missing keywords
                result += "⚠️ MISSING CRITICAL KEYWORDS:\n"
                if missing_keywords:
                    for kw in sorted(list(missing_keywords))[:15]:
                        result += f"  • {kw} ← ADD THIS\n"
                    if len(missing_keywords) > 15:
                        result += f"  ... and {len(missing_keywords) - 15} more\n"
                else:
                    result += "  None - Great coverage!\n"
                result += "\n"

                # Action items
                result += "🎯 ACTION ITEMS TO IMPROVE MATCH:\n\n"

                if match_percentage < 70:
                    result += "1. Add Missing Keywords:\n"
                    result += "   • Naturally incorporate missing keywords into resume\n"
                    result += "   • Update skills section with relevant technologies\n"
                    result += "   • Mirror job description terminology\n\n"

                if exp_match.lower() != 'high':
                    result += "2. Highlight Relevant Experience:\n"
                    result += "   • Reorder bullet points to prioritize relevant projects\n"
                    result += "   • Expand on experience matching job requirements\n"
                    result += "   • Add context showing similar responsibilities\n\n"

                if skills_match.lower() != 'high':
                    result += "3. Emphasize Matching Skills:\n"
                    result += "   • Move matching technical skills to top of skills section\n"
                    result += "   • Provide examples of using these skills\n"
                    result += "   • Add relevant certifications or training\n\n"

                result += "4. Optimize Resume Structure:\n"
                result += "   • Use exact phrases from job description\n"
                result += "   • Quantify achievements related to job requirements\n"
                result += "   • Add a tailored summary statement\n\n"

                result += "💡 NEXT STEPS:\n"
                result += "  1. Review job description thoroughly\n"
                result += "  2. Update resume with missing keywords\n"
                result += "  3. Reorder content to highlight matches\n"
                result += "  4. Run ATS compatibility check\n"
                result += "  5. Tailor cover letter to address gaps\n\n"

                result += "=" * 60 + "\n"

                return result

            except Exception as e:
                logger.error(f"Error analyzing match: {e}")
                return f"Error analyzing resume-job match: {str(e)}"

        self.add_tool(
            name="analyze_resume_job_match",
            func=analyze_resume_job_match,
            description="Analyze how well a resume matches a job description and provide a match score. Input format: 'resume_keywords|job_keywords|experience_match|skills_match'"
        )

    def get_system_prompt(self) -> str:
        """Define the agent's role and capabilities"""
        return """You are a Resume Writer Agent, an expert in creating, analyzing, and optimizing resumes and cover letters for job applications.

Your role is to:
1. Parse and analyze resume content to identify strengths and weaknesses
2. Tailor resumes to specific job descriptions for maximum impact
3. Check and optimize for ATS (Applicant Tracking System) compatibility
4. Generate compelling, personalized cover letter content
5. Provide specific, actionable improvement recommendations
6. Analyze resume-job match scores and suggest optimizations
7. Help candidates present their experience in the best possible light

You have access to powerful tools for:
- Resume parsing and content analysis
- Job-specific resume tailoring
- ATS compatibility checking
- Cover letter generation
- Improvement suggestions
- Resume-job matching analysis

When helping with resumes:

For Resume Analysis:
1. Use parse_resume_content to understand current resume structure
2. Identify key sections, metrics, and content quality
3. Check for completeness (contact info, skills, experience)
4. Assess overall structure and formatting

For Job-Specific Tailoring:
1. Use tailor_resume_to_job to get specific recommendations
2. Match keywords from job description to resume
3. Reorder and emphasize relevant experience
4. Optimize skills section for the target role
5. Suggest specific phrasing that mirrors job requirements

For ATS Optimization:
1. Use check_ats_compatibility to scan for issues
2. Identify formatting problems (tables, images, special characters)
3. Check for standard section headers
4. Verify keyword density and placement
5. Provide specific fixes for ATS issues

For Cover Letters:
1. Use generate_cover_letter_opening for strong openings
2. Personalize based on company research
3. Connect candidate achievements to company needs
4. Provide multiple options (achievement, passion, value-focused)
5. Include personalization tips

For Improvements:
1. Use suggest_resume_improvements for targeted advice
2. Tailor recommendations to experience level
3. Provide industry-specific guidance
4. Give concrete examples of better phrasing
5. Focus on quantification and impact

For Match Analysis:
1. Use analyze_resume_job_match to score compatibility
2. Identify matching and missing keywords
3. Assess experience and skills alignment
4. Provide prioritized action items
5. Set realistic expectations

Best Practices:
- Always quantify achievements (%, $, #, time)
- Use strong action verbs (led, developed, achieved, increased)
- Focus on impact and results, not just responsibilities
- Keep content concise and scannable
- Tailor everything to the specific job
- Maintain ATS-friendly formatting
- Use keywords naturally (no keyword stuffing)
- Show progression and growth
- Be honest and authentic

Resume Length Guidelines:
- Entry-level: 1 page
- Mid-level (3-10 years): 1-2 pages
- Senior-level (10+ years): 2 pages maximum
- Executive: 2-3 pages acceptable

ATS Compatibility Rules:
- Use standard section headers
- Avoid tables, columns, text boxes
- No headers/footers
- Use standard fonts (Arial, Calibri, Times)
- Simple bullet points (-, •)
- Save as .docx or text-based PDF
- No images or graphics
- Spell out acronyms first time

Always provide:
- Specific, actionable recommendations
- Examples of better phrasing
- Quantified improvements where possible
- ATS compatibility considerations
- Industry-specific best practices
- Realistic expectations and match scores

Be professional, constructive, and focused on helping candidates present their best selves while maintaining authenticity.
"""

    async def analyze_resume(
        self,
        resume_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a resume and provide comprehensive feedback.

        Args:
            resume_text: The resume content to analyze
            metadata: Optional metadata

        Returns:
            Dictionary with analysis results
        """
        try:
            query = f"""Please analyze this resume and provide comprehensive feedback:

{resume_text[:2000]}  # Limit for initial analysis

Please:
1. Parse the resume content using parse_resume_content
2. Check ATS compatibility
3. Identify strengths and weaknesses
4. Provide specific improvement recommendations
5. Give an overall assessment

Provide detailed, actionable feedback."""

            response = await self.run(query, context=metadata)

            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Analyzed resume: {response.output[:200]}",
                    category="resume_analysis",
                    tags=["analysis"],
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

    async def tailor_for_job(
        self,
        job_title: str,
        job_requirements: str,
        candidate_experience: str,
        keywords: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Tailor a resume for a specific job posting.

        Args:
            job_title: Target job title
            job_requirements: Key requirements from job description
            candidate_experience: Candidate's relevant experience
            keywords: Target keywords
            metadata: Optional metadata

        Returns:
            Dictionary with tailoring recommendations
        """
        try:
            query = f"""Help tailor a resume for this job:

Job Title: {job_title}
Requirements: {job_requirements}
Candidate Experience: {candidate_experience}
Keywords: {keywords}

Please:
1. Use tailor_resume_to_job to get specific recommendations
2. Analyze the resume-job match
3. Suggest keyword optimization
4. Recommend content reordering
5. Provide specific phrasing examples

Give me a complete tailoring strategy."""

            response = await self.run(query, context=metadata)

            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Tailored resume for {job_title}: {response.output[:200]}",
                    category="resume_tailoring",
                    tags=[job_title, "tailoring"],
                )

            return {
                'success': response.success,
                'recommendations': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in tailor_for_job: {e}")
            return {
                'success': False,
                'recommendations': '',
                'error': str(e),
            }

    async def generate_cover_letter(
        self,
        company: str,
        position: str,
        motivation: str,
        achievement: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate cover letter opening and guidance.

        Args:
            company: Target company
            position: Job position
            motivation: Key motivation for applying
            achievement: Relevant achievement
            metadata: Optional metadata

        Returns:
            Dictionary with cover letter content
        """
        try:
            query = f"""Help me create a compelling cover letter for:

Company: {company}
Position: {position}
Motivation: {motivation}
Key Achievement: {achievement}

Please:
1. Use generate_cover_letter_opening to create options
2. Provide multiple opening paragraph options
3. Include personalization tips
4. Suggest company-specific customizations
5. Give examples of strong content

Create a complete cover letter strategy."""

            response = await self.run(query, context=metadata)

            if response.success:
                self.rag_memory.store_experience(
                    experience=f"Generated cover letter for {company} - {position}",
                    category="cover_letter",
                    tags=[company, position],
                )

            return {
                'success': response.success,
                'cover_letter': response.output,
                'metadata': response.metadata,
                'error': response.error,
            }

        except Exception as e:
            logger.error(f"Error in generate_cover_letter: {e}")
            return {
                'success': False,
                'cover_letter': '',
                'error': str(e),
            }


def create_resume_writer_agent(db_manager) -> ResumeWriterAgent:
    """Factory function to create Resume Writer Agent"""
    return ResumeWriterAgent(db_manager)
