"""Items system routes."""

import logging

from fastapi import APIRouter, HTTPException, status

from app.models.game_models import (
    Equipment,
    ItemCatalogResponse,
    ItemRarity,
    ItemType,
    MagicalEffectsRequest,
    MagicalEffectsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["items"])


@router.post("/items/magical-effects", response_model=MagicalEffectsResponse)
async def manage_magical_effects(request: MagicalEffectsRequest):
    """Apply magical item effects to character stats."""
    try:
        # Sample magical item effects
        magical_effects = {
            "cloak_of_elvenkind": {
                "stealth": 2,
                "perception": 2,
                "effects": [
                    "Advantage on Dexterity (Stealth) checks",
                    "Disadvantage on Perception checks against you",
                ],
            },
            "gauntlets_of_ogre_power": {
                "strength": 19,  # Sets Strength to 19 if it's lower
                "effects": ["Strength becomes 19", "Advantage on Strength checks"],
            },
            "ring_of_mind_shielding": {
                "effects": ["Immune to charm", "Mind cannot be read", "Soul protected"]
            },
        }

        item_effects = magical_effects.get(request.item_id.lower(), {})

        if request.action == "apply":
            message = f"Applied magical effects of {request.item_id}"
            active_effects = item_effects.get("effects", [])
            stat_modifiers = {k: v for k, v in item_effects.items() if k != "effects"}
        elif request.action == "remove":
            message = f"Removed magical effects of {request.item_id}"
            active_effects = []
            stat_modifiers = {}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid action: {request.action}",
            )

        return MagicalEffectsResponse(
            success=True,
            message=message,
            active_effects=active_effects,
            stat_modifiers=stat_modifiers,
        )
    except HTTPException:
        raise
    except Exception as e:
        return MagicalEffectsResponse(
            success=False,
            message=f"Failed to manage magical effects: {str(e)}",
            active_effects=[],
            stat_modifiers={},
        )


@router.get("/items/catalog", response_model=ItemCatalogResponse)
async def get_item_catalog(
    item_type: ItemType | None = None,
    rarity: ItemRarity | None = None,
    min_value: int | None = None,
    max_value: int | None = None,
):
    """Browse available items with rarity and value information."""
    try:
        # Sample equipment catalog
        sample_items = [
            Equipment(
                name="Longsword",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.COMMON,
                weight=3.0,
                value=15,
                damage_dice="1d8",
                damage_type="slashing",
                properties=["versatile"],
            ),
            Equipment(
                name="Plate Armor",
                item_type=ItemType.ARMOR,
                rarity=ItemRarity.COMMON,
                weight=65.0,
                value=1500,
                armor_class=18,
                stat_modifiers={"stealth": -1},
            ),
            Equipment(
                name="Ring of Protection",
                item_type=ItemType.RING,
                rarity=ItemRarity.RARE,
                weight=0.1,
                value=3500,
                requires_attunement=True,
                is_magical=True,
                stat_modifiers={"armor_class": 1, "saving_throws": 1},
            ),
            Equipment(
                name="Flame Tongue",
                item_type=ItemType.WEAPON,
                rarity=ItemRarity.RARE,
                weight=3.0,
                value=5000,
                requires_attunement=True,
                is_magical=True,
                damage_dice="1d8",
                damage_type="slashing",
                special_abilities=["Fire damage", "Light source"],
                properties=["versatile"],
            ),
            Equipment(
                name="Thieves' Tools",
                item_type=ItemType.TOOL,
                rarity=ItemRarity.COMMON,
                weight=1.0,
                value=25,
            ),
        ]

        # Filter items based on parameters
        filtered_items = sample_items
        if item_type:
            filtered_items = [
                item for item in filtered_items if item.item_type == item_type
            ]
        if rarity:
            filtered_items = [item for item in filtered_items if item.rarity == rarity]
        if min_value is not None:
            filtered_items = [
                item
                for item in filtered_items
                if item.value and item.value >= min_value
            ]
        if max_value is not None:
            filtered_items = [
                item
                for item in filtered_items
                if item.value and item.value <= max_value
            ]

        return ItemCatalogResponse(
            items=filtered_items, total_count=len(filtered_items)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get item catalog: {str(e)}",
        ) from e
