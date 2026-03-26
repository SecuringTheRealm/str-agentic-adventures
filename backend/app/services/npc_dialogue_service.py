"""Service for NPC dialogue context and conversation memory."""

import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.db_models import NPCProfileDB, NPCRelationshipDB
from app.models.game_models import NPCConversationEntry

logger = logging.getLogger(__name__)

# Disposition score bounds
_MIN_DISPOSITION = -100
_MAX_DISPOSITION = 100

# Number of recent conversations to include in dialogue context
_RECENT_CONVERSATION_LIMIT = 10


def _disposition_tone(score: int) -> str:
    """Map a disposition score to a descriptive tone for dialogue generation."""
    if score >= 50:
        return "warm and enthusiastic, treating the party as trusted allies"
    if score >= 20:
        return "friendly and helpful, willing to share information"
    if score >= -19:
        return "polite but guarded, sticking to business"
    if score >= -49:
        return "cold and suspicious, reluctant to cooperate"
    return "openly hostile, dismissive and threatening"


class NPCDialogueService:
    """Manages NPC dialogue context and conversation memory."""

    def get_npc_context(
        self, npc_id: str, campaign_id: str, db: Session
    ) -> dict:
        """Get full NPC context for the narrator agent.

        Returns personality, relationship data, and recent conversations
        so the DM agent can voice this NPC accurately.

        Args:
            npc_id: The NPC profile ID.
            campaign_id: The campaign ID.
            db: SQLAlchemy session.

        Returns:
            Dict with profile, relationship, and recent_conversations keys.
        """
        profile_row = (
            db.query(NPCProfileDB)
            .filter(
                NPCProfileDB.id == npc_id,
                NPCProfileDB.campaign_id == campaign_id,
            )
            .first()
        )
        if profile_row is None:
            return {}

        rel_row = (
            db.query(NPCRelationshipDB)
            .filter(
                NPCRelationshipDB.npc_id == npc_id,
                NPCRelationshipDB.campaign_id == campaign_id,
            )
            .first()
        )

        history: list[dict] = list(profile_row.conversation_history or [])
        recent = history[-_RECENT_CONVERSATION_LIMIT:]

        disposition_score = rel_row.disposition_score if rel_row else 0

        return {
            "name": profile_row.name,
            "description": profile_row.description or "",
            "personality_traits": list(profile_row.personality_traits or []),
            "disposition": profile_row.disposition,
            "disposition_score": disposition_score,
            "disposition_tone": _disposition_tone(disposition_score),
            "location": profile_row.location or "",
            "is_alive": profile_row.is_alive,
            "conversation_notes": list(profile_row.conversation_notes or []),
            "recent_conversations": recent,
            "interactions_count": rel_row.interactions_count if rel_row else 0,
            "key_events": list(rel_row.key_events or []) if rel_row else [],
        }

    def record_conversation(
        self,
        npc_id: str,
        campaign_id: str,
        summary: str,
        disposition_change: int,
        topics: list[str],
        db: Session,
    ) -> None:
        """Record a conversation interaction with an NPC.

        Appends the conversation to the NPC's history, updates
        conversation_notes with the summary, and adjusts the
        relationship disposition score.

        Args:
            npc_id: The NPC profile ID.
            campaign_id: The campaign ID.
            summary: A short summary of the conversation.
            disposition_change: How much the disposition score should shift.
            topics: Key topics discussed.
            db: SQLAlchemy session.
        """
        profile_row = (
            db.query(NPCProfileDB)
            .filter(
                NPCProfileDB.id == npc_id,
                NPCProfileDB.campaign_id == campaign_id,
            )
            .first()
        )
        if profile_row is None:
            return

        entry = NPCConversationEntry(
            timestamp=datetime.now(UTC).isoformat(),
            summary=summary,
            disposition_change=disposition_change,
            topics=topics,
        )

        # Append to conversation history
        history: list[dict] = list(profile_row.conversation_history or [])
        history.append(entry.model_dump())
        profile_row.conversation_history = history

        # Append summary to conversation_notes
        notes: list[str] = list(profile_row.conversation_notes or [])
        notes.append(summary)
        profile_row.conversation_notes = notes

        # Update or create relationship
        now_str = datetime.now(UTC).isoformat()
        rel_row = (
            db.query(NPCRelationshipDB)
            .filter(
                NPCRelationshipDB.npc_id == npc_id,
                NPCRelationshipDB.campaign_id == campaign_id,
            )
            .first()
        )
        if rel_row is None:
            import uuid

            rel_row = NPCRelationshipDB(
                id=str(uuid.uuid4()),
                npc_id=npc_id,
                campaign_id=campaign_id,
                disposition_score=max(
                    _MIN_DISPOSITION,
                    min(_MAX_DISPOSITION, disposition_change),
                ),
                interactions_count=1,
                key_events=[summary] if summary else [],
                last_interaction=now_str,
            )
            db.add(rel_row)
        else:
            new_score = rel_row.disposition_score + disposition_change
            rel_row.disposition_score = max(
                _MIN_DISPOSITION, min(_MAX_DISPOSITION, new_score)
            )
            rel_row.interactions_count = (rel_row.interactions_count or 0) + 1
            rel_row.last_interaction = now_str
            existing_events: list[str] = list(rel_row.key_events or [])
            if summary:
                existing_events.append(summary)
            rel_row.key_events = existing_events

        db.commit()

    def get_dialogue_prompt(
        self, npc_id: str, campaign_id: str, db: Session
    ) -> str:
        """Generate a system prompt snippet for the DM agent to voice this NPC.

        Args:
            npc_id: The NPC profile ID.
            campaign_id: The campaign ID.
            db: SQLAlchemy session.

        Returns:
            A string prompt snippet describing how to portray this NPC.
        """
        ctx = self.get_npc_context(npc_id, campaign_id, db)
        if not ctx:
            return ""

        parts: list[str] = []
        name = ctx.get("name", "Unknown NPC")
        parts.append(f"You are voicing {name}.")

        description = ctx.get("description")
        if description:
            parts.append(f"Description: {description}")

        traits = ctx.get("personality_traits", [])
        if traits:
            parts.append(f"Personality traits: {', '.join(traits)}.")

        tone = ctx.get("disposition_tone", "")
        if tone:
            parts.append(f"Current demeanour: {tone}.")

        recent = ctx.get("recent_conversations", [])
        if recent:
            last_topics: list[str] = []
            for conv in recent[-3:]:
                last_topics.extend(conv.get("topics", []))
            if last_topics:
                unique_topics = list(dict.fromkeys(last_topics))
                parts.append(
                    f"Recent conversation topics: {', '.join(unique_topics)}."
                )

        return " ".join(parts)


npc_dialogue_service = NPCDialogueService()
