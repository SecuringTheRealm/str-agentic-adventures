import { render, screen } from "@testing-library/react";
import CompactStatusBar from "./CompactStatusBar";

describe("CompactStatusBar", () => {
  it("renders HP and AC correctly", () => {
    render(
      <CompactStatusBar
        currentHp={30}
        maxHp={50}
        armorClass={15}
        level={5}
      />
    );

    expect(screen.getByText("30/50")).toBeInTheDocument();
    expect(screen.getByTestId("ac-value")).toHaveTextContent("15");
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("shows green HP bar when above 50%", () => {
    const { container } = render(
      <CompactStatusBar
        currentHp={40}
        maxHp={50}
        armorClass={10}
        level={1}
      />
    );

    const progressbar = screen.getByRole("progressbar");
    expect(progressbar).toHaveAttribute("aria-valuenow", "40");
    expect(progressbar).toHaveAttribute("aria-valuemax", "50");

    // HP fill should have green class (above 50%)
    const fill = progressbar.firstChild as HTMLElement;
    expect(fill.className).toContain("hpBarGreen");
  });

  it("shows yellow HP bar when between 25% and 50%", () => {
    render(
      <CompactStatusBar
        currentHp={20}
        maxHp={50}
        armorClass={10}
        level={1}
      />
    );

    const progressbar = screen.getByRole("progressbar");
    const fill = progressbar.firstChild as HTMLElement;
    expect(fill.className).toContain("hpBarYellow");
  });

  it("shows red HP bar when below 25%", () => {
    render(
      <CompactStatusBar
        currentHp={10}
        maxHp={50}
        armorClass={10}
        level={1}
      />
    );

    const progressbar = screen.getByRole("progressbar");
    const fill = progressbar.firstChild as HTMLElement;
    expect(fill.className).toContain("hpBarRed");
  });

  it("renders conditions as badges", () => {
    render(
      <CompactStatusBar
        currentHp={30}
        maxHp={50}
        armorClass={12}
        level={3}
        conditions={["Poisoned", "Stunned"]}
      />
    );

    expect(screen.getByText("Poisoned")).toBeInTheDocument();
    expect(screen.getByText("Stunned")).toBeInTheDocument();
  });

  it("handles zero max HP without crashing", () => {
    render(
      <CompactStatusBar
        currentHp={0}
        maxHp={0}
        armorClass={10}
        level={1}
      />
    );

    expect(screen.getByText("0/0")).toBeInTheDocument();
  });
});
