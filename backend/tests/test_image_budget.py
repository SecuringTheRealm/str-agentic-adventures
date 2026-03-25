"""
Tests for the per-session image-generation budget tracker and enforcement.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Unit tests – ImageBudgetTracker
# ---------------------------------------------------------------------------


class TestImageBudgetTracker:
    """Unit tests for the ImageBudgetTracker class."""

    def test_first_request_is_allowed(self) -> None:
        """First request within a fresh session should always be allowed."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=3, window_minutes=30)
        allowed, remaining = tracker.check_and_record("sess-a")
        assert allowed is True
        assert remaining == 2  # 3 max - 1 used = 2 remaining

    def test_requests_up_to_max_are_allowed(self) -> None:
        """All requests up to max_images should succeed."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=3, window_minutes=30)
        for expected_remaining in (2, 1, 0):
            allowed, remaining = tracker.check_and_record("sess-b")
            assert allowed is True
            assert remaining == expected_remaining

    def test_request_exceeding_max_is_blocked(self) -> None:
        """The (max + 1)-th request must be rejected."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=2, window_minutes=30)
        tracker.check_and_record("sess-c")
        tracker.check_and_record("sess-c")
        allowed, remaining = tracker.check_and_record("sess-c")
        assert allowed is False
        assert remaining == 0

    def test_sessions_are_isolated(self) -> None:
        """Different session IDs must not share budget."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=1, window_minutes=30)
        tracker.check_and_record("sess-x")
        # sess-x is now exhausted; sess-y should still be allowed
        allowed, _ = tracker.check_and_record("sess-y")
        assert allowed is True

    def test_get_remaining_matches_check_and_record(self) -> None:
        """get_remaining should reflect recorded images correctly."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=3, window_minutes=30)
        assert tracker.get_remaining("sess-r") == 3
        tracker.check_and_record("sess-r")
        assert tracker.get_remaining("sess-r") == 2

    def test_window_expiry_resets_budget(self) -> None:
        """Timestamps outside the rolling window must not count toward the budget."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=1, window_minutes=0)  # 0-min window
        # Record an image – window is 0 minutes so it expires immediately
        tracker.check_and_record("sess-w")
        # Give the window a moment to expire
        time.sleep(0.01)
        # A fresh check should now allow another image
        allowed, _ = tracker.check_and_record("sess-w")
        assert allowed is True

    def test_max_images_zero_blocks_all_requests(self) -> None:
        """Setting max_images=0 should block every request."""
        from app.image_budget import ImageBudgetTracker

        tracker = ImageBudgetTracker(max_images=0, window_minutes=30)
        allowed, remaining = tracker.check_and_record("sess-z")
        assert allowed is False
        assert remaining == 0


# ---------------------------------------------------------------------------
# Integration tests – /generate-image and /battle-map endpoints
# ---------------------------------------------------------------------------

_MOCK_IMAGE_RESULT = {
    "success": True,
    "image_url": "https://example.com/img.png",
    "revised_prompt": "test",
    "size": "1024x1024",
    "quality": "standard",
    "style": "vivid",
}

_MOCK_MAP_RESULT = {
    "id": "map_1",
    "success": True,
    "image_url": "https://example.com/map.png",
    "name": "Test Map",
}


class TestImageBudgetEndpoints:
    """Integration tests that verify budget enforcement in the API routes."""

    def _make_client_and_reset_budget(self, max_images: int = 3) -> TestClient:
        """Return a TestClient and reset the module-level budget tracker."""
        from app.api.routes import _shared
        from app.image_budget import ImageBudgetTracker
        from app.main import app

        _shared._image_budget = ImageBudgetTracker(
            max_images=max_images, window_minutes=30
        )
        return TestClient(app)

    def test_generate_image_succeeds_within_budget(self) -> None:
        """A request within budget must return 200."""
        client = self._make_client_and_reset_budget(max_images=3)
        artist_mock = AsyncMock(return_value=_MOCK_IMAGE_RESULT)
        with patch(
            "app.api.routes.ai_routes.get_artist"
        ) as mock_get_artist:
            mock_get_artist.return_value.generate_character_portrait = artist_mock
            response = client.post(
                "/game/generate-image",
                json={
                    "session_id": "test-session",
                    "image_type": "character_portrait",
                    "details": {"name": "Hero"},
                },
            )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "images_remaining" in data
        assert data["images_remaining"] == 2

    def test_generate_image_blocked_when_budget_exhausted(self) -> None:
        """Requests over the budget must receive HTTP 429."""
        client = self._make_client_and_reset_budget(max_images=1)
        artist_mock = AsyncMock(return_value=_MOCK_IMAGE_RESULT)
        with patch(
            "app.api.routes.ai_routes.get_artist"
        ) as mock_get_artist:
            mock_get_artist.return_value.generate_character_portrait = artist_mock
            # Use up the single allowed image
            client.post(
                "/game/generate-image",
                json={
                    "session_id": "budget-test",
                    "image_type": "character_portrait",
                    "details": {},
                },
            )
            # Second request must be rejected
            response = client.post(
                "/game/generate-image",
                json={
                    "session_id": "budget-test",
                    "image_type": "character_portrait",
                    "details": {},
                },
            )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "budget" in response.json()["detail"].lower()

    def test_battle_map_blocked_when_budget_exhausted(self) -> None:
        """Battle map requests share the same budget and must also be blocked."""
        client = self._make_client_and_reset_budget(max_images=1)
        map_mock = AsyncMock(return_value=_MOCK_MAP_RESULT)
        with patch(
            "app.api.routes.ai_routes.get_combat_cartographer"
        ) as mock_cart:
            mock_cart.return_value.generate_battle_map = map_mock
            # Use up the budget
            client.post(
                "/game/battle-map",
                json={
                    "session_id": "map-budget-test",
                    "environment": {"location": "dungeon"},
                },
            )
            # Second request must be rejected
            response = client.post(
                "/game/battle-map",
                json={
                    "session_id": "map-budget-test",
                    "environment": {"location": "dungeon"},
                },
            )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_different_sessions_do_not_share_budget(self) -> None:
        """Two different session IDs must each have their own budget."""
        client = self._make_client_and_reset_budget(max_images=1)
        artist_mock = AsyncMock(return_value=_MOCK_IMAGE_RESULT)
        with patch(
            "app.api.routes.ai_routes.get_artist"
        ) as mock_get_artist:
            mock_get_artist.return_value.generate_character_portrait = artist_mock
            # Exhaust session A
            client.post(
                "/game/generate-image",
                json={
                    "session_id": "session-a",
                    "image_type": "character_portrait",
                    "details": {},
                },
            )
            # Session B should still succeed
            response = client.post(
                "/game/generate-image",
                json={
                    "session_id": "session-b",
                    "image_type": "character_portrait",
                    "details": {},
                },
            )
        assert response.status_code == status.HTTP_200_OK

    def test_anonymous_session_uses_shared_budget(self) -> None:
        """Requests without a session_id fall into the 'anonymous' bucket."""
        client = self._make_client_and_reset_budget(max_images=1)
        artist_mock = AsyncMock(return_value=_MOCK_IMAGE_RESULT)
        with patch(
            "app.api.routes.ai_routes.get_artist"
        ) as mock_get_artist:
            mock_get_artist.return_value.generate_character_portrait = artist_mock
            client.post(
                "/game/generate-image",
                json={"image_type": "character_portrait", "details": {}},
            )
            response = client.post(
                "/game/generate-image",
                json={"image_type": "character_portrait", "details": {}},
            )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
