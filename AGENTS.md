# Repository Guidelines

## Security & Configuration Guardrails
- Never commit secrets, API keys, or real connection strings. `.env.example`, docs, and committed configs must use placeholders such as `your-api-key-goes-here` and `your-resource-name`.
- Keep real credentials in local `.env` files (gitignored), GitHub secrets, Azure Key Vault, or deployment env vars only.
- Before committing config changes, re-check `.env.example`, docs, and Azure resource names for accidental secrets.

## Project Structure & Module Organization
- `backend/`: FastAPI & Semantic Kernel services, SQLAlchemy models, and backend tests under `backend/tests/`.
- `frontend/`: TypeScript + React UI, generated OpenAPI client in `src/api-client/` (never edit manually), tests in `src/__tests__/` and `e2e/`.
- `docs/`: Architecture (`docs/adr/`), design, specs, reference, and user guides. Update or link here instead of adding root-level docs.
- `infra/`: Azure deployment artifacts and automation.
- `.bmad-core/agents/`: BMAD agent playbooks used by orchestration tooling.

## Development Environment Setup
- Python 3.12+ with [UV](https://github.com/astral-sh/uv). Run `make deps` to sync backend dependencies from `pyproject.toml` / `uv.lock`.
- Node.js ≥22 (CI uses 20). Install frontend packages with `npm install` inside `frontend/`.
- Java (OpenJDK) for OpenAPI client generation: `brew install openjdk` on macOS. Required for `npm run generate:api`. In GitHub Actions runner, Java is pre-installed.
- SQLite for local development (no external DB needed). Use `sqlite3` CLI.
- Copy `.env.example` to `.env` in backend and frontend as needed; fill with local secrets only.
- **First-time setup**: After starting the backend, generate the frontend API client with `cd frontend && npm run generate:api`.

## Build, Test, and Development Commands
- `make run`: start the backend at `http://localhost:8000`.
- `cd frontend && npm run dev`: start the Vite dev server at `http://127.0.0.1:5173`.
- `make test`: execute backend pytest suite with UV.
- `cd frontend && npm run test:run`: run Vitest in watchless mode; `npm run test:e2e` launches Playwright (requires `npx playwright install` once).
- `make lint` / `make format`: Ruff linting + formatting for Python; `cd frontend && npm run lint` uses Biome.
- `cd frontend && npm run build`: type-check with `tsc --noEmit` and build production bundle.

## Coding Style & Naming Conventions
- **Python**: 4-space indentation, snake_case for functions/vars, PascalCase for classes, ALL_CAPS constants. Enforce Ruff (line length 88) and type hints on all functions. Use SQLAlchemy ORM for all database interactions.
- **TypeScript/React**: Prefer functional components with hooks, PascalCase for components/types, camelCase for variables, ALL_CAPS constants. Biome handles lint + format.
- **General**: Keep components small, follow existing directory layout, remove orphaned files instead of leaving placeholders.
- **Detailed Standards**: See `.github/instructions/` for comprehensive language-specific coding standards, error handling patterns, and best practices.

## Testing Guidelines
- **Backend**: Pytest with `pytest-asyncio`; tests in `backend/tests/` follow `test_*.py`. Mock external services; keep tests deterministic.
- **Frontend**: Vitest + Testing Library for unit/UI tests, Playwright for E2E. Unit tests in `__tests__/` or `*.test.ts[x]`; E2E in `e2e/*.spec.ts`.
- **Coverage**: 90% for new code, 85% overall (statements/branches/functions/lines). Never commit `.only`, `.skip`, or disabled tests.
- **Core Principle**: When tests fail, investigate and fix the code issue—never rewrite tests just to make them pass.
- **Playwright**: Use Codex MCP commands (`pw-explore-website`, `pw-generate-tests`, `pw-manual-testing`) per the [Codex Playwright MCP blog](https://blog.gopenai.com/automating-e2e-chat-flow-testing-with-codex-playwright-mcp-1ce4020dcbca).
- **Detailed Standards**: See `.github/instructions/testing.instructions.md` for comprehensive testing practices, test integrity rules, and failure resolution processes.

## Database & Migration Guidelines
- **ORM Requirement**: Use SQLAlchemy ORM for all database interactions—never use raw database connectors (sqlite3, psycopg2).
- **Migrations**: Use Alembic for all schema changes. Migrations run automatically on startup. Create with `alembic revision --autogenerate -m "description"`.
- **Version Control**: Never commit database files (`*.db`, `*.sqlite`). Use `.gitignore` to prevent accidental commits.
- **Detailed Standards**: See `.github/instructions/database.instructions.md` for migration workflows, environment configuration, and data management patterns.

## API Client & Integration Workflow
- **CRITICAL**: The frontend TypeScript client (`src/api-client/`) is generated from the backend OpenAPI schema and is **NOT** committed to the repository.
- **Initial Setup**: Run `cd frontend && npm run generate:api` after cloning the repository to generate the client (backend must be running at `http://localhost:8000`).
- **Requirements**: OpenAPI Generator CLI requires Java. Install with `brew install openjdk` on macOS.
- **When to Regenerate**: After any backend API schema change (models, endpoints, request/response types), regenerate with `cd frontend && npm run generate:api`.
- **Never Edit Manually**: The `src/api-client/` directory is auto-generated. Wrap generated calls in service modules (`src/services/`) instead.
- **After Regeneration**: Restart the frontend dev server to pick up changes, then re-run builds and tests.
- **Validation**: Use `./scripts/validate-openapi-client.sh` when modifying shared contracts.

## Documentation Expectations
- **Structure**: Place new docs under appropriate `docs/` subdirectory (adr/, design/, specs/, reference/, user/). Follow snake_case filenames.
- **Documentation Hierarchy**: `AGENTS.md` provides high-level repository guidelines; `.github/instructions/` contains detailed, file-specific standards; `docs/` holds architecture, specs, and user guides.
- **Style**: Use US English, active voice, and provide code or command snippets where they clarify steps.
- **Key References**:
  - `docs/AZURE_OPENAI_REQUIREMENTS.md` - Azure setup patterns
  - `docs/specs/TESTING_STRATEGY.md` - Test coverage practices
  - `docs/contributions.md` - Critical dependencies acknowledgement
- **Detailed Standards**: See `.github/instructions/documentation.instructions.md` for file naming, content standards, and maintenance practices. See `.github/instructions/adr.instructions.md` for ADR-specific guidelines.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat: ...`, `fix: ...`, `docs: ...`) as seen in `git log`; group related changes per commit.
- Before opening a PR, ensure formatting, linting, tests, and OpenAPI regeneration (if applicable) have run successfully.
- PRs should include: concise summary, linked issues (e.g., `Closes #123`), screenshots for UI changes, notes on regenerated assets or migrations, and test evidence.
- Keep PRs focused; update documentation and ADRs alongside the code they describe.

# BMAD Agents
agents:
  - id: analyst
    path: .bmad-core/agents/analyst.md
  - id: architect
    path: .bmad-core/agents/architect.md
  - id: bmad-master
    path: .bmad-core/agents/bmad-master.md
  - id: bmad-orchestrator
    path: .bmad-core/agents/bmad-orchestrator.md
  - id: dev
    path: .bmad-core/agents/dev.md
  - id: pm
    path: .bmad-core/agents/pm.md
  - id: po
    path: .bmad-core/agents/po.md
  - id: qa
    path: .bmad-core/agents/qa.md
  - id: sm
    path: .bmad-core/agents/sm.md
  - id: ux-expert
    path: .bmad-core/agents/ux-expert.md