"""
Session manager for handling game session persistence.
Coordinates saving and loading of complete game state.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from .interface import PersistenceInterface
from .file_storage import FilePersistence

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages game session persistence and state coordination."""
    
    def __init__(self, persistence: Optional[PersistenceInterface] = None):
        """
        Initialize session manager with persistence backend.
        
        Args:
            persistence: Persistence backend to use. Defaults to FilePersistence.
        """
        self.persistence = persistence or FilePersistence()
        self._current_session_id = None
    
    async def create_session(self, campaign_id: str, session_name: str = None) -> str:
        """
        Create a new game session.
        
        Args:
            campaign_id: ID of the campaign this session belongs to
            session_name: Optional name for the session
            
        Returns:
            str: The new session ID
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "id": session_id,
            "campaign_id": campaign_id,
            "name": session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.now().isoformat(),
            "last_saved": datetime.now().isoformat(),
            "characters": {},
            "narrative_memory": {
                "memories": {},
                "events": [],
                "npcs": {},
                "locations": {}
            },
            "campaign_state": {},
            "session_log": []
        }
        
        success = await self.persistence.save_session(session_id, session_data)
        if success:
            self._current_session_id = session_id
            logger.info(f"Created new session: {session_id}")
            return session_id
        else:
            raise Exception("Failed to create session")
    
    async def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """
        Save session data.
        
        Args:
            session_id: ID of the session to save
            session_data: Complete session state data
            
        Returns:
            bool: True if successful
        """
        # Update last saved timestamp
        session_data["last_saved"] = datetime.now().isoformat()
        
        success = await self.persistence.save_session(session_id, session_data)
        if success:
            logger.info(f"Saved session: {session_id}")
        else:
            logger.error(f"Failed to save session: {session_id}")
        
        return success
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            Optional[Dict[str, Any]]: Session data if found
        """
        session_data = await self.persistence.load_session(session_id)
        if session_data:
            self._current_session_id = session_id
            logger.info(f"Loaded session: {session_id}")
        else:
            logger.warning(f"Session not found: {session_id}")
        
        return session_data
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions with metadata.
        
        Returns:
            List[Dict[str, Any]]: List of session metadata
        """
        session_ids = await self.persistence.list_sessions()
        sessions = []
        
        for session_id in session_ids:
            session_data = await self.persistence.load_session(session_id)
            if session_data:
                # Return minimal metadata
                sessions.append({
                    "id": session_data.get("id", session_id),
                    "name": session_data.get("name", "Unnamed Session"),
                    "campaign_id": session_data.get("campaign_id"),
                    "created_at": session_data.get("created_at"),
                    "last_saved": session_data.get("last_saved")
                })
        
        return sorted(sessions, key=lambda x: x.get("last_saved", ""), reverse=True)
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            bool: True if successful
        """
        # For file persistence, we'd delete the session file
        # For now, we'll use the persistence interface
        # This is a limitation of the current interface - we need to implement session deletion
        try:
            session_data = await self.persistence.load_session(session_id)
            if session_data:
                # Mark as deleted rather than actually deleting for safety
                session_data["deleted"] = True
                session_data["deleted_at"] = datetime.now().isoformat()
                success = await self.persistence.save_session(session_id, session_data)
                if success:
                    logger.info(f"Marked session as deleted: {session_id}")
                return success
            return False
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self._current_session_id
    
    def set_current_session_id(self, session_id: str):
        """Set the current session ID."""
        self._current_session_id = session_id


# Global session manager instance
session_manager = SessionManager()