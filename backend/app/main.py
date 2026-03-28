"""
Main FastAPI application to serve the AI Dungeon Master backend.
"""

import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pythonjsonlogger.json import JsonFormatter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.api import websocket_routes

# Local imports
from app.api.routes import all_routers
from app.api.routes.realtime import router as realtime_router
from app.api.routes._shared import limiter
from app.config import init_settings
from app.middleware.prompt_shield_middleware import PromptShieldMiddleware
from app.services.campaign_service import campaign_service

# Load environment variables
load_dotenv()

# Configure structured JSON logging


def configure_logging() -> None:
    """Set up structured JSON logging on the root logger."""
    log_level = getattr(logging, os.getenv("APP_LOG_LEVEL", "INFO").upper())
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        JsonFormatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(module)s %(funcName)s"
        )
    )
    logging.root.handlers = [handler]
    logging.root.setLevel(log_level)


configure_logging()

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:  # noqa: ANN401
        """Add security headers to the response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Handle application lifespan events."""
    # Startup
    logger.info("Initializing configuration...")
    init_settings()  # Load configuration once at startup

    logger.info("Running database migrations...")
    from app.migration_runner import run_migrations

    run_migrations()

    logger.info("Creating default campaign templates...")
    campaign_service.create_template_campaigns()

    logger.info("Application startup complete.")

    yield

    # Shutdown (currently no cleanup needed)
    logger.info("Application shutdown complete.")


# Determine root_path based on environment
# In production (Azure Container Apps), routes are served under /api prefix
# In development/testing, no prefix is used
is_production = bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("CONTAINER_APP_NAME"))
root_path = "/api" if is_production else ""

# Create FastAPI app
app = FastAPI(
    title="AI Dungeon Master API",
    description="Backend API for the AI Dungeon Master application",
    version="0.1.0",
    lifespan=lifespan,
    root_path=root_path,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Prompt injection detection middleware
app.add_middleware(PromptShieldMiddleware)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware - configured via environment variable
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler - prevents internal details leaking to clients
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a generic error response."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "An internal error occurred"}
    )


# Include routers
for _router in all_routers:
    app.include_router(_router, prefix="/game")
app.include_router(websocket_routes.router)
app.include_router(realtime_router)


# Health check endpoint
@app.get("/health")
@limiter.limit("120/minute")
async def health_check(request: Request) -> dict[str, Any]:  # noqa: ARG001
    return {"status": "ok", "version": "0.1.0"}


@app.get("/health/dependencies")
@limiter.limit("120/minute")
async def health_dependencies(request: Request) -> dict[str, str]:  # noqa: ARG001
    """Return the health status of external dependencies and the circuit breaker."""
    from app.agent_client_setup import agent_client_manager
    from app.agents.base_agent import azure_circuit_breaker

    # Azure OpenAI status
    cb_state = azure_circuit_breaker.current_state  # "closed", "open", "half-open"
    if agent_client_manager.is_fallback_mode():
        azure_status = "unavailable"
    elif cb_state == "open":
        azure_status = "degraded"
    else:
        azure_status = "healthy"

    # Database status — attempt a lightweight query
    try:
        from sqlalchemy import text

        from app.database import get_session_local

        session_factory = get_session_local()
        db = session_factory()
        try:
            db.execute(text("SELECT 1"))
            db_status = "healthy"
        finally:
            db.close()
    except Exception:
        db_status = "unavailable"

    return {
        "azure_openai": azure_status,
        "database": db_status,
        "circuit_breaker_state": cb_state,
    }


# Root endpoint
@app.get("/")
async def root() -> dict[str, Any]:
    return {"message": "Welcome to the AI Dungeon Master API"}


if __name__ == "__main__":
    # Development server defaults to all interfaces for convenience
    # Production should use specific interface via APP_HOST env var
    host = os.getenv("APP_HOST", "0.0.0.0")  # noqa: S104
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
