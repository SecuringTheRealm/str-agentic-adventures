import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChatBox from "./ChatBox";

describe("ChatBox markdown rendering", () => {
  it("renders bold text in DM messages", () => {
    const messages = [
      { sender: "dm" as const, text: "You see a **glowing** sword" },
    ];
    render(
      <ChatBox messages={messages} onSendMessage={() => {}} isLoading={false} />
    );
    const strong = document.querySelector("strong");
    expect(strong).toBeInTheDocument();
    expect(strong?.textContent).toBe("glowing");
  });

  it("renders paragraphs in DM messages", () => {
    const messages = [
      { sender: "dm" as const, text: "First paragraph.\n\nSecond paragraph." },
    ];
    render(
      <ChatBox messages={messages} onSendMessage={() => {}} isLoading={false} />
    );
    const paragraphs = document.querySelectorAll("[role='log'] p");
    expect(paragraphs.length).toBeGreaterThanOrEqual(2);
  });

  it("does not render markdown in player messages", () => {
    const messages = [
      { sender: "player" as const, text: "I cast **fireball**" },
    ];
    render(
      <ChatBox messages={messages} onSendMessage={() => {}} isLoading={false} />
    );
    expect(screen.getByText("I cast **fireball**")).toBeInTheDocument();
  });
});
