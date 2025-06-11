"""
Base agent class with persistence capabilities.
Provides common persistence functionality for all agents.
"""
import logging
from typing import Dict, Any, Optional
from abc import ABC

from app.persistence.interface import PersistenceInterface
from app.persistence.file_storage import FilePersistence
from app.persistence.session_manager import session_manager

logger = logging.getLogger(__name__)


class PersistentAgent(ABC):
    """Base class for agents that need persistence capabilities."""
    
    def __init__(self, agent_name: str, persistence: Optional[PersistenceInterface] = None):
        """
        Initialize persistent agent.
        
        Args:
            agent_name: Name of the agent (used as collection name)
            persistence: Persistence backend to use
        """
        self.agent_name = agent_name
        self.persistence = persistence or FilePersistence()
        self._data_cache = {}
    
    async def save_agent_data(self, key: str, data: Dict[str, Any]) -> bool:
        """
        Save agent-specific data.
        
        Args:
            key: Unique identifier for the data
            data: Data to save
            
        Returns:
            bool: True if successful
        """
        try:
            success = await self.persistence.save_data(self.agent_name, key, data)
            if success:
                self._data_cache[key] = data
                logger.debug(f"{self.agent_name} saved data for key: {key}")
            return success
        except Exception as e:
            logger.error(f"{self.agent_name} failed to save data for {key}: {str(e)}")
            return False
    
    async def load_agent_data(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load agent-specific data.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            Optional[Dict[str, Any]]: Data if found
        """
        try:
            # Check cache first
            if key in self._data_cache:
                return self._data_cache[key]
            
            data = await self.persistence.load_data(self.agent_name, key)
            if data:
                self._data_cache[key] = data
                logger.debug(f"{self.agent_name} loaded data for key: {key}")
            return data
        except Exception as e:
            logger.error(f"{self.agent_name} failed to load data for {key}: {str(e)}")
            return None
    
    async def delete_agent_data(self, key: str) -> bool:
        """
        Delete agent-specific data.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            bool: True if successful
        """
        try:
            success = await self.persistence.delete_data(self.agent_name, key)
            if success and key in self._data_cache:
                del self._data_cache[key]
                logger.debug(f"{self.agent_name} deleted data for key: {key}")
            return success
        except Exception as e:
            logger.error(f"{self.agent_name} failed to delete data for {key}: {str(e)}")
            return False
    
    async def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent's data from a specific session.
        
        Args:
            session_id: Session ID to load data from
            
        Returns:
            Optional[Dict[str, Any]]: Agent's session data if found
        """
        session_data = await session_manager.load_session(session_id)
        if session_data and self.agent_name in session_data:
            return session_data[self.agent_name]
        return None
    
    async def save_to_session(self, session_id: str, agent_data: Dict[str, Any]) -> bool:
        """
        Save agent's data to a specific session.
        
        Args:
            session_id: Session ID to save data to
            agent_data: Agent's data to save
            
        Returns:
            bool: True if successful
        """
        session_data = await session_manager.load_session(session_id)
        if session_data:
            session_data[self.agent_name] = agent_data
            return await session_manager.save_session(session_id, session_data)
        return False
    
    def get_agent_collection_name(self) -> str:
        """Get the collection name for this agent."""
        return self.agent_name
    
    def clear_cache(self):
        """Clear the agent's data cache."""
        self._data_cache.clear()