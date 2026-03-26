"""
Tests for spell slot tracking, consumption, and recovery.

Covers:
- Full caster slot tables (wizard/cleric/druid/bard/sorcerer)
- Half caster (paladin/ranger) starting at level 2
- Warlock pact magic system
- Slot consumption and recovery
- Upcasting checks
"""

import pytest
from app.models.game_models import SpellSlotState
from app.plugins.rules_engine_plugin import RulesEnginePlugin


class TestSpellSlotState:
    """Test the SpellSlotState Pydantic model."""

    @pytest.mark.unit
    def test_default_empty_state(self) -> None:
        """SpellSlotState initialises with empty dicts by default."""
        state = SpellSlotState()
        assert state.max_slots == {}
        assert state.used_slots == {}

    @pytest.mark.unit
    def test_state_with_values(self) -> None:
        """SpellSlotState stores max and used slot counts correctly."""
        state = SpellSlotState(
            max_slots={1: 4, 2: 3, 3: 2},
            used_slots={1: 1, 2: 0, 3: 0},
        )
        assert state.max_slots[1] == 4
        assert state.used_slots[1] == 1


class TestGetSpellSlots:
    """Test get_spell_slots() for all caster types."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    # ---- Full casters -------------------------------------------------------

    @pytest.mark.unit
    def test_full_caster_level_1(self) -> None:
        """Wizard at level 1 gets two 1st-level slots."""
        slots = self.plugin.get_spell_slots("wizard", 1)
        assert slots == {1: 2}

    @pytest.mark.unit
    def test_full_caster_level_3(self) -> None:
        """Wizard at level 3 gets 1st and 2nd level slots."""
        slots = self.plugin.get_spell_slots("wizard", 3)
        assert slots == {1: 4, 2: 2}

    @pytest.mark.unit
    def test_full_caster_level_5(self) -> None:
        """Wizard at level 5 gets slots up to 3rd level."""
        slots = self.plugin.get_spell_slots("wizard", 5)
        assert slots == {1: 4, 2: 3, 3: 2}

    @pytest.mark.unit
    def test_full_caster_level_20(self) -> None:
        """Wizard at level 20 has all nine spell slot levels."""
        slots = self.plugin.get_spell_slots("wizard", 20)
        assert len(slots) == 9
        assert slots[1] == 4
        assert slots[9] == 1

    @pytest.mark.unit
    def test_cleric_matches_full_caster_table(self) -> None:
        """Cleric (full caster) matches the same slot table as wizard."""
        assert self.plugin.get_spell_slots("cleric", 5) == self.plugin.get_spell_slots(
            "wizard", 5
        )

    @pytest.mark.unit
    def test_case_insensitive(self) -> None:
        """Class name matching is case-insensitive."""
        assert self.plugin.get_spell_slots("Wizard", 1) == self.plugin.get_spell_slots(
            "wizard", 1
        )

    # ---- Half casters -------------------------------------------------------

    @pytest.mark.unit
    def test_half_caster_level_1_no_slots(self) -> None:
        """Paladin at level 1 has no spell slots (half-casters start at level 2)."""
        slots = self.plugin.get_spell_slots("paladin", 1)
        assert slots == {}

    @pytest.mark.unit
    def test_half_caster_level_2(self) -> None:
        """Paladin at level 2 gains first spell slots."""
        slots = self.plugin.get_spell_slots("paladin", 2)
        assert slots == {1: 2}

    @pytest.mark.unit
    def test_ranger_level_2(self) -> None:
        """Ranger at level 2 has the same slots as paladin."""
        assert self.plugin.get_spell_slots("ranger", 2) == self.plugin.get_spell_slots(
            "paladin", 2
        )

    @pytest.mark.unit
    def test_half_caster_max_level(self) -> None:
        """Paladin at level 20 caps at 5th-level slots (SRD half-caster table)."""
        slots = self.plugin.get_spell_slots("paladin", 20)
        assert max(slots.keys()) == 5

    # ---- Warlock pact magic -------------------------------------------------

    @pytest.mark.unit
    def test_warlock_level_1(self) -> None:
        """Warlock at level 1 has one 1st-level pact slot."""
        slots = self.plugin.get_spell_slots("warlock", 1)
        assert slots == {1: 1}

    @pytest.mark.unit
    def test_warlock_level_3(self) -> None:
        """Warlock at level 3 upgrades to 2nd-level pact slots."""
        slots = self.plugin.get_spell_slots("warlock", 3)
        assert slots == {2: 2}

    @pytest.mark.unit
    def test_warlock_level_11(self) -> None:
        """Warlock at level 11 has three 5th-level pact slots."""
        slots = self.plugin.get_spell_slots("warlock", 11)
        assert slots == {5: 3}

    @pytest.mark.unit
    def test_warlock_single_slot_level(self) -> None:
        """Warlock always has exactly one slot level (pact magic)."""
        for level in range(1, 21):
            slots = self.plugin.get_spell_slots("warlock", level)
            assert len(slots) == 1

    # ---- Error cases --------------------------------------------------------

    @pytest.mark.unit
    def test_non_spellcasting_class_raises(self) -> None:
        """Non-spellcasting class raises ValueError."""
        with pytest.raises(ValueError, match="not a spellcasting class"):
            self.plugin.get_spell_slots("fighter", 5)

    @pytest.mark.unit
    def test_invalid_level_raises(self) -> None:
        """Level outside 1-20 raises ValueError."""
        with pytest.raises(ValueError, match="Level must be between"):
            self.plugin.get_spell_slots("wizard", 0)

        with pytest.raises(ValueError, match="Level must be between"):
            self.plugin.get_spell_slots("wizard", 21)


class TestUseSpellSlot:
    """Test use_spell_slot() consumption logic."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    @pytest.mark.unit
    def test_consuming_slot_decrements_count(self) -> None:
        """Using a slot decrements the available count by one."""
        slots = {1: 4, 2: 3}
        updated = self.plugin.use_spell_slot(slots, 1)
        assert updated[1] == 3
        assert updated[2] == 3  # Unchanged

    @pytest.mark.unit
    def test_original_dict_not_mutated(self) -> None:
        """use_spell_slot does not mutate the input dict."""
        slots = {1: 2}
        self.plugin.use_spell_slot(slots, 1)
        assert slots[1] == 2  # Original unchanged

    @pytest.mark.unit
    def test_use_last_slot(self) -> None:
        """Using the last remaining slot leaves count at zero."""
        slots = {1: 1}
        updated = self.plugin.use_spell_slot(slots, 1)
        assert updated[1] == 0

    @pytest.mark.unit
    def test_no_slots_available_raises(self) -> None:
        """Using a slot when none are available raises ValueError."""
        slots = {1: 0}
        with pytest.raises(ValueError, match="No spell slots of level 1 available"):
            self.plugin.use_spell_slot(slots, 1)

    @pytest.mark.unit
    def test_missing_level_raises(self) -> None:
        """Using a slot level not present in available_slots raises ValueError."""
        slots = {1: 3}
        with pytest.raises(ValueError, match="No spell slots of level 2 available"):
            self.plugin.use_spell_slot(slots, 2)

    @pytest.mark.unit
    def test_upcast_consumes_higher_slot(self) -> None:
        """Upcasting consumes the higher-level slot, not the lower one."""
        slots = {1: 4, 2: 3}
        updated = self.plugin.use_spell_slot(slots, 2)
        assert updated[1] == 4  # Level-1 slots untouched
        assert updated[2] == 2  # Level-2 slot consumed


class TestRecoverSlots:
    """Test recover_slots() for long and short rests."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    @pytest.mark.unit
    def test_long_rest_recovers_all_slots(self) -> None:
        """Long rest restores all spell slots to maximum."""
        recovered = self.plugin.recover_slots("wizard", 5, "long")
        max_slots = self.plugin.get_spell_slots("wizard", 5)
        assert recovered == max_slots

    @pytest.mark.unit
    def test_long_rest_works_for_all_classes(self) -> None:
        """All spellcasting classes recover fully on a long rest."""
        for cls in ("wizard", "cleric", "druid", "bard", "sorcerer", "warlock",
                    "paladin", "ranger"):
            level = 5 if cls not in ("paladin", "ranger") else 5
            recovered = self.plugin.recover_slots(cls, level, "long")
            assert recovered == self.plugin.get_spell_slots(cls, level)

    @pytest.mark.unit
    def test_warlock_recovers_on_short_rest(self) -> None:
        """Warlock recovers all pact slots on a short rest."""
        recovered = self.plugin.recover_slots("warlock", 5, "short")
        max_slots = self.plugin.get_spell_slots("warlock", 5)
        assert recovered == max_slots

    @pytest.mark.unit
    def test_non_warlock_no_recovery_on_short_rest(self) -> None:
        """Non-warlock classes return empty dict on short rest (no recovery)."""
        recovered = self.plugin.recover_slots("wizard", 5, "short")
        assert recovered == {}

    @pytest.mark.unit
    def test_case_insensitive_rest_type(self) -> None:
        """rest_type matching is case-insensitive."""
        long_upper = self.plugin.recover_slots("wizard", 3, "Long")
        long_lower = self.plugin.recover_slots("wizard", 3, "long")
        assert long_upper == long_lower

    @pytest.mark.unit
    def test_invalid_rest_type_raises(self) -> None:
        """Invalid rest_type raises ValueError."""
        with pytest.raises(ValueError, match="rest_type must be"):
            self.plugin.recover_slots("wizard", 5, "nap")


class TestCanCastAtLevel:
    """Test can_cast_at_level() for upcasting checks."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.plugin = RulesEnginePlugin()

    @pytest.mark.unit
    def test_exact_level_available(self) -> None:
        """Returns True when a slot of the exact required level exists."""
        slots = {1: 4, 2: 3}
        assert self.plugin.can_cast_at_level(slots, 1) is True
        assert self.plugin.can_cast_at_level(slots, 2) is True

    @pytest.mark.unit
    def test_higher_slot_allows_upcasting(self) -> None:
        """Returns True when only a higher-level slot is available."""
        slots = {1: 0, 2: 3}
        assert self.plugin.can_cast_at_level(slots, 1) is True

    @pytest.mark.unit
    def test_no_suitable_slot(self) -> None:
        """Returns False when no slot at required level or higher is available."""
        slots = {1: 0, 2: 0}
        assert self.plugin.can_cast_at_level(slots, 1) is False

    @pytest.mark.unit
    def test_empty_slots(self) -> None:
        """Returns False for empty slot dict."""
        assert self.plugin.can_cast_at_level({}, 1) is False

    @pytest.mark.unit
    def test_required_level_too_high(self) -> None:
        """Returns False when the required level exceeds all available slots."""
        slots = {1: 4, 2: 3}
        assert self.plugin.can_cast_at_level(slots, 3) is False

    @pytest.mark.unit
    def test_partial_slots_exhausted(self) -> None:
        """Returns True when at least one level still has slots remaining."""
        slots = {1: 0, 2: 0, 3: 1}
        assert self.plugin.can_cast_at_level(slots, 2) is True
        assert self.plugin.can_cast_at_level(slots, 4) is False
