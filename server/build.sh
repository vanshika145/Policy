#!/usr/bin/env bash
# Build script for Render deployment

set -e  # Exit on any error

echo "Starting build process..."

echo "1. Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "2. Installing Rust locally in project directory..."
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path --default-toolchain stable --profile minimal

echo "3. Setting Rust environment variables..."
export CARGO_HOME=$PWD/.cargo
export RUSTUP_HOME=$PWD/.rustup
export PATH="$CARGO_HOME/bin:$PATH"

echo "4. Verifying Rust installation..."
rustc --version
cargo --version

echo "5. Updating Rust toolchain..."
rustup update

echo "6. Installing dependencies with improved strategies..."
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

echo "7. Creating uploads directory..."
mkdir -p uploads

echo "8. Checking Python version..."
python --version

echo "9. Checking if FastAPI can be imported..."
if python -c "import fastapi; print('FastAPI imported successfully')"; then
    echo "✅ FastAPI import successful"
else
    echo "❌ FastAPI import failed"
    exit 1
fi

echo "10. Checking if uvicorn can be imported..."
if python -c "import uvicorn; print('Uvicorn imported successfully')"; then
    echo "✅ Uvicorn import successful"
else
    echo "❌ Uvicorn import failed"
    exit 1
fi

echo "Build completed successfully!" 