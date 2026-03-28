# Secure the Realm — Claude Code Guidelines

## Security Guardrails
- Never commit secrets, API keys, or real connection strings.
- `.env.example` and docs must use placeholders like `your-api-key-goes-here`.
- Real credentials: local `.env` (gitignored), GitHub secrets, or Azure Key Vault only.

## Critical Gotchas
- `src/api-client/schema.d.ts` is auto-generated and NOT in git. Run `cd frontend && bun run generate:api` after cloning (requires running backend). No Java needed — uses `openapi-typescript`.
- After backend API schema changes, regenerate the client (`bun run generate:api`) and restart the frontend dev server.
- Use SQLAlchemy ORM for all DB interactions — never raw sqlite3/psycopg2.
- Alembic migrations run automatically on startup.

## Agent Framework
- Use the singleton `azure_openai_client` from `backend/app/azure_openai_client.py` — never instantiate clients directly.
- All agents MUST handle Azure OpenAI unavailability: when `is_configured()` returns False, use deterministic fallback logic.
- Microsoft Agent Framework SDK (azure-ai-agents) lifecycle: `create_agent` → `create_thread` → `add_message` → `create_and_process_run`. See `agent_client_setup.py`.
- Circuit breaker (pybreaker) guards Azure calls — 3 failures trips open, 60s auto-reset. Check `/health/dependencies`.
- See ADR-0018 for architectural decisions.

## Testing
- Coverage: 90% new code, 85% overall. Never commit `.only` or `.skip`.
- When tests fail, fix the code — never rewrite tests just to make them pass.

## Tooling
- Python: `uv sync`, `uv run pytest backend/tests/ -v`, `uv run ruff check .`
- Frontend: `cd frontend && bun dev`, `bun test:run`, `bun lint`
- Use Bun over npm/npx for frontend. Use Biome (not eslint) for linting/formatting.
- Use `gh` CLI for all GitHub operations.

## GitHub Workflow
- **All work is tracked in GitHub issues.** Use `gh issue list` to find open work.
- **Start work:** mention the issue number in commits. Use worktrees for isolation: `git worktree add`.
- **Complete work:** close with `gh issue close <number> -c "Fixed in <commit>"`.
- **Create issues:** `gh issue create --title "type: description" --label "label"`.
- **Assign to Copilot** (small, mechanical tasks): `gh issue edit <number> --add-assignee @copilot`.
- **Assign to yourself:** `gh issue edit <number> --add-assignee @me`.
- **Review Copilot PRs:** `gh pr list --author "app/copilot-swe-agent"`. Merge ready ones with `gh pr merge <n> --squash`.
- **Sync before work:** `git pull --rebase origin main` then `git push origin main`.
- **Labels:** `priority:critical`, `priority:high`, `priority:medium`, `bug`, `security`, `cleanup`, `architecture`, `game-engine`, `frontend`, `infra`, `cost`.

## Sprint Plan
Work is organised in sprints tracked via GitHub issues (#567 is the master tracking issue):
- **Sprint 1-4 (complete):** Foundation, game engine basics, modernisation
- **Sprint 5 (complete):** Security & infrastructure hardening — #558 MI, #557 Key Vault, #559 PostgreSQL, #564 blob lockdown, #563 deploy safety, #568 Agent Framework, #569 thread persistence
- **Sprint 6 (complete):** Observability & reliability — #560 OpenTelemetry, #561 circuit breakers, #562 rate limiter, #570 parallel agents, #480 health probes, #565 Bicep params, #566 cost budget
- **Sprint 7 (active):** Game engine depth — #416 game wiring, #418 shadcn/ui, #419 battle maps, #421 openapi-typescript
  - **QA Remediation (complete):** 56 bugs fixed across 12 PRs (#724-#735) — ability scores, combat system, Agent Framework SDK wiring, WebSocket security, frontend polish
- **Backlog:** #511 multiplayer WebSockets, #512 mobile redesign, #513 azd integration, #407 FLUX, #404 diarisation

## Commits
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Reference issues: `fix: migrate to gpt-image-1-mini (closes #408)`.
