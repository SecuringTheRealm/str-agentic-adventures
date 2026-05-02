# Secure the Realm — Claude Code Guidelines

## Security Guardrails
- Never commit secrets, API keys, or real connection strings.
- `.env.example` and docs must use placeholders like `your-api-key-goes-here`.
- Real credentials: local `.env` (gitignored), GitHub secrets, or Azure Key Vault only.

## Critical Gotchas
- `src/api-client/schema.d.ts` is auto-generated and committed to git (commit-and-verify pattern). Regenerate via `./scripts/generate-client.sh` (no running backend needed). Uses `openapi-typescript`.
- After backend API schema changes, run `./scripts/generate-client.sh` and commit the updated `openapi.json` + `schema.d.ts`.

## Frontend API Access Pattern
- All backend API calls MUST go through `frontend/src/services/api.ts` (the SDK service layer).
- `services/api.ts` wraps the `openapi-fetch` SDK client at `api-client/client.ts`.
- Components import from `services/api.ts`, NEVER directly from `api-client/`.
- Direct `fetch()` calls to the backend are prohibited — use the SDK.
- Only exception: external service calls (e.g., Azure Realtime SDP exchange).

## Agent Framework
- Use the singleton `azure_openai_client` from `backend/app/azure_openai_client.py` — never instantiate clients directly.
- All agents MUST handle Azure OpenAI unavailability: when `is_configured()` returns False, use deterministic fallback logic.
- Microsoft Agent Framework SDK (azure-ai-agents) lifecycle: `create_agent` → `create_thread` → `add_message` → `create_and_process_run`. See `agent_client_setup.py`.
- Circuit breaker (pybreaker) guards Azure calls — 3 failures trips open, 60s auto-reset. Check `/health/dependencies`.
- See ADR-0018 for architectural decisions.

## Database
- Use SQLAlchemy ORM for all DB interactions — never raw sqlite3/psycopg2.
- Alembic migrations run automatically on startup.

## Testing
- Coverage: 90% new code, 85% overall. Never commit `.only` or `.skip`.
- When tests fail, fix the code — never rewrite tests just to make them pass.

## Tooling
- Python: `uv sync`, `uv run pytest backend/tests/ -v`, `uv run ruff check .`
- Frontend: `cd frontend && bun dev`, `bun test:run`, `bun lint`
- Use Bun over npm/npx for frontend. Use Biome (not eslint) for linting/formatting.
- Use `gh` CLI for all GitHub operations.

## GitHub Workflow
- **All work is tracked in GitHub issues** (#567 is the master tracking issue). Use `gh issue list` to find open work.
- **Start work:** mention the issue number in commits. Use worktrees for isolation: `git worktree add`.
- **Complete work:** close with `gh issue close <number> -c "Fixed in <commit>"`.
- **Create issues:** `gh issue create --title "type: description" --label "label"`.
- **Assign to Copilot** (small, mechanical tasks): `gh issue edit <number> --add-assignee @copilot`.
- **Assign to yourself:** `gh issue edit <number> --add-assignee @me`.
- **Review Copilot PRs:** `gh pr list --author "app/copilot-swe-agent"`. Merge ready ones with `gh pr merge <n> --squash`.
- **Sync before work:** `git pull --rebase origin main` then `git push origin main`.
- **Labels:** `priority:critical`, `priority:high`, `priority:medium`, `bug`, `security`, `cleanup`, `architecture`, `game-engine`, `frontend`, `infra`, `cost`.

## Commits
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Reference issues: `fix: migrate to gpt-image-1-mini (closes #408)`.
