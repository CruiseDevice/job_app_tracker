# Job Application Tracker - Agent Architecture Summary

## Overview
The system uses a sophisticated AI agent framework built on LangChain/LangGraph with specialized agents for different tasks. Each agent is autonomous, has tools for specific operations, manages conversation memory, and can learn from experiences using RAG (Retrieval Augmented Generation).

---

## 1. AGENT ARCHITECTURE & BASE CLASSES

### 1.1 BaseAgent Class (`backend/agents_framework/core/base_agent.py`)

**Core Structure:**
```
BaseAgent (Abstract Base Class)
├── Config: AgentConfig (name, description, model, temperature, max_iterations, etc.)
├── LLM: ChatOpenAI instance (gpt-4o-mini by default, temp=0.1 for analysis)
├── Tools: List of registered tools
├── Memory: Conversation history (LangChain messages)
├── Executor: LangGraph compiled ReAct agent
└── Tracking: tokens used, cost, execution count
```

**Key Components:**

1. **AgentConfig**: Configuration object
   - `name`: Agent identifier
   - `description`: Agent purpose
   - `model`: "gpt-4o-mini" (can be customized)
   - `temperature`: 0.1 for analytical tasks, 0.3 for creative
   - `max_iterations`: 8-10
   - `enable_memory`: True/False
   - `memory_k`: Number of messages to keep (10-20)

2. **AgentResponse**: Standardized response object
   - `output`: Main result string
   - `agent_name`: Which agent produced it
   - `success`: Boolean status
   - `intermediate_steps`: List of tool calls
   - `metadata`: Additional context
   - `error`: Error message if failed
   - `timestamp`: When response was generated

3. **Core Methods:**
   ```python
   @abstractmethod
   def _register_tools(self) -> None
       # Subclasses must implement - register all tools here
   
   @abstractmethod
   def get_system_prompt(self) -> str
       # Subclasses must implement - define agent's role/capabilities
   
   async def run(input_text: str, context: Optional[Dict]) -> AgentResponse
       # Main execution method - async
       # Takes input and optional context
       # Returns AgentResponse with results
   
   def add_tool(name, func, description, return_direct=False) -> None
       # Helper to register individual tools
       # Tools are wrapped with @tool decorator automatically
   ```

**Memory Management:**
- `conversation_history`: LangChain messages (HumanMessage, AIMessage, SystemMessage)
- `add_message_to_memory()`: Store messages
- `get_memory_context()`: Get last N conversations as string
- `clear_memory()`: Reset conversation history
- Automatic trimming when exceeds memory_k * 2

**Statistics:**
- `get_stats()`: Returns dict with execution_count, tools_count, memory_size, etc.

---

## 2. EXISTING AGENTS STRUCTURE

### 2.1 Email Analyst Agent (`backend/agents_framework/agents/email_analyst_agent.py`)

**Configuration:**
```python
config = AgentConfig(
    name="Email Analyst",
    description="Analyzes job-related emails...",
    model="gpt-4o-mini",
    temperature=0.1,  # Low temp - analytical
    max_iterations=8,
    enable_memory=True,
    memory_k=15
)
```

**Tools Registered (7 total):**
1. `analyze_email_sentiment` - Detects sentiment (positive/negative/neutral), urgency
2. `extract_action_items` - Extracts tasks and deadlines using regex patterns
3. `categorize_email` - Classifies email type (interview, rejection, offer, assessment, etc.)
4. `extract_company_position` - Extracts company name and job position
5. `find_matching_applications` - Searches database for related applications
6. `recommend_followup` - Suggests appropriate follow-up actions based on category
7. `analyze_email_thread` - Analyzes multi-email conversations for progression

**Memory System:**
- `conversation_memory`: AgentMemoryManager instance
- `rag_memory`: RAGMemoryManager for semantic storage (ChromaDB)
- Stores analyses in RAG for learning

**Public Methods:**
```python
async def analyze_email(subject, body, sender="", metadata=None) -> Dict
    # Analyzes single email
    # Returns: success, analysis, metadata, error

async def analyze_thread(emails: List[Dict], metadata=None) -> Dict
    # Analyzes email conversation thread
    # Returns: success, analysis, email_count, metadata, error
```

**System Prompt Focus:**
- Reasoning and analysis
- Using tools systematically
- Extracting actionable insights
- Understanding context and patterns

### 2.2 Follow-up Agent (`backend/agents_framework/agents/followup_agent.py`)

**Configuration:**
```python
config = AgentConfig(
    name="Follow-up Agent",
    description="Manages follow-up communications...",
    model="gpt-4o-mini",
    temperature=0.3,  # Higher - creative message drafting
    max_iterations=10,
    enable_memory=True,
    memory_k=20
)
```

**Tools Registered (7 total):**
1. `calculate_optimal_timing` - Recommends when to follow up (based on status & days)
2. `draft_followup_message` - Creates personalized email messages
3. `get_followup_schedule` - Retrieves past/upcoming follow-ups for a job
4. `analyze_response_patterns` - Analyzes historical success rates by timing/type
5. `suggest_followup_strategy` - Recommends complete multi-step follow-up plan
6. `track_followup_performance` - Tracks engagement metrics (opened, clicked, responded)
7. `get_followup_templates` - Returns proven message templates with effectiveness ratings

**Timing Rules (Built-in):**
```
Status: applied → 5-7 day wait
Status: interview → 1-3 days (post-interview)
Status: assessment → 1-2 days (confirm receipt)
Status: offer → 0-1 day (respond immediately)
Status: rejected → 1-3 days (thank you & feedback)
```

**Public Methods:**
```python
async def optimize_followup_timing(job_id, status, days_since_contact, 
                                   application_date, metadata=None) -> Dict
    # Returns: success, recommendations, metadata, error

async def draft_followup(followup_type, company, position, tone="professional",
                         context_notes="", metadata=None) -> Dict
    # Returns: success, message, metadata, error

async def analyze_strategy(status, days_since_application, response_history,
                          priority="medium", metadata=None) -> Dict
    # Returns: success, strategy, metadata, error
```

---

## 3. TOOL SYSTEM IMPLEMENTATION

### 3.1 Tool Registration Pattern

**Each agent registers tools by:**
1. Defining functions with docstrings (docstring = tool description)
2. Using `self.add_tool(name, func, description, return_direct=False)`
3. Tools are wrapped with `@tool` decorator automatically

**Example Pattern:**
```python
def _register_tools(self) -> None:
    # Tool 1: Sentiment Analysis
    def analyze_sentiment(email_text: str) -> str:
        """Docstring explains what tool does"""
        try:
            # Implementation
            return formatted_result
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {str(e)}"
    
    self.add_tool(
        name="analyze_sentiment",
        func=analyze_sentiment,
        description="Clear description of tool functionality",
        return_direct=False  # False = tool output goes back to LLM for reasoning
    )
```

### 3.2 Tool Architecture

**Tool Execution Flow:**
1. Agent receives input → Creates prompt with tool descriptions
2. LLM decides which tools to use (ReAct pattern)
3. Tools execute → Return formatted string results
4. Results fed back to LLM for reasoning
5. LLM provides final answer or calls more tools

**Tool Characteristics:**
- Pure Python functions (no external dependencies needed)
- Single string input, string output
- Self-contained error handling
- Logging of operations
- Clear, formatted output for LLM comprehension

### 3.3 Base Tools (`backend/agents_framework/tools/base_tools.py`)

**Tool Classes (Reusable):**
- `DatabaseTools`: get_all_applications, get_by_id, update_status, search_applications
- `EmailTools`: analyze_sentiment, extract_action_items
- `AnalyticsTools`: get_application_statistics
- `UtilityTools`: get_current_datetime, calculate_days_since

**Legacy Support:**
- Tools can be created as LangChain `Tool` objects
- or using `@tool` decorator (preferred for new agents)

---

## 4. API ENDPOINT PATTERNS

### 4.1 Route Structure (`backend/api/routes/agents.py`)

**Pattern - Email Analyst Endpoints:**

```
POST /api/agents/email-analyst/analyze
├── Request: EmailAnalysisRequest (subject, body, sender, metadata)
├── Process: Create agent → Call agent.analyze_email()
└── Response: EmailAnalysisResponse (success, analysis, metadata, error)

POST /api/agents/email-analyst/analyze-thread
├── Request: EmailThreadAnalysisRequest (emails: List, metadata)
├── Process: Validate → Create agent → Call agent.analyze_thread()
└── Response: EmailThreadAnalysisResponse (success, analysis, email_count, metadata, error)

GET /api/agents/email-analyst/stats
├── Process: Create agent → Call agent.get_stats()
└── Response: AgentStatsResponse (name, execution_count, tools_count, memory_size)

WebSocket /api/agents/email-analyst/ws
├── Message Types:
│   ├── "analyze" → Single email analysis
│   ├── "analyze_thread" → Thread analysis
│   ├── "ping" → Heartbeat
│   └── Response: "analysis_started", "analysis_complete", "analysis_error"
```

**Pattern - Follow-up Agent Endpoints:**

```
POST /api/agents/followup-agent/optimize-timing
├── Request: FollowUpTimingRequest (job_id, status, days_since_contact, application_date)
└── Response: FollowUpResponse (success, output, metadata, error)

POST /api/agents/followup-agent/draft-message
├── Request: FollowUpDraftRequest (followup_type, company, position, tone, context_notes)
└── Response: FollowUpResponse (success, output, metadata, error)

POST /api/agents/followup-agent/analyze-strategy
├── Request: FollowUpStrategyRequest (status, days_since_application, response_history, priority)
└── Response: FollowUpResponse (success, output, metadata, error)

GET /api/agents/followup-agent/stats
└── Response: AgentStatsResponse

WebSocket /api/agents/followup-agent/ws
├── Message Types: "optimize_timing", "draft_message", "analyze_strategy", "ping"
```

### 4.2 Request/Response Models (Pydantic)

**Pattern:**
```python
from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    field1: str = Field(..., description="Description")
    field2: Optional[str] = Field(None, description="Optional")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field1": "value1",
                "field2": "value2"
            }
        }

class AgentResponse(BaseModel):
    success: bool
    output: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### 4.3 WebSocket Pattern

**Connection Flow:**
1. Client connects → Server accepts WebSocket
2. Client sends JSON message with type and data
3. Server sends acknowledgment ("*_started")
4. Server sends result ("*_complete") or error ("*_error")
5. Client processes result
6. Continue or close

**Error Handling:**
- Try/catch around tool execution
- Return HTTP 500 with detail message for REST
- Send error JSON for WebSocket
- Logging at each stage

---

## 5. MEMORY SYSTEMS

### 5.1 Conversation Memory (`backend/agents_framework/memory/agent_memory.py`)

**ConversationMemory Class:**
- Stores: HumanMessage, AIMessage, SystemMessage with timestamps
- Max size: Keep last N messages (prevents context overflow)
- Methods: add_message, get_messages, get_langchain_messages, get_context_string
- Export: export_history as List[Dict]

**AgentMemoryManager Class:**
- Wraps both conversation and semantic memory
- `add_interaction()`: Store human + AI pair
- `store_learning()`: Save insights in semantic memory
- `retrieve_relevant_memories()`: Semantic search
- `get_full_stats()`: Combined memory statistics

### 5.2 Semantic/RAG Memory (`backend/agents_framework/memory/vector_memory.py`)

**RAGMemoryManager:**
- Uses ChromaDB for vector storage and semantic search
- Stores: Experience data with embeddings
- Methods: store_experience, retrieve_relevant, get_stats
- Persists to: `./data/chroma` directory

**Agent Usage:**
```python
self.rag_memory.store_experience(
    experience="What I learned from this...",
    category="email_analysis",  # For filtering
    tags=["company", "context"]  # For search
)

memories = self.rag_memory.retrieve_relevant(
    query="Similar past analysis?",
    category="email_analysis",
    limit=5
)
```

---

## 6. FRONTEND UI STRUCTURE

### 6.1 Dashboard Component Pattern

**Agent Dashboard Layout:**
```
Dashboard Component
├── Header (Title, Description, Stats Overview)
├── Main Content Grid (2 columns: Input + Output)
│   ├── Left Column (Input Section)
│   │   ├── Form with input fields
│   │   ├── Error display
│   │   └── Action buttons
│   └── Right Column (Results Section)
│       ├── No results placeholder (dashed border)
│       └── Results card (when available)
└── Additional Sections (Stats, Guidelines, Tips)
```

### 6.2 Components (`frontend/src/components/Agents/`)

**Email Analyst Components:**
- `EmailAnalystDashboard.tsx`: Main dashboard
- `EmailAnalysisCard.tsx`: Results display
- `SentimentBadge.tsx`: Sentiment indicator
- `FollowupRecommendations.tsx`: Suggested actions
- `ActionItemsList.tsx`: Extracted tasks

**Follow-up Components:**
- `FollowUpAgentDashboard.tsx`: Main dashboard with tabs
- `TimingOptimizerCard.tsx`: Timing analysis
- `MessageDrafterCard.tsx`: Message composition
- `StrategyPlannerCard.tsx`: Strategy recommendations
- `FollowUpScheduleCard.tsx`: Schedule management

### 6.3 Common Patterns

**State Management:**
```typescript
const [data, setData] = useState<Type>(initialValue);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

**API Calls:**
```typescript
const handleSubmit = async () => {
  setLoading(true);
  setError(null);
  
  try {
    const response = await fetch('endpoint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) throw new Error('Failed');
    const result = await response.json();
    setData(result);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

**UI Components Used:**
- Tailwind CSS for styling
- Grid layouts for responsive design
- Conditional rendering for states
- Loading spinners during API calls
- Error boundaries for crashes

---

## 7. TESTING PATTERNS

### 7.1 Test Structure (`backend/tests/` and `backend/test_*.py`)

**Test Levels:**

1. **Unit Tests** (No API calls)
   - Test individual tool logic
   - Test data parsing/formatting
   - Mock dependencies
   - Use: `unittest.TestCase`

2. **Mock Integration Tests** (No API calls)
   - Test agent initialization
   - Test tool registration
   - Mock LLM responses
   - Use: `@patch('ChatOpenAI')`

3. **Integration Tests** (Requires OPENAI_API_KEY)
   - Real agent execution
   - Real LLM calls
   - Real database access
   - Use: `@unittest.skipUnless(os.getenv('OPENAI_API_KEY'))`

4. **Manual/Demonstration Tests**
   - Print formatted output for inspection
   - Show agent in action
   - Verify user-facing quality

### 7.2 Example Test Class Pattern

```python
class TestFollowUpAgent(unittest.IsolatedAsyncioTestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.has_api_key = bool(os.getenv('OPENAI_API_KEY'))
    
    def setUp(self):
        self.db = DatabaseManager()
        if self.has_api_key:
            self.agent = create_followup_agent(self.db)
    
    @unittest.skipUnless(os.getenv('OPENAI_API_KEY'), "Requires API key")
    async def test_specific_feature(self):
        result = await self.agent.method(params)
        
        self.assertTrue(result['success'])
        self.assertIn('expected_text', result['output'].lower())
        self.assertEqual(result['email_count'], expected_count)
```

### 7.3 Test Coverage

**Email Analyst Tests:**
- Sentiment detection (positive/negative/neutral)
- Action item extraction
- Email categorization
- Company/position extraction
- Thread analysis
- Agent statistics

**Follow-up Agent Tests:**
- Timing optimization (by status)
- Message drafting (by type)
- Tone variations
- Strategy planning (by response history)
- Priority adjustments
- Error handling
- Performance (response time < 30s)

---

## 8. DEPLOYMENT & RUNNING

### 8.1 Starting the Backend

```bash
cd backend
python main.py
# Runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### 8.2 Running Tests

```bash
# Unit + Mock tests (no API key needed)
python tests/test_followup_agent.py

# Full test suite with API (requires .env file)
python -m pytest backend/tests/ -v

# Specific test
python test_email_analyst_comprehensive.py --manual
```

---

## 9. KEY ARCHITECTURAL DECISIONS

1. **Agent Pattern**: BaseAgent provides framework, subclasses specialize
2. **Tool System**: Pure Python functions, string I/O, self-contained
3. **Memory**: Dual system (conversation + RAG) for learning
4. **API**: FastAPI with Pydantic models, WebSocket support
5. **Frontend**: React + TypeScript with Tailwind, component-driven
6. **Testing**: Multiple levels from unit to integration
7. **Configuration**: AgentConfig allows customization per agent
8. **Error Handling**: Try/catch in tools, logging throughout, user-friendly responses

---

## 10. IMPLEMENTATION CHECKLIST FOR RESUME WRITER AGENT

When implementing the Resume Writer Agent, follow:

1. **Create Agent Class**
   - Inherit from BaseAgent
   - Create AgentConfig (model, temperature, iterations)
   - Implement _register_tools()
   - Implement get_system_prompt()

2. **Register Tools**
   - Extract resume sections (contact, summary, experience, etc.)
   - Tailor resume to job description
   - Check for ATS compatibility
   - Suggest improvements
   - Generate cover letter intro
   - Format/export options

3. **Add Memory**
   - ConversationMemory for context
   - RAGMemory for storing templates/feedback

4. **Create API Routes**
   - POST /api/agents/resume-writer/analyze
   - POST /api/agents/resume-writer/tailor
   - POST /api/agents/resume-writer/improve
   - WebSocket /api/agents/resume-writer/ws
   - GET /api/agents/resume-writer/stats

5. **Create Frontend Components**
   - ResumeWriterDashboard (main layout)
   - ResumeInputCard (upload/paste resume)
   - JobDescriptionCard (paste job description)
   - AnalysisCard (display results)
   - TailorCard (customize for specific job)

6. **Write Tests**
   - Unit tests for tool logic
   - Mock tests for agent behavior
   - Integration tests (if API available)
   - Manual demonstration tests

7. **Update Exports**
   - Add to `agents/__init__.py`
   - Include create_resume_writer_agent factory

