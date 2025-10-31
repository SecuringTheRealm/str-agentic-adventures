"""
Main FastAPI application to serve the AI Dungeon Master backend.
"""

import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
