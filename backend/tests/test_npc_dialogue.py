"""Tests for the NPC dialogue system with conversation memory."""

import pytest
from app.database import Base, get_session
from app.main import app
from app.services.npc_dialogue_service import NPCDialogueService
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


def _make_test_db():
    """Create an isolated in-memory SQLite database for testing."""
    import app.models.db_models  # noqa: F401

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_session_factory():
    """Provide a session factory bound to an in-memory database."""
    return _make_test_db()


@pytest.fixture
def db(test_session_factory) -> Session:
    """Provide a single database session for service-level tests."""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(test_session_factory):
    """Test client backed by an isolated in-memory database."""

    def override_get_session():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.pop(get_session, None)


@pytest.fixture
def campaign_id() -> str:
    return "test_campaign_dialogue"


@pytest.fixture
def service() -> NPCDialogueService:
    return NPCDialogueService()


def _create_npc_via_api(client: TestClient, campaign_id: str, **kwargs) -> str:
    """Create an NPC profile via the API and return its ID."""
    payload = {"name": kwargs.pop("name", "Test NPC"), **kwargs}
    resp = client.post(f"/game/npcs/{campaign_id}", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


class TestGetDialogueContext:
    """Tests for GET /game/npcs/{campaign_id}/{npc_id}/dialogue-context."""

    def test_returns_personality_and_relationship(self, client, campaign_id) -> None:
        """Dialogue context includes personality traits and relationship data."""
        npc_id = _create_npc_via_api(
            client,
            campaign_id,
            name="Elara",
            personality_traits=["wise", "patient"],
            description="An elderly sage",
        )
        # Set a disposition so relationship exists
        client.patch(
            f"/game/npcs/{campaign_id}/{npc_id}/disposition",
            json={"disposition_score": 40, "event_note": "Helped find her cat"},
        )

        resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}/dialogue-context")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Elara"
        assert "wise" in data["personality_traits"]
        assert "patient" in data["personality_traits"]
        assert data["description"] == "An elderly sage"
        assert data["disposition_score"] == 40
        assert data["interactions_count"] == 1
        assert "Helped find her cat" in data["key_events"]

    def test_returns_recent_conversations(self, client, campaign_id) -> None:
        """Dialogue context includes recently recorded conversations."""
        npc_id = _create_npc_via_api(client, campaign_id, name="Barkeep")
        # Record a conversation
        client.post(
            f"/game/npcs/{campaign_id}/{npc_id}/conversation",
            json={
                "summary": "Asked about rumours in town",
                "disposition_change": 5,
                "topics": ["rumours", "town"],
            },
        )

        resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}/dialogue-context")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["recent_conversations"]) == 1
        assert data["recent_conversations"][0]["summary"] == "Asked about rumours in town"
        assert "rumours" in data["recent_conversations"][0]["topics"]

    def test_empty_history_returns_valid_context(self, client, campaign_id) -> None:
        """NPC with no conversation history still returns a valid context dict."""
        npc_id = _create_npc_via_api(client, campaign_id, name="Silent Guard")
        resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}/dialogue-context")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Silent Guard"
        assert data["recent_conversations"] == []
        assert data["conversation_notes"] == []
        assert data["disposition_score"] == 0
        assert data["interactions_count"] == 0
        assert "disposition_tone" in data

    def test_unknown_npc_returns_404(self, client, campaign_id) -> None:
        """Requesting dialogue context for a non-existent NPC returns 404."""
        resp = client.get(f"/game/npcs/{campaign_id}/nonexistent/dialogue-context")
        assert resp.status_code == 404


class TestRecordConversation:
    """Tests for POST /game/npcs/{campaign_id}/{npc_id}/conversation."""

    def test_record_conversation_returns_201(self, client, campaign_id) -> None:
        """Recording a conversation returns HTTP 201."""
        npc_id = _create_npc_via_api(client, campaign_id, name="Merchant")
        resp = client.post(
            f"/game/npcs/{campaign_id}/{npc_id}/conversation",
            json={"summary": "Bought a healing potion"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "recorded"
        assert data["npc_id"] == npc_id

    def test_record_conversation_updates_notes_and_disposition(
        self, client, campaign_id
    ) -> None:
        """Recording a conversation updates conversation_notes and disposition score."""
        npc_id = _create_npc_via_api(client, campaign_id, name="Blacksmith")

        client.post(
            f"/game/npcs/{campaign_id}/{npc_id}/conversation",
            json={
                "summary": "Commissioned a new sword",
                "disposition_change": 10,
                "topics": ["weapons", "crafting"],
            },
        )

        # Verify via the profile endpoint
        profile_resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        assert profile_resp.status_code == 200
        profile_data = profile_resp.json()
        assert "Commissioned a new sword" in profile_data["profile"]["conversation_notes"]

        # Relationship should have been created
        rel = profile_data["relationship"]
        assert rel is not None
        assert rel["disposition_score"] == 10
        assert rel["interactions_count"] == 1

    def test_multiple_conversations_accumulate(self, client, campaign_id) -> None:
        """Multiple recorded conversations stack disposition changes."""
        npc_id = _create_npc_via_api(client, campaign_id, name="Innkeeper")

        client.post(
            f"/game/npcs/{campaign_id}/{npc_id}/conversation",
            json={"summary": "Rented a room", "disposition_change": 5},
        )
        client.post(
            f"/game/npcs/{campaign_id}/{npc_id}/conversation",
            json={"summary": "Complimented the stew", "disposition_change": 10},
        )

        profile_resp = client.get(f"/game/npcs/{campaign_id}/{npc_id}")
        rel = profile_resp.json()["relationship"]
        assert rel["disposition_score"] == 15
        assert rel["interactions_count"] == 2

        notes = profile_resp.json()["profile"]["conversation_notes"]
        assert "Rented a room" in notes
        assert "Complimented the stew" in notes

    def test_record_conversation_unknown_npc_returns_404(
        self, client, campaign_id
    ) -> None:
        """Recording a conversation for a non-existent NPC returns 404."""
        resp = client.post(
            f"/game/npcs/{campaign_id}/nonexistent/conversation",
            json={"summary": "Hello"},
        )
        assert resp.status_code == 404


class TestDialoguePrompt:
    """Tests for NPCDialogueService.get_dialogue_prompt (service-level)."""

    def _create_npc_in_db(self, db: Session, campaign_id: str, **kwargs) -> str:
        """Insert an NPC profile directly into the database."""
        import uuid

        from app.models.db_models import NPCProfileDB

        npc_id = str(uuid.uuid4())
        row = NPCProfileDB(
            id=npc_id,
            campaign_id=campaign_id,
            name=kwargs.get("name", "Test NPC"),
            description=kwargs.get("description", ""),
            personality_traits=kwargs.get("personality_traits", []),
            disposition=kwargs.get("disposition", "neutral"),
            location=kwargs.get("location", ""),
            is_alive=True,
            conversation_notes=[],
            conversation_history=[],
        )
        db.add(row)
        db.commit()
        return npc_id

    def test_prompt_includes_personality(self, service, db, campaign_id) -> None:
        """Dialogue prompt mentions personality traits."""
        npc_id = self._create_npc_in_db(
            db,
            campaign_id,
            name="Grumpy Dwarf",
            personality_traits=["grumpy", "loyal"],
        )
        prompt = service.get_dialogue_prompt(npc_id, campaign_id, db)
        assert "Grumpy Dwarf" in prompt
        assert "grumpy" in prompt
        assert "loyal" in prompt

    def test_prompt_includes_description(self, service, db, campaign_id) -> None:
        """Dialogue prompt includes NPC description."""
        npc_id = self._create_npc_in_db(
            db,
            campaign_id,
            name="The Oracle",
            description="A blind seer who speaks in riddles",
        )
        prompt = service.get_dialogue_prompt(npc_id, campaign_id, db)
        assert "A blind seer who speaks in riddles" in prompt

    def test_disposition_affects_tone(self, service, db, campaign_id) -> None:
        """Different disposition scores produce different tone descriptions."""
        import uuid

        from app.models.db_models import NPCRelationshipDB

        npc_id = self._create_npc_in_db(db, campaign_id, name="Guard Captain")

        # Create a friendly relationship
        rel = NPCRelationshipDB(
            id=str(uuid.uuid4()),
            npc_id=npc_id,
            campaign_id=campaign_id,
            disposition_score=60,
            interactions_count=5,
            key_events=[],
            last_interaction="",
        )
        db.add(rel)
        db.commit()

        prompt = service.get_dialogue_prompt(npc_id, campaign_id, db)
        assert "warm" in prompt or "trusted" in prompt or "allies" in prompt

    def test_hostile_disposition_tone(self, service, db, campaign_id) -> None:
        """Hostile disposition produces appropriately negative tone."""
        import uuid

        from app.models.db_models import NPCRelationshipDB

        npc_id = self._create_npc_in_db(db, campaign_id, name="Bandit Leader")

        rel = NPCRelationshipDB(
            id=str(uuid.uuid4()),
            npc_id=npc_id,
            campaign_id=campaign_id,
            disposition_score=-70,
            interactions_count=2,
            key_events=[],
            last_interaction="",
        )
        db.add(rel)
        db.commit()

        prompt = service.get_dialogue_prompt(npc_id, campaign_id, db)
        assert "hostile" in prompt or "threatening" in prompt or "dismissive" in prompt

    def test_prompt_empty_for_unknown_npc(self, service, db, campaign_id) -> None:
        """Dialogue prompt returns empty string for non-existent NPC."""
        prompt = service.get_dialogue_prompt("nonexistent", campaign_id, db)
        assert prompt == ""

    def test_prompt_includes_recent_topics(self, service, db, campaign_id) -> None:
        """Dialogue prompt references topics from recent conversations."""
        npc_id = self._create_npc_in_db(db, campaign_id, name="Librarian")

        # Record a conversation with topics
        service.record_conversation(
            npc_id=npc_id,
            campaign_id=campaign_id,
            summary="Discussed ancient tomes",
            disposition_change=5,
            topics=["ancient history", "forbidden knowledge"],
            db=db,
        )

        prompt = service.get_dialogue_prompt(npc_id, campaign_id, db)
        assert "ancient history" in prompt
        assert "forbidden knowledge" in prompt
