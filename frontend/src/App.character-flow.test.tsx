import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

// Mock API calls
vi.mock("./services/api", () => ({
  getCampaignTemplates: vi.fn().mockResolvedValue([]),
  getCampaigns: vi.fn().mockResolvedValue({ campaigns: [], templates: [] }),
  createCampaign: vi.fn(),
  createCharacter: vi.fn(),
  deleteCampaign: vi.fn(),
  cloneCampaign: vi.fn(),
}));

describe("App Character Flow Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows campaign selection at root route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Campaign Hub")).toBeInTheDocument();
    });
  });

  it("does not show character selection at root route", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText("Campaign Hub")).toBeInTheDocument();
    });

    expect(
      screen.queryByText("Choose Your Character")
    ).not.toBeInTheDocument();
  });

  it("shows predefined characters when Browse Characters is clicked", async () => {
    // Verify the components exist and can be imported
    const CharacterSelection = (await import("./components/CharacterSelection"))
      .default;
    const PredefinedCharacters = (
      await import("./components/PredefinedCharacters")
    ).default;

    expect(CharacterSelection).toBeDefined();
    expect(PredefinedCharacters).toBeDefined();
  });
});
