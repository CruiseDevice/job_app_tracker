"""
Test script for Email Analyst Agent

Demonstrates the capabilities of the Email Analyst Agent with sample emails.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework.agents.email_analyst_agent import create_email_analyst_agent
from database.database_manager import DatabaseManager


# Sample test emails
SAMPLE_EMAILS = [
    {
        'name': 'Interview Invitation',
        'subject': 'Interview Invitation - Software Engineer Position at Google',
        'sender': 'recruiting@google.com',
        'body': '''Hi there,

Thank you for your interest in the Software Engineer position at Google!

We were impressed with your background and would like to schedule a technical interview with you. The interview will consist of two 45-minute sessions focusing on algorithms and system design.

Could you please let us know your availability for next week? We'd like to schedule this as soon as possible.

Looking forward to hearing from you!

Best regards,
Google Recruiting Team
'''
    },
    {
        'name': 'Rejection Email',
        'subject': 'Re: Senior Developer Application - Amazon',
        'sender': 'hiring@amazon.com',
        'body': '''Dear Candidate,

Thank you for your interest in the Senior Developer position at Amazon and for taking the time to interview with our team.

After careful consideration, we have decided to move forward with other candidates whose experience more closely matches our current needs. This was a difficult decision as we had many qualified applicants.

We appreciate your interest in Amazon and encourage you to apply for other positions that match your skills and experience.

Best of luck in your job search.

Sincerely,
Amazon Talent Acquisition
'''
    },
    {
        'name': 'Coding Challenge',
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
Stripe Engineering Team
'''
    },
    {
        'name': 'Job Offer',
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
Meta Recruiting Team
'''
    },
    {
        'name': 'Phone Screen Confirmation',
        'sender': 'recruiter@netflix.com',
        'subject': 'Phone Screen Scheduled - Software Engineer Position',
        'body': '''Hi,

Just confirming our phone screen scheduled for tomorrow at 2:00 PM PST.

The call will last approximately 30 minutes and will focus on:
- Your background and experience
- Your interest in Netflix and this role
- Your salary expectations
- Technical screening questions

Please have your resume handy and be prepared to discuss your recent projects.

Looking forward to our conversation!

Best,
Sarah Johnson
Netflix Recruiting
'''
    }
]


async def test_email_analyst():
    """Test the Email Analyst Agent with sample emails"""
    print("=" * 70)
    print("EMAIL ANALYST AGENT TEST SUITE")
    print("=" * 70)
    print()

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    try:
        # Initialize database
        print("1. Initializing database...")
        db = DatabaseManager()
        print("   ✅ Database initialized\n")

        # Create Email Analyst Agent
        print("2. Creating Email Analyst Agent...")
        agent = create_email_analyst_agent(db)
        print(f"   ✅ Agent created: {agent.name}")
        print(f"   Tools available: {len(agent.tools)}")
        for tool in agent.tools:
            print(f"      - {tool.name}")
        print()

        # Test each sample email
        for i, email in enumerate(SAMPLE_EMAILS, 1):
            print("=" * 70)
            print(f"TEST {i}: {email['name']}")
            print("=" * 70)
            print()

            print(f"📧 Email Preview:")
            print(f"   From: {email['sender']}")
            print(f"   Subject: {email['subject']}")
            print(f"   Body: {email['body'][:100]}...")
            print()

            print("🤖 Running Email Analyst Agent...")
            print()

            # Analyze the email
            result = await agent.analyze_email(
                subject=email['subject'],
                body=email['body'],
                sender=email['sender']
            )

            if result['success']:
                print("✅ ANALYSIS RESULTS:")
                print()
                print(result['analysis'])
                print()
                print(f"Metadata: {result['metadata']}")
            else:
                print(f"❌ Error: {result['error']}")

            print()
            print("-" * 70)
            print()

            # Small delay between tests
            if i < len(SAMPLE_EMAILS):
                print("Press Enter to continue to next test...")
                input()
                print()

        # Show agent statistics
        print("=" * 70)
        print("AGENT STATISTICS")
        print("=" * 70)
        print()

        stats = agent.get_stats()
        print(f"Agent: {stats['name']}")
        print(f"Total Executions: {stats['execution_count']}")
        print(f"Tools Available: {stats['tools_count']}")
        print(f"Memory Size: {stats['memory_size']} messages")
        print()

        print("=" * 70)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def test_quick_analysis():
    """Quick test with a single email"""
    print("🧪 Quick Email Analysis Test\n")

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)

    # Initialize
    db = DatabaseManager()
    agent = create_email_analyst_agent(db)

    # Test with interview invitation
    email = SAMPLE_EMAILS[0]  # Interview invitation

    print(f"Analyzing: {email['subject']}\n")

    result = await agent.analyze_email(
        subject=email['subject'],
        body=email['body'],
        sender=email['sender']
    )

    if result['success']:
        print("Analysis:")
        print(result['analysis'])
    else:
        print(f"Error: {result['error']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test Email Analyst Agent')
    parser.add_argument('--quick', action='store_true', help='Run quick test with single email')
    args = parser.parse_args()

    if args.quick:
        asyncio.run(test_quick_analysis())
    else:
        asyncio.run(test_email_analyst())
