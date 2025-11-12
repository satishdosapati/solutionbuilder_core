#!/bin/bash
# Start script for AWS Solution Architect Tool Backend
# Using --no-reload to avoid Python 3.13 compatibility issues on Windows

echo "Starting AWS Solution Architect Tool Backend..."

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Start uvicorn without reload
uvicorn main:app --host 0.0.0.0 --port 8000 --no-reload

