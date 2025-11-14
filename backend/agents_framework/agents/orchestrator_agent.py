"""
Orchestrator Agent

Master agent for coordinating multiple specialized agents.
Manages multi-agent workflows, task routing, and agent communication.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

from agents_framework.core.base_agent import BaseAgent, AgentConfig, AgentResponse
from agents_framework.core.agent_protocol import (
    AgentCommunicationProtocol,
    AgentMessage,
    MessageType,
    MessagePriority,
    get_global_protocol
)
from agents_framework.core.workflow_manager import (
    WorkflowManager,
    Workflow,
    WorkflowTask,
    ExecutionMode,
    WorkflowStatus
)

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent - Coordinates multiple specialized agents.

    Capabilities:
    - Multi-agent workflow coordination
    - Intelligent task routing
    - Parallel agent execution
    - Agent-to-agent communication
    - Workflow management and monitoring
    - Result aggregation and synthesis
    - Error handling and recovery
    """

    def __init__(self, db_manager, agent_registry: Optional[Dict[str, Any]] = None):
        # Create agent configuration
        config = AgentConfig(
            name="Orchestrator",
            description="Coordinates multiple specialized agents to handle complex multi-step tasks",
            model="gpt-4o-mini",
            temperature=0.2,
            max_iterations=15,
            verbose=True,
            enable_memory=True,
            memory_k=20,
        )

        # Store dependencies
        self.db_manager = db_manager

        # Agent registry - maps agent names to agent instances or factory functions
        self.agent_registry: Dict[str, Any] = agent_registry or {}

        # Communication protocol
        self.protocol = get_global_protocol()
        self.protocol.register_agent("Orchestrator", self)

        # Workflow manager
        self.workflow_manager = WorkflowManager()
        self.workflow_manager.register_task_executor(self._execute_agent_task)

        # Active agent instances cache
        self._agent_cache: Dict[str, Any] = {}

        # Initialize base agent
        super().__init__(config)

        logger.info("✅ Orchestrator Agent initialized with multi-agent coordination")

    def register_agent(self, agent_name: str, agent_factory: Callable, cache: bool = True) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent_name: Name of the agent
            agent_factory: Factory function that creates the agent instance
            cache: Whether to cache the agent instance
        """
        self.agent_registry[agent_name] = {
            "factory": agent_factory,
            "cache": cache
        }
        self.protocol.register_agent(agent_name)
        logger.info(f"📝 Agent '{agent_name}' registered with Orchestrator")

    def _get_agent(self, agent_name: str) -> Any:
        """Get or create an agent instance"""
        # Check cache first
        if agent_name in self._agent_cache:
            return self._agent_cache[agent_name]

        # Check registry
        if agent_name not in self.agent_registry:
            raise ValueError(f"Agent '{agent_name}' not registered with Orchestrator")

        # Create agent instance
        agent_info = self.agent_registry[agent_name]
        agent = agent_info["factory"]()

        # Cache if requested
        if agent_info.get("cache", True):
            self._agent_cache[agent_name] = agent

        return agent

    def _register_tools(self) -> None:
        """Register orchestrator tools"""

        # Tool 1: Route Task to Agent
        def route_task_to_agent(agent_name: str, task_description: str) -> str:
            """
            Route a task to a specific agent for execution.
            Use this when you know which agent should handle a task.

            Args:
                agent_name: Name of the agent (e.g., 'Email Analyst', 'Job Hunter', 'Resume Writer')
                task_description: Description of the task to perform

            Returns:
                Recommendation for which agent to use and why
            """
            available_agents = list(self.agent_registry.keys())

            if not available_agents:
                return "No agents registered. Cannot route task."

            if agent_name in available_agents:
                return f"✅ Task '{task_description}' should be routed to '{agent_name}' agent."
            else:
                return f"❌ Agent '{agent_name}' not found. Available agents: {', '.join(available_agents)}"

        # Tool 2: List Available Agents
        def list_available_agents() -> str:
            """
            List all agents registered with the orchestrator.
            Use this to see what agents are available for task routing.

            Returns:
                List of available agents with their capabilities
            """
            if not self.agent_registry:
                return "No agents currently registered."

            agent_list = ["Available Agents:"]
            for agent_name in self.agent_registry.keys():
                agent_list.append(f"  - {agent_name}")

            return "\n".join(agent_list)

        # Tool 3: Analyze Task Complexity
        def analyze_task_complexity(task: str) -> str:
            """
            Analyze if a task requires multiple agents or can be handled by a single agent.

            Args:
                task: The task description to analyze

            Returns:
                Analysis of task complexity and recommended approach
            """
            task_lower = task.lower()

            # Keywords indicating multi-agent tasks
            multi_agent_keywords = [
                ('analyze email' and 'draft follow-up'),
                ('search jobs' and 'tailor resume'),
                ('interview prep' and 'research company'),
                'end-to-end',
                'complete workflow',
                'full process'
            ]

            # Check for multiple agent needs
            needs_multiple = any(keyword in task_lower for keyword in multi_agent_keywords if isinstance(keyword, str))

            if needs_multiple or len(task.split(' and ')) > 1:
                return """
Task Complexity: HIGH - Multi-Agent Workflow Required

This task appears to require coordination between multiple agents.
Recommended approach:
1. Break down into subtasks
2. Identify required agents for each subtask
3. Define workflow dependencies
4. Execute as coordinated multi-agent workflow
"""
            else:
                return """
Task Complexity: LOW - Single Agent Sufficient

This task can likely be handled by a single specialized agent.
Recommended approach:
1. Identify the most appropriate agent
2. Route task directly to that agent
3. Return results
"""

        # Add tools
        self.add_tool("route_task_to_agent", route_task_to_agent, "Route a task to a specific agent")
        self.add_tool("list_available_agents", list_available_agents, "List all available agents")
        self.add_tool("analyze_task_complexity", analyze_task_complexity, "Analyze task complexity")

    def get_system_prompt(self) -> str:
        """Get the system prompt for the orchestrator"""
        available_agents = list(self.agent_registry.keys())

        return f"""You are the Orchestrator Agent, a master coordinator of specialized AI agents.

Your role is to:
1. Analyze user requests to determine if they require single or multiple agents
2. Route simple tasks to the appropriate specialized agent
3. Break down complex tasks into multi-agent workflows
4. Coordinate execution between multiple agents
5. Aggregate and synthesize results from multiple agents

Available Specialized Agents:
{chr(10).join(f'- {name}' for name in available_agents)}

Guidelines:
- For simple, single-purpose tasks: Route directly to the appropriate agent
- For complex, multi-step tasks: Create a workflow with multiple agents
- Always explain your reasoning for task routing decisions
- Provide clear, actionable responses
- Handle errors gracefully and provide alternatives

When coordinating multiple agents:
1. Define clear subtasks for each agent
2. Specify dependencies between tasks
3. Execute in the optimal order (sequential or parallel)
4. Synthesize results into a coherent response
"""

    async def _execute_agent_task(
        self,
        agent_name: str,
        task_description: str,
        input_data: Dict[str, Any]
    ) -> Any:
        """
        Execute a task using a specific agent.

        This is called by the workflow manager for each task.
        """
        try:
            logger.info(f"🤖 Executing task with {agent_name}: {task_description}")

            # Get agent instance
            agent = self._get_agent(agent_name)

            # Execute task
            result = await agent.run(task_description, context=input_data)

            logger.info(f"✅ {agent_name} completed task successfully")

            return {
                "success": result.success,
                "output": result.output,
                "agent_name": agent_name,
                "metadata": result.metadata
            }

        except Exception as e:
            logger.error(f"❌ Error executing task with {agent_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "agent_name": agent_name
            }

    async def execute_workflow(
        self,
        workflow_name: str,
        workflow_description: str,
        tasks: List[Dict[str, Any]],
        execution_mode: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Execute a multi-agent workflow.

        Args:
            workflow_name: Name of the workflow
            workflow_description: Description of the workflow
            tasks: List of task definitions, each containing:
                - agent_name: Name of the agent to execute the task
                - task_description: Description of the task
                - input_data: Input data for the task (optional)
                - dependencies: List of task IDs this task depends on (optional)
            execution_mode: "sequential" or "parallel"

        Returns:
            Workflow execution results
        """
        try:
            # Convert execution mode string to enum
            mode = ExecutionMode.SEQUENTIAL if execution_mode == "sequential" else ExecutionMode.PARALLEL

            # Create workflow
            workflow = self.workflow_manager.create_workflow(
                name=workflow_name,
                description=workflow_description,
                tasks=tasks,
                execution_mode=mode
            )

            logger.info(f"🚀 Executing workflow '{workflow_name}' with {len(tasks)} tasks")

            # Execute workflow
            result = await self.workflow_manager.execute_workflow(workflow.workflow_id)

            return result

        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def route_to_agent(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Route a task directly to a specific agent.

        Args:
            agent_name: Name of the agent
            task: Task description
            context: Optional context data

        Returns:
            AgentResponse from the agent
        """
        try:
            logger.info(f"🎯 Routing task to {agent_name}: {task}")

            # Get agent
            agent = self._get_agent(agent_name)

            # Execute task
            result = await agent.run(task, context=context)

            logger.info(f"✅ {agent_name} completed task")

            return result

        except Exception as e:
            logger.error(f"❌ Error routing to {agent_name}: {e}", exc_info=True)
            return AgentResponse(
                output="",
                agent_name=agent_name,
                success=False,
                error=str(e)
            )

    async def coordinate_agents(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Coordinate multiple agents to complete a complex task.

        The orchestrator will:
        1. Analyze the task
        2. Determine which agents are needed
        3. Create a workflow
        4. Execute the workflow
        5. Synthesize results

        Args:
            task: The complex task to complete
            context: Optional context data

        Returns:
            Coordinated results from multiple agents
        """
        try:
            logger.info(f"🎭 Coordinating agents for task: {task}")

            # Use the orchestrator's reasoning to determine the workflow
            planning_prompt = f"""
Analyze this task and create a multi-agent workflow plan:

Task: {task}

Create a JSON workflow plan with the following structure:
{{
    "workflow_name": "descriptive name",
    "execution_mode": "sequential" or "parallel",
    "tasks": [
        {{
            "agent_name": "name of agent",
            "task_description": "what the agent should do",
            "input_data": {{}},
            "dependencies": []
        }}
    ]
}}

Available agents: {', '.join(self.agent_registry.keys())}
"""

            # Get workflow plan from orchestrator's reasoning
            plan_response = await super().run(planning_prompt, context=context)

            if not plan_response.success:
                return {
                    "success": False,
                    "error": "Failed to create workflow plan"
                }

            # TODO: Parse the plan and execute workflow
            # For now, return the plan
            return {
                "success": True,
                "plan": plan_response.output,
                "message": "Workflow plan created. Implementation pending."
            }

        except Exception as e:
            logger.error(f"❌ Error coordinating agents: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow"""
        return self.workflow_manager.get_workflow_status(workflow_id)

    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication protocol statistics"""
        return self.protocol.get_stats()

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        base_stats = self.get_stats()
        workflow_stats = self.workflow_manager.get_stats()
        comm_stats = self.protocol.get_stats()

        return {
            **base_stats,
            "registered_agents": list(self.agent_registry.keys()),
            "cached_agents": list(self._agent_cache.keys()),
            "workflow_stats": workflow_stats,
            "communication_stats": comm_stats
        }


def create_orchestrator_agent(db_manager) -> OrchestratorAgent:
    """
    Factory function to create an Orchestrator Agent.

    Args:
        db_manager: Database manager instance

    Returns:
        Configured OrchestratorAgent instance
    """
    from agents_framework.agents.email_analyst_agent import create_email_analyst_agent
    from agents_framework.agents.followup_agent import create_followup_agent
    from agents_framework.agents.job_hunter_agent import create_job_hunter_agent
    from agents_framework.agents.resume_writer_agent import create_resume_writer_agent
    from agents_framework.agents.interview_prep_agent import create_interview_prep_agent

    # Create orchestrator
    orchestrator = OrchestratorAgent(db_manager)

    # Register all available agents
    orchestrator.register_agent(
        "Email Analyst",
        lambda: create_email_analyst_agent(db_manager),
        cache=True
    )

    orchestrator.register_agent(
        "Follow-up Agent",
        lambda: create_followup_agent(db_manager),
        cache=True
    )

    orchestrator.register_agent(
        "Job Hunter",
        lambda: create_job_hunter_agent(db_manager),
        cache=True
    )

    orchestrator.register_agent(
        "Resume Writer",
        lambda: create_resume_writer_agent(db_manager),
        cache=True
    )

    orchestrator.register_agent(
        "Interview Prep",
        lambda: create_interview_prep_agent(db_manager),
        cache=True
    )

    logger.info(f"✅ Orchestrator Agent created with {len(orchestrator.agent_registry)} registered agents")

    return orchestrator
