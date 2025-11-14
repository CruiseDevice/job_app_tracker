"""
Manual test script for Job Hunter Agent

This script tests the Job Hunter Agent without requiring pytest.
Run with: python tests/manual_test_job_hunter.py
"""

import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents_framework.agents.job_hunter_agent import create_job_hunter_agent
from database.database_manager import DatabaseManager


def test_tool_registration():
    """Test that all tools are registered correctly"""
    print("=" * 60)
    print("TEST 1: Tool Registration")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)

    tools = agent._register_tools()
    print(f"✓ Agent created successfully")
    print(f"✓ Number of tools registered: {len(tools)}")

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

    tool_names = [tool.name for tool in tools]

    for expected_tool in expected_tools:
        if expected_tool in tool_names:
            print(f"✓ Tool '{expected_tool}' registered")
        else:
            print(f"✗ Tool '{expected_tool}' NOT found")

    print()


def test_linkedin_search():
    """Test LinkedIn job search"""
    print("=" * 60)
    print("TEST 2: LinkedIn Job Search")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    search_tool = next(t for t in tools if t.name == 'search_linkedin_jobs')

    result = search_tool.invoke({
        "keywords": "Software Engineer",
        "location": "San Francisco, CA",
        "experience_level": "Mid-Senior level",
        "job_type": "Full-time"
    })

    data = json.loads(result)

    print(f"✓ Search completed successfully")
    print(f"✓ Platform: {data['platform']}")
    print(f"✓ Total results: {data['total_results']}")
    print(f"✓ First job: {data['jobs'][0]['title']}")
    print()


def test_job_matching():
    """Test job matching algorithm"""
    print("=" * 60)
    print("TEST 3: Job Matching Algorithm")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    calc_match = next(t for t in tools if t.name == 'calculate_job_match_score')

    # Perfect match scenario
    job = {
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "salary_range": "$150K - $200K",
        "experience_level": "Mid-Senior level",
        "description": "Python JavaScript React AWS",
        "benefits": ["Health insurance", "Remote work", "401k"],
        "company_rating": 4.5
    }

    prefs = {
        "preferred_roles": ["Software Engineer"],
        "preferred_locations": ["San Francisco, CA"],
        "salary_min": 120000,
        "experience_level": "Mid-Senior level",
        "skills": ["Python", "JavaScript", "React", "AWS"],
        "required_benefits": ["Health insurance", "Remote work"]
    }

    result = calc_match.invoke({
        "job_data": json.dumps(job),
        "user_preferences": json.dumps(prefs)
    })

    data = json.loads(result)

    print(f"✓ Match score calculated: {data['total_score']}/100")
    print(f"✓ Match level: {data['match_level']}")
    print(f"✓ Recommendation: {data['recommendation']}")
    print("\nScore Breakdown:")
    for category, score in data['score_breakdown'].items():
        print(f"  - {category}: {score}")
    print()


def test_company_research():
    """Test company research"""
    print("=" * 60)
    print("TEST 4: Company Research")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    research_tool = next(t for t in tools if t.name == 'research_company')

    result = research_tool.invoke({"company_name": "Tech Innovations Inc"})
    data = json.loads(result)

    print(f"✓ Company research completed")
    print(f"✓ Company: {data['company_name']}")
    print(f"✓ Industry: {data['industry']}")
    print(f"✓ Rating: {data['rating']}/5.0")
    print(f"✓ Size: {data['size']}")
    print(f"✓ Total reviews: {data['total_reviews']}")
    print(f"✓ Number of pros: {len(data['pros'])}")
    print(f"✓ Number of cons: {len(data['cons'])}")
    print()


def test_user_preferences():
    """Test getting user preferences"""
    print("=" * 60)
    print("TEST 5: User Preferences")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    prefs_tool = next(t for t in tools if t.name == 'get_user_preferences')

    result = prefs_tool.invoke({"user_id": 1})
    data = json.loads(result)

    print(f"✓ User preferences retrieved")
    print(f"✓ User ID: {data['user_id']}")
    print(f"✓ Preferred roles: {', '.join(data['preferred_roles'])}")
    print(f"✓ Preferred locations: {', '.join(data['preferred_locations'])}")
    print(f"✓ Salary range: ${data['salary_min']:,} - ${data['salary_max']:,}")
    print(f"✓ Skills: {', '.join(data['skills'])}")
    print()


def test_extract_job_details():
    """Test job details extraction"""
    print("=" * 60)
    print("TEST 6: Job Details Extraction")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    extract_tool = next(t for t in tools if t.name == 'extract_job_details')

    description = """
    We are looking for a Senior Software Engineer with 5+ years of experience.
    Must have a Bachelor's degree in Computer Science.
    Strong experience with Python, JavaScript, React, Node.js, AWS, and Docker required.
    We offer comprehensive health insurance, 401k matching, generous PTO, and remote work options.
    """

    result = extract_tool.invoke({"job_description": description})
    data = json.loads(result)

    print(f"✓ Job details extracted")
    print(f"✓ Experience required: {data['experience_years']} years")
    print(f"✓ Education: {data['education_required']}")
    print(f"✓ Tech stack: {', '.join(data['tech_stack']) if data['tech_stack'] else 'None detected'}")
    print(f"✓ Benefits: {', '.join(data['benefits']) if data['benefits'] else 'None detected'}")
    print()


def test_save_recommendation():
    """Test saving job recommendation"""
    print("=" * 60)
    print("TEST 7: Save Job Recommendation")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)
    tools = agent._register_tools()

    save_tool = next(t for t in tools if t.name == 'save_job_recommendation')

    job = {
        "id": "test_job_123",
        "title": "Senior Software Engineer",
        "company": "Tech Company",
        "location": "San Francisco, CA"
    }

    result = save_tool.invoke({
        "job_data": json.dumps(job),
        "match_score": 85,
        "user_id": 1
    })

    data = json.loads(result)

    print(f"✓ Recommendation saved: {data['success']}")
    print(f"✓ Job ID: {data['job_id']}")
    print(f"✓ Match score: {data['match_score']}")
    print(f"✓ Message: {data['message']}")
    print()


def test_agent_stats():
    """Test agent statistics"""
    print("=" * 60)
    print("TEST 8: Agent Statistics")
    print("=" * 60)

    db = DatabaseManager()
    agent = create_job_hunter_agent(db)

    stats = agent.get_stats()

    print(f"✓ Agent name: {stats['name']}")
    print(f"✓ Tools count: {stats['tools_count']}")
    print(f"✓ Memory size: {stats['memory_size']}")
    print(f"✓ Execution count: {stats['execution_count']}")
    print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "JOB HUNTER AGENT - MANUAL TESTS" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    tests = [
        test_tool_registration,
        test_linkedin_search,
        test_job_matching,
        test_company_research,
        test_user_preferences,
        test_extract_job_details,
        test_save_recommendation,
        test_agent_stats
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ TEST FAILED: {e}")
            print()

    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"✗ Failed: {failed}/{len(tests)}")
    print()

    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check output above for details.")

    print()


if __name__ == "__main__":
    main()
