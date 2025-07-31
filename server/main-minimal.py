from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
import logging
from datetime import datetime
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Policy Analysis API", version="1.0.0")

# CORS middleware - allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

HACKRX_TOKEN = os.getenv("HACKRX_TOKEN", "my_hackrx_token")  # Get from environment

class HackrxRunRequest(BaseModel):
    documents: str
    questions: List[str]

@app.get("/")
async def root():
    return {"message": "Policy Analysis API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/hackrx/run")
async def hackrx_run(
    request: Request,
    body: HackrxRunRequest = Body(...)
):
    # Validate Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header != f"Bearer {HACKRX_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Download the PDF
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(body.documents)
            if response.status_code != 200:
                raise Exception(f"Failed to download PDF: {response.status_code}")
            pdf_bytes = response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF download failed: {e}")

    # For now, just return a simple response
    # In a full implementation, you would process the PDF and answer questions
    return {
        "status": "success",
        "message": "PDF downloaded successfully",
        "questions": body.questions,
        "answers": [f"Answer to: {q}" for q in body.questions]
    }

@app.post("/hackrx/run-simple")
async def hackrx_run_simple(
    request: dict
):
    return {
        "status": "success",
        "message": "Simple webhook endpoint working",
        "data": request
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 