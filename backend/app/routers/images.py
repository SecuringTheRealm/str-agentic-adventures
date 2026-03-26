"""Image generation API routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.agents.artist_agent import get_artist
from app.agents.combat_cartographer_agent import get_combat_cartographer
from app.api.routes._shared import limiter
from app.image_budget import ImageBudgetTracker

logger = logging.getLogger(__name__)

router = APIRouter(tags=["images"])

# ---------------------------------------------------------------------------
# Per-session image budget – initialised from config on first use
# ---------------------------------------------------------------------------
_image_budget: ImageBudgetTracker | None = None


def _get_image_budget() -> ImageBudgetTracker:
    """Return the singleton ImageBudgetTracker, creating it on first call."""
    global _image_budget
    if _image_budget is None:
        from app.config import get_settings

        cfg = get_settings()
        _image_budget = ImageBudgetTracker(
            max_images=cfg.max_images_per_session,
            window_minutes=cfg.image_session_window_minutes,
        )
    return _image_budget


@router.post("/generate-image", response_model=dict[str, Any])
@limiter.limit("5/minute")
async def generate_image(  # noqa: ARG001
    request: Request, image_request: dict[str, Any],
) -> dict[str, Any]:
    """Generate an image based on the request details.

    Accepts an optional ``session_id`` field in the request body.  Each session
    is limited to ``max_images_per_session`` DALL-E calls per rolling
    ``image_session_window_minutes`` window (configurable via environment
    variables).  Requests that exceed the budget receive a 429 response.
    """
    try:
        session_id = str(image_request.get("session_id") or "anonymous")
        budget = _get_image_budget()
        allowed, remaining = budget.check_and_record(session_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Image budget exceeded. You may generate at most "
                    f"{budget.max_images} image(s) per "
                    f"{budget.window.seconds // 60}-minute session."
                ),
            )

        image_type = image_request.get("image_type")
        details = image_request.get("details", {})

        if image_type == "character_portrait":
            result = await get_artist().generate_character_portrait(details)
        elif image_type == "scene_illustration":
            result = await get_artist().illustrate_scene(details)
        elif image_type == "item_visualization":
            result = await get_artist().create_item_visualization(details)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image type: {image_type}",
            )

        result["images_remaining"] = remaining
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}",
        ) from e


@router.post("/battle-map", response_model=dict[str, Any])
@limiter.limit("5/minute")
async def generate_battle_map(  # noqa: ARG001
    request: Request, map_request: dict[str, Any],
) -> dict[str, Any]:
    """Generate a battle map based on environment details.

    Accepts an optional ``session_id`` field in the request body.  The same
    per-session image budget used by ``/generate-image`` applies here.
    """
    try:
        session_id = str(map_request.get("session_id") or "anonymous")
        budget = _get_image_budget()
        allowed, remaining = budget.check_and_record(session_id)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Image budget exceeded. You may generate at most "
                    f"{budget.max_images} image(s) per "
                    f"{budget.window.seconds // 60}-minute session."
                ),
            )

        environment = map_request.get("environment", {})
        combat_context = map_request.get("combat_context")

        result = await get_combat_cartographer().generate_battle_map(
            environment, combat_context
        )
        result["images_remaining"] = remaining
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate battle map: {str(e)}",
        ) from e
