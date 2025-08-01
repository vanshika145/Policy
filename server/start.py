import sys
import os

# Add 'server' directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

# Import FastAPI app
from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 