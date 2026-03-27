export type TerrainType =
  | "stone_floor"
  | "wooden_floor"
  | "grass"
  | "dirt"
  | "water"
  | "lava"
  | "wall"
  | "door"
  | "stairs";

export type TeamType = "player" | "enemy" | "neutral";

export type EffectType = "aoe_circle" | "aoe_cone" | "aoe_line";

export interface MapTile {
  type: TerrainType;
  passable: boolean;
  elevation: number;
}

export interface MapEntity {
  id: string;
  type: string;
  x: number;
  y: number;
  blocks_los: boolean;
  blocks_movement: boolean;
}

export interface MapToken {
  id: string;
  name: string;
  x: number;
  y: number;
  team: TeamType;
  hp?: number;
  max_hp?: number;
}

export interface MapEffect {
  type: EffectType;
  origin_x: number;
  origin_y: number;
  radius?: number;
  direction?: number;
  colour?: string;
  label?: string;
}

export interface BattleMapData {
  id: string;
  width: number;
  height: number;
  tile_size: number;
  tiles: MapTile[][];
  entities: MapEntity[];
  tokens: MapToken[];
  effects: MapEffect[];
  fog_of_war: boolean;
  ambient_image_url?: string;
}
