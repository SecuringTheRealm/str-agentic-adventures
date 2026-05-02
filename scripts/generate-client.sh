#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Export OpenAPI spec from FastAPI (no running server needed)
uv run python "$REPO_ROOT/scripts/export_openapi.py"

# Generate TypeScript types from spec
cd "$REPO_ROOT/frontend"
bunx openapi-typescript "$REPO_ROOT/openapi.json" -o src/api-client/schema.d.ts

# Format generated output
bunx biome format --write src/api-client/schema.d.ts 2>/dev/null || true
