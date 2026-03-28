import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import * as api from "../services/api";
import PredefinedCharacters from "./PredefinedCharacters";

vi.mock("../services/api");

describe("PredefinedCharacters", () => {
  const mockOnCharacterSelected = vi.fn();
  const mockOnBack = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.createCharacter).mockResolvedValue({
      id: "created-id",
      name: "Thorin Ironforge",
      race: "dwarf",
      character_class: "fighter",
      abilities: {
        strength: 16,
        dexterity: 10,
        constitution: 15,
        intelligence: 10,
        wisdom: 12,
        charisma: 8,
      },
    });
  });

  it("renders predefined characters list", () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    expect(
      screen.getByText("Choose a Pre-Defined Character")
    ).toBeInTheDocument();
    expect(screen.getByText("Thorin Ironforge")).toBeInTheDocument();
    expect(screen.getByText("Lyralei Swiftarrow")).toBeInTheDocument();
    expect(screen.getByText("Zara Moonwhisper")).toBeInTheDocument();
  });

  it("displays character details correctly", () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    // Check for character basics
    expect(screen.getByText("Level 1 dwarf fighter")).toBeInTheDocument();
    expect(screen.getByText("Level 1 elf ranger")).toBeInTheDocument();

    // Check for ability scores
    expect(screen.getAllByText("STR")).toHaveLength(6); // 6 characters
    expect(screen.getAllByText("DEX")).toHaveLength(6);
  });

  it("calls onBack when back button is clicked", () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    const backButton = screen.getByRole("button", {
      name: "← Back to Character Options",
    });
    fireEvent.click(backButton);

    expect(mockOnBack).toHaveBeenCalledTimes(1);
  });

  it("calls onCharacterSelected when character is selected", async () => {
    render(
      <PredefinedCharacters
        onCharacterSelected={mockOnCharacterSelected}
        onBack={mockOnBack}
      />
    );

    const selectButtons = screen.getAllByText("Select This Character");
    fireEvent.click(selectButtons[0]);

    await waitFor(() => {
      expect(mockOnCharacterSelected).toHaveBeenCalledTimes(1);
    });
    expect(mockOnCharacterSelected).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "Thorin Ironforge",
        race: "dwarf",
        character_class: "fighter",
        id: expect.any(String),
      })
    );
  });
});
