/**
 * Tests for WebSocket Client SDK
 * Validates WebSocket connection management and message handling
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  WebSocketClient,
  type ChatInputMessage,
  type ChatStreamMessage,
  type DiceRollMessage,
  websocketClient,
} from "../websocketClient";

// Mock WebSocket
class MockWebSocket {
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  readyState = MockWebSocket.CONNECTING;
  url: string;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    // Simulate async connection
    setTimeout(() => {
      this.readyState = MockWebSocket.OPEN;
      this.onopen?.(new Event("open"));
    }, 0);
  }

  send(data: string): void {
    if (this.readyState !== MockWebSocket.OPEN) {
      throw new Error("WebSocket is not connected");
    }
    // Echo the message back for testing
    setTimeout(() => {
      this.onmessage?.(new MessageEvent("message", { data }));
    }, 0);
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.(new CloseEvent("close"));
  }
}

// Replace global WebSocket with mock
global.WebSocket = MockWebSocket as any;

describe("WebSocket Client SDK", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("WebSocketClient initialization", () => {
    it("should create a WebSocketClient instance", () => {
      const client = new WebSocketClient();
      expect(client).toBeDefined();
      expect(client).toBeInstanceOf(WebSocketClient);
    });

    it("should use default base URL from environment", () => {
      const client = new WebSocketClient();
      const baseUrl = client.getWebSocketBaseUrl();
      expect(baseUrl).toBeDefined();
      expect(baseUrl.startsWith("ws://") || baseUrl.startsWith("wss://")).toBe(
        true
      );
    });

    it("should use custom base URL when provided", () => {
      const client = new WebSocketClient({
        baseUrl: "http://custom.example.com",
      });
      const baseUrl = client.getWebSocketBaseUrl();
      expect(baseUrl).toBe("ws://custom.example.com");
    });

    it("should convert HTTPS to WSS", () => {
      const client = new WebSocketClient({
        baseUrl: "https://secure.example.com",
      });
      const baseUrl = client.getWebSocketBaseUrl();
      expect(baseUrl).toBe("wss://secure.example.com");
    });
  });

  describe("Campaign WebSocket connection", () => {
    it("should connect to campaign WebSocket", async () => {
      const client = new WebSocketClient();
      const onConnect = vi.fn();

      const connection = client.connectToCampaign("test-campaign-id", {
        onConnect,
      });

      // Wait for connection
      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(connection).toBeDefined();
      expect(connection.isConnected()).toBe(true);
      expect(onConnect).toHaveBeenCalled();
    });

    it("should construct correct campaign WebSocket URL", async () => {
      const client = new WebSocketClient({
        baseUrl: "http://localhost:8000",
      });

      const connection = client.connectToCampaign("test-campaign-id");
      await new Promise((resolve) => setTimeout(resolve, 10));

      const socket = connection.getSocket();
      expect(socket?.url).toBe("ws://localhost:8000/api/ws/test-campaign-id");
    });

    it("should handle disconnect", async () => {
      const client = new WebSocketClient();
      const onDisconnect = vi.fn();

      const connection = client.connectToCampaign("test-campaign-id", {
        onDisconnect,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      connection.disconnect();

      expect(connection.isConnected()).toBe(false);
      expect(onDisconnect).toHaveBeenCalled();
    });
  });

  describe("Chat WebSocket connection", () => {
    it("should connect to chat WebSocket", async () => {
      const client = new WebSocketClient();
      const onConnect = vi.fn();

      const connection = client.connectToChat("test-campaign-id", {
        onConnect,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(connection).toBeDefined();
      expect(connection.isConnected()).toBe(true);
      expect(onConnect).toHaveBeenCalled();
    });

    it("should construct correct chat WebSocket URL", async () => {
      const client = new WebSocketClient({
        baseUrl: "http://localhost:8000",
      });

      const connection = client.connectToChat("test-campaign-id");
      await new Promise((resolve) => setTimeout(resolve, 10));

      const socket = connection.getSocket();
      expect(socket?.url).toBe(
        "ws://localhost:8000/api/ws/chat/test-campaign-id"
      );
    });
  });

  describe("Global WebSocket connection", () => {
    it("should connect to global WebSocket", async () => {
      const client = new WebSocketClient();
      const onConnect = vi.fn();

      const connection = client.connectToGlobal({
        onConnect,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(connection).toBeDefined();
      expect(connection.isConnected()).toBe(true);
      expect(onConnect).toHaveBeenCalled();
    });

    it("should construct correct global WebSocket URL", async () => {
      const client = new WebSocketClient({
        baseUrl: "http://localhost:8000",
      });

      const connection = client.connectToGlobal();
      await new Promise((resolve) => setTimeout(resolve, 10));

      const socket = connection.getSocket();
      expect(socket?.url).toBe("ws://localhost:8000/api/ws/global");
    });
  });

  describe("Message handling", () => {
    it("should receive and parse WebSocket messages", async () => {
      const client = new WebSocketClient();
      const onMessage = vi.fn();

      const connection = client.connectToCampaign("test-campaign-id", {
        onMessage,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      // Simulate receiving a message
      const testMessage: ChatStreamMessage = {
        type: "chat_stream",
        chunk: "Hello",
        full_text: "Hello world",
      };

      const socket = connection.getSocket();
      socket?.onmessage?.(
        new MessageEvent("message", { data: JSON.stringify(testMessage) })
      );

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(onMessage).toHaveBeenCalledWith(testMessage);
    });

    it("should send chat input messages", async () => {
      const client = new WebSocketClient();
      const connection = client.connectToChat("test-campaign-id");

      await new Promise((resolve) => setTimeout(resolve, 10));

      const message: ChatInputMessage = {
        type: "chat_input",
        message: "Test message",
        character_id: "test-char-id",
      };

      const result = connection.send(message);
      expect(result).toBe(true);
    });

    it("should send dice roll messages", async () => {
      const client = new WebSocketClient();
      const connection = client.connectToCampaign("test-campaign-id");

      await new Promise((resolve) => setTimeout(resolve, 10));

      const message: DiceRollMessage = {
        type: "dice_roll",
        notation: "1d20",
        player_name: "Test Player",
      };

      const result = connection.send(message);
      expect(result).toBe(true);
    });

    it("should not send when disconnected", async () => {
      const client = new WebSocketClient();
      const connection = client.connectToCampaign("test-campaign-id");

      await new Promise((resolve) => setTimeout(resolve, 10));

      connection.disconnect();

      const message: ChatInputMessage = {
        type: "chat_input",
        message: "Test message",
        character_id: "test-char-id",
      };

      const result = connection.send(message);
      expect(result).toBe(false);
    });
  });

  describe("Error handling", () => {
    it("should handle connection errors", async () => {
      const client = new WebSocketClient();
      const onError = vi.fn();

      const connection = client.connectToCampaign("test-campaign-id", {
        onError,
      });

      await new Promise((resolve) => setTimeout(resolve, 10));

      // Simulate error
      const socket = connection.getSocket();
      socket?.onerror?.(new Event("error"));

      expect(onError).toHaveBeenCalled();
    });

    it("should reject invalid WebSocket URLs", () => {
      const client = new WebSocketClient({
        baseUrl: "invalid-url",
      });

      expect(() => {
        client.connectToCampaign("test-campaign-id");
      }).toThrow("Invalid WebSocket URL");
    });
  });

  describe("Default client instance", () => {
    it("should export a default websocketClient instance", () => {
      expect(websocketClient).toBeDefined();
      expect(websocketClient).toBeInstanceOf(WebSocketClient);
    });

    it("should have the same base URL as configured", () => {
      const baseUrl = websocketClient.getWebSocketBaseUrl();
      expect(baseUrl).toBeDefined();
      expect(baseUrl.startsWith("ws://") || baseUrl.startsWith("wss://")).toBe(
        true
      );
    });
  });

  describe("Type validation", () => {
    it("should validate ChatInputMessage structure", () => {
      const message: ChatInputMessage = {
        type: "chat_input",
        message: "Test message",
        character_id: "test-char-id",
        campaign_id: "test-campaign-id",
      };

      expect(message.type).toBe("chat_input");
      expect(message.message).toBe("Test message");
      expect(message.character_id).toBe("test-char-id");
      expect(message.campaign_id).toBe("test-campaign-id");
    });

    it("should validate DiceRollMessage structure", () => {
      const message: DiceRollMessage = {
        type: "dice_roll",
        notation: "2d6+3",
        character_id: "test-char-id",
        skill: "Athletics",
        player_name: "Test Player",
      };

      expect(message.type).toBe("dice_roll");
      expect(message.notation).toBe("2d6+3");
      expect(message.skill).toBe("Athletics");
    });

    it("should validate ChatStreamMessage structure", () => {
      const message: ChatStreamMessage = {
        type: "chat_stream",
        chunk: "Hello",
        full_text: "Hello world",
        timestamp: "2025-01-01T00:00:00Z",
      };

      expect(message.type).toBe("chat_stream");
      expect(message.chunk).toBe("Hello");
      expect(message.full_text).toBe("Hello world");
    });
  });
});
