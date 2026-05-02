---
name: api-client
description: "Triggers when the agent modifies backend API routes, Pydantic models, or request/response types; when frontend TypeScript shows type errors against api-client/; or when openapi.json or schema.d.ts need regeneration. Covers the openapi-typescript generation workflow."
---

# API Client Workflow

## Key Facts
- Tool: `openapi-typescript` (NOT openapi-generator, NOT Java)
- Output: `frontend/src/api-client/schema.d.ts` (committed to git)
- Schema source: `frontend/openapi.json` (committed to git)
- No running backend needed — uses the committed `openapi.json`
- Frontend uses `openapi-fetch` SDK client via `frontend/src/services/api.ts`

## Generate
```bash
./scripts/generate-client.sh
```

## When to Regenerate
- After ANY backend API schema change (models, endpoints, request/response types)
- After adding/removing/modifying route decorators
- After changing Pydantic model fields

## After Regeneration
- Commit both `openapi.json` and `schema.d.ts` together (commit-and-verify pattern)
- Run `cd frontend && bun run build` to verify TypeScript compiles
- Run `cd frontend && bun test:run` to verify tests pass

## Usage Rules
- All API calls go through `frontend/src/services/api.ts` — never import from `api-client/` directly
- The `api.ts` service wraps `openapi-fetch` with typed helpers
