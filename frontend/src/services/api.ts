// API client for interacting with the backend
import axios from "axios";
import { getApiBaseUrl } from "../utils/urls";

// Define the base API URL - would come from environment in production
const API_BASE_URL = getApiBaseUrl();

// Create axios instance with default config
export const apiClient = axios.create({
	baseURL: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

// Define API interface types
export interface InventoryItem {
	name: string;
	quantity: number;
	type?: string;
	description?: string;
}

export interface CharacterCreateRequest {
	name: string;
	race: string;
	character_class: string;
	abilities: {
		strength: number;
		dexterity: number;
		constitution: number;
		intelligence: number;
		wisdom: number;
		charisma: number;
	};
	backstory?: string;
}

export interface Character {
	id: string;
	name: string;
	race: string;
	character_class: string;
	level: number;
	abilities: {
		strength: number;
		dexterity: number;
		constitution: number;
		intelligence: number;
		wisdom: number;
		charisma: number;
	};
	hit_points: {
		current: number;
		maximum: number;
	};
	inventory: InventoryItem[];
}

export interface Campaign {
	id: string;
	name: string;
	setting: string;
	tone: string;
	homebrew_rules: string[];
	characters: string[];
	description?: string;
	world_description?: string;
	world_art?: {
		image_url: string;
	};
	is_template?: boolean;
	is_custom?: boolean;
	template_id?: string;
	plot_hooks?: string[];
	key_npcs?: string[];
}

export interface CampaignCreateRequest {
	name: string;
	setting: string;
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
	new_name?: string;
}

export interface CampaignListResponse {
	campaigns: Campaign[];
	templates: Campaign[];
}

export interface AIAssistanceRequest {
	text: string;
	context_type: string;
	campaign_tone?: string;
}

export interface AIAssistanceResponse {
	suggestions: string[];
	enhanced_text?: string;
}

export interface PlayerInputRequest {
	message: string;
	character_id: string;
	campaign_id: string;
}

export interface CombatUpdate {
	status?: string;
	map_url?: string;
	current_turn?: string;
	initiative?: Array<{
		character_id: string;
		name: string;
		initiative: number;
	}>;
}

export interface GameResponse {
	message: string;
	images: string[];
	state_updates: Record<string, unknown>;
	combat_updates?: CombatUpdate;
}

export interface ImageGenerateRequest {
	image_type:
		| "character_portrait"
		| "scene_illustration"
		| "item_visualization";
	details: Record<string, unknown>;
}

export interface BattleMapRequest {
	environment: Record<string, unknown>;
	combat_context?: Record<string, unknown>;
}

// API functions
export const createCharacter = async (
	characterData: CharacterCreateRequest,
): Promise<Character> => {
	try {
		const response = await apiClient.post("/game/character", characterData);
		return response.data;
	} catch (error) {
		console.error("Error creating character:", error);
		throw error;
	}
};

export const getCharacter = async (characterId: string): Promise<Character> => {
	try {
		const response = await apiClient.get(`/game/character/${characterId}`);
		return response.data;
	} catch (error) {
		console.error(`Error fetching character ${characterId}:`, error);
		throw error;
	}
};

export const sendPlayerInput = async (
	input: PlayerInputRequest,
): Promise<GameResponse> => {
	try {
		const response = await apiClient.post("/game/input", input);
		return response.data;
	} catch (error) {
		console.error("Error sending player input:", error);
		throw error;
	}
};

export const createCampaign = async (
	campaignData: CampaignCreateRequest,
): Promise<Campaign> => {
	try {
		const response = await apiClient.post("/game/campaign", campaignData);
		return response.data;
	} catch (error) {
		console.error("Error creating campaign:", error);
		throw error;
	}
};

export const getCampaigns = async (): Promise<CampaignListResponse> => {
	try {
		const response = await apiClient.get("/game/campaigns");
		return response.data;
	} catch (error) {
		console.error("Error fetching campaigns:", error);
		throw error;
	}
};

export const getCampaign = async (campaignId: string): Promise<Campaign> => {
	try {
		const response = await apiClient.get(`/game/campaign/${campaignId}`);
		return response.data;
	} catch (error) {
		console.error(`Error fetching campaign ${campaignId}:`, error);
		throw error;
	}
};

export const updateCampaign = async (
	campaignId: string,
	updates: CampaignUpdateRequest,
): Promise<Campaign> => {
	try {
		const response = await apiClient.put(`/game/campaign/${campaignId}`, updates);
		return response.data;
	} catch (error) {
		console.error(`Error updating campaign ${campaignId}:`, error);
		throw error;
	}
};

export const cloneCampaign = async (
	cloneData: CloneCampaignRequest,
): Promise<Campaign> => {
	try {
		const response = await apiClient.post("/game/campaign/clone", cloneData);
		return response.data;
	} catch (error) {
		console.error("Error cloning campaign:", error);
		throw error;
	}
};

export const deleteCampaign = async (campaignId: string): Promise<void> => {
	try {
		await apiClient.delete(`/game/campaign/${campaignId}`);
	} catch (error) {
		console.error(`Error deleting campaign ${campaignId}:`, error);
		throw error;
	}
};

export const getCampaignTemplates = async (): Promise<Campaign[]> => {
	try {
		const response = await apiClient.get("/game/campaign/templates");
		return response.data.templates;
	} catch (error) {
		console.error("Error fetching campaign templates:", error);
		throw error;
	}
};

export const getAIAssistance = async (
	request: AIAssistanceRequest,
): Promise<AIAssistanceResponse> => {
	try {
		const response = await apiClient.post("/game/campaign/ai-assist", request);
		return response.data;
	} catch (error) {
		console.error("Error getting AI assistance:", error);
		throw error;
	}
};

export const generateImage = async (
	imageRequest: ImageGenerateRequest,
): Promise<unknown> => {
	try {
		const response = await apiClient.post("/game/generate-image", imageRequest);
		return response.data;
	} catch (error) {
		console.error("Error generating image:", error);
		throw error;
	}
};

export const generateBattleMap = async (
	mapRequest: BattleMapRequest,
): Promise<unknown> => {
	try {
		const response = await apiClient.post("/game/battle-map", mapRequest);
		return response.data;
	} catch (error) {
		console.error("Error generating battle map:", error);
		throw error;
	}
};
