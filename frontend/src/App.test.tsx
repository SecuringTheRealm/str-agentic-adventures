import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "./App";

// Mock the child components to focus on App integration
vi.mock("./components/CampaignSelection", () => ({
  default: ({
    onCampaignCreated,
  }: {
    onCampaignCreated: (campaign: any) => void;
  }) => (
    <div data-testid="campaign-selection">
      <button
        type="button"
        onClick={() =>
          onCampaignCreated({
            id: "test-campaign",
            name: "Test Campaign",
            setting: "Test Setting",
            tone: "heroic",
            homebrew_rules: [],
            characters: [],
          })
        }
      >
        Create Campaign
      </button>
    </div>
  ),
}));

vi.mock("./components/CharacterSelection", () => ({
  default: ({
    onCharacterSelected,
  }: {
    campaign: any;
    onCharacterSelected: (character: any) => void;
  }) => (
    <div data-testid="character-selection">
      <button
        type="button"
        onClick={() =>
          onCharacterSelected({
            id: "test-character",
            name: "Test Character",
            race: "human",
            character_class: "fighter",
            level: 1,
            abilities: {
              strength: 15,
              dexterity: 14,
              constitution: 13,
              intelligence: 12,
              wisdom: 10,
              charisma: 8,
            },
            hit_points: { current: 10, maximum: 10 },
            inventory: [],
          })
        }
      >
        Select Character
      </button>
    </div>
  ),
}));

vi.mock("./components/GameInterface", () => ({
  default: ({ campaign, character }: { campaign: any; character: any }) => (
    <div data-testid="game-interface">
      Game Interface for {campaign.name} with {character.name}
    </div>
  ),
}));

describe("App", () => {
  it("renders the app header with title", () => {
    render(<App />);
    expect(
      screen.getByText("Securing the Realm - Agentic Adventures")
    ).toBeInTheDocument();
  });

  it("shows campaign selection by default", () => {
    render(<App />);
    expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
  });

  it("shows character selection after campaign creation", async () => {
    render(<App />);

    // Should start with campaign selection
    expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();

    // Create a campaign
    await userEvent.click(screen.getByText("Create Campaign"));

    // Should now show character selection
    expect(screen.getByTestId("character-selection")).toBeInTheDocument();
  });

  it("switches to game interface after character selection", async () => {
    render(<App />);

    // Create a campaign
    await userEvent.click(screen.getByText("Create Campaign"));

    // Select a character
    await userEvent.click(screen.getByText("Select Character"));

    // Should now show game interface
    expect(screen.getByTestId("game-interface")).toBeInTheDocument();
    expect(
      screen.getByText(/Game Interface for Test Campaign/)
    ).toBeInTheDocument();
  });

  it("shows back button when game is started", async () => {
    render(<App />);

    // Create a campaign and select character to start the game
    await userEvent.click(screen.getByText("Create Campaign"));
    await userEvent.click(screen.getByText("Select Character"));

    // Should show back button
    expect(screen.getByText("← Back to Campaigns")).toBeInTheDocument();
  });

  it("returns to campaign selection when back button is clicked", async () => {
    render(<App />);

    // Start a game
    await userEvent.click(screen.getByText("Create Campaign"));
    await userEvent.click(screen.getByText("Select Character"));
    expect(screen.getByTestId("game-interface")).toBeInTheDocument();

    // Go back
    await userEvent.click(screen.getByText("← Back to Campaigns"));

    // Should be back to campaign selection
    expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
  });
});
