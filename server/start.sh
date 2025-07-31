#!/usr/bin/env bash
# Start script for Render deployment

echo "Starting Policy Analysis API..."

# Check if we're in a Docker environment
if command -v docker &> /dev/null; then
    echo "Running with Docker..."
    docker run -p $PORT:8000 policy-api
else
    echo "Running with Python directly..."
    uvicorn main-minimal:app --host 0.0.0.0 --port $PORT
fi 