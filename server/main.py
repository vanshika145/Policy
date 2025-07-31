from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from datetime import datetime
from typing import List
import tempfile
import httpx
import uuid # Added for Pinecone namespace
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Try to import optional dependencies
try:
    from sqlalchemy.orm import Session
    from database import get_db, engine
    from models import Base, User
    from schemas import UploadResponse, UserInfoResponse, UploadedFile as UploadedFileSchema
    from crud import get_or_create_user, create_uploaded_file, get_user_by_firebase_uid
    from models import UploadedFile
    from firebase_auth import get_firebase_uid, get_user_info_from_token
    from routes.embeddings import router as embeddings_router
    from utils.embeddings_utils import get_embeddings_manager
    HAS_FULL_DEPS = True
except ImportError:
    HAS_FULL_DEPS = False
    print("Warning: Some dependencies not available, using minimal mode")

from pydantic import BaseModel

# Add LangChain imports for RetrievalQA
try:
    from langchain.chains import RetrievalQA
    from langchain_community.vectorstores import Pinecone
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import HuggingFaceEmbeddings
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False
    print("Warning: LangChain not available")

# Create database tables (only if database is available)
if HAS_FULL_DEPS:
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("   The API will work for authentication but file uploads will be limited")
        print("   Install PostgreSQL to enable full functionality")
else:
    print("⚠️  Running in minimal mode without database")

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

# Allowed file types (PDF only for conservative deployment)
ALLOWED_EXTENSIONS = {".pdf"}
ALLOWED_MIME_TYPES = {
    "application/pdf"
}

HACKRX_TOKEN = os.getenv("HACKRX_TOKEN", "my_hackrx_token")  # Get from environment

# Remove the duplicate call_llm function since it's now in embeddings_utils.py

class HackrxRunRequest(BaseModel):
    documents: str
    questions: List[str]

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

    # Save to a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_pdf_path = tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to save PDF: {e}")

    # For now, just return a simple response
    # In a full implementation, you would process the PDF and answer questions
    return {
        "status": "success",
        "message": "PDF downloaded successfully",
        "questions": body.questions,
        "answers": [f"Answer to: {q}" for q in body.questions]
    }

@app.get("/")
async def root():
    return {"message": "Policy Analysis API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/hackrx/run-simple")
async def hackrx_run_simple(
    request: dict
):
    return {
        "status": "success",
        "message": "Simple webhook endpoint working",
        "data": request
    }

def validate_file(file: UploadFile) -> tuple[str, str]:
    """Validate uploaded file and return file type and extension"""
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"MIME type not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Map extension to file type for database
    file_type_map = {
        ".pdf": "pdf"
    }
    
    return file_type_map[file_extension], file_extension

@app.get("/me", response_model=UserInfoResponse)
async def get_current_user(
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    user = get_user_by_firebase_uid(db, firebase_uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfoResponse(
        firebase_uid=user.firebase_uid,
        email=user.email,
        display_name=user.display_name,
        created_at=user.created_at
    )

@app.post("/upload-simple-v2")
async def upload_file_simple_v2(
    file: UploadFile = File(...)
):
    """Simplified upload endpoint that works without database dependencies"""
    
    # Validate file
    file_type, file_extension = validate_file(file)
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"upload_{timestamp}{file_extension}"
        file_path = os.path.join(UPLOADS_DIR, safe_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Try to generate embeddings (optional)
        try:
            embeddings_manager = get_embeddings_manager()
            embeddings_result = await embeddings_manager.store_embeddings(
                file_path=file_path,
                user_id="test_user",
                filename=file.filename,
                user_email="test@example.com"
            )
            
            if embeddings_result["success"]:
                return {
                    "success": True,
                    "message": "File uploaded and processed successfully",
                    "filename": file.filename,
                    "file_path": file_path,
                    "file_type": file_type,
                    "chunks": embeddings_result["chunks_count"],
                    "status": "success"
                }
            else:
                return {
                    "success": True,
                    "message": "File uploaded but embeddings failed",
                    "filename": file.filename,
                    "file_path": file_path,
                    "file_type": file_type,
                    "chunks": 0,
                    "status": "success",
                    "embedding_error": embeddings_result["message"]
                }
                
        except Exception as embedding_error:
            print(f"⚠️  Embedding error: {embedding_error}")
            return {
                "success": True,
                "message": "File uploaded successfully (embeddings failed)",
                "filename": file.filename,
                "file_path": file_path,
                "file_type": file_type,
                "chunks": 0,
                "status": "success",
                "embedding_error": str(embedding_error)
            }
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):
    """Upload a file (PDF, DOCX, DOC, or EML) - Simplified version without database dependencies"""
    
    # Validate file
    file_type, file_extension = validate_file(file)
    
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"upload_{timestamp}{file_extension}"
        file_path = os.path.join(UPLOADS_DIR, safe_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Try to generate embeddings (optional)
        try:
            embeddings_manager = get_embeddings_manager()
            embeddings_result = await embeddings_manager.store_embeddings(
                file_path=file_path,
                user_id="upload_user",
                filename=file.filename,
                user_email="upload@example.com"
            )
            
            if embeddings_result["success"]:
                return {
                    "filename": file.filename,
                    "number_of_chunks": embeddings_result["chunks_count"],
                    "status": "success",
                    "message": embeddings_result["message"]
                }
            else:
                return {
                    "filename": file.filename,
                    "number_of_chunks": 0,
                    "status": "success",
                    "message": "File uploaded but embeddings generation failed",
                    "embedding_error": embeddings_result["message"]
                }
                
        except Exception as embedding_error:
            print(f"⚠️  Embedding error: {embedding_error}")
            return {
                "filename": file.filename,
                "number_of_chunks": 0,
                "status": "success",
                "message": "File uploaded successfully (embeddings failed)",
                "embedding_error": str(embedding_error)
            }
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/files", response_model=List[UploadedFileSchema])
async def get_user_files(
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """Get all files uploaded by the current user"""
    try:
        user = get_user_by_firebase_uid(db, firebase_uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        files = db.query(UploadedFile).filter(UploadedFile.user_id == user.id).all()
        return [UploadedFileSchema.from_orm(file) for file in files]
    except Exception as e:
        # For testing purposes, return empty list if authentication fails
        print(f"Authentication failed for /files: {e}")
        return []

# Include embeddings router
app.include_router(embeddings_router)

# Add query request model
class QueryRequest(BaseModel):
    query: str
    k: int = 5  # Number of results to return

@app.post("/query")
async def query_documents(
    request: QueryRequest,
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """
    Query uploaded documents using semantic search and generate intelligent answers.
    
    Args:
        request: QueryRequest with search query and number of results
        firebase_uid: User's Firebase UID (from auth)
        db: Database session
        
    Returns:
        Intelligent answer with source justification
    """
    try:
        # Get the user
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get embeddings manager
        from utils.embeddings_utils import get_embeddings_manager
        embeddings_manager = get_embeddings_manager()
        
        if embeddings_manager.embeddings is None:
            raise HTTPException(status_code=500, detail="No embeddings model available")
        
        # First try: Search for similar documents with user filter
        results = embeddings_manager.search_similar(
            query=request.query,
            user_id=firebase_uid,
            k=request.k
        )
        
        # If no results found, try without user filter (for debugging)
        if not results:
            print(f"⚠️  No results found for user {firebase_uid}, trying without user filter...")
            # Search without user filter to see if documents exist
            results = embeddings_manager.search_similar(
                query=request.query,
                user_id="",  # Empty string to bypass user filter
                k=request.k
            )
            if results:
                print(f"✅ Found {len(results)} results without user filter")
        
        if not results:
            return {
                "success": True,
                "query": request.query,
                "answer": "No relevant information found in your documents.",
                "sources": [],
                "count": 0,
                "user_id": firebase_uid,
                "debug_info": {
                    "user_found": user is not None,
                    "user_email": user.email if user else None
                }
            }
        
        # Extract context from search results
        context_chunks = []
        similarity_scores = []
        sources = []
        
        for result in results:
            context_chunks.append(result.get("content", ""))
            similarity_scores.append(result.get("score", 0))
            sources.append({
                "filename": result.get("metadata", {}).get("filename", "Unknown"),
                "upload_date": result.get("metadata", {}).get("upload_date", ""),
                "score": result.get("score", 0)
            })
        
        # Generate intelligent answer using LLM
        from utils.embeddings_utils import call_llm
        answer = call_llm(request.query, context_chunks, similarity_scores)
        
        return {
            "success": True,
            "query": request.query,
            "answer": answer,
            "sources": sources,
            "count": len(results),
            "user_id": firebase_uid,
            "debug_info": {
                "user_found": user is not None,
                "user_email": user.email if user else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# Add a simple query endpoint without authentication for testing
@app.post("/query-simple")
async def query_documents_simple(
    request: QueryRequest
):
    """
    Simple query endpoint without authentication for testing.
    """
    try:
        # Get embeddings manager
        from utils.embeddings_utils import get_embeddings_manager
        embeddings_manager = get_embeddings_manager()
        
        if embeddings_manager.embeddings is None:
            raise HTTPException(status_code=500, detail="No embeddings model available")
        
        # Search for similar documents (without user filter)
        results = embeddings_manager.search_similar(
            query=request.query,
            user_id="test_user",  # Use test user ID
            k=request.k
        )
        
        if not results:
            return {
                "success": True,
                "query": request.query,
                "answer": "No relevant information found in your documents.",
                "sources": [],
                "count": 0
            }
        
        # Extract context from search results
        context_chunks = []
        similarity_scores = []
        sources = []
        
        for result in results:
            context_chunks.append(result.get("content", ""))
            similarity_scores.append(result.get("score", 0))
            sources.append({
                "filename": result.get("metadata", {}).get("filename", "Unknown"),
                "upload_date": result.get("metadata", {}).get("upload_date", ""),
                "score": result.get("score", 0)
            })
        
        # Generate answer using LLM
        from utils.embeddings_utils import call_llm
        answer = call_llm(request.query, context_chunks, similarity_scores)
        
        return {
            "success": True,
            "query": request.query,
            "answer": answer,
            "sources": sources,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# Add a debug endpoint to check Pinecone contents
@app.get("/debug/pinecone")
async def debug_pinecone():
    """
    Debug endpoint to check what's stored in Pinecone.
    """
    try:
        from utils.embeddings_utils import get_embeddings_manager
        embeddings_manager = get_embeddings_manager()
        
        if not embeddings_manager.pinecone_index:
            return {"error": "Pinecone not configured"}
        
        # Query all vectors (no filter)
        results = embeddings_manager.pinecone_index.query(
            vector=[0.1] * 1024,  # Dummy vector
            top_k=100,
            include_metadata=True
        )
        
        # Format results
        documents = []
        for match in results.matches:
            documents.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            })
        
        return {
            "success": True,
            "total_vectors": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        return {"error": f"Debug failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 