from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import os
from pathlib import Path

from database import get_db
from models import UploadedFile, User
from firebase_auth import get_firebase_uid
from utils.embeddings_utils import get_embeddings_manager
from schemas import EmbeddingsResponse, EmbeddingsStatus

router = APIRouter(prefix="/embeddings", tags=["embeddings"])

@router.post("/generate-embeddings", response_model=EmbeddingsResponse)
async def generate_embeddings(
    file_id: int,
    background_tasks: BackgroundTasks,
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """
    Generate embeddings for an uploaded file.
    
    Args:
        file_id: ID of the uploaded file to process
        background_tasks: FastAPI background tasks
        firebase_uid: User's Firebase UID (from auth)
        db: Database session
        
    Returns:
        EmbeddingsResponse with processing status
    """
    try:
        # Get the user
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get the uploaded file
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user.id
        ).first()
        
        if not uploaded_file:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        # Check if file exists
        file_path = Path(uploaded_file.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Check if file type is supported
        file_extension = file_path.suffix.lower()
        if file_extension not in ['.pdf', '.docx', '.doc']:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Only PDF and Word documents are supported."
            )
        
        # Get embeddings manager
        embeddings_manager = get_embeddings_manager()
        
        # Process embeddings in background
        background_tasks.add_task(
            process_embeddings_background,
            str(file_path),
            firebase_uid,
            file_id,
            db
        )
        
        return EmbeddingsResponse(
            success=True,
            message="Embeddings generation started in background",
            file_id=file_id,
            user_id=user.id,
            status=EmbeddingsStatus.PROCESSING
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start embeddings generation: {str(e)}")

async def process_embeddings_background(
    file_path: str,
    user_id: str,
    file_id: int,
    db: Session
):
    """
    Background task to process embeddings.
    
    Args:
        file_path: Path to the file to process
        user_id: User identifier
        file_id: File ID for status updates
        db: Database session
    """
    try:
        # Get embeddings manager
        embeddings_manager = get_embeddings_manager()
        
        # Get user info for metadata
        user = db.query(User).filter(User.firebase_uid == user_id).first()
        uploaded_file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
        
        if not user or not uploaded_file:
            print(f"❌ User or file not found for embeddings processing")
            return
        
        # Process embeddings
        result = await embeddings_manager.store_embeddings(
            file_path=file_path,
            user_id=user_id,
            filename=uploaded_file.filename,
            user_email=user.email
        )
        
        if result["success"]:
            print(f"✅ Embeddings generated successfully for file {file_id}: {result['chunks_count']} chunks")
        else:
            print(f"❌ Failed to generate embeddings for file {file_id}: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error in background embeddings processing for file {file_id}: {str(e)}")

@router.get("/status/{file_id}", response_model=EmbeddingsResponse)
async def get_embeddings_status(
    file_id: int,
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """
    Get the status of embeddings generation for a file.
    
    Args:
        file_id: ID of the uploaded file
        firebase_uid: User's Firebase UID (from auth)
        db: Database session
        
    Returns:
        EmbeddingsResponse with current status
    """
    try:
        # Get the user
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get the uploaded file
        uploaded_file = db.query(UploadedFile).filter(
            UploadedFile.id == file_id,
            UploadedFile.user_id == user.id
        ).first()
        
        if not uploaded_file:
            raise HTTPException(status_code=404, detail="File not found or access denied")
        
        # For now, we'll return a simple status
        # In a real implementation, you might want to track processing status in the database
        return EmbeddingsResponse(
            success=True,
            message="Embeddings status retrieved",
            file_id=file_id,
            user_id=user.id,
            status=EmbeddingsStatus.COMPLETED  # You could check actual status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get embeddings status: {str(e)}")

@router.get("/search", response_model=Dict[str, Any])
async def search_embeddings(
    query: str,
    k: int = 5,
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """
    Search through user's embedded documents.
    
    Args:
        query: Search query
        k: Number of results to return
        firebase_uid: User's Firebase UID (from auth)
        db: Database session
        
    Returns:
        Dictionary with search results
    """
    try:
        # Get embeddings manager
        embeddings_manager = get_embeddings_manager()
        
        # Search for similar documents
        results = embeddings_manager.search_similar(query, firebase_uid, k)
        
        # Format results
        formatted_results = []
        for doc in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, 'score', None)
            })
        
        return {
            "success": True,
            "query": query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")