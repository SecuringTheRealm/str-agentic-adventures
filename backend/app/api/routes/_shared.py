"""Shared utilities for domain route modules."""

from slowapi import Limiter
from starlette.requests import Request

from app.image_budget import ImageBudgetTracker


def _get_real_client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For for Container Apps."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For may contain a comma-separated chain; leftmost is the client
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "127.0.0.1"


# Singleton rate limiter — all route modules MUST import this instance
# instead of creating their own Limiter().
# Default limit: 60 requests/minute per IP.
limiter = Limiter(key_func=_get_real_client_ip, default_limits=["60/minute"])

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
