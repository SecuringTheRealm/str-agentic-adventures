// API client for interacting with the backend
import axios from 'axios';

// Define the base API URL - would come from environment in production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define API interface types
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
  class: string;
  level: number;
  abilities: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
  hitPoints: {
    current: number;
    maximum: number;
  };
  inventory: any[];
}

export interface PlayerInputRequest {
  message: string;
  character_id: string;
  campaign_id: string;
}

export interface GameResponse {
  message: string;
  images: string[];
  state_updates: Record<string, any>;
  combat_updates?: Record<string, any>;
}

// API functions
export const createCharacter = async (characterData: CharacterCreateRequest): Promise<Character> => {
  try {
    const response = await apiClient.post('/game/character', characterData);
    return response.data;
  } catch (error) {
    console.error('Error creating character:', error);
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

export const sendPlayerInput = async (input: PlayerInputRequest): Promise<GameResponse> => {
  try {
    const response = await apiClient.post('/game/input', input);
    return response.data;
  } catch (error) {
    console.error('Error sending player input:', error);
    throw error;
  }
};
