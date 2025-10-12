import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import BattleMap from "./BattleMap";
import styles from "./BattleMap.module.css";

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
      screen.getByRole("button", { name: "Minimize" })
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
    const toggleButton = screen.getByRole("button");

    // Expand first
    await userEvent.click(toggleButton);
    expect(battleMap).toHaveClass(styles.expanded);

    // Then minimize
    await userEvent.click(toggleButton);
    expect(battleMap).not.toHaveClass(styles.expanded);
  });

  it("has correct CSS classes", () => {
    const { container } = render(<BattleMap mapUrl="test.jpg" />);

    expect(container.querySelector(`.${styles.battleMap}`)).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.battleMapHeader}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.mapContainer}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.toggleButton}`)
    ).toBeInTheDocument();
  });

  it("has correct CSS classes for empty state", () => {
    const { container } = render(<BattleMap mapUrl={null} />);

    expect(container.querySelector(`.${styles.battleMap}`)).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.mapContainer}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.emptyMapState}`)
    ).toBeInTheDocument();
  });

  it("toggle button has correct class", () => {
    render(<BattleMap mapUrl="test.jpg" />);

    const button = screen.getByRole("button");
    expect(button).toHaveClass(styles.toggleButton);
  });
});
