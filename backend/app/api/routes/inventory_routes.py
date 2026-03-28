"""Inventory and equipment management routes."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    AddInventoryItemRequest,
    Inventory,
    InventoryActionResponse,
    InventoryItem,
    ItemType,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["inventory"])


def _get_character_inventory(character: dict) -> Inventory:
    """Deserialise the structured_inventory field from a character dict."""
    raw = character.get("structured_inventory")
    if raw is None:
        return Inventory()
    if isinstance(raw, Inventory):
        return raw
    return Inventory.model_validate(raw)


def _find_item(inventory: Inventory, item_id: str) -> InventoryItem | None:
    """Find an item in the inventory by ID."""
    for item in inventory.items:
        if item.id == item_id:
            return item
    return None


def _slot_for_item_type(item_type: ItemType) -> str | None:
    """Return the equipment slot name for a given item type, or None."""
    mapping = {
        ItemType.WEAPON: "main_hand",
        ItemType.SHIELD: "off_hand",
        ItemType.ARMOR: "armor",
    }
    return mapping.get(item_type)


@router.post("/inventory/{character_id}/add", response_model=InventoryActionResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    character_id: str, request: AddInventoryItemRequest
) -> InventoryActionResponse:
    """Add an item to a character's structured inventory."""
    try:
        from app.agents.scribe_agent import get_scribe

        scribe = get_scribe()
        character = await scribe.get_character(character_id)
        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        inv = _get_character_inventory(character)

        new_item = InventoryItem(
            name=request.name,
            item_type=request.item_type,
            weight=request.weight,
            quantity=request.quantity,
            requires_attunement=request.requires_attunement,
            description=request.description,
        )
        inv.items.append(new_item)

        character["structured_inventory"] = inv.model_dump()
        await scribe.update_character(character_id, character)

        return InventoryActionResponse(
            success=True,
            message=f"Added {new_item.name} to inventory",
            inventory=inv,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to add item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add item: {e}",
        ) from e


@router.delete(
    "/inventory/{character_id}/remove/{item_id}",
    response_model=InventoryActionResponse,
)
async def remove_item(
    character_id: str, item_id: str
) -> InventoryActionResponse:
    """Remove an item from a character's structured inventory."""
    try:
        from app.agents.scribe_agent import get_scribe

        scribe = get_scribe()
        character = await scribe.get_character(character_id)
        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        inv = _get_character_inventory(character)
        item = _find_item(inv, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found in inventory",
            )

        # Unequip if currently equipped
        if item.equipped:
            slot_name = _slot_for_item_type(item.item_type)
            if slot_name and getattr(inv.equipment, slot_name) == item.id:
                setattr(inv.equipment, slot_name, None)
            item.equipped = False
            item.attuned = False

        inv.items = [i for i in inv.items if i.id != item_id]

        character["structured_inventory"] = inv.model_dump()
        await scribe.update_character(character_id, character)

        return InventoryActionResponse(
            success=True,
            message=f"Removed {item.name} from inventory",
            inventory=inv,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to remove item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove item: {e}",
        ) from e


@router.post(
    "/inventory/{character_id}/equip/{item_id}",
    response_model=InventoryActionResponse,
)
async def equip_item(
    character_id: str, item_id: str
) -> InventoryActionResponse:
    """Equip an item from the character's inventory."""
    try:
        from app.agents.scribe_agent import get_scribe

        scribe = get_scribe()
        character = await scribe.get_character(character_id)
        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        inv = _get_character_inventory(character)
        item = _find_item(inv, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found in inventory",
            )

        if item.equipped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item {item.name} is already equipped",
            )

        # Validate that the item can be equipped
        slot_name = _slot_for_item_type(item.item_type)
        if slot_name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot equip item of type {item.item_type.value}",
            )

        # Check attunement limit
        if item.requires_attunement:
            attuned_count = sum(1 for i in inv.items if i.attuned)
            if attuned_count >= inv.max_attunements:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot attune: already at maximum "
                        f"({inv.max_attunements}) attunements"
                    ),
                )

        # Unequip whatever is currently in that slot
        current_id = getattr(inv.equipment, slot_name)
        if current_id is not None:
            current_item = _find_item(inv, current_id)
            if current_item is not None:
                current_item.equipped = False
                current_item.attuned = False

        setattr(inv.equipment, slot_name, item.id)
        item.equipped = True
        if item.requires_attunement:
            item.attuned = True

        character["structured_inventory"] = inv.model_dump()
        await scribe.update_character(character_id, character)

        return InventoryActionResponse(
            success=True,
            message=f"Equipped {item.name} in {slot_name}",
            inventory=inv,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to equip item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to equip item: {e}",
        ) from e


@router.post(
    "/inventory/{character_id}/unequip/{item_id}",
    response_model=InventoryActionResponse,
)
async def unequip_item(
    character_id: str, item_id: str
) -> InventoryActionResponse:
    """Unequip an item, returning it to unequipped inventory state."""
    try:
        from app.agents.scribe_agent import get_scribe

        scribe = get_scribe()
        character = await scribe.get_character(character_id)
        if character is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character {character_id} not found",
            )

        inv = _get_character_inventory(character)
        item = _find_item(inv, item_id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found in inventory",
            )

        if not item.equipped:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Item {item.name} is not equipped",
            )

        # Clear the equipment slot
        slot_name = _slot_for_item_type(item.item_type)
        if slot_name and getattr(inv.equipment, slot_name) == item.id:
            setattr(inv.equipment, slot_name, None)

        item.equipped = False
        item.attuned = False

        character["structured_inventory"] = inv.model_dump()
        await scribe.update_character(character_id, character)

        return InventoryActionResponse(
            success=True,
            message=f"Unequipped {item.name}",
            inventory=inv,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to unequip item")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unequip item: {e}",
        ) from e
