"""Combat system routes."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.agents.scribe_agent import get_scribe
from app.database import get_session_context
from app.models.db_models import CombatState
from app.utils.dice import DiceRoller

logger = logging.getLogger(__name__)

router = APIRouter(tags=["combat"])


def _persist_combat(combat_id: str, data: dict[str, Any]) -> None:
    """Save or update a combat encounter in the database."""
    try:
        with get_session_context() as db:
            row = db.query(CombatState).filter(CombatState.id == combat_id).first()
            if row:
                row.status = data.get("status", row.status)
                row.round = data.get("round", row.round)
                row.current_turn = data.get("current_turn", row.current_turn)
                row.initiative_order = data.get("initiative_order", row.initiative_order)
                row.combat_log = data.get("combat_log", row.combat_log)
                row.updated_at = datetime.now(UTC)
            else:
                row = CombatState(
                    id=combat_id,
                    session_id=data.get("session_id", ""),
                    status=data.get("status", "active"),
                    round=data.get("round", 1),
                    current_turn=data.get("current_turn", 0),
                    initiative_order=data.get("initiative_order", []),
                    participants=data.get("participants", []),
                    environment=data.get("environment", "standard"),
                    combat_log=data.get("combat_log", []),
                )
                db.add(row)
            db.commit()
    except Exception as exc:
        logger.warning("Failed to persist combat state %s: %s", combat_id, exc)


def _load_combat(combat_id: str) -> dict[str, Any] | None:
    """Load a combat encounter from the database, or None if not found."""
    try:
        with get_session_context() as db:
            row = db.query(CombatState).filter(CombatState.id == combat_id).first()
            if row is None:
                return None
            return {
                "combat_id": row.id,
                "session_id": row.session_id,
                "status": row.status,
                "round": row.round,
                "current_turn": row.current_turn,
                "initiative_order": row.initiative_order,
                "participants": row.participants,
                "environment": row.environment,
                "combat_log": row.combat_log,
            }
    except Exception as exc:
        logger.warning("Failed to load combat state %s: %s", combat_id, exc)
        return None


@router.post("/combat/initialize", response_model=dict[str, Any])
async def initialize_combat(combat_data: dict[str, Any]) -> dict[str, Any]:
    """Initialize a new combat encounter."""
    try:
        session_id = combat_data.get("session_id")
        participants = combat_data.get("participants", [])
        environment = combat_data.get("environment", "standard")

        # Generate initiative order — d20 + DEX modifier for every
        # combatant, using DiceRoller for consistent randomness.
        initiative_order: list[dict[str, Any]] = []
        for participant in participants:
            dex_modifier = participant.get("dex_modifier", 0)

            if participant.get("type") == "player":
                # Try to pull DEX from the character sheet
                try:
                    character = await get_scribe().get_character(
                        participant["character_id"]
                    )
                    if isinstance(character, dict) and "error" not in character:
                        dex_score = (
                            character.get("abilities", {}).get("dexterity", 10)
                        )
                        dex_modifier = (dex_score - 10) // 2
                except Exception:
                    logger.debug(
                        "Could not fetch character %s for initiative; "
                        "using dex_modifier from request.",
                        participant.get("character_id"),
                    )

                roll = DiceRoller.roll_d20(modifier=dex_modifier)
                initiative_order.append(
                    {
                        "type": "player",
                        "id": participant.get("character_id", participant.get("id")),
                        "name": participant.get("name", "Player"),
                        "initiative": roll["total"],
                    }
                )
            else:
                # NPCs / enemies
                roll = DiceRoller.roll_d20(modifier=dex_modifier)
                initiative_order.append(
                    {
                        "type": "npc",
                        "id": participant.get("id", "npc"),
                        "name": participant.get("name", "NPC"),
                        "initiative": roll["total"],
                    }
                )

        # Sort by initiative (highest first)
        initiative_order.sort(key=lambda x: x["initiative"], reverse=True)

        combat_id = f"combat_{session_id}_{uuid.uuid4().hex[:8]}"
        result = {
            "combat_id": combat_id,
            "session_id": session_id,
            "status": "active",
            "round": 1,
            "current_turn": 0,
            "initiative_order": initiative_order,
            "environment": environment,
            "battle_map_requested": True,
            "started_at": str(datetime.now(UTC)),
        }

        # Persist to database so combat survives restarts (#701)
        _persist_combat(combat_id, {
            "session_id": session_id,
            "status": "active",
            "round": 1,
            "current_turn": 0,
            "initiative_order": initiative_order,
            "participants": participants,
            "environment": environment,
            "combat_log": [],
        })

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize combat: {str(e)}",
        ) from e


@router.post("/combat/{combat_id}/turn", response_model=dict[str, Any])
async def process_combat_turn(combat_id: str, turn_data: dict[str, Any]) -> dict[str, Any]:
    """Process a single combat turn."""
    try:
        action_type = turn_data.get(
            "action", "attack"
        )  # attack, move, spell, item, etc.
        target_id = turn_data.get("target_id")
        character_id = turn_data.get("character_id")
        dice_result = turn_data.get("dice_result")

        # Process the combat action
        turn_result: dict[str, Any] = {
            "combat_id": combat_id,
            "character_id": character_id,
            "action": action_type,
            "target_id": target_id,
            "success": False,
            "damage": 0,
            "description": "",
            "next_turn": True,
        }

        if action_type == "attack":
            # Roll attack if the caller did not supply a pre-rolled result
            attack_bonus = turn_data.get("attack_bonus", 0)
            if dice_result is None:
                dice_result = DiceRoller.roll_d20(modifier=attack_bonus)

            target_ac = turn_data.get("target_ac", 15)
            if dice_result["total"] >= target_ac:
                # Hit -- roll damage
                damage_dice = turn_data.get("damage_dice", "1d6")
                damage_result = DiceRoller.roll_damage(damage_dice)

                turn_result.update(
                    {
                        "success": True,
                        "damage": damage_result["total"],
                        "description": f"Attack hits for {damage_result['total']} damage!",
                        "attack_roll": dice_result,
                        "damage_roll": damage_result,
                    }
                )
            else:
                turn_result.update(
                    {
                        "success": False,
                        "description": (
                            f"Attack misses (rolled {dice_result['total']} "
                            f"vs AC {target_ac})"
                        ),
                        "attack_roll": dice_result,
                    }
                )

        turn_result["timestamp"] = str(datetime.now(UTC))

        # Append to the persistent combat log (#701)
        existing = _load_combat(combat_id)
        if existing is not None:
            log = list(existing.get("combat_log", []))
            log.append(turn_result)
            _persist_combat(combat_id, {"combat_log": log})
        return turn_result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process combat turn: {str(e)}",
        ) from e


@router.post("/encounter/generate", response_model=dict[str, Any])
async def generate_encounter(encounter_request: dict[str, Any]) -> dict[str, Any]:
    """Generate a balanced encounter for the party.

    Request body:
        - ``party_levels``: List of character levels (required).
        - ``difficulty``: Desired difficulty — ``easy``, ``medium``, ``hard``,
          or ``deadly`` (default ``"medium"``).
        - ``location``: Thematic location hint, e.g. ``"dungeon"``, ``"forest"``
          (default ``"dungeon"``).

    Returns a dict describing the generated encounter, including selected
    monsters, adjusted XP, and XP award per character.
    """
    from app.encounter_balancer import generate_balanced_encounter

    try:
        raw_party_levels = encounter_request.get("party_levels", [1])
        raw_difficulty = encounter_request.get("difficulty", "medium")
        raw_location = encounter_request.get("location", "dungeon")

        # Validate types immediately after extraction
        if not isinstance(raw_party_levels, list) or not raw_party_levels:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="party_levels must be a non-empty list of integers",
            )
        if not isinstance(raw_difficulty, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="difficulty must be a string",
            )
        if not isinstance(raw_location, str):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="location must be a string",
            )

        # Coerce party level entries to int, reject non-numeric values
        try:
            party_levels: list[int] = [int(lvl) for lvl in raw_party_levels]
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="party_levels must contain only integers",
            ) from exc

        difficulty: str = raw_difficulty
        location: str = raw_location

        valid_difficulties = {"easy", "medium", "hard", "deadly"}
        if difficulty.lower() not in valid_difficulties:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"difficulty must be one of: {', '.join(sorted(valid_difficulties))}",
            )

        return generate_balanced_encounter(
            party_levels=party_levels,
            difficulty=difficulty,
            location=location,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate encounter: {str(e)}",
        ) from e


@router.post("/encounter/xp-award", response_model=dict[str, Any])
async def encounter_xp_award(award_request: dict[str, Any]) -> dict[str, Any]:
    """Calculate XP awarded to each character after completing an encounter.

    Request body:
        - ``monsters``: List of monster dicts (each with ``"cr"`` or ``"xp"``).
        - ``party_size``: Number of characters receiving XP (required, ≥ 1).

    Returns total XP and per-character XP.
    """
    from app.encounter_balancer import calculate_xp_award

    try:
        monsters: list[dict[str, Any]] = award_request.get("monsters", [])
        party_size: int = award_request.get("party_size", 1)

        if not isinstance(party_size, int) or party_size < 1:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="party_size must be a positive integer",
            )

        return calculate_xp_award(monsters=monsters, party_size=party_size)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate XP award: {str(e)}",
        ) from e


# Internal combat helpers used by session_routes
async def process_combat_action(
    session_id: str, character_id: str, description: str, dice_rolls: list[dict]
) -> dict[str, Any]:
    """Process a combat action."""
    return {
        "type": "combat",
        "description": description,
        "result": "Combat action processed - dice rolls applied",
        "dice_rolls": dice_rolls,
        "effects": ["Damage dealt", "Position changed"],
        "next_actions": ["Continue combat", "End turn"],
    }


async def process_skill_check(
    session_id: str, character_id: str, description: str, dice_rolls: list[dict]
) -> dict[str, Any]:
    """Process a skill check action."""
    success = (
        any(roll.get("total", 0) >= 15 for roll in dice_rolls) if dice_rolls else False
    )
    return {
        "type": "skill_check",
        "description": description,
        "result": "Success!" if success else "Failure!",
        "success": success,
        "dice_rolls": dice_rolls,
        "next_actions": ["Continue exploring", "Try a different approach"],
    }


async def process_exploration_action(
    session_id: str, character_id: str, description: str
) -> dict[str, Any]:
    """Process an exploration action."""
    return {
        "type": "exploration",
        "description": description,
        "result": "You discover something interesting in your exploration.",
        "discoveries": [
            "A hidden passage",
            "An ancient inscription",
            "Signs of recent activity",
        ],
        "next_actions": ["Investigate further", "Move to a new area", "Rest here"],
    }


async def process_general_action(
    session_id: str, character_id: str, description: str
) -> dict[str, Any]:
    """Process a general action, with auto-detection of specialist agents."""
    from app.agents.orchestration import (
        detect_agent_triggers,
        orchestrate_specialist_agents,
    )

    base_result: dict[str, Any] = {
        "type": "general",
        "description": description,
        "result": "Your action has consequences that ripple through the world.",
        "effects": ["The situation changes", "New opportunities arise"],
        "next_actions": ["Continue the adventure", "Try something else"],
    }

    # Auto-detect specialist agent triggers from the player description.
    # We use an empty DM response here because the DM hasn't processed the
    # action in this code path (the session/action endpoint doesn't call the
    # DM agent directly).
    triggers = detect_agent_triggers(dm_response="", player_input=description)
    if triggers:
        logger.info(
            "General action orchestration triggers for session %s: %s",
            session_id,
            triggers,
        )
        specialist_results = await orchestrate_specialist_agents(
            triggers=triggers,
            player_input=description,
            game_state={"character_id": character_id} if character_id else None,
            session_id=session_id,
        )
        if specialist_results:
            base_result["specialist_results"] = specialist_results

    return base_result
