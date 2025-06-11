import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import App from "./App";

// Mock the child components to focus on App integration
vi.mock("./components/CampaignCreation", () => ({
	default: ({ onCampaignCreated }: { onCampaignCreated: (campaign: any) => void }) => (
		<div data-testid="campaign-creation">
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
		expect(screen.getByText("AI Dungeon Master")).toBeInTheDocument();
	});

	it("shows campaign creation by default", () => {
		render(<App />);
		expect(screen.getByText("Create a New Campaign")).toBeInTheDocument();
		expect(screen.getByTestId("campaign-creation")).toBeInTheDocument();
	});

	it("switches to game interface after campaign creation", async () => {
		render(<App />);
		
		// Should start with campaign creation
		expect(screen.getByTestId("campaign-creation")).toBeInTheDocument();
		
		// Create a campaign
		await userEvent.click(screen.getByText("Create Campaign"));
		
		// Should now show game interface
		expect(screen.getByTestId("game-interface")).toBeInTheDocument();
		expect(screen.getByText(/Game Interface for Test Campaign/)).toBeInTheDocument();
	});

	it("shows back button when game is started", async () => {
		render(<App />);
		
		// Create a campaign to start the game
		await userEvent.click(screen.getByText("Create Campaign"));
		
		// Should show back button
		expect(screen.getByText("← Back to Campaigns")).toBeInTheDocument();
	});

	it("returns to campaign creation when back button is clicked", async () => {
		render(<App />);
		
		// Start a game
		await userEvent.click(screen.getByText("Create Campaign"));
		expect(screen.getByTestId("game-interface")).toBeInTheDocument();
		
		// Go back
		await userEvent.click(screen.getByText("← Back to Campaigns"));
		
		// Should be back to campaign creation
		expect(screen.getByText("Create a New Campaign")).toBeInTheDocument();
		expect(screen.getByTestId("campaign-creation")).toBeInTheDocument();
	});
});
