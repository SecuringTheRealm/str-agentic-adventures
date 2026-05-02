/**
 * API service layer using openapi-fetch + openapi-typescript.
 *
 * All HTTP calls go through the typed `api` client exported from
 * `../api-client/client.ts`. That client is configured from the generated
 * schema types (`schema.d.ts`) produced by `bun run generate:api`.
 *
 * Migration note: this file previously used @openapitools/openapi-generator-cli
 * runtime classes (GameApi, DefaultApi, Configuration) plus an axios instance.
 * Those have been replaced by openapi-fetch which provides the same type safety
 * without requiring Java or generated runtime code.
 */
import { api } from "../api-client/client";
// Import WebSocket client for unified SDK
import {
  WebSocketClient,
  type WebSocketConnectionOptions,
  type WebSocketMessage,
  websocketClient,
} from "../api-client/websocketClient";
import type { BattleMapData } from "../types/battleMap";
import { getApiBaseUrl } from "../utils/urls";

// Export WebSocket client for unified SDK access
export const wsClient = websocketClient;
export type { WebSocketConnectionOptions, WebSocketMessage };
export { WebSocketClient };

// ============================================================================
// Type definitions
//
// These mirror the backend Pydantic models. Once schema.d.ts is generated
// (`bun run generate:api`), openapi-fetch infers the exact request/response
// types automatically. The interfaces below exist so that consuming components
// can import named types without depending on the generated file at build time.
// ============================================================================

export interface AbilityScores {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

export interface HitPoints {
  current: number;
  maximum: number;
}

export interface Character {
  id?: string;
  name: string;
  race: string;
  character_class: string;
  level?: number;
  abilities: AbilityScores;
  hitPoints?: HitPoints;
  hit_points?: HitPoints;
  inventory?: InventoryItem[];
  backstory?: string;
  equipment?: Record<string, unknown>;
  spellcasting?: Record<string, unknown>;
  exhaustion_level?: number;
  hit_dice_remaining?: number;
  is_custom?: boolean;
}

export interface Campaign {
  id?: string;
  name: string;
  description?: string | null;
  setting?: string;
  tone?: string;
  homebrew_rules?: string[];
  world_description?: string;
  world_art?: { image_url?: string };
  is_template?: boolean;
  is_custom?: boolean;
  template_id?: string | null;
  plot_hooks?: string[];
  predefined_characters?: Record<string, unknown>[];
}

export interface CharacterCreateRequest {
  name: string;
  race: string;
  character_class: string;
  abilities: AbilityScores;
  backstory?: string;
}

export interface CampaignCreateRequest {
  name: string;
  setting?: string;
  tone?: string;
  homebrew_rules?: string[];
  description?: string;
}

export interface CampaignUpdateRequest {
  name?: string;
  description?: string;
  setting?: string;
  tone?: string;
  homebrew_rules?: string[];
  world_description?: string;
}

export interface CloneCampaignRequest {
  template_id: string;
  name?: string;
}

export interface PlayerInput {
  character_id: string;
  campaign_id: string;
  message: string;
}

export interface AIAssistanceRequest {
  prompt: string;
  context: string;
  campaign_tone: string | null;
}

export interface AIContentGenerationRequest {
  suggestion: string;
  current_text: string;
  content_type?: string;
  context_type: string;
  campaign_tone: string | null;
}

export interface InventoryItem {
  name?: string;
  item_id?: string;
  quantity: number;
  type?: string;
  description?: string;
}

export interface PlayerInputResponse {
  message: string;
  images?: string[];
  combat_updates?: {
    status?: string;
    map_url?: string;
    combat_id?: string;
    combat_context?: Record<string, unknown>;
  };
  state_updates?: {
    auto_saved?: boolean;
    last_auto_save?: string;
  };
}

export interface OpeningNarrativeResponse {
  scene_description: string;
  quest_hook: string;
  suggested_actions: string[];
  help_text: string;
}

export interface VisualGenerationStatus {
  available: boolean;
  status: "healthy" | "degraded" | "unavailable";
  message: string | null;
}

interface DependencyHealthStatus {
  azure_openai?: "healthy" | "degraded" | "unavailable";
}

// ============================================================================
// API wrapper functions
//
// Each function calls the backend via the openapi-fetch `api` client.
// The path strings match the FastAPI route definitions.
// ============================================================================

export const createCharacter = async (
  characterData: CharacterCreateRequest
): Promise<Character> => {
  // Normalise race and character_class to lowercase as backend expects
  const body = {
    ...characterData,
    race: characterData.race?.toLowerCase(),
    character_class: characterData.character_class?.toLowerCase(),
  };

  const { data, error } = await api.POST("/game/character", {
    body: body as any,
  });
  if (error) throw error;
  return data as Character;
};

export const getCharacter = async (characterId: string): Promise<Character> => {
  const { data, error } = await api.GET("/game/character/{character_id}", {
    params: { path: { character_id: characterId } },
  });
  if (error) throw error;
  return data as unknown as Character;
};

export const sendPlayerInput = async (
  input: PlayerInput
): Promise<PlayerInputResponse> => {
  const { data, error } = await api.POST("/game/input", {
    body: input,
  });
  if (error) throw error;
  return data as PlayerInputResponse;
};

export const createCampaign = async (
  campaignData: CampaignCreateRequest
): Promise<Campaign> => {
  const { data, error } = await api.POST("/game/campaign", {
    body: campaignData as any,
  });
  if (error) throw error;
  return data as Campaign;
};

export const getCampaigns = async (): Promise<Campaign[]> => {
  const { data, error } = await api.GET("/game/campaigns");
  if (error) throw error;
  const payload = data as unknown as
    | { campaigns?: Campaign[]; templates?: Campaign[] }
    | Campaign[];
  if (Array.isArray(payload)) return payload;
  return payload?.campaigns ?? [];
};

export const getCampaign = async (campaignId: string): Promise<Campaign> => {
  const { data, error } = await api.GET("/game/campaign/{campaign_id}", {
    params: { path: { campaign_id: campaignId } },
  });
  if (error) throw error;
  return data as Campaign;
};

export const updateCampaign = async (
  campaignId: string,
  updates: CampaignUpdateRequest
): Promise<Campaign> => {
  const { data, error } = await api.PUT("/game/campaign/{campaign_id}", {
    params: { path: { campaign_id: campaignId } },
    body: updates as any,
  });
  if (error) throw error;
  return data as Campaign;
};

export const cloneCampaign = async (
  cloneData: CloneCampaignRequest
): Promise<Campaign> => {
  const { data, error } = await api.POST("/game/campaign/clone", {
    body: cloneData as any,
  });
  if (error) throw error;
  return data as Campaign;
};

export const deleteCampaign = async (campaignId: string): Promise<void> => {
  const { error } = await api.DELETE("/game/campaign/{campaign_id}", {
    params: { path: { campaign_id: campaignId } },
  });
  if (error) throw error;
};

export const getCampaignTemplates = async (): Promise<Campaign[]> => {
  const { data, error } = await api.GET("/game/campaign/templates");
  if (error) throw error;
  const payload = data as unknown as { templates?: Campaign[] } | Campaign[];
  if (Array.isArray(payload)) return payload;
  return payload?.templates ?? [];
};

/**
 * Retry wrapper for API calls to handle temporary failures.
 */
const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  retries = 3,
  initialDelay = 1000
): Promise<T> => {
  const sleep = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  let lastError: unknown;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await apiCall();
    } catch (error: unknown) {
      lastError = error;

      // Don't retry on client errors (4xx), only server errors (5xx) and network errors
      const errorObj = error as { status?: number; message?: string };
      if (errorObj.status && errorObj.status >= 400 && errorObj.status < 500) {
        throw error;
      }

      if (attempt === retries) break;

      const delayMs = initialDelay * 2 ** (attempt - 1);
      console.warn(
        `API call failed (attempt ${attempt}/${retries}), retrying in ${delayMs}ms...`,
        errorObj.message
      );
      await sleep(delayMs);
    }
  }

  throw lastError || new Error("All retry attempts failed");
};

/** Get campaign templates with retry logic for production reliability. */
export const getCampaignTemplatesWithRetry = async (): Promise<Campaign[]> => {
  return retryApiCall(() => getCampaignTemplates(), 3, 1000);
};

export const getAIAssistance = async (request: AIAssistanceRequest) => {
  const { data, error } = await api.POST("/game/campaign/ai-assist", {
    body: request as any,
  });
  if (error) throw error;
  return data as { suggestions: string[]; enhanced_text?: string | null };
};

export const generateAIContent = async (
  request: AIContentGenerationRequest
) => {
  const { data, error } = await api.POST("/game/campaign/ai-generate", {
    body: request as any,
  });
  if (error) throw error;
  return data as {
    generated_content: string;
    success: boolean;
    error?: string | null;
  };
};

export const generateImage = async (imageRequest: Record<string, unknown>) => {
  const { data, error } = await api.POST("/game/generate-image", {
    body: imageRequest as never,
  });
  if (error) throw error;
  return data;
};

export const generateBattleMap = async (
  mapRequest: Record<string, unknown>
) => {
  const { data, error } = await api.POST("/game/battle-map", {
    body: mapRequest as never,
  });
  if (error) throw error;
  return data;
};

export const generateStructuredBattleMap = async (
  environment: object,
  combatContext?: object
): Promise<BattleMapData> => {
  const { data, error } = await (api as any).POST(
    "/game/battle-map/structured",
    {
      body: { environment, combat_context: combatContext },
    }
  );
  if (error) throw error;
  return data as BattleMapData;
};

export const getOpeningNarrative = async (
  campaignId: string,
  character: {
    name?: string;
    character_class?: string;
    race?: string;
    backstory?: string;
  }
): Promise<OpeningNarrativeResponse> => {
  const { data, error } = await api.POST(
    "/game/campaign/{campaign_id}/opening-narrative",
    {
      params: { path: { campaign_id: campaignId } },
      body: { character } as never,
    }
  );
  if (error) throw error;
  return data as unknown as OpeningNarrativeResponse;
};

export const getVisualGenerationStatus =
  async (): Promise<VisualGenerationStatus> => {
    const response = await fetch(`${getApiBaseUrl()}/health/dependencies`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(
        `Failed to load visual generation status (${response.status.toString()})`
      );
    }

    const dependencyHealth = (await response.json()) as DependencyHealthStatus;
    const azureStatus = dependencyHealth.azure_openai ?? "unavailable";

    if (azureStatus === "healthy") {
      return {
        available: true,
        status: "healthy",
        message: null,
      };
    }

    if (azureStatus === "degraded") {
      return {
        available: false,
        status: "degraded",
        message:
          "Visual generation is temporarily unavailable while the AI service recovers.",
      };
    }

    return {
      available: false,
      status: "unavailable",
      message:
        "Visual generation is unavailable because image generation is not configured.",
    };
  };

// ============================================================================
// Dice roll helper
//
// Replaces the old `apiClient` (axios instance) that was used by DiceRoller.
// ============================================================================

export const rollDice = async (
  notation: string,
  characterId?: string,
  skill?: string
) => {
  if (characterId && skill) {
    const { data, error } = await api.POST("/game/dice/roll-with-character", {
      body: { notation, character_id: characterId, skill } as never,
    });
    if (error) throw error;
    return data;
  }

  const { data, error } = await api.POST("/game/dice/roll", {
    body: { notation } as never,
  });
  if (error) throw error;
  return data;
};
