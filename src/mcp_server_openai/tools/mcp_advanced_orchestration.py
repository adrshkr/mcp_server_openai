"""
MCP Advanced Orchestration Tool

This module provides complex workflow management capabilities for
content creation, including multi-step processes, conditional logic,
and automated decision making.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_TIMEOUT = 300  # 5 minutes
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 5  # seconds
MAX_WORKFLOW_STEPS = 50
MAX_WORKFLOW_DURATION = 3600  # 1 hour


@dataclass
class WorkflowStep:
    """Individual workflow step definition."""

    step_id: str
    name: str
    description: str
    step_type: str  # "action", "decision", "parallel", "loop", "condition"
    tool_name: str
    parameters: dict[str, Any]
    dependencies: list[str] = field(default_factory=list)  # Step IDs this depends on
    timeout: int = DEFAULT_TIMEOUT
    retry_attempts: int = DEFAULT_MAX_RETRIES
    retry_delay: int = DEFAULT_RETRY_DELAY
    condition: str | None = None  # Conditional logic for execution
    parallel_group: str | None = None  # For parallel execution
    loop_config: dict[str, Any] | None = None  # For loop execution
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowCondition:
    """Conditional logic for workflow execution."""

    condition_id: str
    name: str
    description: str
    condition_type: str  # "if", "switch", "loop", "parallel"
    expression: str  # Conditional expression
    true_steps: list[str] = field(default_factory=list)  # Steps to execute if true
    false_steps: list[str] = field(default_factory=list)  # Steps to execute if false
    case_steps: dict[str, list[str]] = field(default_factory=dict)  # For switch statements
    loop_steps: list[str] = field(default_factory=list)  # For loop execution
    max_iterations: int = 10  # Maximum loop iterations
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution instance."""

    execution_id: str
    workflow_id: str
    status: str  # "pending", "running", "completed", "failed", "cancelled"
    current_step: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    failed_steps: list[str] = field(default_factory=list)
    skipped_steps: list[str] = field(default_factory=list)
    step_results: dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    total_duration: float | None = None
    error_message: str | None = None
    progress: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""

    workflow_id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    steps: list[WorkflowStep] = field(default_factory=list)
    conditions: list[WorkflowCondition] = field(default_factory=list)
    entry_point: str = "start"
    exit_points: list[str] = field(default_factory=list)
    timeout: int = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_id: str
    execution_id: str
    status: str
    message: str
    step_results: dict[str, Any]
    final_output: Any
    execution_summary: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class AdvancedOrchestrationEngine:
    """Core advanced orchestration engine."""

    def __init__(self) -> None:
        self.workflows: dict[str, WorkflowDefinition] = {}
        self.executions: dict[str, WorkflowExecution] = {}
        self.execution_history: list[WorkflowExecution] = []
        self.available_tools: dict[str, Any] = {}
        self._initialize_default_workflows()

    def _initialize_default_workflows(self) -> None:
        """Initialize default workflow templates."""
        # Content Creation Workflow
        content_creation_workflow = WorkflowDefinition(
            workflow_id="content_creation_v1",
            name="Content Creation Workflow",
            description="Complete workflow for creating content with research and validation",
            version="1.0.0",
            author="system",
            steps=[
                WorkflowStep(
                    step_id="start",
                    name="Initialize Content Creation",
                    description="Start the content creation process",
                    step_type="action",
                    tool_name="workflow_start",
                    parameters={},
                    dependencies=[],
                ),
                WorkflowStep(
                    step_id="plan_content",
                    name="Plan Content Structure",
                    description="Plan content structure using sequential thinking",
                    step_type="action",
                    tool_name="mcp_sequential_thinking_plan",
                    parameters={
                        "topic": "{{content_topic}}",
                        "objectives": "{{content_objectives}}",
                        "content_type": "{{content_type}}",
                        "audience": "{{target_audience}}",
                    },
                    dependencies=["start"],
                ),
                WorkflowStep(
                    step_id="research_content",
                    name="Research Content",
                    description="Conduct research for content enhancement",
                    step_type="action",
                    tool_name="mcp_research_integration_conduct_research",
                    parameters={
                        "topic": "{{content_topic}}",
                        "content_type": "{{content_type}}",
                        "target_audience": "{{target_audience}}",
                        "objectives": "{{content_objectives}}",
                        "research_depth": "comprehensive",
                    },
                    dependencies=["plan_content"],
                ),
                WorkflowStep(
                    step_id="generate_content",
                    name="Generate Content",
                    description="Generate content using appropriate tools",
                    step_type="action",
                    tool_name="unified_content_create",
                    parameters={
                        "title": "{{content_topic}}",
                        "brief": "{{content_brief}}",
                        "output_format": "{{content_type}}",
                        "style": "{{content_style}}",
                        "research_data": "{{research_results}}",
                    },
                    dependencies=["research_content"],
                ),
                WorkflowStep(
                    step_id="validate_content",
                    name="Validate Content",
                    description="Validate content quality and compliance",
                    step_type="action",
                    tool_name="mcp_content_validation_validate_content",
                    parameters={
                        "content": "{{generated_content}}",
                        "content_type": "{{content_type}}",
                        "target_audience": "{{target_audience}}",
                        "objectives": "{{content_objectives}}",
                        "key_messages": "{{key_messages}}",
                    },
                    dependencies=["generate_content"],
                ),
                WorkflowStep(
                    step_id="enhance_content",
                    name="Enhance Content",
                    description="Enhance content based on validation results",
                    step_type="condition",
                    tool_name="content_enhancement",
                    parameters={"validation_results": "{{validation_results}}", "enhancement_threshold": 0.8},
                    dependencies=["validate_content"],
                    condition="validation_score < 0.8",
                ),
                WorkflowStep(
                    step_id="finalize_content",
                    name="Finalize Content",
                    description="Finalize and save content",
                    step_type="action",
                    tool_name="content_finalization",
                    parameters={
                        "content": "{{enhanced_content}}",
                        "output_path": "{{output_path}}",
                        "metadata": "{{content_metadata}}",
                    },
                    dependencies=["enhance_content", "validate_content"],
                ),
            ],
            conditions=[
                WorkflowCondition(
                    condition_id="enhancement_condition",
                    name="Content Enhancement Decision",
                    description="Decide whether to enhance content based on validation",
                    condition_type="if",
                    expression="validation_score < 0.8",
                    true_steps=["enhance_content"],
                    false_steps=["finalize_content"],
                )
            ],
            entry_point="start",
            exit_points=["finalize_content"],
            tags=["content", "creation", "workflow"],
        )

        self.workflows[content_creation_workflow.workflow_id] = content_creation_workflow

    async def create_workflow(self, workflow_def: WorkflowDefinition) -> str:
        """Create a new workflow definition."""
        try:
            # Validate workflow
            if not self._validate_workflow(workflow_def):
                raise ValueError("Invalid workflow definition")

            # Generate unique ID if not provided
            if not workflow_def.workflow_id:
                workflow_def.workflow_id = f"workflow_{uuid.uuid4().hex[:8]}"

            # Store workflow
            self.workflows[workflow_def.workflow_id] = workflow_def
            logger.info(f"Workflow created: {workflow_def.workflow_id}")

            return workflow_def.workflow_id

        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            raise

    def _validate_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Validate workflow definition."""
        try:
            # Check step limits
            if len(workflow.steps) > MAX_WORKFLOW_STEPS:
                logger.error(f"Workflow has too many steps: {len(workflow.steps)}")
                return False

            # Check for circular dependencies
            if self._has_circular_dependencies(workflow):
                logger.error("Workflow has circular dependencies")
                return False

            # Check entry point exists
            entry_steps = [s for s in workflow.steps if s.step_id == workflow.entry_point]
            if not entry_steps:
                logger.error(f"Entry point '{workflow.entry_point}' not found")
                return False

            # Check exit points exist
            for exit_point in workflow.exit_points:
                exit_steps = [s for s in workflow.steps if s.step_id == exit_point]
                if not exit_steps:
                    logger.error(f"Exit point '{exit_point}' not found")
                    return False

            return True

        except Exception as e:
            logger.error(f"Workflow validation failed: {e}")
            return False

    def _has_circular_dependencies(self, workflow: WorkflowDefinition) -> bool:
        """Check for circular dependencies in workflow."""
        visited = set()
        rec_stack = set()

        def has_cycle(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False

            visited.add(step_id)
            rec_stack.add(step_id)

            step = next((s for s in workflow.steps if s.step_id == step_id), None)
            if step:
                for dep in step.dependencies:
                    if has_cycle(dep):
                        return True

            rec_stack.remove(step_id)
            return False

        for step in workflow.steps:
            if has_cycle(step.step_id):
                return True

        return False

    async def execute_workflow(self, workflow_id: str, parameters: dict[str, Any]) -> str:
        """Execute a workflow with given parameters."""
        try:
            # Get workflow definition
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow not found: {workflow_id}")

            workflow = self.workflows[workflow_id]

            # Create execution instance
            execution = WorkflowExecution(
                execution_id=f"exec_{uuid.uuid4().hex[:8]}",
                workflow_id=workflow_id,
                status="pending",
                metadata={"parameters": parameters},
            )

            # Store execution
            self.executions[execution.execution_id] = execution
            self.execution_history.append(execution)

            # Start execution in background
            asyncio.create_task(self._execute_workflow_async(execution, parameters))

            logger.info(f"Workflow execution started: {execution.execution_id}")
            return execution.execution_id

        except Exception as e:
            logger.error(f"Failed to start workflow execution: {e}")
            raise

    async def _execute_workflow_async(self, execution: WorkflowExecution, parameters: dict[str, Any]) -> None:
        """Execute workflow asynchronously."""
        try:
            execution.status = "running"
            workflow = self.workflows[execution.workflow_id]

            # Initialize execution context
            context = parameters.copy()
            context["execution_id"] = execution.execution_id
            context["workflow_id"] = execution.workflow_id

            # Execute workflow steps
            await self._execute_workflow_steps(execution, workflow, context)

            # Mark as completed
            execution.status = "completed"
            execution.end_time = datetime.now()
            execution.total_duration = (execution.end_time - execution.start_time).total_seconds()
            execution.progress = 100.0

            logger.info(f"Workflow execution completed: {execution.execution_id}")

        except Exception as e:
            execution.status = "failed"
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            execution.total_duration = (execution.end_time - execution.start_time).total_seconds()

            logger.error(f"Workflow execution failed: {execution.execution_id} - {e}")

    async def _execute_workflow_steps(
        self, execution: WorkflowExecution, workflow: WorkflowDefinition, context: dict[str, Any]
    ) -> None:
        """Execute workflow steps in order."""
        try:
            # Get execution order
            execution_order = self._get_execution_order(workflow)

            for step_id in execution_order:
                if execution.status == "cancelled":
                    break

                step = next((s for s in workflow.steps if s.step_id == step_id), None)
                if not step:
                    execution.skipped_steps.append(step_id)
                    continue

                # Check dependencies
                if not self._check_dependencies(execution, step):
                    execution.skipped_steps.append(step_id)
                    continue

                # Execute step
                execution.current_step = step_id
                execution.progress = (len(execution.completed_steps) / len(execution_order)) * 100

                try:
                    result = await self._execute_step(step, context)
                    execution.step_results[step_id] = result
                    execution.completed_steps.append(step_id)

                    # Update context with step result
                    context[f"{step_id}_result"] = result

                except Exception as e:
                    logger.error(f"Step execution failed: {step_id} - {e}")
                    execution.failed_steps.append(step_id)

                    # Check if we should continue or fail
                    if step.step_type == "action":
                        execution.status = "failed"
                        execution.error_message = f"Step {step_id} failed: {e}"
                        break
                    else:
                        # For conditional steps, continue with default behavior
                        continue

                # Check timeout
                if execution.total_duration and execution.total_duration > workflow.timeout:
                    execution.status = "failed"
                    execution.error_message = "Workflow execution timeout"
                    break

        except Exception as e:
            logger.error(f"Workflow step execution failed: {e}")
            execution.status = "failed"
            execution.error_message = str(e)

    def _get_execution_order(self, workflow: WorkflowDefinition) -> list[str]:
        """Get the order of step execution based on dependencies."""
        # Topological sort for dependency resolution
        in_degree = {step.step_id: 0 for step in workflow.steps}
        graph = {step.step_id: [] for step in workflow.steps}

        # Build dependency graph
        for step in workflow.steps:
            for dep in step.dependencies:
                if dep in graph:
                    graph[dep].append(step.step_id)
                    in_degree[step.step_id] += 1

        # Topological sort
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        execution_order = []

        while queue:
            current = queue.pop(0)
            execution_order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(execution_order) != len(workflow.steps):
            logger.warning("Circular dependency detected, using fallback order")
            execution_order = [step.step_id for step in workflow.steps]

        return execution_order

    def _check_dependencies(self, execution: WorkflowExecution, step: WorkflowStep) -> bool:
        """Check if step dependencies are satisfied."""
        for dep in step.dependencies:
            if dep not in execution.completed_steps:
                return False
        return True

    async def _execute_step(self, step: WorkflowStep, context: dict[str, Any]) -> Any:
        """Execute a single workflow step."""
        try:
            # Resolve parameters
            resolved_params = self._resolve_parameters(step.parameters, context)

            # Execute based on step type
            if step.step_type == "action":
                return await self._execute_action_step(step, resolved_params)
            elif step.step_type == "condition":
                return await self._execute_condition_step(step, resolved_params, context)
            elif step.step_type == "parallel":
                return await self._execute_parallel_step(step, resolved_params)
            elif step.step_type == "loop":
                return await self._execute_loop_step(step, resolved_params, context)
            else:
                logger.warning(f"Unknown step type: {step.step_type}")
                return {"status": "skipped", "reason": "unknown_step_type"}

        except Exception as e:
            logger.error(f"Step execution failed: {step.step_id} - {e}")
            raise

    def _resolve_parameters(self, parameters: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Resolve parameter placeholders with context values."""
        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Extract placeholder name
                placeholder = value[2:-2].strip()
                resolved[key] = context.get(placeholder, value)
            else:
                resolved[key] = value

        return resolved

    async def _execute_action_step(self, step: WorkflowStep, params: dict[str, Any]) -> Any:
        """Execute an action step."""
        # For now, return mock results
        # In a real implementation, this would call the actual tool
        return {
            "status": "completed",
            "step_id": step.step_id,
            "tool_name": step.tool_name,
            "parameters": params,
            "result": f"Mock result for {step.tool_name}",
            "timestamp": datetime.now().isoformat(),
        }

    async def _execute_condition_step(self, step: WorkflowStep, params: dict[str, Any], context: dict[str, Any]) -> Any:
        """Execute a conditional step."""
        try:
            # Evaluate condition
            condition_result = self._evaluate_condition(step.condition, context)

            return {
                "status": "completed",
                "step_id": step.step_id,
                "condition": step.condition,
                "result": condition_result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            return {
                "status": "failed",
                "step_id": step.step_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a conditional expression."""
        try:
            # Simple condition evaluation
            # In a real implementation, this would use a proper expression evaluator

            # Check for common patterns
            if "validation_score < 0.8" in condition:
                validation_score = context.get("validation_score", 0.0)
                return validation_score < 0.8

            # Default to True for unknown conditions
            return True

        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return True

    async def _execute_parallel_step(self, step: WorkflowStep, params: dict[str, Any]) -> Any:
        """Execute a parallel step."""
        # For now, return mock result
        return {
            "status": "completed",
            "step_id": step.step_id,
            "type": "parallel",
            "result": "Parallel execution completed",
            "timestamp": datetime.now().isoformat(),
        }

    async def _execute_loop_step(self, step: WorkflowStep, params: dict[str, Any], context: dict[str, Any]) -> Any:
        """Execute a loop step."""
        # For now, return mock result
        return {
            "status": "completed",
            "step_id": step.step_id,
            "type": "loop",
            "result": "Loop execution completed",
            "timestamp": datetime.now().isoformat(),
        }

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        """Get workflow definition by ID."""
        return self.workflows.get(workflow_id)

    def get_execution(self, execution_id: str) -> WorkflowExecution | None:
        """Get workflow execution by ID."""
        return self.executions.get(execution_id)

    def get_execution_history(self, limit: int = 50) -> list[WorkflowExecution]:
        """Get execution history."""
        return self.execution_history[-limit:] if self.execution_history else []

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running workflow execution."""
        execution = self.executions.get(execution_id)
        if execution and execution.status == "running":
            execution.status = "cancelled"
            execution.end_time = datetime.now()
            logger.info(f"Workflow execution cancelled: {execution_id}")
            return True
        return False

    def list_workflows(self) -> list[dict[str, Any]]:
        """List all available workflows."""
        return [
            {
                "workflow_id": w.workflow_id,
                "name": w.name,
                "description": w.description,
                "version": w.version,
                "steps_count": len(w.steps),
                "created_at": w.created_at.isoformat(),
                "tags": w.tags,
            }
            for w in self.workflows.values()
        ]


# Global instance
orchestration_engine = AdvancedOrchestrationEngine()


async def create_workflow_definition(
    name: str,
    description: str,
    steps: list[dict[str, Any]],
    conditions: list[dict[str, Any]] | None = None,
    version: str = "1.0.0",
    author: str = "system",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Create a new workflow definition.

    Args:
        name: Workflow name
        description: Workflow description
        steps: List of workflow steps
        conditions: List of workflow conditions
        version: Workflow version
        author: Workflow author
        tags: Workflow tags

    Returns:
        Dictionary containing workflow creation result
    """
    try:
        # Convert step dictionaries to WorkflowStep objects
        workflow_steps = []
        for step_data in steps:
            step = WorkflowStep(
                step_id=step_data.get("step_id", f"step_{len(workflow_steps)}"),
                name=step_data.get("name", ""),
                description=step_data.get("description", ""),
                step_type=step_data.get("step_type", "action"),
                tool_name=step_data.get("tool_name", ""),
                parameters=step_data.get("parameters", {}),
                dependencies=step_data.get("dependencies", []),
                timeout=step_data.get("timeout", DEFAULT_TIMEOUT),
                retry_attempts=step_data.get("retry_attempts", DEFAULT_MAX_RETRIES),
                retry_delay=step_data.get("retry_delay", DEFAULT_RETRY_DELAY),
                condition=step_data.get("condition"),
                parallel_group=step_data.get("parallel_group"),
                loop_config=step_data.get("loop_config"),
                metadata=step_data.get("metadata", {}),
            )
            workflow_steps.append(step)

        # Convert condition dictionaries to WorkflowCondition objects
        workflow_conditions = []
        if conditions:
            for cond_data in conditions:
                condition = WorkflowCondition(
                    condition_id=cond_data.get("condition_id", f"cond_{len(workflow_conditions)}"),
                    name=cond_data.get("name", ""),
                    description=cond_data.get("description", ""),
                    condition_type=cond_data.get("condition_type", "if"),
                    expression=cond_data.get("expression", ""),
                    true_steps=cond_data.get("true_steps", []),
                    false_steps=cond_data.get("false_steps", []),
                    case_steps=cond_data.get("case_steps", {}),
                    loop_steps=cond_data.get("loop_steps", []),
                    max_iterations=cond_data.get("max_iterations", 10),
                    metadata=cond_data.get("metadata", {}),
                )
                workflow_conditions.append(condition)

        # Create workflow definition
        workflow_def = WorkflowDefinition(
            workflow_id="",
            name=name,
            description=description,
            version=version,
            author=author,
            steps=workflow_steps,
            conditions=workflow_conditions,
            entry_point=workflow_steps[0].step_id if workflow_steps else "start",
            exit_points=[workflow_steps[-1].step_id] if workflow_steps else [],
            tags=tags or [],
        )

        # Create workflow
        workflow_id = await orchestration_engine.create_workflow(workflow_def)

        return {
            "status": "success",
            "workflow_id": workflow_id,
            "message": f"Workflow '{name}' created successfully",
            "steps_count": len(workflow_steps),
            "conditions_count": len(workflow_conditions),
        }

    except Exception as e:
        logger.error(f"Failed to create workflow definition: {e}")
        return {"status": "error", "message": f"Failed to create workflow: {str(e)}"}


async def execute_workflow(workflow_id: str, parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Execute a workflow with given parameters.

    Args:
        workflow_id: ID of the workflow to execute
        parameters: Parameters for workflow execution

    Returns:
        Dictionary containing execution result
    """
    try:
        execution_id = await orchestration_engine.execute_workflow(workflow_id, parameters)

        return {
            "status": "success",
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Workflow execution started successfully",
        }

    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        return {"status": "error", "message": f"Failed to execute workflow: {str(e)}"}


def get_workflow_status(execution_id: str) -> dict[str, Any]:
    """
    Get the status of a workflow execution.

    Args:
        execution_id: ID of the workflow execution

    Returns:
        Dictionary containing execution status
    """
    try:
        execution = orchestration_engine.get_execution(execution_id)

        if not execution:
            return {"status": "error", "message": f"Execution not found: {execution_id}"}

        return {
            "status": "success",
            "execution_id": execution_id,
            "workflow_id": execution.workflow_id,
            "execution_status": execution.status,
            "current_step": execution.current_step,
            "progress": execution.progress,
            "completed_steps": len(execution.completed_steps),
            "failed_steps": len(execution.failed_steps),
            "skipped_steps": len(execution.skipped_steps),
            "start_time": execution.start_time.isoformat(),
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "total_duration": execution.total_duration,
            "error_message": execution.error_message,
        }

    except Exception as e:
        logger.error(f"Failed to get workflow status: {e}")
        return {"status": "error", "message": f"Failed to get workflow status: {str(e)}"}


def list_available_workflows() -> dict[str, Any]:
    """
    List all available workflows.

    Returns:
        Dictionary containing list of workflows
    """
    try:
        workflows = orchestration_engine.list_workflows()

        return {"status": "success", "workflows": workflows, "total_count": len(workflows)}

    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        return {"status": "error", "message": f"Failed to list workflows: {str(e)}"}


def get_execution_history(limit: int = 50) -> dict[str, Any]:
    """
    Get workflow execution history.

    Args:
        limit: Maximum number of history entries to return

    Returns:
        Dictionary containing execution history
    """
    try:
        history = orchestration_engine.get_execution_history(limit)

        history_entries = [
            {
                "execution_id": entry.execution_id,
                "workflow_id": entry.workflow_id,
                "status": entry.status,
                "progress": entry.progress,
                "start_time": entry.start_time.isoformat(),
                "end_time": entry.end_time.isoformat() if entry.end_time else None,
                "total_duration": entry.total_duration,
            }
            for entry in history
        ]

        return {"status": "success", "history": history_entries, "total_count": len(history_entries)}

    except Exception as e:
        logger.error(f"Failed to get execution history: {e}")
        return {"status": "error", "message": f"Failed to get execution history: {str(e)}"}


def register(server: Any) -> None:
    """Register MCP tools with the server."""

    @server.tool()
    async def mcp_advanced_orchestration_create_workflow(
        name: str,
        description: str,
        steps: list[dict[str, Any]],
        conditions: list[dict[str, Any]] | None = None,
        version: str = "1.0.0",
        author: str = "system",
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new workflow definition for advanced orchestration.

        This tool allows you to create complex workflow definitions with
        multiple steps, conditional logic, and parallel execution.

        Args:
            name: Workflow name
            description: Workflow description
            steps: List of workflow steps with configuration
            conditions: List of workflow conditions for decision logic
            version: Workflow version
            author: Workflow author
            tags: Workflow tags for categorization

        Returns:
            Workflow creation result with ID and metadata
        """
        return await create_workflow_definition(
            name=name,
            description=description,
            steps=steps,
            conditions=conditions,
            version=version,
            author=author,
            tags=tags,
        )

    @server.tool()
    async def mcp_advanced_orchestration_execute_workflow(
        workflow_id: str, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a workflow with given parameters.

        Args:
            workflow_id: ID of the workflow to execute
            parameters: Parameters for workflow execution

        Returns:
            Workflow execution result with execution ID
        """
        return await execute_workflow(workflow_id, parameters)

    @server.tool()
    def mcp_advanced_orchestration_get_status(execution_id: str) -> dict[str, Any]:
        """
        Get the status of a workflow execution.

        Args:
            execution_id: ID of the workflow execution

        Returns:
            Execution status with progress and details
        """
        return get_workflow_status(execution_id)

    @server.tool()
    def mcp_advanced_orchestration_list_workflows() -> dict[str, Any]:
        """
        List all available workflows.

        Returns:
            List of available workflows with metadata
        """
        return list_available_workflows()

    @server.tool()
    def mcp_advanced_orchestration_get_history(limit: int = 50) -> dict[str, Any]:
        """
        Get workflow execution history.

        Args:
            limit: Maximum number of history entries to return

        Returns:
            Execution history with status and timing information
        """
        return get_execution_history(limit)


if __name__ == "__main__":
    # Demo and testing
    async def main() -> None:
        print("MCP Advanced Orchestration Tool Demo")
        print("=" * 40)

        # List default workflows
        print("Available workflows:")
        workflows = list_available_workflows()
        if workflows["status"] == "success":
            for workflow in workflows["workflows"]:
                print(f"  - {workflow['name']} (v{workflow['version']})")
                print(f"    ID: {workflow['workflow_id']}")
                print(f"    Steps: {workflow['steps_count']}")
                print(f"    Tags: {', '.join(workflow['tags'])}")
                print()

        # Create a simple custom workflow
        print("Creating custom workflow...")
        custom_workflow = await create_workflow_definition(
            name="Simple Content Workflow",
            description="A simple workflow for content creation",
            steps=[
                {
                    "step_id": "start",
                    "name": "Start",
                    "description": "Start the workflow",
                    "step_type": "action",
                    "tool_name": "workflow_start",
                    "parameters": {},
                },
                {
                    "step_id": "process",
                    "name": "Process Content",
                    "description": "Process the content",
                    "step_type": "action",
                    "tool_name": "content_processor",
                    "parameters": {"content": "{{input_content}}"},
                    "dependencies": ["start"],
                },
                {
                    "step_id": "finish",
                    "name": "Finish",
                    "description": "Complete the workflow",
                    "step_type": "action",
                    "tool_name": "workflow_finish",
                    "parameters": {"result": "{{process_result}}"},
                    "dependencies": ["process"],
                },
            ],
            tags=["custom", "simple", "content"],
        )

        if custom_workflow["status"] == "success":
            print(f"✓ Custom workflow created: {custom_workflow['workflow_id']}")

            # Execute the workflow
            print("Executing custom workflow...")
            execution_result = await execute_workflow(
                custom_workflow["workflow_id"], {"input_content": "Sample content for processing"}
            )

            if execution_result["status"] == "success":
                print(f"✓ Workflow execution started: {execution_result['execution_id']}")

                # Check status
                import time

                time.sleep(1)  # Wait a moment for execution to start

                status = get_workflow_status(execution_result["execution_id"])
                if status["status"] == "success":
                    print(f"  Status: {status['execution_status']}")
                    print(f"  Progress: {status['progress']:.1f}%")
                    print(f"  Current Step: {status['current_step']}")

        print("\nDemo completed successfully!")

    asyncio.run(main())
