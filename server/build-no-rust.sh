#!/usr/bin/env bash
# Build script for Render deployment - No Rust compilation

set -e  # Exit on any error

echo "Starting build process (No Rust compilation)..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Installing all necessary dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 httpx>=0.24.0 sqlalchemy==2.0.23 pydantic[email]==2.5.0 firebase-admin==6.2.0

echo "3. Creating uploads directory..."
mkdir -p uploads

echo "4. Checking Python version..."
python --version

echo "5. Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "6. Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "7. Checking if sqlalchemy can be imported..."
python -c "import sqlalchemy; print('SQLAlchemy imported successfully')"

echo "Build completed successfully (No Rust dependencies)!" 