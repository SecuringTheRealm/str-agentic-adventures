"""Tests for the BSP tile grid generator."""

from app.models.map_models import BattleMapData, MapTile, TerrainType
from app.services.tile_grid_generator import TileGridGenerator


def _make_grid(
    width: int = 20,
    height: int = 20,
    terrain: str = "dungeon",
    features: list[str] | None = None,
    hazards: list[str] | None = None,
    seed: int = 42,
) -> BattleMapData:
    gen = TileGridGenerator()
    return gen.generate_grid(
        width=width,
        height=height,
        environment_context={
            "terrain": terrain,
            "features": features or [],
            "hazards": hazards or [],
        },
        seed=seed,
    )


class TestGridDimensions:
    """Grid generation produces correct dimensions."""

    def test_default_20x20(self) -> None:
        data = _make_grid(20, 20)
        assert data.width == 20
        assert data.height == 20
        assert len(data.tiles) == 20
        assert all(len(row) == 20 for row in data.tiles)

    def test_small_15x15(self) -> None:
        data = _make_grid(15, 15)
        assert data.width == 15
        assert data.height == 15
        assert len(data.tiles) == 15

    def test_large_30x30(self) -> None:
        data = _make_grid(30, 30)
        assert data.width == 30
        assert data.height == 30
        assert len(data.tiles) == 30


class TestTilePopulation:
    """All tiles are populated with valid TerrainType values."""

    def test_all_tiles_have_valid_type(self) -> None:
        data = _make_grid()
        valid_types = set(TerrainType)
        for row in data.tiles:
            for tile in row:
                assert isinstance(tile, MapTile)
                assert tile.type in valid_types

    def test_no_empty_rows(self) -> None:
        data = _make_grid()
        for row in data.tiles:
            assert len(row) > 0

    def test_passable_matches_type(self) -> None:
        data = _make_grid()
        for row in data.tiles:
            for tile in row:
                if tile.type in (TerrainType.WALL, TerrainType.LAVA):
                    assert not tile.passable


class TestWallBoundaries:
    """Walls form boundaries around the map edges."""

    def test_top_row_is_walls(self) -> None:
        data = _make_grid()
        for tile in data.tiles[0]:
            assert tile.type == TerrainType.WALL

    def test_bottom_row_is_walls(self) -> None:
        data = _make_grid()
        for tile in data.tiles[-1]:
            assert tile.type == TerrainType.WALL

    def test_left_column_is_walls(self) -> None:
        data = _make_grid()
        for row in data.tiles:
            assert row[0].type == TerrainType.WALL

    def test_right_column_is_walls(self) -> None:
        data = _make_grid()
        for row in data.tiles:
            assert row[-1].type == TerrainType.WALL


class TestDoorPlacement:
    """Doors are placed on the grid."""

    def test_doors_exist(self) -> None:
        data = _make_grid(seed=42)
        door_count = sum(
            1 for row in data.tiles for tile in row if tile.type == TerrainType.DOOR
        )
        assert door_count > 0

    def test_doors_are_passable(self) -> None:
        data = _make_grid()
        for row in data.tiles:
            for tile in row:
                if tile.type == TerrainType.DOOR:
                    assert tile.passable


class TestEntityPlacement:
    """Entity placement doesn't overlap walls."""

    def test_entities_not_on_walls(self) -> None:
        data = _make_grid(features=["pillars", "barrels", "chest"])
        for entity in data.entities:
            tile = data.tiles[entity.y][entity.x]
            assert tile.type != TerrainType.WALL, (
                f"Entity {entity.type} at ({entity.x}, {entity.y}) overlaps a wall"
            )

    def test_entities_on_passable_tiles(self) -> None:
        data = _make_grid(features=["tables", "crates"])
        for entity in data.entities:
            tile = data.tiles[entity.y][entity.x]
            assert tile.passable

    def test_no_duplicate_positions(self) -> None:
        data = _make_grid(features=["pillars", "barrels", "chest", "crates"])
        positions = [(e.x, e.y) for e in data.entities]
        assert len(positions) == len(set(positions))


class TestEnvironmentContextVariation:
    """Different environment contexts produce different results."""

    def test_dungeon_uses_stone(self) -> None:
        data = _make_grid(terrain="dungeon")
        floor_types = {
            tile.type for row in data.tiles for tile in row if tile.passable
        }
        assert TerrainType.STONE_FLOOR in floor_types

    def test_forest_uses_grass(self) -> None:
        data = _make_grid(terrain="forest")
        floor_types = {
            tile.type for row in data.tiles for tile in row if tile.passable
        }
        assert TerrainType.GRASS in floor_types

    def test_tavern_uses_wooden_floor(self) -> None:
        data = _make_grid(terrain="tavern")
        floor_types = {
            tile.type for row in data.tiles for tile in row if tile.passable
        }
        assert TerrainType.WOODEN_FLOOR in floor_types

    def test_cave_uses_stone_and_dirt(self) -> None:
        data = _make_grid(terrain="cave")
        floor_types = {
            tile.type for row in data.tiles for tile in row if tile.passable
        }
        # Cave rooms use stone, corridors use dirt
        assert TerrainType.STONE_FLOOR in floor_types or TerrainType.DIRT in floor_types

    def test_different_terrains_differ(self) -> None:
        dungeon = _make_grid(terrain="dungeon", seed=1)
        forest = _make_grid(terrain="forest", seed=1)
        # With same seed but different terrain, floor types should differ
        dungeon_floors = {
            tile.type
            for row in dungeon.tiles
            for tile in row
            if tile.passable and tile.type != TerrainType.DOOR
        }
        forest_floors = {
            tile.type
            for row in forest.tiles
            for tile in row
            if tile.passable and tile.type != TerrainType.DOOR
        }
        assert dungeon_floors != forest_floors


class TestHazardPlacement:
    """Hazards are placed correctly."""

    def test_water_hazard(self) -> None:
        data = _make_grid(hazards=["water"], seed=7)
        water_count = sum(
            1 for row in data.tiles for tile in row if tile.type == TerrainType.WATER
        )
        assert water_count > 0

    def test_lava_is_impassable(self) -> None:
        data = _make_grid(hazards=["lava"], seed=7)
        for row in data.tiles:
            for tile in row:
                if tile.type == TerrainType.LAVA:
                    assert not tile.passable


class TestDeterminism:
    """Same seed produces identical maps."""

    def test_same_seed_same_result(self) -> None:
        a = _make_grid(seed=123)
        b = _make_grid(seed=123)
        assert a.tiles == b.tiles
        assert len(a.entities) == len(b.entities)
        assert len(a.tokens) == len(b.tokens)

    def test_different_seed_different_result(self) -> None:
        a = _make_grid(seed=1)
        b = _make_grid(seed=2)
        # Tile layout should differ
        a_flat = [(t.type, t.passable) for row in a.tiles for t in row]
        b_flat = [(t.type, t.passable) for row in b.tiles for t in row]
        assert a_flat != b_flat


class TestTokenSpawnPlacement:
    """Spawn tokens are placed correctly."""

    def test_player_tokens_exist(self) -> None:
        data = _make_grid()
        player_tokens = [t for t in data.tokens if t.team == "player"]
        assert len(player_tokens) == 4

    def test_enemy_tokens_exist(self) -> None:
        data = _make_grid()
        enemy_tokens = [t for t in data.tokens if t.team == "enemy"]
        assert len(enemy_tokens) == 3

    def test_tokens_have_unique_ids(self) -> None:
        data = _make_grid()
        ids = [t.id for t in data.tokens]
        assert len(ids) == len(set(ids))


class TestSpawnPoints:
    """spawn_points field is populated from BSP rooms."""

    def test_spawn_points_not_empty(self) -> None:
        data = _make_grid()
        assert len(data.spawn_points) > 0

    def test_player_spawn_points(self) -> None:
        data = _make_grid()
        player_spawns = [sp for sp in data.spawn_points if sp.team == "player"]
        assert len(player_spawns) == 4

    def test_enemy_spawn_points(self) -> None:
        data = _make_grid()
        enemy_spawns = [sp for sp in data.spawn_points if sp.team == "enemy"]
        assert len(enemy_spawns) == 3

    def test_spawn_points_deterministic(self) -> None:
        a = _make_grid(seed=42)
        b = _make_grid(seed=42)
        assert len(a.spawn_points) == len(b.spawn_points)
        for sp_a, sp_b in zip(a.spawn_points, b.spawn_points, strict=True):
            assert sp_a.x == sp_b.x
            assert sp_a.y == sp_b.y
            assert sp_a.team == sp_b.team
