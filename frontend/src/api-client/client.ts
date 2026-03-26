/**
 * Typed API client using openapi-fetch + openapi-typescript.
 *
 * `paths` is generated from the backend OpenAPI schema by running:
 *   bun run generate:api
 *
 * Migration note: the codebase previously used @openapitools/openapi-generator-cli
 * which produced runtime classes (GameApi, DefaultApi, Configuration) plus enum/interface
 * types. The new approach generates only a TypeScript type definition file (schema.d.ts)
 * and uses openapi-fetch for runtime HTTP calls via a single `api` instance.
 *
 * To migrate an existing call:
 *   BEFORE (generated axios client):
 *     const response = await gameApi.getCharacterGameCharacterCharacterIdGet(id);
 *     return response.data;
 *
 *   AFTER (openapi-fetch):
 *     const { data, error } = await api.GET("/game/character/{character_id}", {
 *       params: { path: { character_id: id } },
 *     });
 *     if (error) throw error;
 *     return data;
 *
 * All path/query/body types are inferred automatically from the schema, giving
 * the same compile-time safety without Java or generated runtime code.
 */
import createClient from "openapi-fetch";
import { getApiBaseUrl } from "../utils/urls";
import type { paths } from "./schema.d.ts";

const API_BASE = getApiBaseUrl();

/** Typed API client -- use this for all new backend calls. */
export const api = createClient<paths>({
  baseUrl: API_BASE,
});
