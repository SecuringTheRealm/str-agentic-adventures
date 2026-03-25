"""
Utility module for loading and accessing D&D 5e SRD data.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Path to data directory
DATA_DIR = Path(__file__).parent / "data"

# Global data stores
_class_features_data: dict[str, Any] | None = None
_racial_traits_data: dict[str, Any] | None = None
_backgrounds_data: dict[str, Any] | None = None
_spells_data: list[dict[str, Any]] | None = None
_monsters_data: list[dict[str, Any]] | None = None
_weapons_data: dict[str, Any] | None = None
_armor_data: dict[str, Any] | None = None

# XP required to reach each character level (D&D 5e SRD)
XP_THRESHOLDS: dict[int, int] = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000,
}

# Hit die size per class (D&D 5e SRD)
CLASS_HIT_DICE: dict[str, int] = {
    "barbarian": 12,
    "fighter": 10,
    "paladin": 10,
    "ranger": 10,
    "bard": 8,
    "cleric": 8,
    "druid": 8,
    "monk": 8,
    "rogue": 8,
    "warlock": 8,
    "sorcerer": 6,
    "wizard": 6,
}


def load_class_features() -> dict[str, Any]:
    """Load class features data from JSON file."""
    global _class_features_data
    if _class_features_data is None:
        try:
            with open(DATA_DIR / "class_features.json") as f:
                _class_features_data = json.load(f)
        except Exception as e:
            logger.error("Failed to load class features data: %s", e)
            _class_features_data = {}
    return _class_features_data


def load_racial_traits() -> dict[str, Any]:
    """Load racial traits data from JSON file."""
    global _racial_traits_data
    if _racial_traits_data is None:
        try:
            with open(DATA_DIR / "racial_traits.json") as f:
                _racial_traits_data = json.load(f)
        except Exception as e:
            logger.error("Failed to load racial traits data: %s", e)
            _racial_traits_data = {}
    return _racial_traits_data


def load_backgrounds() -> dict[str, Any]:
    """Load backgrounds data from JSON file."""
    global _backgrounds_data
    if _backgrounds_data is None:
        try:
            with open(DATA_DIR / "backgrounds.json") as f:
                _backgrounds_data = json.load(f)
        except Exception as e:
            logger.error("Failed to load backgrounds data: %s", e)
            _backgrounds_data = {}
    return _backgrounds_data


def load_spells() -> list[dict[str, Any]]:
    """Load spells data from JSON file."""
    global _spells_data
    if _spells_data is None:
        try:
            with open(DATA_DIR / "spells.json") as f:
                _spells_data = json.load(f)
        except Exception as e:
            logger.error("Failed to load spells data: %s", e)
            _spells_data = []
    return _spells_data


def get_class_features(character_class: str, level: int) -> list[dict[str, Any]]:
    """Get class features for a specific class and level."""
    class_data = load_class_features()
    class_info = class_data.get(character_class.lower(), {})
    features = class_info.get("features", {})
    return features.get(str(level), [])


def get_class_info(character_class: str) -> dict[str, Any]:
    """Get class information including hit die and saving throws."""
    class_data = load_class_features()
    return class_data.get(character_class.lower(), {})


def get_racial_traits(race: str) -> dict[str, Any]:
    """Get racial traits for a specific race."""
    racial_data = load_racial_traits()
    return racial_data.get(race.lower().replace("_", "-"), {})


def get_background_info(background: str) -> dict[str, Any]:
    """Get background information including skill proficiencies."""
    backgrounds = load_backgrounds()
    return backgrounds.get(background.lower(), {})


def get_spells_by_class(character_class: str) -> list[dict[str, Any]]:
    """Get all spells available to a specific class."""
    spells = load_spells()
    return [
        spell
        for spell in spells
        if character_class.lower() in spell.get("available_classes", [])
    ]


def get_spells_by_level(spell_level: int) -> list[dict[str, Any]]:
    """Get all spells of a specific level."""
    spells = load_spells()
    return [spell for spell in spells if spell.get("level") == spell_level]


def get_spell_by_id(spell_id: str) -> dict[str, Any] | None:
    """Get a specific spell by ID."""
    spells = load_spells()
    return next((spell for spell in spells if spell.get("id") == spell_id), None)


def apply_racial_ability_bonuses(
    abilities: dict[str, int], race: str
) -> dict[str, int]:
    """Apply racial ability score bonuses to character abilities."""
    racial_data = get_racial_traits(race)
    bonuses = racial_data.get("ability_score_increases", {})

    updated_abilities = abilities.copy()
    for ability, bonus in bonuses.items():
        if ability in updated_abilities:
            # Apply racial bonus, but cap at 20
            updated_abilities[ability] = min(updated_abilities[ability] + bonus, 20)

    return updated_abilities


def get_racial_speed(race: str) -> int:
    """Get the base speed for a race."""
    racial_data = get_racial_traits(race)
    return racial_data.get("speed", 30)


def get_class_hit_die(character_class: str) -> str:
    """Get the hit die for a character class."""
    class_info = get_class_info(character_class)
    return class_info.get("hit_die", "1d8")


def get_class_saving_throws(character_class: str) -> list[str]:
    """Get saving throw proficiencies for a character class."""
    class_info = get_class_info(character_class)
    return class_info.get("saving_throw_proficiencies", [])


def get_class_spellcasting_ability(character_class: str) -> str | None:
    """Get the spellcasting ability for a character class."""
    class_info = get_class_info(character_class)
    return class_info.get("spellcasting_ability")


def get_level_for_xp(xp: int) -> int:
    """Return the character level corresponding to the given XP total."""
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level


# ---------------------------------------------------------------------------
# Monsters
# ---------------------------------------------------------------------------


def load_monsters() -> list[dict[str, Any]]:
    """Load monster stat blocks from JSON file."""
    global _monsters_data
    if _monsters_data is None:
        try:
            with open(DATA_DIR / "monsters.json") as f:
                _monsters_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load monsters data: {e}")
            _monsters_data = []
    return _monsters_data


def get_monster_by_id(monster_id: str) -> dict[str, Any] | None:
    """Get a monster stat block by its ID."""
    monsters = load_monsters()
    return next(
        (m for m in monsters if m.get("id") == monster_id.lower().replace(" ", "_")),
        None,
    )


def get_monster_by_name(name: str) -> dict[str, Any] | None:
    """Get a monster stat block by its name (case-insensitive)."""
    monsters = load_monsters()
    return next(
        (m for m in monsters if m.get("name", "").lower() == name.lower()),
        None,
    )


def get_monsters_by_cr(cr: str) -> list[dict[str, Any]]:
    """Get all monsters with a specific challenge rating."""
    monsters = load_monsters()
    return [m for m in monsters if str(m.get("cr")) == str(cr)]


def get_monsters_by_type(monster_type: str) -> list[dict[str, Any]]:
    """Get all monsters of a specific type (e.g. 'humanoid', 'undead')."""
    monsters = load_monsters()
    return [
        m
        for m in monsters
        if m.get("type", "").lower() == monster_type.lower()
    ]


# ---------------------------------------------------------------------------
# Weapons
# ---------------------------------------------------------------------------


def load_weapons() -> dict[str, Any]:
    """Load weapon tables from JSON file."""
    global _weapons_data
    if _weapons_data is None:
        try:
            with open(DATA_DIR / "weapons.json") as f:
                _weapons_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load weapons data: {e}")
            _weapons_data = {}
    return _weapons_data


def get_all_weapons() -> list[dict[str, Any]]:
    """Return a flat list of all weapons across all categories."""
    weapons_by_category = load_weapons()
    all_weapons: list[dict[str, Any]] = []
    for category_weapons in weapons_by_category.values():
        all_weapons.extend(category_weapons)
    return all_weapons


def get_weapon_by_id(weapon_id: str) -> dict[str, Any] | None:
    """Get a weapon by its ID."""
    return next(
        (w for w in get_all_weapons() if w.get("id") == weapon_id.lower()),
        None,
    )


def get_weapons_by_category(category: str) -> list[dict[str, Any]]:
    """Get all weapons in a category (e.g. 'simple_melee', 'martial_ranged')."""
    weapons_by_category = load_weapons()
    return weapons_by_category.get(category.lower(), [])


def get_weapons_with_property(prop: str) -> list[dict[str, Any]]:
    """Get all weapons that have a specific property (e.g. 'finesse', 'heavy')."""
    return [
        w for w in get_all_weapons() if prop.lower() in w.get("properties", [])
    ]


# ---------------------------------------------------------------------------
# Armor
# ---------------------------------------------------------------------------


def load_armor() -> dict[str, Any]:
    """Load armor table from JSON file."""
    global _armor_data
    if _armor_data is None:
        try:
            with open(DATA_DIR / "armor.json") as f:
                _armor_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load armor data: {e}")
            _armor_data = {}
    return _armor_data


def get_all_armor() -> list[dict[str, Any]]:
    """Return a flat list of all armor pieces across all categories."""
    armor_by_category = load_armor()
    all_armor: list[dict[str, Any]] = []
    for category_armor in armor_by_category.values():
        all_armor.extend(category_armor)
    return all_armor


def get_armor_by_id(armor_id: str) -> dict[str, Any] | None:
    """Get an armor entry by its ID."""
    return next(
        (a for a in get_all_armor() if a.get("id") == armor_id.lower()),
        None,
    )


def get_armor_by_category(category: str) -> list[dict[str, Any]]:
    """Get all armor in a category (e.g. 'light', 'medium', 'heavy', 'shield')."""
    armor_by_category = load_armor()
    return armor_by_category.get(category.lower(), [])


def calculate_armor_class(
    armor_id: str, dexterity_modifier: int, shield: bool = False
) -> int:
    """Calculate total AC for a given armor, DEX modifier, and optional shield."""
    armor = get_armor_by_id(armor_id)
    if armor is None:
        # Unarmored: 10 + DEX modifier
        return 10 + dexterity_modifier

    base_ac = armor.get("base_ac", 10)
    dex_cap = armor.get("dex_bonus_cap")
    category = armor.get("category", "")

    if category == "shield":
        # Shield by itself doesn't grant a full AC; it adds to existing AC.
        # Treat as unarmored + shield bonus when called standalone.
        return 10 + dexterity_modifier + base_ac

    if dex_cap is None:
        # No cap: add full DEX modifier
        effective_dex = dexterity_modifier
    elif dex_cap == 0:
        # Heavy armour: no DEX bonus
        effective_dex = 0
    else:
        effective_dex = min(dexterity_modifier, dex_cap)

    total = base_ac + effective_dex
    if shield:
        shield_entry = get_armor_by_id("shield")
        total += shield_entry.get("base_ac", 2) if shield_entry else 2
    return total
