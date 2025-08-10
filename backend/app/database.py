"""Simple SQLAlchemy database setup for persistent storage."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database URL configuration
# Priority: DATABASE_URL env var > PostgreSQL params > SQLite fallback
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

if DATABASE_HOST:
    # PostgreSQL configuration (production)
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"
    if not DATABASE_USER or not DATABASE_PASSWORD:
        # Use Azure AD authentication if no password provided
        DATABASE_URL = f"postgresql://{DATABASE_HOST}/{DATABASE_NAME}"
elif os.getenv("DATABASE_URL"):
    # Use explicit DATABASE_URL if provided
    DATABASE_URL = os.getenv("DATABASE_URL")
else:
    # SQLite fallback (development)
    DATABASE_URL = "sqlite:///./app.db"

# Create engine with appropriate configuration
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_session() -> Generator:
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    from app.models import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
