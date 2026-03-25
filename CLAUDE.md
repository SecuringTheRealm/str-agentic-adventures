# Secure the Realm — Claude Code Guidelines

## Security Guardrails
- Never commit secrets, API keys, or real connection strings.
- `.env.example` and docs must use placeholders like `your-api-key-goes-here`.
- Real credentials: local `.env` (gitignored), GitHub secrets, or Azure Key Vault only.

## Critical Gotchas
- `src/api-client/` is auto-generated and NOT in git. Run `cd frontend && bun run generate:api` after cloning (requires Java + running backend).
- After backend API schema changes, regenerate the client and restart the frontend dev server.
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

## Issue Tracking
- Track work via GitHub issues. Use `gh issue list` to find open work.
- When starting work on an issue: mention the issue number in commits.
- When work is complete: close with `gh issue close <number> -c "Fixed in <commit>"`.
- Create issues for new findings: `gh issue create --title "type: description" --label "label"`.
- Assign small, self-contained issues to Copilot: `gh issue edit <number> --add-assignee @copilot`.
- Assign to yourself: `gh issue edit <number> --add-assignee @me`.
- Available labels: `priority:critical`, `priority:high`, `priority:medium`, `bug`, `security`, `cleanup`, `architecture`, `game-engine`, `frontend`, `infra`, `cost`.

## Commits
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Reference issues: `fix: migrate to gpt-image-1-mini (closes #408)`.
