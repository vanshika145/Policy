#!/usr/bin/env bash
# Build script for Render deployment

set -e  # Exit on any error

echo "Starting build process..."

echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "Installing Rust locally in project directory..."
curl https://sh.rustup.rs -sSf | sh -s -- -y --no-modify-path --default-toolchain stable --profile minimal --target-dir=./rust-target

echo "Setting Rust environment variables..."
export CARGO_HOME=$PWD/.cargo
export RUSTUP_HOME=$PWD/.rustup
export PATH="$CARGO_HOME/bin:$PATH"

echo "Verifying Rust installation..."
rustc --version
cargo --version

echo "Installing dependencies with verbose output..."
if pip install -r requirements.txt --verbose; then
    echo "✅ Full requirements installed successfully"
else
    echo "❌ Full requirements failed, trying conservative requirements..."
    if pip install -r requirements-conservative.txt --verbose; then
        echo "✅ Conservative requirements installed successfully"
    else
        echo "❌ Conservative requirements failed, trying minimal requirements..."
        if pip install -r requirements-minimal.txt --verbose; then
            echo "✅ Minimal requirements installed successfully"
        else
            echo "❌ All requirements failed!"
            exit 1
        fi
    fi
fi

echo "Creating uploads directory..."
mkdir -p uploads

echo "Checking Python version..."
python --version

echo "Checking if FastAPI can be imported..."
if python -c "import fastapi; print('FastAPI imported successfully')"; then
    echo "✅ FastAPI import successful"
else
    echo "❌ FastAPI import failed"
    exit 1
fi

echo "Checking if uvicorn can be imported..."
if python -c "import uvicorn; print('Uvicorn imported successfully')"; then
    echo "✅ Uvicorn import successful"
else
    echo "❌ Uvicorn import failed"
    exit 1
fi

echo "Build completed successfully!" 