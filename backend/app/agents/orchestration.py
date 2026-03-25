"""
Agent orchestration - context-based routing from the DM to specialist agents.

After the DM agent processes a player action, this module analyses the DM
response and the player input to decide which specialist agents (Narrator,
Scribe, Combat MC) should be invoked automatically.  The auto-detection only
fires for "general" actions; explicit action types set by the frontend still
take priority.
"""

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword groups for each specialist agent
# ---------------------------------------------------------------------------

COMBAT_KEYWORDS: list[str] = [
    "attack",
    "fight",
    "combat",
    "initiative",
    "hit",
    "damage",
    "sword",
    "cast spell at",
    "shoot",
]

EXPLORATION_KEYWORDS: list[str] = [
    "look around",
    "examine",
    "search",
    "explore",
    "enter",
    "walk",
    "travel",
    "describe",
]

CHARACTER_KEYWORDS: list[str] = [
    "inventory",
    "character sheet",
    "level up",
    "equipment",
    "stats",
    "spell slots",
    "hit points",
    "hp",
]

NPC_KEYWORDS: list[str] = [
    "talk to",
    "speak with",
    "ask",
    "persuade",
    "intimidate",
    "negotiate",
    "conversation",
]


def detect_agent_triggers(dm_response: str, player_input: str) -> list[str]:
    """Detect which specialist agents should be triggered based on context.

    Args:
        dm_response: The narrative text returned by the DM agent.
        player_input: The original player input string.

    Returns:
        A deduplicated list of specialist agent identifiers, e.g.
        ``["combat_mc", "narrator"]``.
    """
    triggers: list[str] = []
    combined = f"{player_input} {dm_response}".lower()

    # Combat triggers
    if any(kw in combined for kw in COMBAT_KEYWORDS):
        triggers.append("combat_mc")

    # Exploration / narrative triggers
    has_explore = any(kw in combined for kw in EXPLORATION_KEYWORDS)
    if has_explore and "narrator" not in triggers:
        triggers.append("narrator")

    # Character / inventory triggers
    if any(kw in combined for kw in CHARACTER_KEYWORDS):
        triggers.append("scribe")

    # NPC interaction triggers (narrator handles NPC voicing)
    if any(kw in combined for kw in NPC_KEYWORDS) and "narrator" not in triggers:
        triggers.append("narrator")

    # Parse explicit [AGENT:name] delegation tags from the DM response
    agent_tags = re.findall(r"\[AGENT:(\w+)\]", dm_response)
    for tag in agent_tags:
        tag_lower = tag.lower()
        if tag_lower not in triggers:
            triggers.append(tag_lower)

    return triggers


async def orchestrate_specialist_agents(
    triggers: list[str],
    player_input: str,
    game_state: dict[str, Any] | None,
    session_id: str,
) -> dict[str, Any]:
    """Invoke specialist agents based on the detected triggers.

    Each specialist agent call is wrapped in its own try/except so that a
    failure in one agent does not prevent the others from running.

    Args:
        triggers: List of agent identifiers from ``detect_agent_triggers``.
        player_input: The original player action text.
        game_state: Current game state dict (may be ``None``).
        session_id: The active game session identifier.

    Returns:
        A dict whose keys describe the specialist outputs, e.g.
        ``{"combat_update": {...}, "scene_narrative": "..."}``.
    """
    if not triggers:
        return {}

    results: dict[str, Any] = {}
    state = game_state or {}

    if "combat_mc" in triggers:
        try:
            from app.agents.combat_mc_agent import get_combat_mc

            combat_mc = get_combat_mc()
            # Use a lightweight action dict; full encounter management is
            # handled separately by the combat workflow endpoints.
            action_data: dict[str, Any] = {
                "type": "attack",
                "description": player_input,
                "actor_id": state.get("character_id", "player"),
                "target_id": state.get("target_id", "enemy_1"),
            }
            combat_result = await combat_mc.process_combat_action(
                encounter_id=state.get("encounter_id", "auto"),
                action_data=action_data,
            )
            results["combat_update"] = combat_result
        except Exception as exc:
            logger.error("Combat MC orchestration failed: %s", exc)

    if "narrator" in triggers:
        try:
            from app.agents.narrator_agent import get_narrator

            narrator = get_narrator()
            scene_context: dict[str, Any] = {
                "location": state.get("location", "an unknown place"),
                "mood": state.get("mood", "neutral"),
                "recent_events": player_input,
            }
            scene = await narrator.describe_scene(scene_context=scene_context)
            results["scene_narrative"] = scene
        except Exception as exc:
            logger.error("Narrator orchestration failed: %s", exc)

    if "scribe" in triggers:
        try:
            from app.agents.scribe_agent import get_scribe

            scribe = get_scribe()
            character_id = state.get("character_id", "")
            if character_id:
                char_info = await scribe.get_character(character_id)
            else:
                char_info = {"note": "No character_id in game state"}
            results["character_update"] = char_info
        except Exception as exc:
            logger.error("Scribe orchestration failed: %s", exc)

    return results
