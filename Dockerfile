# Production-optimized multi-stage Dockerfile
# Solves certificate issues and reduces image size

# Stage 1: Build dependencies
FROM python:3.12-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install build dependencies and UV using installer script
# This avoids certificate issues with pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Add UV to PATH for this stage
ENV PATH="/root/.local/bin:$PATH"

# Copy pyproject.toml, uv.lock, and README.md for dependency installation
COPY pyproject.toml uv.lock README.md ./

# Install dependencies in virtual environment
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev

# Stage 2: Production runtime
FROM python:3.12-slim-bookworm AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser backend/ ./backend/

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Create app directories with proper permissions
RUN mkdir -p /app/logs /app/data \
    && chown -R appuser:appuser /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "-m", "app.main"]