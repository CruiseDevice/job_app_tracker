# AI Agent Framework

A comprehensive framework for building autonomous AI agents with LangChain.

## Features

- **Base Agent Class**: Extensible foundation for all agents
- **Tool Support**: Easy integration of custom tools using LangChain
- **Memory Management**: Conversation history and semantic memory
- **ReAct Pattern**: Reasoning and acting for autonomous decision-making
- **Error Handling**: Robust error handling and logging
- **Cost Tracking**: Monitor API usage and costs
- **Async Support**: Asynchronous execution for better performance

## Quick Start

### 1. Create a Custom Agent

```python
from agents_framework import BaseAgent, AgentConfig

class MyCustomAgent(BaseAgent):
    def __init__(self, db_manager):
        config = AgentConfig(
            name="My Agent",
            description="Does something useful",
            model="gpt-4o-mini",
            temperature=0.1,
            max_iterations=10,
        )

        self.db = db_manager
        super().__init__(config)

    def _register_tools(self):
        """Register custom tools"""
        def my_tool(input_text: str) -> str:
            return f"Processed: {input_text}"

        self.add_tool(
            name="my_tool",
            func=my_tool,
            description="My custom tool that does something"
        )

    def get_system_prompt(self) -> str:
        return "You are a helpful agent that..."
```

### 2. Use the Agent

```python
# Create agent
agent = MyCustomAgent(db_manager)

# Run agent
response = await agent.run("What should I do?")

# Check result
if response.success:
    print(response.output)
else:
    print(f"Error: {response.error}")
```

### 3. Use the Example Agent

```python
from agents_framework import create_job_analyst_agent

# Create the example agent
agent = create_job_analyst_agent(db_manager)

# Ask it questions
response = await agent.run("What are my job application statistics?")
print(response.output)

# Ask for insights
response = await agent.run("Which applications need follow-up?")
print(response.output)
```

## Architecture

```
agents_framework/
├── core/
│   ├── base_agent.py       # Base agent class
│   └── example_agent.py    # Example implementation
├── tools/
│   └── base_tools.py        # Reusable tools
├── memory/
│   └── agent_memory.py      # Memory management
└── utils/
    └── helpers.py           # Utility functions
```

## Components

### BaseAgent

The foundation class that all agents inherit from.

**Key Features:**
- Tool registration and management
- LLM integration (OpenAI)
- ReAct agent executor
- Conversation memory
- Error handling

**Key Methods:**
- `run(input_text, context)`: Execute the agent
- `add_tool(name, func, description)`: Add a tool
- `get_stats()`: Get agent statistics
- `clear_memory()`: Clear conversation history

### AgentConfig

Configuration object for agents.

```python
config = AgentConfig(
    name="Agent Name",
    description="What this agent does",
    model="gpt-4o-mini",           # Model to use
    temperature=0.1,                # Creativity (0-2)
    max_iterations=10,              # Max reasoning steps
    verbose=True,                   # Log tool calls
    enable_memory=True,             # Use conversation memory
    memory_k=10,                    # Messages to keep
)
```

### Memory System

**ConversationMemory:**
- Stores conversation history
- Limits size to prevent context overflow
- Formats context for prompts

**SemanticMemory:**
- Long-term memory with vector embeddings
- Store and retrieve learnings
- Category-based organization

**AgentMemoryManager:**
- Manages both types of memory
- Easy interaction API
- Statistics and monitoring

### Tools

Pre-built tools that agents can use:

**DatabaseTools:**
- `get_all_applications`: Fetch all applications
- `get_application_by_id`: Get specific application
- `update_application_status`: Update status
- `search_applications`: Search by company/position

**EmailTools:**
- `analyze_email_sentiment`: Determine email sentiment
- `extract_action_items`: Find action items

**AnalyticsTools:**
- `get_application_statistics`: Calculate metrics

**UtilityTools:**
- `get_current_datetime`: Current date/time
- `calculate_days_since`: Date calculations

### Creating Custom Tools

```python
def my_custom_tool(input_text: str) -> str:
    """Tool description for the agent"""
    # Your logic here
    return "Result"

agent.add_tool(
    name="my_tool",
    func=my_custom_tool,
    description="Clear description for the LLM"
)
```

## Best Practices

### 1. System Prompts

Write clear, detailed system prompts:

```python
def get_system_prompt(self) -> str:
    return """You are an expert at X who helps users do Y.

Your role is to:
1. Specific task 1
2. Specific task 2
3. Specific task 3

When responding:
- Be clear and concise
- Use tools when available
- Provide specific recommendations
- Cite data from tools
"""
```

### 2. Tool Descriptions

Make tool descriptions clear for the LLM:

```python
# Good
description = "Search for job applications by company name or position title. Input should be the search query (e.g., 'Google' or 'Software Engineer')."

# Bad
description = "Search apps"
```

### 3. Error Handling

Tools should handle errors gracefully:

```python
def my_tool(input_text: str) -> str:
    try:
        # Your logic
        return result
    except ValueError as e:
        return f"Invalid input: {e}"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"Error occurred: {str(e)}"
```

### 4. Input Validation

Validate inputs in tools:

```python
def my_tool(input_str: str) -> str:
    parts = input_str.split(",")
    if len(parts) != 2:
        return "Invalid format. Expected: 'id,status'"

    # Process valid input
    ...
```

## Configuration

### Environment Variables

```env
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here  # Optional: for debugging
```

### Model Selection

Choose models based on use case:

- **gpt-4o**: Most capable, higher cost
- **gpt-4o-mini**: Balanced (recommended)
- **gpt-3.5-turbo**: Fast and cheap

### Temperature Settings

- **0.0-0.3**: Deterministic, factual tasks
- **0.4-0.7**: Balanced creativity
- **0.8-2.0**: Creative writing

## Monitoring

### Agent Statistics

```python
stats = agent.get_stats()
print(f"Executions: {stats['execution_count']}")
print(f"Tools: {stats['tools']}")
print(f"Memory size: {stats['memory_size']}")
```

### Memory Statistics

```python
stats = agent.memory_manager.get_full_stats()
print(stats)
```

## Examples

See `core/example_agent.py` for a complete working example.

## Future Enhancements

- [ ] Vector database integration for semantic memory
- [ ] Streaming responses
- [ ] Multi-agent orchestration
- [ ] Human-in-the-loop workflows
- [ ] Advanced cost tracking
- [ ] Agent performance analytics

## Contributing

When adding new agents:
1. Extend `BaseAgent`
2. Implement `_register_tools()`
3. Implement `get_system_prompt()`
4. Add tests
5. Update documentation
