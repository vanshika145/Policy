#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating uploads directory..."
mkdir -p uploads

echo "Checking Python version..."
python --version

echo "Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "Build completed successfully!" 