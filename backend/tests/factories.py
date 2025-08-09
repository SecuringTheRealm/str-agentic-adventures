"""
Factory classes for generating test data using pytest-factoryboy.

This module provides factory classes for creating common test data patterns,
reducing code duplication and making tests more maintainable.

Note: This module requires factory_boy to be installed. If factory_boy is not
available, importing this module will raise an ImportError.
"""

try:
    import factory
    from factory import fuzzy
    import uuid
except ImportError as e:
    raise ImportError(
        "factory_boy is required for test factories. "
        "Install it with: pip install factory_boy pytest-factoryboy"
    ) from e


class AbilitiesFactory(factory.DictFactory):
    """Factory for creating D&D 5e ability scores."""

    strength = fuzzy.FuzzyInteger(8, 18)
    dexterity = fuzzy.FuzzyInteger(8, 18)
    constitution = fuzzy.FuzzyInteger(8, 18)
    intelligence = fuzzy.FuzzyInteger(8, 18)
    wisdom = fuzzy.FuzzyInteger(8, 18)
    charisma = fuzzy.FuzzyInteger(8, 18)


class StandardAbilitiesFactory(AbilitiesFactory):
    """Factory for creating standard D&D 5e ability scores (10-15 range)."""

    strength = 16
    dexterity = 14
    constitution = 15
    intelligence = 12
    wisdom = 13
    charisma = 10


class HitPointsFactory(factory.DictFactory):
    """Factory for creating hit point data."""

    current = 10
    maximum = 10


class CharacterFactory(factory.DictFactory):
    """Factory for creating D&D 5e character data."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Faker("first_name")
    race = fuzzy.FuzzyChoice(["human", "elf", "dwarf", "halfling"])
    character_class = fuzzy.FuzzyChoice(["fighter", "wizard", "rogue", "cleric"])
    level = 1
    abilities = factory.SubFactory(StandardAbilitiesFactory)
    hit_points = factory.SubFactory(HitPointsFactory)
    armor_class = 15
    inventory = []
    features = []
    spells = []


class FighterCharacterFactory(CharacterFactory):
    """Factory for creating fighter characters with appropriate stats."""

    character_class = "fighter"
    abilities = factory.SubFactory(StandardAbilitiesFactory)
    armor_class = 16


class WizardCharacterFactory(CharacterFactory):
    """Factory for creating wizard characters with appropriate stats."""

    character_class = "wizard"
    abilities = factory.SubFactory(
        StandardAbilitiesFactory, intelligence=16, constitution=13, dexterity=14
    )
    armor_class = 12


class CampaignFactory(factory.DictFactory):
    """Factory for creating campaign data."""

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Faker("catch_phrase")
    setting = fuzzy.FuzzyChoice(["Fantasy", "Modern", "Sci-Fi"])
    tone = fuzzy.FuzzyChoice(["heroic", "dark", "comedic", "serious"])
    homebrew_rules = []
    characters = []
    session_log = []
    state = "created"


class CombatEncounterFactory(factory.DictFactory):
    """Factory for creating combat encounter data."""

    id = factory.LazyFunction(lambda: f"encounter_{uuid.uuid4().hex[:8]}")
    status = "active"
    enemies = factory.LazyFunction(lambda: [{"id": "enemy1", "type": "goblin"}])
    round = 1
    turn_order = []


class AttackActionFactory(factory.DictFactory):
    """Factory for creating attack action data."""

    type = "attack"
    actor_id = "player1"
    target_id = "enemy1"
    weapon = "longsword"
    attack_bonus = 5
    damage = "1d8+3"


class SpellAttackActionFactory(factory.DictFactory):
    """Factory for creating spell attack action data."""

    type = "spell_attack"
    actor_id = "wizard1"
    target_id = "enemy1"
    spell_name = "fire_bolt"
    attack_bonus = 6
    damage = "1d10"
    damage_type = "fire"


class SpellDamageActionFactory(factory.DictFactory):
    """Factory for creating spell damage action data."""

    type = "spell_damage"
    actor_id = "wizard1"
    spell_name = "fireball"
    damage = "8d6"
    damage_type = "fire"
    save_type = "dexterity"
    save_dc = 15


class SkillCheckActionFactory(factory.DictFactory):
    """Factory for creating skill check action data."""

    type = "skill_check"
    actor_id = "player1"
    skill = "perception"
    ability_score = 13
    proficient = True
    proficiency_bonus = 2
    difficulty_class = 15


class SavingThrowActionFactory(factory.DictFactory):
    """Factory for creating saving throw action data."""

    type = "saving_throw"
    actor_id = "player1"
    save_type = "dexterity"
    ability_score = 14
    proficient = False
    proficiency_bonus = 2
    difficulty_class = 15


# Common test data combinations
def create_standard_fighter():
    """Create a standard fighter character for testing."""
    return FighterCharacterFactory()


def create_standard_wizard():
    """Create a standard wizard character for testing."""
    return WizardCharacterFactory()


def create_basic_encounter():
    """Create a basic combat encounter for testing."""
    return CombatEncounterFactory()


def create_melee_attack():
    """Create a standard melee attack action for testing."""
    return AttackActionFactory()


def create_spell_attack():
    """Create a standard spell attack action for testing."""
    return SpellAttackActionFactory()
