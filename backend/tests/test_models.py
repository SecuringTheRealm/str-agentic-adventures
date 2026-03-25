"""
Tests for Pydantic models validation — boundary and error cases only.

Framework behaviour (model creation, defaults, field access) is tested
implicitly by the route/integration tests. Only validation boundaries
and required-field errors are tested here.
"""

import os
import sys

import pytest

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.game_models import (
    Abilities,
    CharacterClass,
    CharacterSheet,
    HitPoints,
    PlayerInput,
    Race,
    Spell,
)
from pydantic import ValidationError


class TestValidationBoundaries:
    """Validation boundary and required-field error tests."""

    def test_hit_points_requires_maximum(self) -> None:
        """HitPoints requires both current and maximum fields."""
        with pytest.raises(ValidationError):
            HitPoints(current=10)  # maximum is required

    def test_character_sheet_requires_fields(self) -> None:
        """CharacterSheet raises ValidationError when required fields are missing."""
        with pytest.raises(ValidationError):
            CharacterSheet()  # type: ignore[call-arg]

    def test_player_input_rejects_non_string_message(self) -> None:
        """PlayerInput rejects a non-string message value."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerInput(
                message=123,  # must be a string
                character_id="char_123",
                campaign_id="camp_456",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("message",) for e in errors)

    def test_abilities_min_boundary(self) -> None:
        """Abilities accepts the minimum realistic score of 1."""
        abilities = Abilities(
            strength=1, dexterity=1, constitution=1,
            intelligence=1, wisdom=1, charisma=1,
        )
        assert abilities.strength == 1

    def test_abilities_max_boundary(self) -> None:
        """Abilities accepts the maximum realistic score of 30."""
        abilities = Abilities(
            strength=30, dexterity=30, constitution=30,
            intelligence=30, wisdom=30, charisma=30,
        )
        assert abilities.strength == 30

    def test_hit_points_zero_current(self) -> None:
        """HitPoints accepts zero current HP (unconscious/dead)."""
        hp = HitPoints(current=0, maximum=30)
        assert hp.current == 0

    def test_spell_cantrip_level(self) -> None:
        """Spell accepts level 0 (cantrip)."""
        spell = Spell(
            name="Prestidigitation", level=0, school="Transmutation",
            casting_time="1 action", range="10 feet", components="V, S",
            duration="Up to 1 hour", description="Simple magical effect",
        )
        assert spell.level == 0

    def test_spell_max_level(self) -> None:
        """Spell accepts level 9 (highest spell slot)."""
        spell = Spell(
            name="Wish", level=9, school="Conjuration",
            casting_time="1 action", range="Self", components="V",
            duration="Instantaneous", description="The most powerful spell",
        )
        assert spell.level == 9

    def test_character_sheet_required_fields_accepted(self) -> None:
        """CharacterSheet is created successfully with all required fields present."""
        character = CharacterSheet(
            name="Test Hero",
            race=Race.HUMAN,
            character_class=CharacterClass.FIGHTER,
            abilities=Abilities(),
            hit_points=HitPoints(current=10, maximum=10),
        )
        assert character.name == "Test Hero"
