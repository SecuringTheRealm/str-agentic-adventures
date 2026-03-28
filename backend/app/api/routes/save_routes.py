"""Save slot CRUD routes for campaign save/load functionality."""

import logging
import uuid as _uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.database import DbDep
from app.models.db_models import Campaign as CampaignDB
from app.models.db_models import SaveSlot as SaveSlotDB
from app.models.game_models import (
    MAX_SAVE_SLOTS,
    CreateSaveSlotRequest,
    SaveSlot,
    SaveSlotListResponse,
)
from app.services.game_state_service import game_state_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["saves"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _save_slot_from_db(db_slot: Any) -> SaveSlot:  # noqa: ANN401
    """Convert a SaveSlotDB ORM object to a SaveSlot Pydantic model."""
    return SaveSlot(
        id=db_slot.id,
        campaign_id=db_slot.campaign_id,
        slot_number=db_slot.slot_number,
        name=db_slot.name,
        created_at=db_slot.created_at,
        updated_at=db_slot.updated_at,
        play_time_seconds=db_slot.play_time_seconds,
        interaction_count=db_slot.interaction_count,
        character_level=db_slot.character_level,
        current_location=db_slot.current_location,
        save_data=db_slot.save_data or {},
    )


# ---------------------------------------------------------------------------
# Save Slot endpoints
# ---------------------------------------------------------------------------


@router.get("/campaign/{campaign_id}/saves", response_model=SaveSlotListResponse)
async def list_save_slots(campaign_id: str, db: DbDep) -> dict[str, Any]:
    """List all save slots for a campaign."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    db_slots = (
        db.query(SaveSlotDB)
        .filter(SaveSlotDB.campaign_id == campaign_id)
        .order_by(SaveSlotDB.slot_number)
        .all()
    )
    slots = [_save_slot_from_db(s) for s in db_slots]
    return SaveSlotListResponse(saves=slots, total_count=len(slots))


@router.post(
    "/campaign/{campaign_id}/saves",
    response_model=SaveSlot,
    status_code=status.HTTP_201_CREATED,
)
async def create_save_slot(campaign_id: str, request: CreateSaveSlotRequest, db: DbDep) -> dict[str, Any]:
    """Create a new save slot for a campaign, picking the next available slot number (1-5)."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )

    # Find occupied slot numbers
    existing = (
        db.query(SaveSlotDB.slot_number)
        .filter(SaveSlotDB.campaign_id == campaign_id)
        .all()
    )
    occupied = {row.slot_number for row in existing}

    # Pick next available slot (1-5)
    next_slot = next(
        (n for n in range(1, MAX_SAVE_SLOTS + 1) if n not in occupied), None
    )
    if next_slot is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"All {MAX_SAVE_SLOTS} save slots are occupied for campaign {campaign_id}",
        )

    now = datetime.now(UTC)
    slot_id = str(_uuid.uuid4())
    db_slot = SaveSlotDB(
        id=slot_id,
        campaign_id=campaign_id,
        slot_number=next_slot,
        name=request.name,
        created_at=now,
        updated_at=now,
        play_time_seconds=request.play_time_seconds,
        interaction_count=request.interaction_count,
        character_level=request.character_level,
        current_location=request.current_location,
        save_data=request.save_data,
    )
    db.add(db_slot)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            "Duplicate save slot race: campaign=%s slot=%d",
            campaign_id,
            next_slot,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Save slot {next_slot} was just claimed by another request. "
                "Please try again."
            ),
        ) from None
    db.refresh(db_slot)
    return _save_slot_from_db(db_slot)


@router.get("/campaign/{campaign_id}/saves/{slot_number}", response_model=SaveSlot)
async def get_save_slot(campaign_id: str, slot_number: int, db: DbDep) -> dict[str, Any]:
    """Get a specific save slot by slot number."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    db_slot = (
        db.query(SaveSlotDB)
        .filter(
            SaveSlotDB.campaign_id == campaign_id,
            SaveSlotDB.slot_number == slot_number,
        )
        .first()
    )
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Save slot {slot_number} not found for campaign {campaign_id}",
        )
    return _save_slot_from_db(db_slot)


@router.delete("/campaign/{campaign_id}/saves/{slot_number}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_save_slot(campaign_id: str, slot_number: int, db: DbDep) -> None:
    """Delete a save slot, freeing that slot number for future use."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    db_slot = (
        db.query(SaveSlotDB)
        .filter(
            SaveSlotDB.campaign_id == campaign_id,
            SaveSlotDB.slot_number == slot_number,
        )
        .first()
    )
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Save slot {slot_number} not found for campaign {campaign_id}",
        )
    db.delete(db_slot)
    db.commit()


@router.post("/campaign/{campaign_id}/saves/{slot_number}/load")
async def load_save_slot(campaign_id: str, slot_number: int, db: DbDep) -> dict[str, Any]:
    """Load a save slot, returning the full save_data state blob."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )
    db_slot = (
        db.query(SaveSlotDB)
        .filter(
            SaveSlotDB.campaign_id == campaign_id,
            SaveSlotDB.slot_number == slot_number,
        )
        .first()
    )
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Save slot {slot_number} not found for campaign {campaign_id}",
        )
    return {
        "slot_number": db_slot.slot_number,
        "name": db_slot.name,
        "character_level": db_slot.character_level,
        "current_location": db_slot.current_location,
        "play_time_seconds": db_slot.play_time_seconds,
        "interaction_count": db_slot.interaction_count,
        "save_data": db_slot.save_data or {},
    }


# ---------------------------------------------------------------------------
# Full state capture / restore endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/campaign/{campaign_id}/saves/capture",
    response_model=SaveSlot,
    status_code=status.HTTP_201_CREATED,
)
async def capture_game_state(campaign_id: str, db: DbDep):
    """Capture the current game state into a new save slot.

    Serialises all campaign data, characters, NPCs, NPC profiles,
    relationships, and conversation history, then writes the blob into the
    next available save slot.
    """
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )

    # Capture the full state
    try:
        state_data = game_state_service.capture_state(campaign_id, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    # Find next available slot
    existing = (
        db.query(SaveSlotDB.slot_number)
        .filter(SaveSlotDB.campaign_id == campaign_id)
        .all()
    )
    occupied = {row.slot_number for row in existing}
    next_slot = next(
        (n for n in range(1, MAX_SAVE_SLOTS + 1) if n not in occupied), None
    )
    if next_slot is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"All {MAX_SAVE_SLOTS} save slots are occupied"
                f" for campaign {campaign_id}"
            ),
        )

    summary = game_state_service.get_save_summary(state_data)

    now = datetime.now(UTC)
    slot_id = str(_uuid.uuid4())
    db_slot = SaveSlotDB(
        id=slot_id,
        campaign_id=campaign_id,
        slot_number=next_slot,
        name=summary.get("campaign_name", ""),
        created_at=now,
        updated_at=now,
        play_time_seconds=0,
        interaction_count=summary.get("conversation_entries", 0),
        character_level=1,
        current_location=summary.get("current_location", ""),
        save_data=state_data,
    )
    db.add(db_slot)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            "Duplicate save slot race on capture: campaign=%s slot=%d",
            campaign_id,
            next_slot,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Save slot {next_slot} was just claimed by another request. "
                "Please try again."
            ),
        ) from None
    db.refresh(db_slot)
    return _save_slot_from_db(db_slot)


@router.post("/campaign/{campaign_id}/saves/{slot_number}/restore")
async def restore_game_state(campaign_id: str, slot_number: int, db: DbDep):
    """Restore game state from a save slot.

    Reads the state blob from the specified save slot and recreates campaign
    data, characters, NPCs, profiles, and relationships in the database.
    """
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )

    db_slot = (
        db.query(SaveSlotDB)
        .filter(
            SaveSlotDB.campaign_id == campaign_id,
            SaveSlotDB.slot_number == slot_number,
        )
        .first()
    )
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Save slot {slot_number} not found for campaign {campaign_id}",
        )

    state_data = db_slot.save_data or {}
    if not state_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Save slot contains no state data to restore",
        )

    try:
        restored = game_state_service.restore_state(campaign_id, state_data, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return {
        "status": "restored",
        "slot_number": db_slot.slot_number,
        "name": db_slot.name,
        "restored_summary": restored,
    }


@router.get("/campaign/{campaign_id}/saves/{slot_number}/summary")
async def get_save_summary(campaign_id: str, slot_number: int, db: DbDep):
    """Return a human-readable summary of the state in a save slot."""
    campaign = db.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found",
        )

    db_slot = (
        db.query(SaveSlotDB)
        .filter(
            SaveSlotDB.campaign_id == campaign_id,
            SaveSlotDB.slot_number == slot_number,
        )
        .first()
    )
    if not db_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Save slot {slot_number} not found for campaign {campaign_id}",
        )

    state_data = db_slot.save_data or {}
    summary = game_state_service.get_save_summary(state_data)
    return summary
