"""
Pydantic models for structured battle map data.
"""

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class TerrainType(str, Enum):
    STONE_FLOOR = "stone_floor"
    WOODEN_FLOOR = "wooden_floor"
    GRASS = "grass"
    DIRT = "dirt"
    WATER = "water"
    LAVA = "lava"
    WALL = "wall"
    DOOR = "door"
    STAIRS = "stairs"


class TeamType(str, Enum):
    PLAYER = "player"
    ENEMY = "enemy"
    NEUTRAL = "neutral"


class MapTile(BaseModel):
    type: TerrainType = TerrainType.STONE_FLOOR
    passable: bool = True
    elevation: int = 0


class MapEntity(BaseModel):
    id: str
    type: str  # "pillar", "barrel", "chest", "trap", etc.
    x: int
    y: int
    blocks_los: bool = False
    blocks_movement: bool = False


class MapToken(BaseModel):
    id: str
    name: str
    x: int
    y: int
    team: TeamType = TeamType.NEUTRAL
    hp: int | None = None
    max_hp: int | None = None


class MapEffect(BaseModel):
    type: str  # "aoe_circle", "aoe_cone", "aoe_line"
    origin_x: int
    origin_y: int
    radius: int | None = None
    direction: int | None = Field(default=None, ge=0, lt=360)  # degrees for cones
    colour: str = "red"
    label: str = ""


class BattleMapData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    width: int = 20
    height: int = 20
    tile_size: int = 64
    tiles: list[list[MapTile]] = Field(default_factory=list)
    entities: list[MapEntity] = Field(default_factory=list)
    tokens: list[MapToken] = Field(default_factory=list)
    effects: list[MapEffect] = Field(default_factory=list)
    fog_of_war: bool = True
    ambient_image_url: str | None = None
