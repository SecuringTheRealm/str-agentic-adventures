import { render, screen } from "@testing-library/react";
import React from "react";
import type { Character } from "../services/api";
import CharacterSheet from "./CharacterSheet";

describe("CharacterSheet", () => {
	const mockCharacter: Character = {
		id: "1",
		name: "Aragorn",
		race: "Human",
		character_class: "Ranger",
		level: 5,
		abilities: {
			strength: 16,
			dexterity: 14,
			constitution: 15,
			intelligence: 12,
			wisdom: 18,
			charisma: 10,
		},
		hit_points: {
			current: 45,
			maximum: 50,
		},
		inventory: [
			{ name: "Longsword", quantity: 1 },
			{ name: "Health Potion", quantity: 3 },
		],
	};

	it("renders character basic information", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Aragorn")).toBeInTheDocument();
		expect(screen.getByText("Level 5 Human Ranger")).toBeInTheDocument();
	});

	it("renders hit points correctly", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Hit Points")).toBeInTheDocument();
		expect(screen.getByText("45 / 50")).toBeInTheDocument();
	});

	it("renders armor class", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Armor Class")).toBeInTheDocument();
		// Look for default armor class value
		expect(screen.getByText("10")).toBeInTheDocument();
	});

	it("renders all ability scores", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("STR")).toBeInTheDocument();
		expect(screen.getByText("DEX")).toBeInTheDocument();
		expect(screen.getByText("CON")).toBeInTheDocument();
		expect(screen.getByText("INT")).toBeInTheDocument();
		expect(screen.getByText("WIS")).toBeInTheDocument();
		expect(screen.getByText("CHA")).toBeInTheDocument();

		// Check for ability scores being displayed
		expect(screen.getByText("16")).toBeInTheDocument(); // STR
		expect(screen.getByText("14")).toBeInTheDocument(); // DEX
		expect(screen.getByText("15")).toBeInTheDocument(); // CON
		expect(screen.getByText("12")).toBeInTheDocument(); // INT
		expect(screen.getByText("18")).toBeInTheDocument(); // WIS
	});

	it("calculates and displays ability modifiers correctly", () => {
		render(<CharacterSheet character={mockCharacter} />);

		// Check for specific modifiers
		expect(screen.getByText("+3")).toBeInTheDocument(); // STR 16 -> +3
		expect(screen.getByText("+4")).toBeInTheDocument(); // WIS 18 -> +4
		expect(screen.getByText("+1")).toBeInTheDocument(); // INT 12 -> +1
		expect(screen.getByText("+0")).toBeInTheDocument(); // CHA 10 -> +0

		// DEX 14 and CON 15 both give +2
		const plusTwoElements = screen.getAllByText("+2");
		expect(plusTwoElements.length).toBeGreaterThanOrEqual(2);
	});

	it("calculates negative ability modifiers correctly", () => {
		const lowStatCharacter: Character = {
			...mockCharacter,
			abilities: {
				strength: 8, // -1
				dexterity: 6, // -2
				constitution: 4, // -3
				intelligence: 2, // -4
				wisdom: 1, // -5
				charisma: 10, // +0
			},
		};

		render(<CharacterSheet character={lowStatCharacter} />);

		// Check for negative modifiers
		expect(screen.getByText("-1")).toBeInTheDocument(); // STR 8
		expect(screen.getByText("-2")).toBeInTheDocument(); // DEX 6
		expect(screen.getByText("-3")).toBeInTheDocument(); // CON 4
		expect(screen.getByText("-4")).toBeInTheDocument(); // INT 2
		expect(screen.getByText("-5")).toBeInTheDocument(); // WIS 1
	});

	it("handles character with empty inventory", () => {
		const emptyInventoryCharacter: Character = {
			...mockCharacter,
			inventory: [],
		};

		render(<CharacterSheet character={emptyInventoryCharacter} />);

		expect(screen.getByText("Inventory")).toBeInTheDocument();
		// Should handle empty inventory gracefully without errors
		expect(screen.getByText("Aragorn")).toBeInTheDocument();
	});

	it("handles character without optional properties", () => {
		// Character interface doesn't include spells or experience, so test other edge cases
		const basicCharacter: Character = {
			...mockCharacter,
		};

		render(<CharacterSheet character={basicCharacter} />);

		// Should still render without errors
		expect(screen.getByText("Aragorn")).toBeInTheDocument();
	});

	it("renders inventory items correctly", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Inventory")).toBeInTheDocument();
		expect(screen.getByText("Longsword (1)")).toBeInTheDocument();
		expect(screen.getByText("Health Potion (3)")).toBeInTheDocument();
	});

	it("handles extreme ability scores correctly", () => {
		const extremeCharacter: Character = {
			...mockCharacter,
			abilities: {
				strength: 30, // +10 modifier
				dexterity: 1, // -5 modifier
				constitution: 20, // +5 modifier
				intelligence: 8, // -1 modifier
				wisdom: 13, // +1 modifier
				charisma: 6, // -2 modifier
			},
		};

		render(<CharacterSheet character={extremeCharacter} />);

		// Should show extreme modifiers correctly
		expect(screen.getByText("+10")).toBeInTheDocument(); // STR 30
		expect(screen.getByText("-5")).toBeInTheDocument(); // DEX 1
		expect(screen.getByText("+5")).toBeInTheDocument(); // CON 20
		expect(screen.getByText("-1")).toBeInTheDocument(); // INT 8
		expect(screen.getByText("+1")).toBeInTheDocument(); // WIS 13
		expect(screen.getByText("-2")).toBeInTheDocument(); // CHA 6
	});

	it("handles character data consistency", () => {
		// Test with regular character data since experience isn't in the interface
		render(<CharacterSheet character={mockCharacter} />);

		// Should show character level
		expect(screen.getByText(/Level 5/)).toBeInTheDocument();
	});

	it("handles minimal character data gracefully", () => {
		const minimalCharacter: Character = {
			id: "minimal",
			name: "Basic Hero",
			race: "Human",
			character_class: "Fighter",
			level: 1,
			abilities: {
				strength: 10,
				dexterity: 10,
				constitution: 10,
				intelligence: 10,
				wisdom: 10,
				charisma: 10,
			},
			hit_points: {
				current: 10,
				maximum: 10,
			},
			inventory: [],
		};

		render(<CharacterSheet character={minimalCharacter} />);

		// Should render successfully with minimal data
		expect(screen.getByText("Basic Hero")).toBeInTheDocument();
		expect(screen.getByText("Level 1 Human Fighter")).toBeInTheDocument();
		expect(screen.getByText("10 / 10")).toBeInTheDocument();

		// All ability modifiers should be +0
		const zeroModifiers = screen.getAllByText("+0");
		expect(zeroModifiers.length).toBe(6); // All 6 abilities should show +0
	});

	it("displays different character classes correctly", () => {
		const wizardCharacter: Character = {
			...mockCharacter,
			character_class: "Wizard",
			name: "Gandalf",
		};

		render(<CharacterSheet character={wizardCharacter} />);

		expect(screen.getByText("Gandalf")).toBeInTheDocument();
		expect(screen.getByText(/Wizard/)).toBeInTheDocument();
	});

	it("displays different races correctly", () => {
		const elfCharacter: Character = {
			...mockCharacter,
			race: "Elf",
			name: "Legolas",
		};

		render(<CharacterSheet character={elfCharacter} />);

		expect(screen.getByText("Legolas")).toBeInTheDocument();
		expect(screen.getByText(/Elf/)).toBeInTheDocument();
	});

	it("handles high level characters", () => {
		const highLevelCharacter: Character = {
			...mockCharacter,
			level: 20,
		};

		render(<CharacterSheet character={highLevelCharacter} />);

		expect(screen.getByText(/Level 20/)).toBeInTheDocument();
	});

	it("handles very low hit points scenarios", () => {
		const lowHpCharacter: Character = {
			...mockCharacter,
			hit_points: {
				current: 0,
				maximum: 30,
			},
		};

		render(<CharacterSheet character={lowHpCharacter} />);

		expect(screen.getByText("0 / 30")).toBeInTheDocument();
	});

	it("handles characters with no armor class modifier", () => {
		render(<CharacterSheet character={mockCharacter} />);

		// Default armor class should be shown
		expect(screen.getByText("Armor Class")).toBeInTheDocument();
		expect(screen.getByText("10")).toBeInTheDocument();
	});
});
