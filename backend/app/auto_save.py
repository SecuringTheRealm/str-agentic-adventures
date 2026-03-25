"""
Auto-save functionality for game state.

Persists conversation history, character stats, and campaign metadata
to the Campaign model's session_log field every N player interactions.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from app.services.campaign_service import campaign_service

logger = logging.getLogger(__name__)

# Per-campaign interaction counter (in-memory; resets on server restart)
_interaction_counters: dict[str, int] = {}

# Maximum number of auto-save snapshots to retain in session_log
_MAX_SNAPSHOTS = 10


def increment_and_get_counter(campaign_id: str) -> int:
    """Increment and return the interaction count for a campaign."""
    _interaction_counters[campaign_id] = _interaction_counters.get(campaign_id, 0) + 1
    return _interaction_counters[campaign_id]


def get_interaction_counter(campaign_id: str) -> int:
    """Return the current interaction count for a campaign (without incrementing)."""
    return _interaction_counters.get(campaign_id, 0)


def reset_interaction_counter(campaign_id: str) -> None:
    """Reset the interaction counter for a campaign (used in tests)."""
    _interaction_counters.pop(campaign_id, None)


def _extract_character_stats(character_data: dict[str, Any] | None) -> dict[str, Any]:
    """Extract relevant character stats for the auto-save snapshot."""
    if not character_data:
        return {}
    spellcasting = character_data.get("spellcasting") or {}
    return {
        "id": character_data.get("id"),
        "name": character_data.get("name"),
        "level": character_data.get("level"),
        "hit_points": character_data.get("hit_points"),
        "spell_slots": spellcasting.get("spell_slots"),
        "conditions": character_data.get("conditions", []),
    }


async def _write_snapshot_to_campaign(
    campaign_id: str,
    snapshot: dict[str, Any],
) -> None:
    """Append a snapshot to the campaign's session_log (background task)."""
    try:
        existing = campaign_service.get_campaign(campaign_id)
        if existing is None:
            logger.warning("Auto-save: campaign %s not found, skipping.", campaign_id)
            return

        current_log: list[dict[str, Any]] = list(existing.session_log or [])
        # Keep only the most recent snapshots to prevent unbounded growth
        auto_save_entries = [e for e in current_log if e.get("type") == "auto_save"]
        other_entries = [e for e in current_log if e.get("type") != "auto_save"]
        trimmed = auto_save_entries[-(  _MAX_SNAPSHOTS - 1):] if len(auto_save_entries) >= _MAX_SNAPSHOTS else auto_save_entries
        updated_log = other_entries + trimmed + [snapshot]

        campaign_service.update_campaign(campaign_id, {"session_log": updated_log})
        logger.info(
            "Auto-saved game state for campaign %s (interaction #%d)",
            campaign_id,
            snapshot.get("interaction_count", "?"),
        )
    except Exception:
        logger.exception("Auto-save DB write failed for campaign %s", campaign_id)


def schedule_auto_save(
    campaign_id: str,
    interaction_count: int,
    conversation_history: list[dict[str, str]],
    character_data: dict[str, Any] | None,
) -> None:
    """
    Build an auto-save snapshot and schedule the DB write as a background task.

    This is intentionally fire-and-forget so it never blocks the game response.
    """
    now = datetime.now(UTC)
    snapshot: dict[str, Any] = {
        "type": "auto_save",
        "timestamp": now.isoformat(),
        "interaction_count": interaction_count,
        "conversation_history": conversation_history[-20:],  # cap at 20 messages
        "character_snapshot": _extract_character_stats(character_data),
        "campaign_metadata": {
            "session_interactions": interaction_count,
        },
    }

    # Schedule as an asyncio background task so we don't block the response
    asyncio.create_task(
        _write_snapshot_to_campaign(campaign_id, snapshot),
        name=f"auto_save_{campaign_id}",
    )


def check_and_schedule_auto_save(
    campaign_id: str,
    auto_save_interval: int,
    conversation_history: list[dict[str, str]],
    character_data: dict[str, Any] | None,
) -> tuple[bool, int]:
    """
    Increment the interaction counter and trigger an auto-save when the
    interval threshold is reached.

    Returns:
        (auto_saved, interaction_count) – auto_saved is True when a save
        was scheduled on this call.
    """
    count = increment_and_get_counter(campaign_id)
    if count % auto_save_interval == 0:
        schedule_auto_save(campaign_id, count, conversation_history, character_data)
        return True, count
    return False, count
