"""Tests for rest endpoint character update call."""

from unittest.mock import AsyncMock, patch

import pytest
from app.models.game_models import (
    Abilities,
    CharacterSheet,
    HitPoints,
)


@pytest.mark.asyncio
async def test_rest_endpoint_calls_update_with_character_id_and_data():
    """update_character must be called with (character_id, updates) not just (character)."""
    from app.api.routes.rest_routes import router
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(router, prefix="/game")

    # Build a real CharacterSheet so calculate_long_rest works
    character = CharacterSheet(
        id="char_123",
        name="TestHero",
        race="human",
        character_class="fighter",
        level=1,
        hit_points=HitPoints(current=5, maximum=10),
        hit_dice="1d10",
        hit_dice_remaining=1,
        abilities=Abilities(
            strength=10,
            dexterity=10,
            constitution=14,
            intelligence=10,
            wisdom=10,
            charisma=10,
        ),
    )

    mock_scribe = AsyncMock()
    mock_scribe.get_character = AsyncMock(return_value=character)
    mock_scribe.update_character = AsyncMock(return_value={"success": True})

    with patch(
        "app.agents.scribe_agent.get_scribe", return_value=mock_scribe
    ):
        client = TestClient(app)
        client.post(
            "/game/game/rest",
            json={
                "character_id": "char_123",
                "rest_type": "long",
            },
        )

    # Verify update_character was called with character_id AND updates dict
    assert mock_scribe.update_character.called, "update_character was not called"
    args = mock_scribe.update_character.call_args[0]
    assert len(args) == 2, (
        f"update_character should take 2 positional args, got {len(args)}"
    )
    assert args[0] == "char_123", "First arg should be character_id"
