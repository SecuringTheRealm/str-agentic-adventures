"""
API routes for NPC management in the AI Dungeon Master application.
"""
from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from app.models.game_models import (
    CreateNPCRequest,
    UpdateNPCRequest,
    NPCInteractionRequest,
    NPC
)
from app.plugins.npc_management_plugin import NPCManagementPlugin

router = APIRouter(tags=["npcs"])

# Initialize NPC management plugin
npc_manager = NPCManagementPlugin()

@router.post("/npc", response_model=Dict[str, Any])
async def create_npc(npc_data: CreateNPCRequest):
    """Create a new NPC."""
    try:
        result = npc_manager.create_npc(
            name=npc_data.name,
            description=npc_data.description,
            race=npc_data.race.value,
            role=npc_data.role.value,
            location=npc_data.current_location,
            personality=npc_data.personality.value if npc_data.personality else "neutral"
        )

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NPC: {str(e)}"
        )

@router.get("/npc/{npc_id}", response_model=Dict[str, Any])
async def get_npc(npc_id: str):
    """Get NPC details by ID."""
    try:
        result = npc_manager.get_npc_details(npc_id)
        
        if result["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )
        elif result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NPC: {str(e)}"
        )

@router.put("/npc/{npc_id}", response_model=Dict[str, Any])
async def update_npc(npc_id: str, update_data: UpdateNPCRequest):
    """Update NPC details."""
    try:
        # First check if NPC exists
        result = npc_manager.get_npc_details(npc_id)
        if result["status"] == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )

        # Get current NPC data
        npc_data = result["npc"]
        
        # Update fields if provided
        if update_data.name:
            npc_data["name"] = update_data.name
        if update_data.description:
            npc_data["description"] = update_data.description
        if update_data.current_location:
            npc_data["current_location"] = update_data.current_location
        if update_data.is_available is not None:
            npc_data["is_available"] = update_data.is_available
        if update_data.behavior:
            npc_data["behavior"] = update_data.behavior.model_dump()

        # Update the NPC in storage
        npc_manager.npcs[npc_id] = NPC(**npc_data)
        
        return {
            "status": "success",
            "message": f"NPC {npc_id} updated successfully",
            "npc": npc_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update NPC: {str(e)}"
        )

@router.post("/npc/{npc_id}/interact", response_model=Dict[str, Any])
async def interact_with_npc(npc_id: str, interaction: NPCInteractionRequest):
    """Generate an interaction with an NPC."""
    try:
        result = npc_manager.generate_npc_response(
            npc_id=npc_id,
            character_id=interaction.character_id,
            player_message=interaction.message or "",
            context=str(interaction.context) if interaction.context else ""
        )

        if result["status"] != "success":
            if result["status"] == "unavailable":
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result["message"]
                )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to interact with NPC: {str(e)}"
        )

@router.put("/npc/{npc_id}/relationship/{character_id}", response_model=Dict[str, Any])
async def update_npc_relationship(
    npc_id: str, 
    character_id: str, 
    relationship_data: Dict[str, Any]
):
    """Update relationship between NPC and character."""
    try:
        result = npc_manager.update_npc_relationship(
            npc_id=npc_id,
            character_id=character_id,
            affection_change=relationship_data.get("affection_change", 0),
            trust_change=relationship_data.get("trust_change", 0),
            respect_change=relationship_data.get("respect_change", 0),
            event_description=relationship_data.get("event_description", "")
        )

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update relationship: {str(e)}"
        )

@router.get("/npcs/location/{location}", response_model=Dict[str, Any])
async def get_npcs_in_location(location: str):
    """Get all NPCs in a specific location."""
    try:
        result = npc_manager.get_npcs_in_location(location)

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NPCs in location: {str(e)}"
        )

@router.get("/npcs", response_model=Dict[str, Any])
async def list_all_npcs():
    """List all NPCs in the system."""
    try:
        npcs = []
        for npc_id, npc in npc_manager.npcs.items():
            npcs.append({
                "id": npc.id,
                "name": npc.name,
                "description": npc.description,
                "role": npc.role.value,
                "personality": npc.personality.value,
                "current_location": npc.current_location,
                "is_available": npc.is_available,
                "is_alive": npc.is_alive
            })

        return {
            "status": "success",
            "npcs": npcs,
            "count": len(npcs)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list NPCs: {str(e)}"
        )