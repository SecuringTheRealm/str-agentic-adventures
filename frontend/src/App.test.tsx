import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import App from "./App";

// Mock the child components to focus on App integration
vi.mock("./components/CampaignSelection", () => ({
	default: ({ onCampaignCreated }: { onCampaignCreated: (campaign: any) => void }) => (
		<div data-testid="campaign-selection">
			<button 
				onClick={() => onCampaignCreated({
					id: "test-campaign",
					name: "Test Campaign",
					setting: "Test Setting",
					tone: "heroic",
					homebrew_rules: [],
					characters: []
				})}
			>
				Create Campaign
			</button>
		</div>
	),
}));

vi.mock("./components/CharacterCreation", () => ({
	default: ({ onCharacterCreated, onCancel }: { 
		onCharacterCreated: (character: any) => void;
		onCancel: () => void;
	}) => (
		<div data-testid="character-creation">
			<button 
				onClick={() => onCharacterCreated({
					id: "test-character",
					name: "Test Character",
					race: "Human",
					character_class: "Fighter",
					level: 1,
					abilities: {
						strength: 16,
						dexterity: 14,
						constitution: 15,
						intelligence: 12,
						wisdom: 13,
						charisma: 10
					},
					hit_points: { current: 12, maximum: 12 },
					inventory: []
				})}
			>
				Create Character
			</button>
			<button onClick={onCancel}>
				Cancel Character Creation
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
		expect(screen.getByText("Securing the Realm - Agentic Adventures")).toBeInTheDocument();
	});

	it("shows campaign selection by default", () => {
		render(<App />);
		expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
	});

	it("switches to character creation after campaign selection", async () => {
		render(<App />);
		
		// Should start with campaign selection
		expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
		
		// Create a campaign
		await userEvent.click(screen.getByText("Create Campaign"));
		
		// Should now show character creation
		await waitFor(() => {
			expect(screen.getByTestId("character-creation")).toBeInTheDocument();
		});
	});

	it("switches to game interface after character creation", async () => {
		render(<App />);
		
		// Create a campaign
		await userEvent.click(screen.getByText("Create Campaign"));
		
		// Should show character creation
		await waitFor(() => {
			expect(screen.getByTestId("character-creation")).toBeInTheDocument();
		});
		
		// Create a character
		await userEvent.click(screen.getByText("Create Character"));
		
		// Should now show game interface
		await waitFor(() => {
			expect(screen.getByTestId("game-interface")).toBeInTheDocument();
			expect(screen.getByText(/Game Interface for Test Campaign with Test Character/)).toBeInTheDocument();
		});
	});

	it("shows back button when game is started", async () => {
		render(<App />);
		
		// Create a campaign and character to start the game
		await userEvent.click(screen.getByText("Create Campaign"));
		await waitFor(() => expect(screen.getByTestId("character-creation")).toBeInTheDocument());
		
		await userEvent.click(screen.getByText("Create Character"));
		await waitFor(() => expect(screen.getByTestId("game-interface")).toBeInTheDocument());
		
		// Should show back button
		expect(screen.getByText("← Back to Campaigns")).toBeInTheDocument();
	});

	it("returns to campaign selection when back button is clicked from game", async () => {
		render(<App />);
		
		// Start a game
		await userEvent.click(screen.getByText("Create Campaign"));
		await waitFor(() => expect(screen.getByTestId("character-creation")).toBeInTheDocument());
		
		await userEvent.click(screen.getByText("Create Character"));
		await waitFor(() => expect(screen.getByTestId("game-interface")).toBeInTheDocument());
		
		// Go back
		await userEvent.click(screen.getByText("← Back to Campaigns"));
		
		// Should be back to campaign selection
		await waitFor(() => {
			expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
		});
	});

	it("returns to campaign selection when character creation is cancelled", async () => {
		render(<App />);
		
		// Create a campaign
		await userEvent.click(screen.getByText("Create Campaign"));
		await waitFor(() => expect(screen.getByTestId("character-creation")).toBeInTheDocument());
		
		// Cancel character creation
		await userEvent.click(screen.getByText("Cancel Character Creation"));
		
		// Should be back to campaign selection
		await waitFor(() => {
			expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
		});
	});

	it("follows complete flow: campaign → character → game", async () => {
		render(<App />);
		
		// Step 1: Campaign selection
		expect(screen.getByTestId("campaign-selection")).toBeInTheDocument();
		
		// Step 2: Create campaign → Character creation
		await userEvent.click(screen.getByText("Create Campaign"));
		await waitFor(() => expect(screen.getByTestId("character-creation")).toBeInTheDocument());
		
		// Step 3: Create character → Game interface
		await userEvent.click(screen.getByText("Create Character"));
		await waitFor(() => {
			expect(screen.getByTestId("game-interface")).toBeInTheDocument();
			expect(screen.getByText(/Game Interface for Test Campaign with Test Character/)).toBeInTheDocument();
		});
	});
});
