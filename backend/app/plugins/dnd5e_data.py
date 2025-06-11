"""
D&D 5e rules data and constants for the rules engine.
This module contains basic D&D 5e SRD data that can be used by the rules engine.
"""

# D&D 5e Ability Scores
ABILITIES = {
    "strength": {"abbr": "STR", "description": "Natural athleticism, bodily power"},
    "dexterity": {"abbr": "DEX", "description": "Physical agility, reflexes, balance, poise"},
    "constitution": {"abbr": "CON", "description": "Health, stamina, vital force"},
    "intelligence": {"abbr": "INT", "description": "Reasoning ability, memory"},
    "wisdom": {"abbr": "WIS", "description": "Awareness, intuition, insight"},
    "charisma": {"abbr": "CHA", "description": "Force of personality, leadership, confidence"}
}

# D&D 5e Skills and their associated abilities
SKILLS = {
    "acrobatics": {"ability": "dexterity", "description": "Stay on your feet in a tricky situation"},
    "animal_handling": {"ability": "wisdom", "description": "Calm down a domesticated animal"},
    "arcana": {"ability": "intelligence", "description": "Recall lore about spells, magic items, eldritch symbols"},
    "athletics": {"ability": "strength", "description": "Climb, jump, or swim in difficult circumstances"},
    "deception": {"ability": "charisma", "description": "Hide the truth, either verbally or through actions"},
    "history": {"ability": "intelligence", "description": "Recall lore about historical events"},
    "insight": {"ability": "wisdom", "description": "Determine the true intentions of a creature"},
    "intimidation": {"ability": "charisma", "description": "Influence someone through overt threats"},
    "investigation": {"ability": "intelligence", "description": "Look around for clues and make deductions"},
    "medicine": {"ability": "wisdom", "description": "Stabilize a dying companion or diagnose an illness"},
    "nature": {"ability": "intelligence", "description": "Recall lore about terrain, plants and animals"},
    "perception": {"ability": "wisdom", "description": "Spot, hear, or otherwise detect the presence of something"},
    "performance": {"ability": "charisma", "description": "Delight an audience with music, dance, acting, storytelling"},
    "persuasion": {"ability": "charisma", "description": "Influence someone or a group of people with tact"},
    "religion": {"ability": "intelligence", "description": "Recall lore about deities, rites, prayers, religious hierarchies"},
    "sleight_of_hand": {"ability": "dexterity", "description": "Plant something, conceal an object, or perform legerdemain"},
    "stealth": {"ability": "dexterity", "description": "Conceal yourself from enemies, slink past guards"},
    "survival": {"ability": "wisdom", "description": "Track creatures, hunt wild game, guide your group"}
}

# D&D 5e Conditions
CONDITIONS = {
    "blinded": {
        "description": "A blinded creature can't see and automatically fails any ability check that requires sight.",
        "effects": ["Attack rolls against the creature have advantage", "The creature's attack rolls have disadvantage"]
    },
    "charmed": {
        "description": "A charmed creature can't attack the charmer or target the charmer with harmful abilities or magical effects.",
        "effects": ["The charmer has advantage on any ability check to interact socially with the creature"]
    },
    "deafened": {
        "description": "A deafened creature can't hear and automatically fails any ability check that requires hearing.",
        "effects": []
    },
    "frightened": {
        "description": "A frightened creature has disadvantage on ability checks and attack rolls while the source of its fear is within line of sight.",
        "effects": ["The creature can't willingly move closer to the source of its fear"]
    },
    "grappled": {
        "description": "A grappled creature's speed becomes 0, and it can't benefit from any bonus to its speed.",
        "effects": ["The condition ends if the grappler is incapacitated", "The condition also ends if an effect removes the grappled creature from the reach of the grappler"]
    },
    "incapacitated": {
        "description": "An incapacitated creature can't take actions or reactions.",
        "effects": []
    },
    "invisible": {
        "description": "An invisible creature is impossible to see without the aid of magic or a special sense.",
        "effects": ["Attack rolls against the creature have disadvantage", "The creature's attack rolls have advantage"]
    },
    "paralyzed": {
        "description": "A paralyzed creature is incapacitated and can't move or speak.",
        "effects": ["The creature automatically fails Strength and Dexterity saving throws", "Attack rolls against the creature have advantage", "Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature"]
    },
    "petrified": {
        "description": "A petrified creature is transformed, along with any nonmagical object it is wearing or carrying, into a solid inanimate substance (usually stone).",
        "effects": ["Its weight increases by a factor of ten, and it ceases aging", "The creature is incapacitated, can't move or speak, and is unaware of its surroundings", "Attack rolls against the creature have advantage", "The creature automatically fails Strength and Dexterity saving throws", "The creature has resistance to all damage", "The creature is immune to poison and disease"]
    },
    "poisoned": {
        "description": "A poisoned creature has disadvantage on attack rolls and ability checks.",
        "effects": []
    },
    "prone": {
        "description": "A prone creature's only movement option is to crawl, unless it stands up and thereby ends the condition.",
        "effects": ["The creature has disadvantage on attack rolls", "An attack roll against the creature has advantage if the attacker is within 5 feet of the creature", "Otherwise, the attack roll has disadvantage"]
    },
    "restrained": {
        "description": "A restrained creature's speed becomes 0, and it can't benefit from any bonus to its speed.",
        "effects": ["Attack rolls against the creature have advantage, and the creature's attack rolls have disadvantage", "The creature has disadvantage on Dexterity saving throws"]
    },
    "stunned": {
        "description": "A stunned creature is incapacitated, can't move, and can speak only falteringly.",
        "effects": ["The creature automatically fails Strength and Dexterity saving throws", "Attack rolls against the creature have advantage"]
    },
    "unconscious": {
        "description": "An unconscious creature is incapacitated, can't move or speak, and is unaware of its surroundings.",
        "effects": ["The creature drops whatever it's holding and falls prone", "The creature automatically fails Strength and Dexterity saving throws", "Attack rolls against the creature have advantage", "Any attack that hits the creature is a critical hit if the attacker is within 5 feet of the creature"]
    }
}

# Common D&D 5e Difficulty Classes
DIFFICULTY_CLASSES = {
    "very_easy": 5,
    "easy": 10,
    "medium": 15,
    "hard": 20,
    "very_hard": 25,
    "nearly_impossible": 30
}

# D&D 5e Damage Types
DAMAGE_TYPES = [
    "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic", 
    "piercing", "poison", "psychic", "radiant", "slashing", "thunder"
]

# Basic spell schools
SPELL_SCHOOLS = [
    "abjuration", "conjuration", "divination", "enchantment", 
    "evocation", "illusion", "necromancy", "transmutation"
]

# Common spell components
SPELL_COMPONENTS = {
    "V": "Verbal",
    "S": "Somatic", 
    "M": "Material"
}

# Basic spell list (SRD spells only)
SRD_SPELLS = {
    "acid_splash": {
        "level": 0,
        "school": "conjuration",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You hurl a bubble of acid. Choose one creature within range, or choose two creatures within range that are within 5 feet of each other. A target must succeed on a Dexterity saving throw or take 1d6 acid damage."
    },
    "cure_wounds": {
        "level": 1,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier."
    },
    "fireball": {
        "level": 3,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "components": "V, S, M (a tiny ball of bat guano and sulfur)",
        "duration": "Instantaneous",
        "description": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one."
    },
    "magic_missile": {
        "level": 1,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "120 feet",
        "components": "V, S",
        "duration": "Instantaneous",
        "description": "You create three glowing darts of magical force. Each dart hits a creature of your choice that you can see within range. A dart deals 1d4 + 1 force damage to its target."
    }
}