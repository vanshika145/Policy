# Import the FastAPI app from server module
import sys
import os

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

try:
    from main import app
except ImportError:
    # Fallback: try direct import
    from server.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 