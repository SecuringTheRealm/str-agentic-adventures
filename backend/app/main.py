"""
Main FastAPI application to serve the AI Dungeon Master backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv

# Local imports
from app.api import game_routes
from app.core.service_manager import orchestration_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("APP_LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Dungeon Master API",
    description="Backend API for the AI Dungeon Master application",
    version="0.1.0",
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
app.include_router(game_routes.router, prefix="/api/game")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize orchestration services on startup."""
    logger.info("Starting AI Dungeon Master API")
    await orchestration_service.start()

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean up orchestration services on shutdown."""
    logger.info("Shutting down AI Dungeon Master API")
    await orchestration_service.stop()

# Health check endpoint
@app.get("/health")
async def health_check():
    system_status = await orchestration_service.get_system_status()
    return {
        "status": "ok", 
        "version": "0.1.0",
        "orchestration": system_status
    }

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Dungeon Master API"}

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"

    uvicorn.run("main:app", host=host, port=port, reload=debug)
