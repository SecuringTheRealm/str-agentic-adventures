// API client using generated OpenAPI client
import axios from "axios";
import { Configuration, GameApi } from "../api-client";
import { getApiBaseUrl } from "../utils/urls";

// Create configuration for the generated API client
const configuration = new Configuration({
  basePath: getApiBaseUrl(),
});

// Create the API client instance
export const gameApi = new GameApi(configuration);

// Create a compatible apiClient for existing code that uses direct axios calls
export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for better error handling in production
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Add context to errors for better debugging
    if (error.response) {
      console.error('API Error Response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        url: error.config?.url,
        data: error.response.data
      });
    } else if (error.request) {
      console.error('API Network Error:', {
        url: error.config?.url,
        message: error.message,
        baseURL: apiClient.defaults.baseURL
      });
    }
    return Promise.reject(error);
  }
);

// Export all types from the generated client
export * from "../api-client";

// Export compatibility aliases for types that have different names
export type {
  CharacterSheet as Character,
  CreateCharacterRequest as CharacterCreateRequest,
  CreateCampaignRequest as CampaignCreateRequest,
} from "../api-client";

// Define legacy interface types for compatibility
export interface InventoryItem {
  name: string;
  quantity: number;
  type?: string;
  description?: string;
}

// Wrapper functions to maintain compatibility with existing frontend code
export const createCharacter = async (characterData: import("../api-client").CreateCharacterRequest) => {
  const response = await gameApi.createCharacterApiGameCharacterPost(characterData);
  return response.data;
};

export const getCharacter = async (characterId: string) => {
  const response = await gameApi.getCharacterApiGameCharacterCharacterIdGet(characterId);
  return response.data;
};

export const sendPlayerInput = async (input: import("../api-client").PlayerInput) => {
  const response = await gameApi.processPlayerInputApiGameInputPost(input);
  return response.data;
};

export const createCampaign = async (campaignData: import("../api-client").CreateCampaignRequest) => {
  const response = await gameApi.createCampaignApiGameCampaignPost(campaignData);
  return response.data;
};

export const getCampaigns = async () => {
  const response = await gameApi.listCampaignsApiGameCampaignsGet();
  return response.data;
};

export const getCampaign = async (campaignId: string) => {
  const response = await gameApi.getCampaignApiGameCampaignCampaignIdGet(campaignId);
  return response.data;
};

export const updateCampaign = async (campaignId: string, updates: import("../api-client").CampaignUpdateRequest) => {
  const response = await gameApi.updateCampaignApiGameCampaignCampaignIdPut(campaignId, updates);
  return response.data;
};

export const cloneCampaign = async (cloneData: import("../api-client").CloneCampaignRequest) => {
  const response = await gameApi.cloneCampaignApiGameCampaignClonePost(cloneData);
  return response.data;
};

export const deleteCampaign = async (campaignId: string) => {
  const response = await gameApi.deleteCampaignApiGameCampaignCampaignIdDelete(campaignId);
  return response.data;
};

export const getCampaignTemplates = async () => {
  const response = await gameApi.getCampaignTemplatesApiGameCampaignTemplatesGet();
  return response.data;
};

/**
 * Retry wrapper for API calls to handle temporary failures
 */
const retryApiCall = async <T>(
  apiCall: () => Promise<T>,
  retries: number = 3,
  initialDelay: number = 1000
): Promise<T> => {
  const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
  
  let lastError: any;
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await apiCall();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on client errors (4xx), only server errors (5xx) and network errors
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        throw error;
      }
      
      if (attempt === retries) {
        break;
      }
      
      const delayMs = initialDelay * Math.pow(2, attempt - 1);
      console.warn(`API call failed (attempt ${attempt}/${retries}), retrying in ${delayMs}ms...`, error.message);
      await sleep(delayMs);
    }
  }
  
  throw lastError || new Error('All retry attempts failed');
};

/**
 * Get campaign templates with retry logic for production reliability
 */
export const getCampaignTemplatesWithRetry = async () => {
  return retryApiCall(() => getCampaignTemplates(), 3, 1000);
};

export const getAIAssistance = async (request: import("../api-client").AIAssistanceRequest) => {
  const response = await gameApi.getAiAssistanceApiGameCampaignAiAssistPost(request);
  return response.data;
};

export const generateAIContent = async (request: import("../api-client").AIContentGenerationRequest) => {
  const response = await gameApi.generateAiContentApiGameCampaignAiGeneratePost(request);
  return response.data;
};

export const generateImage = async (imageRequest: Record<string, unknown>) => {
  const response = await gameApi.generateImageApiGameGenerateImagePost(imageRequest);
  return response.data;
};

export const generateBattleMap = async (mapRequest: Record<string, unknown>) => {
  const response = await gameApi.generateBattleMapApiGameBattleMapPost(mapRequest);
  return response.data;
};