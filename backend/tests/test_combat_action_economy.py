"""Integration tests for combat action-economy enforcement (#769).

Exercises the real ``/game/combat/initialize`` and
``/game/combat/{id}/turn`` endpoints end to end (including DB persistence),
so the full request/response flow is covered, not just the rules_engine
helpers it's built on.
"""

from app.main import app
from fastapi.testclient import TestClient


def _init_combat(client: TestClient) -> dict:
    """Start a two-combatant encounter and return the response body."""
    response = client.post(
        "/game/combat/initialize",
        json={
            "participants": [
                {"type": "npc", "id": "combatant-a", "name": "A", "dex_modifier": 0},
                {"type": "npc", "id": "combatant-b", "name": "B", "dex_modifier": 0},
            ],
        },
    )
    assert response.status_code == 200
    return response.json()


class TestActionEconomyEnforcement:
    """Action/bonus-action/reaction used-flags surfaced and enforced (#769)."""

    def test_action_flag_starts_unused_and_is_set_after_use(self) -> None:
        with TestClient(app) as client:
            combat = _init_combat(client)
            first = combat["initiative_order"][0]
            assert first["action_used"] is False

            response = client.post(
                f"/game/combat/{combat['combat_id']}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            )
            body = response.json()
            assert body["success"] is True
            assert body["action_economy"]["action_used"] is True

    def test_second_action_same_turn_is_rejected(self) -> None:
        with TestClient(app) as client:
            combat = _init_combat(client)
            first = combat["initiative_order"][0]
            combat_id = combat["combat_id"]

            client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            )
            second_attempt = client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            ).json()

            assert second_attempt["success"] is False
            assert "already used" in second_attempt["description"]
            assert second_attempt["next_turn"] is False
            # No dice were rolled for the rejected attempt.
            assert second_attempt["damage"] == 0

    def test_flags_reset_when_turn_comes_back_around(self) -> None:
        with TestClient(app) as client:
            combat = _init_combat(client)
            first = combat["initiative_order"][0]
            second = combat["initiative_order"][1]
            combat_id = combat["combat_id"]

            # First combatant acts -> turn passes to second.
            client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            )
            # Second combatant acts -> round advances, turn returns to
            # first, refreshing first's action/bonus_action/reaction.
            client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": second["id"], "action": "dodge"},
            )

            third = client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            ).json()

            assert third["success"] is True
            assert third["action_economy"]["action_used"] is True

    def test_bonus_action_is_a_separate_slot_from_action(self) -> None:
        with TestClient(app) as client:
            combat = _init_combat(client)
            first = combat["initiative_order"][0]
            combat_id = combat["combat_id"]

            action_result = client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": first["id"], "action": "dodge"},
            ).json()
            assert action_result["success"] is True

            # Same combatant, same round, but a *bonus* action — should
            # still be free even though their action is already spent.
            bonus_result = client.post(
                f"/game/combat/{combat_id}/turn",
                json={
                    "character_id": first["id"],
                    "action": "dodge",
                    "action_economy": "bonus_action",
                },
            ).json()
            assert bonus_result["success"] is True
            assert bonus_result["action_economy"]["bonus_action_used"] is True

            # A second bonus action in the same round is rejected.
            second_bonus = client.post(
                f"/game/combat/{combat_id}/turn",
                json={
                    "character_id": first["id"],
                    "action": "dodge",
                    "action_economy": "bonus_action",
                },
            ).json()
            assert second_bonus["success"] is False
            assert "already used" in second_bonus["description"]

    def test_unknown_combatant_id_skips_enforcement(self) -> None:
        """Actions for an id not present in initiative order aren't tracked."""
        with TestClient(app) as client:
            combat = _init_combat(client)
            combat_id = combat["combat_id"]

            first = client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": "someone-not-in-combat", "action": "dodge"},
            ).json()
            second = client.post(
                f"/game/combat/{combat_id}/turn",
                json={"character_id": "someone-not-in-combat", "action": "dodge"},
            ).json()

            assert first["success"] is True
            assert second["success"] is True
            assert "action_economy" not in second or second.get("action_economy") is None
