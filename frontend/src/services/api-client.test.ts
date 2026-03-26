/**
 * Tests for the openapi-fetch API client integration.
 *
 * Validates that the typed client is properly configured and that the
 * service wrapper functions in api.ts work correctly.
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  type Campaign,
  type CampaignCreateRequest,
  type Character,
  type CharacterCreateRequest,
  createCampaign,
  createCharacter,
  getCampaign,
  getCampaigns,
  getCharacter,
  rollDice,
  sendPlayerInput,
  wsClient,
} from "./api";

// Mock the openapi-fetch client module
vi.mock("../api-client/client", () => {
  const mockGet = vi.fn();
  const mockPost = vi.fn();
  const mockPut = vi.fn();
  const mockDelete = vi.fn();
  return {
    api: {
      GET: mockGet,
      POST: mockPost,
      PUT: mockPut,
      DELETE: mockDelete,
    },
  };
});

// Import the mocked client so we can set up return values
import { api } from "../api-client/client";

const mockApi = api as {
  GET: ReturnType<typeof vi.fn>;
  POST: ReturnType<typeof vi.fn>;
  PUT: ReturnType<typeof vi.fn>;
  DELETE: ReturnType<typeof vi.fn>;
};

describe("openapi-fetch API Client Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("API Client Setup", () => {
    it("should have the typed API client available", () => {
      expect(api).toBeDefined();
      expect(api.GET).toBeDefined();
      expect(api.POST).toBeDefined();
      expect(api.PUT).toBeDefined();
      expect(api.DELETE).toBeDefined();
    });
  });

  describe("Character API", () => {
    it("should create a character via POST /game/character", async () => {
      const mockCharacter: Character = {
        id: "test-id",
        name: "Test Hero",
        race: "human",
        character_class: "fighter",
        level: 1,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      mockApi.POST.mockResolvedValue({ data: mockCharacter, error: undefined });

      const request: CharacterCreateRequest = {
        name: "Test Hero",
        race: "Human",
        character_class: "Fighter",
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      const result = await createCharacter(request);
      expect(result).toEqual(mockCharacter);
      expect(mockApi.POST).toHaveBeenCalledWith("/game/character", {
        body: expect.objectContaining({
          name: "Test Hero",
          race: "human",
          character_class: "fighter",
        }),
      });
    });

    it("should normalise race and class to lowercase", async () => {
      mockApi.POST.mockResolvedValue({
        data: { id: "1", name: "Hero" },
        error: undefined,
      });

      await createCharacter({
        name: "Hero",
        race: "ELF",
        character_class: "WIZARD",
        abilities: {
          strength: 10,
          dexterity: 10,
          constitution: 10,
          intelligence: 10,
          wisdom: 10,
          charisma: 10,
        },
      });

      const callBody = mockApi.POST.mock.calls[0][1].body;
      expect(callBody.race).toBe("elf");
      expect(callBody.character_class).toBe("wizard");
    });

    it("should retrieve a character via GET /game/character/{id}", async () => {
      const mockCharacter: Character = {
        id: "test-id",
        name: "Test Hero",
        race: "human",
        character_class: "fighter",
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      mockApi.GET.mockResolvedValue({ data: mockCharacter, error: undefined });

      const result = await getCharacter("test-id");
      expect(result).toEqual(mockCharacter);
      expect(mockApi.GET).toHaveBeenCalledWith(
        "/game/character/{character_id}",
        {
          params: { path: { character_id: "test-id" } },
        }
      );
    });

    it("should throw on API error", async () => {
      mockApi.POST.mockResolvedValue({
        data: undefined,
        error: { detail: "Validation error" },
      });

      await expect(
        createCharacter({
          name: "Test",
          race: "Human",
          character_class: "Fighter",
          abilities: {
            strength: 16,
            dexterity: 14,
            constitution: 15,
            intelligence: 12,
            wisdom: 13,
            charisma: 10,
          },
        })
      ).rejects.toEqual({ detail: "Validation error" });
    });
  });

  describe("Campaign API", () => {
    it("should create a campaign via POST /game/campaign", async () => {
      const mockCampaign: Campaign = {
        id: "campaign-1",
        name: "Test Campaign",
        setting: "Fantasy",
      };

      mockApi.POST.mockResolvedValue({ data: mockCampaign, error: undefined });

      const request: CampaignCreateRequest = {
        name: "Test Campaign",
        setting: "Fantasy",
      };

      const result = await createCampaign(request);
      expect(result).toEqual(mockCampaign);
      expect(mockApi.POST).toHaveBeenCalledWith("/game/campaign", {
        body: request,
      });
    });

    it("should list campaigns via GET /game/campaigns", async () => {
      const mockCampaigns: Campaign[] = [
        { id: "1", name: "Campaign One" },
        { id: "2", name: "Campaign Two" },
      ];

      mockApi.GET.mockResolvedValue({ data: mockCampaigns, error: undefined });

      const result = await getCampaigns();
      expect(result).toEqual(mockCampaigns);
      expect(mockApi.GET).toHaveBeenCalledWith("/game/campaigns");
    });

    it("should retrieve a campaign via GET /game/campaign/{id}", async () => {
      const mockCampaign: Campaign = { id: "1", name: "Test" };

      mockApi.GET.mockResolvedValue({ data: mockCampaign, error: undefined });

      const result = await getCampaign("1");
      expect(result).toEqual(mockCampaign);
      expect(mockApi.GET).toHaveBeenCalledWith("/game/campaign/{campaign_id}", {
        params: { path: { campaign_id: "1" } },
      });
    });
  });

  describe("Player Input", () => {
    it("should send player input via POST /game/input", async () => {
      const mockResponse = { message: "The dragon attacks!", images: [] };
      mockApi.POST.mockResolvedValue({ data: mockResponse, error: undefined });

      const result = await sendPlayerInput({
        character_id: "char-1",
        campaign_id: "camp-1",
        message: "I attack the dragon",
      });

      expect(result).toEqual(mockResponse);
      expect(mockApi.POST).toHaveBeenCalledWith("/game/input", {
        body: {
          character_id: "char-1",
          campaign_id: "camp-1",
          message: "I attack the dragon",
        },
      });
    });
  });

  describe("Dice Roll API", () => {
    it("should roll dice via POST /game/dice/roll", async () => {
      const mockResult = { notation: "1d20", rolls: [15], total: 15 };
      mockApi.POST.mockResolvedValue({ data: mockResult, error: undefined });

      const result = await rollDice("1d20");
      expect(result).toEqual(mockResult);
      expect(mockApi.POST).toHaveBeenCalledWith("/game/dice/roll", {
        body: { notation: "1d20" },
      });
    });

    it("should roll with character via POST /game/dice/roll-with-character", async () => {
      const mockResult = {
        notation: "1d20",
        rolls: [15],
        total: 17,
        character_bonus: 2,
      };
      mockApi.POST.mockResolvedValue({ data: mockResult, error: undefined });

      const result = await rollDice("1d20", "char-1", "athletics");
      expect(result).toEqual(mockResult);
      expect(mockApi.POST).toHaveBeenCalledWith(
        "/game/dice/roll-with-character",
        {
          body: {
            notation: "1d20",
            character_id: "char-1",
            skill: "athletics",
          },
        }
      );
    });
  });

  describe("WebSocket Client Integration", () => {
    it("should export WebSocket client instance", () => {
      expect(wsClient).toBeDefined();
    });

    it("should provide WebSocket connection methods", () => {
      expect(wsClient.connectToCampaign).toBeDefined();
      expect(typeof wsClient.connectToCampaign).toBe("function");

      expect(wsClient.connectToChat).toBeDefined();
      expect(typeof wsClient.connectToChat).toBe("function");

      expect(wsClient.connectToGlobal).toBeDefined();
      expect(typeof wsClient.connectToGlobal).toBe("function");
    });

    it("should share base URL configuration with REST client", () => {
      const wsBaseUrl = wsClient.getWebSocketBaseUrl();
      expect(wsBaseUrl).toBeDefined();
      expect(
        wsBaseUrl.startsWith("ws://") || wsBaseUrl.startsWith("wss://")
      ).toBe(true);
    });
  });

  describe("Type Definitions", () => {
    it("should define CharacterCreateRequest with required fields", () => {
      const request: CharacterCreateRequest = {
        name: "Test Hero",
        race: "human",
        character_class: "fighter",
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
      };

      expect(request.name).toBe("Test Hero");
      expect(request.race).toBe("human");
      expect(request.character_class).toBe("fighter");
      expect(request.abilities).toBeDefined();
      expect(request.abilities.strength).toBe(16);
    });

    it("should define Character with expected fields", () => {
      const character: Character = {
        id: "test-id",
        name: "Test Hero",
        race: "human",
        character_class: "fighter",
        level: 1,
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
        hitPoints: { current: 20, maximum: 20 },
        inventory: [],
      };

      expect(character.id).toBe("test-id");
      expect(character.name).toBe("Test Hero");
      expect(character.level).toBe(1);
      expect(character.hitPoints?.current).toBe(20);
      expect(character.hitPoints?.maximum).toBe(20);
      expect(character.inventory).toBeInstanceOf(Array);
    });

    it("should allow optional fields to be undefined", () => {
      const request: CharacterCreateRequest = {
        name: "Test Hero",
        race: "human",
        character_class: "fighter",
        abilities: {
          strength: 16,
          dexterity: 14,
          constitution: 15,
          intelligence: 12,
          wisdom: 13,
          charisma: 10,
        },
        // backstory is optional and can be omitted
      };

      expect(request).toBeDefined();
      expect(request.backstory).toBeUndefined();
    });
  });

  describe("Backward Compatibility", () => {
    it("should maintain wrapper functions for existing frontend code", () => {
      expect(createCharacter).toBeDefined();
      expect(typeof createCharacter).toBe("function");

      expect(createCampaign).toBeDefined();
      expect(typeof createCampaign).toBe("function");

      expect(getCampaign).toBeDefined();
      expect(typeof getCampaign).toBe("function");

      expect(getCampaigns).toBeDefined();
      expect(typeof getCampaigns).toBe("function");

      expect(sendPlayerInput).toBeDefined();
      expect(typeof sendPlayerInput).toBe("function");
    });
  });
});
