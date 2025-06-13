"""SQLAlchemy ORM models for persistent storage."""

from __future__ import annotations

from sqlalchemy import Column, JSON, String, Boolean, DateTime, Text
from datetime import datetime

from app.database import Base


class Character(Base):
    """Character table for storing character sheets."""

    __tablename__ = "characters"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)


class Campaign(Base):
    """Campaign table for storing campaign data."""

    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    setting = Column(Text, nullable=False)
    tone = Column(String, nullable=False, default="heroic")
    homebrew_rules = Column(JSON, nullable=True, default=list)
    world_description = Column(Text, nullable=True)
    world_art = Column(JSON, nullable=True)
    is_template = Column(Boolean, nullable=False, default=False)
    is_custom = Column(Boolean, nullable=False, default=True)
    template_id = Column(String, nullable=True)  # For cloned campaigns
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    data = Column(JSON, nullable=False)  # Full campaign data
