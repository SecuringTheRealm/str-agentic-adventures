"""Tests for character progression: level up, ASIs, proficiency scaling, HP gains."""

import pytest
from app.rules_engine import (
    apply_level_up,
    check_level_up,
    get_proficiency_bonus,
    is_asi_level,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_character(
    *,
    level: int = 1,
    experience: int = 0,
    char_class: str = "fighter",
    strength: int = 16,
    dexterity: int = 14,
    constitution: int = 14,
    intelligence: int = 10,
    wisdom: int = 12,
    charisma: int = 8,
    hp_max: int = 12,
    hp_current: int | None = None,
) -> dict:
    """Build a minimal character dict for testing."""
    return {
        "id": "test-char",
        "name": "Test Character",
        "race": "human",
        "character_class": char_class,
        "level": level,
        "experience": experience,
        "abilities": {
            "strength": strength,
            "dexterity": dexterity,
            "constitution": constitution,
            "intelligence": intelligence,
            "wisdom": wisdom,
            "charisma": charisma,
        },
        "hit_points": {
            "current": hp_current if hp_current is not None else hp_max,
            "maximum": hp_max,
        },
        "proficiency_bonus": get_proficiency_bonus(level),
        "features": [],
        "ability_score_improvements_used": 0,
    }


# ---------------------------------------------------------------------------
# XP threshold triggers level up correctly
# ---------------------------------------------------------------------------


class TestXPThresholdTriggers:
    """XP threshold correctly determines whether a character can level up."""

    def test_exact_threshold_allows_level_up(self) -> None:
        assert check_level_up(300, 1) is True

    def test_above_threshold_allows_level_up(self) -> None:
        assert check_level_up(1000, 1) is True

    def test_below_threshold_blocks_level_up(self) -> None:
        assert check_level_up(299, 1) is False

    def test_zero_xp_blocks_level_up(self) -> None:
        assert check_level_up(0, 1) is False

    @pytest.mark.parametrize(
        "level,xp",
        [
            (1, 300),
            (4, 6500),
            (9, 64000),
            (14, 165000),
            (19, 355000),
        ],
    )
    def test_each_tier_boundary(self, level: int, xp: int) -> None:
        assert check_level_up(xp, level) is True
        assert check_level_up(xp - 1, level) is False


# ---------------------------------------------------------------------------
# Proficiency bonus scales correctly
# ---------------------------------------------------------------------------


class TestProficiencyBonusScaling:
    """Proficiency bonus scales every 4 levels from +2 to +6."""

    @pytest.mark.parametrize(
        "levels,expected",
        [
            ([1, 2, 3, 4], 2),
            ([5, 6, 7, 8], 3),
            ([9, 10, 11, 12], 4),
            ([13, 14, 15, 16], 5),
            ([17, 18, 19, 20], 6),
        ],
    )
    def test_proficiency_by_tier(self, levels: list[int], expected: int) -> None:
        for level in levels:
            assert get_proficiency_bonus(level) == expected, (
                f"Level {level} should have proficiency bonus {expected}"
            )


# ---------------------------------------------------------------------------
# ASI at correct levels
# ---------------------------------------------------------------------------


class TestASILevels:
    """ASI is granted at levels 4, 8, 12, 16, 19."""

    @pytest.mark.parametrize("level", [4, 8, 12, 16, 19])
    def test_asi_level(self, level: int) -> None:
        assert is_asi_level(level) is True

    @pytest.mark.parametrize(
        "level",
        [1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 20],
    )
    def test_non_asi_level(self, level: int) -> None:
        assert is_asi_level(level) is False


class TestASIApplication:
    """ASI allows +2 to one ability or +1 to two abilities."""

    def test_plus_2_to_one_ability(self) -> None:
        char = _make_character(
            level=3,
            experience=2700,  # enough for level 4
            strength=16,
        )
        result = apply_level_up(char, choices={"asi": {"strength": 2}})
        assert result["success"] is True
        assert result["new_level"] == 4
        assert result["ability_improvements"] == {"strength": 2}
        assert result["updated_character"]["abilities"]["strength"] == 18

    def test_plus_1_to_two_abilities(self) -> None:
        char = _make_character(
            level=3,
            experience=2700,
            dexterity=14,
            wisdom=12,
        )
        result = apply_level_up(char, choices={"asi": {"dexterity": 1, "wisdom": 1}})
        assert result["success"] is True
        assert result["ability_improvements"] == {"dexterity": 1, "wisdom": 1}
        assert result["updated_character"]["abilities"]["dexterity"] == 15
        assert result["updated_character"]["abilities"]["wisdom"] == 13

    def test_asi_rejected_when_not_asi_level(self) -> None:
        """ASI choices at a non-ASI level are silently ignored (no error)."""
        char = _make_character(level=1, experience=300)
        result = apply_level_up(char, choices={"asi": {"strength": 2}})
        # Level 2 is not an ASI level, so no ability improvements applied
        assert result["ability_improvements"] == {}
        assert result["updated_character"]["abilities"]["strength"] == 16

    def test_asi_total_must_be_2(self) -> None:
        char = _make_character(level=3, experience=2700)
        with pytest.raises(ValueError, match="must total exactly 2"):
            apply_level_up(char, choices={"asi": {"strength": 1}})

    def test_asi_invalid_ability_name(self) -> None:
        char = _make_character(level=3, experience=2700)
        with pytest.raises(ValueError, match="Invalid ability name"):
            apply_level_up(char, choices={"asi": {"luck": 2}})

    def test_asi_cannot_exceed_20(self) -> None:
        char = _make_character(level=3, experience=2700, strength=20)
        with pytest.raises(ValueError, match="Cannot increase strength above 20"):
            apply_level_up(char, choices={"asi": {"strength": 2}})

    def test_asi_cannot_push_above_20(self) -> None:
        char = _make_character(level=3, experience=2700, strength=19)
        with pytest.raises(ValueError, match="Cannot increase strength above 20"):
            apply_level_up(char, choices={"asi": {"strength": 2}})

    def test_asi_at_exactly_cap_with_plus_1(self) -> None:
        """A +1 to a score of 19 is fine (goes to 20)."""
        char = _make_character(level=3, experience=2700, strength=19, dexterity=14)
        result = apply_level_up(char, choices={"asi": {"strength": 1, "dexterity": 1}})
        assert result["updated_character"]["abilities"]["strength"] == 20

    def test_asi_tracks_improvements_used(self) -> None:
        char = _make_character(level=3, experience=2700)
        result = apply_level_up(char, choices={"asi": {"strength": 2}})
        assert result["updated_character"]["ability_score_improvements_used"] == 1


# ---------------------------------------------------------------------------
# HP increases on level up
# ---------------------------------------------------------------------------


class TestHPIncrease:
    """HP increases by hit die average + CON modifier on level up."""

    def test_fighter_hp_gain(self) -> None:
        """Fighter (d10) with CON 14 (+2): average = 6 + 2 = 8."""
        char = _make_character(
            level=1,
            experience=300,
            char_class="fighter",
            constitution=14,
            hp_max=12,
        )
        result = apply_level_up(char)
        assert result["hp_gained"] == 8
        assert result["updated_character"]["hit_points"]["maximum"] == 20
        assert result["updated_character"]["hit_points"]["current"] == 20

    def test_wizard_hp_gain(self) -> None:
        """Wizard (d6) with CON 10 (+0): average = 4 + 0 = 4."""
        char = _make_character(
            level=1,
            experience=300,
            char_class="wizard",
            constitution=10,
            hp_max=6,
        )
        result = apply_level_up(char)
        assert result["hp_gained"] == 4
        assert result["updated_character"]["hit_points"]["maximum"] == 10

    def test_barbarian_hp_gain(self) -> None:
        """Barbarian (d12) with CON 16 (+3): average = 7 + 3 = 10."""
        char = _make_character(
            level=1,
            experience=300,
            char_class="barbarian",
            constitution=16,
            hp_max=15,
        )
        result = apply_level_up(char)
        assert result["hp_gained"] == 10
        assert result["updated_character"]["hit_points"]["maximum"] == 25

    def test_hp_gain_with_negative_con(self) -> None:
        """Rogue (d8) with CON 8 (-1): average = 5 - 1 = 4."""
        char = _make_character(
            level=1,
            experience=300,
            char_class="rogue",
            constitution=8,
            hp_max=7,
        )
        result = apply_level_up(char)
        assert result["hp_gained"] == 4

    def test_hp_gain_adds_to_both_current_and_max(self) -> None:
        """HP gained is added to both current and maximum HP."""
        char = _make_character(
            level=1,
            experience=300,
            char_class="fighter",
            constitution=14,
            hp_max=12,
            hp_current=8,  # wounded
        )
        result = apply_level_up(char)
        hp = result["updated_character"]["hit_points"]
        assert hp["maximum"] == 20  # 12 + 8
        assert hp["current"] == 16  # 8 + 8


# ---------------------------------------------------------------------------
# Cannot level up past 20
# ---------------------------------------------------------------------------


class TestMaxLevelCap:
    """Character cannot exceed level 20."""

    def test_cannot_level_past_20(self) -> None:
        char = _make_character(level=20, experience=999999)
        with pytest.raises(ValueError, match="maximum level"):
            apply_level_up(char)

    def test_level_19_to_20_works(self) -> None:
        char = _make_character(level=19, experience=355000)
        result = apply_level_up(char)
        assert result["new_level"] == 20


# ---------------------------------------------------------------------------
# Cannot level up without enough XP
# ---------------------------------------------------------------------------


class TestInsufficientXP:
    """Level up is rejected when XP is below the threshold."""

    def test_no_level_up_without_xp(self) -> None:
        char = _make_character(level=1, experience=0)
        with pytest.raises(ValueError, match="Not enough XP"):
            apply_level_up(char)

    def test_just_below_threshold(self) -> None:
        char = _make_character(level=1, experience=299)
        with pytest.raises(ValueError, match="Not enough XP"):
            apply_level_up(char)


# ---------------------------------------------------------------------------
# Proficiency bonus updates on level up
# ---------------------------------------------------------------------------


class TestProficiencyOnLevelUp:
    """Proficiency bonus is updated when levelling up across a tier boundary."""

    def test_proficiency_stays_2_at_level_2(self) -> None:
        char = _make_character(level=1, experience=300)
        result = apply_level_up(char)
        assert result["new_proficiency_bonus"] == 2

    def test_proficiency_increases_at_level_5(self) -> None:
        char = _make_character(level=4, experience=6500)
        result = apply_level_up(char)
        assert result["new_proficiency_bonus"] == 3
        assert result["updated_character"]["proficiency_bonus"] == 3

    def test_proficiency_increases_at_level_9(self) -> None:
        char = _make_character(level=8, experience=48000)
        result = apply_level_up(char)
        assert result["new_proficiency_bonus"] == 4

    def test_proficiency_increases_at_level_13(self) -> None:
        char = _make_character(level=12, experience=120000)
        result = apply_level_up(char)
        assert result["new_proficiency_bonus"] == 5

    def test_proficiency_increases_at_level_17(self) -> None:
        char = _make_character(level=16, experience=225000)
        result = apply_level_up(char)
        assert result["new_proficiency_bonus"] == 6


# ---------------------------------------------------------------------------
# Class features are tracked on level up
# ---------------------------------------------------------------------------


class TestClassFeatures:
    """Class features gained at the new level are recorded."""

    def test_features_returned_in_result(self) -> None:
        char = _make_character(level=1, experience=300, char_class="fighter")
        result = apply_level_up(char)
        # Features depend on class_features.json data; at minimum the key exists
        assert "features_gained" in result
        assert isinstance(result["features_gained"], list)

    def test_features_appended_to_character(self) -> None:
        char = _make_character(level=1, experience=300, char_class="fighter")
        char["features"] = [
            {"name": "Second Wind", "source": "class", "level_gained": 1},
        ]
        result = apply_level_up(char)
        updated_features = result["updated_character"]["features"]
        # Original feature preserved
        assert any(f["name"] == "Second Wind" for f in updated_features)
        # New features (if any) have level_gained == 2
        new_feats = [f for f in updated_features if f.get("level_gained") == 2]
        assert len(new_feats) == len(result["features_gained"])


# ---------------------------------------------------------------------------
# Full integration: level up from 3 to 4 (ASI level) as a fighter
# ---------------------------------------------------------------------------


class TestFullLevelUpIntegration:
    """End-to-end level up covering all mechanics together."""

    def test_fighter_level_3_to_4_with_asi(self) -> None:
        char = _make_character(
            level=3,
            experience=2700,
            char_class="fighter",
            strength=16,
            constitution=14,
            hp_max=31,  # reasonable for a L3 fighter with +2 CON
        )
        result = apply_level_up(char, choices={"asi": {"strength": 2}})

        assert result["success"] is True
        assert result["new_level"] == 4
        assert result["hp_gained"] == 8  # d10 avg(6) + CON mod(2)
        assert result["new_proficiency_bonus"] == 2  # still tier 1
        assert result["ability_improvements"] == {"strength": 2}

        updated = result["updated_character"]
        assert updated["level"] == 4
        assert updated["abilities"]["strength"] == 18
        assert updated["hit_points"]["maximum"] == 39  # 31 + 8
        assert updated["ability_score_improvements_used"] == 1

    def test_wizard_level_4_to_5_proficiency_bump(self) -> None:
        char = _make_character(
            level=4,
            experience=6500,
            char_class="wizard",
            constitution=12,
            hp_max=22,
        )
        result = apply_level_up(char)

        assert result["new_level"] == 5
        assert result["new_proficiency_bonus"] == 3
        assert result["hp_gained"] == 5  # d6 avg(4) + CON mod(1)
        assert result["updated_character"]["hit_points"]["maximum"] == 27

    def test_level_up_without_asi_choices_at_asi_level(self) -> None:
        """Levelling up at an ASI level without providing choices is valid."""
        char = _make_character(level=3, experience=2700, char_class="rogue")
        result = apply_level_up(char, choices=None)
        assert result["success"] is True
        assert result["new_level"] == 4
        assert result["ability_improvements"] == {}
