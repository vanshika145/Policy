#!/usr/bin/env python3
"""
Simple startup script for Render deployment
"""

import os
import sys

# Add server directory to path
server_dir = os.path.join(os.path.dirname(__file__), 'server')
sys.path.insert(0, server_dir)

# Import the FastAPI app
from server.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting server on port {port}")
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