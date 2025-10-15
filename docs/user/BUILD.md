# Build System Documentation

This project uses a modern build system based on UV package manager and Make targets for consistent development and deployment workflows.

## Prerequisites

- Python 3.12+
- UV package manager (installed automatically by `make deps`)

## Quick Start

```bash
# Install dependencies
make deps

# Run the application
make run

# Run tests  
make test

# Generate frontend API client (runs validation workflow)
make generate-client

# Format and lint code
make format
make lint

# Clean temporary files
make clean
```

## Available Make Targets

| Target | Description |
|--------|-------------|
| `make deps` | Install all dependencies using uv sync |
| `make deps-prod` | Install production dependencies only |
| `make test` | Run all tests with pytest |
| `make run` | Start the backend server |
| `make lint` | Run linting checks with ruff |
| `make format` | Format code with ruff |
| `make clean` | Clean temporary files |
| `make dev-setup` | Complete development environment setup |
| `make generate-client` | Generate the frontend API client via validation script |
| `make validate-openapi-client` | Alias for `generate-client`; runs the full validation workflow |

## Legacy Scripts

- `backend/start.sh` - Now uses `make run` internally
- The original shell script logic has been replaced with standardized Make targets

## Container Builds

The Dockerfile now uses the modern build system:

```bash
# Build container (from repository root)
docker build -t str-agentic-adventures .

# Run container
docker run -p 8000:8000 str-agentic-adventures
```

## Key Improvements

1. **Reproducible builds** - Uses uv.lock for exact dependency versions
2. **Faster dependency resolution** - UV is significantly faster than pip
3. **Better layer caching** - Docker builds copy pyproject.toml and uv.lock first
4. **Consistent interface** - Same commands work in development and CI/CD
5. **Simplified maintenance** - Single source of truth for dependencies in pyproject.toml
