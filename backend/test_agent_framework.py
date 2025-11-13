"""
Quick test script for the agent framework
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents_framework import create_job_analyst_agent, AgentConfig
from database.database_manager import DatabaseManager


async def test_agent_framework():
    """Test the agent framework"""
    print("🧪 Testing Agent Framework\n")

    # Initialize database
    print("1. Initializing database...")
    db = DatabaseManager()
    print("   ✅ Database initialized\n")

    # Create agent
    print("2. Creating Job Analyst Agent...")
    agent = create_job_analyst_agent(db)
    print(f"   ✅ Agent created: {agent.name}")
    print(f"   Tools available: {len(agent.tools)}")
    for tool in agent.tools:
        print(f"      - {tool.name}")
    print()

    # Test 1: Simple query without tools
    print("3. Testing simple query (no tools needed)...")
    response = await agent.run("Hello! What can you help me with?")

    if response.success:
        print(f"   ✅ Response: {response.output[:100]}...")
    else:
        print(f"   ❌ Error: {response.error}")
    print()

    # Test 2: Query that should use tools
    print("4. Testing query with tools...")
    response = await agent.run("Can you analyze my job applications and give me insights?")

    if response.success:
        print(f"   ✅ Response generated")
        print(f"   Tools used: {len(response.intermediate_steps)}")
        for step in response.intermediate_steps[:3]:
            action = step[0]
            tool_name = action.tool if hasattr(action, 'tool') else 'unknown'
            print(f"      - Used tool: {tool_name}")
        print()
        print(f"   Output:\n   {response.output[:300]}...")
    else:
        print(f"   ❌ Error: {response.error}")
    print()

    # Test 3: Agent statistics
    print("5. Checking agent statistics...")
    stats = agent.get_stats()
    print(f"   ✅ Statistics:")
    print(f"      - Name: {stats['name']}")
    print(f"      - Executions: {stats['execution_count']}")
    print(f"      - Tools: {stats['tools_count']}")
    print(f"      - Memory size: {stats['memory_size']} messages")
    print()

    # Test 4: Memory
    print("6. Testing memory...")
    agent.add_message_to_memory(agent.conversation_history[-1] if agent.conversation_history else None)
    memory_context = agent.get_memory_context()
    print(f"   ✅ Memory context length: {len(memory_context)} characters")
    print()

    print("✅ All tests completed successfully!")
    return True


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in your .env file or environment")
        sys.exit(1)

    try:
        asyncio.run(test_agent_framework())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
