"""Combat-related API routes."""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.models.game_models import (
    CastSpellRequest,
    SpellCastingResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["combat"])


@router.post("/combat/initialize", response_model=dict[str, Any])
async def initialize_combat(combat_data: dict[str, Any]):
    """Initialize a new combat encounter."""
    try:
        session_id = combat_data.get("session_id")
        participants = combat_data.get("participants", [])
        environment = combat_data.get("environment", "standard")

        initiative_order = []
        for participant in participants:
            if participant.get("type") == "player":
                from app.plugins.rules_engine_plugin import RulesEnginePlugin

                rules_engine = RulesEnginePlugin()
                character = await get_scribe().get_character(
                    participant["character_id"]
                )
                if "error" not in character:
                    dex_modifier = (character["abilities"]["dexterity"] - 10) // 2
                    initiative_roll = rules_engine.roll_dice("1d20")
                    initiative_total = initiative_roll["total"] + dex_modifier
                else:
                    initiative_total = 10

                initiative_order.append(
                    {
                        "type": "player",
                        "id": participant["character_id"],
                        "name": participant.get("name", "Player"),
                        "initiative": initiative_total,
                    }
                )
            else:
                from random import randint

                initiative_order.append(
                    {
                        "type": "npc",
                        "id": participant["id"],
                        "name": participant.get("name", "NPC"),
                        "initiative": randint(1, 20)  # noqa: S311
                        + participant.get("dex_modifier", 0),
                    }
                )

        initiative_order.sort(key=lambda x: x["initiative"], reverse=True)

        return {
            "combat_id": f"combat_{session_id}_{hash(str(participants))}",
            "session_id": session_id,
            "status": "active",
            "round": 1,
            "current_turn": 0,
            "initiative_order": initiative_order,
            "environment": environment,
            "battle_map_requested": True,
            "started_at": str(datetime.now()),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize combat: {str(e)}",
        ) from e


@router.post("/combat/{combat_id}/turn", response_model=dict[str, Any])
async def process_combat_turn(combat_id: str, turn_data: dict[str, Any]):
    """Process a single combat turn."""
    try:
        action_type = turn_data.get("action", "attack")
        target_id = turn_data.get("target_id")
        character_id = turn_data.get("character_id")
        dice_result = turn_data.get("dice_result")

        turn_result = {
            "combat_id": combat_id,
            "character_id": character_id,
            "action": action_type,
            "target_id": target_id,
            "success": False,
            "damage": 0,
            "description": "",
            "next_turn": True,
        }

        if action_type == "attack" and dice_result:
            target_ac = turn_data.get("target_ac", 15)
            if dice_result["total"] >= target_ac:
                damage_dice = turn_data.get("damage_dice", "1d6")
                from app.plugins.rules_engine_plugin import RulesEnginePlugin

                rules_engine = RulesEnginePlugin()
                damage_result = rules_engine.roll_dice(damage_dice)

                turn_result.update(
                    {
                        "success": True,
                        "damage": damage_result["total"],
                        "description": f"Attack hits for {damage_result['total']} damage!",
                        "damage_roll": damage_result,
                    }
                )
            else:
                turn_result.update(
                    {
                        "success": False,
                        "description": f"Attack misses (rolled {dice_result['total']} vs AC {target_ac})",
                    }
                )

        turn_result["timestamp"] = str(datetime.now())
        return turn_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process combat turn: {str(e)}",
        ) from e


@router.post("/combat/{combat_id}/cast-spell", response_model=SpellCastingResponse)
async def cast_spell_in_combat(combat_id: str, request: CastSpellRequest):
    """Cast spells during combat with sophisticated effect resolution."""
    try:
        spell_data = await _get_spell_data(request.spell_id)

        spell_effects = await _calculate_spell_effects(
            spell_data, request.slot_level, request.target_ids, combat_id
        )

        concentration_needed = spell_data.get("concentration", False) or spell_data.get(
            "requires_concentration", False
        )

        if concentration_needed:
            from app.plugins.rules_engine_plugin import RulesEnginePlugin

            rules_engine = RulesEnginePlugin()
            rules_engine.start_concentration(
                request.character_id,
                spell_data,
                duration_rounds=10,
            )

        return SpellCastingResponse(
            success=True,
            message=f"Spell '{spell_data.get('name', request.spell_id)}' cast successfully in combat {combat_id}",
            spell_effects=spell_effects,
            concentration_broken=False,
            slot_used=True,
        )
    except Exception as e:
        return SpellCastingResponse(
            success=False, message=f"Failed to cast spell: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Spell helpers (used by cast-spell endpoint)
# ---------------------------------------------------------------------------


async def _get_spell_data(spell_id: str) -> dict[str, Any]:
    """Get spell data from database or return default spell structure."""
    from app.database import get_session
    from app.models.db_models import Spell

    try:
        with next(get_session()) as db:
            spell = db.query(Spell).filter(Spell.id == spell_id).first()
            if spell:
                return {
                    "id": spell.id,
                    "name": spell.name,
                    "level": spell.level,
                    "school": spell.school,
                    "damage_dice": spell.damage_dice,
                    "save_type": spell.save_type,
                    "concentration": spell.concentration,
                    "ritual": spell.ritual,
                    "components": spell.components,
                    "description": spell.description,
                    "higher_levels": spell.higher_levels,
                    **spell.data,
                }
    except Exception:
        pass

    return _get_default_spell_data(spell_id)


def _get_default_spell_data(spell_id: str) -> dict[str, Any]:
    """Get default spell data for common spells."""
    default_spells = {
        "magic_missile": {
            "name": "Magic Missile",
            "level": 1,
            "school": "evocation",
            "damage_dice": "1d4+1",
            "save_type": None,
            "concentration": False,
            "auto_hit": True,
            "base_missiles": 3,
        },
        "fireball": {
            "name": "Fireball",
            "level": 3,
            "school": "evocation",
            "damage_dice": "8d6",
            "save_type": "dexterity",
            "concentration": False,
            "area_effect": True,
            "radius": 20,
        },
        "healing_word": {
            "name": "Healing Word",
            "level": 1,
            "school": "evocation",
            "healing_dice": "1d4",
            "save_type": None,
            "concentration": False,
            "range": 60,
            "bonus_action": True,
        },
        "shield": {
            "name": "Shield",
            "level": 1,
            "school": "abjuration",
            "ac_bonus": 5,
            "save_type": None,
            "concentration": False,
            "duration": "1 round",
            "reaction": True,
        },
        "cure_wounds": {
            "name": "Cure Wounds",
            "level": 1,
            "school": "evocation",
            "healing_dice": "1d8",
            "save_type": None,
            "concentration": False,
            "touch": True,
        },
    }

    return default_spells.get(
        spell_id,
        {
            "name": spell_id.replace("_", " ").title(),
            "level": 1,
            "school": "unknown",
            "concentration": False,
        },
    )


async def _calculate_spell_effects(
    spell_data: dict[str, Any],
    cast_level: int,
    target_ids: list[str] | None,
    combat_id: str,
) -> dict[str, Any]:
    """Calculate sophisticated spell effects based on spell data and level."""
    effects: dict[str, Any] = {
        "spell_name": spell_data.get("name", "Unknown Spell"),
        "spell_level": cast_level,
        "base_level": spell_data.get("level", 1),
        "school": spell_data.get("school", "unknown"),
        "target_count": len(target_ids) if target_ids else 1,
        "combat_id": combat_id,
        "effects": [],
        "damage": None,
        "healing": None,
        "save_required": spell_data.get("save_type") is not None,
        "save_type": spell_data.get("save_type"),
        "concentration": spell_data.get("concentration", False),
    }

    upcast_levels = cast_level - spell_data.get("level", 1)

    if spell_data.get("damage_dice"):
        base_damage = spell_data["damage_dice"]
        if upcast_levels > 0 and spell_data.get("higher_levels"):
            additional_dice = upcast_levels * _get_upcast_scaling(spell_data["name"])
            effects["damage"] = f"{base_damage} + {additional_dice}d6"
        else:
            effects["damage"] = base_damage
        effects["effects"].append(f"Deals {effects['damage']} damage")

    if spell_data.get("healing_dice"):
        base_healing = spell_data["healing_dice"]
        if upcast_levels > 0:
            additional_healing = upcast_levels
            effects["healing"] = f"{base_healing} + {additional_healing}"
        else:
            effects["healing"] = base_healing
        effects["effects"].append(f"Heals {effects['healing']} hit points")

    if spell_data.get("auto_hit"):
        effects["effects"].append("Automatically hits target(s)")

    if spell_data.get("area_effect"):
        radius = spell_data.get("radius", 10)
        effects["effects"].append(f"Area effect: {radius} foot radius")

    if spell_data.get("ac_bonus"):
        effects["effects"].append(f"Grants +{spell_data['ac_bonus']} AC")

    if spell_data.get("name") == "Magic Missile":
        base_missiles = spell_data.get("base_missiles", 3)
        total_missiles = base_missiles + upcast_levels
        effects["effects"].append(f"Fires {total_missiles} missiles")
        effects["damage"] = (
            f"{total_missiles} missiles, each dealing 1d4+1 force damage"
        )

    if upcast_levels > 0:
        effects["effects"].append(
            f"Cast at {cast_level} level (+{upcast_levels} levels)"
        )

    return effects


def _get_upcast_scaling(spell_name: str) -> int:
    """Get damage dice scaling for upcasting spells."""
    scaling_table = {
        "Fireball": 1,
        "Lightning Bolt": 1,
        "Scorching Ray": 1,
        "Cure Wounds": 1,
        "Healing Word": 1,
    }
    return scaling_table.get(spell_name, 1)
