import { act, render, screen, waitFor } from "@testing-library/react";
import AutoSaveToast from "./AutoSaveToast";

describe("AutoSaveToast", () => {
  it("renders nothing when lastAutoSave is null", () => {
    const { container } = render(<AutoSaveToast lastAutoSave={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("shows the toast when lastAutoSave is set", async () => {
    render(<AutoSaveToast lastAutoSave="2026-01-01T00:00:00Z" />);
    expect(screen.getByRole("status")).toBeInTheDocument();
    expect(screen.getByText("✓ Auto-saved")).toBeInTheDocument();
  });

  it("hides the toast after the display duration", async () => {
    vi.useFakeTimers();

    render(<AutoSaveToast lastAutoSave="2026-01-01T00:00:00Z" />);
    expect(screen.getByRole("status")).toBeInTheDocument();

    // Advance all timers so the hide timeout fires
    act(() => {
      vi.runAllTimers();
    });

    expect(screen.queryByRole("status")).not.toBeInTheDocument();

    vi.useRealTimers();
  });

  it("re-shows toast on a new save timestamp", async () => {
    vi.useFakeTimers();

    const { rerender } = render(
      <AutoSaveToast lastAutoSave="2026-01-01T00:00:00Z" />
    );
    expect(screen.getByRole("status")).toBeInTheDocument();

    // Dismiss the first toast
    act(() => {
      vi.runAllTimers();
    });
    expect(screen.queryByRole("status")).not.toBeInTheDocument();

    // Trigger a new save with a different timestamp
    rerender(<AutoSaveToast lastAutoSave="2026-01-01T00:05:00Z" />);
    expect(screen.getByRole("status")).toBeInTheDocument();

    vi.useRealTimers();
  });
});
