#!/usr/bin/env bash
# Simple build script for Render deployment

set -e  # Exit on any error

echo "Starting simple build process..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Installing minimal requirements..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 httpx>=0.24.0

echo "3. Creating uploads directory..."
mkdir -p uploads

echo "4. Checking Python version..."
python --version

echo "5. Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "6. Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "Simple build completed successfully!" 