import { fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import type { BattleMapData } from "@/types/battleMap";
import TileGridRenderer from "./TileGridRenderer";

// Mock canvas context since jsdom doesn't support canvas
const mockContext = {
  fillRect: vi.fn(),
  strokeRect: vi.fn(),
  clearRect: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  arc: vi.fn(),
  closePath: vi.fn(),
  fill: vi.fn(),
  stroke: vi.fn(),
  fillText: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  translate: vi.fn(),
  rotate: vi.fn(),
  set fillStyle(_: string) {},
  get fillStyle() {
    return "";
  },
  set strokeStyle(_: string) {},
  get strokeStyle() {
    return "";
  },
  set globalAlpha(_: number) {},
  get globalAlpha() {
    return 1;
  },
  set lineWidth(_: number) {},
  get lineWidth() {
    return 1;
  },
  set font(_: string) {},
  get font() {
    return "";
  },
  set textAlign(_: string) {},
  get textAlign() {
    return "start";
  },
  set textBaseline(_: string) {},
  get textBaseline() {
    return "alphabetic";
  },
  set imageSmoothingEnabled(_: boolean) {},
  get imageSmoothingEnabled() {
    return true;
  },
};

beforeEach(() => {
  vi.clearAllMocks();

  // Mock HTMLCanvasElement.getContext
  HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue(mockContext);

  // Mock Image to immediately call onload
  vi.spyOn(globalThis, "Image").mockImplementation(() => {
    const img = {
      onload: null as (() => void) | null,
      onerror: null as (() => void) | null,
      src: "",
      complete: false,
      width: 16,
      height: 16,
    };
    // Trigger onload asynchronously
    Object.defineProperty(img, "src", {
      set(_val: string) {
        setTimeout(() => {
          (img as { complete: boolean }).complete = true;
          img.onload?.();
        }, 0);
      },
      get() {
        return "";
      },
    });
    return img as unknown as HTMLImageElement;
  });
});

const createMockMapData = (
  overrides?: Partial<BattleMapData>
): BattleMapData => ({
  id: "test-map",
  width: 3,
  height: 3,
  tile_size: 16,
  tiles: [
    [
      { type: "stone_floor", passable: true, elevation: 0 },
      { type: "stone_floor", passable: true, elevation: 0 },
      { type: "wall", passable: false, elevation: 1 },
    ],
    [
      { type: "stone_floor", passable: true, elevation: 0 },
      { type: "wooden_floor", passable: true, elevation: 0 },
      { type: "stone_floor", passable: true, elevation: 0 },
    ],
    [
      { type: "wall", passable: false, elevation: 1 },
      { type: "door", passable: true, elevation: 0 },
      { type: "stone_floor", passable: true, elevation: 0 },
    ],
  ],
  entities: [
    {
      id: "e1",
      type: "chest",
      x: 2,
      y: 2,
      blocks_los: false,
      blocks_movement: true,
    },
  ],
  tokens: [
    {
      id: "token-hero",
      name: "Hero",
      x: 1,
      y: 1,
      team: "player",
      hp: 15,
      max_hp: 20,
    },
    {
      id: "token-goblin",
      name: "Goblin",
      x: 2,
      y: 1,
      team: "enemy",
      hp: 8,
      max_hp: 10,
    },
  ],
  effects: [],
  fog_of_war: false,
  ...overrides,
});

describe("TileGridRenderer", () => {
  it("renders a canvas element", () => {
    render(<TileGridRenderer mapData={createMockMapData()} />);

    const canvas = screen.getByTestId("tile-grid-canvas");
    expect(canvas).toBeInTheDocument();
    expect(canvas.tagName).toBe("CANVAS");
  });

  it("renders with the tile-grid-renderer container", () => {
    render(<TileGridRenderer mapData={createMockMapData()} />);

    expect(screen.getByTestId("tile-grid-renderer")).toBeInTheDocument();
  });

  it("renders with mock BattleMapData", () => {
    const mapData = createMockMapData();
    render(<TileGridRenderer mapData={mapData} />);

    const canvas = screen.getByTestId("tile-grid-canvas");
    expect(canvas).toBeInTheDocument();
    // Canvas should have been initialised via getContext
    expect(HTMLCanvasElement.prototype.getContext).toHaveBeenCalledWith("2d");
  });

  it("renders with effects data", () => {
    const mapData = createMockMapData({
      effects: [
        {
          type: "aoe_circle",
          origin_x: 1,
          origin_y: 1,
          radius: 2,
          colour: "rgba(255, 0, 0, 0.5)",
          label: "Fireball",
        },
      ],
    });

    render(<TileGridRenderer mapData={mapData} />);

    const canvas = screen.getByTestId("tile-grid-canvas");
    expect(canvas).toBeInTheDocument();
  });

  it("calls onTokenMove when a non-token cell is clicked after selecting a token", async () => {
    const onTokenMove = vi.fn();
    const mapData = createMockMapData();

    render(<TileGridRenderer mapData={mapData} onTokenMove={onTokenMove} />);

    const canvas = screen.getByTestId("tile-grid-canvas");

    // Mock getBoundingClientRect for click position calculation
    vi.spyOn(canvas, "getBoundingClientRect").mockReturnValue({
      left: 0,
      top: 0,
      right: 192,
      bottom: 192,
      width: 192,
      height: 192,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    });

    // Click on the token at grid position (1, 1) — pixel center (96, 96) at scale=1 with tile size 64
    fireEvent.click(canvas, { clientX: 96, clientY: 96 });

    // Click on empty cell at grid position (0, 0) — pixel (32, 32)
    fireEvent.click(canvas, { clientX: 32, clientY: 32 });

    expect(onTokenMove).toHaveBeenCalledWith("token-hero", 0, 0);
  });

  it("does not call onTokenMove when clicking a token (selects it instead)", () => {
    const onTokenMove = vi.fn();
    const mapData = createMockMapData();

    render(<TileGridRenderer mapData={mapData} onTokenMove={onTokenMove} />);

    const canvas = screen.getByTestId("tile-grid-canvas");

    vi.spyOn(canvas, "getBoundingClientRect").mockReturnValue({
      left: 0,
      top: 0,
      right: 192,
      bottom: 192,
      width: 192,
      height: 192,
      x: 0,
      y: 0,
      toJSON: () => ({}),
    });

    // Click on token at grid (1, 1)
    fireEvent.click(canvas, { clientX: 96, clientY: 96 });

    // Should not have called onTokenMove — just selected the token
    expect(onTokenMove).not.toHaveBeenCalled();
  });

  it("renders with empty tokens and entities", () => {
    const mapData = createMockMapData({
      tokens: [],
      entities: [],
    });

    render(<TileGridRenderer mapData={mapData} />);

    expect(screen.getByTestId("tile-grid-canvas")).toBeInTheDocument();
  });

  it("renders canvas with imageRendering pixelated style", () => {
    const mapData = createMockMapData();
    render(<TileGridRenderer mapData={mapData} />);

    const canvas = screen.getByTestId("tile-grid-canvas");
    // Canvas should be present and have pixelated rendering
    expect(canvas).toBeInTheDocument();
    expect(canvas.style.imageRendering).toBe("pixelated");
  });
});
