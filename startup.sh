#!/bin/bash
# Azure App Service Linux Startup Script for FastAPI
set -e

echo "Starting Azure App Service Python 3.12 Backend..."

# Ensure persistent directories exist under /home/site/data
mkdir -p /home/site/data/chroma /home/site/data/uploads/raw /home/site/data/uploads/processed /home/site/data/uploads/cache

# Install dependencies if required
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

# Execute Alembic Database Migrations
echo "Running Alembic database migrations..."
alembic upgrade head

# Start Gunicorn / Uvicorn server
echo "Launching FastAPI server..."
exec uvicorn backend.src.app:app --host 0.0.0.0 --port ${PORT:-8000}
