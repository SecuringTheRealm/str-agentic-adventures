"""Middleware that checks user input for prompt injection via PromptShieldService."""

import json
import logging

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.prompt_shield_service import prompt_shield_service

logger = logging.getLogger(__name__)

# Path prefixes that should be checked for prompt injection
_GUARDED_PREFIXES = ("/game/",)


def _should_check(request: Request) -> bool:
    """Return True if this request should be checked for prompt injection."""
    if request.method != "POST":
        return False
    return any(request.url.path.startswith(p) for p in _GUARDED_PREFIXES)


class PromptShieldMiddleware(BaseHTTPMiddleware):
    """Check POST bodies to game endpoints for prompt injection attacks.

    Skips WebSocket requests — BaseHTTPMiddleware's dispatch breaks the
    WebSocket handshake if it calls ``call_next`` on a WS connection.
    """

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        """Intercept requests and check for prompt injection."""
        # BaseHTTPMiddleware cannot forward WebSocket connections through
        # call_next; let them pass through untouched (see issue #618).
        if request.scope.get("type") == "websocket":
            return await call_next(request)

        if not _should_check(request):
            return await call_next(request)

        # Fail open if service is not configured
        if not prompt_shield_service.is_configured():
            return await call_next(request)

        # Read and parse the request body
        try:
            body_bytes = await request.body()
            body = json.loads(body_bytes)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Can't parse body — let the route handler deal with it
            return await call_next(request)

        # Extract user text from the request body
        user_text = body.get("message") or body.get("input") or body.get("text")
        if not user_text or not isinstance(user_text, str):
            return await call_next(request)

        # Check for prompt injection
        try:
            result = await prompt_shield_service.check_user_input(user_text)
        except Exception:
            logger.exception("Prompt shield check failed — failing open")
            return await call_next(request)

        if result.attack_detected:
            logger.warning(
                "Prompt injection attack blocked by middleware on %s",
                request.url.path,
            )
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Your message could not be processed. "
                    "Please rephrase and try again."
                },
            )

        return await call_next(request)
