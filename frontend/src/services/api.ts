// API client using generated OpenAPI client
import axios from "axios";
import { Configuration, GameApi } from "../api-client";
import { getApiBaseUrl } from "../utils/urls";

// Enhanced error class for API errors
export class APIError extends Error {
  public status?: number;
  public details?: string;

  constructor(message: string, status?: number, details?: string) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.details = details;
  }
}

// Utility function to parse API errors and provide better error messages
const parseAPIError = (error: any): APIError => {
  if (error.response) {
    const status = error.response.status;
    const details = error.response.data?.detail || error.response.statusText;
    
    if (status === 503) {
      if (details?.includes('Azure OpenAI configuration')) {
        return new APIError(
          'Azure OpenAI configuration is required. Please contact your administrator to set up the required Azure OpenAI credentials.',
          status,
          details
        );
      }
      return new APIError(
        'Service temporarily unavailable. Please try again later.',
        status,
        details
      );
    }
    
    if (status === 404) {
      return new APIError('Resource not found.', status, details);
    }
    
    if (status === 400) {
      return new APIError(
        details || 'Invalid request. Please check your input and try again.',
        status,
        details
      );
    }
    
    if (status >= 500) {
      return new APIError(
        'Server error occurred. Please try again later.',
        status,
        details
      );
    }
    
    return new APIError(
      details || 'An error occurred while processing your request.',
      status,
      details
    );
  }
  
  if (error.request) {
    return new APIError(
      'Unable to connect to the server. Please check your internet connection and try again.',
      0,
      'Network error'
    );
  }
  
  return new APIError(
    error.message || 'An unexpected error occurred.',
    undefined,
    error.toString()
  );
};

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
  try {
    const response = await gameApi.createCharacterApiGameCharacterPost(characterData);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const getCharacter = async (characterId: string) => {
  try {
    const response = await gameApi.getCharacterApiGameCharacterCharacterIdGet(characterId);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const sendPlayerInput = async (input: import("../api-client").PlayerInput) => {
  try {
    const response = await gameApi.processPlayerInputApiGameInputPost(input);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const createCampaign = async (campaignData: import("../api-client").CreateCampaignRequest) => {
  try {
    const response = await gameApi.createCampaignApiGameCampaignPost(campaignData);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const getCampaigns = async () => {
  try {
    const response = await gameApi.listCampaignsApiGameCampaignsGet();
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const getCampaign = async (campaignId: string) => {
  try {
    const response = await gameApi.getCampaignApiGameCampaignCampaignIdGet(campaignId);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const updateCampaign = async (campaignId: string, updates: import("../api-client").CampaignUpdateRequest) => {
  try {
    const response = await gameApi.updateCampaignApiGameCampaignCampaignIdPut(campaignId, updates);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const cloneCampaign = async (cloneData: import("../api-client").CloneCampaignRequest) => {
  try {
    const response = await gameApi.cloneCampaignApiGameCampaignClonePost(cloneData);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const deleteCampaign = async (campaignId: string) => {
  try {
    const response = await gameApi.deleteCampaignApiGameCampaignCampaignIdDelete(campaignId);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const getCampaignTemplates = async () => {
  try {
    const response = await gameApi.getCampaignTemplatesApiGameCampaignTemplatesGet();
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const getAIAssistance = async (request: import("../api-client").AIAssistanceRequest) => {
  try {
    const response = await gameApi.getAiAssistanceApiGameCampaignAiAssistPost(request);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const generateAIContent = async (request: import("../api-client").AIContentGenerationRequest) => {
  try {
    const response = await gameApi.generateAiContentApiGameCampaignAiGeneratePost(request);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const generateImage = async (imageRequest: Record<string, unknown>) => {
  try {
    const response = await gameApi.generateImageApiGameGenerateImagePost(imageRequest);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};

export const generateBattleMap = async (mapRequest: Record<string, unknown>) => {
  try {
    const response = await gameApi.generateBattleMapApiGameBattleMapPost(mapRequest);
    return response.data;
  } catch (error) {
    throw parseAPIError(error);
  }
};