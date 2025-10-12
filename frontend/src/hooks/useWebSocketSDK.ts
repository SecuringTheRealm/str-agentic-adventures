/**
 * React hook for WebSocket connections using the unified SDK
 *
 * This hook wraps the WebSocketClient SDK to provide a React-friendly interface
 * for managing WebSocket connections in components.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import {
  type WebSocketConnectionOptions,
  type WebSocketMessage,
  wsClient,
} from "../services/api";

export interface UseWebSocketSDKOptions extends WebSocketConnectionOptions {
  /**
   * Type of WebSocket connection
   */
  connectionType: "campaign" | "chat" | "global";

  /**
   * Campaign ID (required for campaign and chat connections)
   */
  campaignId?: string;
}

export const useWebSocketSDK = (options: UseWebSocketSDKOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connectionRef = useRef<ReturnType<
    typeof wsClient.connectToCampaign
  > | null>(null);
  const shouldConnectRef = useRef(true);

  const {
    connectionType,
    campaignId,
    onConnect,
    onDisconnect,
    onMessage,
    onError,
    reconnectInterval,
    maxReconnectAttempts,
  } = options;

  const connect = useCallback(() => {
    if (connectionRef.current?.isConnected()) {
      return;
    }

    setIsConnecting(true);
    setError(null);

    try {
      const wrappedOptions: WebSocketConnectionOptions = {
        reconnectInterval,
        maxReconnectAttempts,
        onConnect: () => {
          setIsConnected(true);
          setIsConnecting(false);
          setError(null);
          onConnect?.();
        },
        onDisconnect: () => {
          setIsConnected(false);
          setIsConnecting(false);
          onDisconnect?.();
        },
        onMessage,
        onError: (event) => {
          setError("WebSocket connection error");
          setIsConnecting(false);
          onError?.(event);
        },
      };

      // Create connection based on type
      if (connectionType === "campaign") {
        if (!campaignId) {
          throw new Error("Campaign ID is required for campaign connections");
        }
        connectionRef.current = wsClient.connectToCampaign(
          campaignId,
          wrappedOptions
        );
      } else if (connectionType === "chat") {
        if (!campaignId) {
          throw new Error("Campaign ID is required for chat connections");
        }
        connectionRef.current = wsClient.connectToChat(
          campaignId,
          wrappedOptions
        );
      } else if (connectionType === "global") {
        connectionRef.current = wsClient.connectToGlobal(wrappedOptions);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to connect";
      setError(errorMessage);
      setIsConnecting(false);
    }
  }, [
    connectionType,
    campaignId,
    onConnect,
    onDisconnect,
    onMessage,
    onError,
    reconnectInterval,
    maxReconnectAttempts,
  ]);

  const disconnect = useCallback(() => {
    shouldConnectRef.current = false;
    if (connectionRef.current) {
      connectionRef.current.disconnect();
      connectionRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
  }, []);

  const sendMessage = useCallback((message: Partial<WebSocketMessage>) => {
    if (!connectionRef.current) {
      return false;
    }
    return connectionRef.current.send(message);
  }, []);

  // Connect on mount
  useEffect(() => {
    if (shouldConnectRef.current) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    socket: connectionRef.current?.getSocket() ?? null,
    isConnected,
    isConnecting,
    error,
    connect,
    disconnect,
    sendMessage,
    reconnectAttempts: connectionRef.current?.getReconnectAttempts() ?? 0,
  };
};
