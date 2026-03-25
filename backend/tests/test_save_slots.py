"""
Tests for the save slot API endpoints.

Covers: create, retrieve, list, delete, load and business rules
(max 5 slots per campaign, slot-number reuse after delete).
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Return a TestClient backed by the real FastAPI app."""
    from app.main import app

    return TestClient(app)


@pytest.fixture()
def campaign_id(client: TestClient) -> str:
    """Create a fresh campaign and return its id."""
    response = client.post(
        "/game/campaign",
        json={"name": "Save Test Campaign", "setting": "fantasy", "tone": "heroic"},
    )
    assert response.status_code == 200
    return response.json()["id"]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _create_save(client: TestClient, campaign_id: str, **kwargs) -> dict:
    payload = {
        "name": kwargs.get("name", "Quick save"),
        "play_time_seconds": kwargs.get("play_time_seconds", 120),
        "interaction_count": kwargs.get("interaction_count", 5),
        "character_level": kwargs.get("character_level", 3),
        "current_location": kwargs.get("current_location", "Tavern"),
        "save_data": kwargs.get("save_data", {"hp": 42}),
    }
    response = client.post(f"/game/campaign/{campaign_id}/saves", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSaveSlotCreate:
    def test_create_save_returns_slot(self, client: TestClient, campaign_id: str) -> None:
        """Creating a save returns a SaveSlot with correct fields."""
        data = _create_save(
            client,
            campaign_id,
            name="Slot One",
            play_time_seconds=300,
            interaction_count=10,
            character_level=5,
            current_location="Dungeon Level 2",
            save_data={"hp": 30, "gold": 100},
        )

        assert data["campaign_id"] == campaign_id
        assert data["slot_number"] == 1  # first slot
        assert data["name"] == "Slot One"
        assert data["play_time_seconds"] == 300
        assert data["interaction_count"] == 10
        assert data["character_level"] == 5
        assert data["current_location"] == "Dungeon Level 2"
        assert data["save_data"] == {"hp": 30, "gold": 100}
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_second_save_uses_next_slot(self, client: TestClient, campaign_id: str) -> None:
        """Second save for the same campaign occupies slot 2."""
        first = _create_save(client, campaign_id)
        second = _create_save(client, campaign_id)
        assert first["slot_number"] == 1
        assert second["slot_number"] == 2

    def test_create_save_unknown_campaign_returns_404(self, client: TestClient) -> None:
        """Creating a save for a non-existent campaign returns 404."""
        response = client.post(
            "/game/campaign/nonexistent-id/saves",
            json={"name": "x", "save_data": {}},
        )
        assert response.status_code == 404

    def test_max_5_slots_per_campaign(self, client: TestClient, campaign_id: str) -> None:
        """No more than 5 save slots are allowed per campaign."""
        for _ in range(5):
            _create_save(client, campaign_id)

        # 6th attempt should be rejected
        response = client.post(
            f"/game/campaign/{campaign_id}/saves",
            json={"name": "overflow"},
        )
        assert response.status_code == 409


class TestSaveSlotRetrieve:
    def test_get_save_slot(self, client: TestClient, campaign_id: str) -> None:
        """GET /saves/{slot} returns the correct save slot."""
        created = _create_save(client, campaign_id, name="Retrieve Me")
        slot_num = created["slot_number"]

        response = client.get(f"/game/campaign/{campaign_id}/saves/{slot_num}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created["id"]
        assert data["name"] == "Retrieve Me"

    def test_get_nonexistent_slot_returns_404(self, client: TestClient, campaign_id: str) -> None:
        """GET on a slot that doesn't exist returns 404."""
        response = client.get(f"/game/campaign/{campaign_id}/saves/99")
        assert response.status_code == 404

    def test_list_saves_empty(self, client: TestClient, campaign_id: str) -> None:
        """Listing saves for a fresh campaign returns an empty list."""
        response = client.get(f"/game/campaign/{campaign_id}/saves")
        assert response.status_code == 200
        data = response.json()
        assert data["saves"] == []
        assert data["total_count"] == 0

    def test_list_saves_returns_all(self, client: TestClient, campaign_id: str) -> None:
        """Listing saves returns every created slot."""
        _create_save(client, campaign_id, name="A")
        _create_save(client, campaign_id, name="B")
        _create_save(client, campaign_id, name="C")

        response = client.get(f"/game/campaign/{campaign_id}/saves")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 3
        names = {s["name"] for s in data["saves"]}
        assert names == {"A", "B", "C"}

    def test_list_saves_unknown_campaign_returns_404(self, client: TestClient) -> None:
        """Listing saves for a non-existent campaign returns 404."""
        response = client.get("/game/campaign/no-such-campaign/saves")
        assert response.status_code == 404


class TestSaveSlotDelete:
    def test_delete_save_slot(self, client: TestClient, campaign_id: str) -> None:
        """Deleting a save slot returns 204 and the slot is gone."""
        created = _create_save(client, campaign_id)
        slot_num = created["slot_number"]

        response = client.delete(f"/game/campaign/{campaign_id}/saves/{slot_num}")
        assert response.status_code == 204

        # Confirm it's gone
        get_response = client.get(f"/game/campaign/{campaign_id}/saves/{slot_num}")
        assert get_response.status_code == 404

    def test_delete_frees_slot_number(self, client: TestClient, campaign_id: str) -> None:
        """After deletion the freed slot number is reused for the next save."""
        s1 = _create_save(client, campaign_id)
        _create_save(client, campaign_id)  # slot 2
        assert s1["slot_number"] == 1

        client.delete(f"/game/campaign/{campaign_id}/saves/1")

        # New save should claim slot 1 again
        new_save = _create_save(client, campaign_id)
        assert new_save["slot_number"] == 1

    def test_delete_nonexistent_slot_returns_404(self, client: TestClient, campaign_id: str) -> None:
        """Deleting a slot that doesn't exist returns 404."""
        response = client.delete(f"/game/campaign/{campaign_id}/saves/3")
        assert response.status_code == 404

    def test_delete_unknown_campaign_returns_404(self, client: TestClient) -> None:
        """Deleting a save for a non-existent campaign returns 404."""
        response = client.delete("/game/campaign/no-such-campaign/saves/1")
        assert response.status_code == 404


class TestSaveSlotLoad:
    def test_load_save_slot_returns_save_data(self, client: TestClient, campaign_id: str) -> None:
        """Loading a save slot returns the full save_data blob and metadata."""
        save_payload = {"hp": 25, "mana": 10, "position": {"x": 10, "y": 20}}
        created = _create_save(
            client,
            campaign_id,
            name="Boss Fight Save",
            play_time_seconds=600,
            interaction_count=20,
            character_level=8,
            current_location="Dragon's Lair",
            save_data=save_payload,
        )
        slot_num = created["slot_number"]

        response = client.post(f"/game/campaign/{campaign_id}/saves/{slot_num}/load")
        assert response.status_code == 200
        data = response.json()
        assert data["save_data"] == save_payload
        assert data["character_level"] == 8
        assert data["current_location"] == "Dragon's Lair"
        assert data["play_time_seconds"] == 600
        assert data["interaction_count"] == 20
        assert data["name"] == "Boss Fight Save"

    def test_load_nonexistent_slot_returns_404(self, client: TestClient, campaign_id: str) -> None:
        """Loading a slot that doesn't exist returns 404."""
        response = client.post(f"/game/campaign/{campaign_id}/saves/5/load")
        assert response.status_code == 404

    def test_load_unknown_campaign_returns_404(self, client: TestClient) -> None:
        """Loading a save for a non-existent campaign returns 404."""
        response = client.post("/game/campaign/no-such-campaign/saves/1/load")
        assert response.status_code == 404


class TestSaveSlotMetadata:
    def test_save_includes_metadata(self, client: TestClient, campaign_id: str) -> None:
        """SaveSlot stores play time, level, and location correctly."""
        created = _create_save(
            client,
            campaign_id,
            play_time_seconds=1800,
            interaction_count=42,
            character_level=10,
            current_location="Underdark",
        )
        assert created["play_time_seconds"] == 1800
        assert created["interaction_count"] == 42
        assert created["character_level"] == 10
        assert created["current_location"] == "Underdark"
