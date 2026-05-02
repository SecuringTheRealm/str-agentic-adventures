---
name: release
description: "Releases a new version by determining bump type from conventional commits, running lint and test checks, tagging, pushing, and creating a GitHub release. Use when ready to cut a release from main."
disable-model-invocation: true
---

## Steps

1. **Determine bump type** from commits since the last tag:
   - If `$ARGUMENTS` is `major`, `minor`, or `patch`, use that directly.
   - Otherwise, inspect `git log $(git describe --tags --abbrev=0)..HEAD --oneline`:
     - Any commit mentioning "breaking" or "BREAKING CHANGE" -> major
     - Any commit with `feat:` prefix -> minor
     - Otherwise -> patch

2. **Calculate next version**: parse the latest tag (`git describe --tags --abbrev=0`),
   increment the appropriate component, reset lower components to 0.

3. **Pre-flight checks** (abort on failure):
   - `git status` must show a clean working tree (no uncommitted changes).
   - `git branch --show-current` must be `main`.
   - `uv run ruff check .` must pass (Python lint).
   - `cd frontend && bun lint` must pass (Frontend lint via Biome).
   - `uv run pytest backend/tests/ -v` must pass (Python tests).
   - `cd frontend && bun test:run` must pass (Frontend tests).

4. **Tag and release**:
   - `git tag v<MAJOR>.<MINOR>.<PATCH>`
   - `git push origin main`
   - `git push origin v<MAJOR>.<MINOR>.<PATCH>`
   - `gh release create v<MAJOR>.<MINOR>.<PATCH> --generate-notes`

5. **Report**: print the new version, release URL, and a one-line summary.
