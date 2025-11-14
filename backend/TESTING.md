# Email Analyst Agent Testing Guide

This guide explains how to test the Email Analyst Agent with various approaches.

## Test Files

1. **`test_email_analyst.py`** - Original interactive test suite
   - Full test suite with 5 sample emails
   - Quick test mode
   - Requires OPENAI_API_KEY

2. **`test_email_analyst_comprehensive.py`** - Complete test suite
   - Unit tests (no API key required)
   - Mock tests (no API key required)
   - Integration tests (requires API key)
   - Thread analysis tests
   - Uses unittest framework

3. **`test_email_analyst_demo.py`** - Tool demonstration
   - Shows what each tool does
   - No API key required
   - Great for understanding agent capabilities

## Quick Start

### 1. Set Up Environment (Optional for Unit Tests)

```bash
# Copy example env file
cp .env.example .env

# Add your OpenAI API key to .env
# OPENAI_API_KEY=sk-...
```

### 2. Run Tests

#### Run All Unit Tests (No API Key Required)
```bash
cd backend
python test_email_analyst_comprehensive.py --unit
```

#### Run Tool Demonstration (No API Key Required)
```bash
cd backend
python test_email_analyst_demo.py
```

#### Run Integration Tests (Requires API Key)
```bash
cd backend
python test_email_analyst_comprehensive.py --integration
```

#### Run All Tests
```bash
cd backend
python test_email_analyst_comprehensive.py --all
```

#### Run Original Interactive Test Suite
```bash
cd backend
python test_email_analyst.py

# Or quick test mode
python test_email_analyst.py --quick
```

## Test Coverage

### Unit Tests (8 tests)
These tests validate individual tool logic without making API calls:

- ✅ Sentiment analysis (positive/negative detection)
- ✅ Action item extraction
- ✅ Email categorization
- ✅ Company name extraction
- ✅ Agent initialization
- ✅ Tool registration
- ✅ Thread data formatting

**Status**: ✅ All passing

### Integration Tests (5 tests)
These tests make real API calls to OpenAI:

- Analyze interview invitation email
- Analyze rejection email
- Analyze job offer email
- Analyze email thread
- Get agent statistics

**Requires**: OPENAI_API_KEY environment variable

### Demo Tests
Interactive demonstration of all 7 agent tools:

1. **Sentiment Analysis** - Detects tone and urgency
2. **Email Categorization** - Identifies email type
3. **Company & Position Extraction** - Finds entities
4. **Action Items** - Extracts tasks and deadlines
5. **Follow-up Recommendations** - Suggests next steps
6. **Application Matching** - Finds related jobs
7. **Thread Analysis** - Analyzes conversation flow

## Sample Test Data

The test suite includes realistic job-related emails:

1. **Interview Invitation** (Google) - Positive, urgent
2. **Job Offer** (Meta) - Very positive, time-sensitive
3. **Rejection** (Amazon) - Negative, informational
4. **Technical Assessment** (Stripe) - Neutral, action required
5. **Phone Screen** (Netflix) - Positive, scheduled

Plus a 3-email conversation thread demonstrating progression analysis.

## Test Results Example

```
Running unit tests...
test_action_item_extraction ... ok
test_company_extraction ... ok
test_email_categorization ... ok
test_sentiment_analysis_negative ... ok
test_sentiment_analysis_positive ... ok
test_agent_has_all_tools ... ok
test_agent_initialization ... ok
test_thread_data_formatting ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.382s

OK
```

## Testing with Real Emails

To test with your own emails:

1. Set OPENAI_API_KEY in .env
2. Modify sample emails in test files
3. Run: `python test_email_analyst.py`

Or use the API:

```python
import asyncio
from database.database_manager import DatabaseManager
from agents_framework.agents.email_analyst_agent import create_email_analyst_agent

async def test_my_email():
    db = DatabaseManager()
    agent = create_email_analyst_agent(db)

    result = await agent.analyze_email(
        subject="Your email subject",
        body="Your email body",
        sender="sender@example.com"
    )

    print(result['analysis'])

asyncio.run(test_my_email())
```

## API Testing

Test the REST API endpoints:

```bash
# Start the backend
cd backend
python main.py

# In another terminal, test the API
curl -X POST http://localhost:8000/api/agents/email-analyst/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Interview Invitation",
    "body": "We would like to schedule an interview...",
    "sender": "recruiting@company.com"
  }'
```

Or visit http://localhost:8000/docs for interactive API documentation.

## Frontend Testing

The frontend components can be tested by:

1. Starting the backend: `cd backend && python main.py`
2. Starting the frontend: `cd frontend && npm run dev`
3. Navigating to the EmailAnalystDashboard component
4. Using the sample email loader or pasting real emails

## Performance Testing

The comprehensive test suite tracks:
- Execution time per test
- Agent response time
- Tool execution counts
- Memory usage

## Troubleshooting

### "OPENAI_API_KEY not set"
- This is expected for unit tests and demo
- For integration tests, add your key to .env

### "ChromaDB warnings"
- ChromaDB uses default embeddings when API key is missing
- This is normal for unit tests

### Import errors
- Ensure you're in the backend directory
- The tests add the parent directory to sys.path

### Database errors
- The tests use an in-memory SQLite database
- No setup required

## CI/CD Integration

For continuous integration:

```yaml
# .github/workflows/test.yml
- name: Run unit tests
  run: |
    cd backend
    python test_email_analyst_comprehensive.py --unit
```

Unit tests run fast (~0.4s) and don't require API keys, making them perfect for CI.

## Next Steps

After testing the Email Analyst Agent:

1. ✅ Phase 2 complete - Email Analyst Agent tested
2. 📋 Phase 3 - Build Application Manager Agent
3. 📋 Phase 4 - Build Follow-up Agent
4. 📋 And 6 more specialized agents...

For questions or issues, check the main README or create an issue.
