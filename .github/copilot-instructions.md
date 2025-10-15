# Secure the Realm - Agentic Adventures

AI-powered tabletop RPG application with a FastAPI backend and React frontend orchestrated by specialized AI agents.

## Start Here
- Read `AGENTS.md` for repository-wide security guardrails, project structure, coding standards, testing expectations, and PR workflow.
- Only fall back to discovery or shell inspection when behavior differs from what `AGENTS.md` describes.

## Copilot Runner Setup
- The `.github/workflows/copilot-setup-steps.yml` workflow preps the runner before each Copilot session by:
  - Installing Python 3.12, Node.js 20, and caching UV and npm dependencies.
  - Checking out the repository and syncing dependencies via `uv` and `npm`.
  - Exporting configured Azure secrets to the runner so backend tests and Playwright suites can use real services.
- Secrets currently surfaced: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_CHAT_DEPLOYMENT`. Optional secrets include `AZURE_CLIENT_ID`, `AZURE_OPENAI_API_VERSION`, `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`, `AZURE_OPENAI_DALLE_DEPLOYMENT`, `AZURE_SUBSCRIPTION_ID`, and `AZURE_TENANT_ID`.
- Secrets are masked in logs and are only present for the duration of the session; configure them as standard repository secrets.

## Manual Bootstrap (if the workflow fails)
1. Install UV:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   ```
2. Install backend deps and start the API:
   ```bash
   make deps
   make run
   ```
3. In another shell:
   ```bash
   cd frontend
   npm install
   npm run generate:api  # backend must be running
   npm run dev
   ```

## Development Loop Essentials
- Backend quick commands: `make run`, `make test`, `make lint`, `make format`.
- Frontend quick commands: `npm run dev`, `npm run build`, `npm run test:run`, `npm run test:e2e`, `npm run lint`.
- Regenerate `src/api-client/` after any backend contract change with `npm run generate:api`; never edit generated files manually.
- Local `.env` files must stay uncommitted and should mirror placeholder values from `.env.example`.

## Validation Checklist
- Run impacted test suites (Pytest, Vitest, Playwright) and ensure format/lint checks succeed before pushing.
- Manually exercise core flows when relevant: campaign creation, character creation, and backend health checks (`curl http://localhost:8000/health`).
- Confirm OpenAPI schema availability (`curl http://localhost:8000/openapi.json`) when altering APIs.
- For Playwright work, lean on the Codex MCP helpers (`pw-explore-website`, `pw-generate-tests`, `pw-manual-testing`) outlined in the automation guide: https://blog.gopenai.com/automating-e2e-chat-flow-testing-with-codex-playwright-mcp-1ce4020dcbca.

## Troubleshooting Notes
- Node.js 20 works despite `package.json` targeting 22; expect warnings only.
- Missing UV? Re-run the install script above.
- Frontend errors about missing API client mean `npm run generate:api` was skipped or backend was offline.
- Some backend tests fail without Azure OpenAI credentials; configure local secrets when debugging those cases.
- `scripts/validate-openapi-client.sh` assumes a pip-style requirements file—adjust or bypass if using UV.

## Key Documentation
- `docs/AZURE_OPENAI_REQUIREMENTS.md` – Azure configuration and testing implications.
- `docs/specs/TESTING_STRATEGY.md` – Detailed testing approach and coverage guardrails.
- `docs/deployment.md` – Azure deployment playbooks.
- `docs/contributions.md` – Open source acknowledgements for foundational tooling.
- `AGENTS.md` – Repository guidelines kept in sync with this file.

## Documentation Maintenance
- When adding or removing docs in `docs/`, update the reference lists here and in `AGENTS.md`.
- Keep instructions concise and avoid duplicating guidance already captured in `AGENTS.md`; link instead.
