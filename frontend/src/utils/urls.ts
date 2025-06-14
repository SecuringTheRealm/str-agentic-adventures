/**
 * URL configuration utilities for consistent API and WebSocket URL construction
 */

// Get the base URL from environment, defaulting to localhost
const getBaseUrl = (): string => {
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
};

// Convert HTTP URLs to WebSocket URLs
const httpToWs = (url: string): string => {
  return url.replace(/^https?:\/\//, (match) =>
    match === 'https://' ? 'wss://' : 'ws://'
  );
};

/**
 * Get the API base URL with /api suffix
 */
export const getApiBaseUrl = (): string => {
  return `${getBaseUrl()}/api`;
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
