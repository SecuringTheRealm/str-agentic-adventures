import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import * as api from "../services/api";
import type { Campaign, Character } from "../services/api";
import GameInterface from "./GameInterface";
import styles from "./GameInterface.module.css";

// Mock the API module
vi.mock("../services/api");
const mockSendPlayerInput = vi.mocked(api.sendPlayerInput);

// Mock the WebSocket hook
vi.mock("../hooks/useWebSocket", () => ({
	useWebSocket: (url: string, options: any) => {
		// Simulate connection failure to trigger fallback
		const isChatWebSocket = url.includes('/chat');
		if (isChatWebSocket && options?.onError) {
			// Trigger error callback to enable fallback
			setTimeout(() => options.onError(new Error('Mock connection failed')), 0);
		}
		return {
			socket: null,
			isConnected: false,
			isConnecting: false,
			error: null,
			connect: vi.fn(),
			disconnect: vi.fn(),
			sendMessage: vi.fn(),
			reconnectAttempts: 0,
		};
	},
}));

// Mock child components
vi.mock("./ChatBox", () => ({
	default: ({
		messages,
		onSendMessage,
		isLoading,
	}: {
		messages: Array<{ text: string }>;
		onSendMessage: (msg: string) => void;
		isLoading: boolean;
	}) => (
		<div data-testid="chat-box">
			<div data-testid="messages">
				{messages.map((msg, idx) => (
					<div key={`${msg.text}-${idx}`}>{msg.text}</div>
				))}
			</div>
			<button
				type="button"
				onClick={() => onSendMessage("test message")}
				disabled={isLoading}
			>
				Send Message
			</button>
		</div>
	),
}));

vi.mock("./CharacterSheet", () => ({
	default: ({ character }: { character: Character }) => (
		<div data-testid="character-sheet">{character.name}</div>
	),
}));

vi.mock("./ImageDisplay", () => ({
	default: ({ imageUrl }: { imageUrl: string | null }) => (
		<div data-testid="image-display">{imageUrl || "No image"}</div>
	),
}));

vi.mock("./BattleMap", () => ({
	default: ({ mapUrl }: { mapUrl: string | null }) => (
		<div data-testid="battle-map">{mapUrl || "No map"}</div>
	),
}));

describe("GameInterface", () => {
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
		inventory: [],
	};

	const mockCampaign: Campaign = {
		id: "1",
		name: "The Lost Kingdom",
		setting: "Medieval Fantasy",
		tone: "heroic",
		homebrew_rules: [],
		characters: ["1"],
		world_description: "A mystical realm awaits.",
	};

	beforeEach(() => {
		mockSendPlayerInput.mockClear();
	});

	it("renders all child components", () => {
		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

		expect(screen.getByTestId("character-sheet")).toBeInTheDocument();
		expect(screen.getByTestId("chat-box")).toBeInTheDocument();
		expect(screen.getByTestId("image-display")).toBeInTheDocument();
	});

	it("displays welcome message on mount", () => {
		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

		const expectedMessage =
			"Welcome, Aragorn! Your adventure in The Lost Kingdom begins now. A mystical realm awaits.";
		expect(screen.getByText(expectedMessage)).toBeInTheDocument();
	});

	it("displays welcome message without world description", () => {
		const campaignWithoutDescription = {
			...mockCampaign,
			world_description: undefined,
		};
		render(
			<GameInterface
				character={mockCharacter}
				campaign={campaignWithoutDescription}
			/>,
		);

		expect(
			screen.getByText(
				/Welcome, Aragorn! Your adventure in The Lost Kingdom begins now\./,
			),
		).toBeInTheDocument();
	});

	it("shows initial world art if available", () => {
		const campaignWithArt = {
			...mockCampaign,
			world_art: { image_url: "https://example.com/world.jpg" },
		};
		render(
			<GameInterface character={mockCharacter} campaign={campaignWithArt} />,
		);

		expect(
			screen.getByText("https://example.com/world.jpg"),
		).toBeInTheDocument();
	});

	it("handles player input and API response", async () => {
		const mockResponse = {
			message: "You see a castle in the distance.",
			images: ["https://example.com/castle.jpg"],
			state_updates: {},
			combat_updates: null,
		};
		mockSendPlayerInput.mockResolvedValue(mockResponse);

		const { rerender } = render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Simulate that the component will use REST API fallback by triggering a re-render after initial setup
		await act(async () => {
			// Wait for initial useEffect to complete
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(mockSendPlayerInput).toHaveBeenCalledWith({
				message: "test message",
				character_id: "1",
				campaign_id: "1",
			});
		});

		await waitFor(() => {
			expect(
				screen.getByText("You see a castle in the distance."),
			).toBeInTheDocument();
		});
	});

	it("updates image when response includes new image", async () => {
		const mockResponse = {
			message: "Response with image",
			images: ["https://example.com/new-image.jpg"],
			state_updates: {},
			combat_updates: null,
		};
		mockSendPlayerInput.mockResolvedValue(mockResponse);

		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Wait for initial setup
		await act(async () => {
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(
				screen.getByText("https://example.com/new-image.jpg"),
			).toBeInTheDocument();
		});
	});

	it("activates combat mode when combat updates received", async () => {
		const mockResponse = {
			message: "Combat begins!",
			images: [],
			state_updates: {},
			combat_updates: {
				status: "active",
				map_url: "https://example.com/battle-map.jpg",
			},
		};
		mockSendPlayerInput.mockResolvedValue(mockResponse);

		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Wait for initial setup
		await act(async () => {
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		// Battle map should not be visible initially
		expect(screen.queryByTestId("battle-map")).not.toBeInTheDocument();

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(screen.getByTestId("battle-map")).toBeInTheDocument();
			expect(
				screen.getByText("https://example.com/battle-map.jpg"),
			).toBeInTheDocument();
		});
	});

	it("handles API errors gracefully", async () => {
		mockSendPlayerInput.mockRejectedValue(new Error("API Error"));

		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Wait for initial setup
		await act(async () => {
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(
				screen.getByText("API Error"),
			).toBeInTheDocument();
		});
	});

	it("shows loading state during API call", async () => {
		let resolvePromise: ((value: unknown) => void) | undefined;
		const promise = new Promise((resolve) => {
			resolvePromise = resolve;
		});
		mockSendPlayerInput.mockReturnValue(promise);

		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Wait for initial setup
		await act(async () => {
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		// Should be disabled during loading
		expect(sendButton).toBeDisabled();

		// Resolve to clean up and wait for completion
		await act(async () => {
			resolvePromise?.({
				message: "Response",
				images: [],
				state_updates: {},
				combat_updates: null,
			});
			await promise;
		});
	});

	it("deactivates combat mode when combat is no longer active", async () => {
		// First activate combat
		const activateCombatResponse = {
			message: "Combat begins!",
			images: [],
			state_updates: {},
			combat_updates: { status: "active", map_url: "battle.jpg" },
		};
		mockSendPlayerInput.mockResolvedValueOnce(activateCombatResponse);

		render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);
		
		// Wait for initial setup
		await act(async () => {
			await new Promise(resolve => setTimeout(resolve, 0));
		});

		const sendButton = screen.getByText("Send Message");
		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(screen.getByTestId("battle-map")).toBeInTheDocument();
		});

		// Then deactivate combat
		const deactivateCombatResponse = {
			message: "Combat ends!",
			images: [],
			state_updates: {},
			combat_updates: { status: "inactive" },
		};
		mockSendPlayerInput.mockResolvedValueOnce(deactivateCombatResponse);

		await userEvent.click(sendButton);

		await waitFor(() => {
			expect(screen.queryByTestId("battle-map")).not.toBeInTheDocument();
		});
	});

	it("has correct CSS structure", () => {
		const { container } = render(
			<GameInterface character={mockCharacter} campaign={mockCampaign} />,
		);

		expect(container.querySelector(`.${styles.gameInterface}`)).toBeInTheDocument();
		expect(container.querySelector(`.${styles.gameContainer}`)).toBeInTheDocument();
		expect(container.querySelector(`.${styles.leftPanel}`)).toBeInTheDocument();
		expect(container.querySelector(`.${styles.centerPanel}`)).toBeInTheDocument();
		expect(container.querySelector(`.${styles.rightPanel}`)).toBeInTheDocument();
	});
});
