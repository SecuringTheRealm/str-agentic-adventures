# UV Migration Status

The repository now standardizes on [uv](https://docs.astral.sh/uv/) for Python dependency and workflow management. This document captures the current state, recommended developer practices, and maintenance tips.

## Current Implementation

- Root-level `pyproject.toml` is the single source of truth for dependency declarations.
- Workspace `uv.lock` files (root and `backend/uv.lock`) are committed for reproducible installs.
- The project `Makefile` wraps common tasks (`make deps`, `make run`, `make test`) using `uv`.
- GitHub Actions workflows run `uv sync --frozen` to guarantee identical dependency sets in CI.

## Local Developer Workflow

```bash
# Install all dependencies
make deps

# Run tests
make test

# Start the backend with uv-run
make run
```

Additional uv commands developers may need:

```bash
uv add <package>             # Add a dependency to pyproject.toml
uv remove <package>          # Remove a dependency
uv lock                      # Refresh lock files after dependency changes
uv run <command>             # Execute commands within the uv environment
```

Run `uv sync --frozen` when you want to assert that the lock file is respected (e.g., in CI or reproducibility checks).

## CI/CD Integration

All GitHub Actions workflows install dependencies with `uv sync --frozen`, ensuring:
- Deterministic environments across unit, integration, and E2E pipelines
- Faster installs compared to pip thanks to uv's Rust-based resolver
- Automatic alignment with the checked-in lock files

If CI fails because of out-of-date locks, regenerate them locally (`uv lock`) and commit the updated files.

## Legacy Artifacts

- `requirements.txt` files have been removed. Always use `uv` commands instead of `pip install`.
- Legacy scripts that previously invoked `pip` now delegate to the Makefile targets backed by uv.

## Troubleshooting

| Symptom | Resolution |
| ------- | ---------- |
| `ModuleNotFoundError` for project dependencies | Run `make deps` (or `uv sync`) from the repository root to hydrate the uv environment. |
| Lock file drift error (`uv sync --frozen` fails) | Execute `uv lock` locally, verify changes, and commit updated lock files. |
| CI uses outdated dependencies | Confirm the workflow is running `uv sync --frozen` and that the lock files are committed. |

For more background on the migration away from Semantic Kernel workflows and the adoption of uv-backed tooling, review [docs/migration-guide-azure-ai-sdk.md](../migration-guide-azure-ai-sdk.md).
