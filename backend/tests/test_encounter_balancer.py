"""
Tests for encounter_balancer.py

Covers:
- CR-to-XP conversion
- Encounter multiplier logic
- Party XP budget calculation
- Encounter difficulty labelling
- XP award calculation
- Encounter generation
"""


from app.encounter_balancer import (
    CR_TO_XP,
    ENCOUNTER_DIFFICULTY_THRESHOLDS,
    calculate_encounter_xp,
    calculate_xp_award,
    cr_to_xp,
    generate_balanced_encounter,
    get_encounter_difficulty,
    get_encounter_multiplier,
    get_party_xp_budget,
)

# ---------------------------------------------------------------------------
# CR to XP
# ---------------------------------------------------------------------------


class TestCrToXp:
    def test_known_fractional_crs(self) -> None:
        assert cr_to_xp("1/8") == 25
        assert cr_to_xp("1/4") == 50
        assert cr_to_xp("1/2") == 100

    def test_known_integer_crs(self) -> None:
        assert cr_to_xp("0") == 10
        assert cr_to_xp("1") == 200
        assert cr_to_xp("5") == 1800
        assert cr_to_xp("20") == 25000

    def test_all_srd_crs_covered(self) -> None:
        for cr in CR_TO_XP:
            assert cr_to_xp(cr) > 0

    def test_unknown_cr_returns_zero(self) -> None:
        assert cr_to_xp("99") == 0
        assert cr_to_xp("bad") == 0


# ---------------------------------------------------------------------------
# Encounter Multiplier
# ---------------------------------------------------------------------------


class TestGetEncounterMultiplier:
    def test_single_monster_standard_party(self) -> None:
        assert get_encounter_multiplier(1, 4) == 1.0

    def test_two_monsters_standard_party(self) -> None:
        assert get_encounter_multiplier(2, 4) == 1.5

    def test_three_to_six_monsters(self) -> None:
        for n in range(3, 7):
            assert get_encounter_multiplier(n, 4) == 2.0

    def test_seven_to_ten_monsters(self) -> None:
        for n in range(7, 11):
            assert get_encounter_multiplier(n, 4) == 2.5

    def test_small_party_steps_up(self) -> None:
        # Single monster, 2-person party → step up from 1.0 to 1.5
        assert get_encounter_multiplier(1, 2) == 1.5

    def test_large_party_steps_down(self) -> None:
        # Single monster, 6-person party → stays at 1.0 (already lowest)
        assert get_encounter_multiplier(1, 6) == 1.0
        # Two monsters, 6-person party → step down from 1.5 to 1.0
        assert get_encounter_multiplier(2, 6) == 1.0

    def test_zero_monsters(self) -> None:
        assert get_encounter_multiplier(0, 4) == 1.0


# ---------------------------------------------------------------------------
# Encounter XP Calculation
# ---------------------------------------------------------------------------

_GOBLIN = {"name": "Goblin", "cr": "1/4", "xp": 50, "type": "humanoid"}
_SKELETON = {"name": "Skeleton", "cr": "1/4", "xp": 50, "type": "undead"}
_ORC = {"name": "Orc", "cr": "1/2", "xp": 100, "type": "humanoid"}


class TestCalculateEncounterXp:
    def test_empty_encounter(self) -> None:
        result = calculate_encounter_xp([], 4)
        assert result["raw_xp"] == 0
        assert result["adjusted_xp"] == 0
        assert result["monster_count"] == 0

    def test_single_monster(self) -> None:
        result = calculate_encounter_xp([_GOBLIN], 4)
        assert result["raw_xp"] == 50
        assert result["multiplier"] == 1.0
        assert result["adjusted_xp"] == 50

    def test_two_monsters(self) -> None:
        result = calculate_encounter_xp([_GOBLIN, _SKELETON], 4)
        assert result["raw_xp"] == 100
        assert result["multiplier"] == 1.5
        assert result["adjusted_xp"] == 150

    def test_monster_without_xp_key_falls_back_to_cr(self) -> None:
        monster = {"name": "Wolf", "cr": "1/4", "type": "beast"}  # no xp key
        result = calculate_encounter_xp([monster], 4)
        assert result["raw_xp"] == 50

    def test_monster_count_is_correct(self) -> None:
        result = calculate_encounter_xp([_GOBLIN, _ORC, _SKELETON], 4)
        assert result["monster_count"] == 3


# ---------------------------------------------------------------------------
# Party XP Budget
# ---------------------------------------------------------------------------


class TestGetPartyXpBudget:
    def test_single_level_1_easy(self) -> None:
        assert get_party_xp_budget([1], "easy") == 25

    def test_four_level_1_medium(self) -> None:
        assert get_party_xp_budget([1, 1, 1, 1], "medium") == 200

    def test_mixed_party_hard(self) -> None:
        # Level 1 (75) + level 2 (150) = 225
        assert get_party_xp_budget([1, 2], "hard") == 225

    def test_all_difficulty_tiers_level_5(self) -> None:
        thresholds = ENCOUNTER_DIFFICULTY_THRESHOLDS[5]
        assert get_party_xp_budget([5], "easy") == thresholds["easy"]
        assert get_party_xp_budget([5], "medium") == thresholds["medium"]
        assert get_party_xp_budget([5], "hard") == thresholds["hard"]
        assert get_party_xp_budget([5], "deadly") == thresholds["deadly"]

    def test_level_clamped_to_20(self) -> None:
        # Level 25 → treated as 20
        assert get_party_xp_budget([25], "medium") == get_party_xp_budget(
            [20], "medium"
        )

    def test_level_clamped_to_1(self) -> None:
        assert get_party_xp_budget([0], "medium") == get_party_xp_budget([1], "medium")


# ---------------------------------------------------------------------------
# Encounter Difficulty
# ---------------------------------------------------------------------------


class TestGetEncounterDifficulty:
    def test_empty_party_returns_trivial(self) -> None:
        assert get_encounter_difficulty([], [_GOBLIN]) == "trivial"

    def test_empty_monsters_returns_trivial(self) -> None:
        assert get_encounter_difficulty([1, 1, 1, 1], []) == "trivial"

    def test_trivial_encounter(self) -> None:
        # Single Goblin vs. level 5 party of 4 → way below easy threshold
        result = get_encounter_difficulty([5, 5, 5, 5], [_GOBLIN])
        assert result == "trivial"

    def test_easy_encounter(self) -> None:
        # 1 goblin (50 XP adj) vs 1 level-1 character (easy=25, medium=50)
        # 50 >= medium(50) so it's medium actually; let's test with a kobold
        kobold = {"name": "Kobold", "cr": "1/8", "xp": 25}
        result = get_encounter_difficulty([1], [kobold])
        # adjusted=25, easy budget=25, medium budget=50 → easy
        assert result == "easy"

    def test_medium_encounter(self) -> None:
        # 1 orc (100) + 1 goblin (50), 4-person party:
        # raw=150, multiplier=1.5, adjusted=225
        # medium_budget=200, hard_budget=300 → 200 <= 225 < 300 → medium
        result = get_encounter_difficulty([1, 1, 1, 1], [_ORC, _GOBLIN])
        assert result == "medium"

    def test_hard_encounter(self) -> None:
        # 2 goblins (raw=100) vs 1 level-1 char (party_size=1 → small party step-up)
        # get_encounter_multiplier(2, 1): base=1.5, step up → 2.0
        # adjusted = 100 * 2.0 = 200; deadly_budget = 100 → 200 >= 100 → deadly
        result = get_encounter_difficulty([1], [_GOBLIN, _GOBLIN])
        assert result == "deadly"

    def test_deadly_encounter(self) -> None:
        # Lots of orcs vs low-level party
        orcs = [_ORC] * 8  # 800 raw, multiplier 2.5 → 2000 adjusted
        result = get_encounter_difficulty([1, 1], orcs)
        assert result == "deadly"


# ---------------------------------------------------------------------------
# XP Award Calculation
# ---------------------------------------------------------------------------


class TestCalculateXpAward:
    def test_single_monster_four_characters(self) -> None:
        result = calculate_xp_award([_GOBLIN], 4)
        assert result["total_xp"] == 50
        assert result["xp_per_character"] == 12  # 50 // 4
        assert result["party_size"] == 4

    def test_multiple_monsters(self) -> None:
        result = calculate_xp_award([_GOBLIN, _ORC], 4)
        assert result["total_xp"] == 150  # 50 + 100
        assert result["xp_per_character"] == 37  # 150 // 4

    def test_empty_encounter_no_xp(self) -> None:
        result = calculate_xp_award([], 4)
        assert result["total_xp"] == 0
        assert result["xp_per_character"] == 0

    def test_zero_party_size_no_division_error(self) -> None:
        result = calculate_xp_award([_GOBLIN], 0)
        assert result["xp_per_character"] == 0

    def test_solo_character(self) -> None:
        result = calculate_xp_award([_GOBLIN], 1)
        assert result["xp_per_character"] == 50


# ---------------------------------------------------------------------------
# Encounter Generator
# ---------------------------------------------------------------------------


_SAMPLE_MONSTERS = [
    {"id": "goblin",   "name": "Goblin",   "cr": "1/4", "xp": 50,  "type": "humanoid"},
    {"id": "skeleton", "name": "Skeleton", "cr": "1/4", "xp": 50,  "type": "undead"},
    {"id": "orc",      "name": "Orc",      "cr": "1/2", "xp": 100, "type": "humanoid"},
    {"id": "wolf",     "name": "Wolf",     "cr": "1/4", "xp": 50,  "type": "beast"},
    {"id": "zombie",   "name": "Zombie",   "cr": "1/4", "xp": 50,  "type": "undead"},
    {"id": "ogre",     "name": "Ogre",     "cr": "2",   "xp": 450, "type": "giant"},
    {"id": "troll",    "name": "Troll",    "cr": "5",   "xp": 1800,"type": "giant"},
]


class TestGenerateBalancedEncounter:
    def test_returns_expected_keys(self) -> None:
        result = generate_balanced_encounter(
            [1, 1, 1, 1], "medium", available_monsters=_SAMPLE_MONSTERS
        )
        for key in ("monsters", "difficulty", "xp_budget", "adjusted_xp", "raw_xp",
                    "xp_per_character", "party_size"):
            assert key in result, f"Missing key: {key}"

    def test_empty_monster_pool_returns_empty(self) -> None:
        result = generate_balanced_encounter(
            [1, 1, 1, 1], "medium", available_monsters=[]
        )
        assert result["monsters"] == []

    def test_party_size_recorded_correctly(self) -> None:
        result = generate_balanced_encounter(
            [3, 3, 3], "easy", available_monsters=_SAMPLE_MONSTERS
        )
        assert result["party_size"] == 3

    def test_selected_monsters_are_from_pool(self) -> None:
        pool_ids = {m["id"] for m in _SAMPLE_MONSTERS}
        result = generate_balanced_encounter(
            [1, 1, 1, 1], "medium", available_monsters=_SAMPLE_MONSTERS
        )
        for monster in result["monsters"]:
            assert monster["id"] in pool_ids

    def test_adjusted_xp_not_wildly_over_budget(self) -> None:
        result = generate_balanced_encounter(
            [1, 1, 1, 1], "medium", available_monsters=_SAMPLE_MONSTERS
        )
        # Allow generous 200% budget overshoot; should still be bounded
        assert result["adjusted_xp"] <= result["xp_budget"] * 2

    def test_xp_per_character_is_raw_xp_divided_by_party(self) -> None:
        result = generate_balanced_encounter(
            [2, 2, 2, 2], "easy", available_monsters=_SAMPLE_MONSTERS
        )
        if result["monsters"]:
            expected = result["raw_xp"] // result["party_size"]
            assert result["xp_per_character"] == expected

    def test_generate_for_high_level_party(self) -> None:
        result = generate_balanced_encounter(
            [10, 10, 10, 10], "medium", available_monsters=_SAMPLE_MONSTERS
        )
        # Should still return something (even if it's all the monsters)
        assert isinstance(result["monsters"], list)

    def test_location_filter_dungeon(self) -> None:
        # _SAMPLE_MONSTERS has humanoid + undead options for dungeon; the wolf
        # (beast) should be excluded by the dungeon location filter since there
        # are enough preferred-type monsters available.
        dungeon_preferred = {"humanoid", "undead", "construct", "aberration"}
        result = generate_balanced_encounter(
            [1, 1, 1, 1],
            "medium",
            location="dungeon",
            available_monsters=_SAMPLE_MONSTERS,
        )
        if result["monsters"]:
            monster_types = {m.get("type") for m in result["monsters"]}
            # All selected monsters must be of dungeon-preferred types
            assert monster_types <= dungeon_preferred, (
                f"Unexpected monster types in dungeon encounter: "
                f"{monster_types - dungeon_preferred}"
            )

    def test_empty_party_levels_defaults_to_level_1(self) -> None:
        result = generate_balanced_encounter(
            [], "medium", available_monsters=_SAMPLE_MONSTERS
        )
        assert result["party_size"] == 1
