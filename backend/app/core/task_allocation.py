"""
Task allocation and management system for multi-agent coordination.
"""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.communication_models import (
    AgentTask, TaskStatus, TaskPriority, AgentStatus
)

logger = logging.getLogger(__name__)


class TaskAllocator:
    """Manages task allocation and distribution across agents."""
    
    def __init__(self):
        """Initialize the task allocator."""
        self._tasks: Dict[str, AgentTask] = {}
        self._agent_statuses: Dict[str, AgentStatus] = {}
        self._task_queue: List[str] = []  # Task IDs in priority order
        self._running = False
        
        # Agent type mappings
        self._agent_type_mapping = {
            "narrative": ["narrator"],
            "character": ["scribe"],
            "combat": ["combat_mc", "combat_cartographer"],
            "visual": ["artist", "combat_cartographer"],
            "rules": ["combat_mc"],
            "orchestration": ["dungeon_master"]
        }
    
    def register_agent(self, agent_status: AgentStatus) -> None:
        """
        Register an agent with the task allocator.
        
        Args:
            agent_status: Status and capabilities of the agent
        """
        self._agent_statuses[agent_status.agent_id] = agent_status
        logger.info(f"Registered agent {agent_status.agent_id} of type {agent_status.agent_type}")
    
    def update_agent_status(self, agent_id: str, status: str, load: float = None, 
                           current_tasks: List[str] = None) -> None:
        """
        Update an agent's status.
        
        Args:
            agent_id: ID of the agent
            status: New status ("idle", "busy", "offline")
            load: Current workload (0.0 to 1.0)
            current_tasks: List of current task IDs
        """
        if agent_id in self._agent_statuses:
            agent_status = self._agent_statuses[agent_id]
            agent_status.status = status
            if load is not None:
                agent_status.load = load
            if current_tasks is not None:
                agent_status.current_tasks = current_tasks
            agent_status.last_heartbeat = datetime.now()
            
            logger.debug(f"Updated status for agent {agent_id}: {status}, load: {load}")
    
    async def submit_task(self, task: AgentTask) -> str:
        """
        Submit a task for execution.
        
        Args:
            task: Task to execute
            
        Returns:
            str: Task ID
        """
        self._tasks[task.id] = task
        self._insert_task_by_priority(task.id)
        
        logger.info(f"Submitted task {task.id} ({task.name}) with priority {task.priority}")
        
        # Try to allocate immediately if there are available agents
        await self._try_allocate_tasks()
        
        return task.id
    
    async def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            AgentTask: Current task status, None if not found
        """
        return self._tasks.get(task_id)
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending or in-progress task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            bool: True if task was cancelled successfully
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        
        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False  # Cannot cancel completed tasks
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        
        # Remove from queue if pending
        if task_id in self._task_queue:
            self._task_queue.remove(task_id)
        
        # Update agent status if task was in progress
        if task.assigned_agent:
            self._remove_task_from_agent(task.assigned_agent, task_id)
        
        logger.info(f"Cancelled task {task_id}")
        return True
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark a task as completed with results.
        
        Args:
            task_id: ID of the completed task
            result: Task results
            
        Returns:
            bool: True if task was marked as completed
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.result = result
        task.completed_at = datetime.now()
        
        # Update agent status
        if task.assigned_agent:
            self._remove_task_from_agent(task.assigned_agent, task_id)
        
        logger.info(f"Completed task {task_id}")
        
        # Try to allocate more tasks
        await self._try_allocate_tasks()
        
        return True
    
    async def fail_task(self, task_id: str, error_message: str) -> bool:
        """
        Mark a task as failed.
        
        Args:
            task_id: ID of the failed task
            error_message: Error description
            
        Returns:
            bool: True if task was marked as failed
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.now()
        
        # Update agent status
        if task.assigned_agent:
            self._remove_task_from_agent(task.assigned_agent, task_id)
        
        logger.error(f"Failed task {task_id}: {error_message}")
        
        # Try to allocate more tasks
        await self._try_allocate_tasks()
        
        return True
    
    async def get_pending_tasks(self, agent_type: Optional[str] = None) -> List[AgentTask]:
        """
        Get all pending tasks, optionally filtered by agent type.
        
        Args:
            agent_type: Filter by agent type capability
            
        Returns:
            List[AgentTask]: Pending tasks
        """
        pending_tasks = [
            self._tasks[task_id] for task_id in self._task_queue
            if self._tasks[task_id].status == TaskStatus.PENDING
        ]
        
        if agent_type:
            # Filter by agent type that can handle the task
            filtered_tasks = []
            for task in pending_tasks:
                if self._can_agent_handle_task(agent_type, task):
                    filtered_tasks.append(task)
            return filtered_tasks
        
        return pending_tasks
    
    def _insert_task_by_priority(self, task_id: str) -> None:
        """Insert a task into the queue maintaining priority order."""
        task = self._tasks[task_id]
        priority_order = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        task_priority = priority_order[task.priority]
        
        # Find insertion point
        insert_index = 0
        for i, existing_task_id in enumerate(self._task_queue):
            existing_task = self._tasks[existing_task_id]
            existing_priority = priority_order[existing_task.priority]
            
            if task_priority < existing_priority:
                insert_index = i
                break
            insert_index = i + 1
        
        self._task_queue.insert(insert_index, task_id)
    
    async def _try_allocate_tasks(self) -> None:
        """Try to allocate pending tasks to available agents."""
        for task_id in self._task_queue.copy():
            task = self._tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                self._task_queue.remove(task_id)
                continue
            
            # Check dependencies
            if not self._are_dependencies_met(task):
                continue
            
            # Find best agent for this task
            best_agent = self._find_best_agent_for_task(task)
            
            if best_agent:
                await self._allocate_task_to_agent(task, best_agent)
                self._task_queue.remove(task_id)
    
    def _are_dependencies_met(self, task: AgentTask) -> bool:
        """Check if all task dependencies are completed."""
        for dep_task_id in task.dependencies:
            if dep_task_id in self._tasks:
                dep_task = self._tasks[dep_task_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True
    
    def _find_best_agent_for_task(self, task: AgentTask) -> Optional[str]:
        """
        Find the best available agent for a task.
        
        Args:
            task: Task to allocate
            
        Returns:
            str: Agent ID of best agent, None if no suitable agent available
        """
        suitable_agents = []
        
        for agent_id, agent_status in self._agent_statuses.items():
            # Check if agent can handle this task type
            if not self._can_agent_handle_task(agent_status.agent_type, task):
                continue
            
            # Check if agent is available
            if agent_status.status == "offline":
                continue
            
            # Check load
            if agent_status.load >= 1.0:
                continue
            
            suitable_agents.append((agent_id, agent_status))
        
        if not suitable_agents:
            return None
        
        # Sort by load (prefer less loaded agents)
        suitable_agents.sort(key=lambda x: x[1].load)
        
        return suitable_agents[0][0]
    
    def _can_agent_handle_task(self, agent_type: str, task: AgentTask) -> bool:
        """Check if an agent type can handle a specific task."""
        # Check if agent type is directly mapped to task type
        task_agents = self._agent_type_mapping.get(task.agent_type, [])
        return agent_type in task_agents or agent_type == task.agent_type
    
    async def _allocate_task_to_agent(self, task: AgentTask, agent_id: str) -> None:
        """Allocate a task to a specific agent."""
        task.status = TaskStatus.IN_PROGRESS
        task.assigned_agent = agent_id
        task.started_at = datetime.now()
        
        # Update agent status
        agent_status = self._agent_statuses[agent_id]
        agent_status.current_tasks.append(task.id)
        agent_status.status = "busy" if agent_status.load >= 0.8 else "idle"
        
        logger.info(f"Allocated task {task.id} to agent {agent_id}")
    
    def _remove_task_from_agent(self, agent_id: str, task_id: str) -> None:
        """Remove a task from an agent's current tasks."""
        if agent_id in self._agent_statuses:
            agent_status = self._agent_statuses[agent_id]
            if task_id in agent_status.current_tasks:
                agent_status.current_tasks.remove(task_id)
            
            # Update agent status based on remaining load
            if not agent_status.current_tasks:
                agent_status.status = "idle"
                agent_status.load = 0.0
    
    async def start_monitoring(self) -> None:
        """Start the task monitoring loop."""
        if self._running:
            return
        
        self._running = True
        logger.info("Starting task allocation monitoring")
        
        while self._running:
            try:
                await self._monitor_tasks()
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in task monitoring: {str(e)}")
    
    async def stop_monitoring(self) -> None:
        """Stop the task monitoring loop."""
        logger.info("Stopping task allocation monitoring")
        self._running = False
    
    async def _monitor_tasks(self) -> None:
        """Monitor tasks for timeouts and stale assignments."""
        current_time = datetime.now()
        
        for task_id, task in self._tasks.items():
            # Check for timeouts
            if (task.status == TaskStatus.IN_PROGRESS and 
                task.timeout_seconds and 
                task.started_at and
                (current_time - task.started_at).total_seconds() > task.timeout_seconds):
                
                await self.fail_task(task_id, "Task timed out")
            
            # Check for stale agent heartbeats
            if (task.assigned_agent and 
                task.assigned_agent in self._agent_statuses):
                
                agent_status = self._agent_statuses[task.assigned_agent]
                if (current_time - agent_status.last_heartbeat).total_seconds() > 60:  # 1 minute
                    logger.warning(f"Agent {task.assigned_agent} appears stale, failing task {task_id}")
                    await self.fail_task(task_id, "Agent became unresponsive")


# Global task allocator instance
task_allocator = TaskAllocator()