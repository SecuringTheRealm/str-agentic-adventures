"""
Base agent class with communication and task management capabilities.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.models.communication_models import (
    AgentMessage, MessageType, AgentStatus, AgentCapability, AgentTask
)
from app.core.agent_communication import communication_hub
from app.core.task_allocation import task_allocator
from app.core.orchestration import workflow_orchestrator

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents with communication and task management."""
    
    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for this agent instance
            agent_type: Type of agent (e.g., "narrator", "scribe", etc.)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self._current_tasks: List[str] = []
        self._capabilities: List[AgentCapability] = []
        self._running = False
        
        # Initialize capabilities (to be overridden by subclasses)
        self._initialize_capabilities()
        
        # Register with communication hub
        self._register_message_handlers()
        
        # Register with task allocator
        self._register_with_task_allocator()
    
    @abstractmethod
    def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities. Must be implemented by subclasses."""
        pass
    
    def _register_message_handlers(self) -> None:
        """Register message handlers with the communication hub."""
        communication_hub.register_handler(
            self.agent_id, MessageType.REQUEST, self._handle_request_message
        )
        communication_hub.register_handler(
            self.agent_id, MessageType.NOTIFICATION, self._handle_notification_message
        )
    
    def _register_with_task_allocator(self) -> None:
        """Register this agent with the task allocator."""
        agent_status = AgentStatus(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            status="idle",
            capabilities=self._capabilities,
            current_tasks=self._current_tasks,
            load=0.0
        )
        task_allocator.register_agent(agent_status)
    
    async def _handle_request_message(self, message: AgentMessage) -> None:
        """
        Handle incoming request messages.
        
        Args:
            message: The request message to handle
        """
        try:
            logger.debug(f"Agent {self.agent_id} received request: {message.content}")
            
            action = message.content.get("action")
            parameters = message.content.get("parameters", {})
            
            # Execute the requested action
            result = await self._execute_action(action, parameters)
            
            # Send response back
            response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                content={"result": result, "success": True},
                correlation_id=message.id
            )
            
            await communication_hub.send_message(response)
            
        except Exception as e:
            logger.error(f"Error handling request in agent {self.agent_id}: {str(e)}")
            
            # Send error response
            error_response = AgentMessage(
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                content={"error": str(e), "success": False},
                correlation_id=message.id
            )
            
            await communication_hub.send_message(error_response)
    
    async def _handle_notification_message(self, message: AgentMessage) -> None:
        """
        Handle incoming notification messages.
        
        Args:
            message: The notification message to handle
        """
        logger.debug(f"Agent {self.agent_id} received notification: {message.content}")
        
        notification_type = message.content.get("type")
        
        if notification_type == "task_allocated":
            await self._handle_task_allocation(message.content.get("task_id"))
        elif notification_type == "workflow_step":
            await self._handle_workflow_step(message.content)
    
    async def _handle_task_allocation(self, task_id: str) -> None:
        """
        Handle a task allocation notification.
        
        Args:
            task_id: ID of the allocated task
        """
        task = await task_allocator.get_task_status(task_id)
        if not task:
            logger.error(f"Task {task_id} not found for agent {self.agent_id}")
            return
        
        try:
            # Add to current tasks
            self._current_tasks.append(task_id)
            self._update_agent_status()
            
            logger.info(f"Agent {self.agent_id} starting task {task_id}")
            
            # Execute the task
            result = await self._execute_task(task)
            
            # Mark task as completed
            await task_allocator.complete_task(task_id, result)
            
            # Notify workflow orchestrator if this is a workflow task
            if "_" in task_id:
                await workflow_orchestrator.handle_task_completion(task_id, result)
            
        except Exception as e:
            logger.error(f"Task {task_id} failed in agent {self.agent_id}: {str(e)}")
            
            # Mark task as failed
            await task_allocator.fail_task(task_id, str(e))
            
            # Notify workflow orchestrator if this is a workflow task
            if "_" in task_id:
                await workflow_orchestrator.handle_task_failure(task_id, str(e))
        
        finally:
            # Remove from current tasks
            if task_id in self._current_tasks:
                self._current_tasks.remove(task_id)
            self._update_agent_status()
    
    async def _handle_workflow_step(self, step_data: Dict[str, Any]) -> None:
        """
        Handle a workflow step notification.
        
        Args:
            step_data: Workflow step data
        """
        # Default implementation - can be overridden by subclasses
        logger.debug(f"Agent {self.agent_id} received workflow step: {step_data}")
    
    @abstractmethod
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific action. Must be implemented by subclasses.
        
        Args:
            action: The action to execute
            parameters: Action parameters
            
        Returns:
            Dict[str, Any]: Action result
        """
        pass
    
    async def _execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent.
        
        Args:
            task: The task to execute
            
        Returns:
            Dict[str, Any]: Task result
        """
        # Extract action from task parameters
        action = task.parameters.get("action", task.name.lower().replace(" ", "_"))
        
        # Execute the action
        return await self._execute_action(action, task.parameters)
    
    def _update_agent_status(self) -> None:
        """Update agent status in the task allocator."""
        load = len(self._current_tasks) / max(len(self._capabilities), 1)
        status = "busy" if load >= 0.8 else "idle"
        
        task_allocator.update_agent_status(
            self.agent_id,
            status=status,
            load=load,
            current_tasks=self._current_tasks.copy()
        )
    
    async def send_message(self, recipient: str, message_type: MessageType, 
                          content: Dict[str, Any], requires_response: bool = False) -> Optional[AgentMessage]:
        """
        Send a message to another agent.
        
        Args:
            recipient: ID of the recipient agent
            message_type: Type of message
            content: Message content
            requires_response: Whether a response is required
            
        Returns:
            AgentMessage: Response message if requires_response is True
        """
        if requires_response and message_type == MessageType.REQUEST:
            return await communication_hub.send_request(
                self.agent_id, recipient, content
            )
        else:
            message = AgentMessage(
                sender=self.agent_id,
                recipient=recipient,
                message_type=message_type,
                content=content,
                requires_response=requires_response
            )
            
            await communication_hub.send_message(message)
            return None
    
    async def broadcast_message(self, message_type: MessageType, content: Dict[str, Any], 
                               exclude_agents: Optional[List[str]] = None) -> List[str]:
        """
        Broadcast a message to all other agents.
        
        Args:
            message_type: Type of message
            content: Message content
            exclude_agents: List of agent IDs to exclude
            
        Returns:
            List[str]: List of agents that received the message
        """
        return await communication_hub.broadcast_message(
            self.agent_id, message_type, content, exclude_agents
        )
    
    async def start(self) -> None:
        """Start the agent."""
        if self._running:
            return
        
        self._running = True
        logger.info(f"Starting agent {self.agent_id}")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self) -> None:
        """Stop the agent."""
        logger.info(f"Stopping agent {self.agent_id}")
        self._running = False
    
    async def _monitoring_loop(self) -> None:
        """Internal monitoring loop for agent health."""
        while self._running:
            try:
                # Update heartbeat
                task_allocator.update_agent_status(self.agent_id, "idle" if not self._current_tasks else "busy")
                
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Error in agent {self.agent_id} monitoring loop: {str(e)}")
    
    def add_capability(self, capability: AgentCapability) -> None:
        """
        Add a capability to this agent.
        
        Args:
            capability: The capability to add
        """
        self._capabilities.append(capability)
        self._register_with_task_allocator()  # Re-register with updated capabilities
    
    def get_capabilities(self) -> List[AgentCapability]:
        """
        Get all capabilities of this agent.
        
        Returns:
            List[AgentCapability]: List of agent capabilities
        """
        return self._capabilities.copy()