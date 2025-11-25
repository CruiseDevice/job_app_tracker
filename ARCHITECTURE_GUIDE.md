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

**Monitoring Integration:**
- `performance_monitor`: Global performance monitor for tracking execution metrics
- `cost_tracker`: Global cost tracker for API usage and costs
- Structured logging with correlation IDs and execution tracking

---

## 2. EXISTING AGENTS STRUCTURE

### 2.1 Current Status

**No specialized agents are currently implemented.** The `backend/agents_framework/agents/` directory contains only the `__init__.py` file, which states that agents can be added as they are developed.

**Framework Ready:**
- BaseAgent class is fully implemented and ready for use
- Tool system is functional with reusable base tools
- Memory systems (conversation + RAG) are available
- Monitoring and cost tracking systems are integrated

**To Create a New Agent:**
1. Create a new file in `backend/agents_framework/agents/`
2. Inherit from `BaseAgent`
3. Implement `_register_tools()` and `get_system_prompt()`
4. Add the agent to `agents/__init__.py` exports

**Example Agent Structure:**
```python
from agents_framework.core.base_agent import BaseAgent, AgentConfig

class MyCustomAgent(BaseAgent):
    def __init__(self, db_manager):
        config = AgentConfig(
            name="My Agent",
            description="Does something useful",
            model="gpt-4o-mini",
            temperature=0.1,
            max_iterations=10,
            enable_memory=True,
            memory_k=15
        )
        self.db = db_manager
        super().__init__(config)
    
    def _register_tools(self) -> None:
        # Register tools here
        pass
    
    def get_system_prompt(self) -> str:
        return "You are a helpful agent that..."
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

**Tool Creation:**
- `create_standard_toolset()`: Factory function to create a standard set of tools
- Tools can be created as LangChain `Tool` objects (legacy)
- Preferred: Use `@tool` decorator via `BaseAgent.add_tool()` method

**Note:** The base_tools.py uses the legacy LangChain `Tool` API. New agents should use the `@tool` decorator approach through `BaseAgent.add_tool()` for better compatibility with LangGraph.

---

## 4. API ENDPOINT PATTERNS

### 4.1 Route Structure (`backend/api/routes/agents.py`)

**Current Status:**
The `agents.py` route file exists but is currently a placeholder. It contains:
- Basic router setup
- `AgentStatsResponse` model definition
- Comments indicating where future agent endpoints can be added

**Pattern for Future Agent Endpoints:**

When implementing agent endpoints, follow this structure:

```
POST /api/agents/{agent-name}/{action}
├── Request: AgentRequest (Pydantic model with required fields)
├── Process: Create agent → Call agent method
└── Response: AgentResponse (success, output, metadata, error)

GET /api/agents/{agent-name}/stats
├── Process: Create agent → Call agent.get_stats()
└── Response: AgentStatsResponse (name, execution_count, tools_count, memory_size)

WebSocket /api/agents/{agent-name}/ws
├── Message Types:
│   ├── "{action}" → Execute agent action
│   ├── "ping" → Heartbeat
│   └── Response: "{action}_started", "{action}_complete", "{action}_error"
```

**Example Implementation Pattern:**
```python
@router.post("/{agent_name}/run")
async def run_agent(
    agent_name: str,
    request: AgentRequest,
    db: DatabaseManager = Depends(get_db)
):
    # Create agent instance
    agent = create_agent(agent_name, db)
    
    # Run agent
    response = await agent.run(request.input_text, request.context)
    
    # Return response
    return AgentResponse(
        success=response.success,
        output=response.output,
        metadata=response.metadata,
        error=response.error
    )
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
- Methods: `store_experience()`, `retrieve_similar()`, `get_context_for_query()`, `get_stats()`
- Persists to: `./data/chroma` directory

**VectorMemoryStore:**
- Low-level vector storage interface
- Methods: `add()`, `search()`, `get()`, `delete()`, `count()`
- Supports metadata filtering and batch operations

**Agent Usage:**
```python
# Initialize RAG memory
from agents_framework.memory.vector_memory import RAGMemoryManager

self.rag_memory = RAGMemoryManager(agent_name="MyAgent")

# Store experiences
self.rag_memory.store_experience(
    experience="What I learned from this...",
    category="analysis",  # For filtering
    tags=["company", "context"],  # For search
    metadata={"key": "value"}
)

# Retrieve similar memories
memories = self.rag_memory.retrieve_similar(
    query="Similar past analysis?",
    category="analysis",
    limit=5
)

# Get formatted context
context = self.rag_memory.get_context_for_query(
    query="What did I learn?",
    category="analysis",
    limit=3
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

### 6.2 Components (`frontend/src/components/`)

**Current Frontend Structure:**
- `Applications/`: Application management components
- `Dashboard/`: Main dashboard and statistics
- `Layout/`: Layout wrapper components
- `Matching/`: Email-job matching components
- `Settings/`: Settings and configuration
- `common/`: Shared UI components (Loading, ErrorBoundary, etc.)

**Note:** No `Agents/` directory currently exists. When implementing agent UIs, create components following the dashboard pattern described above.

**Example Agent Component Structure (for future implementation):**
```
Agents/
├── {AgentName}Dashboard.tsx    # Main dashboard
├── {AgentName}InputCard.tsx     # Input form
├── {AgentName}ResultsCard.tsx   # Results display
└── {AgentName}StatsCard.tsx     # Statistics display
```

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

### 7.2 Test Coverage

**Current Test Files:**
- `test_email_job_matching.py`: Tests for email-job matching functionality
- `test_phase10_integration.py`: Integration tests for Phase 10 features

**Test Coverage for Future Agents:**
When implementing agents, create tests covering:
- Agent initialization and configuration
- Tool registration and execution
- Memory management (conversation + RAG)
- Error handling and edge cases
- Agent statistics and monitoring
- Integration with database and external services

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
# Full test suite (requires .env file with API keys)
python -m pytest backend/tests/ -v

# Run specific test file
python backend/tests/test_email_job_matching.py
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

