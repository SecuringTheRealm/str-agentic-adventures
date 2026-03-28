"""Battle map tile-grid API routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.map_models import BattleMapData
from app.services.tile_grid_generator import TileGridGenerator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["maps"])

# Singleton generator
_generator = TileGridGenerator()

# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class EnvironmentSpec(BaseModel):
    location: str = "dungeon"
    terrain: str = "dungeon"
    size: str = "medium"
    features: list[str] = Field(default_factory=list)
    hazards: list[str] = Field(default_factory=list)


class StructuredMapRequest(BaseModel):
    environment: EnvironmentSpec = Field(default_factory=EnvironmentSpec)
    combat_context: dict[str, Any] | None = None
    seed: int | None = None


# ---------------------------------------------------------------------------
# Size presets (matches map_generation_plugin conventions)
# ---------------------------------------------------------------------------

_SIZE_DIMENSIONS: dict[str, tuple[int, int]] = {
    "small": (15, 15),
    "medium": (20, 20),
    "large": (30, 30),
}


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post("/battle-map/structured", response_model=BattleMapData)
async def generate_structured_battle_map(
    body: StructuredMapRequest,
) -> BattleMapData:
    """Generate a tile-grid battle map with populated tiles, entities, and tokens.

    Returns the full ``BattleMapData`` model (including the 2-D tile grid) as JSON.
    """
    try:
        env = body.environment
        width, height = _SIZE_DIMENSIONS.get(env.size, _SIZE_DIMENSIONS["medium"])

        context: dict[str, Any] = {
            "location": env.location,
            "terrain": env.terrain,
            "features": env.features,
            "hazards": env.hazards,
        }
        if body.combat_context:
            context["combat"] = body.combat_context

        return _generator.generate_grid(
            width=width,
            height=height,
            environment_context=context,
            seed=body.seed,
        )

    except Exception as e:
        logger.exception("Failed to generate structured battle map: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Map generation failed: {e}",
        ) from e
