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
from app.api import websocket_routes
from app.database import init_db
from app.services.campaign_service import campaign_service
from app.config import init_settings

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

# Initialize database and create templates on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default templates."""
    logger.info("Initializing configuration...")
    init_settings()  # Load configuration once at startup
    
    logger.info("Initializing database...")
    init_db()
    
    logger.info("Creating default campaign templates...")
    campaign_service.create_template_campaigns()
    
    logger.info("Application startup complete.")

# Include routers
app.include_router(game_routes.router, prefix="/api/game")
app.include_router(websocket_routes.router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Dungeon Master API"}

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"

    uvicorn.run("app.main:app", host=host, port=port, reload=debug)
