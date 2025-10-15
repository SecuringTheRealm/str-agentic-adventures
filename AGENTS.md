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
- Copy `.env.example` to `.env` in backend and frontend as needed; fill with local secrets only.

## Build, Test, and Development Commands
- `make run`: start the backend at `http://localhost:8000`.
- `cd frontend && npm run dev`: start the Vite dev server at `http://127.0.0.1:5173`.
- `make test`: execute backend pytest suite with UV.
- `cd frontend && npm run test:run`: run Vitest in watchless mode; `npm run test:e2e` launches Playwright (requires `npx playwright install` once).
- `make lint` / `make format`: Ruff linting + formatting for Python; `cd frontend && npm run lint` uses Biome.
- `cd frontend && npm run build`: type-check with `tsc --noEmit` and build production bundle.

## Coding Style & Naming Conventions
- Python: 4-space indentation, snake_case for functions/vars, PascalCase for classes, ALL_CAPS constants. Enforce Ruff (line length 88) and type hints on all functions.
- TypeScript/React: prefer functional components with hooks, use PascalCase for components/types, camelCase for variables, ALL_CAPS constants. Biome handles lint + format.
- Keep components small and leverage CSS modules; favor immutable data patterns (`const`, `readonly`) and optional chaining.
- Follow existing directory layout; remove orphaned files instead of leaving placeholders.

## Testing Guidelines
- Backend: Pytest with `pytest-asyncio`; tests live in `backend/tests/` and follow `test_*.py`. Mock Azure OpenAI and external services; keep tests deterministic.
- Frontend: Vitest + Testing Library for unit/UI tests, Playwright for E2E. Unit tests reside in `__tests__/` or `*.test.ts[x]`; E2E specs end with `.spec.ts`.
- Coverage targets (Vitest): 90% statements/branches/functions/lines on new code, 85% overall. Maintain Pytest markers (`unit`, `integration`, `slow`) and run affected suites locally.
- Regenerate coverage in CI (`vitest --coverage`, `pytest --cov`) and avoid committing `.only`, `.skip`, or disabled tests.
- For Playwright authoring, use the Codex MCP helper commands (`pw-explore-website`, `pw-generate-tests`, `pw-manual-testing`) described in the [Codex Playwright MCP blog](https://blog.gopenai.com/automating-e2e-chat-flow-testing-with-codex-playwright-mcp-1ce4020dcbca) to speed up exploration, test generation, and manual walkthroughs.

## API Client & Integration Workflow
- Regenerate the TypeScript OpenAPI client after any backend schema change: `cd frontend && npm run generate:api` (backend must be running).
- Never edit `src/api-client/` manually; wrap generated calls in service modules and re-run builds/tests after regeneration.
- Validate integration with `./scripts/validate-openapi-client.sh` when modifying shared contracts.

## Documentation Expectations
- Place new docs under the appropriate `docs/` subdirectory (ADR, design, specs, reference, user). Follow snake_case filenames and update ADR index when adding decisions.
- Keep `AGENTS.md` and `.github/copilot-instructions.md` aligned—if guidance lives here, avoid duplicating it elsewhere.
- Use US English, active voice, and provide code or command snippets where they clarify steps.
- Refer to `docs/AZURE_OPENAI_REQUIREMENTS.md` for Azure setup patterns and `docs/specs/TESTING_STRATEGY.md` for required test coverage practices before altering related code.
- Acknowledge critical dependencies in `docs/contributions.md`; update the list when introducing or removing major third-party tooling.

## Commit & Pull Request Guidelines
- Use Conventional Commits (`feat: ...`, `fix: ...`, `docs: ...`) as seen in `git log`; group related changes per commit.
- Before opening a PR, ensure formatting, linting, tests, and OpenAPI regeneration (if applicable) have run successfully.
- PRs should include: concise summary, linked issues (e.g., `Closes #123`), screenshots for UI changes, notes on regenerated assets or migrations, and test evidence.
- Keep PRs focused; update documentation and ADRs alongside the code they describe.
