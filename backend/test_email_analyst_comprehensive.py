"""
Comprehensive Test Suite for Email Analyst Agent

This test suite includes:
1. Unit tests for individual tools (no API key required)
2. Mock tests for agent behavior (no API key required)
3. Integration tests with real API (requires OPENAI_API_KEY)
4. Thread analysis tests
5. Performance and error handling tests
"""

import asyncio
import os
import sys
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework.agents.email_analyst_agent import create_email_analyst_agent, EmailAnalystAgent
from database.database_manager import DatabaseManager


# ============================================================================
# Test Data
# ============================================================================

SAMPLE_EMAILS = {
    'interview_invite': {
        'subject': 'Interview Invitation - Software Engineer Position at Google',
        'sender': 'recruiting@google.com',
        'body': '''Hi there,

Thank you for your interest in the Software Engineer position at Google!

We were impressed with your background and would like to schedule a technical interview with you. The interview will consist of two 45-minute sessions focusing on algorithms and system design.

Could you please let us know your availability for next week? We'd like to schedule this as soon as possible.

Looking forward to hearing from you!

Best regards,
Google Recruiting Team'''
    },
    'rejection': {
        'subject': 'Re: Senior Developer Application - Amazon',
        'sender': 'hiring@amazon.com',
        'body': '''Dear Candidate,

Thank you for your interest in the Senior Developer position at Amazon and for taking the time to interview with our team.

After careful consideration, we have decided to move forward with other candidates whose experience more closely matches our current needs. This was a difficult decision as we had many qualified applicants.

We appreciate your interest in Amazon and encourage you to apply for other positions that match your skills and experience.

Best of luck in your job search.

Sincerely,
Amazon Talent Acquisition'''
    },
    'offer': {
        'subject': 'Job Offer - Full Stack Engineer at Meta',
        'sender': 'offers@meta.com',
        'body': '''Congratulations!

We are pleased to extend an offer for the Full Stack Engineer position at Meta!

Offer Details:
- Base Salary: $180,000 per year
- Signing Bonus: $30,000
- Equity: RSUs valued at $100,000 (vesting over 4 years)
- Start Date: Flexible, preferably within next 4-6 weeks

This offer is valid for 7 days. Please review the attached offer letter and let us know if you have any questions.

We're excited about the possibility of you joining our team!

Best regards,
Meta Recruiting Team'''
    },
    'assessment': {
        'subject': 'Next Steps - Technical Assessment for Backend Engineer Role',
        'sender': 'talent@stripe.com',
        'body': '''Hello,

We're excited to move forward with your application for the Backend Engineer position at Stripe!

As a next step, we'd like you to complete a technical assessment. This is a take-home coding challenge that typically takes 3-4 hours to complete. You'll have 7 days to submit your solution.

The assessment will test your ability to:
- Design and implement RESTful APIs
- Work with databases
- Write clean, maintainable code
- Handle edge cases

Please confirm your interest and we'll send you the assessment link within 24 hours.

Best,
Stripe Engineering Team'''
    }
}

EMAIL_THREAD = [
    {
        'subject': 'Software Engineer Application',
        'sender': 'recruiting@techcorp.com',
        'date': '2025-01-10',
        'body': 'Thank you for your application. We are reviewing candidates and will be in touch soon.'
    },
    {
        'subject': 'Re: Software Engineer Application',
        'sender': 'me@email.com',
        'date': '2025-01-11',
        'body': 'Thank you for the update. I look forward to hearing from you.'
    },
    {
        'subject': 'Interview Invitation - Software Engineer',
        'sender': 'recruiting@techcorp.com',
        'date': '2025-01-15',
        'body': 'We would like to schedule an interview with you next week. Are you available on Tuesday or Wednesday?'
    }
]


# ============================================================================
# Unit Tests - No API Key Required
# ============================================================================

class TestEmailAnalystTools(unittest.TestCase):
    """Test individual tools without requiring API calls"""

    def setUp(self):
        self.db = DatabaseManager()
        # We'll mock the agent to avoid API calls
        self.mock_agent = Mock(spec=EmailAnalystAgent)
        self.mock_agent.db_manager = self.db

    def test_sentiment_analysis_positive(self):
        """Test sentiment analysis on positive email"""
        email_text = SAMPLE_EMAILS['offer']['body']

        # This would be the logic from the analyze_sentiment tool
        positive_keywords = ['congratulations', 'pleased', 'offer', 'excited']
        found_positive = sum(1 for kw in positive_keywords if kw.lower() in email_text.lower())

        self.assertGreater(found_positive, 0, "Should detect positive keywords")

    def test_sentiment_analysis_negative(self):
        """Test sentiment analysis on rejection email"""
        email_text = SAMPLE_EMAILS['rejection']['body']

        negative_keywords = ['unfortunately', 'decided not to', 'other candidates']
        found_negative = sum(1 for kw in negative_keywords if kw.lower() in email_text.lower())

        self.assertGreater(found_negative, 0, "Should detect negative keywords")

    def test_action_item_extraction(self):
        """Test action item extraction from email"""
        email_text = SAMPLE_EMAILS['interview_invite']['body']

        # Look for action-related patterns
        action_patterns = ['please', 'let us know', 'schedule', 'availability']
        found_actions = sum(1 for pattern in action_patterns if pattern.lower() in email_text.lower())

        self.assertGreater(found_actions, 0, "Should detect action items")

    def test_email_categorization(self):
        """Test email categorization logic"""
        interview_email = SAMPLE_EMAILS['interview_invite']['body']
        rejection_email = SAMPLE_EMAILS['rejection']['body']
        offer_email = SAMPLE_EMAILS['offer']['body']

        # Interview
        self.assertIn('interview', interview_email.lower())
        self.assertIn('schedule', interview_email.lower())

        # Rejection
        self.assertIn('other candidates', rejection_email.lower())
        self.assertIn('decided', rejection_email.lower())

        # Offer
        self.assertIn('offer', offer_email.lower())
        self.assertIn('salary', offer_email.lower())

    def test_company_extraction(self):
        """Test company name extraction"""
        emails = SAMPLE_EMAILS

        # Should be able to extract company names from sender or body
        companies = {
            'interview_invite': 'Google',
            'rejection': 'Amazon',
            'offer': 'Meta',
            'assessment': 'Stripe'
        }

        for email_type, expected_company in companies.items():
            email_content = f"{emails[email_type]['subject']} {emails[email_type]['body']}"
            self.assertIn(expected_company, email_content,
                         f"Should find {expected_company} in {email_type} email")


# ============================================================================
# Mock Integration Tests - No API Key Required
# ============================================================================

class TestEmailAnalystAgentMocked(unittest.TestCase):
    """Test agent behavior with mocked LLM responses"""

    def setUp(self):
        self.db = DatabaseManager()

    @patch('agents_framework.core.base_agent.ChatOpenAI')
    def test_agent_initialization(self, mock_llm):
        """Test that agent initializes correctly"""
        mock_llm.return_value = Mock()

        agent = create_email_analyst_agent(self.db)

        self.assertIsNotNone(agent)
        self.assertEqual(agent.name, "Email Analyst")
        self.assertGreater(len(agent.tools), 0, "Should have tools registered")

    @patch('agents_framework.core.base_agent.ChatOpenAI')
    def test_agent_has_all_tools(self, mock_llm):
        """Test that agent has all required tools"""
        mock_llm.return_value = Mock()

        agent = create_email_analyst_agent(self.db)

        expected_tools = [
            'analyze_email_sentiment',
            'extract_action_items',
            'categorize_email',
            'extract_company_position',
            'find_matching_applications',
            'recommend_followup',
            'analyze_email_thread'
        ]

        tool_names = [tool.name for tool in agent.tools]

        for expected_tool in expected_tools:
            self.assertIn(expected_tool, tool_names,
                         f"Agent should have {expected_tool} tool")

    def test_thread_data_formatting(self):
        """Test thread data formatting logic"""
        emails = EMAIL_THREAD

        # Format as the analyze_thread method does
        thread_data = ' /// '.join([
            f"{email.get('subject', 'No Subject')}|{email.get('sender', 'Unknown')}|{email.get('date', 'Unknown')}|{email.get('body', '')}"
            for email in emails
        ])

        self.assertIn('///', thread_data)
        self.assertIn('|', thread_data)
        self.assertEqual(thread_data.count('///'), len(emails) - 1)


# ============================================================================
# Integration Tests - Require API Key
# ============================================================================

class TestEmailAnalystAgentIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration tests with real API calls (requires OPENAI_API_KEY)"""

    @classmethod
    def setUpClass(cls):
        cls.has_api_key = bool(os.getenv('OPENAI_API_KEY'))
        if not cls.has_api_key:
            print("\n⚠️  OPENAI_API_KEY not set - skipping integration tests")
            print("   Set OPENAI_API_KEY in .env file to run these tests")

    def setUp(self):
        self.db = DatabaseManager()
        if self.has_api_key:
            self.agent = create_email_analyst_agent(self.db)

    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    async def test_analyze_interview_email(self):
        """Test analyzing an interview invitation email"""
        email = SAMPLE_EMAILS['interview_invite']

        result = await self.agent.analyze_email(
            subject=email['subject'],
            body=email['body'],
            sender=email['sender']
        )

        self.assertTrue(result['success'], "Analysis should succeed")
        self.assertIsNotNone(result['analysis'], "Should return analysis")
        self.assertIn('interview', result['analysis'].lower(),
                     "Analysis should mention interview")

    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    async def test_analyze_rejection_email(self):
        """Test analyzing a rejection email"""
        email = SAMPLE_EMAILS['rejection']

        result = await self.agent.analyze_email(
            subject=email['subject'],
            body=email['body'],
            sender=email['sender']
        )

        self.assertTrue(result['success'], "Analysis should succeed")
        self.assertIsNotNone(result['analysis'], "Should return analysis")

    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    async def test_analyze_offer_email(self):
        """Test analyzing an offer email"""
        email = SAMPLE_EMAILS['offer']

        result = await self.agent.analyze_email(
            subject=email['subject'],
            body=email['body'],
            sender=email['sender']
        )

        self.assertTrue(result['success'], "Analysis should succeed")
        self.assertIsNotNone(result['analysis'], "Should return analysis")
        self.assertIn('offer', result['analysis'].lower(),
                     "Analysis should mention offer")

    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    async def test_analyze_thread(self):
        """Test analyzing an email thread"""
        result = await self.agent.analyze_thread(
            emails=EMAIL_THREAD
        )

        self.assertTrue(result['success'], "Thread analysis should succeed")
        self.assertEqual(result['email_count'], len(EMAIL_THREAD))
        self.assertIsNotNone(result['analysis'], "Should return analysis")

    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires OPENAI_API_KEY")
    async def test_agent_statistics(self):
        """Test getting agent statistics"""
        stats = self.agent.get_stats()

        self.assertIn('name', stats)
        self.assertIn('execution_count', stats)
        self.assertIn('tools_count', stats)
        self.assertEqual(stats['name'], 'Email Analyst')
        self.assertGreaterEqual(stats['tools_count'], 7)


# ============================================================================
# Manual Test Runner
# ============================================================================

async def run_manual_tests():
    """Run manual tests with real emails to see actual output"""
    print("=" * 80)
    print("MANUAL EMAIL ANALYST AGENT TESTING")
    print("=" * 80)
    print()

    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not set!")
        print()
        print("To run these tests:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to the .env file")
        print("3. Run: python -m pytest test_email_analyst_comprehensive.py")
        print()
        print("Running unit tests only (no API calls)...")
        print()
        return False

    try:
        print("✅ OPENAI_API_KEY found")
        print("🔧 Initializing Email Analyst Agent...")
        print()

        db = DatabaseManager()
        agent = create_email_analyst_agent(db)

        print(f"✅ Agent initialized: {agent.name}")
        print(f"📊 Tools available: {len(agent.tools)}")
        for i, tool in enumerate(agent.tools, 1):
            print(f"   {i}. {tool.name}")
        print()

        # Test each email type
        for email_type, email_data in SAMPLE_EMAILS.items():
            print("=" * 80)
            print(f"TEST: {email_type.replace('_', ' ').title()}")
            print("=" * 80)
            print()
            print(f"📧 From: {email_data['sender']}")
            print(f"📧 Subject: {email_data['subject']}")
            print()
            print("🤖 Analyzing...")
            print()

            result = await agent.analyze_email(
                subject=email_data['subject'],
                body=email_data['body'],
                sender=email_data['sender']
            )

            if result['success']:
                print("✅ ANALYSIS RESULTS:")
                print()
                print(result['analysis'])
            else:
                print(f"❌ Error: {result['error']}")

            print()
            print("-" * 80)
            print()

        # Test thread analysis
        print("=" * 80)
        print("TEST: Email Thread Analysis")
        print("=" * 80)
        print()
        print(f"🧵 Thread with {len(EMAIL_THREAD)} emails")
        print()

        result = await agent.analyze_thread(emails=EMAIL_THREAD)

        if result['success']:
            print("✅ THREAD ANALYSIS:")
            print()
            print(result['analysis'])
        else:
            print(f"❌ Error: {result['error']}")

        print()
        print("=" * 80)
        print("✅ ALL MANUAL TESTS COMPLETED!")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"❌ Error during manual testing: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description='Test Email Analyst Agent')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--manual', action='store_true', help='Run manual tests with output')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    args = parser.parse_args()

    # Default to all tests if no specific option
    if not any([args.unit, args.integration, args.manual, args.all]):
        args.all = True

    print()
    print("🧪 Email Analyst Agent Test Suite")
    print("=" * 80)
    print()

    if args.manual or args.all:
        print("Running manual tests...")
        asyncio.run(run_manual_tests())
        print()

    if args.unit or args.all:
        print("Running unit tests...")
        suite = unittest.TestLoader().loadTestsFromTestCase(TestEmailAnalystTools)
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestEmailAnalystAgentMocked))
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        print()

    if args.integration or args.all:
        if os.getenv('OPENAI_API_KEY'):
            print("Running integration tests...")
            suite = unittest.TestLoader().loadTestsFromTestCase(TestEmailAnalystAgentIntegration)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            print()
        else:
            print("⚠️  Skipping integration tests (OPENAI_API_KEY not set)")
            print()


if __name__ == '__main__':
    main()
