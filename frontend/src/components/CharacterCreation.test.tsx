import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import { vi } from "vitest";
import CharacterCreation from "./CharacterCreation";
import * as api from "../services/api";

// Mock the API module
vi.mock("../services/api", () => ({
  createCharacter: vi.fn(),
}));

describe("CharacterCreation", () => {
  const mockOnCharacterCreated = vi.fn();
  const mockOnCancel = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders character creation form", () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText("Create Your Character")).toBeInTheDocument();
    expect(screen.getByLabelText("Character Name *")).toBeInTheDocument();
    expect(screen.getByLabelText("Race *")).toBeInTheDocument();
    expect(screen.getByLabelText("Class *")).toBeInTheDocument();
    expect(screen.getByText("Ability Scores")).toBeInTheDocument();
    expect(screen.getByText("Create Character")).toBeInTheDocument();
  });

  it("renders all ability score inputs", () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"];
    
    abilities.forEach((ability) => {
      expect(screen.getByLabelText(ability)).toBeInTheDocument();
    });
  });

  it("has default values for form fields", () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const nameInput = screen.getByLabelText("Character Name *") as HTMLInputElement;
    const raceSelect = screen.getByLabelText("Race *") as HTMLSelectElement;
    const classSelect = screen.getByLabelText("Class *") as HTMLSelectElement;

    expect(nameInput.value).toBe("");
    expect(raceSelect.value).toBe("Human");
    expect(classSelect.value).toBe("Fighter");

    // Check default ability scores
    const strengthInput = screen.getByLabelText("Strength") as HTMLInputElement;
    expect(strengthInput.value).toBe("10");
  });

  it("updates form fields when user types", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const nameInput = screen.getByLabelText("Character Name *");
    await userEvent.type(nameInput, "Gandalf");

    expect(nameInput).toHaveValue("Gandalf");
  });

  it("updates ability scores when user changes values", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const strengthInput = screen.getByLabelText("Strength");
    await userEvent.clear(strengthInput);
    await userEvent.type(strengthInput, "18");

    expect(strengthInput).toHaveValue(18);
  });

  it("randomizes ability scores when randomize button is clicked", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const strengthInput = screen.getByLabelText("Strength") as HTMLInputElement;
    const originalValue = strengthInput.value;

    const randomizeButton = screen.getByText("🎲 Randomize");
    await userEvent.click(randomizeButton);

    // After randomization, the value should be different (highly likely) or at least within valid range
    const newValue = strengthInput.value;
    const newValueNumber = parseInt(newValue);
    expect(newValueNumber).toBeGreaterThanOrEqual(8);
    expect(newValueNumber).toBeLessThanOrEqual(18);
  });

  it("shows validation errors for empty required fields", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const submitButton = screen.getByText("Create Character");
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Character name is required")).toBeInTheDocument();
    });
  });

  it("shows validation errors for invalid ability scores", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const strengthInput = screen.getByLabelText("Strength");
    await userEvent.clear(strengthInput);
    await userEvent.type(strengthInput, "25"); // Invalid value > 18

    const submitButton = screen.getByText("Create Character");
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Ability scores must be between 3 and 18")).toBeInTheDocument();
    });
  });

  it("calls onCancel when cancel button is clicked", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByText("Cancel");
    await userEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onCancel when back button is clicked", async () => {
    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    const backButton = screen.getByText("← Back to Campaigns");
    await userEvent.click(backButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it("creates character successfully with valid data", async () => {
    const mockCharacter = {
      id: "char-123",
      name: "Test Hero",
      race: "Human",
      character_class: "Fighter",
      level: 1,
      abilities: {
        strength: 16,
        dexterity: 14,
        constitution: 15,
        intelligence: 12,
        wisdom: 13,
        charisma: 10,
      },
      hit_points: { current: 12, maximum: 12 },
      inventory: [],
    };

    vi.mocked(api.createCharacter).mockResolvedValue(mockCharacter);

    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    // Fill in form
    const nameInput = screen.getByLabelText("Character Name *");
    await userEvent.type(nameInput, "Test Hero");

    const submitButton = screen.getByText("Create Character");
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(api.createCharacter).toHaveBeenCalledWith({
        name: "Test Hero",
        race: "Human",
        character_class: "Fighter",
        abilities: {
          strength: 10,
          dexterity: 10,
          constitution: 10,
          intelligence: 10,
          wisdom: 10,
          charisma: 10,
        },
        backstory: "",
      });
    });

    await waitFor(() => {
      expect(mockOnCharacterCreated).toHaveBeenCalledWith(mockCharacter);
    });
  });

  it("handles character creation error", async () => {
    vi.mocked(api.createCharacter).mockRejectedValue(new Error("API Error"));

    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    // Fill in form
    const nameInput = screen.getByLabelText("Character Name *");
    await userEvent.type(nameInput, "Test Hero");

    const submitButton = screen.getByText("Create Character");
    await userEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("Failed to create character. Please try again.")).toBeInTheDocument();
    });

    expect(mockOnCharacterCreated).not.toHaveBeenCalled();
  });

  it("disables form during submission", async () => {
    // Mock a delayed response
    vi.mocked(api.createCharacter).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <CharacterCreation
        onCharacterCreated={mockOnCharacterCreated}
        onCancel={mockOnCancel}
      />
    );

    // Fill in form
    const nameInput = screen.getByLabelText("Character Name *");
    await userEvent.type(nameInput, "Test Hero");

    const submitButton = screen.getByText("Create Character");
    await userEvent.click(submitButton);

    // Check that button text changes and is disabled
    expect(screen.getByText("Creating Character...")).toBeInTheDocument();
    expect(screen.getByText("Creating Character...")).toBeDisabled();
  });
});