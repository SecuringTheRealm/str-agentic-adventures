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
Work is organised in sprints tracked via GitHub issues:
- **Sprint 1 (foundation):** #408, #409, #411 — Azure SDK, DALL-E migration, security
- **Sprint 2 (game engine):** #436-#441 — conversation history, agent orchestration, rules engine, dice, spells, opening experience
- **Sprint 3 (modernisation):** #414 architecture, #415 infra/Bicep, #418 frontend/shadcn, #419 battle maps
- **Backlog:** #407 FLUX investigation, #421 OpenAPI generator, #404 diarisation

## Commits
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Reference issues: `fix: migrate to gpt-image-1-mini (closes #408)`.
