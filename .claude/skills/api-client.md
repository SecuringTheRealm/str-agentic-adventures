# OpenAPI Client Regeneration

## Key Facts
- `frontend/src/api-client/` is **auto-generated** and **not committed** to the repository.
- After cloning or after any backend API change, regenerate the client before running the frontend.
- The generator requires **Java** (OpenJDK). Install: `brew install openjdk` on macOS. Pre-installed in CI.

## When to Regenerate
- Any change to backend models, endpoints, request types, or response types.
- After pulling changes that include backend API modifications.

## Steps
```bash
# 1. Start the backend (must be running at http://localhost:8000)
make run

# 2. In another shell, regenerate the client
cd frontend && npm run generate:api

# 3. Restart the frontend dev server to pick up changes
# 4. Re-run builds and tests
npm run build
npm run test:run
```

## Validation
Run `./scripts/validate-openapi-client.sh` when modifying shared contracts.

## Never Edit Manually
Wrap generated calls in service modules (`src/services/`) instead of calling generated code directly.
