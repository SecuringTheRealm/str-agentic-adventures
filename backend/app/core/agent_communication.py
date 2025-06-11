"""
Agent communication hub for inter-agent messaging.
"""
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict

from app.models.communication_models import AgentMessage, MessageType

logger = logging.getLogger(__name__)


class AgentCommunicationHub:
    """Central hub for managing inter-agent communication."""
    
    def __init__(self):
        """Initialize the communication hub."""
        self._message_handlers: Dict[str, Dict[MessageType, List[Callable]]] = defaultdict(lambda: defaultdict(list))
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._message_history: List[AgentMessage] = []
        self._max_history = 1000  # Keep last 1000 messages
    
    def register_handler(self, agent_id: str, message_type: MessageType, handler: Callable[[AgentMessage], Any]) -> None:
        """
        Register a message handler for an agent.
        
        Args:
            agent_id: ID of the agent registering the handler
            message_type: Type of message to handle
            handler: Async function to call when message is received
        """
        self._message_handlers[agent_id][message_type].append(handler)
        logger.info(f"Registered {message_type} handler for agent {agent_id}")
    
    def unregister_handler(self, agent_id: str, message_type: MessageType, handler: Callable[[AgentMessage], Any]) -> None:
        """
        Unregister a message handler for an agent.
        
        Args:
            agent_id: ID of the agent
            message_type: Type of message handler to remove
            handler: Handler function to remove
        """
        if agent_id in self._message_handlers and message_type in self._message_handlers[agent_id]:
            try:
                self._message_handlers[agent_id][message_type].remove(handler)
                logger.info(f"Unregistered {message_type} handler for agent {agent_id}")
            except ValueError:
                logger.warning(f"Handler not found for agent {agent_id}, message type {message_type}")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: Message to send
            
        Returns:
            bool: True if message was queued successfully
        """
        try:
            await self._message_queue.put(message)
            logger.debug(f"Queued message {message.id} from {message.sender} to {message.recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to queue message {message.id}: {str(e)}")
            return False
    
    async def broadcast_message(self, sender: str, message_type: MessageType, content: Dict[str, Any], 
                               exclude_agents: Optional[List[str]] = None) -> List[str]:
        """
        Broadcast a message to all registered agents.
        
        Args:
            sender: ID of the sending agent
            message_type: Type of message
            content: Message content
            exclude_agents: List of agent IDs to exclude from broadcast
            
        Returns:
            List[str]: List of agent IDs that received the message
        """
        if exclude_agents is None:
            exclude_agents = []
        
        recipients = []
        for agent_id in self._message_handlers.keys():
            if agent_id != sender and agent_id not in exclude_agents:
                message = AgentMessage(
                    sender=sender,
                    recipient=agent_id,
                    message_type=message_type,
                    content=content
                )
                if await self.send_message(message):
                    recipients.append(agent_id)
        
        logger.info(f"Broadcast message from {sender} to {len(recipients)} agents")
        return recipients
    
    async def send_request(self, sender: str, recipient: str, content: Dict[str, Any], 
                          timeout: float = 30.0) -> Optional[AgentMessage]:
        """
        Send a request message and wait for a response.
        
        Args:
            sender: ID of the sending agent
            recipient: ID of the recipient agent
            content: Request content
            timeout: Maximum time to wait for response
            
        Returns:
            AgentMessage: Response message if received, None if timeout
        """
        request_message = AgentMessage(
            sender=sender,
            recipient=recipient,
            message_type=MessageType.REQUEST,
            content=content,
            requires_response=True
        )
        
        if not await self.send_message(request_message):
            return None
        
        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(
                self._wait_for_response(request_message.id),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Request {request_message.id} timed out after {timeout} seconds")
            return None
    
    async def _wait_for_response(self, correlation_id: str) -> AgentMessage:
        """
        Wait for a response message with the given correlation ID.
        
        Args:
            correlation_id: ID of the original request
            
        Returns:
            AgentMessage: The response message
        """
        while True:
            # Check recent messages for response
            for message in reversed(self._message_history[-100:]):  # Check last 100 messages
                if (message.correlation_id == correlation_id and 
                    message.message_type == MessageType.RESPONSE):
                    return message
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
    
    async def start_processing(self) -> None:
        """Start the message processing loop."""
        if self._running:
            logger.warning("Communication hub is already running")
            return
        
        self._running = True
        logger.info("Starting agent communication hub")
        
        while self._running:
            try:
                # Wait for a message with timeout to allow checking _running flag
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                await self._process_message(message)
            except asyncio.TimeoutError:
                continue  # Normal timeout, just continue loop
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
    
    async def stop_processing(self) -> None:
        """Stop the message processing loop."""
        logger.info("Stopping agent communication hub")
        self._running = False
    
    async def _process_message(self, message: AgentMessage) -> None:
        """
        Process a message by delivering it to the appropriate handlers.
        
        Args:
            message: Message to process
        """
        try:
            # Add to history
            self._message_history.append(message)
            if len(self._message_history) > self._max_history:
                self._message_history = self._message_history[-self._max_history:]
            
            # Find handlers for the recipient and message type
            handlers = self._message_handlers.get(message.recipient, {}).get(message.message_type, [])
            
            if not handlers:
                logger.warning(f"No handlers found for message {message.id} to {message.recipient}")
                return
            
            # Call all handlers
            for handler in handlers:
                try:
                    await handler(message)
                    logger.debug(f"Delivered message {message.id} to {message.recipient}")
                except Exception as e:
                    logger.error(f"Handler error for message {message.id}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Failed to process message {message.id}: {str(e)}")
    
    def get_message_history(self, agent_id: Optional[str] = None, 
                           message_type: Optional[MessageType] = None,
                           limit: int = 100) -> List[AgentMessage]:
        """
        Get message history with optional filtering.
        
        Args:
            agent_id: Filter by sender or recipient
            message_type: Filter by message type
            limit: Maximum number of messages to return
            
        Returns:
            List[AgentMessage]: Filtered message history
        """
        messages = self._message_history
        
        if agent_id:
            messages = [m for m in messages if m.sender == agent_id or m.recipient == agent_id]
        
        if message_type:
            messages = [m for m in messages if m.message_type == message_type]
        
        return messages[-limit:]


# Global communication hub instance
communication_hub = AgentCommunicationHub()