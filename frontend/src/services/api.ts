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
	weight?: number;
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
	world_description?: string;
	world_art?: {
		image_url: string;
	};
}

export interface CampaignCreateRequest {
	name: string;
	setting: string;
	tone?: string;
	homebrew_rules?: string[];
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
