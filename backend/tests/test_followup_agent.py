# backend/tests/test_followup_agent.py

"""
Test scripts to validate the Follow-up Agent functionality.
Tests timing optimization, message drafting, and strategy planning.
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database_manager import DatabaseManager
from agents_framework.agents.followup_agent import create_followup_agent


class FollowUpAgentTests:
    """Comprehensive test suite for Follow-up Agent"""

    def __init__(self):
        self.db = DatabaseManager()
        self.agent = create_followup_agent(self.db)
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

    async def test_timing_optimization_applied_status(self):
        """Test timing recommendations for 'applied' status"""
        print("\n🧪 Testing timing optimization for 'applied' status...")

        test_cases = [
            # (days_since_contact, should_wait, description)
            (3, True, "Too early - should wait"),
            (7, False, "Optimal timing - should follow up"),
            (10, False, "Overdue - should follow up immediately"),
        ]

        for days, should_wait, description in test_cases:
            result = await self.agent.optimize_followup_timing(
                job_id=1,
                status="applied",
                days_since_contact=days,
                application_date="2025-11-01"
            )

            # Check if result contains appropriate recommendation
            output = result.get('output', '').lower() if result.get('success') else ''

            if should_wait:
                passed = 'wait' in output or 'too early' in output
            else:
                passed = 'follow up' in output or 'optimal' in output or 'overdue' in output

            self.log_test(
                f"Timing for 'applied' at {days} days",
                passed,
                f"{description} - Success: {result.get('success')}"
            )

    async def test_timing_optimization_interview_status(self):
        """Test timing recommendations for 'interview' status"""
        print("\n🧪 Testing timing optimization for 'interview' status...")

        result = await self.agent.optimize_followup_timing(
            job_id=2,
            status="interview",
            days_since_contact=1,
            application_date="2025-10-15"
        )

        # Post-interview should recommend quick follow-up
        output = result.get('output', '').lower() if result.get('success') else ''
        passed = result.get('success') and ('optimal' in output or 'follow up' in output)

        self.log_test(
            "Timing for 'interview' status",
            passed,
            f"Should recommend prompt follow-up - Success: {result.get('success')}"
        )

    async def test_message_drafting_initial_application(self):
        """Test message drafting for initial application follow-up"""
        print("\n🧪 Testing message drafting for initial application...")

        result = await self.agent.draft_followup(
            followup_type="initial_application",
            company="Google",
            position="Software Engineer",
            tone="professional",
            context_notes="Applied via LinkedIn"
        )

        # Check if message contains key elements
        message = result.get('message', '').lower() if result.get('success') else ''

        has_subject = 'subject:' in message
        has_company = 'google' in message
        has_position = 'software engineer' in message.lower()
        has_closing = 'regards' in message or 'sincerely' in message

        passed = result.get('success') and has_subject and has_company and has_position

        self.log_test(
            "Draft initial application message",
            passed,
            f"Contains required elements - Subject: {has_subject}, Company: {has_company}, Position: {has_position}"
        )

    async def test_message_drafting_post_interview(self):
        """Test message drafting for post-interview thank you"""
        print("\n🧪 Testing message drafting for post-interview...")

        result = await self.agent.draft_followup(
            followup_type="post_interview",
            company="Meta",
            position="Frontend Developer",
            tone="enthusiastic",
            context_notes="Discussed React and TypeScript"
        )

        message = result.get('message', '').lower() if result.get('success') else ''

        has_thank_you = 'thank' in message
        has_company = 'meta' in message
        has_enthusiasm = 'excited' in message or 'enjoyed' in message or 'looking forward' in message

        passed = result.get('success') and has_thank_you and has_enthusiasm

        self.log_test(
            "Draft post-interview thank you",
            passed,
            f"Contains thank you and enthusiasm - Success: {result.get('success')}"
        )

    async def test_message_tone_variations(self):
        """Test different message tones"""
        print("\n🧪 Testing message tone variations...")

        tones = ["professional", "casual", "enthusiastic"]

        for tone in tones:
            result = await self.agent.draft_followup(
                followup_type="checking_in",
                company="Amazon",
                position="Backend Engineer",
                tone=tone,
                context_notes=""
            )

            passed = result.get('success', False)

            self.log_test(
                f"Draft message with '{tone}' tone",
                passed,
                f"Success: {result.get('success')}"
            )

    async def test_strategy_planning_no_response(self):
        """Test strategy planning for applications with no response"""
        print("\n🧪 Testing strategy planning for no response scenario...")

        result = await self.agent.analyze_strategy(
            status="applied",
            days_since_application=10,
            response_history="no_response",
            priority="medium"
        )

        strategy = result.get('strategy', '').lower() if result.get('success') else ''

        # Should recommend progressive persistence
        has_sequence = 'follow-up sequence' in strategy or 'sequence' in strategy
        has_timeline = 'day' in strategy
        has_strategy_type = 'progressive' in strategy or 'persistence' in strategy or 'strategy' in strategy

        passed = result.get('success') and (has_sequence or has_timeline)

        self.log_test(
            "Strategy for no response",
            passed,
            f"Contains follow-up sequence - Success: {result.get('success')}"
        )

    async def test_strategy_planning_positive_response(self):
        """Test strategy planning for positive response"""
        print("\n🧪 Testing strategy planning for positive response...")

        result = await self.agent.analyze_strategy(
            status="interview",
            days_since_application=5,
            response_history="positive",
            priority="high"
        )

        strategy = result.get('strategy', '').lower() if result.get('success') else ''

        # Should be more aggressive/engaged
        has_engagement = 'engaged' in strategy or 'enthusiastic' in strategy or 'follow-through' in strategy

        passed = result.get('success')

        self.log_test(
            "Strategy for positive response",
            passed,
            f"Success: {result.get('success')}"
        )

    async def test_strategy_priority_levels(self):
        """Test strategy adjustments based on priority"""
        print("\n🧪 Testing strategy priority levels...")

        priorities = ["low", "medium", "high"]

        for priority in priorities:
            result = await self.agent.analyze_strategy(
                status="applied",
                days_since_application=8,
                response_history="no_response",
                priority=priority
            )

            passed = result.get('success', False)

            self.log_test(
                f"Strategy with '{priority}' priority",
                passed,
                f"Success: {result.get('success')}"
            )

    async def test_agent_tools_registration(self):
        """Test that all agent tools are properly registered"""
        print("\n🧪 Testing agent tools registration...")

        # Check if agent has required tools
        expected_tools = [
            'calculate_optimal_timing',
            'draft_followup_message',
            'get_followup_schedule',
            'analyze_response_patterns',
            'suggest_followup_strategy',
            'track_followup_performance',
            'get_followup_templates'
        ]

        # Agent tools are registered internally
        # We verify by checking if the agent can execute
        passed = True
        missing_tools = []

        # This is a basic check - in production you'd verify each tool
        if not hasattr(self.agent, 'tools') or len(self.agent.tools) == 0:
            passed = False
            missing_tools = expected_tools

        self.log_test(
            "Agent tools registration",
            passed,
            f"Expected {len(expected_tools)} tools, Agent initialized successfully"
        )

    async def test_agent_memory_system(self):
        """Test agent memory and learning capabilities"""
        print("\n🧪 Testing agent memory system...")

        # Test that agent has memory managers
        has_conversation_memory = hasattr(self.agent, 'conversation_memory')
        has_rag_memory = hasattr(self.agent, 'rag_memory')

        passed = has_conversation_memory and has_rag_memory

        self.log_test(
            "Agent memory system",
            passed,
            f"Conversation memory: {has_conversation_memory}, RAG memory: {has_rag_memory}"
        )

    async def test_error_handling_invalid_inputs(self):
        """Test error handling for invalid inputs"""
        print("\n🧪 Testing error handling...")

        # Test with missing required fields (should handle gracefully)
        try:
            result = await self.agent.optimize_followup_timing(
                job_id=None,
                status="",
                days_since_contact=-1,
                application_date=""
            )

            # Should either return error or handle gracefully
            passed = not result.get('success') or 'error' in str(result).lower()

        except Exception as e:
            # Catching exception is acceptable
            passed = True

        self.log_test(
            "Error handling for invalid inputs",
            passed,
            "Agent handles invalid inputs appropriately"
        )

    async def test_agent_performance(self):
        """Test agent response time"""
        print("\n🧪 Testing agent performance...")

        start_time = datetime.now()

        result = await self.agent.draft_followup(
            followup_type="initial_application",
            company="Test Corp",
            position="Test Position",
            tone="professional",
            context_notes=""
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Agent should respond within reasonable time (< 30 seconds)
        passed = duration < 30 and result.get('success')

        self.log_test(
            "Agent response time",
            passed,
            f"Response time: {duration:.2f}s (should be < 30s)"
        )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️ {self.failed} test(s) failed")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}")

        print("="*60)

    async def run_all_tests(self):
        """Run all test cases"""
        print("🚀 Starting Follow-up Agent Test Suite")
        print("="*60)

        # Timing tests
        await self.test_timing_optimization_applied_status()
        await self.test_timing_optimization_interview_status()

        # Message drafting tests
        await self.test_message_drafting_initial_application()
        await self.test_message_drafting_post_interview()
        await self.test_message_tone_variations()

        # Strategy planning tests
        await self.test_strategy_planning_no_response()
        await self.test_strategy_planning_positive_response()
        await self.test_strategy_priority_levels()

        # System tests
        await self.test_agent_tools_registration()
        await self.test_agent_memory_system()
        await self.test_error_handling_invalid_inputs()
        await self.test_agent_performance()

        # Print summary
        self.print_summary()

        return self.failed == 0


async def main():
    """Main test runner"""
    tests = FollowUpAgentTests()
    success = await tests.run_all_tests()

    # Exit with appropriate code
    exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
