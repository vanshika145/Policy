#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting build process..."

echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "Installing Rust locally in project directory..."
curl https://sh.rustup.rs -sSf | sh -s -- -y --no-modify-path --default-toolchain stable --profile minimal --target-dir=./rust-target

echo "Setting Rust environment variables..."
export CARGO_HOME=$PWD/.cargo
export RUSTUP_HOME=$PWD/.rustup
export PATH="$CARGO_HOME/bin:$PATH"

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