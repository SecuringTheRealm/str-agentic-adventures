#!/bin/bash

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Navigate to project root for UV commands
cd "$(dirname "$0")/.."

# Sync dependencies using UV
echo "Installing dependencies with uv..."
uv sync

# Activate virtual environment
source .venv/bin/activate

# Navigate back to backend directory
cd backend

# Start the application
echo "Starting AI Dungeon Master backend..."
python -m app.main
