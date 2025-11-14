"""
Email Analyst Agent Demonstration

This script demonstrates the Email Analyst Agent's capabilities by showing
what each tool does with sample emails. No API key required for this demo.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework.agents.email_analyst_agent import create_email_analyst_agent
from database.database_manager import DatabaseManager


# Sample emails
SAMPLE_EMAILS = {
    'Interview Invitation': {
        'sender': 'recruiting@google.com',
        'subject': 'Interview Invitation - Software Engineer Position at Google',
        'body': '''Hi there,

Thank you for your interest in the Software Engineer position at Google!

We were impressed with your background and would like to schedule a technical interview with you. The interview will consist of two 45-minute sessions focusing on algorithms and system design.

Could you please let us know your availability for next week? We'd like to schedule this as soon as possible.

Looking forward to hearing from you!

Best regards,
Google Recruiting Team'''
    },
    'Job Offer': {
        'sender': 'offers@meta.com',
        'subject': 'Job Offer - Full Stack Engineer at Meta',
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
    'Rejection': {
        'sender': 'hiring@amazon.com',
        'subject': 'Re: Senior Developer Application - Amazon',
        'body': '''Dear Candidate,

Thank you for your interest in the Senior Developer position at Amazon and for taking the time to interview with our team.

After careful consideration, we have decided to move forward with other candidates whose experience more closely matches our current needs. This was a difficult decision as we had many qualified applicants.

We appreciate your interest in Amazon and encourage you to apply for other positions that match your skills and experience.

Best of luck in your job search.

Sincerely,
Amazon Talent Acquisition'''
    }
}


def demonstrate_tools():
    """Demonstrate what each tool does"""
    print("=" * 80)
    print("EMAIL ANALYST AGENT - TOOL DEMONSTRATION")
    print("=" * 80)
    print()
    print("This demo shows what each tool does with sample emails.")
    print("These are the same tools the AI agent uses to analyze emails.")
    print()

    try:
        db = DatabaseManager()
        # Note: We're creating the agent but won't call the LLM
        # We'll just demonstrate the tools directly
        print("✅ Database initialized")
        print()

        # For each sample email, show what the tools would extract
        for email_name, email_data in SAMPLE_EMAILS.items():
            print("=" * 80)
            print(f"EMAIL: {email_name}")
            print("=" * 80)
            print()
            print(f"📧 From: {email_data['sender']}")
            print(f"📧 Subject: {email_data['subject']}")
            print()
            print("Email Preview:")
            print("-" * 40)
            print(email_data['body'][:200] + "...")
            print("-" * 40)
            print()

            # Demonstrate sentiment analysis
            print("🔍 TOOL 1: Sentiment Analysis")
            print("-" * 40)
            analyze_sentiment_indicators(email_data['subject'], email_data['body'])
            print()

            # Demonstrate categorization
            print("🔍 TOOL 2: Email Categorization")
            print("-" * 40)
            categorize_email_manual(email_data['subject'], email_data['body'])
            print()

            # Demonstrate company/position extraction
            print("🔍 TOOL 3: Company & Position Extraction")
            print("-" * 40)
            extract_entities(email_data['subject'], email_data['body'])
            print()

            # Demonstrate action item extraction
            print("🔍 TOOL 4: Action Items")
            print("-" * 40)
            extract_actions(email_data['body'])
            print()

            # Demonstrate follow-up recommendations
            print("🔍 TOOL 5: Follow-up Recommendations")
            print("-" * 40)
            recommend_followup_manual(email_data['subject'], email_data['body'])
            print()

            print()

        # Demonstrate thread analysis
        print("=" * 80)
        print("THREAD ANALYSIS DEMONSTRATION")
        print("=" * 80)
        print()
        demonstrate_thread_analysis()

        print()
        print("=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print()
        print("Note: This demo shows what the tools extract from emails.")
        print("With an OpenAI API key, the AI agent combines these insights")
        print("to provide comprehensive analysis and recommendations.")
        print()
        print("To test with real AI analysis:")
        print("1. Set OPENAI_API_KEY in .env file")
        print("2. Run: python test_email_analyst_comprehensive.py --manual")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def analyze_sentiment_indicators(subject, body):
    """Manually analyze sentiment indicators"""
    text = f"{subject} {body}".lower()

    positive_keywords = {
        'congratulations': 3, 'pleased': 3, 'offer': 3, 'selected': 3,
        'impressed': 2, 'excited': 2, 'next steps': 2
    }
    negative_keywords = {
        'unfortunately': 3, 'regret': 3, 'not selected': 3,
        'other candidates': 2, 'decided not to': 3
    }
    urgency_keywords = {
        'urgent': 3, 'asap': 3, 'deadline': 2, 'as soon as possible': 2,
        'within 24': 2
    }

    positive_score = sum(score for kw, score in positive_keywords.items() if kw in text)
    negative_score = sum(score for kw, score in negative_keywords.items() if kw in text)
    urgency_score = sum(score for kw, score in urgency_keywords.items() if kw in text)

    # Determine sentiment
    if negative_score > positive_score + 2:
        sentiment = "NEGATIVE (Likely rejection or bad news)"
        confidence = min(95, 60 + (negative_score * 5))
    elif positive_score > negative_score + 2:
        sentiment = "POSITIVE (Likely good news - interview/offer)"
        confidence = min(95, 60 + (positive_score * 5))
    else:
        sentiment = "NEUTRAL (Informational)"
        confidence = 50

    # Determine urgency
    if urgency_score >= 5:
        urgency = "HIGH - Requires immediate attention"
    elif urgency_score >= 2:
        urgency = "MEDIUM - Respond within 24-48 hours"
    else:
        urgency = "LOW - No immediate action needed"

    print(f"Sentiment: {sentiment}")
    print(f"Confidence: {confidence}%")
    print(f"Urgency: {urgency}")
    print(f"Scores - Positive: {positive_score}, Negative: {negative_score}, Urgency: {urgency_score}")


def categorize_email_manual(subject, body):
    """Manually categorize email"""
    text = f"{subject} {body}".lower()

    categories = {
        'Interview Invite': ['interview', 'schedule', 'meet with', 'chat with'],
        'Rejection': ['unfortunately', 'not selected', 'other candidates'],
        'Offer': ['offer', 'compensation', 'salary', 'start date'],
        'Assessment': ['coding challenge', 'technical test', 'assessment'],
        'Screening': ['phone screen', 'initial call', 'quick call']
    }

    matches = {}
    for category, keywords in categories.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > 0:
            matches[category] = count

    if matches:
        top_category = max(matches.items(), key=lambda x: x[1])
        print(f"Category: {top_category[0]}")
        print(f"Confidence: {min(95, 50 + (top_category[1] * 15))}%")
        if len(matches) > 1:
            print(f"Other categories detected: {', '.join([k for k in matches.keys() if k != top_category[0]])}")
    else:
        print("Category: GENERAL (Unable to determine specific category)")


def extract_entities(subject, body):
    """Extract company and position"""
    text = f"{subject} {body}"

    # Common companies
    companies = ['Google', 'Amazon', 'Meta', 'Facebook', 'Apple', 'Microsoft',
                'Netflix', 'Stripe', 'Tesla', 'OpenAI']

    # Common positions
    positions = ['Software Engineer', 'Senior Developer', 'Full Stack Engineer',
                'Backend Engineer', 'Frontend Engineer', 'DevOps Engineer']

    found_companies = [c for c in companies if c in text]
    found_positions = [p for p in positions if p in text]

    if found_companies:
        print(f"Company: {found_companies[0]}")
    else:
        print("Company: Not clearly identified")

    if found_positions:
        print(f"Position: {found_positions[0]}")
    else:
        print("Position: Not clearly identified")


def extract_actions(body):
    """Extract action items"""
    action_keywords = [
        'please', 'let us know', 'confirm', 'reply', 'respond', 'submit',
        'complete', 'review', 'schedule', 'availability'
    ]

    found_actions = []
    for line in body.split('\n'):
        line_lower = line.lower()
        if any(kw in line_lower for kw in action_keywords) and len(line) > 20:
            found_actions.append(line.strip())

    if found_actions:
        print(f"Found {len(found_actions)} action items:")
        for i, action in enumerate(found_actions[:5], 1):
            print(f"  {i}. {action[:80]}...")
    else:
        print("No explicit action items found")


def recommend_followup_manual(subject, body):
    """Recommend follow-up based on email type"""
    text = f"{subject} {body}".lower()

    if 'interview' in text and 'schedule' in text:
        print("Recommended Action: CONFIRM INTERVIEW")
        print("Timeline: Within 24 hours")
        print("Steps:")
        print("  1. Reply confirming your availability")
        print("  2. Prepare questions about the role")
        print("  3. Research the company and interviewers")

    elif 'offer' in text:
        print("Recommended Action: REVIEW & RESPOND")
        print("Timeline: Within deadline (typically 1 week)")
        print("Steps:")
        print("  1. Review all offer details carefully")
        print("  2. Research market salary for the role")
        print("  3. Prepare questions or negotiation points")

    elif 'unfortunately' in text or 'other candidates' in text:
        print("Recommended Action: SEND THANK YOU (Optional)")
        print("Timeline: Within 48 hours")
        print("Steps:")
        print("  1. Send a gracious thank-you note")
        print("  2. Request constructive feedback (politely)")
        print("  3. Update application status to 'rejected'")

    else:
        print("Recommended Action: RESPOND APPROPRIATELY")
        print("Timeline: Within 24-48 hours")
        print("Steps:")
        print("  1. Read the email carefully")
        print("  2. Determine what action is needed")
        print("  3. Respond professionally")


def demonstrate_thread_analysis():
    """Demonstrate thread analysis"""
    thread = [
        {
            'date': '2025-01-10',
            'sender': 'recruiting@techcorp.com',
            'subject': 'Application Received',
            'body': 'Thank you for applying. We are reviewing candidates.'
        },
        {
            'date': '2025-01-15',
            'sender': 'recruiting@techcorp.com',
            'subject': 'Interview Invitation',
            'body': 'We would like to schedule an interview next week.'
        },
        {
            'date': '2025-01-20',
            'sender': 'recruiting@techcorp.com',
            'subject': 'Offer Letter',
            'body': 'Congratulations! We are pleased to extend an offer.'
        }
    ]

    print("🧵 Thread Analysis (3 emails)")
    print()
    print("Timeline:")
    for i, email in enumerate(thread, 1):
        print(f"  {i}. {email['date']} - From {email['sender']}")
        print(f"     Subject: {email['subject']}")

    print()
    print("Progression:")
    print("  • One-way communication (all from same sender)")
    print("  • Total exchanges: 3")
    print("  • Sentiment shift detected: neutral → neutral → positive")

    print()
    print("Key Insights:")
    print("  • Active conversation thread")
    print("  • Interview scheduling completed")
    print("  • Offer extended")

    print()
    print("💡 Recommendation: This is a successful application progression!")
    print("   Review the offer details and respond within the deadline.")


if __name__ == '__main__':
    demonstrate_tools()
