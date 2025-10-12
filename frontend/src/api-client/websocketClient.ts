/**
 * WebSocket Client SDK
 *
 * Provides a unified client interface for WebSocket connections to the backend.
 * This extends the OpenAPI-generated REST client with WebSocket support.
 *
 * Since OpenAPI doesn't support WebSocket definitions, this client is manually
 * implemented to provide the same developer experience as the REST client.
 */

import { getApiBaseUrl } from "../utils/urls";

// ============================================================================
// WebSocket Message Type Definitions
// ============================================================================

/**
 * Base WebSocket message structure
 */
export interface BaseWebSocketMessage {
  type: string;
  timestamp?: string;
}

/**
 * Chat-related message types
 */
export interface ChatStartMessage extends BaseWebSocketMessage {
  type: "chat_start";
  message: string;
}

export interface ChatTypingMessage extends BaseWebSocketMessage {
  type: "chat_typing";
}

export interface ChatStartStreamMessage extends BaseWebSocketMessage {
  type: "chat_start_stream";
}

export interface ChatStreamMessage extends BaseWebSocketMessage {
  type: "chat_stream";
  chunk: string;
  full_text?: string;
}

export interface ChatCompleteMessage extends BaseWebSocketMessage {
  type: "chat_complete";
  message: string;
}

export interface ChatErrorMessage extends BaseWebSocketMessage {
  type: "chat_error";
  message: string;
}

export interface ChatInputMessage extends BaseWebSocketMessage {
  type: "chat_input";
  message: string;
  character_id: string;
  campaign_id?: string;
}

/**
 * Game update message types
 */
export interface DiceRollMessage extends BaseWebSocketMessage {
  type: "dice_roll";
  notation: string;
  character_id?: string;
  skill?: string;
  player_name?: string;
}

export interface DiceResultMessage extends BaseWebSocketMessage {
  type: "dice_result";
  player_name: string;
  notation: string;
  result: {
    total: number;
    rolls: number[];
    modifier?: number;
    timestamp?: string;
  };
  skill?: string;
}

export interface GameUpdateMessage extends BaseWebSocketMessage {
  type: "game_update";
  update_type: string;
  data?: Record<string, unknown>;
}

export interface CharacterUpdateMessage extends BaseWebSocketMessage {
  type: "character_update";
  character_id: string;
  data: Record<string, unknown>;
}

/**
 * Connection control messages
 */
export interface PingMessage extends BaseWebSocketMessage {
  type: "ping";
}

export interface PongMessage extends BaseWebSocketMessage {
  type: "pong";
}

export interface ErrorMessage extends BaseWebSocketMessage {
  type: "error";
  message: string;
}

/**
 * Union type of all possible WebSocket messages
 */
export type WebSocketMessage =
  | ChatStartMessage
  | ChatTypingMessage
  | ChatStartStreamMessage
  | ChatStreamMessage
  | ChatCompleteMessage
  | ChatErrorMessage
  | ChatInputMessage
  | DiceRollMessage
  | DiceResultMessage
  | GameUpdateMessage
  | CharacterUpdateMessage
  | PingMessage
  | PongMessage
  | ErrorMessage;

// ============================================================================
// WebSocket Client Configuration
// ============================================================================

export interface WebSocketClientConfig {
  /**
   * Base URL for the API (will be converted to ws:// or wss://)
   */
  baseUrl?: string;

  /**
   * Reconnection settings
   */
  reconnectInterval?: number;
  maxReconnectAttempts?: number;

  /**
   * Enable debug logging
   */
  debug?: boolean;
}

export interface WebSocketConnectionOptions {
  /**
   * Callback when connection is established
   */
  onConnect?: () => void;

  /**
   * Callback when connection is closed
   */
  onDisconnect?: () => void;

  /**
   * Callback when a message is received
   */
  onMessage?: (message: WebSocketMessage) => void;

  /**
   * Callback when an error occurs
   */
  onError?: (error: Event) => void;

  /**
   * Reconnection settings (overrides client config)
   */
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

// ============================================================================
// WebSocket Connection Manager
// ============================================================================

class WebSocketConnection {
  private ws: WebSocket | null = null;
  private url: string;
  private options: WebSocketConnectionOptions;
  private reconnectAttempts = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private shouldReconnect = true;
  private reconnectInterval: number;
  private maxReconnectAttempts: number;
  private debug: boolean;

  constructor(
    url: string,
    options: WebSocketConnectionOptions = {},
    config: WebSocketClientConfig = {}
  ) {
    this.url = url;
    this.options = options;
    this.reconnectInterval =
      options.reconnectInterval ?? config.reconnectInterval ?? 3000;
    this.maxReconnectAttempts =
      options.maxReconnectAttempts ?? config.maxReconnectAttempts ?? 5;
    this.debug = config.debug ?? false;
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.log("Already connected");
      return;
    }

    if (!this.url || !this.url.startsWith("ws")) {
      throw new Error(`Invalid WebSocket URL: ${this.url}`);
    }

    this.log(`Connecting to ${this.url}`);

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.log("Connected");
        this.reconnectAttempts = 0;
        this.options.onConnect?.();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          this.log("Received message:", message);
          this.options.onMessage?.(message);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = () => {
        this.log("Disconnected");
        this.options.onDisconnect?.();

        // Attempt reconnection if enabled
        if (
          this.shouldReconnect &&
          this.reconnectAttempts < this.maxReconnectAttempts
        ) {
          this.reconnectAttempts++;
          this.log(
            `Reconnecting (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
          );
          this.reconnectTimeout = setTimeout(() => {
            this.connect();
          }, this.reconnectInterval);
        }
      };

      this.ws.onerror = (error) => {
        this.log("Error:", error);
        this.options.onError?.(error);
      };
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      throw error;
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.log("Disconnected (manual)");
  }

  /**
   * Send a message to the WebSocket server
   */
  send(message: Partial<WebSocketMessage>): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error("WebSocket is not connected");
      return false;
    }

    try {
      this.ws.send(JSON.stringify(message));
      this.log("Sent message:", message);
      return true;
    } catch (error) {
      console.error("Failed to send WebSocket message:", error);
      return false;
    }
  }

  /**
   * Check if the WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get the underlying WebSocket instance
   */
  getSocket(): WebSocket | null {
    return this.ws;
  }

  /**
   * Get the number of reconnection attempts
   */
  getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  private log(...args: unknown[]): void {
    if (this.debug) {
      console.log("[WebSocketClient]", ...args);
    }
  }
}

// ============================================================================
// WebSocket Client API
// ============================================================================

/**
 * Main WebSocket client class
 */
export class WebSocketClient {
  private config: WebSocketClientConfig;
  private baseUrl: string;
  private wsBaseUrl: string;

  constructor(config: WebSocketClientConfig = {}) {
    this.config = config;
    this.baseUrl = config.baseUrl ?? getApiBaseUrl();
    this.wsBaseUrl = this.httpToWs(this.baseUrl);
  }

  /**
   * Convert HTTP(S) URL to WS(S) URL
   */
  private httpToWs(url: string): string {
    return url.replace(/^https?:\/\//, (match) =>
      match === "https://" ? "wss://" : "ws://"
    );
  }

  /**
   * Connect to a campaign-specific WebSocket for real-time updates
   */
  connectToCampaign(
    campaignId: string,
    options: WebSocketConnectionOptions = {}
  ): WebSocketConnection {
    const url = `${this.wsBaseUrl}/api/ws/${campaignId}`;
    const connection = new WebSocketConnection(url, options, this.config);
    connection.connect();
    return connection;
  }

  /**
   * Connect to the chat WebSocket for streaming chat responses
   */
  connectToChat(
    campaignId: string,
    options: WebSocketConnectionOptions = {}
  ): WebSocketConnection {
    const url = `${this.wsBaseUrl}/api/ws/chat/${campaignId}`;
    const connection = new WebSocketConnection(url, options, this.config);
    connection.connect();
    return connection;
  }

  /**
   * Connect to the global WebSocket for system-wide updates
   */
  connectToGlobal(
    options: WebSocketConnectionOptions = {}
  ): WebSocketConnection {
    const url = `${this.wsBaseUrl}/api/ws/global`;
    const connection = new WebSocketConnection(url, options, this.config);
    connection.connect();
    return connection;
  }

  /**
   * Get the WebSocket base URL (for advanced use cases)
   */
  getWebSocketBaseUrl(): string {
    return this.wsBaseUrl;
  }
}

// ============================================================================
// Default Export
// ============================================================================

/**
 * Create a default WebSocket client instance
 */
export const websocketClient = new WebSocketClient();

/**
 * Helper functions for backward compatibility
 */
export const connectToCampaign = (
  campaignId: string,
  options?: WebSocketConnectionOptions
) => websocketClient.connectToCampaign(campaignId, options);

export const connectToChat = (
  campaignId: string,
  options?: WebSocketConnectionOptions
) => websocketClient.connectToChat(campaignId, options);

export const connectToGlobal = (options?: WebSocketConnectionOptions) =>
  websocketClient.connectToGlobal(options);
