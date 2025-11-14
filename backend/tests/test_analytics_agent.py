"""
Test Suite for Analytics Agent

Tests for the Analytics & Strategy Agent functionality including:
- Data analysis
- Success pattern recognition
- Offer likelihood prediction
- Strategy recommendations
- Salary analysis
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from backend.agents_framework.agents.analytics_agent import AnalyticsAgent, create_analytics_agent
from backend.agents_framework.core.base_agent import AgentConfig
from backend.database.database_manager import DatabaseManager


@pytest.fixture
def db_manager():
    """Create a database manager for testing."""
    return DatabaseManager()


@pytest.fixture
def analytics_agent(db_manager):
    """Create an Analytics Agent for testing."""
    config = AgentConfig(
        name="Test Analytics Agent",
        description="Analytics agent for testing",
        model="gpt-4o-mini",
        temperature=0.2,
        verbose=True
    )
    return AnalyticsAgent(db_manager=db_manager, config=config)


@pytest.mark.asyncio
async def test_agent_initialization(analytics_agent):
    """Test that the Analytics Agent initializes correctly."""
    assert analytics_agent is not None
    assert analytics_agent.name == "Test Analytics Agent"
    assert len(analytics_agent.tools) == 6
    print(f"✅ Agent initialized with {len(analytics_agent.tools)} tools")


@pytest.mark.asyncio
async def test_analyze_application_data(analytics_agent):
    """Test application data analysis."""
    print("\n📊 Testing application data analysis...")

    result = await analytics_agent.analyze_application_data(
        user_id=1,
        time_period_days=90
    )

    assert result['success'] is True
    assert 'analysis' in result
    print(f"✅ Data analysis completed successfully")
    print(f"Analysis preview: {result['analysis'][:200]}...")


@pytest.mark.asyncio
async def test_get_success_patterns(analytics_agent):
    """Test success pattern identification."""
    print("\n🔍 Testing success pattern identification...")

    result = await analytics_agent.get_success_patterns(
        user_id=1,
        min_confidence=0.7
    )

    assert result['success'] is True
    assert 'patterns' in result
    print(f"✅ Pattern identification completed successfully")
    print(f"Patterns preview: {result['patterns'][:200]}...")


@pytest.mark.asyncio
async def test_predict_offer_success(analytics_agent):
    """Test offer likelihood prediction."""
    print("\n🎯 Testing offer likelihood prediction...")

    job_details = {
        "title": "Software Engineer",
        "company_size": "Medium",
        "industry": "Technology"
    }

    user_profile = {
        "skills_match_percent": 75,
        "has_referral": False,
        "has_cover_letter": True,
        "years_experience": 5,
        "application_quality_score": 8.0
    }

    result = await analytics_agent.predict_offer_success(
        job_details=job_details,
        user_profile=user_profile
    )

    assert result['success'] is True
    assert 'prediction' in result
    print(f"✅ Offer prediction completed successfully")
    print(f"Prediction preview: {result['prediction'][:200]}...")


@pytest.mark.asyncio
async def test_get_optimization_strategy(analytics_agent):
    """Test strategy recommendation generation."""
    print("\n🎯 Testing strategy recommendations...")

    current_stats = {
        "success_rate": 0.067,
        "applications_per_week": 10
    }

    result = await analytics_agent.get_optimization_strategy(
        current_stats=current_stats,
        target_role="Software Engineer"
    )

    assert result['success'] is True
    assert 'strategy' in result
    print(f"✅ Strategy generation completed successfully")
    print(f"Strategy preview: {result['strategy'][:200]}...")


@pytest.mark.asyncio
async def test_get_salary_insights(analytics_agent):
    """Test market salary analysis."""
    print("\n💰 Testing salary analysis...")

    result = await analytics_agent.get_salary_insights(
        job_title="Software Engineer",
        location="San Francisco, CA",
        years_experience=5,
        industry="Technology",
        company_size="Medium"
    )

    assert result['success'] is True
    assert 'salary_analysis' in result
    print(f"✅ Salary analysis completed successfully")
    print(f"Salary analysis preview: {result['salary_analysis'][:200]}...")


@pytest.mark.asyncio
async def test_factory_function(db_manager):
    """Test the factory function for creating Analytics Agent."""
    print("\n🏭 Testing factory function...")

    agent = create_analytics_agent(db_manager)

    assert agent is not None
    assert isinstance(agent, AnalyticsAgent)
    assert len(agent.tools) == 6
    print(f"✅ Factory function created agent successfully")


@pytest.mark.asyncio
async def test_agent_stats(analytics_agent):
    """Test agent statistics retrieval."""
    print("\n📊 Testing agent statistics...")

    # Run a few operations first
    await analytics_agent.analyze_application_data(user_id=1)

    stats = analytics_agent.get_stats()

    assert stats['name'] == "Test Analytics Agent"
    assert stats['execution_count'] > 0
    assert stats['tools_count'] == 6
    assert len(stats['tools']) == 6

    print(f"✅ Agent stats retrieved successfully")
    print(f"Executions: {stats['execution_count']}")
    print(f"Tools: {stats['tools_count']}")


def test_comprehensive_workflow():
    """Test a comprehensive workflow using the Analytics Agent."""
    print("\n🔄 Testing comprehensive workflow...")

    async def workflow():
        db = DatabaseManager()
        agent = create_analytics_agent(db)

        # 1. Analyze application data
        print("Step 1: Analyzing application data...")
        data_result = await agent.analyze_application_data(user_id=1, time_period_days=90)
        assert data_result['success'] is True

        # 2. Identify success patterns
        print("Step 2: Identifying success patterns...")
        patterns_result = await agent.get_success_patterns(user_id=1, min_confidence=0.7)
        assert patterns_result['success'] is True

        # 3. Predict offer likelihood
        print("Step 3: Predicting offer likelihood...")
        prediction_result = await agent.predict_offer_success(
            job_details={"title": "Software Engineer", "company_size": "Medium", "industry": "Technology"},
            user_profile={"skills_match_percent": 80, "has_referral": True, "has_cover_letter": True,
                         "years_experience": 5, "application_quality_score": 8.5}
        )
        assert prediction_result['success'] is True

        # 4. Generate strategy
        print("Step 4: Generating optimization strategy...")
        strategy_result = await agent.get_optimization_strategy(
            current_stats={"success_rate": 0.15, "applications_per_week": 12},
            target_role="Software Engineer"
        )
        assert strategy_result['success'] is True

        # 5. Analyze salary
        print("Step 5: Analyzing market salary...")
        salary_result = await agent.get_salary_insights(
            job_title="Software Engineer",
            location="San Francisco, CA",
            years_experience=5
        )
        assert salary_result['success'] is True

        print("✅ All workflow steps completed successfully!")

        # Get final stats
        final_stats = agent.get_stats()
        print(f"\nFinal Agent Stats:")
        print(f"  - Total executions: {final_stats['execution_count']}")
        print(f"  - Tools available: {final_stats['tools_count']}")
        print(f"  - Memory size: {final_stats['memory_size']}")

    # Run the async workflow
    asyncio.run(workflow())


if __name__ == "__main__":
    print("=" * 70)
    print("ANALYTICS AGENT TEST SUITE")
    print("=" * 70)

    # Run comprehensive workflow test
    test_comprehensive_workflow()

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
