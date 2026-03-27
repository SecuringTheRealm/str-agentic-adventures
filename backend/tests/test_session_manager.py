"""Tests for the multiplayer SessionManager service and REST endpoints."""

import uuid

import pytest
from app.database import Base, get_session
from app.main import app
from app.models.db_models import Campaign as CampaignDB
from app.models.db_models import Character as CharacterDB
from app.services.session_manager import SessionManager
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory SQLite database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """Return a TestClient that uses the in-memory DB session."""

    def override_get_session():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def campaign_id(db_session) -> str:
    """Insert a campaign row and return its id."""
    cid = str(uuid.uuid4())
    db_session.add(
        CampaignDB(
            id=cid,
            name="Test Campaign",
            setting="fantasy",
            tone="heroic",
            data={},
        )
    )
    db_session.commit()
    return cid


@pytest.fixture()
def character_id(db_session) -> str:
    """Insert a character row and return its id."""
    char_id = str(uuid.uuid4())
    db_session.add(
        CharacterDB(
            id=char_id,
            name="Testy McTestface",
            data={"class": "Fighter", "level": 1},
        )
    )
    db_session.commit()
    return char_id


@pytest.fixture()
def character_id_2(db_session) -> str:
    """Insert a second character row and return its id."""
    char_id = str(uuid.uuid4())
    db_session.add(
        CharacterDB(
            id=char_id,
            name="Second Hero",
            data={"class": "Wizard", "level": 1},
        )
    )
    db_session.commit()
    return char_id


@pytest.fixture()
def manager(db_session) -> SessionManager:
    """Return a SessionManager that uses the test db_session."""
    from unittest.mock import patch

    # Patch get_session_context to yield our test session
    class FakeContext:
        def __enter__(self) -> object:
            return db_session

        def __exit__(self, *args: object) -> None:
            pass

    with patch(
        "app.services.session_manager.get_session_context",
        return_value=FakeContext(),
    ):
        yield SessionManager()


# ---------------------------------------------------------------------------
# Unit tests for SessionManager
# ---------------------------------------------------------------------------


class TestSessionManagerCreateSession:
    def test_create_session(self, manager, campaign_id):
        session = manager.create_session(campaign_id)
        assert session["campaign_id"] == campaign_id
        assert session["status"] == "active"
        assert session["turn_order"] == []
        assert session["current_turn_index"] == 0
        assert "id" in session

    def test_create_session_ends_existing_active(self, manager, campaign_id):
        first = manager.create_session(campaign_id)
        second = manager.create_session(campaign_id)
        assert second["id"] != first["id"]
        # First session should be ended now
        old = manager.get_session(first["id"])
        assert old is not None
        assert old["status"] == "ended"


class TestSessionManagerJoin:
    def test_join_session(self, manager, campaign_id, character_id):
        session = manager.create_session(campaign_id)
        participant = manager.join_session(
            session["id"], character_id, "Alice"
        )
        assert participant["player_name"] == "Alice"
        assert participant["character_id"] == character_id
        assert participant["is_dm"] is False
        assert participant["is_connected"] is True

    def test_join_session_as_dm(self, manager, campaign_id, character_id):
        session = manager.create_session(campaign_id)
        participant = manager.join_session(
            session["id"], character_id, "DM Alice", is_dm=True
        )
        assert participant["is_dm"] is True

    def test_join_session_reconnect(self, manager, campaign_id, character_id):
        session = manager.create_session(campaign_id)
        p1 = manager.join_session(session["id"], character_id, "Alice")
        manager.leave_session(session["id"], p1["id"])
        # Rejoin with same character
        p2 = manager.join_session(session["id"], character_id, "Alice")
        assert p2["id"] == p1["id"]
        assert p2["is_connected"] is True

    def test_join_nonexistent_session(self, manager, character_id):
        with pytest.raises(ValueError, match="not found"):
            manager.join_session("fake-id", character_id, "Alice")


class TestSessionManagerLeave:
    def test_leave_session(self, manager, campaign_id, character_id):
        session = manager.create_session(campaign_id)
        p = manager.join_session(session["id"], character_id, "Alice")
        manager.leave_session(session["id"], p["id"])
        participants = manager.get_participants(session["id"])
        assert participants[0]["is_connected"] is False


class TestSessionManagerGetSession:
    def test_get_session_with_participants(
        self, manager, campaign_id, character_id
    ):
        session = manager.create_session(campaign_id)
        manager.join_session(session["id"], character_id, "Alice")
        result = manager.get_session(session["id"])
        assert result is not None
        assert len(result["participants"]) == 1

    def test_get_nonexistent_session(self, manager):
        assert manager.get_session("fake") is None

    def test_get_active_session(self, manager, campaign_id):
        session = manager.create_session(campaign_id)
        result = manager.get_active_session(campaign_id)
        assert result is not None
        assert result["id"] == session["id"]

    def test_get_active_session_none(self, manager):
        assert manager.get_active_session("no-campaign") is None


class TestSessionManagerTurns:
    def test_set_turn_order(self, manager, campaign_id, character_id, character_id_2):
        session = manager.create_session(campaign_id)
        updated = manager.set_turn_order(
            session["id"], [character_id, character_id_2]
        )
        assert updated["turn_order"] == [character_id, character_id_2]
        assert updated["current_turn_index"] == 0

    def test_advance_turn(self, manager, campaign_id, character_id, character_id_2):
        session = manager.create_session(campaign_id)
        manager.set_turn_order(session["id"], [character_id, character_id_2])
        next_id = manager.advance_turn(session["id"])
        assert next_id == character_id_2
        # Wrap around
        next_id = manager.advance_turn(session["id"])
        assert next_id == character_id

    def test_advance_turn_no_order(self, manager, campaign_id):
        session = manager.create_session(campaign_id)
        with pytest.raises(ValueError, match="no turn order"):
            manager.advance_turn(session["id"])


class TestSessionManagerEndSession:
    def test_end_session(self, manager, campaign_id, character_id):
        session = manager.create_session(campaign_id)
        manager.join_session(session["id"], character_id, "Alice")
        ended = manager.end_session(session["id"])
        assert ended["status"] == "ended"
        participants = manager.get_participants(session["id"])
        assert all(not p["is_connected"] for p in participants)

    def test_end_nonexistent_session(self, manager):
        with pytest.raises(ValueError, match="not found"):
            manager.end_session("fake")


# ---------------------------------------------------------------------------
# REST endpoint integration tests
# ---------------------------------------------------------------------------


class TestSessionEndpoints:
    def test_create_session_endpoint(self, client, campaign_id):
        resp = client.post("/game/session/create", json={"campaign_id": campaign_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["campaign_id"] == campaign_id
        assert data["status"] == "active"

    def test_create_session_missing_campaign(self, client):
        resp = client.post("/game/session/create", json={})
        assert resp.status_code == 400

    def test_get_session_endpoint(self, client, campaign_id):
        create = client.post("/game/session/create", json={"campaign_id": campaign_id})
        sid = create.json()["id"]
        resp = client.get(f"/game/session/{sid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_session_not_found(self, client):
        resp = client.get("/game/session/nonexistent")
        assert resp.status_code == 404

    def test_participants_endpoint(self, client, campaign_id):
        create = client.post("/game/session/create", json={"campaign_id": campaign_id})
        sid = create.json()["id"]
        resp = client.get(f"/game/session/{sid}/participants")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_end_session_endpoint(self, client, campaign_id):
        create = client.post("/game/session/create", json={"campaign_id": campaign_id})
        sid = create.json()["id"]
        resp = client.post(f"/game/session/{sid}/end")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ended"

    def test_end_session_not_found(self, client):
        resp = client.post("/game/session/nonexistent/end")
        assert resp.status_code == 404
