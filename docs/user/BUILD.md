# Build & Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Bun](https://bun.sh/) (frontend runtime and package manager)
- Docker (optional, for container builds)

## Quick Start

```bash
# 1. Install dependencies
cd backend && uv sync
cd frontend && bun install

# 2. Copy environment config
cp .env.example .env   # then fill in your values

# 3. Start the backend (from repo root)
cd backend && uv run uvicorn app.main:app --reload

# 4. Start the frontend (separate terminal)
cd frontend && bun dev
```

The backend runs on `http://localhost:8000`, the frontend on `http://127.0.0.1:5173`.

## Common Tasks

| Task | Backend | Frontend |
|------|---------|----------|
| Install deps | `cd backend && uv sync` | `cd frontend && bun install` |
| Run dev server | `cd backend && uv run uvicorn app.main:app --reload` | `cd frontend && bun dev` |
| Run tests | `uv run pytest backend/tests/ -v` | `cd frontend && bun test:run` |
| Lint | `uv run ruff check .` | `cd frontend && bun lint` |
| Format | `uv run ruff format .` | `cd frontend && bunx biome check --write .` |
| Generate API client | `./scripts/generate-client.sh` | |
| Production build | | `cd frontend && bun run build` |

## API Client Generation

The frontend uses `openapi-typescript` to generate a typed API client from the backend's OpenAPI schema. No Java is needed.

```bash
# No running backend needed -- exports the OpenAPI spec directly from the FastAPI app:
./scripts/generate-client.sh
```

The generated file (`frontend/src/api-client/schema.d.ts`) is committed to git (commit-and-verify pattern) -- regenerate and commit it after any backend API change.

## Container Builds

```bash
# Build (from repo root)
docker build -t str-agentic-adventures .

# Run
docker run -p 8000:8000 str-agentic-adventures
```

## UV Package Manager

[uv](https://docs.astral.sh/uv/) manages all Python dependencies.

```bash
uv add <package>      # Add a dependency
uv remove <package>   # Remove a dependency
uv lock               # Refresh lock file after changes
uv run <command>      # Run a command in the uv environment
uv sync --frozen      # Install exact versions from lock file (CI)
```

`pyproject.toml` is the single source of truth for dependencies. `uv.lock` is committed for reproducible installs. Run `uv lock` locally if CI reports lock file drift, then commit the updated file.
