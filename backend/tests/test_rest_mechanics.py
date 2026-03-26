"""Tests for short and long rest mechanics."""

from unittest.mock import patch

from app.api.routes.rest_routes import calculate_long_rest, calculate_short_rest
from app.models.game_models import (
    Abilities,
    CharacterClass,
    CharacterSheet,
    HitPoints,
    Race,
    SpellCasting,
    SpellSlot,
)


def _make_character(
    *,
    character_class: CharacterClass = CharacterClass.FIGHTER,
    level: int = 5,
    current_hp: int = 20,
    max_hp: int = 40,
    constitution: int = 14,
    hit_dice_remaining: int | None = None,
    exhaustion_level: int = 0,
    spellcasting: SpellCasting | None = None,
) -> CharacterSheet:
    """Create a test character with sensible defaults."""
    return CharacterSheet(
        name="Test Hero",
        race=Race.HUMAN,
        character_class=character_class,
        level=level,
        abilities=Abilities(constitution=constitution),
        hit_points=HitPoints(current=current_hp, maximum=max_hp),
        hit_dice_remaining=hit_dice_remaining,
        exhaustion_level=exhaustion_level,
        spellcasting=spellcasting,
    )


# --- Short rest tests ---


def test_short_rest_spend_hit_dice_recovers_hp():
    """Spending hit dice on a short rest recovers HP."""
    char = _make_character(current_hp=20, max_hp=40, hit_dice_remaining=5)
    # Patch random to return a known value: Fighter d10, CON mod +2 => 5+2=7 per die
    with patch("app.api.routes.rest_routes.random.randint", return_value=5):
        result = calculate_short_rest(char, hit_dice_to_spend=2)
    assert result["hp_recovered"] == 14  # 2 dice * (5+2)
    assert result["hit_dice_remaining"] == 3
    assert char.hit_points.current == 34


def test_short_rest_hp_cannot_exceed_maximum():
    """HP recovery is capped at the character's maximum HP."""
    char = _make_character(current_hp=38, max_hp=40, hit_dice_remaining=5)
    with patch("app.api.routes.rest_routes.random.randint", return_value=10):
        result = calculate_short_rest(char, hit_dice_to_spend=2)
    assert char.hit_points.current == 40
    assert result["hp_recovered"] == 2  # Only 2 HP were needed to reach max


def test_short_rest_cannot_spend_more_dice_than_available():
    """Requesting more dice than available spends only what's available."""
    char = _make_character(current_hp=10, max_hp=40, hit_dice_remaining=2)
    with patch("app.api.routes.rest_routes.random.randint", return_value=5):
        result = calculate_short_rest(char, hit_dice_to_spend=5)
    # Should only spend 2 dice (all that's available)
    assert result["hit_dice_remaining"] == 0
    assert result["hp_recovered"] == 14  # 2 * (5+2)


def test_short_rest_zero_dice_available():
    """No recovery when zero hit dice are available."""
    char = _make_character(current_hp=20, max_hp=40, hit_dice_remaining=0)
    result = calculate_short_rest(char, hit_dice_to_spend=3)
    assert result["hp_recovered"] == 0
    assert result["hit_dice_remaining"] == 0
    assert char.hit_points.current == 20


def test_short_rest_warlock_recovers_spell_slots():
    """Warlocks recover all spell slots on a short rest."""
    spellcasting = SpellCasting(
        spellcasting_ability="charisma",
        spell_slots=[
            SpellSlot(level=1, total=2, used=2),
            SpellSlot(level=2, total=1, used=1),
        ],
    )
    char = _make_character(
        character_class=CharacterClass.WARLOCK,
        current_hp=30,
        max_hp=30,
        hit_dice_remaining=5,
        spellcasting=spellcasting,
    )
    result = calculate_short_rest(char, hit_dice_to_spend=0)
    assert sorted(result["spell_slots_recovered"]) == [1, 2]
    # Slots should now be fully recovered
    for slot in char.spellcasting.spell_slots:
        assert slot.used == 0


# --- Long rest tests ---


def test_long_rest_recovers_all_hp():
    """Long rest restores HP to maximum."""
    char = _make_character(current_hp=10, max_hp=40)
    result = calculate_long_rest(char)
    assert result["hp_recovered"] == 30
    assert char.hit_points.current == 40


def test_long_rest_recovers_all_spell_slots():
    """Long rest recovers all spent spell slots."""
    spellcasting = SpellCasting(
        spellcasting_ability="intelligence",
        spell_slots=[
            SpellSlot(level=1, total=4, used=3),
            SpellSlot(level=2, total=3, used=3),
            SpellSlot(level=3, total=2, used=1),
        ],
    )
    char = _make_character(
        character_class=CharacterClass.WIZARD, spellcasting=spellcasting
    )
    result = calculate_long_rest(char)
    assert sorted(result["spell_slots_recovered"]) == [1, 2, 3]
    for slot in char.spellcasting.spell_slots:
        assert slot.used == 0


def test_long_rest_recovers_half_hit_dice():
    """Long rest recovers half of total hit dice (minimum 1)."""
    # Level 5, 0 remaining => recover floor(5/2) = 2 dice
    char = _make_character(level=5, hit_dice_remaining=0)
    result = calculate_long_rest(char)
    assert result["hit_dice_remaining"] == 2


def test_long_rest_hit_dice_cap_at_level():
    """Hit dice recovery cannot exceed the character's level."""
    # Level 5, already has 4 => recover 2 but cap at 5
    char = _make_character(level=5, hit_dice_remaining=4)
    result = calculate_long_rest(char)
    assert result["hit_dice_remaining"] == 5


def test_long_rest_recovers_half_hit_dice_minimum_one():
    """At level 1, long rest recovers at least 1 hit die."""
    char = _make_character(level=1, hit_dice_remaining=0)
    result = calculate_long_rest(char)
    assert result["hit_dice_remaining"] == 1


def test_long_rest_reduces_exhaustion_by_one():
    """Long rest reduces exhaustion level by 1."""
    char = _make_character(exhaustion_level=3)
    result = calculate_long_rest(char)
    assert result["exhaustion_level"] == 2
    assert char.exhaustion_level == 2


def test_long_rest_exhaustion_does_not_go_below_zero():
    """Exhaustion cannot be reduced below 0."""
    char = _make_character(exhaustion_level=0)
    result = calculate_long_rest(char)
    assert result["exhaustion_level"] == 0
    assert char.exhaustion_level == 0
