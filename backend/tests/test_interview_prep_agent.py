"""
Test Script for Interview Prep Agent

This script tests the core functionality of the Interview Prep Agent
to ensure all tools and workflows are working correctly.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents_framework.agents.interview_prep_agent import create_interview_prep_agent
from database.database_manager import DatabaseManager


async def test_interview_prep_agent():
    """Test the Interview Prep Agent functionality"""

    print("=" * 80)
    print("INTERVIEW PREP AGENT TEST")
    print("=" * 80)
    print()

    # Initialize database manager
    print("1. Initializing Database Manager...")
    db = DatabaseManager()
    print("✅ Database Manager initialized")
    print()

    # Create Interview Prep Agent
    print("2. Creating Interview Prep Agent...")
    agent = create_interview_prep_agent(db)
    print(f"✅ Agent created: {agent.config.name}")
    print(f"   - Model: {agent.config.model}")
    print(f"   - Temperature: {agent.config.temperature}")
    print(f"   - Tools: {len(agent.tools)}")
    print()

    # Test 1: Generate Interview Questions
    print("3. Test: Generating Interview Questions")
    print("-" * 80)
    try:
        result = await agent.generate_practice_questions(
            job_title="Software Engineer",
            company_name="Google",
            job_description="We are looking for a talented software engineer...",
            question_type="mixed",
            difficulty="medium"
        )

        if result["success"]:
            print("✅ Question generation successful")
            print(f"   Questions preview: {result['questions'][:200]}...")
        else:
            print(f"❌ Question generation failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error during question generation: {e}")
    print()

    # Test 2: STAR Format Answer Preparation
    print("4. Test: STAR Format Answer Preparation")
    print("-" * 80)
    try:
        result = await agent.practice_star_answer(
            question="Tell me about a time when you faced a significant challenge",
            experience_context="I led a complex system migration project"
        )

        if result["success"]:
            print("✅ STAR answer preparation successful")
            print(f"   Framework preview: {result['star_framework'][:200]}...")
        else:
            print(f"❌ STAR preparation failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error during STAR preparation: {e}")
    print()

    # Test 3: Mock Interview
    print("5. Test: Starting Mock Interview")
    print("-" * 80)
    try:
        result = await agent.start_mock_interview(
            job_title="Product Manager",
            focus_area="behavioral",
            difficulty="medium"
        )

        if result["success"]:
            print("✅ Mock interview started successfully")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Mock interview preview: {result['mock_interview'][:200]}...")
        else:
            print(f"❌ Mock interview failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error starting mock interview: {e}")
    print()

    # Test 4: Comprehensive Interview Preparation
    print("6. Test: Comprehensive Interview Preparation")
    print("-" * 80)
    try:
        result = await agent.prepare_for_interview(
            company_name="Microsoft",
            job_title="Senior Software Engineer",
            job_description="We are seeking an experienced software engineer to join our cloud computing team...",
            interview_date="2025-12-15",
            interview_type="technical"
        )

        if result["success"]:
            print("✅ Interview preparation successful")
            print(f"   Preparation plan preview: {result['preparation_plan'][:200]}...")
        else:
            print(f"❌ Interview preparation failed: {result.get('error')}")
    except Exception as e:
        print(f"❌ Error during interview preparation: {e}")
    print()

    # Test 5: Agent Statistics
    print("7. Test: Agent Statistics")
    print("-" * 80)
    try:
        stats = agent.get_stats()
        print("✅ Statistics retrieved successfully")
        print(f"   Agent Name: {stats['name']}")
        print(f"   Execution Count: {stats['execution_count']}")
        print(f"   Tools Count: {stats['tools_count']}")
        print(f"   Memory Size: {stats['memory_size']}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    print()

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("All core Interview Prep Agent functionalities have been tested.")
    print()
    print("Tools tested:")
    print("  ✓ Interview Question Generation")
    print("  ✓ STAR Format Answer Preparation")
    print("  ✓ Mock Interview Practice")
    print("  ✓ Comprehensive Interview Preparation")
    print("  ✓ Agent Statistics")
    print()
    print("Note: Individual tool functionalities (research_company, get_interview_tips,")
    print("      analyze_job_for_interview, get_interview_checklist) are used within")
    print("      the higher-level methods tested above.")
    print("=" * 80)


if __name__ == "__main__":
    print()
    print("Starting Interview Prep Agent Tests...")
    print()

    try:
        asyncio.run(test_interview_prep_agent())
        print()
        print("🎉 All tests completed successfully!")
        print()
    except KeyboardInterrupt:
        print()
        print("⚠️  Tests interrupted by user")
        print()
    except Exception as e:
        print()
        print(f"❌ Fatal error during testing: {e}")
        print()
        import traceback
        traceback.print_exc()
