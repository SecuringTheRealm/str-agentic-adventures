"""
Abstract interface for persistence layer.
Provides a common interface for different storage backends.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json


class PersistenceInterface(ABC):
    """Abstract interface for data persistence operations."""
    
    @abstractmethod
    async def save_data(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """
        Save data to the specified collection with the given key.
        
        Args:
            collection: The collection/namespace to store data in
            key: The unique identifier for this data
            data: The data to store
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def load_data(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """
        Load data from the specified collection with the given key.
        
        Args:
            collection: The collection/namespace to load data from
            key: The unique identifier for the data
            
        Returns:
            Optional[Dict[str, Any]]: The data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_data(self, collection: str, key: str) -> bool:
        """
        Delete data from the specified collection with the given key.
        
        Args:
            collection: The collection/namespace to delete data from
            key: The unique identifier for the data
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_keys(self, collection: str) -> List[str]:
        """
        List all keys in the specified collection.
        
        Args:
            collection: The collection/namespace to list keys from
            
        Returns:
            List[str]: List of keys in the collection
        """
        pass
    
    @abstractmethod
    async def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Save complete session data.
        
        Args:
            session_id: Unique identifier for the session
            session_data: Complete session state data
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load complete session data.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Optional[Dict[str, Any]]: Session data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_sessions(self) -> List[str]:
        """
        List all available session IDs.
        
        Returns:
            List[str]: List of session IDs
        """
        pass