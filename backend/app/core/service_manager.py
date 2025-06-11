"""
Service management for agent communication and orchestration systems.
"""
import asyncio
import logging

from app.core.agent_communication import communication_hub
from app.core.task_allocation import task_allocator
from app.core.orchestration import workflow_orchestrator

logger = logging.getLogger(__name__)


class AgentOrchestrationService:
    """Service to manage agent communication and orchestration systems."""
    
    def __init__(self):
        """Initialize the orchestration service."""
        self._running = False
        self._tasks = []
    
    async def start(self) -> None:
        """Start all orchestration services."""
        if self._running:
            logger.warning("Orchestration service is already running")
            return
        
        self._running = True
        logger.info("Starting agent orchestration service")
        
        try:
            # Start communication hub
            comm_task = asyncio.create_task(communication_hub.start_processing())
            self._tasks.append(comm_task)
            
            # Start task allocator monitoring
            task_task = asyncio.create_task(task_allocator.start_monitoring())
            self._tasks.append(task_task)
            
            # Start workflow orchestrator monitoring
            workflow_task = asyncio.create_task(workflow_orchestrator.start_monitoring())
            self._tasks.append(workflow_task)
            
            logger.info("All orchestration services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start orchestration services: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop all orchestration services."""
        if not self._running:
            return
        
        logger.info("Stopping agent orchestration service")
        self._running = False
        
        try:
            # Stop individual services
            await communication_hub.stop_processing()
            await task_allocator.stop_monitoring()
            await workflow_orchestrator.stop_monitoring()
            
            # Cancel background tasks
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            
            self._tasks.clear()
            logger.info("All orchestration services stopped")
            
        except Exception as e:
            logger.error(f"Error stopping orchestration services: {str(e)}")
    
    def is_running(self) -> bool:
        """Check if the orchestration service is running."""
        return self._running
    
    async def get_system_status(self) -> dict:
        """Get status of all orchestration systems."""
        return {
            "service_running": self._running,
            "active_tasks": len(self._tasks),
            "communication_hub_active": communication_hub._running,
            "task_allocator_active": task_allocator._running,
            "workflow_orchestrator_active": workflow_orchestrator._running,
            "agent_count": len(task_allocator._agent_statuses),
            "pending_tasks": len(await task_allocator.get_pending_tasks()),
            "active_workflows": len([w for w in workflow_orchestrator._workflows.values() 
                                   if w.status.value == "in_progress"])
        }


# Global orchestration service instance
orchestration_service = AgentOrchestrationService()