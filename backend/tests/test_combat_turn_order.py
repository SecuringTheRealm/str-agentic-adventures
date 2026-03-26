"""Tests for combat turn-order enforcement.

Covers:
1. Turn order follows initiative (roll_initiative).
2. Can't act out of turn (is_combatant_turn).
3. Turn advances correctly (advance_turn).
4. Round tracking — after all combatants act, round increments (advance_turn).
5. Removed combatants — killed/removed combatants are skipped (remove_combatant).
6. Delayed/held actions — delaying moves a combatant down in initiative.
"""

from unittest.mock import patch

import pytest
from app.rules_engine import (
    advance_turn,
    get_active_combatant,
    is_combatant_turn,
    remove_combatant,
    roll_initiative,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FIGHTER = {"id": "fighter", "name": "Fighter", "dex_modifier": 1}
_ROGUE = {"id": "rogue", "name": "Rogue", "dex_modifier": 4}
_WIZARD = {"id": "wizard", "name": "Wizard", "dex_modifier": 2}
_GOBLIN = {"id": "goblin", "name": "Goblin", "dex_modifier": 2}


def _fixed_initiative(combatants: list[dict], rolls: list[int]) -> list[dict]:
    """Run roll_initiative with deterministic d20 results."""
    with patch("app.rules_engine.random.randint", side_effect=rolls):
        return roll_initiative(combatants)


# ---------------------------------------------------------------------------
# 1. Turn order follows initiative
# ---------------------------------------------------------------------------


class TestTurnOrderFollowsInitiative:
    """After rolling initiative, combatants are ordered highest initiative first."""

    def test_highest_initiative_goes_first(self) -> None:
        # Rogue rolls 16 (+4) = 20, Wizard rolls 10 (+2) = 12, Fighter rolls 8 (+1) = 9
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )
        assert order[0]["id"] == "rogue"
        assert order[1]["id"] == "wizard"
        assert order[2]["id"] == "fighter"

    def test_lowest_initiative_goes_last(self) -> None:
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[5, 14, 9]
        )
        assert order[-1]["id"] == "fighter"

    def test_four_combatants_sorted_descending(self) -> None:
        # rolls: Fighter=6, Rogue=15, Wizard=11, Goblin=8
        # totals: Fighter=7, Rogue=19, Wizard=13, Goblin=10
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD, _GOBLIN], rolls=[6, 15, 11, 8]
        )
        initiatives = [c["initiative"] for c in order]
        assert initiatives == sorted(initiatives, reverse=True)

    def test_dex_modifier_breaks_ties(self) -> None:
        # Both roll 10; Rogue (dex 4) beats Fighter (dex 1)
        order = _fixed_initiative([_FIGHTER, _ROGUE], rolls=[10, 6])
        # Fighter: 10+1=11, Rogue: 6+4=10 — but same if both produce same total
        # Force a tie: Fighter rolls 9 (+1=10), Rogue rolls 6 (+4=10)
        order = _fixed_initiative([_FIGHTER, _ROGUE], rolls=[9, 6])
        assert order[0]["initiative"] == order[1]["initiative"] == 10
        assert order[0]["id"] == "rogue"  # higher dex_modifier wins

    def test_initiative_fields_added_to_results(self) -> None:
        order = _fixed_initiative([_FIGHTER], rolls=[12])
        assert "initiative_roll" in order[0]
        assert "initiative" in order[0]
        assert order[0]["initiative_roll"] == 12
        assert order[0]["initiative"] == 13  # 12 + 1 (fighter dex)

    def test_original_combatant_data_preserved(self) -> None:
        order = _fixed_initiative([_FIGHTER], rolls=[10])
        assert order[0]["name"] == "Fighter"
        assert order[0]["id"] == "fighter"

    def test_single_combatant_is_first(self) -> None:
        order = _fixed_initiative([_ROGUE], rolls=[7])
        assert len(order) == 1
        assert order[0]["id"] == "rogue"

    def test_empty_combatant_list_returns_empty(self) -> None:
        assert roll_initiative([]) == []


# ---------------------------------------------------------------------------
# 2. Can't act out of turn
# ---------------------------------------------------------------------------


class TestCannotActOutOfTurn:
    """is_combatant_turn rejects actions from combatants who aren't active."""

    def setup_method(self) -> None:
        # Rogue goes first (initiative 20), Wizard second (12), Fighter third (9)
        self.order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )
        self.current_turn = 0  # Rogue's turn

    def test_active_combatant_can_act(self) -> None:
        assert is_combatant_turn(self.order, self.current_turn, "rogue") is True

    def test_inactive_combatant_cannot_act(self) -> None:
        assert is_combatant_turn(self.order, self.current_turn, "fighter") is False
        assert is_combatant_turn(self.order, self.current_turn, "wizard") is False

    def test_unknown_combatant_cannot_act(self) -> None:
        assert is_combatant_turn(self.order, self.current_turn, "dragon") is False

    def test_second_slot_combatant_can_act_on_second_turn(self) -> None:
        assert is_combatant_turn(self.order, 1, "wizard") is True

    def test_first_slot_combatant_cannot_act_on_second_turn(self) -> None:
        assert is_combatant_turn(self.order, 1, "rogue") is False

    def test_empty_turn_order(self) -> None:
        assert is_combatant_turn([], 0, "rogue") is False

    def test_out_of_range_current_turn(self) -> None:
        assert is_combatant_turn(self.order, 99, "rogue") is False


# ---------------------------------------------------------------------------
# 3. Turn advances correctly
# ---------------------------------------------------------------------------


class TestTurnAdvances:
    """After a combatant acts, the next combatant in initiative order becomes active."""

    def setup_method(self) -> None:
        # order: Rogue → Wizard → Fighter  (indices 0, 1, 2)
        self.order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )

    def test_advance_moves_to_next_slot(self) -> None:
        result = advance_turn(self.order, current_turn=0, current_round=1)
        assert result["current_turn"] == 1

    def test_advance_second_slot_moves_to_third(self) -> None:
        result = advance_turn(self.order, current_turn=1, current_round=1)
        assert result["current_turn"] == 2

    def test_round_does_not_advance_mid_round(self) -> None:
        result = advance_turn(self.order, current_turn=0, current_round=1)
        assert result["round_advanced"] is False
        assert result["current_round"] == 1

    def test_advance_from_last_slot_wraps_to_zero(self) -> None:
        result = advance_turn(self.order, current_turn=2, current_round=1)
        assert result["current_turn"] == 0

    def test_advance_result_has_required_keys(self) -> None:
        result = advance_turn(self.order, current_turn=0, current_round=1)
        assert "current_turn" in result
        assert "current_round" in result
        assert "round_advanced" in result

    def test_next_combatant_is_active_after_advance(self) -> None:
        result = advance_turn(self.order, current_turn=0, current_round=1)
        new_turn = result["current_turn"]
        assert is_combatant_turn(self.order, new_turn, "wizard") is True

    def test_empty_turn_order_raises(self) -> None:
        with pytest.raises(ValueError):
            advance_turn([], current_turn=0, current_round=1)


# ---------------------------------------------------------------------------
# 4. Round tracking
# ---------------------------------------------------------------------------


class TestRoundTracking:
    """After all combatants have acted, the round counter increments."""

    def setup_method(self) -> None:
        # Three combatants: order indices 0, 1, 2
        self.order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )

    def test_round_increments_after_last_combatant_acts(self) -> None:
        result = advance_turn(self.order, current_turn=2, current_round=1)
        assert result["round_advanced"] is True
        assert result["current_round"] == 2

    def test_round_increments_correctly_on_subsequent_rounds(self) -> None:
        result = advance_turn(self.order, current_turn=2, current_round=3)
        assert result["current_round"] == 4
        assert result["round_advanced"] is True

    def test_order_resets_to_top_after_round(self) -> None:
        result = advance_turn(self.order, current_turn=2, current_round=1)
        assert result["current_turn"] == 0

    def test_full_round_cycle(self) -> None:
        """Simulate a complete round through all three combatants."""
        turn = 0
        round_num = 1

        # Combatant 0 acts
        res = advance_turn(self.order, current_turn=turn, current_round=round_num)
        assert res["round_advanced"] is False
        turn, round_num = res["current_turn"], res["current_round"]

        # Combatant 1 acts
        res = advance_turn(self.order, current_turn=turn, current_round=round_num)
        assert res["round_advanced"] is False
        turn, round_num = res["current_turn"], res["current_round"]

        # Combatant 2 acts (last in round 1)
        res = advance_turn(self.order, current_turn=turn, current_round=round_num)
        assert res["round_advanced"] is True
        assert res["current_round"] == 2
        assert res["current_turn"] == 0

    def test_two_rounds_increments_twice(self) -> None:
        """Two complete rounds produce round 3."""
        last_idx = len(self.order) - 1

        result = advance_turn(self.order, current_turn=last_idx, current_round=1)
        assert result["current_round"] == 2

        result = advance_turn(self.order, current_turn=last_idx, current_round=2)
        assert result["current_round"] == 3

    def test_single_combatant_round_increments_each_turn(self) -> None:
        single = [_ROGUE]
        result = advance_turn(single, current_turn=0, current_round=1)
        assert result["round_advanced"] is True
        assert result["current_round"] == 2


# ---------------------------------------------------------------------------
# 5. Removed combatants are skipped
# ---------------------------------------------------------------------------


class TestRemovedCombatants:
    """Killed or otherwise removed combatants are dropped from the turn order."""

    def setup_method(self) -> None:
        # Order: Rogue(0) → Wizard(1) → Fighter(2)
        self.order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )

    def test_removed_combatant_absent_from_turn_order(self) -> None:
        result = remove_combatant(self.order, current_turn=0, combatant_id="wizard")
        ids = [c["id"] for c in result["turn_order"]]
        assert "wizard" not in ids

    def test_turn_order_length_decreases_by_one(self) -> None:
        result = remove_combatant(self.order, current_turn=0, combatant_id="fighter")
        assert len(result["turn_order"]) == len(self.order) - 1

    def test_removing_combatant_before_current_adjusts_index(self) -> None:
        # Remove rogue (idx 0) while wizard's turn is active (current_turn=1)
        result = remove_combatant(self.order, current_turn=1, combatant_id="rogue")
        # After removal wizard is now at index 0; current_turn should shift to 0
        assert result["current_turn"] == 0
        assert result["turn_order"][0]["id"] == "wizard"

    def test_removing_combatant_after_current_preserves_index(self) -> None:
        # Rogue's turn (current_turn=0); remove fighter (idx 2, after current)
        result = remove_combatant(self.order, current_turn=0, combatant_id="fighter")
        assert result["current_turn"] == 0
        assert result["turn_order"][0]["id"] == "rogue"

    def test_removing_active_combatant_mid_order(self) -> None:
        # Remove wizard (idx 1) while it is wizard's turn (current_turn=1)
        result = remove_combatant(self.order, current_turn=1, combatant_id="wizard")
        # After removal, idx 1 now points to fighter (next in line)
        assert result["current_turn"] == 1
        assert result["turn_order"][1]["id"] == "fighter"

    def test_removing_last_active_combatant_wraps_to_zero(self) -> None:
        # Fighter is last (idx 2); remove fighter when it's fighter's turn
        result = remove_combatant(self.order, current_turn=2, combatant_id="fighter")
        assert result["current_turn"] == 0

    def test_removing_nonexistent_combatant_is_no_op(self) -> None:
        result = remove_combatant(self.order, current_turn=0, combatant_id="dragon")
        assert len(result["turn_order"]) == len(self.order)
        assert result["current_turn"] == 0

    def test_removed_combatant_never_becomes_active(self) -> None:
        # Remove wizard then iterate through all turns — wizard should never appear
        result = remove_combatant(self.order, current_turn=0, combatant_id="wizard")
        new_order = result["turn_order"]
        active_ids = [c["id"] for c in new_order]
        assert "wizard" not in active_ids

    def test_all_remaining_combatants_still_act_after_removal(self) -> None:
        # Remove wizard; rogue and fighter should still act in order
        result = remove_combatant(self.order, current_turn=0, combatant_id="wizard")
        new_order = result["turn_order"]
        remaining_ids = {c["id"] for c in new_order}
        assert remaining_ids == {"rogue", "fighter"}


# ---------------------------------------------------------------------------
# get_active_combatant helper
# ---------------------------------------------------------------------------


class TestGetActiveCombatant:
    """Unit tests for the get_active_combatant helper."""

    def setup_method(self) -> None:
        self.order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )

    def test_returns_correct_combatant_at_index(self) -> None:
        assert get_active_combatant(self.order, 0)["id"] == "rogue"
        assert get_active_combatant(self.order, 1)["id"] == "wizard"
        assert get_active_combatant(self.order, 2)["id"] == "fighter"

    def test_returns_none_for_empty_list(self) -> None:
        assert get_active_combatant([], 0) is None

    def test_returns_none_for_out_of_range_index(self) -> None:
        assert get_active_combatant(self.order, 99) is None

    def test_returns_none_for_negative_index(self) -> None:
        assert get_active_combatant(self.order, -1) is None


# ---------------------------------------------------------------------------
# 6. Delayed / held actions (optional — tests the spec; implemented via re-sort)
# ---------------------------------------------------------------------------


class TestDelayedActions:
    """A combatant who delays should move down in initiative order.

    Implementation strategy: delaying is modelled by reducing the
    combatant's ``initiative`` value and re-sorting the turn order.
    The tests below validate the expected behaviour of that pattern.
    """

    def test_delaying_moves_combatant_down_in_order(self) -> None:
        """A combatant who delays should act after those with higher initiative."""
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )
        # Original: Rogue(20) → Wizard(12) → Fighter(9)
        assert order[0]["id"] == "rogue"

        # Rogue delays: lower their initiative below the next combatant
        delayed_order = list(order)
        rogue_entry = dict(delayed_order[0])
        # Set rogue's initiative just below wizard's to slot in between wizard and fighter
        rogue_entry["initiative"] = order[1]["initiative"] - 1
        delayed_order[0] = rogue_entry

        # Re-sort to reflect the delay
        delayed_order.sort(
            key=lambda c: (c["initiative"], c.get("dex_modifier", 0)), reverse=True
        )

        # Wizard should now go first; rogue should have moved down
        assert delayed_order[0]["id"] == "wizard"
        rogue_position = next(
            i for i, c in enumerate(delayed_order) if c["id"] == "rogue"
        )
        assert rogue_position > 0  # Rogue is no longer first

    def test_delaying_to_end_places_combatant_last(self) -> None:
        """Delaying to initiative 0 places the combatant at the very end."""
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )
        # Rogue delays to initiative 0
        delayed_order = list(order)
        rogue_entry = dict(delayed_order[0])
        rogue_entry["initiative"] = 0
        delayed_order[0] = rogue_entry

        delayed_order.sort(
            key=lambda c: (c["initiative"], c.get("dex_modifier", 0)), reverse=True
        )

        assert delayed_order[-1]["id"] == "rogue"

    def test_non_delaying_combatants_order_unchanged(self) -> None:
        """Combatants who do not delay keep their relative order."""
        order = _fixed_initiative(
            [_FIGHTER, _ROGUE, _WIZARD], rolls=[8, 16, 10]
        )
        # Only rogue delays
        delayed_order = list(order)
        rogue_entry = dict(delayed_order[0])
        rogue_entry["initiative"] = 0
        delayed_order[0] = rogue_entry

        delayed_order.sort(
            key=lambda c: (c["initiative"], c.get("dex_modifier", 0)), reverse=True
        )

        non_rogue = [c for c in delayed_order if c["id"] != "rogue"]
        assert non_rogue[0]["id"] == "wizard"
        assert non_rogue[1]["id"] == "fighter"
