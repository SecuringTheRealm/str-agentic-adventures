# UV Migration Plan

This document outlines the plan to complete the migration to UV (modern Python package manager) for fully reproducible dependency management.

## Current State (Phase 1 - Complete)

✅ **Centralized Configuration**
- Root `pyproject.toml` with all project metadata and dependencies
- Tool configurations consolidated ([tool.ruff], [tool.pytest])
- Eliminated duplication between `backend/requirements.txt` and `backend/pyproject.toml`

✅ **Backward Compatibility**
- Generated root `requirements.txt` from `pyproject.toml` for CI/CD
- Tests work from both root and backend directories
- Updated CI to use centralized dependency management

## Phase 2 - UV Integration (Future)

**When UV is available, complete the migration with:**

### 1. Install UV in CI
```yaml
- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Generate UV Lock File
```bash
uv lock
```
This will create `uv.lock` for fully reproducible builds.

### 3. Update CI to Use UV
```yaml
- name: Install dependencies with UV
  run: uv sync
```

### 4. Remove Traditional Requirements.txt
- Remove root `requirements.txt` (generated from pyproject.toml)
- Keep `backend/requirements.txt` only for legacy compatibility during transition
- Eventually remove `backend/requirements.txt` completely

### 5. Update pyproject.toml [tool.uv] Section
- Add UV-specific configurations
- Configure lock file management
- Set development group configurations

## Benefits After Full UV Migration

- **Reproducible Builds**: Exact dependency versions locked across environments
- **Faster Installs**: UV's Rust-based resolver is significantly faster
- **Better Conflict Resolution**: Superior dependency resolution algorithm  
- **Modern Tooling**: Industry-standard approach for Python projects
- **Simplified Workflow**: Single source of truth for all dependencies

## Migration Commands

```bash
# Current state (working)
pip install -r requirements.txt

# Future state with UV
uv sync                    # Install all dependencies
uv add package            # Add new dependency
uv remove package         # Remove dependency
uv lock                   # Update lock file
```

## Dependencies Validation

The project's dependency validation tests have been updated to check:
1. Root `pyproject.toml` first (preferred)
2. Fallback to `backend/requirements.txt` if needed
3. Support for both execution contexts (root and backend directories)

This ensures continuity during the UV migration process.