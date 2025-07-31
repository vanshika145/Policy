#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating uploads directory..."
mkdir -p uploads

echo "Build completed successfully!" 