"""
Enhanced orchestration patterns for complex multi-agent workflows.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from app.models.communication_models import (
    Workflow, WorkflowStep, TaskStatus, AgentTask, TaskPriority
)
from app.core.task_allocation import task_allocator

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """Orchestrates complex multi-agent workflows."""
    
    def __init__(self):
        """Initialize the workflow orchestrator."""
        self._workflows: Dict[str, Workflow] = {}
        self._running = False
    
    async def create_workflow(self, workflow: Workflow) -> str:
        """
        Create and start a new workflow.
        
        Args:
            workflow: Workflow definition
            
        Returns:
            str: Workflow ID
        """
        self._workflows[workflow.id] = workflow
        workflow.status = TaskStatus.PENDING
        
        logger.info(f"Created workflow {workflow.id}: {workflow.name}")
        
        # Start workflow execution
        await self._start_workflow(workflow.id)
        
        return workflow.id
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get the current status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow: Current workflow status, None if not found
        """
        return self._workflows.get(workflow_id)
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a workflow and all its pending tasks.
        
        Args:
            workflow_id: ID of the workflow to cancel
            
        Returns:
            bool: True if workflow was cancelled
        """
        if workflow_id not in self._workflows:
            return False
        
        workflow = self._workflows[workflow_id]
        
        if workflow.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
        
        workflow.status = TaskStatus.CANCELLED
        workflow.completed_at = datetime.now()
        
        # Cancel any pending tasks for this workflow
        for step in workflow.steps:
            task_id = f"{workflow_id}_{step.id}"
            await task_allocator.cancel_task(task_id)
        
        logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    async def _start_workflow(self, workflow_id: str) -> None:
        """Start executing a workflow."""
        if workflow_id not in self._workflows:
            return
        
        workflow = self._workflows[workflow_id]
        workflow.status = TaskStatus.IN_PROGRESS
        workflow.started_at = datetime.now()
        
        logger.info(f"Starting workflow {workflow_id}")
        
        # Find initial steps (those with no dependencies)
        initial_steps = [step for step in workflow.steps if not step.dependencies]
        
        for step in initial_steps:
            await self._execute_workflow_step(workflow_id, step.id)
    
    async def _execute_workflow_step(self, workflow_id: str, step_id: str) -> None:
        """Execute a specific workflow step."""
        workflow = self._workflows[workflow_id]
        step = next((s for s in workflow.steps if s.id == step_id), None)
        
        if not step:
            logger.error(f"Step {step_id} not found in workflow {workflow_id}")
            return
        
        # Check if dependencies are met
        if not await self._are_step_dependencies_met(workflow, step):
            logger.debug(f"Dependencies not met for step {step_id} in workflow {workflow_id}")
            return
        
        # Check conditions
        if not self._check_step_conditions(workflow, step):
            logger.debug(f"Conditions not met for step {step_id} in workflow {workflow_id}")
            return
        
        # Create and submit task
        task = AgentTask(
            id=f"{workflow_id}_{step_id}",
            name=f"{workflow.name} - {step.name}",
            description=step.name,
            agent_type=step.agent_type,
            priority=TaskPriority.MEDIUM,
            parameters={
                **step.parameters,
                "workflow_id": workflow_id,
                "step_id": step_id,
                "workflow_context": workflow.context
            },
            timeout_seconds=step.timeout_seconds
        )
        
        await task_allocator.submit_task(task)
        workflow.current_step = step_id
        
        logger.info(f"Submitted task for step {step_id} in workflow {workflow_id}")
    
    async def _are_step_dependencies_met(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """Check if all step dependencies are completed."""
        for dep_step_id in step.dependencies:
            task_id = f"{workflow.id}_{dep_step_id}"
            task_status = await task_allocator.get_task_status(task_id)
            
            if not task_status or task_status.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    def _check_step_conditions(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """Check if step conditions are met based on workflow context."""
        for condition_key, expected_value in step.conditions.items():
            actual_value = workflow.context.get(condition_key)
            
            if actual_value != expected_value:
                return False
        
        return True
    
    async def handle_task_completion(self, task_id: str, result: Dict[str, Any]) -> None:
        """Handle completion of a workflow task."""
        # Extract workflow and step IDs from task ID
        if "_" not in task_id:
            return  # Not a workflow task
        
        workflow_id, step_id = task_id.rsplit("_", 1)
        
        if workflow_id not in self._workflows:
            return
        
        workflow = self._workflows[workflow_id]
        step = next((s for s in workflow.steps if s.id == step_id), None)
        
        if not step:
            return
        
        # Update workflow context with step results
        workflow.context[f"step_{step_id}_result"] = result
        
        logger.info(f"Completed step {step_id} in workflow {workflow_id}")
        
        # Check if this was the last step
        if await self._is_workflow_complete(workflow):
            workflow.status = TaskStatus.COMPLETED
            workflow.completed_at = datetime.now()
            logger.info(f"Workflow {workflow_id} completed successfully")
        else:
            # Find and execute next steps
            await self._execute_next_steps(workflow)
    
    async def handle_task_failure(self, task_id: str, error_message: str) -> None:
        """Handle failure of a workflow task."""
        if "_" not in task_id:
            return  # Not a workflow task
        
        workflow_id, step_id = task_id.rsplit("_", 1)
        
        if workflow_id not in self._workflows:
            return
        
        workflow = self._workflows[workflow_id]
        workflow.status = TaskStatus.FAILED
        workflow.error_message = f"Step {step_id} failed: {error_message}"
        workflow.completed_at = datetime.now()
        
        logger.error(f"Workflow {workflow_id} failed at step {step_id}: {error_message}")
    
    async def _is_workflow_complete(self, workflow: Workflow) -> bool:
        """Check if all workflow steps are completed."""
        for step in workflow.steps:
            task_id = f"{workflow.id}_{step.id}"
            task_status = await task_allocator.get_task_status(task_id)
            
            if not task_status or task_status.status != TaskStatus.COMPLETED:
                return False
        
        return True
    
    async def _execute_next_steps(self, workflow: Workflow) -> None:
        """Execute the next eligible steps in a workflow."""
        for step in workflow.steps:
            task_id = f"{workflow.id}_{step.id}"
            task_status = await task_allocator.get_task_status(task_id)
            
            # Skip if step is already started or completed
            if task_status:
                continue
            
            # Check if dependencies are met
            if await self._are_step_dependencies_met(workflow, step):
                await self._execute_workflow_step(workflow.id, step.id)
    
    async def start_monitoring(self) -> None:
        """Start the workflow monitoring loop."""
        if self._running:
            return
        
        self._running = True
        logger.info("Starting workflow orchestration monitoring")
        
        while self._running:
            try:
                await self._monitor_workflows()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in workflow monitoring: {str(e)}")
    
    async def stop_monitoring(self) -> None:
        """Stop the workflow monitoring loop."""
        logger.info("Stopping workflow orchestration monitoring")
        self._running = False
    
    async def _monitor_workflows(self) -> None:
        """Monitor workflows for completion and errors."""
        for workflow_id, workflow in list(self._workflows.items()):
            if workflow.status not in [TaskStatus.IN_PROGRESS]:
                continue
            
            # Check for stalled workflows
            if workflow.started_at:
                elapsed = (datetime.now() - workflow.started_at).total_seconds()
                if elapsed > 3600:  # 1 hour timeout
                    logger.warning(f"Workflow {workflow_id} appears stalled, checking status")
                    
                    # Check if any steps are still in progress
                    active_steps = False
                    for step in workflow.steps:
                        task_id = f"{workflow_id}_{step.id}"
                        task_status = await task_allocator.get_task_status(task_id)
                        
                        if task_status and task_status.status == TaskStatus.IN_PROGRESS:
                            active_steps = True
                            break
                    
                    if not active_steps:
                        # Try to execute next steps
                        await self._execute_next_steps(workflow)


class CampaignWorkflowBuilder:
    """Builder for common campaign-related workflows."""
    
    @staticmethod
    def create_campaign_creation_workflow(campaign_data: Dict[str, Any]) -> Workflow:
        """Create a workflow for campaign creation."""
        workflow = Workflow(
            name="Campaign Creation",
            description="Create a new campaign with world building and initial setup",
            steps=[
                WorkflowStep(
                    id="generate_world",
                    name="Generate World Description",
                    agent_type="narrative",
                    action="describe_scene",
                    parameters={
                        "setting": campaign_data.get("setting", "fantasy"),
                        "tone": campaign_data.get("tone", "heroic"),
                        "context_type": "world_creation"
                    }
                ),
                WorkflowStep(
                    id="create_world_art",
                    name="Create World Concept Art",
                    agent_type="visual",
                    action="illustrate_scene",
                    parameters={
                        "scene_type": "world_overview"
                    },
                    dependencies=["generate_world"]
                ),
                WorkflowStep(
                    id="setup_initial_location",
                    name="Setup Starting Location",
                    agent_type="narrative",
                    action="create_location",
                    parameters={
                        "location_type": "starting_town"
                    },
                    dependencies=["generate_world"]
                )
            ],
            context=campaign_data
        )
        
        return workflow
    
    @staticmethod
    def create_combat_encounter_workflow(encounter_data: Dict[str, Any]) -> Workflow:
        """Create a workflow for combat encounter setup."""
        workflow = Workflow(
            name="Combat Encounter Setup",
            description="Setup a complete combat encounter with description, map, and initiative",
            steps=[
                WorkflowStep(
                    id="describe_encounter",
                    name="Describe Combat Situation",
                    agent_type="narrative",
                    action="describe_combat_setup",
                    parameters=encounter_data
                ),
                WorkflowStep(
                    id="create_battle_map",
                    name="Generate Battle Map",
                    agent_type="visual",
                    action="generate_battle_map",
                    parameters={
                        "environment_context": encounter_data
                    },
                    dependencies=["describe_encounter"]
                ),
                WorkflowStep(
                    id="setup_initiative",
                    name="Setup Initiative Order",
                    agent_type="combat",
                    action="create_encounter",
                    parameters=encounter_data,
                    dependencies=["describe_encounter"]
                )
            ],
            context=encounter_data
        )
        
        return workflow


# Global workflow orchestrator instance
workflow_orchestrator = WorkflowOrchestrator()