"""Tests for character creation ability score handling."""

import pytest
from app.agents.scribe_agent import ScribeAgent


@pytest.fixture
def scribe():
    return ScribeAgent()


@pytest.mark.asyncio
async def test_create_character_uses_provided_abilities(scribe):
    """Abilities from the nested 'abilities' dict should be used, not defaults."""
    character_data = {
        "name": "TestHero",
        "class": "fighter",
        "race": "human",
        "level": 1,
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 14,
            "intelligence": 10,
            "wisdom": 12,
            "charisma": 8,
        },
    }
    result = await scribe.create_character(character_data)

    # Human gets +1 to all abilities
    assert result["abilities"]["strength"] == 17
    assert result["abilities"]["dexterity"] == 15
    assert result["abilities"]["constitution"] == 15
    assert result["abilities"]["intelligence"] == 11
    assert result["abilities"]["wisdom"] == 13
    assert result["abilities"]["charisma"] == 9


@pytest.mark.asyncio
async def test_create_character_defaults_when_no_abilities(scribe):
    """When no abilities dict provided, default to 10 for each."""
    character_data = {
        "name": "DefaultHero",
        "class": "wizard",
        "race": "elf",
        "level": 1,
    }
    result = await scribe.create_character(character_data)

    # Elf gets +2 DEX
    assert result["abilities"]["dexterity"] == 12
    # Others default to 10 + racial bonuses
    assert result["abilities"]["strength"] == 10
