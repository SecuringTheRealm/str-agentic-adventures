"""SQLAlchemy ORM models for persistent storage."""

from __future__ import annotations

from sqlalchemy import Column, JSON, String

from app.database import Base


class Character(Base):
    """Character table for storing character sheets."""

    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
