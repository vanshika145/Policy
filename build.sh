#!/usr/bin/env bash
# Simple build script for Render deployment

set -e  # Exit on any error

echo "Starting Render build process..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Installing dependencies from requirements.txt..."
pip install -r server/requirements.txt

echo "3. Creating uploads directory..."
mkdir -p server/uploads

echo "4. Checking Python version..."
python --version

echo "5. Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "6. Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "7. Checking if main can be imported..."
python -c "import server.main; print('main.py imported successfully')"

echo "Build completed successfully!" 