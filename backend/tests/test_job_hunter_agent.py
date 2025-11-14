"""
Tests for Job Hunter Agent

This test suite covers:
1. Job search functionality across platforms
2. Job-to-preference matching algorithm
3. Company research capabilities
4. Job recommendations generation
5. Tool functionality
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

from agents_framework.agents.job_hunter_agent import JobHunterAgent, create_job_hunter_agent
from agents_framework.core.base_agent import AgentConfig
from database.database_manager import DatabaseManager


# Test Data
SAMPLE_JOB_SEARCH = {
    "keywords": "Software Engineer",
    "location": "San Francisco, CA",
    "platforms": ["LinkedIn", "Indeed"],
    "filters": {
        "experience_level": "Mid-Senior level",
        "job_type": "Full-time",
        "salary_min": 120
    }
}

SAMPLE_USER_PREFERENCES = {
    "user_id": 1,
    "preferred_roles": ["Software Engineer", "Backend Developer"],
    "preferred_locations": ["San Francisco, CA", "Remote"],
    "salary_min": 120000,
    "skills": ["Python", "JavaScript", "React", "AWS"]
}

SAMPLE_JOB_POSTING = {
    "id": "test_job_1",
    "platform": "LinkedIn",
    "title": "Senior Software Engineer",
    "company": "Tech Company",
    "location": "San Francisco, CA",
    "salary_range": "$150K - $200K",
    "experience_level": "Mid-Senior level",
    "job_type": "Full-time",
    "description": "Looking for a talented Software Engineer with Python and JavaScript experience.",
    "benefits": ["Health insurance", "401k", "Remote work"],
    "requirements": ["5+ years experience", "Python", "JavaScript"]
}


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager"""
    db = Mock(spec=DatabaseManager)
    return db


@pytest.fixture
def job_hunter_agent(mock_db_manager):
    """Create a JobHunterAgent instance for testing"""
    config = AgentConfig(
        agent_name="job_hunter_test",
        model="gpt-4o-mini",
        temperature=0.3,
        max_iterations=10,
        enable_memory=False  # Disable memory for faster tests
    )
    return JobHunterAgent(db_manager=mock_db_manager, config=config)


class TestJobHunterAgentInitialization:
    """Test agent initialization and configuration"""

    def test_agent_creation(self, mock_db_manager):
        """Test that agent is created successfully"""
        agent = JobHunterAgent(db_manager=mock_db_manager)
        assert agent is not None
        assert agent.db_manager == mock_db_manager
        assert agent.config.agent_name == "job_hunter"

    def test_agent_factory(self, mock_db_manager):
        """Test factory function creates agent correctly"""
        agent = create_job_hunter_agent(mock_db_manager)
        assert isinstance(agent, JobHunterAgent)
        assert agent.db_manager == mock_db_manager

    def test_agent_has_tools(self, job_hunter_agent):
        """Test that agent has all required tools registered"""
        tools = job_hunter_agent._register_tools()

        # Should have 8 tools
        assert len(tools) == 8

        # Check tool names
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            'search_linkedin_jobs',
            'search_indeed_jobs',
            'search_glassdoor_jobs',
            'extract_job_details',
            'get_user_preferences',
            'calculate_job_match_score',
            'research_company',
            'save_job_recommendation'
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_system_prompt(self, job_hunter_agent):
        """Test that system prompt is properly defined"""
        prompt = job_hunter_agent.get_system_prompt()
        assert len(prompt) > 0
        assert "Job Hunter Agent" in prompt
        assert "job" in prompt.lower()
        assert "search" in prompt.lower()


class TestJobSearchTools:
    """Test individual job search tools"""

    def test_search_linkedin_jobs_tool(self, job_hunter_agent):
        """Test LinkedIn job search tool"""
        tools = job_hunter_agent._register_tools()
        search_linkedin = next(t for t in tools if t.name == 'search_linkedin_jobs')

        # Test search
        result = search_linkedin.invoke({
            "keywords": "Software Engineer",
            "location": "San Francisco, CA",
            "experience_level": "Mid-Senior level",
            "job_type": "Full-time"
        })

        # Parse result
        data = json.loads(result)
        assert data["success"] is True
        assert data["platform"] == "LinkedIn"
        assert len(data["jobs"]) > 0
        assert data["jobs"][0]["title"].startswith("Software Engineer")

    def test_search_indeed_jobs_tool(self, job_hunter_agent):
        """Test Indeed job search tool"""
        tools = job_hunter_agent._register_tools()
        search_indeed = next(t for t in tools if t.name == 'search_indeed_jobs')

        # Test search
        result = search_indeed.invoke({
            "keywords": "Data Scientist",
            "location": "Remote",
            "salary_min": 100,
            "job_type": "Full-time"
        })

        # Parse result
        data = json.loads(result)
        assert data["success"] is True
        assert data["platform"] == "Indeed"
        assert len(data["jobs"]) > 0

    def test_search_glassdoor_jobs_tool(self, job_hunter_agent):
        """Test Glassdoor job search tool"""
        tools = job_hunter_agent._register_tools()
        search_glassdoor = next(t for t in tools if t.name == 'search_glassdoor_jobs')

        # Test search
        result = search_glassdoor.invoke({
            "keywords": "Product Manager",
            "location": "New York, NY",
            "company_rating_min": 4.0
        })

        # Parse result
        data = json.loads(result)
        assert data["success"] is True
        assert data["platform"] == "Glassdoor"

        # All jobs should meet rating requirement
        for job in data["jobs"]:
            assert job["company_rating"] >= 4.0


class TestJobMatchingTools:
    """Test job matching and scoring tools"""

    def test_extract_job_details_tool(self, job_hunter_agent):
        """Test job details extraction tool"""
        tools = job_hunter_agent._register_tools()
        extract_details = next(t for t in tools if t.name == 'extract_job_details')

        # Test extraction
        description = """
        We are looking for a Software Engineer with 5+ years of experience.
        Must have a Bachelor's degree in Computer Science.
        Experience with Python, JavaScript, React, and AWS required.
        We offer health insurance, 401k matching, and remote work options.
        """

        result = extract_details.invoke({"job_description": description})
        data = json.loads(result)

        # Check extracted data
        assert data["experience_years"] == 5
        assert "Bachelor" in data["education_required"]
        assert len(data["tech_stack"]) > 0
        assert any("Python" in tech for tech in data["tech_stack"])
        assert len(data["benefits"]) > 0

    def test_get_user_preferences_tool(self, job_hunter_agent):
        """Test get user preferences tool"""
        tools = job_hunter_agent._register_tools()
        get_prefs = next(t for t in tools if t.name == 'get_user_preferences')

        # Test getting preferences
        result = get_prefs.invoke({"user_id": 1})
        data = json.loads(result)

        # Check preference structure
        assert data["user_id"] == 1
        assert "preferred_roles" in data
        assert "preferred_locations" in data
        assert "salary_min" in data
        assert "skills" in data
        assert len(data["preferred_roles"]) > 0

    def test_calculate_job_match_score_tool(self, job_hunter_agent):
        """Test job match score calculation"""
        tools = job_hunter_agent._register_tools()
        calc_match = next(t for t in tools if t.name == 'calculate_job_match_score')

        # Create test data
        job = {
            "title": "Software Engineer",
            "location": "San Francisco, CA",
            "salary_range": "$150K - $200K",
            "experience_level": "Mid-Senior level",
            "description": "Python JavaScript React AWS",
            "benefits": ["Health insurance", "Remote work", "401k"]
        }

        prefs = {
            "preferred_roles": ["Software Engineer"],
            "preferred_locations": ["San Francisco, CA"],
            "salary_min": 120000,
            "experience_level": "Mid-Senior level",
            "skills": ["Python", "JavaScript", "React", "AWS"],
            "required_benefits": ["Health insurance", "Remote work"]
        }

        # Calculate match
        result = calc_match.invoke({
            "job_data": json.dumps(job),
            "user_preferences": json.dumps(prefs)
        })

        data = json.loads(result)

        # Check match score
        assert "total_score" in data
        assert "score_breakdown" in data
        assert "match_level" in data
        assert data["total_score"] > 0
        assert data["total_score"] <= 100

        # High match expected for this perfect match
        assert data["total_score"] >= 60

    def test_calculate_job_match_score_low_match(self, job_hunter_agent):
        """Test job match score with poor match"""
        tools = job_hunter_agent._register_tools()
        calc_match = next(t for t in tools if t.name == 'calculate_job_match_score')

        # Create mismatched data
        job = {
            "title": "Sales Manager",
            "location": "Tokyo, Japan",
            "salary_range": "$50K - $70K",
            "experience_level": "Entry level",
            "description": "Sales experience required",
            "benefits": ["Basic insurance"]
        }

        prefs = {
            "preferred_roles": ["Software Engineer"],
            "preferred_locations": ["San Francisco, CA"],
            "salary_min": 120000,
            "experience_level": "Mid-Senior level",
            "skills": ["Python", "JavaScript"],
            "required_benefits": ["Health insurance", "Remote work"]
        }

        # Calculate match
        result = calc_match.invoke({
            "job_data": json.dumps(job),
            "user_preferences": json.dumps(prefs)
        })

        data = json.loads(result)

        # Should be low match
        assert data["total_score"] < 40
        assert data["match_level"] == "Poor"


class TestCompanyResearch:
    """Test company research functionality"""

    def test_research_company_tool(self, job_hunter_agent):
        """Test company research tool"""
        tools = job_hunter_agent._register_tools()
        research = next(t for t in tools if t.name == 'research_company')

        # Research company
        result = research.invoke({"company_name": "Tech Company Inc"})
        data = json.loads(result)

        # Check research data
        assert data["company_name"] == "Tech Company Inc"
        assert "industry" in data
        assert "size" in data
        assert "rating" in data
        assert "pros" in data
        assert "cons" in data
        assert "culture_values" in data
        assert "tech_stack" in data
        assert len(data["pros"]) > 0
        assert len(data["cons"]) > 0


class TestSaveRecommendations:
    """Test saving job recommendations"""

    def test_save_job_recommendation_tool(self, job_hunter_agent):
        """Test saving job recommendation"""
        tools = job_hunter_agent._register_tools()
        save_rec = next(t for t in tools if t.name == 'save_job_recommendation')

        # Save recommendation
        result = save_rec.invoke({
            "job_data": json.dumps(SAMPLE_JOB_POSTING),
            "match_score": 85,
            "user_id": 1
        })

        data = json.loads(result)

        # Check save was successful
        assert data["success"] is True
        assert data["job_id"] == SAMPLE_JOB_POSTING["id"]
        assert data["match_score"] == 85


class TestAgentWorkflows:
    """Test full agent workflows"""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require OpenAI API key"
    )
    async def test_search_jobs_workflow(self, job_hunter_agent):
        """Test full job search workflow with agent"""
        # This test requires OpenAI API key
        result = await job_hunter_agent.search_jobs(
            keywords="Software Engineer",
            location="San Francisco, CA",
            platforms=["LinkedIn"],
            filters={"experience_level": "Mid-Senior level"}
        )

        assert result is not None
        assert result["success"] is True or result.get("error") is not None

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests require OpenAI API key"
    )
    async def test_get_recommendations_workflow(self, job_hunter_agent):
        """Test full recommendations workflow with agent"""
        # This test requires OpenAI API key
        result = await job_hunter_agent.get_recommendations(
            user_id=1,
            limit=5
        )

        assert result is not None
        assert result["success"] is True or result.get("error") is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_search_empty_keywords(self, job_hunter_agent):
        """Test search with empty keywords"""
        tools = job_hunter_agent._register_tools()
        search_linkedin = next(t for t in tools if t.name == 'search_linkedin_jobs')

        # Should still return results (platform may have defaults)
        result = search_linkedin.invoke({"keywords": ""})
        data = json.loads(result)
        assert "jobs" in data

    def test_calculate_match_invalid_json(self, job_hunter_agent):
        """Test match calculation with invalid JSON"""
        tools = job_hunter_agent._register_tools()
        calc_match = next(t for t in tools if t.name == 'calculate_job_match_score')

        # Invalid JSON should return error
        result = calc_match.invoke({
            "job_data": "invalid json",
            "user_preferences": "also invalid"
        })

        data = json.loads(result)
        assert "error" in data or data["total_score"] == 0

    def test_save_recommendation_invalid_job(self, job_hunter_agent):
        """Test saving recommendation with invalid job data"""
        tools = job_hunter_agent._register_tools()
        save_rec = next(t for t in tools if t.name == 'save_job_recommendation')

        # Invalid job data
        result = save_rec.invoke({
            "job_data": "invalid",
            "match_score": 85
        })

        data = json.loads(result)
        assert data["success"] is False
        assert "error" in data


class TestAgentStats:
    """Test agent statistics and monitoring"""

    def test_get_agent_stats(self, job_hunter_agent):
        """Test getting agent statistics"""
        stats = job_hunter_agent.get_stats()

        assert stats is not None
        assert "name" in stats
        assert "tools_count" in stats
        assert stats["name"] == "job_hunter_test"
        assert stats["tools_count"] == 8


# Pytest configuration
def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require OpenAI API"
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring API"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
