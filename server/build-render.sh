#!/usr/bin/env bash
# Simple build script for Render deployment

echo "Starting Render build process..."

echo "1. Upgrading pip..."
pip install --upgrade pip

echo "2. Installing minimal requirements..."
pip install -r requirements-render.txt

echo "3. Creating uploads directory..."
mkdir -p uploads

echo "4. Checking Python version..."
python --version

echo "5. Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "6. Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "7. Checking if main-minimal can be imported..."
python -c "import main_minimal; print('main-minimal imported successfully')"

echo "Build completed successfully!" 