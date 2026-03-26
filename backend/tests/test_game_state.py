"""
Tests for the GameStateService and capture/restore API endpoints.

Covers:
- Capture state includes all expected fields (campaign, characters, NPCs)
- Restore state recreates entities correctly
- Save summary returns human-readable info
- Empty campaign produces valid (empty) state
- Round-trip: capture -> restore -> capture produces equivalent state
- API endpoint integration tests for capture, restore, and summary
"""

import uuid

import pytest
from app.database import Base, get_session
from app.main import app
from app.models.db_models import (
    NPC as NPCDB,
)
from app.models.db_models import (
    Campaign as CampaignDB,
)
from app.models.db_models import (
    Character as CharacterDB,
)
from app.models.db_models import (
    NPCProfileDB,
    NPCRelationshipDB,
)
from app.models.db_models import (
    SaveSlot as SaveSlotDB,
)
from app.services.game_state_service import GameStateService
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# In-memory DB fixtures
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


@pytest.fixture(scope="function")
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
def service() -> GameStateService:
    """Return a GameStateService instance."""
    return GameStateService()


@pytest.fixture()
def campaign_id(db_session) -> str:
    """Insert a campaign and return its id."""
    cid = str(uuid.uuid4())
    campaign = CampaignDB(
        id=cid,
        name="State Test Campaign",
        setting="dark fantasy",
        tone="gritty",
        homebrew_rules=[],
        is_template=False,
        is_custom=True,
        data={
            "id": cid,
            "name": "State Test Campaign",
            "setting": "dark fantasy",
            "tone": "gritty",
            "characters": [],
            "current_location": "Tavern of Shadows",
            "session_log": [
                {"role": "dm", "content": "You enter a dimly lit tavern."},
                {"role": "player", "content": "I look around cautiously."},
            ],
        },
    )
    db_session.add(campaign)
    db_session.commit()
    return cid


@pytest.fixture()
def populated_campaign(db_session, campaign_id) -> dict:
    """Create a campaign with characters, NPCs, profiles, and relationships."""
    char_id = str(uuid.uuid4())
    db_session.add(
        CharacterDB(
            id=char_id,
            name="Thorin Ironforge",
            data={
                "id": char_id,
                "name": "Thorin Ironforge",
                "level": 5,
                "hit_points": {"current": 45, "maximum": 50},
            },
        )
    )

    # Update campaign data to reference the character
    campaign = db_session.query(CampaignDB).filter(CampaignDB.id == campaign_id).first()
    campaign_data = campaign.data.copy()
    campaign_data["characters"] = [char_id]
    campaign.data = campaign_data

    # Legacy NPC
    npc_id = str(uuid.uuid4())
    db_session.add(
        NPCDB(
            id=npc_id,
            name="Bartender Bob",
            race="human",
            occupation="bartender",
            location="Tavern of Shadows",
            campaign_id=campaign_id,
            personality={"traits": ["gruff", "honest"]},
            stats={"strength": 12},
            relationships=[],
            data={"id": npc_id, "name": "Bartender Bob"},
        )
    )

    # NPC Profile
    profile_id = str(uuid.uuid4())
    db_session.add(
        NPCProfileDB(
            id=profile_id,
            campaign_id=campaign_id,
            name="Elara the Seer",
            description="A mysterious fortune teller",
            personality_traits=["cryptic", "wise"],
            disposition="friendly",
            location="Market Square",
            is_alive=True,
            conversation_notes=["Mentioned a dark prophecy"],
        )
    )

    # NPC Relationship
    rel_id = str(uuid.uuid4())
    db_session.add(
        NPCRelationshipDB(
            id=rel_id,
            npc_id=profile_id,
            campaign_id=campaign_id,
            disposition_score=25,
            interactions_count=3,
            key_events=["Helped find a lost ring"],
            last_interaction="Traded information about the dungeon",
        )
    )

    db_session.commit()

    return {
        "campaign_id": campaign_id,
        "character_id": char_id,
        "npc_id": npc_id,
        "profile_id": profile_id,
        "relationship_id": rel_id,
    }


# ---------------------------------------------------------------------------
# Unit tests — GameStateService
# ---------------------------------------------------------------------------


class TestCaptureState:
    def test_capture_includes_all_fields(self, service, db_session, populated_campaign):
        """Captured state dict contains all expected top-level keys."""
        state = service.capture_state(populated_campaign["campaign_id"], db_session)

        assert "version" in state
        assert "captured_at" in state
        assert "campaign_data" in state
        assert "characters" in state
        assert "npcs" in state
        assert "npc_profiles" in state
        assert "npc_relationships" in state
        assert "combat_state" in state
        assert "conversation_history" in state

    def test_capture_includes_characters(self, service, db_session, populated_campaign):
        """Characters are captured with correct data."""
        state = service.capture_state(populated_campaign["campaign_id"], db_session)

        assert len(state["characters"]) == 1
        char = state["characters"][0]
        assert char["id"] == populated_campaign["character_id"]
        assert char["name"] == "Thorin Ironforge"
        assert char["data"]["level"] == 5

    def test_capture_includes_npcs(self, service, db_session, populated_campaign):
        """Legacy NPCs are captured."""
        state = service.capture_state(populated_campaign["campaign_id"], db_session)

        assert len(state["npcs"]) == 1
        npc = state["npcs"][0]
        assert npc["name"] == "Bartender Bob"
        assert npc["race"] == "human"
        assert npc["occupation"] == "bartender"

    def test_capture_includes_npc_profiles(
        self, service, db_session, populated_campaign
    ):
        """NPC profiles are captured."""
        cid = populated_campaign["campaign_id"]
        state = service.capture_state(cid, db_session)

        assert len(state["npc_profiles"]) == 1
        profile = state["npc_profiles"][0]
        assert profile["name"] == "Elara the Seer"
        assert profile["disposition"] == "friendly"

    def test_capture_includes_npc_relationships(
        self, service, db_session, populated_campaign
    ):
        """NPC relationships are captured."""
        cid = populated_campaign["campaign_id"]
        state = service.capture_state(cid, db_session)

        assert len(state["npc_relationships"]) == 1
        rel = state["npc_relationships"][0]
        assert rel["disposition_score"] == 25
        assert rel["interactions_count"] == 3
        assert "Helped find a lost ring" in rel["key_events"]

    def test_capture_includes_conversation_history(
        self, service, db_session, campaign_id
    ):
        """Conversation history is captured from session_log."""
        state = service.capture_state(campaign_id, db_session)

        assert len(state["conversation_history"]) == 2
        first_entry = state["conversation_history"][0]
        assert first_entry["content"] == "You enter a dimly lit tavern."

    def test_capture_nonexistent_campaign_raises(self, service, db_session):
        """Capturing state for a missing campaign raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            service.capture_state("nonexistent-id", db_session)

    def test_capture_version_is_set(self, service, db_session, campaign_id):
        """State includes version number for future migration support."""
        state = service.capture_state(campaign_id, db_session)
        assert state["version"] == 1


class TestCaptureEmptyCampaign:
    def test_empty_campaign_produces_valid_state(self, service, db_session):
        """A campaign with no characters/NPCs produces a valid, empty state."""
        cid = str(uuid.uuid4())
        db_session.add(
            CampaignDB(
                id=cid,
                name="Empty Campaign",
                setting="void",
                tone="neutral",
                homebrew_rules=[],
                is_template=False,
                is_custom=True,
                data={"id": cid, "name": "Empty Campaign", "setting": "void"},
            )
        )
        db_session.commit()

        state = service.capture_state(cid, db_session)

        assert state["characters"] == []
        assert state["npcs"] == []
        assert state["npc_profiles"] == []
        assert state["npc_relationships"] == []
        assert state["combat_state"] is None
        assert state["conversation_history"] == []
        assert state["campaign_data"]["name"] == "Empty Campaign"


class TestRestoreState:
    def test_restore_recreates_entities(self, service, db_session, populated_campaign):
        """Restoring a captured state recreates all entities."""
        cid = populated_campaign["campaign_id"]
        state = service.capture_state(cid, db_session)

        # Remove all NPCs and profiles to simulate a clean slate
        db_session.query(NPCRelationshipDB).filter(
            NPCRelationshipDB.campaign_id == cid
        ).delete()
        db_session.query(NPCProfileDB).filter(
            NPCProfileDB.campaign_id == cid
        ).delete()
        db_session.query(NPCDB).filter(NPCDB.campaign_id == cid).delete()
        db_session.commit()

        # Verify they're gone
        npc_q = db_session.query(NPCDB).filter(
            NPCDB.campaign_id == cid
        )
        prof_q = db_session.query(NPCProfileDB).filter(
            NPCProfileDB.campaign_id == cid
        )
        rel_q = db_session.query(NPCRelationshipDB).filter(
            NPCRelationshipDB.campaign_id == cid
        )
        assert npc_q.count() == 0
        assert prof_q.count() == 0

        # Restore
        result = service.restore_state(cid, state, db_session)

        assert result["campaign"] is True
        assert result["characters_restored"] == 1
        assert result["npcs_restored"] == 1
        assert result["npc_profiles_restored"] == 1
        assert result["npc_relationships_restored"] == 1

        # Check entities exist again
        assert npc_q.count() == 1
        assert prof_q.count() == 1
        assert rel_q.count() == 1

    def test_restore_nonexistent_campaign_raises(self, service, db_session):
        """Restoring to a missing campaign raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            service.restore_state("nonexistent-id", {}, db_session)

    def test_restore_updates_campaign_data(
        self, service, db_session, campaign_id
    ):
        """Restoring updates the campaign data blob."""
        modified_data = {
            "campaign_data": {
                "id": campaign_id,
                "name": "Renamed Campaign",
                "setting": "high fantasy",
                "tone": "heroic",
            },
        }
        result = service.restore_state(
            campaign_id, modified_data, db_session
        )

        assert result["campaign"] is True
        campaign = (
            db_session.query(CampaignDB)
            .filter(CampaignDB.id == campaign_id)
            .first()
        )
        assert campaign.data["name"] == "Renamed Campaign"
        assert campaign.name == "Renamed Campaign"


class TestRoundTrip:
    def test_capture_restore_capture_is_equivalent(
        self, service, db_session, populated_campaign
    ):
        """A capture-restore-capture round-trip produces equivalent state."""
        cid = populated_campaign["campaign_id"]

        # First capture
        state_1 = service.capture_state(cid, db_session)

        # Restore
        service.restore_state(cid, state_1, db_session)

        # Second capture
        state_2 = service.capture_state(cid, db_session)

        # Compare key data (timestamps will differ)
        assert state_1["campaign_data"] == state_2["campaign_data"]
        assert len(state_1["characters"]) == len(state_2["characters"])
        assert len(state_1["npcs"]) == len(state_2["npcs"])
        assert len(state_1["npc_profiles"]) == len(state_2["npc_profiles"])
        assert len(state_1["npc_relationships"]) == len(state_2["npc_relationships"])

        # Verify character data matches
        for c1, c2 in zip(state_1["characters"], state_2["characters"], strict=True):
            assert c1["id"] == c2["id"]
            assert c1["name"] == c2["name"]
            assert c1["data"] == c2["data"]

        # Verify NPC data matches
        for n1, n2 in zip(state_1["npcs"], state_2["npcs"], strict=True):
            assert n1["id"] == n2["id"]
            assert n1["name"] == n2["name"]


class TestGetSaveSummary:
    def test_summary_returns_human_readable_info(
        self, service, db_session, populated_campaign
    ):
        """Summary includes campaign name, character/NPC counts."""
        cid = populated_campaign["campaign_id"]
        state = service.capture_state(cid, db_session)
        summary = service.get_save_summary(state)

        assert summary["campaign_name"] == "State Test Campaign"
        assert summary["character_count"] == 1
        assert "Thorin Ironforge" in summary["characters"]
        assert summary["npc_count"] == 2  # 1 legacy NPC + 1 profile
        assert summary["current_location"] == "Tavern of Shadows"
        assert summary["has_active_combat"] is False
        assert summary["version"] == 1

    def test_summary_with_empty_state(self, service):
        """Summary for an empty state returns sensible defaults."""
        summary = service.get_save_summary({})

        assert summary["campaign_name"] == "Unknown Campaign"
        assert summary["character_count"] == 0
        assert summary["npc_count"] == 0
        assert summary["conversation_entries"] == 0
        assert summary["has_active_combat"] is False

    def test_summary_includes_npc_names(self, service, db_session, populated_campaign):
        """Summary lists both legacy NPCs and profile NPCs by name."""
        state = service.capture_state(populated_campaign["campaign_id"], db_session)
        summary = service.get_save_summary(state)

        assert "Bartender Bob" in summary["npc_names"]
        assert "Elara the Seer" in summary["npc_names"]


# ---------------------------------------------------------------------------
# API integration tests
# ---------------------------------------------------------------------------


class TestCaptureEndpoint:
    def test_capture_creates_save_slot(self, client, campaign_id):
        """POST /saves/capture creates a save slot with full state."""
        response = client.post(f"/game/campaign/{campaign_id}/saves/capture")
        assert response.status_code == 201
        data = response.json()
        assert data["campaign_id"] == campaign_id
        assert data["slot_number"] == 1
        assert "save_data" in data
        assert data["save_data"]["version"] == 1

    def test_capture_nonexistent_campaign_returns_404(self, client):
        """Capturing state for a non-existent campaign returns 404."""
        response = client.post("/game/campaign/nonexistent/saves/capture")
        assert response.status_code == 404

    def test_capture_respects_max_slots(self, client, campaign_id, db_session):
        """Cannot capture when all 5 slots are occupied."""
        # Fill all 5 slots
        for i in range(1, 6):
            db_session.add(
                SaveSlotDB(
                    id=str(uuid.uuid4()),
                    campaign_id=campaign_id,
                    slot_number=i,
                    name=f"slot {i}",
                    save_data={"version": 1},
                )
            )
        db_session.commit()

        response = client.post(f"/game/campaign/{campaign_id}/saves/capture")
        assert response.status_code == 409


class TestRestoreEndpoint:
    def test_restore_from_save_slot(self, client, campaign_id, db_session):
        """POST /saves/{slot}/restore restores the state."""
        # First capture
        capture_resp = client.post(f"/game/campaign/{campaign_id}/saves/capture")
        assert capture_resp.status_code == 201
        slot_number = capture_resp.json()["slot_number"]

        # Then restore
        response = client.post(
            f"/game/campaign/{campaign_id}/saves/{slot_number}/restore"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "restored"
        assert data["slot_number"] == slot_number
        assert "restored_summary" in data
        assert data["restored_summary"]["campaign"] is True

    def test_restore_nonexistent_slot_returns_404(self, client, campaign_id):
        """Restoring from a non-existent slot returns 404."""
        response = client.post(
            f"/game/campaign/{campaign_id}/saves/99/restore"
        )
        assert response.status_code == 404

    def test_restore_nonexistent_campaign_returns_404(self, client):
        """Restoring for a non-existent campaign returns 404."""
        response = client.post("/game/campaign/no-such/saves/1/restore")
        assert response.status_code == 404

    def test_restore_empty_save_data_returns_400(self, client, campaign_id, db_session):
        """Restoring a slot with no state data returns 400."""
        db_session.add(
            SaveSlotDB(
                id=str(uuid.uuid4()),
                campaign_id=campaign_id,
                slot_number=1,
                name="empty",
                save_data={},
            )
        )
        db_session.commit()

        response = client.post(
            f"/game/campaign/{campaign_id}/saves/1/restore"
        )
        assert response.status_code == 400


class TestSummaryEndpoint:
    def test_get_summary(self, client, campaign_id):
        """GET /saves/{slot}/summary returns a human-readable summary."""
        # First capture
        capture_resp = client.post(f"/game/campaign/{campaign_id}/saves/capture")
        assert capture_resp.status_code == 201
        slot_number = capture_resp.json()["slot_number"]

        response = client.get(
            f"/game/campaign/{campaign_id}/saves/{slot_number}/summary"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["campaign_name"] == "State Test Campaign"
        assert "version" in data
        assert "character_count" in data
        assert "npc_count" in data

    def test_summary_nonexistent_slot_returns_404(self, client, campaign_id):
        """Summary for a non-existent slot returns 404."""
        response = client.get(
            f"/game/campaign/{campaign_id}/saves/99/summary"
        )
        assert response.status_code == 404
