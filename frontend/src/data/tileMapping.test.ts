import { describe, expect, it } from "vitest";
import {
  getTileAsset,
  hasTileAsset,
  TILE_ASSETS,
  TILE_RENDER_SIZE,
  TILE_SCALE,
  TILE_SIZE,
} from "./tileMapping";

describe("tileMapping", () => {
  describe("constants", () => {
    it("TILE_SIZE is 16", () => {
      expect(TILE_SIZE).toBe(16);
    });

    it("TILE_SCALE is 4", () => {
      expect(TILE_SCALE).toBe(4);
    });

    it("TILE_RENDER_SIZE is TILE_SIZE × TILE_SCALE (64)", () => {
      expect(TILE_RENDER_SIZE).toBe(TILE_SIZE * TILE_SCALE);
      expect(TILE_RENDER_SIZE).toBe(64);
    });
  });

  describe("TILE_ASSETS", () => {
    it("contains the required terrain types from the issue spec", () => {
      expect(TILE_ASSETS.stone_floor).toBeDefined();
      expect(TILE_ASSETS.wooden_floor).toBeDefined();
      expect(TILE_ASSETS.wall).toBeDefined();
      expect(TILE_ASSETS.door).toBeDefined();
    });

    it("maps to paths under /tiles/kenney-tiny-dungeon/", () => {
      for (const path of Object.values(TILE_ASSETS)) {
        expect(path).toMatch(/^\/tiles\/kenney-tiny-dungeon\/tile_\d{4}\.png$/);
      }
    });

    it("covers all terrain types used by the backend map generator", () => {
      const requiredTypes = [
        "open_terrain",
        "wall",
        "water",
        "door",
        "stairs",
        "pillar",
        "bridge",
        "pit",
        "lava",
        "hazardous_terrain",
        "passage",
      ];
      for (const type of requiredTypes) {
        expect(TILE_ASSETS[type], `Missing tile for "${type}"`).toBeDefined();
      }
    });

    it("covers hazardous terrain types", () => {
      expect(TILE_ASSETS.water).toContain("tile_0080.png");
      expect(TILE_ASSETS.lava).toContain("tile_0083.png");
      expect(TILE_ASSETS.pit).toContain("tile_0087.png");
    });
  });

  describe("getTileAsset", () => {
    it("returns the correct path for a known terrain type", () => {
      expect(getTileAsset("stone_floor")).toBe(
        "/tiles/kenney-tiny-dungeon/tile_0000.png"
      );
    });

    it("falls back to stone_floor for an unknown terrain type", () => {
      expect(getTileAsset("unknown_terrain_xyz")).toBe(TILE_ASSETS.stone_floor);
    });

    it("falls back for an empty string", () => {
      expect(getTileAsset("")).toBe(TILE_ASSETS.stone_floor);
    });
  });

  describe("hasTileAsset", () => {
    it("returns true for a known terrain type", () => {
      expect(hasTileAsset("wall")).toBe(true);
    });

    it("returns false for an unknown terrain type", () => {
      expect(hasTileAsset("totally_unknown_type")).toBe(false);
    });
  });
});
