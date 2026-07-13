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
- Chat runs through the GA Microsoft Agent Framework (`agent-framework-foundry`): the singleton `agent_client_manager` in `backend/app/agent_client_setup.py` wraps a `FoundryChatClient` (Foundry project endpoint + `DefaultAzureCredential`). Chat agents call `self.azure_client.chat_completion(...)` (their `azure_client` is the manager); never instantiate clients directly.
- Availability is config-based: `settings.is_foundry_configured()` (chat) and `settings.is_azure_openai_configured()` (images). When unconfigured, agents use deterministic fallback logic — never call Azure. CI has no secrets, so fallback must always work.
- Per-agent model: set `deployment_setting` on the agent (env `AZURE_OPENAI_{DM,NARRATOR,COMBAT}_DEPLOYMENT`, defaulting to `AZURE_OPENAI_CHAT_DEPLOYMENT`). No model router.
- Images only: `azure_openai_client` (`AsyncAzureOpenAI.images.generate`, gpt-image-1 family). Not for chat.
- Circuit breaker (pybreaker) wraps the real Azure chat + image calls — 3 failures trips open, 60s auto-reset. Check `/health/dependencies`.
- See ADR-0023 (supersedes-in-part ADR-0018) for architectural decisions.

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
