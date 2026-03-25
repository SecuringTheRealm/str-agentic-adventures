"""
Main FastAPI application to serve the AI Dungeon Master backend.
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

# Local imports
from app.api import game_routes, websocket_routes
from app.config import init_settings
from app.services.campaign_service import campaign_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("APP_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):  # noqa: ANN001
        """Add security headers to the response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(game_routes.router, prefix="/game")
app.include_router(websocket_routes.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Dungeon Master API"}


if __name__ == "__main__":
    # Development server defaults to all interfaces for convenience
    # Production should use specific interface via APP_HOST env var
    host = os.getenv("APP_HOST", "0.0.0.0")  # noqa: S104
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
