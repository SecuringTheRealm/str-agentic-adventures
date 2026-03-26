"""
Tests for SRD class features data (levels 1-20) and lookup functions.

Source: D&D 5e SRD (OGL content).
"""

import pytest
from app.srd_data import (
    get_all_features_up_to_level,
    get_class_features,
    get_features_at_level,
    load_class_features,
)

SRD_CLASSES = [
    "barbarian",
    "bard",
    "cleric",
    "druid",
    "fighter",
    "monk",
    "paladin",
    "ranger",
    "rogue",
    "sorcerer",
    "warlock",
    "wizard",
]


class TestClassFeaturesData:
    """Tests for the class_features.json data completeness."""

    def test_all_12_classes_present(self) -> None:
        data = load_class_features()
        for cls in SRD_CLASSES:
            assert cls in data, f"Class '{cls}' missing from class_features data"

    @pytest.mark.parametrize("char_class", SRD_CLASSES)
    def test_class_has_all_20_levels(self, char_class: str) -> None:
        data = load_class_features()
        features = data[char_class]["features"]
        for level in range(1, 21):
            assert str(level) in features, (
                f"Class '{char_class}' missing level {level} in features"
            )

    @pytest.mark.parametrize("char_class", SRD_CLASSES)
    def test_class_has_features_at_level_1(self, char_class: str) -> None:
        data = load_class_features()
        level_1_features = data[char_class]["features"]["1"]
        assert len(level_1_features) > 0, (
            f"Class '{char_class}' has no features at level 1"
        )

    @pytest.mark.parametrize("char_class", SRD_CLASSES)
    def test_each_feature_has_name_and_type(self, char_class: str) -> None:
        data = load_class_features()
        features_by_level = data[char_class]["features"]
        for level_str, feature_list in features_by_level.items():
            for feature in feature_list:
                assert "name" in feature, (
                    f"Class '{char_class}' level {level_str} feature missing 'name'"
                )
                assert "type" in feature, (
                    f"Class '{char_class}' level {level_str} feature "
                    f"'{feature.get('name')}' missing 'type'"
                )

    @pytest.mark.parametrize("char_class", SRD_CLASSES)
    def test_class_has_ability_score_improvement(self, char_class: str) -> None:
        """All SRD classes gain at least one ASI."""
        all_feature_names = get_all_features_up_to_level(char_class, 20)
        assert any("Ability Score Improvement" in name for name in all_feature_names), (
            f"Class '{char_class}' has no Ability Score Improvement across all levels"
        )

    def test_fighter_has_extra_attack_at_level_5(self) -> None:
        features = get_features_at_level("fighter", 5)
        assert "Extra Attack" in features

    def test_wizard_has_arcane_recovery_at_level_1(self) -> None:
        features = get_features_at_level("wizard", 1)
        assert "Arcane Recovery" in features

    def test_rogue_has_sneak_attack_at_level_1(self) -> None:
        features = get_features_at_level("rogue", 1)
        assert any("Sneak Attack" in f for f in features)

    def test_barbarian_has_rage_at_level_1(self) -> None:
        features = get_features_at_level("barbarian", 1)
        assert "Rage" in features

    def test_paladin_has_lay_on_hands_at_level_1(self) -> None:
        features = get_features_at_level("paladin", 1)
        assert "Lay on Hands" in features

    def test_monk_has_ki_at_level_2(self) -> None:
        features = get_features_at_level("monk", 2)
        assert "Ki" in features

    def test_warlock_has_pact_magic_at_level_1(self) -> None:
        features = get_features_at_level("warlock", 1)
        assert "Pact Magic" in features

    def test_cleric_has_channel_divinity_at_level_2(self) -> None:
        features = get_features_at_level("cleric", 2)
        assert any("Channel Divinity" in f for f in features)

    def test_bard_has_bardic_inspiration_at_level_1(self) -> None:
        features = get_features_at_level("bard", 1)
        assert any("Bardic Inspiration" in f for f in features)

    def test_ranger_has_favored_enemy_at_level_1(self) -> None:
        features = get_features_at_level("ranger", 1)
        assert "Favored Enemy" in features

    def test_druid_has_wild_shape_at_level_2(self) -> None:
        features = get_features_at_level("druid", 2)
        assert "Wild Shape" in features

    def test_sorcerer_has_metamagic_at_level_3(self) -> None:
        features = get_features_at_level("sorcerer", 3)
        assert any("Metamagic" in f for f in features)


class TestGetFeaturesAtLevel:
    """Tests for get_features_at_level() function."""

    def test_returns_list_of_strings(self) -> None:
        result = get_features_at_level("fighter", 1)
        assert isinstance(result, list)
        assert all(isinstance(f, str) for f in result)

    def test_fighter_level_1_features(self) -> None:
        features = get_features_at_level("fighter", 1)
        assert "Fighting Style" in features
        assert "Second Wind" in features

    def test_fighter_level_2_features(self) -> None:
        features = get_features_at_level("fighter", 2)
        assert "Action Surge" in features

    def test_fighter_level_3_features(self) -> None:
        features = get_features_at_level("fighter", 3)
        assert "Martial Archetype" in features

    def test_fighter_level_5_features(self) -> None:
        features = get_features_at_level("fighter", 5)
        assert "Extra Attack" in features

    def test_wizard_level_1_features(self) -> None:
        features = get_features_at_level("wizard", 1)
        assert "Spellcasting" in features
        assert "Arcane Recovery" in features

    def test_wizard_level_2_features(self) -> None:
        features = get_features_at_level("wizard", 2)
        assert "Arcane Tradition" in features

    def test_empty_level_returns_empty_list(self) -> None:
        # Wizard level 3 has no features in SRD
        result = get_features_at_level("wizard", 3)
        assert result == []

    def test_unknown_class_returns_empty_list(self) -> None:
        result = get_features_at_level("artificer", 1)
        assert result == []

    def test_case_insensitive_class_name(self) -> None:
        lower = get_features_at_level("fighter", 1)
        upper = get_features_at_level("FIGHTER", 1)
        assert lower == upper

    def test_level_20_features_exist(self) -> None:
        for cls in SRD_CLASSES:
            # Every class should have something meaningful at level 20
            features_1_to_20 = get_all_features_up_to_level(cls, 20)
            assert len(features_1_to_20) > 0, (
                f"Class '{cls}' has no features through level 20"
            )

    def test_rogue_level_1_has_three_features(self) -> None:
        features = get_features_at_level("rogue", 1)
        assert len(features) >= 3

    def test_paladin_level_2_has_spellcasting(self) -> None:
        features = get_features_at_level("paladin", 2)
        assert "Spellcasting" in features

    def test_barbarian_level_20_primal_champion(self) -> None:
        features = get_features_at_level("barbarian", 20)
        assert "Primal Champion" in features

    def test_wizard_level_20_signature_spells(self) -> None:
        features = get_features_at_level("wizard", 20)
        assert "Signature Spells" in features


class TestGetAllFeaturesUpToLevel:
    """Tests for get_all_features_up_to_level() function."""

    def test_returns_list_of_strings(self) -> None:
        result = get_all_features_up_to_level("fighter", 5)
        assert isinstance(result, list)
        assert all(isinstance(f, str) for f in result)

    def test_accumulates_features_correctly(self) -> None:
        features = get_all_features_up_to_level("fighter", 5)
        # Level 1: Fighting Style, Second Wind
        assert "Fighting Style" in features
        assert "Second Wind" in features
        # Level 2: Action Surge
        assert "Action Surge" in features
        # Level 3: Martial Archetype
        assert "Martial Archetype" in features
        # Level 5: Extra Attack
        assert "Extra Attack" in features

    def test_level_1_same_as_get_features_at_level(self) -> None:
        up_to_1 = get_all_features_up_to_level("wizard", 1)
        at_1 = get_features_at_level("wizard", 1)
        assert up_to_1 == at_1

    def test_features_grow_with_level(self) -> None:
        features_5 = get_all_features_up_to_level("fighter", 5)
        features_10 = get_all_features_up_to_level("fighter", 10)
        assert len(features_10) >= len(features_5)

    def test_unknown_class_returns_empty_list(self) -> None:
        result = get_all_features_up_to_level("artificer", 10)
        assert result == []

    def test_level_0_returns_empty_list(self) -> None:
        result = get_all_features_up_to_level("fighter", 0)
        assert result == []

    def test_all_classes_level_20_has_many_features(self) -> None:
        for cls in SRD_CLASSES:
            features = get_all_features_up_to_level(cls, 20)
            assert len(features) >= 5, (
                f"Class '{cls}' has fewer than 5 features through level 20"
            )

    def test_rogue_accumulates_sneak_attack_progressions(self) -> None:
        features = get_all_features_up_to_level("rogue", 20)
        sneak_attack_entries = [f for f in features if "Sneak Attack" in f]
        assert len(sneak_attack_entries) > 1, (
            "Expected multiple Sneak Attack entries (progressions) for rogue"
        )

    def test_cleric_level_10_has_divine_intervention(self) -> None:
        features = get_all_features_up_to_level("cleric", 10)
        assert "Divine Intervention" in features

    def test_monk_level_5_has_stunning_strike(self) -> None:
        features = get_all_features_up_to_level("monk", 5)
        assert "Stunning Strike" in features


class TestGetClassFeaturesBackwardsCompat:
    """Tests ensuring existing get_class_features() still returns dicts."""

    def test_returns_list_of_dicts(self) -> None:
        result = get_class_features("fighter", 1)
        assert isinstance(result, list)
        assert all(isinstance(f, dict) for f in result)

    def test_fighter_level_1_dicts(self) -> None:
        result = get_class_features("fighter", 1)
        names = [f["name"] for f in result]
        assert "Fighting Style" in names
        assert "Second Wind" in names

    def test_unknown_level_returns_empty_list(self) -> None:
        result = get_class_features("fighter", 99)
        assert result == []
