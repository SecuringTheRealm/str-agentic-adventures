---
name: api-client
description: OpenAPI client generation workflow, Java requirement, regeneration triggers
---

# API Client Workflow

## Key Facts
- `frontend/src/api-client/` is auto-generated and NOT committed to git
- Requires Java (OpenJDK): `brew install openjdk` on macOS
- Backend must be running at `http://localhost:8000`

## Generate
```bash
cd frontend && npm run generate:api
```

## When to Regenerate
- After ANY backend API schema change (models, endpoints, request/response types)
- After adding/removing/modifying route decorators
- After changing Pydantic model fields

## After Regeneration
- Restart frontend dev server to pick up changes
- Re-run `npm run build` to verify TypeScript compiles
- Re-run `npm run test:run` to verify tests pass

## CI/CD
- Deploy workflow generates client from the deployed backend's OpenAPI schema
- PR checks do NOT generate the client (no backend running in CI)
