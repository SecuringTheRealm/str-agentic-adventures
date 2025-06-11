"""
Simple test API for battle map system.
"""
from fastapi import FastAPI, HTTPException, status
from typing import Dict, Any
import uvicorn

# Simple import to avoid dependency issues
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.combat_cartographer_agent import combat_cartographer

app = FastAPI(title="Battle Map Test API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Battle Map Test API"}

@app.post("/battle-map")
async def generate_battle_map(map_request: Dict[str, Any]):
    """Generate a battle map based on environment details."""
    try:
        environment = map_request.get("environment", {})
        combat_context = map_request.get("combat_context")
        
        battle_map = await combat_cartographer.generate_battle_map(environment, combat_context)
        
        return battle_map
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}"
        )

@app.get("/battle-map/templates")
async def get_map_templates():
    """Get available battle map templates."""
    try:
        templates = await combat_cartographer.get_map_templates()
        return templates
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get map templates: {str(e)}"
        )

@app.post("/battle-map/{map_id}/update")
async def update_battle_map(map_id: str, update_request: Dict[str, Any]):
    """Update a battle map with combat state."""
    try:
        combat_state = update_request.get("combat_state", {})
        
        updated_map = await combat_cartographer.update_map_with_combat_state(map_id, combat_state)
        
        if "error" in updated_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=updated_map["error"]
            )
        
        return updated_map
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update battle map: {str(e)}"
        )

@app.post("/battle-map/{map_id}/variation")
async def generate_map_variation(map_id: str, variation_request: Dict[str, Any]):
    """Generate a variation of an existing battle map."""
    try:
        variation_type = variation_request.get("variation_type", "minor")
        
        variation_map = await combat_cartographer.generate_map_variation(map_id, variation_type)
        
        if "error" in variation_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=variation_map["error"]
            )
        
        return variation_map
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate map variation: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)