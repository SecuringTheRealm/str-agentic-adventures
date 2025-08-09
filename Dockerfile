# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy pyproject.toml and uv.lock for dependency caching
COPY pyproject.toml uv.lock ./

# Install production dependencies using uv
RUN uv sync --frozen --no-dev

# Copy Makefile for build commands
COPY Makefile ./

# Copy application code
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD uv run python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Use make to run the application
CMD ["make", "run"]