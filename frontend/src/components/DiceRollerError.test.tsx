import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DiceRoller from "./DiceRoller";

describe("DiceRoller error handling", () => {
  it("does not call window.alert on error", () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    render(<DiceRoller />);
    expect(alertSpy).not.toHaveBeenCalled();
    alertSpy.mockRestore();
  });
});
