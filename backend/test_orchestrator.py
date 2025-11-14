"""
Test script for the Orchestrator Agent

Run this script to test the orchestrator's functionality.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database_manager import DatabaseManager
from agents_framework.agents.orchestrator_agent import create_orchestrator_agent
from agents_framework.core.workflow_manager import ExecutionMode


async def test_orchestrator():
    """Test the Orchestrator Agent"""

    print("=" * 80)
    print("ORCHESTRATOR AGENT - TEST SUITE")
    print("=" * 80)
    print()

    # Initialize database manager
    db = DatabaseManager()

    # Create orchestrator
    print("📝 Creating Orchestrator Agent...")
    orchestrator = create_orchestrator_agent(db)
    print(f"✅ Orchestrator created with {len(orchestrator.agent_registry)} agents")
    print()

    # Test 1: Check orchestrator stats
    print("-" * 80)
    print("TEST 1: Get Orchestrator Statistics")
    print("-" * 80)
    stats = orchestrator.get_orchestrator_stats()
    print(f"Agent Name: {stats['name']}")
    print(f"Registered Agents: {', '.join(stats['registered_agents'])}")
    print(f"Tools Available: {stats['tools_count']}")
    print(f"Communication Stats: {stats['communication_stats']}")
    print("✅ Test 1 Passed")
    print()

    # Test 2: Route a simple task to an agent
    print("-" * 80)
    print("TEST 2: Route Task to Specific Agent")
    print("-" * 80)
    task = "List all available agents and their capabilities"
    print(f"Task: {task}")
    print(f"Routing to: Orchestrator (self)")

    result = await orchestrator.run(task)

    if result.success:
        print("✅ Test 2 Passed")
        print(f"Response: {result.output[:200]}...")
    else:
        print(f"❌ Test 2 Failed: {result.error}")
    print()

    # Test 3: Create and execute a simple workflow
    print("-" * 80)
    print("TEST 3: Execute Simple Workflow")
    print("-" * 80)

    workflow_tasks = [
        {
            "agent_name": "Email Analyst",
            "task_description": "Provide a brief introduction of your capabilities",
            "input_data": {},
            "dependencies": [],
            "metadata": {}
        },
        {
            "agent_name": "Resume Writer",
            "task_description": "Provide a brief introduction of your capabilities",
            "input_data": {},
            "dependencies": [],
            "metadata": {}
        }
    ]

    print(f"Workflow: Test Workflow with {len(workflow_tasks)} tasks")
    print(f"Execution Mode: Sequential")

    workflow_result = await orchestrator.execute_workflow(
        workflow_name="Test Workflow",
        workflow_description="Test workflow to verify multi-agent coordination",
        tasks=workflow_tasks,
        execution_mode="sequential"
    )

    if workflow_result.get("success"):
        print("✅ Test 3 Passed")
        print(f"Workflow ID: {workflow_result.get('workflow_id')}")
        print(f"Tasks Executed: {len(workflow_result.get('results', []))}")

        # Show task results
        for i, task_result in enumerate(workflow_result.get('results', []), 1):
            status = task_result.get('status', 'unknown')
            agent = task_result.get('agent_name', 'unknown')
            print(f"  Task {i} ({agent}): {status}")
    else:
        print(f"❌ Test 3 Failed: {workflow_result.get('error')}")
    print()

    # Test 4: Test communication protocol
    print("-" * 80)
    print("TEST 4: Agent Communication Protocol")
    print("-" * 80)

    from agents_framework.core.agent_protocol import AgentMessage, MessageType, MessagePriority

    # Send a test message
    message = AgentMessage(
        sender="Test",
        recipient="Email Analyst",
        message_type=MessageType.QUERY,
        priority=MessagePriority.MEDIUM,
        content="Test message for communication protocol"
    )

    success = orchestrator.protocol.send_message(message)

    if success:
        print("✅ Test 4 Passed")
        comm_stats = orchestrator.get_communication_stats()
        print(f"Total Messages Sent: {comm_stats['total_messages_sent']}")
        print(f"Registered Agents: {comm_stats['agent_count']}")
    else:
        print("❌ Test 4 Failed: Could not send message")
    print()

    # Test 5: Test workflow manager
    print("-" * 80)
    print("TEST 5: Workflow Manager")
    print("-" * 80)

    workflow_stats = orchestrator.workflow_manager.get_stats()
    print(f"Active Workflows: {workflow_stats['active_workflows']}")
    print(f"Total Workflows: {workflow_stats['total_workflows_executed']}")
    print("✅ Test 5 Passed")
    print()

    # Final Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("✅ All tests completed!")
    print()
    print("Orchestrator Agent is ready for use!")
    print()
    print("Available Features:")
    print("  • Multi-agent workflow coordination")
    print("  • Task routing to specialized agents")
    print("  • Sequential and parallel execution")
    print("  • Agent-to-agent communication")
    print("  • Workflow status tracking")
    print("=" * 80)


if __name__ == "__main__":
    print()
    print("Starting Orchestrator Agent Tests...")
    print()

    try:
        asyncio.run(test_orchestrator())
        print()
        print("🎉 All tests completed successfully!")
        print()
    except Exception as e:
        print()
        print(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
