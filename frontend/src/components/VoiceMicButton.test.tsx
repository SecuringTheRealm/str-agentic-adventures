import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import VoiceMicButton from "./VoiceMicButton";

describe("VoiceMicButton", () => {
  it("renders mic button with accessible label", () => {
    render(
      <VoiceMicButton
        isListening={false}
        disabled={false}
        onPressStart={() => {}}
        onPressEnd={() => {}}
      />
    );
    expect(
      screen.getByRole("button", { name: /microphone/i })
    ).toBeInTheDocument();
  });

  it("calls onPressStart on mousedown", () => {
    const onStart = vi.fn();
    render(
      <VoiceMicButton
        isListening={false}
        disabled={false}
        onPressStart={onStart}
        onPressEnd={() => {}}
      />
    );
    fireEvent.mouseDown(screen.getByRole("button"));
    expect(onStart).toHaveBeenCalled();
  });

  it("calls onPressEnd on mouseup", () => {
    const onEnd = vi.fn();
    render(
      <VoiceMicButton
        isListening={false}
        disabled={false}
        onPressStart={() => {}}
        onPressEnd={onEnd}
      />
    );
    fireEvent.mouseUp(screen.getByRole("button"));
    expect(onEnd).toHaveBeenCalled();
  });

  it("shows active state when listening", () => {
    render(
      <VoiceMicButton
        isListening={true}
        disabled={false}
        onPressStart={() => {}}
        onPressEnd={() => {}}
      />
    );
    expect(screen.getByRole("button").getAttribute("data-listening")).toBe(
      "true"
    );
  });

  it("is disabled when disabled prop is true", () => {
    render(
      <VoiceMicButton
        isListening={false}
        disabled={true}
        onPressStart={() => {}}
        onPressEnd={() => {}}
      />
    );
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
