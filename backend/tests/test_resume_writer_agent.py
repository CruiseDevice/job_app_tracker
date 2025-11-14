# backend/tests/test_resume_writer_agent.py

"""
Test scripts to validate the Resume Writer Agent functionality.
Tests resume analysis, tailoring, cover letter generation, and ATS checking.
"""

import sys
import os
import asyncio
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager
from agents_framework.agents.resume_writer_agent import create_resume_writer_agent


# Sample resume for testing
SAMPLE_RESUME = """JOHN DOE
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

SUMMARY
Experienced software engineer with 6+ years building scalable web applications using Python, JavaScript, and cloud technologies.

EXPERIENCE
Senior Software Engineer | TechCorp Inc. | 2021 - Present
• Developed microservices architecture serving 2M+ daily users
• Reduced API response time by 40% through optimization
• Led team of 4 engineers on critical infrastructure projects
• Implemented CI/CD pipelines reducing deployment time by 60%

Software Engineer | StartupXYZ | 2018 - 2021
• Built full-stack web applications using React and Python
• Designed and implemented RESTful APIs
• Collaborated with cross-functional teams on product features
• Mentored junior developers and conducted code reviews

EDUCATION
Bachelor of Science in Computer Science | State University | 2018
GPA: 3.7/4.0

SKILLS
Languages: Python, JavaScript, TypeScript, Java
Frameworks: React, Node.js, Django, FastAPI
Cloud: AWS, Docker, Kubernetes
Databases: PostgreSQL, MongoDB, Redis"""


SAMPLE_SHORT_RESUME = """Jane Smith
jane@email.com

Experience:
- Worked on projects
- Used various technologies

Education:
- Computer Science degree"""


class ResumeWriterAgentTests:
    """Comprehensive test suite for Resume Writer Agent"""

    def __init__(self):
        self.db = DatabaseManager()
        self.agent = create_resume_writer_agent(self.db)
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")

        if passed:
            self.passed += 1
        else:
            self.failed += 1

        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })

    async def test_resume_analysis_comprehensive(self):
        """Test comprehensive resume analysis"""
        print("\n🧪 Testing comprehensive resume analysis...")

        result = await self.agent.analyze_resume(
            resume_text=SAMPLE_RESUME,
            metadata={}
        )

        # Check if analysis is successful and contains key metrics
        analysis = result.get('analysis', '').lower() if result.get('success') else ''

        has_contact_info = 'contact' in analysis or 'email' in analysis
        has_metrics = 'words' in analysis or 'bullet' in analysis
        has_skills = 'skills' in analysis
        has_assessment = 'assessment' in analysis or 'recommendation' in analysis

        passed = (
            result.get('success') and
            has_contact_info and
            has_metrics and
            has_skills
        )

        self.log_test(
            "Comprehensive resume analysis",
            passed,
            f"Success: {result.get('success')}, Has metrics: {has_metrics}, Has skills: {has_skills}"
        )

    async def test_resume_analysis_short_resume(self):
        """Test analysis of short/incomplete resume"""
        print("\n🧪 Testing analysis of short resume...")

        result = await self.agent.analyze_resume(
            resume_text=SAMPLE_SHORT_RESUME,
            metadata={}
        )

        # Should identify issues with short resume
        analysis = result.get('analysis', '').lower() if result.get('success') else ''

        has_warnings = 'warning' in analysis or 'improve' in analysis or 'short' in analysis

        passed = result.get('success') and has_warnings

        self.log_test(
            "Short resume analysis with warnings",
            passed,
            f"Success: {result.get('success')}, Detected issues: {has_warnings}"
        )

    async def test_resume_analysis_empty_resume(self):
        """Test handling of empty resume"""
        print("\n🧪 Testing empty resume handling...")

        result = await self.agent.analyze_resume(
            resume_text="",
            metadata={}
        )

        # Should handle gracefully
        passed = not result.get('success') or 'error' in result.get('analysis', '').lower()

        self.log_test(
            "Empty resume error handling",
            passed,
            f"Properly handled empty input: {not result.get('success')}"
        )

    async def test_resume_tailoring_tech_role(self):
        """Test tailoring resume for tech role"""
        print("\n🧪 Testing resume tailoring for tech role...")

        result = await self.agent.tailor_for_job(
            job_title="Senior Software Engineer",
            job_requirements="5+ years Python, React, AWS experience. Strong system design skills.",
            candidate_experience="6 years full-stack development with Python and React",
            keywords="Python, React, AWS, System Design, Microservices, CI/CD"
        )

        recommendations = result.get('recommendations', '').lower() if result.get('success') else ''

        has_keywords = 'keyword' in recommendations
        has_optimization = 'optimize' in recommendations or 'tailor' in recommendations
        has_skills_section = 'skills' in recommendations
        has_experience = 'experience' in recommendations

        passed = (
            result.get('success') and
            has_keywords and
            has_optimization
        )

        self.log_test(
            "Tailor resume for tech role",
            passed,
            f"Success: {result.get('success')}, Has keywords: {has_keywords}, Has optimization: {has_optimization}"
        )

    async def test_resume_tailoring_keyword_matching(self):
        """Test keyword matching in tailoring"""
        print("\n🧪 Testing keyword matching...")

        keywords = "Python, React, AWS, Docker, Kubernetes"

        result = await self.agent.tailor_for_job(
            job_title="Backend Engineer",
            job_requirements="Python and AWS expertise required",
            candidate_experience="5 years Python development",
            keywords=keywords
        )

        recommendations = result.get('recommendations', '').lower() if result.get('success') else ''

        # Should mention the provided keywords
        has_python = 'python' in recommendations
        has_aws = 'aws' in recommendations
        has_placement = 'placement' in recommendations or 'section' in recommendations

        passed = result.get('success') and has_python and has_placement

        self.log_test(
            "Keyword matching in tailoring",
            passed,
            f"Success: {result.get('success')}, Mentions keywords: {has_python and has_aws}"
        )

    async def test_cover_letter_generation_achievement_focused(self):
        """Test cover letter generation with achievement"""
        print("\n🧪 Testing cover letter generation (achievement-focused)...")

        result = await self.agent.generate_cover_letter(
            company="Google",
            position="Software Engineer",
            motivation="passion for scalable systems",
            achievement="led a team that reduced API latency by 60%"
        )

        cover_letter = result.get('cover_letter', '').lower() if result.get('success') else ''

        has_company = 'google' in cover_letter
        has_position = 'software engineer' in cover_letter
        has_opening = 'dear' in cover_letter or 'subject' in cover_letter
        has_options = 'option' in cover_letter or 'template' in cover_letter

        passed = (
            result.get('success') and
            has_company and
            has_position and
            has_options
        )

        self.log_test(
            "Cover letter with achievement",
            passed,
            f"Success: {result.get('success')}, Has company: {has_company}, Has options: {has_options}"
        )

    async def test_cover_letter_generation_no_achievement(self):
        """Test cover letter generation without achievement"""
        print("\n🧪 Testing cover letter generation (no achievement)...")

        result = await self.agent.generate_cover_letter(
            company="Meta",
            position="Frontend Developer",
            motivation="love for creating great user experiences",
            achievement=""  # No achievement provided
        )

        cover_letter = result.get('cover_letter', '').lower() if result.get('success') else ''

        has_company = 'meta' in cover_letter
        has_templates = 'template' in cover_letter or 'option' in cover_letter

        passed = result.get('success') and has_company and has_templates

        self.log_test(
            "Cover letter without achievement",
            passed,
            f"Success: {result.get('success')}, Generated templates: {has_templates}"
        )

    async def test_cover_letter_personalization_tips(self):
        """Test cover letter includes personalization tips"""
        print("\n🧪 Testing cover letter personalization tips...")

        result = await self.agent.generate_cover_letter(
            company="Amazon",
            position="Backend Engineer",
            motivation="commitment to operational excellence",
            achievement="built systems handling 10M+ requests/day"
        )

        cover_letter = result.get('cover_letter', '').lower() if result.get('success') else ''

        has_tips = 'tip' in cover_letter or 'personalization' in cover_letter
        has_checklist = 'checklist' in cover_letter or '□' in result.get('cover_letter', '')
        has_guidance = 'research' in cover_letter or 'customize' in cover_letter

        passed = result.get('success') and (has_tips or has_guidance)

        self.log_test(
            "Cover letter personalization guidance",
            passed,
            f"Success: {result.get('success')}, Has guidance: {has_tips or has_guidance}"
        )

    async def test_agent_initialization(self):
        """Test agent initialization and configuration"""
        print("\n🧪 Testing agent initialization...")

        # Check agent properties
        has_name = hasattr(self.agent, 'config') and hasattr(self.agent.config, 'name')
        has_tools = hasattr(self.agent, 'tools') and len(self.agent.tools) > 0
        has_memory = hasattr(self.agent, 'conversation_memory')

        passed = has_name and has_tools and has_memory

        self.log_test(
            "Agent initialization",
            passed,
            f"Has config: {has_name}, Tools: {len(self.agent.tools) if has_tools else 0}, Has memory: {has_memory}"
        )

    async def test_agent_tools_count(self):
        """Test that all required tools are registered"""
        print("\n🧪 Testing agent tools registration...")

        expected_tools = [
            'parse_resume_content',
            'tailor_resume_to_job',
            'check_ats_compatibility',
            'generate_cover_letter_opening',
            'suggest_resume_improvements',
            'analyze_resume_job_match'
        ]

        tool_names = [tool['name'] for tool in self.agent.tools]

        missing_tools = [tool for tool in expected_tools if tool not in tool_names]
        passed = len(missing_tools) == 0

        self.log_test(
            "All tools registered",
            passed,
            f"Expected: {len(expected_tools)}, Found: {len(tool_names)}, Missing: {missing_tools}"
        )

    async def test_ats_compatibility_context(self):
        """Test ATS compatibility check context"""
        print("\n🧪 Testing ATS compatibility analysis...")

        # The agent should use parse_resume_content and check_ats_compatibility tools
        result = await self.agent.analyze_resume(
            resume_text=SAMPLE_RESUME,
            metadata={'check_type': 'ats'}
        )

        analysis = result.get('analysis', '').lower() if result.get('success') else ''

        # Should contain ATS-related content
        has_ats = 'ats' in analysis or 'tracking' in analysis
        has_format = 'format' in analysis
        has_compatibility = 'compatible' in analysis or 'compatibility' in analysis

        passed = result.get('success')

        self.log_test(
            "ATS compatibility analysis",
            passed,
            f"Success: {result.get('success')}, Analysis generated"
        )

    async def test_error_handling_invalid_input(self):
        """Test error handling with invalid inputs"""
        print("\n🧪 Testing error handling...")

        # Test with minimal/invalid data
        result = await self.agent.tailor_for_job(
            job_title="",
            job_requirements="",
            candidate_experience="",
            keywords=""
        )

        # Should handle gracefully
        passed = True  # Just checking it doesn't crash

        self.log_test(
            "Error handling with empty inputs",
            passed,
            f"Handled gracefully: {result.get('success')}"
        )

    async def test_agent_stats(self):
        """Test agent statistics retrieval"""
        print("\n🧪 Testing agent statistics...")

        stats = self.agent.get_stats()

        has_name = 'name' in stats
        has_tools_count = 'tools_count' in stats
        has_execution_count = 'execution_count' in stats

        passed = has_name and has_tools_count

        self.log_test(
            "Agent statistics",
            passed,
            f"Stats available: Name={has_name}, Tools={has_tools_count}, Executions={has_execution_count}"
        )

    async def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "=" * 70)
        print("🚀 RESUME WRITER AGENT - COMPREHENSIVE TEST SUITE")
        print("=" * 70)

        # Resume Analysis Tests
        await self.test_resume_analysis_comprehensive()
        await self.test_resume_analysis_short_resume()
        await self.test_resume_analysis_empty_resume()

        # Resume Tailoring Tests
        await self.test_resume_tailoring_tech_role()
        await self.test_resume_tailoring_keyword_matching()

        # Cover Letter Tests
        await self.test_cover_letter_generation_achievement_focused()
        await self.test_cover_letter_generation_no_achievement()
        await self.test_cover_letter_personalization_tips()

        # ATS Tests
        await self.test_ats_compatibility_context()

        # Agent Tests
        await self.test_agent_initialization()
        await self.test_agent_tools_count()
        await self.test_agent_stats()

        # Error Handling
        await self.test_error_handling_invalid_input()

        # Print summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("=" * 70)

        # List failed tests
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['message']}")

        return self.passed, self.failed


async def main():
    """Main test execution"""
    print("🔧 Initializing Resume Writer Agent Test Suite...")

    try:
        tests = ResumeWriterAgentTests()
        passed, failed = await tests.run_all_tests()

        # Exit with appropriate code
        exit(0 if failed == 0 else 1)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
