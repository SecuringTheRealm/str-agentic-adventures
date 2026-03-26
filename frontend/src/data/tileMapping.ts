/**
 * Tile asset mappings for the Kenney Tiny Dungeon tileset.
 *
 * Tileset: Kenney Tiny Dungeon (https://kenney.nl/assets/tiny-dungeon)
 * License: CC0 1.0 Universal – public domain, no attribution required.
 * Tile size: 16×16 px (render at TILE_SCALE × for TILE_RENDER_SIZE px on screen).
 *
 * Each key corresponds to a terrain / entity type produced by the backend
 * BattleMapData model (map_generation_plugin.py) and maps to the public URL
 * path of the corresponding PNG tile.
 */

/** Native tile size in pixels (as shipped in the asset pack). */
export const TILE_SIZE = 16;

/** Recommended scale multiplier for crisp pixel-art rendering. */
export const TILE_SCALE = 4;

/** Rendered tile size in pixels (TILE_SIZE × TILE_SCALE). */
export const TILE_RENDER_SIZE = TILE_SIZE * TILE_SCALE; // 64

const BASE = "/tiles/kenney-tiny-dungeon";

// ---------------------------------------------------------------------------
// Primary terrain-type → tile mapping
// Keys must match the `type` values emitted by the backend map generator.
// ---------------------------------------------------------------------------

/** Map of terrain / entity type names to their tile asset paths. */
export const TILE_ASSETS: Record<string, string> = {
  // ── Floors ──────────────────────────────────────────────────────────────
  stone_floor: `${BASE}/tile_0000.png`,
  stone_floor_variant: `${BASE}/tile_0001.png`,
  wooden_floor: `${BASE}/tile_0002.png`,
  wooden_floor_variant: `${BASE}/tile_0003.png`,
  dirt_floor: `${BASE}/tile_0004.png`,
  dirt_floor_variant: `${BASE}/tile_0005.png`,
  grass_floor: `${BASE}/tile_0006.png`,
  grass_floor_variant: `${BASE}/tile_0007.png`,
  cobblestone_floor: `${BASE}/tile_0008.png`,
  cobblestone_floor_variant: `${BASE}/tile_0009.png`,
  sand_floor: `${BASE}/tile_0010.png`,
  sand_floor_variant: `${BASE}/tile_0011.png`,
  stone_floor_cracked: `${BASE}/tile_0012.png`,
  stone_floor_mossy: `${BASE}/tile_0013.png`,
  stone_floor_stained: `${BASE}/tile_0014.png`,
  stone_floor_dark: `${BASE}/tile_0015.png`,

  // ── Walls ───────────────────────────────────────────────────────────────
  wall: `${BASE}/tile_0016.png`,
  wall_variant: `${BASE}/tile_0017.png`,
  wall_stone: `${BASE}/tile_0018.png`,
  wall_stone_dark: `${BASE}/tile_0019.png`,
  wall_brick: `${BASE}/tile_0020.png`,
  wall_brick_variant: `${BASE}/tile_0021.png`,
  wall_top: `${BASE}/tile_0022.png`,
  wall_top_variant: `${BASE}/tile_0023.png`,
  wall_side_left: `${BASE}/tile_0024.png`,
  wall_side_right: `${BASE}/tile_0025.png`,
  wall_corner_top_left: `${BASE}/tile_0026.png`,
  wall_corner_top_right: `${BASE}/tile_0027.png`,
  wall_corner_bottom_left: `${BASE}/tile_0028.png`,
  wall_corner_bottom_right: `${BASE}/tile_0029.png`,
  wall_inner_corner_top_left: `${BASE}/tile_0030.png`,
  wall_inner_corner_top_right: `${BASE}/tile_0031.png`,
  wall_inner_corner_bottom_left: `${BASE}/tile_0032.png`,
  wall_inner_corner_bottom_right: `${BASE}/tile_0033.png`,
  wall_t_top: `${BASE}/tile_0034.png`,
  wall_t_bottom: `${BASE}/tile_0035.png`,
  wall_t_left: `${BASE}/tile_0036.png`,
  wall_t_right: `${BASE}/tile_0037.png`,
  wall_cross: `${BASE}/tile_0038.png`,
  wall_pillar: `${BASE}/tile_0039.png`,
  wall_column_top: `${BASE}/tile_0040.png`,
  wall_column_mid: `${BASE}/tile_0041.png`,
  wall_column_bottom: `${BASE}/tile_0042.png`,
  wall_arch_left: `${BASE}/tile_0043.png`,
  wall_arch_right: `${BASE}/tile_0044.png`,
  wall_arch_top: `${BASE}/tile_0045.png`,
  wall_banner_left: `${BASE}/tile_0046.png`,
  wall_banner_right: `${BASE}/tile_0047.png`,

  // ── Doors & Passages ────────────────────────────────────────────────────
  door: `${BASE}/tile_0048.png`,
  door_open: `${BASE}/tile_0049.png`,
  door_locked: `${BASE}/tile_0050.png`,
  door_iron: `${BASE}/tile_0051.png`,
  door_iron_open: `${BASE}/tile_0052.png`,
  stairs_up: `${BASE}/tile_0053.png`,
  stairs_down: `${BASE}/tile_0054.png`,
  stairs: `${BASE}/tile_0053.png`,
  portal: `${BASE}/tile_0055.png`,
  portal_active: `${BASE}/tile_0056.png`,
  gate: `${BASE}/tile_0057.png`,
  gate_open: `${BASE}/tile_0058.png`,
  bridge: `${BASE}/tile_0059.png`,
  bridge_horizontal: `${BASE}/tile_0059.png`,
  bridge_vertical: `${BASE}/tile_0060.png`,
  trapdoor: `${BASE}/tile_0061.png`,
  trapdoor_open: `${BASE}/tile_0062.png`,
  secret_door: `${BASE}/tile_0063.png`,

  // ── Objects & Furniture ─────────────────────────────────────────────────
  chest: `${BASE}/tile_0064.png`,
  chest_closed: `${BASE}/tile_0064.png`,
  chest_open: `${BASE}/tile_0065.png`,
  barrel: `${BASE}/tile_0066.png`,
  crate: `${BASE}/tile_0067.png`,
  pot: `${BASE}/tile_0068.png`,
  urn: `${BASE}/tile_0069.png`,
  torch: `${BASE}/tile_0070.png`,
  torch_lit: `${BASE}/tile_0071.png`,
  altar: `${BASE}/tile_0072.png`,
  statue: `${BASE}/tile_0073.png`,
  gravestone: `${BASE}/tile_0074.png`,
  pillar: `${BASE}/tile_0075.png`,
  pillar_top: `${BASE}/tile_0076.png`,
  pillar_bottom: `${BASE}/tile_0077.png`,
  bookshelf: `${BASE}/tile_0078.png`,
  table: `${BASE}/tile_0079.png`,
  obstacle: `${BASE}/tile_0066.png`,
  tree: `${BASE}/tile_0073.png`,

  // ── Hazards & Special Terrain ───────────────────────────────────────────
  water: `${BASE}/tile_0080.png`,
  water_deep: `${BASE}/tile_0081.png`,
  water_shallow: `${BASE}/tile_0082.png`,
  lava: `${BASE}/tile_0083.png`,
  lava_active: `${BASE}/tile_0084.png`,
  lava_edge: `${BASE}/tile_0085.png`,
  void: `${BASE}/tile_0086.png`,
  pit: `${BASE}/tile_0087.png`,
  pit_edge: `${BASE}/tile_0088.png`,
  trap: `${BASE}/tile_0089.png`,
  trap_pressure_plate: `${BASE}/tile_0089.png`,
  trap_spike: `${BASE}/tile_0090.png`,
  trap_arrow: `${BASE}/tile_0091.png`,
  acid_pool: `${BASE}/tile_0092.png`,
  hazardous_terrain: `${BASE}/tile_0092.png`,
  healing_fountain: `${BASE}/tile_0093.png`,
  magic_circle: `${BASE}/tile_0094.png`,
  magic_rune: `${BASE}/tile_0095.png`,

  // ── Characters & Tokens ─────────────────────────────────────────────────
  hero_warrior: `${BASE}/tile_0096.png`,
  hero_mage: `${BASE}/tile_0097.png`,
  hero_rogue: `${BASE}/tile_0098.png`,
  hero_cleric: `${BASE}/tile_0099.png`,
  monster_goblin: `${BASE}/tile_0100.png`,
  monster_orc: `${BASE}/tile_0101.png`,
  monster_skeleton: `${BASE}/tile_0102.png`,
  monster_dragon: `${BASE}/tile_0103.png`,
  monster_boss: `${BASE}/tile_0104.png`,
  npc_merchant: `${BASE}/tile_0105.png`,
  npc_guard: `${BASE}/tile_0106.png`,
  npc_villager: `${BASE}/tile_0107.png`,
  npc_quest: `${BASE}/tile_0108.png`,
  token_marker_red: `${BASE}/tile_0109.png`,
  token_marker_blue: `${BASE}/tile_0110.png`,
  token_marker_green: `${BASE}/tile_0111.png`,

  // ── Effects & UI Overlays ───────────────────────────────────────────────
  effect_fire: `${BASE}/tile_0112.png`,
  effect_spark: `${BASE}/tile_0113.png`,
  effect_ice: `${BASE}/tile_0114.png`,
  effect_shadow: `${BASE}/tile_0115.png`,
  effect_light: `${BASE}/tile_0116.png`,
  fog_of_war: `${BASE}/tile_0117.png`,
  explored: `${BASE}/tile_0118.png`,
  unexplored: `${BASE}/tile_0119.png`,
  aoe_circle: `${BASE}/tile_0120.png`,
  aoe_cone: `${BASE}/tile_0121.png`,
  aoe_line: `${BASE}/tile_0122.png`,
  path_marker: `${BASE}/tile_0123.png`,
  danger_marker: `${BASE}/tile_0124.png`,
  water_current: `${BASE}/tile_0125.png`,
  treasure_marker: `${BASE}/tile_0126.png`,
  spawn_point: `${BASE}/tile_0127.png`,

  // ── Open / default terrain ──────────────────────────────────────────────
  /** Fallback for "open_terrain" zones produced by the map generator. */
  open_terrain: `${BASE}/tile_0000.png`,
  /** Generic passage (e.g. bridge, corridor). */
  passage: `${BASE}/tile_0059.png`,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Retrieve the tile asset path for a given terrain / entity type.
 *
 * Falls back to the default stone floor tile if the requested type is not
 * found in the mapping, so callers never receive `undefined`.
 *
 * @param terrainType - Terrain type string from the BattleMapData model.
 * @returns Public URL path to the tile PNG.
 */
export function getTileAsset(terrainType: string): string {
  return TILE_ASSETS[terrainType] ?? TILE_ASSETS.stone_floor;
}

/**
 * Check whether a terrain / entity type has an explicit tile mapping.
 *
 * @param terrainType - Terrain type string to look up.
 */
export function hasTileAsset(terrainType: string): boolean {
  return terrainType in TILE_ASSETS;
}
