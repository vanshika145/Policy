#!/usr/bin/env bash
# Build script for Render Docker deployment

set -e  # Exit on any error

echo "Starting Docker build for Render..."

echo "1. Checking if we're in a Docker environment..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
else
    echo "❌ Docker not available, using standard build"
    echo "2. Installing dependencies with pip..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements-render.txt
    echo "3. Creating uploads directory..."
    mkdir -p uploads
    echo "4. Build completed successfully!"
    exit 0
fi

echo "2. Building Docker image..."
docker build -t policy-api .

echo "3. Build completed successfully!" 