import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import ErrorState from "./ErrorState";

const renderWithRouter = (ui: React.ReactElement) =>
  render(<MemoryRouter>{ui}</MemoryRouter>);

describe("ErrorState", () => {
  it("renders the error message", () => {
    renderWithRouter(<ErrorState message="Something went wrong" />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("has role=alert for accessibility", () => {
    renderWithRouter(<ErrorState message="An error occurred" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("renders the heading and hint text", () => {
    renderWithRouter(<ErrorState message="An error occurred" />);
    expect(screen.getByText("Quest Interrupted")).toBeInTheDocument();
    expect(
      screen.getByText("The path ahead is unclear. Try retracing your steps.")
    ).toBeInTheDocument();
  });

  it("renders a Try Again button that reloads when no onRetry provided", () => {
    renderWithRouter(<ErrorState message="An error occurred" />);
    expect(
      screen.getByRole("button", { name: /try again/i })
    ).toBeInTheDocument();
  });

  it("renders a retry button when onRetry is provided", () => {
    const onRetry = vi.fn();
    renderWithRouter(
      <ErrorState message="An error occurred" onRetry={onRetry} />
    );
    expect(
      screen.getByRole("button", { name: /try again/i })
    ).toBeInTheDocument();
  });

  it("calls onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    const user = userEvent.setup();
    renderWithRouter(
      <ErrorState message="An error occurred" onRetry={onRetry} />
    );
    await user.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("renders Back to Campaigns link by default", () => {
    renderWithRouter(<ErrorState message="An error occurred" />);
    expect(
      screen.getByRole("button", { name: /back to campaigns/i })
    ).toBeInTheDocument();
  });

  it("hides Back to Campaigns link when showBackLink is false", () => {
    renderWithRouter(
      <ErrorState message="An error occurred" showBackLink={false} />
    );
    expect(
      screen.queryByRole("button", { name: /back to campaigns/i })
    ).not.toBeInTheDocument();
  });
});
