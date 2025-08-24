#!/bin/bash
# Startup script for Insurance Management API

# Get the directory where this script is located (db folder)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get the project root (parent directory of db)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Activate virtual environment
source "$PROJECT_ROOT/venv/bin/activate"

# Set PYTHONPATH to project root and start the server
export PYTHONPATH="$PROJECT_ROOT"
python -m uvicorn db.main:app --reload --host 0.0.0.0 --port 8000
