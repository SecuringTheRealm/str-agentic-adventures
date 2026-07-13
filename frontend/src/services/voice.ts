/**
 * Thin SDK wrapper for the realtime voice token endpoint.
 *
 * Kept separate from services/api.ts (owned by another workstream in this
 * wave) so useRealtimeVoice.ts can go through the typed openapi-fetch client
 * instead of a hardcoded raw fetch().
 */
import { api } from "../api-client/client";
import type { paths } from "../api-client/schema.d.ts";

export type RealtimeTokenResponse =
  paths["/realtime/token"]["get"]["responses"][200]["content"]["application/json"];

export async function getRealtimeToken(): Promise<RealtimeTokenResponse> {
  const { data, error } = await api.GET("/realtime/token");
  if (error) throw error;
  return data;
}
