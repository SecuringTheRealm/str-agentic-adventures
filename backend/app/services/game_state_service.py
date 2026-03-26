"""Service for capturing and restoring full campaign game state."""

import logging
import uuid as _uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.db_models import (
    NPC as NPCDB,
)
from app.models.db_models import (
    Campaign as CampaignDB,
)
from app.models.db_models import (
    Character as CharacterDB,
)
from app.models.db_models import (
    NPCProfileDB,
    NPCRelationshipDB,
)

logger = logging.getLogger(__name__)

# Cap conversation history entries to avoid unbounded save sizes
_MAX_CONVERSATION_ENTRIES = 50


class GameStateService:
    """Serialise and restore full campaign game state."""

    def capture_state(self, campaign_id: str, db: Session) -> dict[str, Any]:
        """Capture complete game state for a campaign.

        Returns dict with: campaign_data, characters, npcs, npc_profiles,
        npc_relationships, combat_state (if present in campaign data),
        conversation_history (recent N entries), and a capture timestamp.
        """
        campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
        if campaign is None:
            raise ValueError(f"Campaign {campaign_id} not found")

        campaign_data: dict[str, Any] = campaign.data or {}

        # Gather characters referenced in campaign data
        character_ids: list[str] = campaign_data.get("characters", [])
        characters: list[dict[str, Any]] = []
        if character_ids:
            char_rows = (
                db.query(CharacterDB)
                .filter(CharacterDB.id.in_(character_ids))
                .all()
            )
            characters = [
                {"id": c.id, "name": c.name, "data": c.data} for c in char_rows
            ]

        # Gather legacy NPCs linked to this campaign
        npc_rows = (
            db.query(NPCDB).filter(NPCDB.campaign_id == campaign_id).all()
        )
        npcs: list[dict[str, Any]] = [
            {
                "id": n.id,
                "name": n.name,
                "race": n.race,
                "occupation": n.occupation,
                "location": n.location,
                "personality": n.personality,
                "stats": n.stats,
                "relationships": n.relationships,
                "data": n.data,
            }
            for n in npc_rows
        ]

        # Gather game-engine NPC profiles
        profile_rows = (
            db.query(NPCProfileDB)
            .filter(NPCProfileDB.campaign_id == campaign_id)
            .all()
        )
        npc_profiles: list[dict[str, Any]] = [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "personality_traits": p.personality_traits,
                "disposition": p.disposition,
                "location": p.location,
                "is_alive": p.is_alive,
                "conversation_notes": p.conversation_notes,
            }
            for p in profile_rows
        ]

        # Gather NPC relationships for the campaign
        relationship_rows = (
            db.query(NPCRelationshipDB)
            .filter(NPCRelationshipDB.campaign_id == campaign_id)
            .all()
        )
        npc_relationships: list[dict[str, Any]] = [
            {
                "id": r.id,
                "npc_id": r.npc_id,
                "campaign_id": r.campaign_id,
                "disposition_score": r.disposition_score,
                "interactions_count": r.interactions_count,
                "key_events": r.key_events,
                "last_interaction": r.last_interaction,
            }
            for r in relationship_rows
        ]

        # Extract combat state from campaign data (if an encounter is active)
        combat_state: dict[str, Any] | None = campaign_data.get("combat_state")

        # Extract recent conversation history from session_log
        session_log: list[dict[str, Any]] = campaign_data.get("session_log", [])
        conversation_history = session_log[-_MAX_CONVERSATION_ENTRIES:]

        return {
            "version": 1,
            "captured_at": datetime.now(UTC).isoformat(),
            "campaign_data": campaign_data,
            "characters": characters,
            "npcs": npcs,
            "npc_profiles": npc_profiles,
            "npc_relationships": npc_relationships,
            "combat_state": combat_state,
            "conversation_history": conversation_history,
        }

    def restore_state(
        self, campaign_id: str, state_data: dict[str, Any], db: Session
    ) -> dict[str, Any]:
        """Restore a previously captured game state.

        Overwrites the campaign's data blob and recreates characters, NPCs,
        profiles and relationships from the saved state.

        Returns a summary of what was restored.
        """
        campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
        if campaign is None:
            raise ValueError(f"Campaign {campaign_id} not found")

        restored: dict[str, Any] = {
            "campaign": False,
            "characters_restored": 0,
            "npcs_restored": 0,
            "npc_profiles_restored": 0,
            "npc_relationships_restored": 0,
        }

        # --- Campaign data ---
        saved_campaign = state_data.get("campaign_data")
        if saved_campaign is not None:
            campaign.data = saved_campaign
            # Sync top-level ORM columns that mirror JSON fields
            campaign.name = saved_campaign.get("name", campaign.name)
            campaign.setting = saved_campaign.get("setting", campaign.setting)
            campaign.tone = saved_campaign.get("tone", campaign.tone)
            campaign.description = saved_campaign.get(
                "description", campaign.description
            )
            campaign.updated_at = datetime.now(UTC)
            restored["campaign"] = True

        # --- Characters ---
        saved_characters: list[dict[str, Any]] = state_data.get("characters", [])
        for char_data in saved_characters:
            char_id = char_data.get("id")
            if not char_id:
                continue
            existing = db.query(CharacterDB).filter(CharacterDB.id == char_id).first()
            if existing:
                existing.name = char_data.get("name", existing.name)
                existing.data = char_data.get("data", existing.data)
            else:
                db.add(
                    CharacterDB(
                        id=char_id,
                        name=char_data.get("name", "Unknown"),
                        data=char_data.get("data", {}),
                    )
                )
            restored["characters_restored"] += 1

        # --- Legacy NPCs ---
        # Remove existing NPCs for the campaign, then re-insert from state
        db.query(NPCDB).filter(NPCDB.campaign_id == campaign_id).delete()
        saved_npcs: list[dict[str, Any]] = state_data.get("npcs", [])
        for npc_data in saved_npcs:
            npc_id = npc_data.get("id", str(_uuid.uuid4()))
            db.add(
                NPCDB(
                    id=npc_id,
                    name=npc_data.get("name", "Unknown"),
                    race=npc_data.get("race"),
                    occupation=npc_data.get("occupation"),
                    location=npc_data.get("location"),
                    campaign_id=campaign_id,
                    personality=npc_data.get("personality", {}),
                    stats=npc_data.get("stats"),
                    relationships=npc_data.get("relationships", []),
                    data=npc_data.get("data", {}),
                )
            )
            restored["npcs_restored"] += 1

        # --- NPC profiles ---
        db.query(NPCProfileDB).filter(
            NPCProfileDB.campaign_id == campaign_id
        ).delete()
        saved_profiles: list[dict[str, Any]] = state_data.get("npc_profiles", [])
        for prof in saved_profiles:
            prof_id = prof.get("id", str(_uuid.uuid4()))
            db.add(
                NPCProfileDB(
                    id=prof_id,
                    campaign_id=campaign_id,
                    name=prof.get("name", "Unknown"),
                    description=prof.get("description"),
                    personality_traits=prof.get("personality_traits", []),
                    disposition=prof.get("disposition", "neutral"),
                    location=prof.get("location"),
                    is_alive=prof.get("is_alive", True),
                    conversation_notes=prof.get("conversation_notes", []),
                )
            )
            restored["npc_profiles_restored"] += 1

        # --- NPC relationships ---
        db.query(NPCRelationshipDB).filter(
            NPCRelationshipDB.campaign_id == campaign_id
        ).delete()
        saved_rels: list[dict[str, Any]] = state_data.get("npc_relationships", [])
        for rel in saved_rels:
            rel_id = rel.get("id", str(_uuid.uuid4()))
            db.add(
                NPCRelationshipDB(
                    id=rel_id,
                    npc_id=rel.get("npc_id", ""),
                    campaign_id=campaign_id,
                    disposition_score=rel.get("disposition_score", 0),
                    interactions_count=rel.get("interactions_count", 0),
                    key_events=rel.get("key_events", []),
                    last_interaction=rel.get("last_interaction"),
                )
            )
            restored["npc_relationships_restored"] += 1

        db.commit()

        logger.info(
            "Restored game state for campaign %s: %s",
            campaign_id,
            restored,
        )
        return restored

    def get_save_summary(self, state_data: dict[str, Any]) -> dict[str, Any]:
        """Generate a human-readable summary of a save state (for UI display)."""
        campaign_data = state_data.get("campaign_data", {})
        characters = state_data.get("characters", [])
        npcs = state_data.get("npcs", [])
        npc_profiles = state_data.get("npc_profiles", [])
        conversation_history = state_data.get("conversation_history", [])
        combat_state = state_data.get("combat_state")

        character_names = [c.get("name", "Unknown") for c in characters]
        npc_names = [n.get("name", "Unknown") for n in npcs]
        profile_names = [p.get("name", "Unknown") for p in npc_profiles]

        return {
            "campaign_name": campaign_data.get("name", "Unknown Campaign"),
            "setting": campaign_data.get("setting", ""),
            "current_location": campaign_data.get("current_location", ""),
            "characters": character_names,
            "character_count": len(characters),
            "npc_count": len(npcs) + len(npc_profiles),
            "npc_names": npc_names + profile_names,
            "conversation_entries": len(conversation_history),
            "has_active_combat": combat_state is not None,
            "captured_at": state_data.get("captured_at", ""),
            "version": state_data.get("version", 1),
        }


# Module-level singleton
game_state_service = GameStateService()
