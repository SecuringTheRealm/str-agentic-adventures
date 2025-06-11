"""
File-based persistence implementation.
Simple JSON file storage for session and game state data.
"""
import os
import json
import aiofiles
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .interface import PersistenceInterface

logger = logging.getLogger(__name__)


class FilePersistence(PersistenceInterface):
    """File-based storage implementation using JSON files."""
    
    def __init__(self, base_path: str = "data"):
        """
        Initialize file persistence with base storage path.
        
        Args:
            base_path: Base directory for storing data files
        """
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"
        self.collections_path = self.base_path / "collections"
        
        # Create directories if they don't exist
        self.base_path.mkdir(exist_ok=True)
        self.sessions_path.mkdir(exist_ok=True)
        self.collections_path.mkdir(exist_ok=True)
    
    def _get_collection_path(self, collection: str) -> Path:
        """Get the directory path for a collection."""
        path = self.collections_path / collection
        path.mkdir(exist_ok=True)
        return path
    
    def _get_data_file_path(self, collection: str, key: str) -> Path:
        """Get the file path for a specific data entry."""
        return self._get_collection_path(collection) / f"{key}.json"
    
    def _get_session_file_path(self, session_id: str) -> Path:
        """Get the file path for a session."""
        return self.sessions_path / f"{session_id}.json"
    
    async def save_data(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Save data to a JSON file."""
        try:
            file_path = self._get_data_file_path(collection, key)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(data, indent=2, default=str))
            
            logger.debug(f"Saved data to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving data to {collection}/{key}: {str(e)}")
            return False
    
    async def load_data(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Load data from a JSON file."""
        try:
            file_path = self._get_data_file_path(collection, key)
            
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
            
            logger.debug(f"Loaded data from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading data from {collection}/{key}: {str(e)}")
            return None
    
    async def delete_data(self, collection: str, key: str) -> bool:
        """Delete a data file."""
        try:
            file_path = self._get_data_file_path(collection, key)
            
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted data file {file_path}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting data from {collection}/{key}: {str(e)}")
            return False
    
    async def list_keys(self, collection: str) -> List[str]:
        """List all keys in a collection."""
        try:
            collection_path = self._get_collection_path(collection)
            
            keys = []
            for file_path in collection_path.glob("*.json"):
                keys.append(file_path.stem)
            
            return sorted(keys)
        except Exception as e:
            logger.error(f"Error listing keys in {collection}: {str(e)}")
            return []
    
    async def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Save complete session data."""
        try:
            file_path = self._get_session_file_path(session_id)
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(session_data, indent=2, default=str))
            
            logger.info(f"Saved session {session_id} to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving session {session_id}: {str(e)}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load complete session data."""
        try:
            file_path = self._get_session_file_path(session_id)
            
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                session_data = json.loads(content)
            
            logger.info(f"Loaded session {session_id} from {file_path}")
            return session_data
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {str(e)}")
            return None
    
    async def list_sessions(self) -> List[str]:
        """List all available session IDs."""
        try:
            session_ids = []
            for file_path in self.sessions_path.glob("*.json"):
                session_ids.append(file_path.stem)
            
            return sorted(session_ids)
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            return []