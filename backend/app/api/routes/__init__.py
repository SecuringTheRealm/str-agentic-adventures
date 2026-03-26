"""Domain-specific route modules for the game API."""

from .ai_routes import router as ai_router
from .campaign_routes import router as campaign_router
from .character_routes import router as character_router
from .combat_routes import router as combat_router
from .dice_routes import router as dice_router
from .item_routes import router as item_router
from .npc_routes import router as npc_router
from .rest_routes import router as rest_router
from .save_routes import router as save_router
from .session_routes import router as session_router
from .spell_routes import router as spell_router

all_routers = [
    character_router,
    campaign_router,
    combat_router,
    spell_router,
    dice_router,
    npc_router,
    ai_router,
    session_router,
    item_router,
    rest_router,
    save_router,
]
