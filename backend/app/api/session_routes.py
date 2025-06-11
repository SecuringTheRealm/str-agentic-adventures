"""
API routes for session management.
Handles saving, loading, and managing game sessions.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from app.models.game_models import (
    CreateSessionRequest,
    SaveSessionRequest,
    SessionMetadata,
    GameSession
)
from app.persistence import session_manager

router = APIRouter(tags=["sessions"])

@router.post("/sessions", response_model=Dict[str, str])
async def create_session(request: CreateSessionRequest):
    """Create a new game session."""
    try:
        session_id = await session_manager.create_session(
            campaign_id=request.campaign_id,
            session_name=request.name
        )
        return {"session_id": session_id, "message": "Session created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )

@router.get("/sessions", response_model=List[SessionMetadata])
async def list_sessions():
    """List all available sessions."""
    try:
        sessions = await session_manager.list_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        )

@router.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """Get a specific session by ID."""
    try:
        session_data = await session_manager.load_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        return session_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session: {str(e)}"
        )

@router.post("/sessions/{session_id}/save", response_model=Dict[str, str])
async def save_session(session_id: str, session_data: Dict[str, Any]):
    """Save session data."""
    try:
        success = await session_manager.save_session(session_id, session_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save session"
            )
        return {"message": "Session saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save session: {str(e)}"
        )

@router.post("/sessions/{session_id}/load", response_model=Dict[str, Any])
async def load_session(session_id: str):
    """Load and set the current session."""
    try:
        session_data = await session_manager.load_session(session_id)
        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        # Set as current session
        session_manager.set_current_session_id(session_id)
        
        return {
            "message": "Session loaded successfully",
            "session_data": session_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load session: {str(e)}"
        )

@router.delete("/sessions/{session_id}", response_model=Dict[str, str])
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        success = await session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )

@router.get("/sessions/current", response_model=Dict[str, Any])
async def get_current_session():
    """Get the current active session."""
    try:
        current_session_id = session_manager.get_current_session_id()
        if not current_session_id:
            return {"message": "No current session", "session_id": None}
        
        session_data = await session_manager.load_session(current_session_id)
        if not session_data:
            return {"message": "Current session not found", "session_id": current_session_id}
        
        return {
            "session_id": current_session_id,
            "session_data": session_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current session: {str(e)}"
        )