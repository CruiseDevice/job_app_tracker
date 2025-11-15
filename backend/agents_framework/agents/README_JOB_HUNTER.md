# Job Hunter Agent

## Overview

The Job Hunter Agent is an AI-powered autonomous agent that helps users find and match job opportunities across multiple platforms. It uses a ReAct (Reasoning-Acting) pattern to search, analyze, and recommend jobs based on user preferences.

## Features

### 1. Multi-Platform Job Search
- **LinkedIn**: Search jobs with filters for experience level and job type
- **Indeed**: Search with salary filters and location preferences
- **Glassdoor**: Search with company rating filters

### 2. Intelligent Job Matching
- **Match Score Calculation**: 0-100 score based on multiple factors:
  - Title Match (30 points): How well the job title matches preferred roles
  - Location Match (20 points): Alignment with preferred locations
  - Salary Match (20 points): Meets minimum salary requirements
  - Skills Match (15 points): Percentage of user skills mentioned in job
  - Experience Match (10 points): Matches experience level
  - Benefits Match (5 points): Includes required benefits
  - Company Rating Bonus (10 points): High-rated companies

### 3. Company Research
- Company information (size, industry, founded)
- Employee ratings and reviews
- Culture and values
- Pros and cons from employees
- CEO rating and employee satisfaction
- Funding and investors
- Recent news and developments
- Tech stack information
- Interview process details

### 4. Job Details Extraction
- Experience requirements
- Education requirements
- Tech stack and skills
- Benefits and perks
- Responsibilities

### 5. User Preference Management
- Preferred job titles and roles
- Location preferences
- Salary expectations
- Required skills
- Work authorization
- Remote/hybrid preferences
- Required benefits

## Architecture

### Tools (8 total)

1. **search_linkedin_jobs**: Search LinkedIn for jobs
2. **search_indeed_jobs**: Search Indeed with salary filters
3. **search_glassdoor_jobs**: Search Glassdoor with rating filters
4. **extract_job_details**: Extract structured data from job descriptions
5. **get_user_preferences**: Retrieve user job search preferences
6. **calculate_job_match_score**: Calculate match score and breakdown
7. **research_company**: Get comprehensive company information
8. **save_job_recommendation**: Save high-quality job matches

### Configuration

```python
AgentConfig(
    agent_name="job_hunter",
    model="gpt-4o-mini",
    temperature=0.3,  # Lower for focused searches
    max_iterations=15,
    enable_memory=True
)
```

## API Endpoints

### 1. Search Jobs
**POST** `/api/agents/job-hunter/search`

Search for jobs across multiple platforms.

**Request:**
```json
{
  "keywords": "Software Engineer",
  "location": "San Francisco, CA",
  "platforms": ["LinkedIn", "Indeed", "Glassdoor"],
  "filters": {
    "experience_level": "Mid-Senior level",
    "job_type": "Full-time",
    "salary_min": 120
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": "Found 15 jobs matching your criteria...",
  "metadata": {
    "total_jobs": 15,
    "avg_match_score": 78,
    "top_companies": ["Company A", "Company B"]
  }
}
```

### 2. Get Recommendations
**POST** `/api/agents/job-hunter/recommendations`

Get personalized job recommendations.

**Request:**
```json
{
  "user_id": 1,
  "limit": 10
}
```

**Response:**
```json
{
  "success": true,
  "analysis": "Based on your profile, here are the top 10 recommendations...",
  "metadata": {
    "recommendations": [...],
    "avg_match_score": 85
  }
}
```

### 3. Get Agent Stats
**GET** `/api/agents/job-hunter/stats`

Get agent statistics and performance metrics.

### 4. WebSocket Endpoint
**WS** `/api/agents/job-hunter/ws`

Real-time job search and recommendations.

**Message Types:**
- `search`: Search for jobs
- `recommendations`: Get personalized recommendations
- `ping`: Heartbeat

## Frontend Components

### 1. JobHunterDashboard
Main dashboard component with two modes:
- **Search Mode**: Manual job search with filters
- **Recommendations Mode**: AI-curated personalized recommendations

### 2. JobCard
Individual job listing card with:
- Job details (title, company, location, salary)
- Match score badge
- Expandable details
- Company research panel
- Action buttons (Save, Apply, View)

### 3. MatchScoreBadge
Visual representation of match score:
- Color-coded based on score (green 80+, blue 60+, yellow 40+)
- Match level label (Excellent, Good, Fair, Poor)
- Progress bar visualization

### 4. JobFilters
Search filter component:
- Keywords input
- Location input
- Platform checkboxes
- Experience level selector
- Job type selector
- Minimum salary input

### 5. CompanyResearch
Comprehensive company information panel:
- Company stats (size, founded, funding)
- Employee ratings and reviews
- Culture and values
- Pros and cons
- Recent news
- Key investors
- Interview difficulty

## Usage Examples

### Backend Usage

```python
from agents_framework.agents.job_hunter_agent import create_job_hunter_agent
from database.database_manager import DatabaseManager

# Create agent
db = DatabaseManager()
agent = create_job_hunter_agent(db)

# Search for jobs
result = await agent.search_jobs(
    keywords="Software Engineer",
    location="San Francisco, CA",
    platforms=["LinkedIn", "Indeed"],
    filters={
        "experience_level": "Mid-Senior level",
        "salary_min": 120
    }
)

# Get personalized recommendations
recommendations = await agent.get_recommendations(
    user_id=1,
    limit=10
)
```

### Frontend Usage

```tsx
import JobHunterDashboard from './components/Agents/JobHunter/JobHunterDashboard';

function App() {
  return <JobHunterDashboard />;
}
```

## Match Score Algorithm

The match score is calculated based on weighted factors:

1. **Title Match (30%)**:
   - Exact match: 30 points
   - Partial match: 15 points

2. **Location Match (20%)**:
   - Exact match: 20 points

3. **Salary Match (20%)**:
   - Meets minimum: 20 points
   - Within 80% of minimum: 10 points

4. **Skills Match (15%)**:
   - Percentage of user skills in job description

5. **Experience Match (10%)**:
   - Matches experience level: 10 points

6. **Benefits Match (5%)**:
   - Percentage of required benefits offered

7. **Company Rating Bonus (10%)**:
   - 4.0+ rating: 10 points
   - 3.5-4.0 rating: 5 points

**Match Levels:**
- 80-100: Excellent Match
- 60-79: Good Match
- 40-59: Fair Match
- 0-39: Poor Match

## Testing

### Unit Tests
Run unit tests (requires pytest):
```bash
pytest backend/tests/test_job_hunter_agent.py -v
```

### Test Coverage
- Tool registration and functionality
- Job search across platforms
- Match score calculation
- Company research
- User preferences
- Job details extraction
- Recommendation saving
- Edge cases and error handling

## Future Enhancements

1. **Real Job Board Integration**
   - Actual LinkedIn API integration
   - Indeed API integration
   - Glassdoor scraping

2. **Advanced Matching**
   - Machine learning-based scoring
   - Collaborative filtering
   - Success rate tracking

3. **Application Tracking**
   - Auto-apply functionality
   - Application status tracking
   - Interview scheduling

4. **Salary Intelligence**
   - Market salary analysis
   - Negotiation recommendations
   - Total compensation calculator

5. **Network Analysis**
   - LinkedIn connection analysis
   - Referral opportunities
   - Company insider connections

## Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_api_key_here
JOB_HUNTER_MODEL=gpt-4o-mini
JOB_HUNTER_TEMPERATURE=0.3
JOB_HUNTER_MAX_ITERATIONS=15
```

### User Preferences Schema
```python
{
    "user_id": int,
    "preferred_roles": List[str],
    "preferred_locations": List[str],
    "preferred_industries": List[str],
    "salary_min": int,
    "salary_max": int,
    "job_type": List[str],
    "experience_level": str,
    "required_benefits": List[str],
    "skills": List[str],
    "years_experience": int,
    "education": str,
    "work_authorization": str,
    "willing_to_relocate": bool,
    "remote_preference": str
}
```

## Troubleshooting

### Common Issues

1. **No jobs found**: Check keywords and filters are not too restrictive
2. **Low match scores**: Review and update user preferences
3. **API errors**: Verify OpenAI API key is configured
4. **Timeout errors**: Reduce max_iterations or simplify search criteria

## Performance

- Average search time: 5-10 seconds
- Recommendations generation: 10-15 seconds
- Company research: 1-2 seconds per company
- Match score calculation: <1 second

## Dependencies

```
langchain>=0.1.0
langchain-openai>=0.0.5
langgraph>=0.0.20
chromadb>=0.4.0  # For memory/RAG
```

## License

Part of the Job Application Tracker project.
