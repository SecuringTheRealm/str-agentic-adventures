import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MobileDrawer from "./MobileDrawer";

describe("MobileDrawer", () => {
  it("renders children when open", () => {
    render(
      <MobileDrawer open={true} onClose={vi.fn()} title="Test Drawer">
        <div>Drawer content</div>
      </MobileDrawer>
    );

    expect(screen.getByText("Drawer content")).toBeInTheDocument();
    expect(screen.getByText("Test Drawer")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(
      <MobileDrawer open={false} onClose={vi.fn()} title="Test Drawer">
        <div>Drawer content</div>
      </MobileDrawer>
    );

    expect(screen.queryByText("Drawer content")).not.toBeInTheDocument();
  });

  it("calls onClose when close button is clicked", async () => {
    const onClose = vi.fn();
    render(
      <MobileDrawer open={true} onClose={onClose} title="Test Drawer">
        <div>Drawer content</div>
      </MobileDrawer>
    );

    const closeButton = screen.getByRole("button", { name: /close/i });
    await userEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("renders with correct aria-label", () => {
    render(
      <MobileDrawer open={true} onClose={vi.fn()} title="Character Sheet">
        <div>Content</div>
      </MobileDrawer>
    );

    expect(
      screen.getByRole("dialog", { name: "Character Sheet" })
    ).toBeInTheDocument();
  });
});
