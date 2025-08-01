#!/usr/bin/env bash
# Start script for Render deployment

echo "Starting Policy Analysis API..."

# Check if we're in a container environment
if [ -f /.dockerenv ]; then
    echo "Running in container environment..."
else
    echo "Running with Python directly..."
    uvicorn main-minimal:app --host 0.0.0.0 --port $PORT
fi 