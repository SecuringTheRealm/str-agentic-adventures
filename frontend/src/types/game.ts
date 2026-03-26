export interface ChatMessage {
  text: string;
  sender: "player" | "dm";
  isStreaming?: boolean;
}

export interface DiceResult {
  notation?: string;
  rolls: number[];
  total: number;
  modifier?: number;
  dropped?: number[];
  rerolls?: Array<{
    original: number;
    new: number;
    index: number;
  }>;
  character_bonus?: number;
  timestamp?: string;
}

export interface GameSession {
  session_id: string;
  campaign_id: string;
  type: string;
  status: string;
  current_scene: string;
  available_actions: string[];
  scene_count: number;
  started_at: string;
}

export interface CombatState {
  combat_id: string;
  status: string;
  round: number;
  current_turn: number;
  initiative_order: Array<{
    type: string;
    id: string;
    name: string;
    initiative: number;
  }>;
  environment: string;
}
