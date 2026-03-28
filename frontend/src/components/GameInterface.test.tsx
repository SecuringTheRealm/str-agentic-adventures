import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import * as api from "../services/api";
import type { Campaign, Character } from "../types";
import GameInterface from "./GameInterface";
import styles from "./GameInterface.module.css";

// Mock the API module
vi.mock("../services/api");
const mockSendPlayerInput = vi.mocked(api.sendPlayerInput);
const mockGetOpeningNarrative = vi.mocked(api.getOpeningNarrative);
const mockGetVisualGenerationStatus = vi.mocked(api.getVisualGenerationStatus);
const mockGenerateImage = vi.mocked(api.generateImage);
const mockGenerateBattleMap = vi.mocked(api.generateBattleMap);

const { mockToastError, mockToastSuccess } = vi.hoisted(() => ({
  mockToastError: vi.fn(),
  mockToastSuccess: vi.fn(),
}));

vi.mock("sonner", () => ({
  toast: {
    error: mockToastError,
    success: mockToastSuccess,
  },
}));

// Mock the WebSocket SDK hook
vi.mock("../hooks/useWebSocketSDK", () => ({
  useWebSocketSDK: (options: any) => {
    // Simulate connection failure for chat to trigger fallback
    const isChatWebSocket = options.connectionType === "chat";
    if (isChatWebSocket && options?.onError) {
      // Trigger error callback to enable fallback
      setTimeout(() => options.onError(new Error("Mock connection failed")), 0);
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
    suggestedActions,
    onSuggestedAction,
  }: {
    messages: Array<{ text: string }>;
    onSendMessage: (msg: string) => void;
    isLoading: boolean;
    suggestedActions?: string[];
    onSuggestedAction?: (action: string) => void;
  }) => (
    <div data-testid="chat-box">
      <div data-testid="messages">
        {messages.map((msg, idx) => (
          <div key={`${msg.text}-${idx}`}>{msg.text}</div>
        ))}
      </div>
      {suggestedActions && suggestedActions.length > 0 && (
        <div data-testid="suggested-actions">
          {suggestedActions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => (onSuggestedAction ?? onSendMessage)(action)}
            >
              {action}
            </button>
          ))}
        </div>
      )}
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
    race: "human",
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

  const defaultOpeningNarrative = {
    scene_description: "The adventure begins in a mystical realm.",
    quest_hook: "A mysterious message arrives at dawn.",
    suggested_actions: ["Explore the area", "Talk to locals"],
    help_text: "What can I do?",
  };

  beforeEach(() => {
    mockSendPlayerInput.mockClear();
    mockGetOpeningNarrative.mockResolvedValue(defaultOpeningNarrative);
    mockGetVisualGenerationStatus.mockResolvedValue({
      available: true,
      status: "healthy",
      message: null,
    });
    mockGenerateImage.mockReset();
    mockGenerateBattleMap.mockReset();
    mockToastError.mockReset();
    mockToastSuccess.mockReset();
  });

  it("renders all child components", async () => {
    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(screen.getByTestId("character-sheet")).toBeInTheDocument();
    expect(screen.getByTestId("chat-box")).toBeInTheDocument();
    expect(screen.getByTestId("image-display")).toBeInTheDocument();
  });

  it("displays opening narrative on mount", async () => {
    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await waitFor(() => {
      expect(mockGetOpeningNarrative).toHaveBeenCalledWith("1", {
        name: "Aragorn",
        character_class: "Ranger",
        race: "human",
        backstory: undefined,
      });
    });

    await waitFor(() => {
      expect(
        screen.getByText(
          /The adventure begins in a mystical realm\..*A mysterious message arrives at dawn\./s
        )
      ).toBeInTheDocument();
    });
  });

  it("shows loading placeholder before narrative arrives", async () => {
    // Use a never-resolving promise to freeze the component in loading state
    mockGetOpeningNarrative.mockReturnValue(new Promise(() => {}));

    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    // The "Setting the scene" placeholder should appear immediately
    await waitFor(() => {
      expect(
        screen.getByText(/Setting the scene for Aragorn's adventure/)
      ).toBeInTheDocument();
    });
  });

  it("shows suggested actions after opening narrative", async () => {
    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await waitFor(() => {
      expect(screen.getByTestId("suggested-actions")).toBeInTheDocument();
      expect(screen.getByText("Explore the area")).toBeInTheDocument();
      expect(screen.getByText("Talk to locals")).toBeInTheDocument();
    });
  });

  it("falls back to welcome message when opening narrative fails", async () => {
    mockGetOpeningNarrative.mockRejectedValue(new Error("Network error"));

    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await waitFor(() => {
      expect(
        screen.getByText(
          /Welcome, Aragorn! Your adventure in The Lost Kingdom begins now\./
        )
      ).toBeInTheDocument();
    });
  });

  it("falls back to welcome message when no campaign id", async () => {
    const campaignWithoutId = { ...mockCampaign, id: undefined };
    render(
      <GameInterface character={mockCharacter} campaign={campaignWithoutId} />
    );

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(
      screen.getByText(
        /Welcome, Aragorn! Your adventure in The Lost Kingdom begins now\./
      )
    ).toBeInTheDocument();
    expect(mockGetOpeningNarrative).not.toHaveBeenCalled();
  });

  it("shows initial world art if available", async () => {
    const campaignWithArt = {
      ...mockCampaign,
      world_art: { image_url: "https://example.com/world.jpg" },
    };
    render(
      <GameInterface character={mockCharacter} campaign={campaignWithArt} />
    );

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(
      screen.getByText("https://example.com/world.jpg")
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

    const { rerender } = render(
      <GameInterface character={mockCharacter} campaign={mockCampaign} />
    );

    // Simulate that the component will use REST API fallback by triggering a re-render after initial setup
    await act(async () => {
      // Wait for initial useEffect to complete
      await new Promise((resolve) => setTimeout(resolve, 0));
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
        screen.getByText("You see a castle in the distance.")
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
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    const sendButton = screen.getByText("Send Message");
    await userEvent.click(sendButton);

    await waitFor(() => {
      expect(
        screen.getByText("https://example.com/new-image.jpg")
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
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Battle map should not be visible initially
    expect(screen.queryByTestId("battle-map")).not.toBeInTheDocument();

    const sendButton = screen.getByText("Send Message");
    await userEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByTestId("battle-map")).toBeInTheDocument();
      expect(
        screen.getByText("https://example.com/battle-map.jpg")
      ).toBeInTheDocument();
    });
  });

  it("handles API errors gracefully", async () => {
    mockSendPlayerInput.mockRejectedValue(new Error("API Error"));

    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    // Wait for initial setup
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    const sendButton = screen.getByText("Send Message");
    await userEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText("API Error")).toBeInTheDocument();
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
      await new Promise((resolve) => setTimeout(resolve, 0));
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
      await new Promise((resolve) => setTimeout(resolve, 0));
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
      <GameInterface character={mockCharacter} campaign={mockCampaign} />
    );

    expect(
      container.querySelector(`.${styles.gameInterface}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.gameContainer}`)
    ).toBeInTheDocument();
    expect(container.querySelector(`.${styles.leftPanel}`)).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.centerPanel}`)
    ).toBeInTheDocument();
    expect(
      container.querySelector(`.${styles.rightPanel}`)
    ).toBeInTheDocument();
  });

  it("disables visual generation controls when image generation is unavailable", async () => {
    mockGetVisualGenerationStatus.mockResolvedValue({
      available: false,
      status: "unavailable",
      message:
        "Visual generation is unavailable because image generation is not configured.",
    });

    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await waitFor(() => {
      expect(screen.getByTestId("visual-generation-status")).toHaveTextContent(
        "Visual generation is unavailable because image generation is not configured."
      );
    });

    expect(screen.getByTestId("generate-portrait-button")).toBeDisabled();
    expect(screen.getByTestId("generate-scene-button")).toBeDisabled();
    expect(screen.getByTestId("generate-battle-map-button")).toBeDisabled();
  });

  it("shows a toast instead of adding a DM message when portrait generation fails", async () => {
    mockGenerateImage.mockRejectedValue(new Error("Image service offline"));

    render(<GameInterface character={mockCharacter} campaign={mockCampaign} />);

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    await userEvent.click(screen.getByTestId("generate-portrait-button"));

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("Character portrait failed", {
        description: "Image service offline",
      });
    });

    expect(screen.queryByText("Image service offline")).not.toBeInTheDocument();
  });
});
