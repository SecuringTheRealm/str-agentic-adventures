"""Tests for auto-save functionality.

Validates:
- Auto-save triggers after N interactions
- Auto-save persists conversation history
- Auto-save doesn't block the response
"""

import asyncio
import contextlib
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.auto_save import (
    _MAX_SNAPSHOTS,
    _extract_character_stats,
    _write_snapshot_to_campaign,
    check_and_schedule_auto_save,
    get_interaction_counter,
    increment_and_get_counter,
    reset_interaction_counter,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _fresh_campaign_id() -> str:
    """Return a unique campaign ID so tests don't share counter state."""
    import uuid

    return f"test-campaign-{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Counter tests
# ---------------------------------------------------------------------------


class TestInteractionCounter:
    def test_counter_starts_at_zero(self):
        cid = _fresh_campaign_id()
        assert get_interaction_counter(cid) == 0

    def test_increment_returns_new_value(self):
        cid = _fresh_campaign_id()
        assert increment_and_get_counter(cid) == 1
        assert increment_and_get_counter(cid) == 2

    def test_reset_counter(self):
        cid = _fresh_campaign_id()
        increment_and_get_counter(cid)
        increment_and_get_counter(cid)
        reset_interaction_counter(cid)
        assert get_interaction_counter(cid) == 0


# ---------------------------------------------------------------------------
# _extract_character_stats
# ---------------------------------------------------------------------------


class TestExtractCharacterStats:
    def test_none_returns_empty(self):
        assert _extract_character_stats(None) == {}

    def test_extracts_basic_fields(self):
        char = {
            "id": "c1",
            "name": "Thorin",
            "level": 5,
            "hit_points": {"current": 30, "maximum": 45},
            "conditions": ["prone"],
        }
        stats = _extract_character_stats(char)
        assert stats["id"] == "c1"
        assert stats["name"] == "Thorin"
        assert stats["level"] == 5
        assert stats["hit_points"] == {"current": 30, "maximum": 45}
        assert stats["conditions"] == ["prone"]
        assert stats["spell_slots"] is None

    def test_extracts_spell_slots(self):
        char = {
            "id": "w1",
            "name": "Gandalf",
            "level": 10,
            "hit_points": None,
            "spellcasting": {"spell_slots": [{"level": 1, "total": 4, "used": 2}]},
        }
        stats = _extract_character_stats(char)
        assert stats["spell_slots"] == [{"level": 1, "total": 4, "used": 2}]


# ---------------------------------------------------------------------------
# check_and_schedule_auto_save – interval triggering
# ---------------------------------------------------------------------------


class TestCheckAndScheduleAutoSave:
    def test_no_save_before_interval(self):
        cid = _fresh_campaign_id()
        interval = 5
        for i in range(1, interval):
            saved, count = check_and_schedule_auto_save(
                campaign_id=cid,
                auto_save_interval=interval,
                conversation_history=[],
                character_data=None,
            )
            assert not saved, f"Should not save at interaction {i}"
            assert count == i

    def test_saves_at_interval(self):
        cid = _fresh_campaign_id()
        interval = 5
        with patch("app.auto_save.asyncio.create_task") as mock_create_task:
            for i in range(1, interval + 1):
                saved, count = check_and_schedule_auto_save(
                    campaign_id=cid,
                    auto_save_interval=interval,
                    conversation_history=[{"role": "user", "content": "hello"}],
                    character_data=None,
                )
            assert saved is True
            assert count == interval
            mock_create_task.assert_called_once()

    def test_saves_every_nth_interaction(self):
        cid = _fresh_campaign_id()
        interval = 3
        save_counts = []
        with patch("app.auto_save.asyncio.create_task"):
            for i in range(1, 10):
                saved, _ = check_and_schedule_auto_save(
                    campaign_id=cid,
                    auto_save_interval=interval,
                    conversation_history=[],
                    character_data=None,
                )
                if saved:
                    save_counts.append(i)
        # Should save at 3, 6, 9
        assert save_counts == [3, 6, 9]

    def test_does_not_save_at_interval_minus_one(self):
        cid = _fresh_campaign_id()
        interval = 5
        with patch("app.auto_save.asyncio.create_task") as mock_create_task:
            for _ in range(interval - 1):
                check_and_schedule_auto_save(
                    campaign_id=cid,
                    auto_save_interval=interval,
                    conversation_history=[],
                    character_data=None,
                )
            mock_create_task.assert_not_called()


# ---------------------------------------------------------------------------
# _write_snapshot_to_campaign – DB persistence
# ---------------------------------------------------------------------------


class TestWriteSnapshotToCampaign:
    @pytest.mark.anyio
    async def test_saves_snapshot_to_session_log(self):
        """Auto-save appends a snapshot to the campaign's session_log."""
        from app.models.game_models import Campaign

        mock_campaign = Campaign(
            id="camp1",
            name="Test",
            setting="fantasy",
            session_log=[],
        )

        mock_service = MagicMock()
        mock_service.get_campaign.return_value = mock_campaign
        mock_service.update_campaign.return_value = mock_campaign

        snapshot = {
            "type": "auto_save",
            "timestamp": datetime.now(UTC).isoformat(),
            "interaction_count": 5,
            "conversation_history": [{"role": "user", "content": "I enter the tavern."}],
            "character_snapshot": {},
            "campaign_metadata": {"session_interactions": 5},
        }

        with patch("app.auto_save.campaign_service", mock_service):
            await _write_snapshot_to_campaign("camp1", snapshot)

        mock_service.update_campaign.assert_called_once()
        call_args = mock_service.update_campaign.call_args
        assert call_args[0][0] == "camp1"
        session_log = call_args[0][1]["session_log"]
        assert len(session_log) == 1
        assert session_log[0]["type"] == "auto_save"
        assert session_log[0]["interaction_count"] == 5

    @pytest.mark.anyio
    async def test_persists_conversation_history(self):
        """Conversation history is stored in the snapshot."""
        from app.models.game_models import Campaign

        history = [
            {"role": "user", "content": "I attack the goblin!"},
            {"role": "assistant", "content": "The goblin stumbles back."},
        ]

        mock_campaign = Campaign(id="c2", name="T", setting="f", session_log=[])
        mock_service = MagicMock()
        mock_service.get_campaign.return_value = mock_campaign
        mock_service.update_campaign.return_value = mock_campaign

        snapshot = {
            "type": "auto_save",
            "timestamp": datetime.now(UTC).isoformat(),
            "interaction_count": 5,
            "conversation_history": history,
            "character_snapshot": {},
            "campaign_metadata": {},
        }

        with patch("app.auto_save.campaign_service", mock_service):
            await _write_snapshot_to_campaign("c2", snapshot)

        saved_log = mock_service.update_campaign.call_args[0][1]["session_log"]
        assert saved_log[0]["conversation_history"] == history

    @pytest.mark.anyio
    async def test_campaign_not_found_does_not_raise(self):
        """If the campaign doesn't exist, _write_snapshot_to_campaign should not raise."""
        mock_service = MagicMock()
        mock_service.get_campaign.return_value = None

        snapshot = {"type": "auto_save", "interaction_count": 5}
        with patch("app.auto_save.campaign_service", mock_service):
            # Should complete without error
            await _write_snapshot_to_campaign("nonexistent", snapshot)

        mock_service.update_campaign.assert_not_called()

    @pytest.mark.anyio
    async def test_trims_old_snapshots(self):
        """Old auto-save snapshots are trimmed to _MAX_SNAPSHOTS."""
        from app.models.game_models import Campaign

        old_snapshots = [
            {"type": "auto_save", "interaction_count": i}
            for i in range(_MAX_SNAPSHOTS)
        ]
        mock_campaign = Campaign(
            id="c3", name="T", setting="f", session_log=old_snapshots
        )
        mock_service = MagicMock()
        mock_service.get_campaign.return_value = mock_campaign
        mock_service.update_campaign.return_value = mock_campaign

        new_snapshot = {
            "type": "auto_save",
            "timestamp": datetime.now(UTC).isoformat(),
            "interaction_count": _MAX_SNAPSHOTS,
            "conversation_history": [],
            "character_snapshot": {},
            "campaign_metadata": {},
        }

        with patch("app.auto_save.campaign_service", mock_service):
            await _write_snapshot_to_campaign("c3", new_snapshot)

        saved_log = mock_service.update_campaign.call_args[0][1]["session_log"]
        auto_saves = [e for e in saved_log if e.get("type") == "auto_save"]
        assert len(auto_saves) <= _MAX_SNAPSHOTS


# ---------------------------------------------------------------------------
# Integration: process_player_input endpoint sets auto_saved flag
# ---------------------------------------------------------------------------


class TestProcessPlayerInputAutoSave:
    """Integration-level tests via the FastAPI test client."""

    def _make_client(self):
        from app.main import app
        from fastapi.testclient import TestClient

        return TestClient(app)

    def test_auto_saved_flag_in_response_at_interval(self):
        """After AUTO_SAVE_INTERVAL interactions the response contains auto_saved."""
        from app.auto_save import reset_interaction_counter
        from app.config import Settings, set_settings

        campaign_id = _fresh_campaign_id()
        reset_interaction_counter(campaign_id)

        # Use interval=2 so we only need 2 requests
        test_settings = Settings(
            auto_save_interval=2,
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_chat_deployment="",
            azure_openai_embedding_deployment="",
        )
        set_settings(test_settings)

        try:
            client = self._make_client()

            mock_dm_response = {
                "message": "The dungeon awaits.",
                "visuals": [],
                "state_updates": {},
                "combat_updates": None,
            }

            with (
                patch(
                    "app.api.game_routes.get_dungeon_master"
                ) as mock_get_dm,
                patch("app.auto_save._write_snapshot_to_campaign", new_callable=AsyncMock),
            ):
                mock_dm = MagicMock()
                mock_dm.process_input = AsyncMock(return_value=mock_dm_response)
                mock_dm._threads = {campaign_id: []}
                mock_get_dm.return_value = mock_dm

                payload = {
                    "message": "I look around",
                    "character_id": "char-1",
                    "campaign_id": campaign_id,
                }

                # First call – not yet at interval
                r1 = client.post("/game/input", json=payload)
                assert r1.status_code == 200
                assert not r1.json()["state_updates"].get("auto_saved")

                # Second call – hits the interval
                r2 = client.post("/game/input", json=payload)
                assert r2.status_code == 200
                state = r2.json()["state_updates"]
                assert state.get("auto_saved") is True
                assert "last_auto_save" in state
        finally:
            reset_interaction_counter(campaign_id)
            # Restore default settings
            from app.config import init_settings

            try:
                init_settings()
            except Exception:
                pass

    def test_response_is_not_blocked_by_auto_save(self):
        """The response returns immediately; DB write is background-tasked."""
        from app.auto_save import reset_interaction_counter
        from app.config import Settings, set_settings

        campaign_id = _fresh_campaign_id()
        reset_interaction_counter(campaign_id)

        test_settings = Settings(
            auto_save_interval=1,  # Save on every interaction
            azure_openai_endpoint="",
            azure_openai_api_key="",
            azure_openai_chat_deployment="",
            azure_openai_embedding_deployment="",
        )
        set_settings(test_settings)

        try:
            client = self._make_client()

            mock_dm_response = {
                "message": "The dragon roars.",
                "visuals": [],
                "state_updates": {},
                "combat_updates": None,
            }

            # Simulate a slow DB write that would block if awaited
            async def slow_write(*args, **kwargs):
                await asyncio.sleep(10)

            with (
                patch("app.api.game_routes.get_dungeon_master") as mock_get_dm,
                patch(
                    "app.auto_save._write_snapshot_to_campaign",
                    side_effect=slow_write,
                ),
            ):
                mock_dm = MagicMock()
                mock_dm.process_input = AsyncMock(return_value=mock_dm_response)
                mock_dm._threads = {campaign_id: []}
                mock_get_dm.return_value = mock_dm

                import time

                start = time.monotonic()
                response = client.post(
                    "/game/input",
                    json={
                        "message": "I charge!",
                        "character_id": "char-1",
                        "campaign_id": campaign_id,
                    },
                )
                elapsed = time.monotonic() - start

            # Response must be well under the 10-second sleep
            assert response.status_code == 200
            assert elapsed < 5.0, f"Response took {elapsed:.2f}s – auto-save is blocking"
        finally:
            reset_interaction_counter(campaign_id)
            from app.config import init_settings

            try:
                init_settings()
            except Exception:
                pass
