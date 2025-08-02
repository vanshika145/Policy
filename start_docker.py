#!/usr/bin/env python3
"""
Docker startup script for Render deployment
"""

import os
import sys

# In Docker, the working directory is /app
# The server directory is at /app/server
server_dir = os.path.join(os.getcwd(), 'server')
sys.path.insert(0, server_dir)

# Import the FastAPI app
from main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🐳 Starting Docker server on port {port}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        timeout_keep_alive=30,
        timeout_graceful_shutdown=10,
        log_level="info"
    ) 