# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file for initial dependency installation 
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies using pip for now (can be updated to use uv later)
RUN pip install --no-cache-dir -r requirements.txt

# Copy Makefile for build commands (when available in container)
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
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Use python directly for now (can be updated to use make when uv is available in container)
CMD ["python", "-m", "backend.app.main"]