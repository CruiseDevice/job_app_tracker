"""
Comprehensive Test Suite for Application Manager Agent

Tests lifecycle prediction, auto-status updates, action recommendations,
pattern recognition, health scoring, and portfolio analysis.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework.agents.application_manager_agent import create_application_manager_agent
from database.database_manager import DatabaseManager


async def test_application_manager():
    """Test Application Manager Agent with sample applications"""
    print("=" * 80)
    print("APPLICATION MANAGER AGENT - COMPREHENSIVE TEST")
    print("=" * 80)
    print()

    # Initialize database
    db = DatabaseManager()
    db.init_db()

    # Create sample applications for testing
    print("🔧 Setting up test applications...")
    test_apps = create_test_applications(db)
    print(f"✅ Created {len(test_apps)} test applications\n")

    # Create agent
    print("🤖 Initializing Application Manager Agent...")
    agent = create_application_manager_agent(db)
    print(f"✅ Agent initialized: {agent.name}")
    print(f"📊 Tools available: {len(agent.tools)}")
    for i, tool in enumerate(agent.tools, 1):
        print(f"   {i}. {tool.name}")
    print()

    # Test 1: Lifecycle Prediction
    print("=" * 80)
    print("TEST 1: Lifecycle Prediction")
    print("=" * 80)
    print()
    for app in test_apps[:3]:  # Test first 3 apps
        print(f"📊 Application: {app['company']} - {app['position']}")
        print(f"   Status: {app['status']}")
        print()

        # Get lifecycle tool
        lifecycle_tool = next(t for t in agent.tools if t.name == "predict_lifecycle")
        result = lifecycle_tool.func(str(app['id']))
        print(result)
        print()

    # Test 2: Health Score Calculation
    print("=" * 80)
    print("TEST 2: Health Score Calculation")
    print("=" * 80)
    print()
    health_tool = next(t for t in agent.tools if t.name == "calculate_health_score")
    for app in test_apps[:3]:
        print(f"💚 Application: {app['company']} - {app['position']}")
        result = health_tool.func(str(app['id']))
        print(result)
        print()

    # Test 3: Next Action Recommendations
    print("=" * 80)
    print("TEST 3: Next Action Recommendations")
    print("=" * 80)
    print()
    actions_tool = next(t for t in agent.tools if t.name == "recommend_next_actions")
    for app in test_apps[:3]:
        print(f"📋 Application: {app['company']} - {app['position']}")
        result = actions_tool.func(str(app['id']))
        print(result)
        print()

    # Test 4: Pattern Recognition
    print("=" * 80)
    print("TEST 4: Success Pattern Recognition")
    print("=" * 80)
    print()
    patterns_tool = next(t for t in agent.tools if t.name == "identify_patterns")
    result = patterns_tool.func()
    print(result)
    print()

    # Test 5: Auto-Status Update
    print("=" * 80)
    print("TEST 5: Auto-Status Update Suggestion")
    print("=" * 80)
    print()
    auto_status_tool = next(t for t in agent.tools if t.name == "auto_update_status")

    # Simulate email analyses
    email_scenarios = [
        (test_apps[0]['id'], "Email contains: 'We would like to schedule an interview with you next week'"),
        (test_apps[1]['id'], "Email contains: 'Unfortunately, we have decided to move forward with other candidates'"),
        (test_apps[2]['id'], "Email contains: 'Congratulations! We are pleased to extend an offer for the position'"),
    ]

    for app_id, analysis in email_scenarios:
        app = next(a for a in test_apps if a['id'] == app_id)
        print(f"🔄 Application: {app['company']} - {app['position']}")
        print(f"   Email Analysis: {analysis}")
        print()
        result = auto_status_tool.func(f"{app_id}|{analysis}")
        print(result)
        print()

    # Test 6: Generate Insights
    print("=" * 80)
    print("TEST 6: Generate Insights")
    print("=" * 80)
    print()
    insights_tool = next(t for t in agent.tools if t.name == "generate_insights")

    for focus in ['general', 'timeline', 'success_rate', 'recommendations']:
        print(f"💡 Focus Area: {focus.upper()}")
        print("-" * 40)
        result = insights_tool.func(focus)
        print(result)
        print()

    # Test 7: Full Application Management (with AI if API key is available)
    if os.getenv('OPENAI_API_KEY'):
        print("=" * 80)
        print("TEST 7: Full Application Management (AI-Powered)")
        print("=" * 80)
        print()
        print("🤖 Using AI to comprehensively manage an application...")
        print()

        result = await agent.manage_application(
            application_id=test_apps[0]['id'],
            context="This is a high-priority application that I'm very interested in."
        )

        if result['success']:
            print("✅ MANAGEMENT INSIGHTS:")
            print()
            print(result['insights'])
        else:
            print(f"❌ Error: {result['error']}")
        print()

        # Test 8: Portfolio Analysis (with AI)
        print("=" * 80)
        print("TEST 8: Portfolio Analysis (AI-Powered)")
        print("=" * 80)
        print()
        print("🤖 Analyzing entire application portfolio...")
        print()

        result = await agent.analyze_portfolio()

        if result['success']:
            print("✅ PORTFOLIO ANALYSIS:")
            print()
            print(result['analysis'])
        else:
            print(f"❌ Error: {result['error']}")
        print()
    else:
        print("=" * 80)
        print("⚠️  OPENAI_API_KEY not set - Skipping AI-powered tests")
        print("=" * 80)
        print()
        print("To test AI-powered features:")
        print("1. Set OPENAI_API_KEY in .env file")
        print("2. Run this test again")
        print()

    print("=" * 80)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 80)
    print()


def create_test_applications(db: DatabaseManager):
    """Create sample applications for testing"""
    test_data = [
        {
            'company': 'Google',
            'position': 'Senior Software Engineer',
            'status': 'interview',
            'days_ago': 15,
            'notes': 'Great interview, felt very positive'
        },
        {
            'company': 'Amazon',
            'position': 'Backend Developer',
            'status': 'applied',
            'days_ago': 20,
            'notes': 'No response yet'
        },
        {
            'company': 'Meta',
            'position': 'Full Stack Engineer',
            'status': 'screening',
            'days_ago': 7,
            'notes': 'Phone screen scheduled for next week'
        },
        {
            'company': 'Netflix',
            'position': 'DevOps Engineer',
            'status': 'assessment',
            'days_ago': 5,
            'notes': 'Completing take-home challenge'
        },
        {
            'company': 'Apple',
            'position': 'iOS Developer',
            'status': 'applied',
            'days_ago': 3,
            'notes': 'Just submitted application'
        },
        {
            'company': 'Microsoft',
            'position': 'Cloud Engineer',
            'status': 'rejected',
            'days_ago': 25,
            'notes': 'Not a good fit for the role'
        },
    ]

    apps = []
    for data in test_data:
        app_date = datetime.now() - timedelta(days=data['days_ago'])

        # Check if application already exists
        all_apps = db.get_all_applications()
        existing = next((a for a in all_apps if a.company == data['company'] and a.position == data['position']), None)

        if existing:
            apps.append({
                'id': existing.id,
                'company': existing.company,
                'position': existing.position,
                'status': existing.status
            })
        else:
            # Create new application (simplified - would need to adjust based on actual DB schema)
            try:
                # Using a mock ID since we can't easily create apps through the API
                app_id = len(all_apps) + len(apps) + 1
                apps.append({
                    'id': app_id,
                    'company': data['company'],
                    'position': data['position'],
                    'status': data['status']
                })
            except Exception as e:
                print(f"Warning: Could not create test application: {e}")

    return apps


def run_quick_test():
    """Quick test of individual tools without AI"""
    print("=" * 80)
    print("QUICK TEST - Application Manager Tools")
    print("=" * 80)
    print()

    db = DatabaseManager()
    agent = create_application_manager_agent(db)

    print("Testing tools with mock data...")
    print()

    # Mock application ID
    app_id = "1"

    # Test each tool
    tools_to_test = [
        ("predict_lifecycle", app_id),
        ("calculate_health_score", app_id),
        ("recommend_next_actions", app_id),
        ("identify_patterns", ""),
        ("generate_insights", "general"),
    ]

    for tool_name, input_val in tools_to_test:
        print(f"🔧 Testing: {tool_name}")
        print("-" * 40)
        try:
            tool = next(t for t in agent.tools if t.name == tool_name)
            if input_val:
                result = tool.func(input_val)
            else:
                result = tool.func()
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

    print("✅ Quick test complete!")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test Application Manager Agent')
    parser.add_argument('--quick', action='store_true', help='Run quick test only')
    args = parser.parse_args()

    if args.quick:
        run_quick_test()
    else:
        asyncio.run(test_application_manager())
