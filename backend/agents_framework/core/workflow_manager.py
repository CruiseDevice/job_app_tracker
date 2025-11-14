"""
Workflow Manager

Manages multi-agent workflows, task routing, and coordination.
Supports sequential, parallel, and conditional task execution.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status of a workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """Status of a workflow task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionMode(Enum):
    """How tasks should be executed"""
    SEQUENTIAL = "sequential"  # One task at a time, in order
    PARALLEL = "parallel"  # All tasks at once
    CONDITIONAL = "conditional"  # Based on conditions


@dataclass
class WorkflowTask:
    """
    A single task in a workflow.

    Attributes:
        task_id: Unique identifier
        agent_name: Name of the agent to execute this task
        task_description: Description of what the task does
        input_data: Input data for the task
        dependencies: List of task IDs that must complete before this task
        condition: Optional condition function that determines if task should run
        status: Current task status
        result: Task execution result
        error: Error message if task failed
        started_at: When task started
        completed_at: When task completed
        metadata: Additional metadata
    """
    agent_name: str
    task_description: str
    input_data: Dict[str, Any]
    task_id: str = field(default_factory=lambda: str(uuid4()))
    dependencies: List[str] = field(default_factory=list)
    condition: Optional[Callable] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "agent_name": self.agent_name,
            "task_description": self.task_description,
            "input_data": self.input_data,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata or {}
        }


@dataclass
class Workflow:
    """
    A workflow consisting of multiple tasks.

    Attributes:
        workflow_id: Unique identifier
        name: Workflow name
        description: Workflow description
        tasks: List of tasks in the workflow
        execution_mode: How tasks should be executed
        status: Current workflow status
        created_at: When workflow was created
        started_at: When workflow started
        completed_at: When workflow completed
        metadata: Additional metadata
        context: Shared context across all tasks
    """
    name: str
    description: str
    tasks: List[WorkflowTask]
    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "execution_mode": self.execution_mode.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata or {},
            "context": self.context
        }


class WorkflowManager:
    """
    Manages workflow execution and task coordination.

    Features:
    - Sequential task execution
    - Parallel task execution
    - Conditional task execution
    - Dependency management
    - Task result aggregation
    - Error handling and recovery
    """

    def __init__(self):
        # Active workflows
        self.workflows: Dict[str, Workflow] = {}

        # Workflow execution history
        self.workflow_history: List[Workflow] = []

        # Maximum history size
        self.max_history_size = 100

        # Task execution callbacks
        self.task_executor: Optional[Callable] = None

        logger.info("✅ Workflow Manager initialized")

    def register_task_executor(self, executor: Callable) -> None:
        """
        Register a task executor function.

        The executor should be an async function that takes:
        - agent_name: str
        - task_description: str
        - input_data: Dict[str, Any]

        And returns:
        - result: Any
        """
        self.task_executor = executor
        logger.info("📝 Task executor registered")

    def create_workflow(
        self,
        name: str,
        description: str,
        tasks: List[Dict[str, Any]],
        execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        Create a new workflow.

        Args:
            name: Workflow name
            description: Workflow description
            tasks: List of task definitions
            execution_mode: How to execute tasks
            metadata: Additional metadata

        Returns:
            Created Workflow instance
        """
        # Create workflow tasks
        workflow_tasks = []
        for task_def in tasks:
            task = WorkflowTask(
                agent_name=task_def["agent_name"],
                task_description=task_def["task_description"],
                input_data=task_def.get("input_data", {}),
                dependencies=task_def.get("dependencies", []),
                metadata=task_def.get("metadata")
            )
            workflow_tasks.append(task)

        # Create workflow
        workflow = Workflow(
            name=name,
            description=description,
            tasks=workflow_tasks,
            execution_mode=execution_mode,
            metadata=metadata
        )

        # Store workflow
        self.workflows[workflow.workflow_id] = workflow

        logger.info(f"✅ Workflow '{name}' created with {len(tasks)} tasks (ID: {workflow.workflow_id})")
        return workflow

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute

        Returns:
            Workflow execution results
        """
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]

        if self.task_executor is None:
            raise RuntimeError("Task executor not registered. Call register_task_executor() first.")

        try:
            # Update workflow status
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()

            logger.info(f"🚀 Starting workflow '{workflow.name}' (ID: {workflow_id})")

            # Execute based on execution mode
            if workflow.execution_mode == ExecutionMode.SEQUENTIAL:
                await self._execute_sequential(workflow)
            elif workflow.execution_mode == ExecutionMode.PARALLEL:
                await self._execute_parallel(workflow)
            elif workflow.execution_mode == ExecutionMode.CONDITIONAL:
                await self._execute_conditional(workflow)

            # Update workflow status
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()

            logger.info(f"✅ Workflow '{workflow.name}' completed successfully")

            # Move to history
            self.workflow_history.append(workflow)
            if len(self.workflow_history) > self.max_history_size:
                self.workflow_history = self.workflow_history[-self.max_history_size:]

            return {
                "success": True,
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "results": [task.to_dict() for task in workflow.tasks],
                "metadata": {
                    "started_at": workflow.started_at.isoformat(),
                    "completed_at": workflow.completed_at.isoformat(),
                    "duration_seconds": (workflow.completed_at - workflow.started_at).total_seconds()
                }
            }

        except Exception as e:
            logger.error(f"❌ Workflow '{workflow.name}' failed: {e}", exc_info=True)
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()

            return {
                "success": False,
                "workflow_id": workflow_id,
                "status": workflow.status.value,
                "error": str(e),
                "results": [task.to_dict() for task in workflow.tasks]
            }

    async def _execute_sequential(self, workflow: Workflow) -> None:
        """Execute tasks sequentially"""
        for task in workflow.tasks:
            # Check dependencies
            if not self._check_dependencies(task, workflow):
                task.status = TaskStatus.SKIPPED
                logger.info(f"⏭️ Task '{task.task_description}' skipped due to failed dependencies")
                continue

            # Check condition
            if task.condition and not task.condition(workflow.context):
                task.status = TaskStatus.SKIPPED
                logger.info(f"⏭️ Task '{task.task_description}' skipped due to condition")
                continue

            # Execute task
            await self._execute_task(task, workflow)

    async def _execute_parallel(self, workflow: Workflow) -> None:
        """Execute all tasks in parallel"""
        # Group tasks by dependency level
        task_groups = self._group_tasks_by_dependencies(workflow.tasks)

        # Execute each group in parallel
        for group in task_groups:
            tasks_to_run = []
            for task in group:
                # Check condition
                if task.condition and not task.condition(workflow.context):
                    task.status = TaskStatus.SKIPPED
                    logger.info(f"⏭️ Task '{task.task_description}' skipped due to condition")
                    continue

                tasks_to_run.append(self._execute_task(task, workflow))

            # Run tasks in parallel
            if tasks_to_run:
                await asyncio.gather(*tasks_to_run, return_exceptions=True)

    async def _execute_conditional(self, workflow: Workflow) -> None:
        """Execute tasks based on conditions and dependencies"""
        await self._execute_parallel(workflow)

    async def _execute_task(self, task: WorkflowTask, workflow: Workflow) -> None:
        """Execute a single task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()

            logger.info(f"▶️ Executing task: {task.task_description} (Agent: {task.agent_name})")

            # Merge workflow context with task input
            task_input = {**workflow.context, **task.input_data}

            # Execute task using the registered executor
            result = await self.task_executor(
                agent_name=task.agent_name,
                task_description=task.task_description,
                input_data=task_input
            )

            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()

            # Update workflow context with task result
            workflow.context[f"task_{task.task_id}_result"] = result
            workflow.context[f"last_result"] = result

            logger.info(f"✅ Task completed: {task.task_description}")

        except Exception as e:
            logger.error(f"❌ Task failed: {task.task_description} - {e}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            raise

    def _check_dependencies(self, task: WorkflowTask, workflow: Workflow) -> bool:
        """Check if all task dependencies are satisfied"""
        if not task.dependencies:
            return True

        for dep_id in task.dependencies:
            # Find dependency task
            dep_task = next((t for t in workflow.tasks if t.task_id == dep_id), None)

            if not dep_task:
                logger.warning(f"⚠️ Dependency task {dep_id} not found")
                return False

            if dep_task.status != TaskStatus.COMPLETED:
                return False

        return True

    def _group_tasks_by_dependencies(self, tasks: List[WorkflowTask]) -> List[List[WorkflowTask]]:
        """Group tasks by dependency level for parallel execution"""
        groups = []
        remaining_tasks = tasks.copy()
        completed_task_ids = set()

        while remaining_tasks:
            # Find tasks with satisfied dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(dep_id in completed_task_ids for dep_id in task.dependencies)
            ]

            if not ready_tasks:
                # Circular dependency or unresolvable dependencies
                logger.warning("⚠️ Circular or unresolvable task dependencies detected")
                groups.append(remaining_tasks)
                break

            groups.append(ready_tasks)
            completed_task_ids.update(task.task_id for task in ready_tasks)

            for task in ready_tasks:
                remaining_tasks.remove(task)

        return groups

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None

        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "task_count": len(workflow.tasks),
            "completed_tasks": sum(1 for t in workflow.tasks if t.status == TaskStatus.COMPLETED),
            "failed_tasks": sum(1 for t in workflow.tasks if t.status == TaskStatus.FAILED),
            "pending_tasks": sum(1 for t in workflow.tasks if t.status == TaskStatus.PENDING),
            "running_tasks": sum(1 for t in workflow.tasks if t.status == TaskStatus.RUNNING)
        }

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False

        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            logger.info(f"🛑 Workflow '{workflow.name}' cancelled")
            return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get workflow manager statistics"""
        return {
            "active_workflows": len(self.workflows),
            "total_workflows_executed": len(self.workflow_history),
            "workflow_statuses": {
                status.value: sum(1 for w in self.workflows.values() if w.status == status)
                for status in WorkflowStatus
            }
        }
