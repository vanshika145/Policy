#!/usr/bin/env bash
# Start script for Render deployment

echo "Starting Policy Analysis API..."

# Check if we're in the right directory
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

# Check if server directory exists
if [ -d "server" ]; then
    echo "✅ Server directory found"
    cd server
    echo "Changed to server directory: $(pwd)"
else
    echo "❌ Server directory not found"
    exit 1
fi

# Check if main.py exists
if [ -f "main.py" ]; then
    echo "✅ main.py found"
else
    echo "❌ main.py not found"
    exit 1
fi

# Go back to root
cd ..

# Start the application
echo "Starting uvicorn server..."
python -m uvicorn server.main:app --host 0.0.0.0 --port $PORT 