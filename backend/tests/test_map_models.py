"""
Tests for battle map Pydantic models.
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.map_models import (
    BattleMapData,
    MapEffect,
    MapEntity,
    MapTile,
    MapToken,
    TeamType,
    TerrainType,
)


class TestTerrainType:
    """Tests for the TerrainType enum."""

    def test_terrain_type_values(self) -> None:
        """TerrainType enum has the correct string values."""
        assert TerrainType.STONE_FLOOR == "stone_floor"
        assert TerrainType.WOODEN_FLOOR == "wooden_floor"
        assert TerrainType.GRASS == "grass"
        assert TerrainType.DIRT == "dirt"
        assert TerrainType.WATER == "water"
        assert TerrainType.LAVA == "lava"
        assert TerrainType.WALL == "wall"
        assert TerrainType.DOOR == "door"
        assert TerrainType.STAIRS == "stairs"

    def test_terrain_type_is_str(self) -> None:
        """TerrainType values are strings."""
        assert isinstance(TerrainType.STONE_FLOOR, str)


class TestTeamType:
    """Tests for the TeamType enum."""

    def test_team_type_values(self) -> None:
        """TeamType enum has the correct string values."""
        assert TeamType.PLAYER == "player"
        assert TeamType.ENEMY == "enemy"
        assert TeamType.NEUTRAL == "neutral"

    def test_team_type_is_str(self) -> None:
        """TeamType values are strings."""
        assert isinstance(TeamType.PLAYER, str)


class TestMapTile:
    """Tests for MapTile model."""

    def test_map_tile_defaults(self) -> None:
        """MapTile can be created with defaults."""
        tile = MapTile()
        assert tile.type == TerrainType.STONE_FLOOR
        assert tile.passable is True
        assert tile.elevation == 0

    def test_map_tile_custom_values(self) -> None:
        """MapTile accepts custom terrain type and passability."""
        tile = MapTile(type=TerrainType.WALL, passable=False, elevation=1)
        assert tile.type == TerrainType.WALL
        assert tile.passable is False
        assert tile.elevation == 1


class TestMapEntity:
    """Tests for MapEntity model."""

    def test_map_entity_serialises_correctly(self) -> None:
        """MapEntity serialises to the expected dict."""
        entity = MapEntity(id="e1", type="pillar", x=3, y=5)
        data = entity.model_dump()
        assert data["id"] == "e1"
        assert data["type"] == "pillar"
        assert data["x"] == 3
        assert data["y"] == 5
        assert data["blocks_los"] is False
        assert data["blocks_movement"] is False

    def test_map_entity_blocking_flags(self) -> None:
        """MapEntity can set blocking flags."""
        entity = MapEntity(
            id="e2",
            type="wall_section",
            x=0,
            y=0,
            blocks_los=True,
            blocks_movement=True,
        )
        assert entity.blocks_los is True
        assert entity.blocks_movement is True


class TestMapToken:
    """Tests for MapToken model."""

    def test_map_token_serialises_correctly(self) -> None:
        """MapToken serialises with all fields including optional hp."""
        token = MapToken(
            id="t1", name="Hero", x=2, y=4, team=TeamType.PLAYER, hp=30, max_hp=40
        )
        data = token.model_dump()
        assert data["id"] == "t1"
        assert data["name"] == "Hero"
        assert data["x"] == 2
        assert data["y"] == 4
        assert data["team"] == "player"
        assert data["hp"] == 30
        assert data["max_hp"] == 40

    def test_map_token_defaults(self) -> None:
        """MapToken defaults team to neutral and hp to None."""
        token = MapToken(id="t2", name="Bystander", x=0, y=0)
        assert token.team == TeamType.NEUTRAL
        assert token.hp is None
        assert token.max_hp is None


class TestBattleMapData:
    """Tests for BattleMapData model."""

    def test_battle_map_data_defaults(self) -> None:
        """BattleMapData can be created with defaults."""
        bm = BattleMapData()
        assert bm.width == 20
        assert bm.height == 20
        assert bm.tile_size == 64
        assert bm.tiles == []
        assert bm.entities == []
        assert bm.tokens == []
        assert bm.effects == []
        assert bm.fog_of_war is True
        assert bm.ambient_image_url is None
        assert bm.id  # auto-generated UUID string

    def test_battle_map_data_id_is_unique(self) -> None:
        """Each BattleMapData instance gets a unique id."""
        bm1 = BattleMapData()
        bm2 = BattleMapData()
        assert bm1.id != bm2.id

    def test_battle_map_tiles_grid(self) -> None:
        """Tiles grid can be populated with MapTile objects."""
        row = [MapTile(type=TerrainType.GRASS), MapTile(type=TerrainType.WATER)]
        bm = BattleMapData(tiles=[row])
        assert len(bm.tiles) == 1
        assert len(bm.tiles[0]) == 2
        assert bm.tiles[0][0].type == TerrainType.GRASS
        assert bm.tiles[0][1].type == TerrainType.WATER

    def test_battle_map_with_entities(self) -> None:
        """BattleMapData serialises entities correctly."""
        entity = MapEntity(id="barrel1", type="barrel", x=1, y=2)
        bm = BattleMapData(entities=[entity])
        data = bm.model_dump()
        assert len(data["entities"]) == 1
        assert data["entities"][0]["type"] == "barrel"

    def test_battle_map_with_tokens(self) -> None:
        """BattleMapData serialises tokens correctly."""
        token = MapToken(id="goblin1", name="Goblin", x=5, y=5, team="enemy")
        bm = BattleMapData(tokens=[token])
        data = bm.model_dump()
        assert len(data["tokens"]) == 1
        assert data["tokens"][0]["name"] == "Goblin"
        assert data["tokens"][0]["team"] == "enemy"

    def test_battle_map_with_effects(self) -> None:
        """BattleMapData serialises effects correctly."""
        effect = MapEffect(
            type="aoe_circle", origin_x=3, origin_y=3, radius=2, colour="blue"
        )
        bm = BattleMapData(effects=[effect])
        data = bm.model_dump()
        assert len(data["effects"]) == 1
        assert data["effects"][0]["type"] == "aoe_circle"
        assert data["effects"][0]["radius"] == 2
        assert data["effects"][0]["colour"] == "blue"

    def test_battle_map_ambient_image_url(self) -> None:
        """BattleMapData accepts an ambient_image_url."""
        bm = BattleMapData(ambient_image_url="https://example.com/map.png")
        assert bm.ambient_image_url == "https://example.com/map.png"


class TestMapEffect:
    """Tests for MapEffect model."""

    def test_map_effect_direction_valid(self) -> None:
        """MapEffect accepts direction values in the 0-359 range."""
        effect = MapEffect(type="aoe_cone", origin_x=0, origin_y=0, direction=90)
        assert effect.direction == 90

    def test_map_effect_direction_invalid(self) -> None:
        """MapEffect rejects direction values outside 0-359."""
        import pytest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            MapEffect(type="aoe_cone", origin_x=0, origin_y=0, direction=360)

        with pytest.raises(ValidationError):
            MapEffect(type="aoe_cone", origin_x=0, origin_y=0, direction=-1)

    def test_map_effect_direction_none_allowed(self) -> None:
        """MapEffect allows direction to be None."""
        effect = MapEffect(type="aoe_circle", origin_x=0, origin_y=0)
        assert effect.direction is None
