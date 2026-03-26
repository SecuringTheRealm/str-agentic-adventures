"""Service for building game context during /input processing.

Loads campaign state, character stats, equipment, and conditions to
pass to the DM agent and orchestration layer. This is the integration
glue that connects the campaign, character, inventory, and rules
engine systems during live gameplay.
"""

import logging
from typing import Any

from app.database import get_session_context
from app.models.db_models import Character as CharacterDB
from app.rules_engine import (
    calculate_ac,
    get_proficiency_bonus,
    get_weapon_stats,
)
from app.services.campaign_service import campaign_service

logger = logging.getLogger(__name__)


def _ability_modifier(score: int) -> int:
    """Calculate the ability modifier for a given ability score."""
    return (score - 10) // 2


def load_character_state(character_id: str) -> dict[str, Any]:
    """Load full character state from the database.

    Returns a dict with stats, equipment, spell slots, conditions,
    and combat-relevant derived values.
    """
    try:
        with get_session_context() as db:
            char_row = (
                db.query(CharacterDB)
                .filter(CharacterDB.id == character_id)
                .first()
            )
            if not char_row or not char_row.data:
                return {}

            data: dict[str, Any] = dict(char_row.data)
            data.setdefault("id", char_row.id)
            data.setdefault("name", char_row.name)

            # Derive combat-relevant values
            abilities = data.get("abilities", {})
            level = data.get("level", 1)
            proficiency_bonus = get_proficiency_bonus(level)
            data["proficiency_bonus"] = proficiency_bonus

            # Determine equipped weapon stats
            equipped_weapon = _get_equipped_weapon(data)
            if equipped_weapon:
                data["equipped_weapon"] = equipped_weapon

            # Calculate AC from equipment
            equipped_armor = _get_equipped_armor_name(data)
            shield_equipped = _has_shield(data)
            dex_mod = _ability_modifier(abilities.get("dexterity", 10))
            data["computed_ac"] = calculate_ac(equipped_armor, shield_equipped, dex_mod)

            return data
    except Exception as e:
        logger.warning("Failed to load character state for %s: %s", character_id, e)
        return {}


def _get_equipped_weapon(char_data: dict[str, Any]) -> dict[str, Any] | None:
    """Determine the character's equipped weapon and return its stats.

    Checks structured_inventory.equipment.main_hand first, then falls
    back to the first equipped weapon-type item in structured_inventory.items.
    """
    inv = char_data.get("structured_inventory", {})
    if isinstance(inv, dict):
        equipment = inv.get("equipment", {})
        items = inv.get("items", [])

        # Check main_hand slot
        main_hand_id = equipment.get("main_hand") if isinstance(equipment, dict) else None

        if main_hand_id and isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("id") == main_hand_id:
                    weapon_name = item.get("name", "")
                    weapon_stats = get_weapon_stats(weapon_name)
                    return {
                        "name": weapon_name,
                        **weapon_stats,
                    }

        # Fallback: first equipped weapon-type item
        if isinstance(items, list):
            for item in items:
                if (
                    isinstance(item, dict)
                    and item.get("equipped")
                    and item.get("item_type") == "weapon"
                ):
                    weapon_name = item.get("name", "")
                    weapon_stats = get_weapon_stats(weapon_name)
                    return {
                        "name": weapon_name,
                        **weapon_stats,
                    }

    return None


def _get_equipped_armor_name(char_data: dict[str, Any]) -> str | None:
    """Return the name of the equipped armor, or None."""
    inv = char_data.get("structured_inventory", {})
    if isinstance(inv, dict):
        equipment = inv.get("equipment", {})
        items = inv.get("items", [])

        armor_id = equipment.get("armor") if isinstance(equipment, dict) else None
        if armor_id and isinstance(items, list):
            for item in items:
                if isinstance(item, dict) and item.get("id") == armor_id:
                    return item.get("name")

        # Fallback: first equipped armor-type item
        if isinstance(items, list):
            for item in items:
                if (
                    isinstance(item, dict)
                    and item.get("equipped")
                    and item.get("item_type") == "armor"
                ):
                    return item.get("name")

    return None


def _has_shield(char_data: dict[str, Any]) -> bool:
    """Check if character has a shield equipped."""
    inv = char_data.get("structured_inventory", {})
    if isinstance(inv, dict):
        equipment = inv.get("equipment", {})
        items = inv.get("items", [])

        off_hand_id = equipment.get("off_hand") if isinstance(equipment, dict) else None
        if off_hand_id and isinstance(items, list):
            for item in items:
                if (
                    isinstance(item, dict)
                    and item.get("id") == off_hand_id
                    and item.get("item_type") == "shield"
                ):
                    return True

        # Fallback: any equipped shield-type item
        if isinstance(items, list):
            for item in items:
                if (
                    isinstance(item, dict)
                    and item.get("equipped")
                    and item.get("item_type") == "shield"
                ):
                    return True

    return False


def load_campaign_state(campaign_id: str) -> dict[str, Any]:
    """Load campaign state for context enrichment.

    Returns a dict with campaign metadata, current location, and any
    active combat state.
    """
    try:
        campaign = campaign_service.get_campaign(campaign_id)
        if campaign is None:
            return {}

        return {
            "id": campaign.id,
            "name": campaign.name,
            "setting": campaign.setting,
            "tone": campaign.tone,
            "current_location": campaign.current_location or "",
            "world_description": campaign.world_description or "",
        }
    except Exception as e:
        logger.warning("Failed to load campaign state for %s: %s", campaign_id, e)
        return {}


def build_game_context(
    character_id: str,
    campaign_id: str,
    character_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the full game context for the DM agent and orchestration layer.

    This combines character state, campaign state, and derived combat
    values into a single context dict that flows through the /input pipeline.

    Args:
        character_id: The player's character ID.
        campaign_id: The active campaign ID.
        character_data: Optional pre-loaded character data (avoids double-load).

    Returns:
        Dict containing all context needed by the DM agent and specialists.
    """
    # Load character state
    if character_data and isinstance(character_data, dict) and character_data.get("level"):
        char_state = dict(character_data)
    else:
        char_state = load_character_state(character_id)

    # Derive equipment-based values if not already present.
    # load_character_state() populates these, but when caller supplies
    # character_data directly we need to compute them here.
    if "equipped_weapon" not in char_state:
        equipped = _get_equipped_weapon(char_state)
        if equipped:
            char_state["equipped_weapon"] = equipped
    if "computed_ac" not in char_state:
        abilities_for_ac = char_state.get("abilities", {})
        dex_for_ac = (
            _ability_modifier(abilities_for_ac.get("dexterity", 10))
            if isinstance(abilities_for_ac, dict)
            else 0
        )
        char_state["computed_ac"] = calculate_ac(
            _get_equipped_armor_name(char_state),
            _has_shield(char_state),
            dex_for_ac,
        )

    # Load campaign state
    campaign_state = load_campaign_state(campaign_id) if campaign_id else {}

    # Extract ability scores for convenience
    abilities = char_state.get("abilities", {})
    if isinstance(abilities, dict):
        str_mod = _ability_modifier(abilities.get("strength", 10))
        dex_mod = _ability_modifier(abilities.get("dexterity", 10))
    else:
        str_mod = 0
        dex_mod = 0

    # Build the equipped weapon attack context
    equipped_weapon = char_state.get("equipped_weapon", {})
    weapon_properties = equipped_weapon.get("properties", [])
    level = char_state.get("level", 1)
    proficiency_bonus = get_proficiency_bonus(level)

    # Determine attack modifier: finesse/ranged use DEX, others use STR
    is_finesse = "finesse" in weapon_properties
    is_ranged = "ammunition" in weapon_properties
    if is_ranged or is_finesse:
        ability_mod = max(str_mod, dex_mod) if is_finesse else dex_mod
    else:
        ability_mod = str_mod

    attack_bonus = ability_mod + proficiency_bonus
    damage_modifier = ability_mod

    # Extract HP
    hp = char_state.get("hit_points", {})
    if isinstance(hp, dict):
        current_hp = hp.get("current", 0)
        max_hp = hp.get("maximum", 0)
    else:
        current_hp = 0
        max_hp = 0

    # Extract conditions
    conditions = char_state.get("conditions", [])

    # Extract spell slots
    spellcasting = char_state.get("spellcasting", {})
    spell_slots = None
    if isinstance(spellcasting, dict):
        spell_slots = spellcasting.get("spell_slots")

    context = {
        # Identity
        "character_id": character_id,
        "campaign_id": campaign_id,
        "character_name": char_state.get("name", "Adventurer"),
        "character_class": char_state.get("character_class", "Fighter"),
        "character_level": str(level),
        # Combat stats
        "current_hp": current_hp,
        "max_hp": max_hp,
        "armor_class": char_state.get("computed_ac", char_state.get("armor_class", 10)),
        "proficiency_bonus": proficiency_bonus,
        "conditions": conditions,
        # Weapon info (for combat orchestration)
        "equipped_weapon_name": equipped_weapon.get("name", ""),
        "equipped_weapon_damage": equipped_weapon.get("damage_dice", "1d4"),
        "equipped_weapon_properties": weapon_properties,
        "attack_bonus": attack_bonus,
        "damage_modifier": damage_modifier,
        # Spell info
        "spell_slots": spell_slots,
        # Campaign context
        "location": campaign_state.get("current_location", ""),
        "setting": campaign_state.get("setting", ""),
        "tone": campaign_state.get("tone", "heroic"),
    }

    return context


def build_state_updates(
    context: dict[str, Any],
    dm_response: dict[str, Any],
) -> dict[str, Any]:
    """Build the state_updates section for the GameResponse.

    Enriches the DM response with current game state so the frontend
    can display HP, conditions, inventory changes, etc.

    Args:
        context: The game context built by build_game_context.
        dm_response: The raw response from the DM agent.

    Returns:
        Dict of state updates to include in GameResponse.
    """
    state = dict(dm_response.get("state_updates", {}))

    # Always include current character state
    state["character_state"] = {
        "current_hp": context.get("current_hp", 0),
        "max_hp": context.get("max_hp", 0),
        "armor_class": context.get("armor_class", 10),
        "conditions": context.get("conditions", []),
        "level": int(context.get("character_level", 1)),
    }

    # Include equipped weapon info if available
    weapon_name = context.get("equipped_weapon_name")
    if weapon_name:
        state["equipped_weapon"] = {
            "name": weapon_name,
            "damage_dice": context.get("equipped_weapon_damage", "1d4"),
            "attack_bonus": context.get("attack_bonus", 0),
        }

    # Include spell slots if available
    spell_slots = context.get("spell_slots")
    if spell_slots:
        state["spell_slots"] = spell_slots

    return state
