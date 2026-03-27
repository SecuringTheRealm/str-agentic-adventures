import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

// Mock page components to isolate App routing logic
vi.mock("./pages/CampaignSelectionPage", () => ({
  default: () => <div data-testid="campaign-selection-page">Campaign Hub</div>,
}));

vi.mock("./pages/CampaignNewPage", () => ({
  default: () => <div data-testid="campaign-new-page">New Campaign</div>,
}));

vi.mock("./pages/CampaignEditPage", () => ({
  default: () => <div data-testid="campaign-edit-page">Edit Campaign</div>,
}));

vi.mock("./pages/CharacterSelectionPage", () => ({
  default: () => (
    <div data-testid="character-selection-page">Choose Your Character</div>
  ),
}));

vi.mock("./pages/CharacterNewPage", () => ({
  default: () => <div data-testid="character-new-page">New Character</div>,
}));

vi.mock("./pages/GamePage", () => ({
  default: () => <div data-testid="game-page">Game Interface</div>,
}));

function renderWithRouter(initialRoute = "/") {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      <App />
    </MemoryRouter>
  );
}

describe("App", () => {
  it("renders the app header with title", () => {
    renderWithRouter();
    expect(
      screen.getByText("Securing the Realm - Agentic Adventures")
    ).toBeInTheDocument();
  });

  it("shows campaign selection by default", () => {
    renderWithRouter();
    expect(
      screen.getByTestId("campaign-selection-page")
    ).toBeInTheDocument();
  });

  it("routes to character selection page", () => {
    renderWithRouter("/campaigns/test-id/characters");
    expect(
      screen.getByTestId("character-selection-page")
    ).toBeInTheDocument();
  });

  it("routes to game page", () => {
    renderWithRouter("/campaigns/test-id/play/char-1");
    expect(screen.getByTestId("game-page")).toBeInTheDocument();
  });

  it("routes to new campaign page", () => {
    renderWithRouter("/campaigns/new");
    expect(screen.getByTestId("campaign-new-page")).toBeInTheDocument();
  });

  it("redirects unknown routes to campaign selection", () => {
    renderWithRouter("/unknown-route");
    expect(
      screen.getByTestId("campaign-selection-page")
    ).toBeInTheDocument();
  });
});
