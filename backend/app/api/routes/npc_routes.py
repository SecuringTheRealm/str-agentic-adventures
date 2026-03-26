"""NPC system routes."""

import logging
import random
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.database import DbDep
from app.models.db_models import NPCProfileDB, NPCRelationshipDB
from app.models.game_models import (
    NPC,
    CreateNPCProfileRequest,
    CreateNPCRequest,
    GenerateNPCStatsRequest,
    NPCInteraction,
    NPCInteractionRequest,
    NPCInteractionResponse,
    NPCPersonality,
    NPCProfile,
    NPCProfileListResponse,
    NPCProfileWithRelationship,
    NPCRelationship,
    NPCStatsResponse,
    UpdateDispositionRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["npcs"])


@router.post("/campaign/{campaign_id}/npcs", response_model=NPC)
async def create_campaign_npc(campaign_id: str, request: CreateNPCRequest):
    """Create and manage campaign NPCs."""
    try:
        # Generate basic personality traits if not provided
        sample_traits = [
            "Honest",
            "Deceitful",
            "Brave",
            "Cowardly",
            "Generous",
            "Greedy",
            "Kind",
            "Cruel",
            "Optimistic",
            "Pessimistic",
            "Curious",
            "Secretive",
        ]

        sample_mannerisms = [
            "Speaks softly",
            "Gestures wildly",
            "Never makes eye contact",
            "Constantly fidgets",
            "Uses elaborate vocabulary",
            "Speaks in short sentences",
        ]

        # Create NPC with generated personality
        personality = NPCPersonality(
            traits=random.sample(sample_traits, 2),
            mannerisms=random.sample(sample_mannerisms, 1),
            motivations=["Survive and prosper", "Help their family"],
        )

        # Generate basic abilities for the NPC
        from app.models.game_models import Abilities, HitPoints

        abilities = Abilities(
            strength=random.randint(8, 16),  # noqa: S311
            dexterity=random.randint(8, 16),  # noqa: S311
            constitution=random.randint(8, 16),  # noqa: S311
            intelligence=random.randint(8, 16),  # noqa: S311
            wisdom=random.randint(8, 16),  # noqa: S311
            charisma=random.randint(8, 16),  # noqa: S311
        )

        hit_points = HitPoints(
            current=random.randint(4, 12),  # noqa: S311
            maximum=random.randint(4, 12),  # noqa: S311
        )

        return NPC(
            name=request.name,
            race=request.race,
            gender=request.gender,
            age=request.age,
            occupation=request.occupation,
            location=request.location,
            campaign_id=campaign_id,
            personality=personality,
            abilities=abilities,
            hit_points=hit_points,
            armor_class=10 + ((abilities.dexterity - 10) // 2),
            importance=request.importance,
            story_role=request.story_role,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create NPC: {str(e)}",
        ) from e


@router.get("/npc/{npc_id}/personality", response_model=NPCPersonality)
async def get_npc_personality(npc_id: str):
    """Get NPC personality traits and behaviors."""
    try:
        # This would normally retrieve from a database
        # For now, return a sample personality
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
async def log_npc_interaction(npc_id: str, request: NPCInteractionRequest):
    """Log and retrieve NPC interaction history."""
    try:
        # Create interaction record
        interaction = NPCInteraction(
            npc_id=npc_id,
            character_id=request.character_id,
            interaction_type=request.interaction_type,
            summary=request.summary,
            outcome=request.outcome,
            relationship_change=request.relationship_change,
        )

        # This would normally be stored in a database
        # For now, return success response

        # Calculate new relationship level (simulated)
        current_level = random.randint(  # noqa: S311
            -50, 50
        )  # Would be retrieved from database
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
async def generate_npc_stats(npc_id: str, request: GenerateNPCStatsRequest):
    """Generate combat stats for NPCs dynamically."""
    try:
        level = request.level or 1
        role = request.role

        # Generate stats based on role and level
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

        # Generate hit points
        hit_dice_num = int(template["hit_dice"].split("d")[1])
        hit_points = sum(random.randint(1, hit_dice_num) for _ in range(level))  # noqa: S311
        hit_points += level * 1  # Constitution modifier (assumed +1)

        # Generate abilities
        base_stat = 10 + template["abilities_mod"]
        abilities = {
            "strength": base_stat + random.randint(-2, 2),  # noqa: S311
            "dexterity": base_stat + random.randint(-2, 2),  # noqa: S311
            "constitution": base_stat + random.randint(-2, 2),  # noqa: S311
            "intelligence": base_stat + random.randint(-2, 2),  # noqa: S311
            "wisdom": base_stat + random.randint(-2, 2),  # noqa: S311
            "charisma": base_stat + random.randint(-2, 2),  # noqa: S311
        }

        # Role-specific stat adjustments
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


# ---------------------------------------------------------------------------
# NPC Profile API endpoints (game-engine disposition tracking)
# ---------------------------------------------------------------------------

# Disposition score bounds for NPC relationship tracking
_MIN_DISPOSITION_SCORE = -100
_MAX_DISPOSITION_SCORE = 100


@router.get("/npcs/{campaign_id}", response_model=NPCProfileListResponse)
async def list_npc_profiles(
    campaign_id: str,
    db: DbDep,
) -> NPCProfileListResponse:
    """List all NPC profiles for a campaign."""
    rows = (
        db.query(NPCProfileDB)
        .filter(NPCProfileDB.campaign_id == campaign_id)
        .all()
    )
    profiles = [
        NPCProfile(
            id=row.id,
            name=row.name,
            description=row.description or "",
            personality_traits=row.personality_traits or [],
            disposition=row.disposition,
            location=row.location or "",
            is_alive=row.is_alive,
            conversation_notes=row.conversation_notes or [],
        )
        for row in rows
    ]
    return NPCProfileListResponse(npcs=profiles, total_count=len(profiles))


@router.post("/npcs/{campaign_id}", response_model=NPCProfile, status_code=status.HTTP_201_CREATED)
async def create_npc_profile(
    campaign_id: str,
    request: CreateNPCProfileRequest,
    db: DbDep,
) -> NPCProfile:
    """Create a new NPC profile in a campaign."""
    npc_id = str(uuid.uuid4())
    row = NPCProfileDB(
        id=npc_id,
        campaign_id=campaign_id,
        name=request.name,
        description=request.description,
        personality_traits=request.personality_traits,
        disposition=request.disposition,
        location=request.location,
        is_alive=True,
        conversation_notes=[],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NPCProfile(
        id=row.id,
        name=row.name,
        description=row.description or "",
        personality_traits=row.personality_traits or [],
        disposition=row.disposition,
        location=row.location or "",
        is_alive=row.is_alive,
        conversation_notes=row.conversation_notes or [],
    )


@router.get("/npcs/{campaign_id}/{npc_id}", response_model=NPCProfileWithRelationship)
async def get_npc_profile(
    campaign_id: str,
    npc_id: str,
    db: DbDep,
) -> NPCProfileWithRelationship:
    """Get an NPC profile with its relationship data."""
    row = (
        db.query(NPCProfileDB)
        .filter(NPCProfileDB.id == npc_id, NPCProfileDB.campaign_id == campaign_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {npc_id} not found in campaign {campaign_id}",
        )
    profile = NPCProfile(
        id=row.id,
        name=row.name,
        description=row.description or "",
        personality_traits=row.personality_traits or [],
        disposition=row.disposition,
        location=row.location or "",
        is_alive=row.is_alive,
        conversation_notes=row.conversation_notes or [],
    )
    rel_row = (
        db.query(NPCRelationshipDB)
        .filter(
            NPCRelationshipDB.npc_id == npc_id,
            NPCRelationshipDB.campaign_id == campaign_id,
        )
        .first()
    )
    relationship = None
    if rel_row is not None:
        relationship = NPCRelationship(
            npc_id=rel_row.npc_id,
            campaign_id=rel_row.campaign_id,
            disposition_score=rel_row.disposition_score,
            interactions_count=rel_row.interactions_count,
            key_events=rel_row.key_events or [],
            last_interaction=rel_row.last_interaction or "",
        )
    return NPCProfileWithRelationship(profile=profile, relationship=relationship)


@router.patch("/npcs/{campaign_id}/{npc_id}/disposition", response_model=NPCRelationship)
async def update_npc_disposition(
    campaign_id: str,
    npc_id: str,
    request: UpdateDispositionRequest,
    db: DbDep,
) -> NPCRelationship:
    """Update the disposition score for an NPC in a campaign."""
    npc_row = (
        db.query(NPCProfileDB)
        .filter(NPCProfileDB.id == npc_id, NPCProfileDB.campaign_id == campaign_id)
        .first()
    )
    if npc_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"NPC {npc_id} not found in campaign {campaign_id}",
        )

    clamped_score = max(_MIN_DISPOSITION_SCORE, min(_MAX_DISPOSITION_SCORE, request.disposition_score))

    rel_row = (
        db.query(NPCRelationshipDB)
        .filter(
            NPCRelationshipDB.npc_id == npc_id,
            NPCRelationshipDB.campaign_id == campaign_id,
        )
        .first()
    )
    now_str = datetime.now(UTC).isoformat()
    if rel_row is None:
        key_events: list[str] = []
        if request.event_note:
            key_events.append(request.event_note)
        rel_row = NPCRelationshipDB(
            id=str(uuid.uuid4()),
            npc_id=npc_id,
            campaign_id=campaign_id,
            disposition_score=clamped_score,
            interactions_count=1,
            key_events=key_events,
            last_interaction=now_str,
        )
        db.add(rel_row)
    else:
        rel_row.disposition_score = clamped_score
        rel_row.interactions_count = (rel_row.interactions_count or 0) + 1
        rel_row.last_interaction = now_str
        existing_events: list[str] = list(rel_row.key_events or [])
        if request.event_note:
            existing_events.append(request.event_note)
        rel_row.key_events = existing_events

    db.commit()
    db.refresh(rel_row)
    return NPCRelationship(
        npc_id=rel_row.npc_id,
        campaign_id=rel_row.campaign_id,
        disposition_score=rel_row.disposition_score,
        interactions_count=rel_row.interactions_count,
        key_events=rel_row.key_events or [],
        last_interaction=rel_row.last_interaction or "",
    )
