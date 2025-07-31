#!/usr/bin/env bash
# Simple build script for Render deployment

set -e  # Exit on any error

echo "Starting simple build process..."

echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "Installing minimal requirements..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 httpx>=0.24.0

echo "Creating uploads directory..."
mkdir -p uploads

echo "Checking Python version..."
python --version

echo "Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "Simple build completed successfully!" 