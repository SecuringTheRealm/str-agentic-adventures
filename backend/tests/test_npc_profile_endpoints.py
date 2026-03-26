"""Tests for the NPC Profile and NPCRelationship endpoints."""

import pytest
from app.database import Base, get_session
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _make_test_db():
    """Create an isolated in-memory SQLite database for testing.

    StaticPool forces a single shared connection so that the tables created by
    ``create_all`` are visible to every session yielded during the test.
    """
    import app.models.db_models  # noqa: F401 - register all ORM models with Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    """Test client backed by an isolated in-memory database."""
    testing_session_local = _make_test_db()

    def override_get_session():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def campaign_id() -> str:
    return "test_campaign_abc"


class TestCreateNPCProfile:
    """Tests for POST /game/npcs/{campaign_id}."""

    def test_create_npc_returns_201(self, client, campaign_id) -> None:
        """Creating an NPC profile returns HTTP 201."""
        resp = client.post(
            f"/game/npcs/{campaign_id}",
            json={"name": "Elara the Innkeeper"},
        )
        assert resp.status_code == 201

    def test_create_npc_stores_fields(self, client, campaign_id) -> None:
        """Created NPC profile contains expected fields."""
        resp = client.post(
            f"/game/npcs/{campaign_id}",
            json={
                "name": "Dwarven Blacksmith",
                "description": "A stout dwarf with a booming laugh.",
                "personality_traits": ["grumpy", "honest"],
                "disposition": "friendly",
                "location": "Ironforge",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Dwarven Blacksmith"
        assert data["description"] == "A stout dwarf with a booming laugh."
        assert data["personality_traits"] == ["grumpy", "honest"]
        assert data["disposition"] == "friendly"
        assert data["location"] == "Ironforge"
        assert data["is_alive"] is True
        assert "id" in data

    def test_create_npc_defaults(self, client, campaign_id) -> None:
        """NPC profile has sensible defaults when optional fields are omitted."""
        resp = client.post(
            f"/game/npcs/{campaign_id}",
            json={"name": "Nameless Guard"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["disposition"] == "neutral"
        assert data["description"] == ""
        assert data["location"] == ""
        assert data["personality_traits"] == []
        assert data["conversation_notes"] == []


class TestListNPCProfiles:
    """Tests for GET /game/npcs/{campaign_id}."""

    def test_list_empty_campaign(self, client, campaign_id) -> None:
        """Listing NPCs for a campaign with none returns empty list."""
        resp = client.get(f"/game/npcs/{campaign_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["npcs"] == []
        assert data["total_count"] == 0

    def test_list_returns_created_npcs(self, client, campaign_id) -> None:
        """NPCs created in a campaign appear in the list."""
        for name in ("Alice", "Bob", "Charlie"):
            client.post(f"/game/npcs/{campaign_id}", json={"name": name})

        resp = client.get(f"/game/npcs/{campaign_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 3
        names = {npc["name"] for npc in data["npcs"]}
        assert names == {"Alice", "Bob", "Charlie"}

    def test_list_filtered_by_campaign(self, client) -> None:
        """NPCs are filtered to the requested campaign."""
        client.post("/game/npcs/campaign_A", json={"name": "NPC in A"})
        client.post("/game/npcs/campaign_B", json={"name": "NPC in B"})

        resp_a = client.get("/game/npcs/campaign_A")
        resp_b = client.get("/game/npcs/campaign_B")

        assert resp_a.json()["total_count"] == 1
        assert resp_a.json()["npcs"][0]["name"] == "NPC in A"
        assert resp_b.json()["total_count"] == 1
        assert resp_b.json()["npcs"][0]["name"] == "NPC in B"


class TestGetNPCProfile:
    """Tests for GET /game/npcs/{campaign_id}/{npc_id}."""

    def test_get_existing_npc(self, client, campaign_id) -> None:
        """Getting a created NPC returns its profile and no relationship."""
        create_resp = client.post(
            f"/game/npcs/{campaign_id}", json={"name": "The Oracle"}
        )
        npc_id = create_resp.json()["id"]

        resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["name"] == "The Oracle"
        assert data["profile"]["id"] == npc_id
        assert data["relationship"] is None

    def test_get_unknown_npc_returns_404(self, client, campaign_id) -> None:
        """Getting a non-existent NPC returns 404."""
        resp = client.get(f"/game/npcs/{campaign_id}/nonexistent-id")
        assert resp.status_code == 404

    def test_get_npc_wrong_campaign_returns_404(self, client, campaign_id) -> None:
        """Getting an NPC with the wrong campaign ID returns 404."""
        create_resp = client.post(
            f"/game/npcs/{campaign_id}", json={"name": "Hidden NPC"}
        )
        npc_id = create_resp.json()["id"]

        resp = client.get(f"/game/npcs/other_campaign/{npc_id}")
        assert resp.status_code == 404


class TestUpdateDisposition:
    """Tests for PATCH /game/npcs/{campaign_id}/{npc_id}/disposition."""

    def _create_npc(self, client, campaign_id, name="Test NPC") -> str:
        resp = client.post(f"/game/npcs/{campaign_id}", json={"name": name})
        return resp.json()["id"]

    def test_update_disposition_creates_relationship(
        self, client, campaign_id
    ) -> None:
        """First disposition update creates an NPCRelationship record."""
        npc_id = self._create_npc(client, campaign_id)
        resp = client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": 30},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["disposition_score"] == 30
        assert data["npc_id"] == npc_id
        assert data["campaign_id"] == campaign_id
        assert data["interactions_count"] == 1

    def test_disposition_score_clamped_positive(self, client, campaign_id) -> None:
        """Disposition score is clamped to 100."""
        npc_id = self._create_npc(client, campaign_id)
        resp = client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": 9999},
        )
        assert resp.status_code == 200
        assert resp.json()["disposition_score"] == 100

    def test_disposition_score_clamped_negative(self, client, campaign_id) -> None:
        """Disposition score is clamped to -100."""
        npc_id = self._create_npc(client, campaign_id)
        resp = client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": -9999},
        )
        assert resp.status_code == 200
        assert resp.json()["disposition_score"] == -100

    def test_key_events_accumulate(self, client, campaign_id) -> None:
        """Key events accumulate across multiple disposition updates."""
        npc_id = self._create_npc(client, campaign_id)
        client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": 10, "event_note": "First meeting"},
        )
        client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": 25, "event_note": "Saved the village"},
        )

        # Retrieve NPC to inspect relationship
        get_resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        rel = get_resp.json()["relationship"]
        assert "First meeting" in rel["key_events"]
        assert "Saved the village" in rel["key_events"]
        assert len(rel["key_events"]) == 2

    def test_interactions_count_increments(self, client, campaign_id) -> None:
        """interactions_count increments on each update."""
        npc_id = self._create_npc(client, campaign_id)
        for i in range(3):
            client.patch(
                f"/game/npcs/{campaign_id}/{npc_id}/disposition",
                json={"disposition_score": i * 10},
            )

        get_resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        rel = get_resp.json()["relationship"]
        assert rel["interactions_count"] == 3

    def test_update_disposition_unknown_npc_returns_404(
        self, client, campaign_id
    ) -> None:
        """Updating disposition on a non-existent NPC returns 404."""
        resp = client.patch(
            f"/game/npcs/{campaign_id}/nonexistent/disposition",
            json={"disposition_score": 10},
        )
        assert resp.status_code == 404

    def test_relationship_visible_in_get_npc(self, client, campaign_id) -> None:
        """After a disposition update, the relationship appears in get-NPC response."""
        npc_id = self._create_npc(client, campaign_id)
        client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": -50},
        )

        resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        assert resp.status_code == 200
        rel = resp.json()["relationship"]
        assert rel is not None
        assert rel["disposition_score"] == -50
