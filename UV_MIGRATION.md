# UV Migration Plan

This document outlines the completed migration to UV (modern Python package manager) for fully reproducible dependency management.

## Current State (Phase 2 - Complete ✅)

✅ **UV Integration Complete**
- Root `pyproject.toml` with all project metadata and dependencies
- UV lockfile (`uv.lock`) for fully reproducible builds  
- Tool configurations consolidated ([tool.ruff], [tool.pytest])
- CI/CD workflows updated to use UV instead of pip
- Backend scripts updated to use UV sync
- Docker configuration updated to use UV

✅ **Centralized Configuration**
- Root `pyproject.toml` with all project metadata and dependencies
- Tool configurations consolidated ([tool.ruff], [tool.pytest])  
- Eliminated duplication between `backend/requirements.txt` and `backend/pyproject.toml`

✅ **Backward Compatibility Maintained**
- Generated root `requirements.txt` from `pyproject.toml` for CI/CD
- Tests work from both root and backend directories
- Updated CI to use centralized dependency management

## Benefits After Full UV Migration

- **Reproducible Builds**: Exact dependency versions locked across environments via `uv.lock`
- **Faster Installs**: UV's Rust-based resolver is significantly faster than pip
- **Better Conflict Resolution**: Superior dependency resolution algorithm  
- **Modern Tooling**: Industry-standard approach for Python projects
- **Simplified Workflow**: Single source of truth for all dependencies

## Migration Commands

```bash
# Current state with UV (working)
uv sync                    # Install all dependencies
uv add package            # Add new dependency
uv remove package         # Remove dependency
uv lock                   # Update lock file
uv lock --check           # Verify lockfile is up-to-date

# Legacy commands (still work for backward compatibility)
pip install -r requirements.txt
```

## Project Structure

```
str-agentic-adventures/
├── pyproject.toml         # Root project configuration and dependencies
├── uv.lock               # UV lockfile for reproducible builds
├── requirements.txt      # Generated from pyproject.toml (backward compatibility)
├── backend/
│   ├── requirements.txt  # Legacy file (still present for transition)
│   ├── start.sh          # Updated to use UV sync
│   ├── Dockerfile        # Updated to use UV
│   └── app/              # Application code
└── .github/workflows/    # CI/CD workflows updated to use UV
```

## Dependencies Validation

The project's dependency validation tests have been updated to check:
1. Root `pyproject.toml` first (preferred)
2. Fallback to `backend/requirements.txt` if needed
3. Support for both execution contexts (root and backend directories)

This ensures continuity during the UV migration process.

## CI/CD Integration

All workflows now use UV for dependency management:

```yaml
- name: Install UV
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Cache UV dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}

- name: Install dependencies with UV
  run: uv sync

- name: Validate lockfile is up-to-date
  run: uv lock --check
```

## Environment Setup

### Local Development
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository and install dependencies
git clone <repository>
cd str-agentic-adventures
uv sync

# Activate environment and start backend
source .venv/bin/activate
cd backend
python -m app.main
```

### Using Backend Start Script
```bash
cd backend
./start.sh  # Automatically installs UV and syncs dependencies
```

### Docker
```bash
# Docker automatically uses UV for dependency installation
docker build -t str-agentic-adventures .
docker run -p 8000:8000 str-agentic-adventures
```

## Troubleshooting

### Common Issues

1. **Lockfile out of date**: Run `uv lock` to regenerate
2. **Missing dependencies**: Run `uv sync` to install all dependencies
3. **CI failures**: Ensure `uv.lock` is committed to version control

### Updating Dependencies

```bash
# Add a new dependency
uv add fastapi

# Update a specific dependency
uv add "fastapi>=0.101.0"

# Update all dependencies
uv lock --upgrade

# Remove a dependency
uv remove old-package
```

## Migration Checklist (Completed ✅)

- [x] ✅ UV is the primary package manager for the project
- [x] ✅ `uv.lock` file is present and maintained
- [x] ✅ CI/CD pipeline successfully uses UV for dependency management
- [x] ✅ All environments (local, CI, production) have reproducible builds
- [x] ✅ Documentation is updated to reflect UV usage

## Success Criteria (All Met ✅)

- ✅ UV is the primary package manager for the project
- ✅ `uv.lock` file is present and maintained
- ✅ CI/CD pipeline successfully uses UV for dependency management
- ✅ All environments (local, CI, production) have reproducible builds
- ✅ Documentation is updated to reflect UV usage

The UV migration is now complete and the project uses modern, reproducible dependency management!