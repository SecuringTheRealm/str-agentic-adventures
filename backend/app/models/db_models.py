"""SQLAlchemy ORM models for persistent storage."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


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
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
    data = Column(JSON, nullable=False)  # Full campaign data


class NPC(Base):
    """NPC table for storing non-player character data."""

    __tablename__ = "npcs"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    race = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    location = Column(String, nullable=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    personality = Column(JSON, nullable=False, default=dict)
    stats = Column(JSON, nullable=True)
    relationships = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )
    data = Column(JSON, nullable=False)  # Full NPC data


class NPCInteraction(Base):
    """Table for logging NPC interactions."""

    __tablename__ = "npc_interactions"

    id = Column(String, primary_key=True, index=True)
    npc_id = Column(String, ForeignKey("npcs.id"), nullable=False)
    character_id = Column(String, ForeignKey("characters.id"), nullable=True)
    interaction_type = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    outcome = Column(Text, nullable=True)
    relationship_change = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, nullable=False, default=_utcnow)
    data = Column(JSON, nullable=False)  # Full interaction data


class SaveSlot(Base):
    """Save slot table for storing campaign save states."""

    __tablename__ = "save_slots"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    slot_number = Column(Integer, nullable=False)  # 1-5
    name = Column(String, nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)
    play_time_seconds = Column(Integer, nullable=False, default=0)
    interaction_count = Column(Integer, nullable=False, default=0)
    character_level = Column(Integer, nullable=False, default=1)
    current_location = Column(String, nullable=False, default="")
    save_data = Column(JSON, nullable=False, default=dict)  # full state blob


class Spell(Base):
    """Spell table for storing spell definitions and effects."""

    __tablename__ = "spells"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    level = Column(Integer, nullable=False)
    school = Column(String, nullable=False)
    casting_time = Column(String, nullable=False)
    range = Column(String, nullable=False)
    components = Column(JSON, nullable=False)
    duration = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    higher_levels = Column(Text, nullable=True)
    ritual = Column(Boolean, nullable=False, default=False)
    concentration = Column(Boolean, nullable=False, default=False)
    damage_dice = Column(String, nullable=True)
    save_type = Column(String, nullable=True)
    spell_lists = Column(
        JSON, nullable=False, default=list
    )  # Classes that can learn this spell
    data = Column(JSON, nullable=False)  # Additional spell data and effects


class NPCProfileDB(Base):
    """NPCProfile table for game-engine NPC profiles."""

    __tablename__ = "npc_profiles"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    personality_traits = Column(JSON, nullable=False, default=list)
    disposition = Column(String, nullable=False, default="neutral")
    location = Column(String, nullable=True)
    is_alive = Column(Boolean, nullable=False, default=True)
    conversation_notes = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)


class NPCRelationshipDB(Base):
    """NPCRelationship table for tracking NPC disposition within a campaign."""

    __tablename__ = "npc_relationships"

    id = Column(String, primary_key=True, index=True)
    npc_id = Column(String, ForeignKey("npc_profiles.id"), nullable=False, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    disposition_score = Column(Integer, nullable=False, default=0)
    interactions_count = Column(Integer, nullable=False, default=0)
    key_events = Column(JSON, nullable=False, default=list)
    last_interaction = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)

