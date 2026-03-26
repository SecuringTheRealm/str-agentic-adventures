"""Shared utilities for domain route modules."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.image_budget import ImageBudgetTracker

# Rate limiter for AI-calling endpoints
limiter = Limiter(key_func=get_remote_address)

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
