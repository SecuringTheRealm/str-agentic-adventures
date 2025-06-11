import { render, screen } from "@testing-library/react";
import React from "react";
import type { Character } from "../services/api";
import CharacterSheet from "./CharacterSheet";

describe("CharacterSheet", () => {
	const mockCharacter: Character = {
		id: "1",
		name: "Aragorn",
		race: "Human",
		class: "Ranger",
		level: 5,
		abilities: {
			strength: 16,
			dexterity: 14,
			constitution: 15,
			intelligence: 12,
			wisdom: 18,
			charisma: 10,
		},
		hitPoints: {
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
		// Find the armor class value specifically by looking for it in the stats area
		const armorClassSection = screen
			.getByText("Armor Class")
			.closest(".armor-class");
		expect(armorClassSection).toHaveTextContent("10");
	});

	it("renders all ability scores", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("STR")).toBeInTheDocument();
		expect(screen.getByText("DEX")).toBeInTheDocument();
		expect(screen.getByText("CON")).toBeInTheDocument();
		expect(screen.getByText("INT")).toBeInTheDocument();
		expect(screen.getByText("WIS")).toBeInTheDocument();
		expect(screen.getByText("CHA")).toBeInTheDocument();

		// Check ability scores in their respective ability sections
		const abilities = screen.getByText("Abilities").closest(".abilities");
		expect(abilities).toHaveTextContent("16"); // STR
		expect(abilities).toHaveTextContent("14"); // DEX
		expect(abilities).toHaveTextContent("15"); // CON
		expect(abilities).toHaveTextContent("12"); // INT
		expect(abilities).toHaveTextContent("18"); // WIS
	});

	it("calculates and displays ability modifiers correctly", () => {
		render(<CharacterSheet character={mockCharacter} />);

		// Check for specific modifiers in the abilities section
		const abilitiesSection = screen
			.getByText("Abilities")
			.closest(".abilities");

		// STR 16 -> +3
		expect(abilitiesSection).toHaveTextContent("+3");
		// WIS 18 -> +4
		expect(abilitiesSection).toHaveTextContent("+4");
		// INT 12 -> +1
		expect(abilitiesSection).toHaveTextContent("+1");
		// CHA 10 -> +0
		expect(abilitiesSection).toHaveTextContent("+0");
		// DEX 14 and CON 15 both give +2, so we expect to find +2 twice
		const plusTwoElements = screen.getAllByText("+2");
		expect(plusTwoElements).toHaveLength(2);
	});

	it("calculates negative ability modifiers correctly", () => {
		const lowStatCharacter: Character = {
			...mockCharacter,
			abilities: {
				strength: 8, // -1
				dexterity: 6, // -2
				constitution: 4, // -3
				intelligence: 10,
				wisdom: 10,
				charisma: 10,
			},
		};

		render(<CharacterSheet character={lowStatCharacter} />);

		expect(screen.getByText("-1")).toBeInTheDocument();
		expect(screen.getByText("-2")).toBeInTheDocument();
		expect(screen.getByText("-3")).toBeInTheDocument();
	});

	it("renders inventory items", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Inventory")).toBeInTheDocument();
		expect(screen.getByText("Longsword")).toBeInTheDocument();
		expect(screen.getByText("Health Potion")).toBeInTheDocument();
		expect(screen.getByText("x3")).toBeInTheDocument(); // Quantity for Health Potion
	});

	it("does not show quantity for items with quantity 1", () => {
		render(<CharacterSheet character={mockCharacter} />);

		const longsword = screen.getByText("Longsword").closest(".inventory-item");
		expect(longsword).not.toHaveTextContent("x1");
	});

	it("handles empty inventory", () => {
		const characterWithEmptyInventory: Character = {
			...mockCharacter,
			inventory: [],
		};

		render(<CharacterSheet character={characterWithEmptyInventory} />);

		expect(screen.getByText("No items in inventory")).toBeInTheDocument();
	});

	it("handles undefined inventory", () => {
		const characterWithUndefinedInventory: Character = {
			...mockCharacter,
			inventory: undefined as unknown as unknown[],
		};

		render(<CharacterSheet character={characterWithUndefinedInventory} />);

		expect(screen.getByText("No items in inventory")).toBeInTheDocument();
	});

	it("has proper CSS classes for styling", () => {
		const { container } = render(<CharacterSheet character={mockCharacter} />);

		expect(container.querySelector(".character-sheet")).toBeInTheDocument();
		expect(container.querySelector(".character-header")).toBeInTheDocument();
		expect(container.querySelector(".abilities-grid")).toBeInTheDocument();
		expect(container.querySelector(".inventory-list")).toBeInTheDocument();
	});

	it("displays abilities section header", () => {
		render(<CharacterSheet character={mockCharacter} />);

		expect(screen.getByText("Abilities")).toBeInTheDocument();
	});
});
