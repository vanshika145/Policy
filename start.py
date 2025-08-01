#!/usr/bin/env python3
"""
Simple startup script for Railway deployment
"""

import os
import sys

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

try:
    from main import app
    print("Successfully imported FastAPI app")
    
    # Get port from environment
    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on port {port}")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=port)
    
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Startup error: {e}")
    sys.exit(1) 