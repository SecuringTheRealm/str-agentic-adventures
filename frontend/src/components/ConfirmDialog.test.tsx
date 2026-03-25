import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ConfirmDialog from "./ConfirmDialog";

const defaultProps = {
  isOpen: true,
  title: "Delete Campaign",
  message: "Are you sure you want to delete this campaign?",
  onConfirm: vi.fn(),
  onCancel: vi.fn(),
};

describe("ConfirmDialog", () => {
  it("renders nothing when isOpen is false", () => {
    render(<ConfirmDialog {...defaultProps} isOpen={false} />);
    expect(screen.queryByRole("alertdialog")).not.toBeInTheDocument();
  });

  it("renders the dialog when isOpen is true", () => {
    render(<ConfirmDialog {...defaultProps} />);
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
  });

  it("displays title and message", () => {
    render(<ConfirmDialog {...defaultProps} />);
    expect(screen.getByText("Delete Campaign")).toBeInTheDocument();
    expect(
      screen.getByText("Are you sure you want to delete this campaign?")
    ).toBeInTheDocument();
  });

  it("has aria-modal='true'", () => {
    render(<ConfirmDialog {...defaultProps} />);
    expect(screen.getByRole("alertdialog")).toHaveAttribute(
      "aria-modal",
      "true"
    );
  });

  it("has aria-labelledby pointing to title", () => {
    render(<ConfirmDialog {...defaultProps} />);
    const dialog = screen.getByRole("alertdialog");
    expect(dialog).toHaveAttribute("aria-labelledby", "confirm-dialog-title");
    expect(document.getElementById("confirm-dialog-title")).toHaveTextContent(
      "Delete Campaign"
    );
  });

  it("has aria-describedby pointing to message", () => {
    render(<ConfirmDialog {...defaultProps} />);
    const dialog = screen.getByRole("alertdialog");
    expect(dialog).toHaveAttribute(
      "aria-describedby",
      "confirm-dialog-message"
    );
  });

  it("uses default confirm and cancel labels", () => {
    render(<ConfirmDialog {...defaultProps} />);
    expect(screen.getByRole("button", { name: "Confirm" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
  });

  it("uses custom confirm and cancel labels", () => {
    render(
      <ConfirmDialog
        {...defaultProps}
        confirmLabel="Delete"
        cancelLabel="Keep"
      />
    );
    expect(screen.getByRole("button", { name: "Delete" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Keep" })).toBeInTheDocument();
  });

  it("calls onConfirm when confirm button is clicked", async () => {
    const onConfirm = vi.fn();
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} onConfirm={onConfirm} />);
    await user.click(screen.getByRole("button", { name: "Confirm" }));
    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when cancel button is clicked", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when Escape key is pressed", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);
    await user.keyboard("{Escape}");
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when overlay is clicked", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    const { container } = render(
      <ConfirmDialog {...defaultProps} onCancel={onCancel} />
    );
    // Click the overlay (the first child div of container)
    const overlay = container.firstChild as HTMLElement;
    await user.click(overlay);
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("does not call onCancel when dialog itself is clicked", async () => {
    const onCancel = vi.fn();
    const user = userEvent.setup();
    render(<ConfirmDialog {...defaultProps} onCancel={onCancel} />);
    await user.click(screen.getByRole("alertdialog"));
    expect(onCancel).not.toHaveBeenCalled();
  });
});
