/**
 * URL configuration utilities for consistent API and WebSocket URL construction
 */
import { getConfiguredApiUrl } from "./environment";

// Get the base URL from environment, defaulting to localhost
const getBaseUrl = (): string => {
  const url = getConfiguredApiUrl();

  // Remove trailing slash to ensure consistent URL construction
  return url.replace(/\/+$/, "");
};

// Convert HTTP URLs to WebSocket URLs
const httpToWs = (url: string): string => {
  return url.replace(/^https?:\/\//, (match) =>
    match === "https://" ? "wss://" : "ws://"
  );
};

/**
 * Get the API base URL without /api suffix for OpenAPI client
 */
export const getApiBaseUrl = (): string => {
  return getBaseUrl();
};

/**
 * Get the WebSocket base URL with /api suffix
 */
export const getWebSocketBaseUrl = (): string => {
  return `${httpToWs(getBaseUrl())}/api`;
};

/**
 * Construct WebSocket URL for campaign connections
 */
export const getCampaignWebSocketUrl = (campaignId: string): string => {
  return `${getWebSocketBaseUrl()}/ws/${campaignId}`;
};

/**
 * Construct WebSocket URL for chat streaming
 */
export const getChatWebSocketUrl = (campaignId: string): string => {
  return `${getWebSocketBaseUrl()}/ws/chat/${campaignId}`;
};
