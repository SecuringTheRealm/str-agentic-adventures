"""
D&D 5e SRD Spell Data Repository
Contains spell information organized by class accessibility and spell level.
"""

from typing import Dict, List, Set
from app.models.game_models import CharacterClass

# Core spell data with basic information
SPELL_DATA = {
    # Cantrips (Level 0)
    "acid_splash": {
        "name": "Acid Splash",
        "level": 0,
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You hurl a bubble of acid. Choose one or two creatures within range. A creature must succeed on a Dexterity saving throw or take 1d6 acid damage.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "dancing_lights": {
        "name": "Dancing Lights",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S, M (a bit of phosphorus or wychwood, or a glowworm)",
        "duration": "Concentration, up to 1 minute",
        "description": "You create up to four torch-sized lights within range, making them appear as torches, lanterns, or glowing orbs.",
        "classes": {CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "fire_bolt": {
        "name": "Fire Bolt",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You hurl a mote of fire at a creature or object within range. Make a ranged spell attack. On a hit, the target takes 1d10 fire damage.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "guidance": {
        "name": "Guidance",
        "level": 0,
        "school": "Divination",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S",
        "duration": "Concentration, up to 1 minute",
        "description": "You touch one willing creature. Once before the spell ends, the target can roll a d4 and add the number rolled to one ability check of its choice.",
        "classes": {CharacterClass.CLERIC, CharacterClass.DRUID}
    },
    "light": {
        "name": "Light",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, M (a firefly or phosphorescent moss)",
        "duration": "1 hour",
        "description": "You touch one object that is no larger than 10 feet in any dimension. Until the spell ends, the object sheds bright light in a 20-foot radius.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "mage_hand": {
        "name": "Mage Hand",
        "level": 0,
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "30 feet",
        "components": "V, S",
        "duration": "1 minute",
        "description": "A spectral, floating hand appears at a point you choose within range. The hand lasts for the duration or until you dismiss it as an action.",
        "classes": {CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WARLOCK, CharacterClass.WIZARD}
    },
    "prestidigitation": {
        "name": "Prestidigitation",
        "level": 0,
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "10 feet",
        "components": "V, S",
        "duration": "Up to 1 hour",
        "description": "This spell is a minor magical trick that novice spellcasters use for practice. You create one of several magical effects within range.",
        "classes": {CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WARLOCK, CharacterClass.WIZARD}
    },
    "sacred_flame": {
        "name": "Sacred Flame",
        "level": 0,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "Flame-like radiance descends on a creature that you can see within range. The target must succeed on a Dexterity saving throw or take 1d8 radiant damage.",
        "classes": {CharacterClass.CLERIC}
    },
    
    # 1st Level Spells
    "burning_hands": {
        "name": "Burning Hands",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Self (15-foot cone)",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "As you hold your hands with thumbs touching and fingers spread, a thin sheet of flames shoots forth from your outstretched fingertips.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "cure_wounds": {
        "name": "Cure Wounds",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.PALADIN, CharacterClass.RANGER}
    },
    "detect_magic": {
        "name": "Detect Magic",
        "level": 1,
        "school": "Divination",
        "casting_time": "1 action",
        "range": "Self",
        "components": "V, S",
        "duration": "Concentration, up to 10 minutes",
        "description": "For the duration, you sense the presence of magic within 30 feet of you.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.PALADIN, CharacterClass.RANGER, CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "magic_missile": {
        "name": "Magic Missile",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "shield": {
        "name": "Shield",
        "level": 1,
        "school": "Abjuration",
        "casting_time": "1 reaction",
        "range": "Self",
        "components": "V, S",
        "duration": "1 round",
        "description": "An invisible barrier of magical force appears and protects you. Until the start of your next turn, you have a +5 bonus to AC.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "healing_word": {
        "name": "Healing Word",
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 bonus action",
        "range": "60 feet",
        "components": "V",
        "duration": "Instantaneous",
        "description": "A creature of your choice that you can see within range regains hit points equal to 1d4 + your spellcasting ability modifier.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID}
    },
    "hex": {
        "name": "Hex",
        "level": 1,
        "school": "Enchantment",
        "casting_time": "1 bonus action",
        "range": "90 feet",
        "components": "V, S, M (the petrified eye of a newt)",
        "duration": "Concentration, up to 1 hour",
        "description": "You place a curse on a creature that you can see within range. Until the spell ends, you deal an extra 1d6 necrotic damage to the target whenever you hit it with an attack.",
        "classes": {CharacterClass.WARLOCK}
    },
    
    # 2nd Level Spells
    "hold_person": {
        "name": "Hold Person",
        "level": 2,
        "school": "Enchantment",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S, M (a small, straight piece of iron)",
        "duration": "Concentration, up to 1 minute",
        "description": "Choose a humanoid that you can see within range. The target must succeed on a Wisdom saving throw or be paralyzed for the duration.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WARLOCK, CharacterClass.WIZARD}
    },
    "invisibility": {
        "name": "Invisibility",
        "level": 2,
        "school": "Illusion",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S, M (an eyelash encased in gum arabic)",
        "duration": "Concentration, up to 1 hour",
        "description": "A creature you touch becomes invisible until the spell ends.",
        "classes": {CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WARLOCK, CharacterClass.WIZARD}
    },
    "lesser_restoration": {
        "name": "Lesser Restoration",
        "level": 2,
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You touch a creature and can end either one disease or one condition afflicting it.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID, CharacterClass.PALADIN, CharacterClass.RANGER}
    },
    "web": {
        "name": "Web",
        "level": 2,
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S, M (a bit of spiderweb)",
        "duration": "Concentration, up to 1 hour",
        "description": "You conjure a mass of thick, sticky webbing at a point of your choice within range.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    
    # Higher level spells (3rd-9th level examples)
    "fireball": {
        "name": "Fireball",
        "level": 3,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "components": "V, S, M (a tiny ball of bat guano and sulfur)",
        "duration": "Instantaneous",
        "description": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "counterspell": {
        "name": "Counterspell",
        "level": 3,
        "school": "Abjuration",
        "casting_time": "1 reaction",
        "range": "60 feet",
        "components": "S",
        "duration": "Instantaneous",
        "description": "You attempt to interrupt a creature in the process of casting a spell.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WARLOCK, CharacterClass.WIZARD}
    },
    "lightning_bolt": {
        "name": "Lightning Bolt",
        "level": 3,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Self (100-foot line)",
        "components": "V, S, M (a bit of fur and a rod of amber, crystal, or glass)",
        "duration": "Instantaneous",
        "description": "A stroke of lightning forming a line 100 feet long and 5 feet wide blasts out from you in a direction you choose.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "revivify": {
        "name": "Revivify",
        "level": 3,
        "school": "Necromancy",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S, M (diamonds worth 300 gp, which the spell consumes)",
        "duration": "Instantaneous",
        "description": "You touch a creature that has died within the last minute. That creature returns to life with 1 hit point.",
        "classes": {CharacterClass.CLERIC, CharacterClass.PALADIN}
    },
    "polymorph": {
        "name": "Polymorph",
        "level": 4,
        "school": "Transmutation",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S, M (a caterpillar cocoon)",
        "duration": "Concentration, up to 1 hour",
        "description": "This spell transforms a creature that you can see within range into a new form.",
        "classes": {CharacterClass.BARD, CharacterClass.DRUID, CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "greater_restoration": {
        "name": "Greater Restoration",
        "level": 5,
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S, M (diamond dust worth at least 100 gp, which the spell consumes)",
        "duration": "Instantaneous",
        "description": "You imbue a creature you touch with positive energy to undo a debilitating effect.",
        "classes": {CharacterClass.BARD, CharacterClass.CLERIC, CharacterClass.DRUID}
    },
    "teleport": {
        "name": "Teleport",
        "level": 7,
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "10 feet",
        "components": "V",
        "duration": "Instantaneous",
        "description": "This spell instantly transports you and up to eight willing creatures of your choice that you can see within range.",
        "classes": {CharacterClass.BARD, CharacterClass.SORCERER, CharacterClass.WIZARD}
    },
    "wish": {
        "name": "Wish",
        "level": 9,
        "school": "Conjuration",
        "casting_time": "1 action",
        "range": "Self",
        "components": "V",
        "duration": "Instantaneous",
        "description": "Wish is the mightiest spell a mortal creature can cast. By simply speaking aloud, you can alter the very foundations of reality.",
        "classes": {CharacterClass.SORCERER, CharacterClass.WIZARD}
    }
}

# Spell slot progression by class and level (D&D 5e SRD)
# This determines which spell levels a character can cast at each level
SPELL_SLOT_PROGRESSION = {
    # Full casters (Bard, Cleric, Druid, Sorcerer, Wizard)
    "full_caster": {
        1: [2],  # 2 first-level slots
        2: [3],  # 3 first-level slots
        3: [4, 2],  # 4 first-level, 2 second-level slots
        4: [4, 3],
        5: [4, 3, 2],  # 4 first, 3 second, 2 third-level slots
        6: [4, 3, 3],
        7: [4, 3, 3, 1],  # 4 first, 3 second, 3 third, 1 fourth-level slot
        8: [4, 3, 3, 2],
        9: [4, 3, 3, 3, 1],  # 4 first, 3 second, 3 third, 3 fourth, 1 fifth-level slot
        10: [4, 3, 3, 3, 2],
        11: [4, 3, 3, 3, 2, 1],  # 6th level spells
        12: [4, 3, 3, 3, 2, 1],
        13: [4, 3, 3, 3, 2, 1, 1],  # 7th level spells
        14: [4, 3, 3, 3, 2, 1, 1],
        15: [4, 3, 3, 3, 2, 1, 1, 1],  # 8th level spells
        16: [4, 3, 3, 3, 2, 1, 1, 1],
        17: [4, 3, 3, 3, 2, 1, 1, 1, 1],  # 9th level spells
        18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
        19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
        20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
    },
    # Half casters (Paladin, Ranger)
    "half_caster": {
        1: [],  # No spells at level 1
        2: [2],  # 2 first-level slots
        3: [3],
        4: [3],
        5: [4, 2],  # 4 first, 2 second-level slots
        6: [4, 2],
        7: [4, 3],
        8: [4, 3],
        9: [4, 3, 2],  # 4 first, 3 second, 2 third-level slots
        10: [4, 3, 2],
        11: [4, 3, 3],
        12: [4, 3, 3],
        13: [4, 3, 3, 1],  # 4 first, 3 second, 3 third, 1 fourth-level slot
        14: [4, 3, 3, 1],
        15: [4, 3, 3, 2],
        16: [4, 3, 3, 2],
        17: [4, 3, 3, 3, 1],  # 5th level spells
        18: [4, 3, 3, 3, 1],
        19: [4, 3, 3, 3, 2],
        20: [4, 3, 3, 3, 2]
    },
    # Warlock (unique pact magic)
    "warlock": {
        1: [1],  # 1 first-level slot
        2: [2],  # 2 first-level slots
        3: [0, 2],  # 2 second-level slots (all slots are the same level)
        4: [0, 2],
        5: [0, 0, 2],  # 2 third-level slots
        6: [0, 0, 2],
        7: [0, 0, 0, 2],  # 2 fourth-level slots
        8: [0, 0, 0, 2],
        9: [0, 0, 0, 0, 2],  # 2 fifth-level slots
        10: [0, 0, 0, 0, 2],
        11: [0, 0, 0, 0, 3],  # 3 fifth-level slots
        12: [0, 0, 0, 0, 3],
        13: [0, 0, 0, 0, 3],
        14: [0, 0, 0, 0, 3],
        15: [0, 0, 0, 0, 3],
        16: [0, 0, 0, 0, 3],
        17: [0, 0, 0, 0, 4],  # 4 fifth-level slots
        18: [0, 0, 0, 0, 4],
        19: [0, 0, 0, 0, 4],
        20: [0, 0, 0, 0, 4]
    }
}

# Map classes to their caster types
CLASS_CASTER_TYPE = {
    CharacterClass.BARD: "full_caster",
    CharacterClass.CLERIC: "full_caster",
    CharacterClass.DRUID: "full_caster",
    CharacterClass.SORCERER: "full_caster",
    CharacterClass.WIZARD: "full_caster",
    CharacterClass.PALADIN: "half_caster",
    CharacterClass.RANGER: "half_caster",
    CharacterClass.WARLOCK: "warlock",
    # Non-casting classes
    CharacterClass.BARBARIAN: None,
    CharacterClass.FIGHTER: None,
    CharacterClass.MONK: None,
    CharacterClass.ROGUE: None,
}


def get_available_spells(character_class: CharacterClass, character_level: int, spell_level: int = None) -> List[Dict]:
    """
    Get available spells for a character class at a given level.
    
    Args:
        character_class: The character's class
        character_level: The character's level (1-20)
        spell_level: Optional filter for specific spell level (0-9)
    
    Returns:
        List of spell dictionaries that the character can cast
    """
    # Check if this class can cast spells
    caster_type = CLASS_CASTER_TYPE.get(character_class)
    if not caster_type:
        return []
    
    # Get the spell slot progression for this class
    progression = SPELL_SLOT_PROGRESSION[caster_type]
    
    # Determine the highest spell level this character can cast
    if character_level not in progression:
        return []
    
    slots = progression[character_level]
    max_spell_level = len(slots) - 1  # Index 0 is 1st level, so length-1 is max level
    
    # If a specific spell level is requested, check if it's available
    if spell_level is not None:
        if spell_level == 0:  # Cantrips are always available for casters
            max_spell_level = 0
        elif spell_level > max_spell_level or (spell_level > 0 and len(slots) < spell_level or slots[spell_level - 1] == 0):
            return []
        else:
            max_spell_level = spell_level
    
    # Filter spells by class and level
    available_spells = []
    for spell_id, spell_data in SPELL_DATA.items():
        # Check if this class can learn this spell
        if character_class not in spell_data["classes"]:
            continue
        
        # Check spell level requirements
        if spell_level is not None:
            # If a specific spell level is requested, only return spells of that level
            if spell_data["level"] != spell_level:
                continue
        else:
            # If no specific level requested, return all spells the character can cast
            if spell_data["level"] > max_spell_level:
                continue
    
        # Convert to API format
        spell_dict = {
            "id": spell_id,
            "name": spell_data["name"],
            "level": spell_data["level"],
            "school": spell_data["school"],
            "casting_time": spell_data["casting_time"],
            "range": spell_data["range"],
            "components": spell_data["components"],
            "duration": spell_data["duration"],
            "description": spell_data["description"]
        }
        available_spells.append(spell_dict)
    
    # Sort by level, then by name
    available_spells.sort(key=lambda x: (x["level"], x["name"]))
    
    return available_spells


def get_spell_levels_for_character(character_class: CharacterClass, character_level: int) -> List[int]:
    """
    Get the spell levels that a character can cast.
    
    Args:
        character_class: The character's class
        character_level: The character's level (1-20)
    
    Returns:
        List of spell levels (0-9) that the character can cast
    """
    caster_type = CLASS_CASTER_TYPE.get(character_class)
    if not caster_type:
        return []
    
    progression = SPELL_SLOT_PROGRESSION[caster_type]
    if character_level not in progression:
        return []
    
    slots = progression[character_level]
    spell_levels = [0]  # Cantrips are always available for casters
    
    # Add spell levels for which the character has slots
    for i, slot_count in enumerate(slots):
        if slot_count > 0:
            spell_levels.append(i + 1)  # i+1 because index 0 is 1st level
    
    return spell_levels