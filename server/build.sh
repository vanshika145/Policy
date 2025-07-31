#!/usr/bin/env bash
# Build script for Render deployment

set -e  # Exit on any error

echo "Starting build process..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Checking existing Rust installation..."
if command -v rustc &> /dev/null; then
    echo "✅ Rust is already installed globally"
    echo "   Rust version: $(rustc --version)"
    echo "   Cargo version: $(cargo --version)"
else
    echo "❌ Rust not found, but skipping local installation due to filesystem constraints"
    echo "   Will proceed with pip installation only"
fi

echo "3. Setting up environment for compilation..."
# Use existing Rust installation if available
if command -v rustc &> /dev/null; then
    export CARGO_HOME=/tmp/.cargo
    export RUSTUP_HOME=/tmp/.rustup
    mkdir -p $CARGO_HOME $RUSTUP_HOME
    echo "✅ Using existing Rust installation with temporary directories"
else
    echo "⚠️  No Rust available, will try pip-only installation"
fi

echo "4. Installing dependencies with improved strategies..."
echo "   Trying full requirements with --no-use-pep517..."

if pip install --no-use-pep517 -r requirements.txt --verbose; then
    echo "✅ Full requirements installed successfully"
else
    echo "❌ Full requirements failed, trying conservative requirements..."
    if pip install --no-use-pep517 -r requirements-conservative.txt --verbose; then
        echo "✅ Conservative requirements installed successfully"
    else
        echo "❌ Conservative requirements failed, trying minimal requirements..."
        if pip install --no-use-pep517 -r requirements-minimal.txt --verbose; then
            echo "✅ Minimal requirements installed successfully"
        else
            echo "❌ All requirements failed!"
            echo "   Trying individual package installation..."
            pip install --no-use-pep517 fastapi==0.104.1 uvicorn[standard]==0.24.0 python-dotenv==1.0.0 httpx>=0.24.0
        fi
    fi
fi

echo "5. Creating uploads directory..."
mkdir -p uploads

echo "6. Checking Python version..."
python --version

echo "7. Checking if FastAPI can be imported..."
if python -c "import fastapi; print('FastAPI imported successfully')"; then
    echo "✅ FastAPI import successful"
else
    echo "❌ FastAPI import failed"
    exit 1
fi

echo "8. Checking if uvicorn can be imported..."
if python -c "import uvicorn; print('Uvicorn imported successfully')"; then
    echo "✅ Uvicorn import successful"
else
    echo "❌ Uvicorn import failed"
    exit 1
fi

echo "Build completed successfully!" 