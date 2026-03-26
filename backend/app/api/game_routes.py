"""Backward-compatible re-exports.

New code should import from app.api.routes.* modules directly.
This module is kept so that existing tests and imports continue to work.
"""

from fastapi import APIRouter

# Re-export agent getters so that existing test patches still resolve
from app.agents.artist_agent import get_artist  # noqa: F401
from app.agents.combat_cartographer_agent import get_combat_cartographer  # noqa: F401
from app.agents.dungeon_master_agent import get_dungeon_master  # noqa: F401
from app.agents.narrator_agent import get_narrator  # noqa: F401
from app.agents.scribe_agent import get_scribe  # noqa: F401
from app.api.routes import all_routers

# Re-export specific functions used by tests
from app.api.routes.spell_routes import (  # noqa: F401
    _calculate_spell_effects,
    _get_spell_data,
    cast_spell_in_combat,
)

# Legacy single router that aggregates all domain routers
router = APIRouter(tags=["game"])
for _r in all_routers:
    router.include_router(_r)
