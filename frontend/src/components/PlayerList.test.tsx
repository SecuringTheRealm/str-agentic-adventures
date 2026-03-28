import { render, screen } from "@testing-library/react";
import type { SessionParticipant } from "@/types";
import PlayerList from "./PlayerList";

const makeParticipant = (
  overrides: Partial<SessionParticipant> = {}
): SessionParticipant => ({
  id: "p1",
  session_id: "s1",
  character_id: "c1",
  player_name: "Alice",
  is_dm: false,
  is_connected: true,
  ...overrides,
});

describe("PlayerList", () => {
  it("renders empty state when no participants", () => {
    render(<PlayerList participants={[]} />);
    expect(screen.getByText("No players have joined yet.")).toBeInTheDocument();
  });

  it("renders player names", () => {
    const participants = [
      makeParticipant({ id: "p1", player_name: "Alice" }),
      makeParticipant({ id: "p2", player_name: "Bob", character_id: "c2" }),
    ];
    render(<PlayerList participants={participants} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("shows DM badge for DM participants", () => {
    const participants = [makeParticipant({ is_dm: true })];
    render(<PlayerList participants={participants} />);
    expect(screen.getByText("DM")).toBeInTheDocument();
  });

  it("does not show DM badge for non-DM participants", () => {
    const participants = [makeParticipant({ is_dm: false })];
    render(<PlayerList participants={participants} />);
    expect(screen.queryByText("DM")).not.toBeInTheDocument();
  });

  it("shows Turn badge for current turn player", () => {
    const participants = [
      makeParticipant({ id: "p1", character_id: "c1" }),
      makeParticipant({ id: "p2", character_id: "c2", player_name: "Bob" }),
    ];
    render(
      <PlayerList participants={participants} currentTurnCharacterId="c1" />
    );
    const turnBadges = screen.getAllByText("Turn");
    expect(turnBadges).toHaveLength(1);
  });

  it("shows green dot for connected and gray for disconnected", () => {
    const participants = [
      makeParticipant({ id: "p1", is_connected: true }),
      makeParticipant({
        id: "p2",
        is_connected: false,
        player_name: "Bob",
        character_id: "c2",
      }),
    ];
    render(<PlayerList participants={participants} />);

    const connectedDot = screen.getByTestId("status-p1");
    const disconnectedDot = screen.getByTestId("status-p2");
    expect(connectedDot.className).toContain("connected");
    expect(disconnectedDot.className).toContain("disconnected");
  });

  it("renders the Players heading", () => {
    render(<PlayerList participants={[]} />);
    expect(screen.getByText("Players")).toBeInTheDocument();
  });
});
