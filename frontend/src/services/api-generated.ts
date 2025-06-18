// API client using generated OpenAPI client
import { Configuration, GameApi } from "../api-client";
import { getApiBaseUrl } from "../utils/urls";

// Create configuration for the generated API client
const configuration = new Configuration({
  basePath: getApiBaseUrl(),
});

// Create the API client instance
export const gameApi = new GameApi(configuration);

// Export all types from the generated client
export * from "../api-client";

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