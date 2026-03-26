"""Simple SQLAlchemy database setup for persistent storage."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()

# Lazy singletons - created on first use (after .env is loaded)
_engine = None
_SessionLocal = None


def _resolve_database_url() -> str:
    """Build the database URL from environment variables."""
    database_host = os.getenv("DATABASE_HOST")
    database_name = os.getenv("DATABASE_NAME", "appdb")
    database_user = os.getenv("DATABASE_USER")
    database_password = os.getenv("DATABASE_PASSWORD")

    if database_host:
        if not database_user or not database_password:
            return f"postgresql://{database_host}/{database_name}"
        return f"postgresql://{database_user}:{database_password}@{database_host}/{database_name}"
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    return "sqlite:///./app.db"


def get_engine():
    """Get or create the SQLAlchemy engine (lazy singleton)."""
    global _engine
    if _engine is None:
        database_url = _resolve_database_url()
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        _engine = create_engine(database_url, connect_args=connect_args)
    return _engine


def get_session_local():
    """Get or create the sessionmaker (lazy singleton)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


# Backward-compatible module-level name used by init_db() and migrations
# This is a property-like that defers to the lazy getter
class _EngineProxy:
    """Proxy so that `database.engine` still works for migrations."""
    def __getattr__(self, name):
        return getattr(get_engine(), name)

engine = _EngineProxy()


def get_session() -> Generator:
    """Yield a database session. Use with FastAPI Depends()."""
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session_context():
    """Context manager for database sessions in non-route code.

    Use this instead of `with next(get_session()) as db:` which leaks sessions.
    """
    session_local = get_session_local()
    db = session_local()
    try:
        yield db
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_session)]
"""FastAPI dependency for injecting a SQLAlchemy database session.

Follows the same pattern as ``ConfigDep``. Use as a type annotation in route
parameters::

    async def my_route(db: DbDep) -> ...:
        ...
"""


def init_db() -> None:
    """Create database tables if they do not exist."""
    from app.models import db_models  # noqa: F401
    Base.metadata.create_all(bind=get_engine())
