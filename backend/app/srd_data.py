"""
Utility module for loading and accessing D&D 5e SRD data.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Path to data directory
DATA_DIR = Path(__file__).parent / "data"

# Global data stores
_class_features_data: Optional[Dict[str, Any]] = None
_racial_traits_data: Optional[Dict[str, Any]] = None
_backgrounds_data: Optional[Dict[str, Any]] = None
_spells_data: Optional[List[Dict[str, Any]]] = None


def load_class_features() -> Dict[str, Any]:
    """Load class features data from JSON file."""
    global _class_features_data
    if _class_features_data is None:
        try:
            with open(DATA_DIR / "class_features.json", "r") as f:
                _class_features_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load class features data: {e}")
            _class_features_data = {}
    return _class_features_data


def load_racial_traits() -> Dict[str, Any]:
    """Load racial traits data from JSON file."""
    global _racial_traits_data
    if _racial_traits_data is None:
        try:
            with open(DATA_DIR / "racial_traits.json", "r") as f:
                _racial_traits_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load racial traits data: {e}")
            _racial_traits_data = {}
    return _racial_traits_data


def load_backgrounds() -> Dict[str, Any]:
    """Load backgrounds data from JSON file."""
    global _backgrounds_data
    if _backgrounds_data is None:
        try:
            with open(DATA_DIR / "backgrounds.json", "r") as f:
                _backgrounds_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load backgrounds data: {e}")
            _backgrounds_data = {}
    return _backgrounds_data


def load_spells() -> List[Dict[str, Any]]:
    """Load spells data from JSON file."""
    global _spells_data
    if _spells_data is None:
        try:
            with open(DATA_DIR / "spells.json", "r") as f:
                _spells_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load spells data: {e}")
            _spells_data = []
    return _spells_data


def get_class_features(character_class: str, level: int) -> List[Dict[str, Any]]:
    """Get class features for a specific class and level."""
    class_data = load_class_features()
    class_info = class_data.get(character_class.lower(), {})
    features = class_info.get("features", {})
    return features.get(str(level), [])


def get_class_info(character_class: str) -> Dict[str, Any]:
    """Get class information including hit die and saving throws."""
    class_data = load_class_features()
    return class_data.get(character_class.lower(), {})


def get_racial_traits(race: str) -> Dict[str, Any]:
    """Get racial traits for a specific race."""
    racial_data = load_racial_traits()
    return racial_data.get(race.lower().replace("_", "-"), {})


def get_background_info(background: str) -> Dict[str, Any]:
    """Get background information including skill proficiencies."""
    backgrounds = load_backgrounds()
    return backgrounds.get(background.lower(), {})


def get_spells_by_class(character_class: str) -> List[Dict[str, Any]]:
    """Get all spells available to a specific class."""
    spells = load_spells()
    return [spell for spell in spells if character_class.lower() in spell.get("available_classes", [])]


def get_spells_by_level(spell_level: int) -> List[Dict[str, Any]]:
    """Get all spells of a specific level."""
    spells = load_spells()
    return [spell for spell in spells if spell.get("level") == spell_level]


def get_spell_by_id(spell_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific spell by ID."""
    spells = load_spells()
    return next((spell for spell in spells if spell.get("id") == spell_id), None)


def apply_racial_ability_bonuses(abilities: Dict[str, int], race: str) -> Dict[str, int]:
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


def get_class_saving_throws(character_class: str) -> List[str]:
    """Get saving throw proficiencies for a character class."""
    class_info = get_class_info(character_class)
    return class_info.get("saving_throw_proficiencies", [])


def get_class_spellcasting_ability(character_class: str) -> Optional[str]:
    """Get the spellcasting ability for a character class."""
    class_info = get_class_info(character_class)
    return class_info.get("spellcasting_ability")