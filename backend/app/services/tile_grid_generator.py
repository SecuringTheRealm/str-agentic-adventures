"""
Procedural tile grid generator using Binary Space Partitioning (BSP).

Generates dungeon-like battle maps with rooms, corridors, doors, and
environment-appropriate terrain for D&D combat encounters.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from uuid import uuid4

from app.models.map_models import (
    BattleMapData,
    MapEntity,
    MapTile,
    MapToken,
    SpawnPoint,
    TeamType,
    TerrainType,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# BSP helpers
# ---------------------------------------------------------------------------

MIN_ROOM_SIZE = 4
SPLIT_RATIO_MIN = 0.35
SPLIT_RATIO_MAX = 0.65


@dataclass
class Rect:
    """Axis-aligned rectangle used during BSP subdivision."""

    x: int
    y: int
    w: int
    h: int

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2


@dataclass
class BSPNode:
    """A node in the BSP tree.  Leaves hold rooms; internal nodes hold splits."""

    rect: Rect
    left: BSPNode | None = None
    right: BSPNode | None = None
    room: Rect | None = None


# ---------------------------------------------------------------------------
# Environment presets
# ---------------------------------------------------------------------------

_FLOOR_MAP: dict[str, TerrainType] = {
    "dungeon": TerrainType.STONE_FLOOR,
    "cave": TerrainType.STONE_FLOOR,
    "forest": TerrainType.GRASS,
    "tavern": TerrainType.WOODEN_FLOOR,
    "castle": TerrainType.STONE_FLOOR,
    "sewer": TerrainType.STONE_FLOOR,
    "temple": TerrainType.STONE_FLOOR,
}

_SECONDARY_FLOOR: dict[str, TerrainType] = {
    "dungeon": TerrainType.DIRT,
    "cave": TerrainType.DIRT,
    "forest": TerrainType.DIRT,
    "tavern": TerrainType.STONE_FLOOR,
    "castle": TerrainType.STONE_FLOOR,
    "sewer": TerrainType.WATER,
    "temple": TerrainType.STONE_FLOOR,
}


def _floor_for_terrain(terrain: str) -> TerrainType:
    return _FLOOR_MAP.get(terrain.lower(), TerrainType.STONE_FLOOR)


def _secondary_floor_for_terrain(terrain: str) -> TerrainType:
    return _SECONDARY_FLOOR.get(terrain.lower(), TerrainType.DIRT)


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------


class TileGridGenerator:
    """Generates a populated ``BattleMapData`` tile grid via BSP."""

    def generate_grid(
        self,
        width: int,
        height: int,
        environment_context: dict,
        seed: int | None = None,
    ) -> BattleMapData:
        """Generate a full ``BattleMapData`` with tiles, entities, and spawn tokens.

        Parameters
        ----------
        width, height:
            Grid dimensions in tiles.
        environment_context:
            Dict with optional keys: ``location``, ``terrain``, ``features``,
            ``hazards``.
        seed:
            Optional RNG seed for deterministic generation.
        """
        rng = random.Random(seed)  # noqa: S311
        terrain = str(environment_context.get("terrain", "dungeon")).lower()
        features: list[str] = environment_context.get("features", [])
        hazards: list[str] = environment_context.get("hazards", [])

        floor = _floor_for_terrain(terrain)
        corridor_floor = _secondary_floor_for_terrain(terrain)

        # 1. Initialise all tiles as walls
        tiles: list[list[MapTile]] = [
            [MapTile(type=TerrainType.WALL, passable=False) for _ in range(width)]
            for _ in range(height)
        ]

        # 2. BSP split & carve rooms
        root = BSPNode(rect=Rect(1, 1, width - 2, height - 2))
        self._split(root, rng)
        rooms: list[Rect] = []
        self._create_rooms(root, rng, rooms)

        for room in rooms:
            for ry in range(room.y, room.y + room.h):
                for rx in range(room.x, room.x + room.w):
                    if 0 <= ry < height and 0 <= rx < width:
                        tiles[ry][rx] = MapTile(type=floor, passable=True)

        # 3. Connect rooms with corridors & place doors
        door_positions: list[tuple[int, int]] = []
        self._connect_rooms(
            root, tiles, width, height, corridor_floor, rng, door_positions
        )

        # Place door tiles
        for dx, dy in door_positions:
            if 0 <= dy < height and 0 <= dx < width:
                tiles[dy][dx] = MapTile(type=TerrainType.DOOR, passable=True)

        # 4. Place hazards
        self._place_hazards(tiles, rooms, hazards, rng, width, height)

        # 5. Place entities from features
        entities = self._place_entities(tiles, rooms, features, rng, width, height)

        # 6. Determine spawn tokens (players in first room, enemies in last)
        tokens = self._place_spawn_tokens(rooms)

        # 7. Generate spawn points from BSP rooms
        spawn_points = self._generate_spawn_points(rooms)

        return BattleMapData(
            id=str(uuid4()),
            width=width,
            height=height,
            tiles=tiles,
            entities=entities,
            tokens=tokens,
            spawn_points=spawn_points,
            fog_of_war=True,
        )

    # -----------------------------------------------------------------------
    # BSP splitting
    # -----------------------------------------------------------------------

    def _split(self, node: BSPNode, rng: random.Random, depth: int = 0) -> None:
        if depth > 5:
            return
        rect = node.rect
        can_split_h = rect.h >= MIN_ROOM_SIZE * 2 + 1
        can_split_v = rect.w >= MIN_ROOM_SIZE * 2 + 1

        if not can_split_h and not can_split_v:
            return

        if can_split_h and can_split_v:
            split_h = rng.random() < 0.5
        elif can_split_h:
            split_h = True
        else:
            split_h = False

        if split_h:
            ratio = rng.uniform(SPLIT_RATIO_MIN, SPLIT_RATIO_MAX)
            split = int(rect.h * ratio)
            split = max(split, MIN_ROOM_SIZE)
            split = min(split, rect.h - MIN_ROOM_SIZE)
            node.left = BSPNode(rect=Rect(rect.x, rect.y, rect.w, split))
            node.right = BSPNode(
                rect=Rect(rect.x, rect.y + split, rect.w, rect.h - split)
            )
        else:
            ratio = rng.uniform(SPLIT_RATIO_MIN, SPLIT_RATIO_MAX)
            split = int(rect.w * ratio)
            split = max(split, MIN_ROOM_SIZE)
            split = min(split, rect.w - MIN_ROOM_SIZE)
            node.left = BSPNode(rect=Rect(rect.x, rect.y, split, rect.h))
            node.right = BSPNode(
                rect=Rect(rect.x + split, rect.y, rect.w - split, rect.h)
            )

        self._split(node.left, rng, depth + 1)
        self._split(node.right, rng, depth + 1)

    # -----------------------------------------------------------------------
    # Room creation
    # -----------------------------------------------------------------------

    def _create_rooms(
        self, node: BSPNode, rng: random.Random, rooms: list[Rect]
    ) -> None:
        if node.left is None and node.right is None:
            # Leaf – create a room inside the partition
            rw = rng.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, node.rect.w))
            rh = rng.randint(MIN_ROOM_SIZE, max(MIN_ROOM_SIZE, node.rect.h))
            rx = node.rect.x + rng.randint(0, max(0, node.rect.w - rw))
            ry = node.rect.y + rng.randint(0, max(0, node.rect.h - rh))
            node.room = Rect(rx, ry, rw, rh)
            rooms.append(node.room)
            return

        if node.left:
            self._create_rooms(node.left, rng, rooms)
        if node.right:
            self._create_rooms(node.right, rng, rooms)

    # -----------------------------------------------------------------------
    # Corridor carving
    # -----------------------------------------------------------------------

    def _get_room(self, node: BSPNode) -> Rect | None:
        """Return a room from this subtree (for corridor connection)."""
        if node.room is not None:
            return node.room
        if node.left:
            r = self._get_room(node.left)
            if r:
                return r
        if node.right:
            return self._get_room(node.right)
        return None

    def _connect_rooms(
        self,
        node: BSPNode,
        tiles: list[list[MapTile]],
        width: int,
        height: int,
        corridor_floor: TerrainType,
        rng: random.Random,
        door_positions: list[tuple[int, int]],
    ) -> None:
        if node.left is None or node.right is None:
            return

        self._connect_rooms(
            node.left, tiles, width, height, corridor_floor, rng, door_positions
        )
        self._connect_rooms(
            node.right, tiles, width, height, corridor_floor, rng, door_positions
        )

        room_a = self._get_room(node.left)
        room_b = self._get_room(node.right)
        if room_a is None or room_b is None:
            return

        ax, ay = room_a.cx, room_a.cy
        bx, by = room_b.cx, room_b.cy

        # Carve an L-shaped corridor between the two room centres
        first_horizontal = rng.random() < 0.5
        if first_horizontal:
            door_pos = self._carve_h(tiles, ax, bx, ay, width, height, corridor_floor)
            if door_pos:
                door_positions.append(door_pos)
            door_pos = self._carve_v(tiles, ay, by, bx, width, height, corridor_floor)
            if door_pos:
                door_positions.append(door_pos)
        else:
            door_pos = self._carve_v(tiles, ay, by, ax, width, height, corridor_floor)
            if door_pos:
                door_positions.append(door_pos)
            door_pos = self._carve_h(tiles, ax, bx, by, width, height, corridor_floor)
            if door_pos:
                door_positions.append(door_pos)

    def _carve_h(
        self,
        tiles: list[list[MapTile]],
        x1: int,
        x2: int,
        y: int,
        width: int,
        height: int,
        floor: TerrainType,
    ) -> tuple[int, int] | None:
        """Carve a horizontal corridor.  Returns a door position if one is placed."""
        door: tuple[int, int] | None = None
        lo, hi = min(x1, x2), max(x1, x2)
        for x in range(lo, hi + 1):
            if 0 <= y < height and 0 <= x < width:
                was_wall = tiles[y][x].type == TerrainType.WALL
                tiles[y][x] = MapTile(type=floor, passable=True)
                if was_wall and door is None:
                    # First wall->floor transition is a candidate door
                    door = (x, y)
        return door

    def _carve_v(
        self,
        tiles: list[list[MapTile]],
        y1: int,
        y2: int,
        x: int,
        width: int,
        height: int,
        floor: TerrainType,
    ) -> tuple[int, int] | None:
        """Carve a vertical corridor.  Returns a door position if one is placed."""
        door: tuple[int, int] | None = None
        lo, hi = min(y1, y2), max(y1, y2)
        for y in range(lo, hi + 1):
            if 0 <= y < height and 0 <= x < width:
                was_wall = tiles[y][x].type == TerrainType.WALL
                tiles[y][x] = MapTile(type=floor, passable=True)
                if was_wall and door is None:
                    door = (x, y)
        return door

    # -----------------------------------------------------------------------
    # Hazards
    # -----------------------------------------------------------------------

    def _place_hazards(
        self,
        tiles: list[list[MapTile]],
        rooms: list[Rect],
        hazards: list[str],
        rng: random.Random,
        width: int,
        height: int,
    ) -> None:
        hazard_map: dict[str, TerrainType] = {
            "water": TerrainType.WATER,
            "lava": TerrainType.LAVA,
            "pit": TerrainType.STAIRS,  # closest approximation
        }
        for hazard in hazards:
            terrain_type = hazard_map.get(hazard.lower())
            if terrain_type is None:
                continue
            if not rooms:
                continue
            room = rng.choice(rooms)
            # Place a small patch inside the room
            patch_w = max(1, rng.randint(1, min(3, room.w - 2)))
            patch_h = max(1, rng.randint(1, min(3, room.h - 2)))
            px = room.x + rng.randint(1, max(1, room.w - patch_w - 1))
            py = room.y + rng.randint(1, max(1, room.h - patch_h - 1))
            passable = terrain_type != TerrainType.LAVA
            for dy in range(patch_h):
                for dx in range(patch_w):
                    nx, ny = px + dx, py + dy
                    if 0 <= ny < height and 0 <= nx < width:
                        tiles[ny][nx] = MapTile(
                            type=terrain_type, passable=passable
                        )

    # -----------------------------------------------------------------------
    # Entity placement
    # -----------------------------------------------------------------------

    _ENTITY_TYPES: list[str] = ["pillar", "barrel", "chest", "crate", "table"]

    def _place_entities(
        self,
        tiles: list[list[MapTile]],
        rooms: list[Rect],
        features: list[str],
        rng: random.Random,
        width: int,
        height: int,
    ) -> list[MapEntity]:
        entities: list[MapEntity] = []
        occupied: set[tuple[int, int]] = set()

        # Map feature names to entity types
        feature_entity_map: dict[str, str] = {
            "pillars": "pillar",
            "pillar": "pillar",
            "barrels": "barrel",
            "barrel": "barrel",
            "chest": "chest",
            "chests": "chest",
            "furniture": "table",
            "tables": "table",
            "crates": "crate",
            "crate": "crate",
            "trap": "trap",
            "traps": "trap",
        }

        entity_types_to_place: list[str] = []
        for feat in features:
            mapped = feature_entity_map.get(feat.lower())
            if mapped:
                entity_types_to_place.append(mapped)

        # If no specific features requested, add some default scatter
        if not entity_types_to_place:
            entity_types_to_place = rng.choices(self._ENTITY_TYPES, k=min(4, len(rooms)))

        for etype in entity_types_to_place:
            if not rooms:
                break
            room = rng.choice(rooms)
            # Try to find a valid passable position that isn't a wall
            for _ in range(20):
                ex = rng.randint(room.x + 1, max(room.x + 1, room.x + room.w - 2))
                ey = rng.randint(room.y + 1, max(room.y + 1, room.y + room.h - 2))
                if (
                    0 <= ey < height
                    and 0 <= ex < width
                    and tiles[ey][ex].passable
                    and tiles[ey][ex].type != TerrainType.WALL
                    and (ex, ey) not in occupied
                ):
                    occupied.add((ex, ey))
                    blocks = etype in ("pillar", "crate")
                    entities.append(
                        MapEntity(
                            id=str(uuid4()),
                            type=etype,
                            x=ex,
                            y=ey,
                            blocks_los=etype == "pillar",
                            blocks_movement=blocks,
                        )
                    )
                    break

        return entities

    # -----------------------------------------------------------------------
    # Token spawn placement
    # -----------------------------------------------------------------------

    def _place_spawn_tokens(self, rooms: list[Rect]) -> list[MapToken]:
        tokens: list[MapToken] = []
        if not rooms:
            return tokens

        # Players spawn in first room
        player_room = rooms[0]
        for i in range(4):
            tx = player_room.x + 1 + (i % 2)
            ty = player_room.y + 1 + (i // 2)
            tokens.append(
                MapToken(
                    id=f"player_spawn_{i}",
                    name=f"Player {i + 1}",
                    x=tx,
                    y=ty,
                    team=TeamType.PLAYER,
                )
            )

        # Enemies spawn in last room
        enemy_room = rooms[-1] if len(rooms) > 1 else rooms[0]
        for i in range(3):
            tx = enemy_room.x + enemy_room.w - 2 - (i % 2)
            ty = enemy_room.y + enemy_room.h - 2 - (i // 2)
            tokens.append(
                MapToken(
                    id=f"enemy_spawn_{i}",
                    name=f"Enemy {i + 1}",
                    x=tx,
                    y=ty,
                    team=TeamType.ENEMY,
                )
            )

        return tokens

    # -----------------------------------------------------------------------
    # Spawn point generation from BSP rooms
    # -----------------------------------------------------------------------

    def _generate_spawn_points(self, rooms: list[Rect]) -> list[SpawnPoint]:
        """Generate spawn points from BSP room centres.

        Players spawn in the first room, enemies in the last.
        """
        spawn_points: list[SpawnPoint] = []
        if not rooms:
            return spawn_points

        # Player spawn points from first room
        player_room = rooms[0]
        for i in range(4):
            spawn_points.append(
                SpawnPoint(
                    x=player_room.x + 1 + (i % 2),
                    y=player_room.y + 1 + (i // 2),
                    team=TeamType.PLAYER,
                )
            )

        # Enemy spawn points from last room
        enemy_room = rooms[-1] if len(rooms) > 1 else rooms[0]
        for i in range(3):
            spawn_points.append(
                SpawnPoint(
                    x=enemy_room.x + enemy_room.w - 2 - (i % 2),
                    y=enemy_room.y + enemy_room.h - 2 - (i // 2),
                    team=TeamType.ENEMY,
                )
            )

        return spawn_points
