#!/usr/bin/env bash
# Optimized build script for Render deployment

set -e  # Exit on any error

echo "Starting optimized Render build process..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Installing Rust for compiled packages..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="$HOME/.cargo/bin:$PATH"

echo "3. Installing all dependencies..."
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 httpx>=0.24.0 pydantic[email]==2.5.0 sqlalchemy==2.0.23 firebase-admin==6.2.0 langchain==0.3.27 langchain-openai==0.3.28 langchain-community==0.3.27 openai>=1.10.0 pinecone==7.3.0 PyPDF2==3.0.1 sentence-transformers==2.2.2 unstructured==0.11.8 transformers>=4.41.0 torch>=1.11.0 scikit-learn>=1.2.0 huggingface-hub>=0.20.0

echo "4. Creating uploads directory..."
mkdir -p uploads

echo "5. Checking Python version..."
python --version

echo "6. Checking if FastAPI can be imported..."
python -c "import fastapi; print('FastAPI imported successfully')"

echo "7. Checking if uvicorn can be imported..."
python -c "import uvicorn; print('Uvicorn imported successfully')"

echo "8. Checking if main can be imported..."
python -c "import server.main; print('main.py imported successfully')"

echo "Build completed successfully!" 