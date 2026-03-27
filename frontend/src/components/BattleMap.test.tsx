import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { BattleMapData } from "@/types/battleMap";
import BattleMap from "./BattleMap";
import styles from "./BattleMap.module.css";

const mockMapData: BattleMapData = {
  id: "test-map-1",
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
  entities: [],
  tokens: [
    { id: "t1", name: "Hero", x: 1, y: 1, team: "player", hp: 20, max_hp: 20 },
  ],
  effects: [],
  fog_of_war: false,
};

describe("BattleMap", () => {
  it("renders battle map with image when mapUrl is provided", () => {
    const mapUrl = "https://example.com/battle-map.jpg";
    render(<BattleMap mapUrl={mapUrl} />);

    expect(screen.getByText("Battle Map")).toBeInTheDocument();

    const image = screen.getByRole("img");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", mapUrl);
    expect(image).toHaveAttribute("alt", "Tactical Battle Map");
  });

  it("renders empty state when mapUrl is null", () => {
    render(<BattleMap mapUrl={null} />);

    expect(screen.getByText("Battle Map")).toBeInTheDocument();
    expect(screen.getByText("No battle map available")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders empty state when mapUrl is empty string", () => {
    render(<BattleMap mapUrl="" />);

    expect(screen.getByText("No battle map available")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("shows expand button initially", () => {
    render(<BattleMap mapUrl="test.jpg" />);

    const button = screen.getByRole("button", { name: "Expand" });
    expect(button).toBeInTheDocument();
  });

  it("toggles expand/minimize when button is clicked", async () => {
    render(<BattleMap mapUrl="test.jpg" />);

    const button = screen.getByRole("button", { name: "Expand" });

    // Initially should show Expand
    expect(button).toHaveTextContent("Expand");

    // Click to expand
    await userEvent.click(button);
    expect(
      screen.getByRole("button", { name: "Minimize" }),
    ).toBeInTheDocument();

    // Click to minimize
    await userEvent.click(screen.getByRole("button", { name: "Minimize" }));
    expect(screen.getByRole("button", { name: "Expand" })).toBeInTheDocument();
  });

  it("applies expanded CSS class when expanded", async () => {
    const { container } = render(<BattleMap mapUrl="test.jpg" />);

    const battleMap = container.querySelector(`.${styles.battleMap}`);
    expect(battleMap).not.toHaveClass(styles.expanded);

    const expandButton = screen.getByRole("button", { name: "Expand" });
    await userEvent.click(expandButton);

    expect(battleMap).toHaveClass(styles.expanded);
  });

  it("removes expanded CSS class when minimized", async () => {
    const { container } = render(<BattleMap mapUrl="test.jpg" />);

    const battleMap = container.querySelector(`.${styles.battleMap}`);
    const toggleButton = screen.getByRole("button", { name: "Expand" });

    // Expand first
    await userEvent.click(toggleButton);
    expect(battleMap).toHaveClass(styles.expanded);

    // Then minimize
    await userEvent.click(screen.getByRole("button", { name: "Minimize" }));
    expect(battleMap).not.toHaveClass(styles.expanded);
  });

  it("has correct CSS classes", () => {
    const { container } = render(<BattleMap mapUrl="test.jpg" />);

    expect(container.querySelector(`.${styles.battleMap}`)).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.battleMapHeader}`),
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.mapContainer}`),
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.toggleButton}`),
    ).toBeInTheDocument();
  });

  it("has correct CSS classes for empty state", () => {
    const { container } = render(<BattleMap mapUrl={null} />);

    expect(container.querySelector(`.${styles.battleMap}`)).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.mapContainer}`),
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.emptyMapState}`),
    ).toBeInTheDocument();
  });

  it("toggle button has correct class", () => {
    render(<BattleMap mapUrl="test.jpg" />);

    const button = screen.getByRole("button", { name: "Expand" });
    expect(button).toHaveClass(styles.toggleButton);
  });

  // ── New tests for tile grid support ──────────────────────────────────────

  it("renders tile grid when mapData is provided", () => {
    render(<BattleMap mapUrl={null} mapData={mockMapData} />);

    expect(screen.getByTestId("tile-grid-renderer")).toBeInTheDocument();
    expect(screen.getByTestId("tile-grid-canvas")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders tile grid by default when both mapUrl and mapData are provided", () => {
    render(<BattleMap mapUrl="test.jpg" mapData={mockMapData} />);

    expect(screen.getByTestId("tile-grid-renderer")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("shows toggle view button when both mapUrl and mapData are available", () => {
    render(<BattleMap mapUrl="test.jpg" mapData={mockMapData} />);

    expect(
      screen.getByRole("button", { name: "Image View" }),
    ).toBeInTheDocument();
  });

  it("does not show toggle view button when only mapUrl is provided", () => {
    render(<BattleMap mapUrl="test.jpg" />);

    expect(
      screen.queryByRole("button", { name: "Image View" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Tile View" }),
    ).not.toBeInTheDocument();
  });

  it("switches between tile and image view when toggle is clicked", async () => {
    render(<BattleMap mapUrl="test.jpg" mapData={mockMapData} />);

    // Initially tile view
    expect(screen.getByTestId("tile-grid-renderer")).toBeInTheDocument();

    // Switch to image view
    await userEvent.click(
      screen.getByRole("button", { name: "Image View" }),
    );
    expect(screen.queryByTestId("tile-grid-renderer")).not.toBeInTheDocument();
    expect(screen.getByRole("img")).toBeInTheDocument();

    // Switch back to tile view
    await userEvent.click(
      screen.getByRole("button", { name: "Tile View" }),
    );
    expect(screen.getByTestId("tile-grid-renderer")).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("renders image view when only mapUrl is provided (no mapData)", () => {
    render(<BattleMap mapUrl="https://example.com/map.jpg" />);

    const image = screen.getByRole("img");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "https://example.com/map.jpg");
    expect(screen.queryByTestId("tile-grid-renderer")).not.toBeInTheDocument();
  });

  it("renders empty state when neither mapUrl nor mapData is provided", () => {
    render(<BattleMap mapUrl={null} mapData={null} />);

    expect(screen.getByText("No battle map available")).toBeInTheDocument();
    expect(screen.queryByTestId("tile-grid-renderer")).not.toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });
});
