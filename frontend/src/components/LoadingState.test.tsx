import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LoadingState from "./LoadingState";

describe("LoadingState", () => {
  it("renders with default message", () => {
    render(<LoadingState />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders with a custom message", () => {
    render(<LoadingState message="Loading game..." />);
    expect(screen.getByText("Loading game...")).toBeInTheDocument();
  });

  it("has role=status for accessibility", () => {
    render(<LoadingState />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("has aria-live=polite on the container", () => {
    render(<LoadingState />);
    expect(screen.getByRole("status")).toHaveAttribute("aria-live", "polite");
  });

  it("renders the spinner element", () => {
    const { container } = render(<LoadingState />);
    // The spinner div is aria-hidden so query via container
    expect(container.querySelector("[aria-hidden='true']")).toBeInTheDocument();
  });
});
