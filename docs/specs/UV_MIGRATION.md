# UV Package Manager

The repository standardizes on [uv](https://docs.astral.sh/uv/) for Python dependency management. The migration from pip/requirements.txt is complete.

## Developer Reference

Full UV workflow documentation has been consolidated into the [Build Guide](../user/BUILD.md#uv-package-manager).

## Quick Summary

- `pyproject.toml` is the single source of truth for dependencies
- `uv.lock` is committed for reproducible installs
- CI runs `uv sync --frozen`; use `uv lock` locally to regenerate if lock drift occurs
- Use `make deps`, `make test`, `make run` for common tasks (all backed by uv)
