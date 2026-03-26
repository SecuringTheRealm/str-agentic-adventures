"""NPC-related API routes."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    GenerateNPCStatsRequest,
    NPCInteraction,
    NPCInteractionRequest,
    NPCInteractionResponse,
    NPCPersonality,
    NPCStatsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["npc"])


@router.get("/npc/{npc_id}/personality", response_model=NPCPersonality)
async def get_npc_personality(npc_id: str) -> dict[str, Any]:
    """Get NPC personality traits and behaviors."""
    try:
        return NPCPersonality(
            traits=["Honest", "Brave"],
            ideals=["Justice", "Freedom"],
            bonds=["Loyal to the crown", "Protects the innocent"],
            flaws=["Quick to anger", "Overly trusting"],
            mannerisms=["Speaks with authority", "Always stands straight"],
            appearance="Tall and imposing with graying hair",
            motivations=["Maintain law and order", "Protect the city"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get NPC personality: {str(e)}",
        ) from e


@router.post("/npc/{npc_id}/interaction", response_model=NPCInteractionResponse)
async def log_npc_interaction(npc_id: str, request: NPCInteractionRequest) -> dict[str, Any]:
    """Log and retrieve NPC interaction history."""
    try:
        interaction = NPCInteraction(
            npc_id=npc_id,
            character_id=request.character_id,
            interaction_type=request.interaction_type,
            summary=request.summary,
            outcome=request.outcome,
            relationship_change=request.relationship_change,
        )

        import random

        current_level = random.randint(-50, 50)  # noqa: S311
        new_level = max(-100, min(100, current_level + request.relationship_change))

        return NPCInteractionResponse(
            success=True,
            message=f"Interaction logged successfully for NPC {npc_id}",
            interaction_id=interaction.id,
            new_relationship_level=new_level,
        )
    except Exception as e:
        return NPCInteractionResponse(
            success=False,
            message=f"Failed to log NPC interaction: {str(e)}",
            interaction_id="",
        )


@router.post("/npc/{npc_id}/generate-stats", response_model=NPCStatsResponse)
async def generate_npc_stats(npc_id: str, request: GenerateNPCStatsRequest) -> dict[str, Any]:
    """Generate combat stats for NPCs dynamically."""
    try:
        import random

        level = request.level or 1
        role = request.role

        stat_templates = {
            "civilian": {
                "hit_dice": "1d4",
                "armor_class_base": 10,
                "proficiency_bonus": 2,
                "abilities_mod": 0,
            },
            "guard": {
                "hit_dice": "1d8",
                "armor_class_base": 16,
                "proficiency_bonus": 2,
                "abilities_mod": 2,
            },
            "soldier": {
                "hit_dice": "1d10",
                "armor_class_base": 18,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 3,
            },
            "spellcaster": {
                "hit_dice": "1d6",
                "armor_class_base": 12,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 4,
            },
            "rogue": {
                "hit_dice": "1d8",
                "armor_class_base": 14,
                "proficiency_bonus": 2 + (level - 1) // 4,
                "abilities_mod": 3,
            },
        }

        template = stat_templates.get(role, stat_templates["civilian"])

        hit_dice_num = int(template["hit_dice"].split("d")[1])
        hit_points = sum(random.randint(1, hit_dice_num) for _ in range(level))  # noqa: S311
        hit_points += level * 1

        base_stat = 10 + template["abilities_mod"]
        abilities = {
            "strength": base_stat + random.randint(-2, 2),  # noqa: S311
            "dexterity": base_stat + random.randint(-2, 2),  # noqa: S311
            "constitution": base_stat + random.randint(-2, 2),  # noqa: S311
            "intelligence": base_stat + random.randint(-2, 2),  # noqa: S311
            "wisdom": base_stat + random.randint(-2, 2),  # noqa: S311
            "charisma": base_stat + random.randint(-2, 2),  # noqa: S311
        }

        if role == "soldier":
            abilities["strength"] += 2
            abilities["constitution"] += 2
        elif role == "spellcaster":
            abilities["intelligence"] += 3
            abilities["wisdom"] += 2
        elif role == "rogue":
            abilities["dexterity"] += 3
            abilities["charisma"] += 1
        elif role == "guard":
            abilities["strength"] += 1
            abilities["constitution"] += 1

        generated_stats = {
            "level": level,
            "hit_points": {"current": hit_points, "maximum": hit_points},
            "armor_class": template["armor_class_base"]
            + ((abilities["dexterity"] - 10) // 2),
            "proficiency_bonus": template["proficiency_bonus"],
            "abilities": abilities,
            "role": role,
            "challenge_rating": level / 2 if level > 1 else 0.25,
        }

        return NPCStatsResponse(
            success=True,
            message=f"Generated {role} stats for level {level} NPC",
            generated_stats=generated_stats,
        )
    except Exception as e:
        return NPCStatsResponse(
            success=False,
            message=f"Failed to generate NPC stats: {str(e)}",
            generated_stats={},
        )
