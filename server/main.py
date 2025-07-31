from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
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

from database import get_db, engine
from models import Base, User
from schemas import UploadResponse, UserInfoResponse, UploadedFile as UploadedFileSchema
from crud import get_or_create_user, create_uploaded_file, get_user_by_firebase_uid
from models import UploadedFile
from firebase_auth import get_firebase_uid, get_user_info_from_token
from routes.embeddings import router as embeddings_router
from utils.embeddings_utils import get_embeddings_manager
from pydantic import BaseModel

# Try to import optional dependencies
try:
    from utils.embeddings_utils import EmbeddingsManager
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    print("Warning: Embeddings functionality not available")

# Add LangChain imports for RetrievalQA
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Pinecone

from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Create database tables (only if database is available)
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"⚠️  Database connection failed: {e}")
    print("   The API will work for authentication but file uploads will be limited")
    print("   Install PostgreSQL to enable full functionality")

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

    # Extract text from PDF
    extracted_text = None
    extraction_error = None
    try:
        try:
            import fitz  # PyMuPDF
            with fitz.open(tmp_pdf_path) as doc:
                extracted_text = "\n".join(page.get_text() for page in doc)
        except ImportError:
            from pdfminer.high_level import extract_text
            extracted_text = extract_text(tmp_pdf_path)
    except Exception as e:
        extraction_error = str(e)

    # Clean up temp file
    try:
        import os
        os.remove(tmp_pdf_path)
    except Exception:
        pass

    if not extracted_text or extraction_error:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {extraction_error or 'No text found'}")

    # --- Simplified: Process text and create embeddings ---
    try:
        import os
        from pinecone import Pinecone

        # Simple text splitting (no LangChain dependency)
        chunk_size = 1000
        chunks = []
        for i in range(0, len(extracted_text), chunk_size):
            chunk = extracted_text[i:i + chunk_size]
            chunks.append(chunk)
        
        print(f"📄 Created {len(chunks)} chunks from text")
        print(f"📝 First chunk preview: {chunks[0][:100]}...")

        # Use the improved embeddings manager with automatic fallback
        from utils.embeddings_utils import get_embeddings_manager
        
        embeddings_manager = get_embeddings_manager()
        if embeddings_manager.embeddings is None:
            raise HTTPException(status_code=400, detail="No embeddings model available")
        
        # Generate embeddings for each chunk with proper dimension handling
        texts = chunks
        vectors = []
        
        for text in texts:
            if hasattr(embeddings_manager.embeddings, 'embed_query'):
                # OpenAI or HuggingFace embeddings
                embedding = embeddings_manager.embeddings.embed_query(text)
            else:
                # Fallback for sentence-transformers
                embedding = embeddings_manager.embeddings.encode(text).tolist()
            
            # Pad embeddings to match Pinecone index dimension (1024)
            original_dim = len(embedding)
            if original_dim == 1536:  # OpenAI embeddings
                print(f"Padding OpenAI embeddings from 1536 to 1024 dimensions...")
                embedding = embedding[:1024]
            elif original_dim == 384:  # HuggingFace embeddings
                print(f"Padding HuggingFace embeddings from 384 to 1024 dimensions...")
                embedding = embedding + [0.0] * (1024 - original_dim)
            elif original_dim != 1024:
                print(f"Padding embeddings from {original_dim} to 1024 dimensions...")
                embedding = embedding + [0.0] * (1024 - original_dim)
            
            vectors.append(embedding)
        
        print(f"📊 Processing {len(texts)} texts for embeddings")
        print(f"📏 Final embedding dimension: {len(vectors[0])}")

        # Pinecone setup
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX", "policy-document")
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Check if index exists (simplified)
        try:
            index = pc.Index(pinecone_index_name)
            print(f"✅ Connected to Pinecone index: {pinecone_index_name}")
        except Exception as e:
            raise Exception(f"Pinecone index '{pinecone_index_name}' does not exist or is not accessible: {e}")

        # Use a unique namespace for this request
        namespace = f"hackrx-{uuid.uuid4().hex[:8]}"
        # Upsert vectors
        pinecone_vectors = []
        for i, vec in enumerate(vectors):
            pinecone_vectors.append({
                "id": f"chunk-{i}",
                "values": vec,
                "metadata": {"text": texts[i]}
            })
        
        try:
            print(f"Upserting {len(pinecone_vectors)} vectors to namespace: {namespace}")
            index.upsert(vectors=pinecone_vectors, namespace=namespace)
            print(f"✅ Successfully upserted vectors to namespace: {namespace}")
            
            # Verify the vectors were stored
            print(f"🔍 Verifying vectors in namespace: {namespace}")
            verify_response = index.query(
                vector=[0.1] * 1024,
                top_k=5,
                namespace=namespace,
                include_metadata=True
            )
            print(f"✅ Found {len(verify_response.matches)} vectors in namespace after upsert")
            
        except Exception as e:
            print(f"❌ Error upserting vectors: {e}")
            # Continue without failing the entire request
        
        num_chunks = len(chunks)
        
        # Step 3: Answer questions using simple similarity
        answers = []
        if len(body.questions) > 0:
            try:
                print(f"🔍 Answering {len(body.questions)} questions...")
                
                # Answer each question using direct Pinecone query
                for question in body.questions:
                    try:
                        print(f"🤔 Processing question: {question}")
                        
                        # Generate embedding for the question
                        if hasattr(embeddings_manager.embeddings, 'embed_query'):
                            question_embedding = embeddings_manager.embeddings.embed_query(question)
                        else:
                            question_embedding = embeddings_manager.embeddings.encode(question).tolist()
                        
                        # Pad embeddings to match Pinecone dimension (1024)
                        original_dim = len(question_embedding)
                        if original_dim == 1536:  # OpenAI embeddings
                            question_embedding = question_embedding[:1024]
                        elif original_dim == 384:  # HuggingFace embeddings
                            question_embedding = question_embedding + [0.0] * (1024 - original_dim)
                        elif original_dim != 1024:
                            question_embedding = question_embedding + [0.0] * (1024 - original_dim)
                        
                        print(f"📏 Question embedding dimension: {len(question_embedding)}")
                        
                        # Query Pinecone directly
                        query_response = index.query(
                            vector=question_embedding,
                            top_k=3,
                            namespace=namespace,
                            include_metadata=True
                        )
                        
                        print(f"🔍 Found {len(query_response.matches)} matches for question")
                        
                        if query_response.matches:
                            # Extract context chunks and similarity scores
                            context_chunks = []
                            similarity_scores = []
                            
                            for match in query_response.matches:
                                context_chunks.append(match.metadata.get('text', ''))
                                similarity_scores.append(match.score)
                            
                            # Call LLM to generate final answer
                            print(f"🤖 Calling LLM for question: {question}")
                            from utils.embeddings_utils import call_llm
                            answer = call_llm(question, context_chunks, similarity_scores)
                            
                            # Keep source documents for reference
                            source_docs = [match.metadata.get('text', '')[:100] + "..." for match in query_response.matches[:2]]
                        else:
                            answer = "No relevant information found in the document."
                            source_docs = []
                        
                        answers.append({
                            "question": question,
                            "answer": answer,
                            "source_documents": source_docs
                        })
                        
                        print(f"✅ Answered question: {answer[:50]}...")
                        
                    except Exception as e:
                        print(f"❌ Error answering question '{question}': {e}")
                        answers.append({
                            "question": question,
                            "answer": f"Unable to process question: {str(e)}",
                            "source_documents": []
                        })
                
                print(f"✅ Successfully answered {len(answers)} questions")
                
            except Exception as e:
                print(f"❌ Error in question answering: {e}")
                # Create fallback answers
                for question in body.questions:
                    answers.append({
                        "question": question,
                        "answer": "Unable to process question due to technical issues.",
                        "source_documents": []
                    })
        else:
            # No questions
            answers = []
            
    except Exception as e:
        import traceback
        error_msg = f"Processing failed: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=error_msg)

    return {
        "message": "Authorized and processed",
        "documents": body.documents,
        "questions": body.questions,
        "num_chunks": num_chunks,
        "pinecone_namespace": namespace,
        "extracted_text_preview": extracted_text[:500],
        "answers": answers
    }

# Remove the first duplicate endpoint (lines 175-427)
# Keep only the webhook-ready version

@app.post("/hackrx/run")
async def hackrx_webhook_endpoint(
    request: dict,
    firebase_uid: str = Depends(get_firebase_uid),
    db: Session = Depends(get_db)
):
    """
    Simplified webhook endpoint for HackRx submissions.
    
    Expected request format:
    {
        "documents": "document_url_or_filename",
        "questions": ["question1", "question2", ...]
    }
    
    Returns:
    {
        "answers": ["answer1", "answer2", ...]
    }
    """
    try:
        # Get the user
        user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate request - only documents and questions allowed
        allowed_fields = {"documents", "questions"}
        if not all(field in allowed_fields for field in request.keys()):
            raise HTTPException(status_code=400, detail="Only 'documents' and 'questions' fields are allowed")
        
        if "questions" not in request:
            raise HTTPException(status_code=400, detail="Questions array is required")
        
        questions = request["questions"]
        if not isinstance(questions, list) or len(questions) == 0:
            raise HTTPException(status_code=400, detail="Questions must be a non-empty array")
        
        # Get embeddings manager
        from utils.embeddings_utils import get_embeddings_manager
        embeddings_manager = get_embeddings_manager()
        
        if embeddings_manager.embeddings is None:
            raise HTTPException(status_code=500, detail="No embeddings model available")
        
        answers = []
        
        # Process each question
        for i, question in enumerate(questions):
            try:
                print(f"🔍 Processing question {i+1}/{len(questions)}: {question}")
                
                # Search for relevant documents
                current_document = request.get("documents", "").split("/")[-1]  # Extract filename
                results = embeddings_manager.search_similar(
                    query=question,
                    user_id=firebase_uid,
                    k=20,  # Get more results for better context
                    document_filter=current_document
                )
                
                # If no results found, try without user filter but keep document filter
                if not results:
                    print(f"⚠️  No results found for user {firebase_uid}, trying without user filter...")
                    results = embeddings_manager.search_similar(
                        query=question,
                        user_id="",  # Empty string to bypass user filter
                        k=10,
                        document_filter=current_document
                    )
                
                if not results:
                    answers.append(f"No relevant information found in the document '{current_document}'.")
                    continue
                
                # Filter and rank results by relevance
                high_quality_results = []
                for result in results:
                    score = result.get("score", 0)
                    content = result.get("content", "")
                    
                    # Only include results with reasonable similarity
                    if score > 0.1:  # Lower similarity threshold for better coverage
                        high_quality_results.append(result)
                
                if not high_quality_results:
                    answers.append(f"No relevant information found in the document '{current_document}'.")
                    continue
                
                # Extract context from high-quality results
                context_chunks = []
                similarity_scores = []
                
                for result in high_quality_results:
                    context_chunks.append(result.get("content", ""))
                    similarity_scores.append(result.get("score", 0))
                
                # Generate answer using LLM
                from utils.embeddings_utils import call_llm
                answer = call_llm(question, context_chunks, similarity_scores)
                
                answers.append(answer)
                
            except Exception as e:
                print(f"❌ Error processing question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
        
        return answers
        
    except Exception as e:
        print(f"❌ Error in hackrx_webhook_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add simple batch query endpoint without authentication for testing
@app.post("/hackrx/run-simple")
async def batch_query_documents_simple(
    request: dict
):
    """
    Simple batch query endpoint without authentication for testing.
    
    Expected request format:
    {
        "documents": "document_url_or_filename",
        "questions": ["question1", "question2", ...]
    }
    
    Returns:
    {
        "answers": ["answer1", "answer2", ...]
    }
    """
    try:
        # Validate request - only documents and questions allowed
        allowed_fields = {"documents", "questions"}
        if not all(field in allowed_fields for field in request.keys()):
            raise HTTPException(status_code=400, detail="Only 'documents' and 'questions' fields are allowed")
        
        if "questions" not in request:
            raise HTTPException(status_code=400, detail="Questions array is required")
        
        questions = request["questions"]
        if not isinstance(questions, list) or len(questions) == 0:
            raise HTTPException(status_code=400, detail="Questions must be a non-empty array")
        
        # Get embeddings manager
        from utils.embeddings_utils import get_embeddings_manager
        embeddings_manager = get_embeddings_manager()
        
        if embeddings_manager.embeddings is None:
            raise HTTPException(status_code=500, detail="No embeddings model available")
        
        answers = []
        
        # Process each question
        for i, question in enumerate(questions):
            try:
                print(f"🔍 Processing question {i+1}/{len(questions)}: {question}")
                
                # Search for relevant documents (without user filter)
                current_document = request.get("documents", "").split("/")[-1]  # Extract filename
                results = embeddings_manager.search_similar(
                    query=question,
                    user_id="upload_user",  # Use upload_user to match stored documents
                    k=20,  # Get more results for better context
                    document_filter=current_document
                )
                
                if not results:
                    answers.append(f"No relevant information found in the document '{current_document}'.")
                    continue
                
                # Filter and rank results by relevance
                high_quality_results = []
                for result in results:
                    score = result.get("score", 0)
                    content = result.get("content", "")
                    
                    # Only include results with reasonable similarity
                    if score > 0.1:  # Lower similarity threshold for better coverage
                        high_quality_results.append(result)
                
                if not high_quality_results:
                    answers.append(f"No relevant information found in the document '{current_document}'.")
                    continue
                
                # Extract context from high-quality results
                context_chunks = []
                similarity_scores = []
                
                for result in high_quality_results:
                    context_chunks.append(result.get("content", ""))
                    similarity_scores.append(result.get("score", 0))
                
                # Generate answer using LLM
                from utils.embeddings_utils import call_llm
                answer = call_llm(question, context_chunks, similarity_scores)
                
                answers.append(answer)
                
            except Exception as e:
                print(f"❌ Error processing question {i+1}: {str(e)}")
                answers.append(f"Error processing question: {str(e)}")
        
        return answers
        
    except Exception as e:
        print(f"❌ Error in batch_query_documents_simple: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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

@app.get("/")
async def root():
    return {"message": "Policy Analysis API is running"}

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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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