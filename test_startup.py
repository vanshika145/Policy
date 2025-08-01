#!/usr/bin/env python3
"""
Test script to verify the FastAPI app starts correctly
"""

import sys
import os

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

try:
    from main import app
    print("✅ Successfully imported FastAPI app")
    
    # Test if the app has the health endpoint
    routes = [route.path for route in app.routes]
    if "/health" in routes:
        print("✅ Health endpoint found")
    else:
        print("❌ Health endpoint not found")
        print(f"Available routes: {routes}")
        
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("✅ App is ready to start!") 