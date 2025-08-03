from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from datetime import datetime
from typing import List
import tempfile
import httpx
import uuid
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import schemas first (always available)
from schemas import UserInfoResponse

# Try to import optional dependencies
try:
    from sqlalchemy.orm import Session
    from database import get_db, engine
    from models import Base, User
    from schemas import UploadResponse, UploadedFile as UploadedFileSchema
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

# Create database tables (only if database is available)
if HAS_FULL_DEPS:
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("   The API will work for authentication but file uploads will be limited")
        print("   Install PostgreSQL to enable full functionality")
else:
    print("Running in minimal mode without database")

app = FastAPI(
    title="Policy Analysis API", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

HACKRX_TOKEN = os.getenv("HACKRX_TOKEN", "my_hackrx_token")

class HackrxRunRequest(BaseModel):
    documents: str
    questions: List[str]

@app.post("/hackrx/run")
async def hackrx_run(
    request: Request,
    body: HackrxRunRequest
):
    """
    Main endpoint for processing PDF documents and answering questions.
    Downloads PDF from URL, extracts text, creates embeddings, and generates answers.
    """
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

    # Extract text from PDF using PyPDF2
    extracted_text = None
    extraction_error = None
    try:
        from PyPDF2 import PdfReader
        with open(tmp_pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"
    except Exception as e:
        extraction_error = str(e)

    # Clean up temp file
    try:
        os.remove(tmp_pdf_path)
    except Exception:
        pass

    if not extracted_text or extraction_error:
        raise HTTPException(status_code=400, detail=f"PDF extraction failed: {extraction_error or 'No text found'}")

    # Process text and create embeddings
    try:
        from pinecone import Pinecone
        
        # Simple text splitting
        chunk_size = 1000
        chunks = []
        for i in range(0, len(extracted_text), chunk_size):
            chunk = extracted_text[i:i + chunk_size]
            chunks.append(chunk)
        
        print(f"📄 Created {len(chunks)} chunks from text")

        # Use OpenAI embeddings
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Generate embeddings for each chunk
            texts = chunks
            vectors = []
            
            for text in texts:
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=text
                )
                embedding = response.data[0].embedding
                
                # Pad embeddings to match Pinecone index dimension (1024)
                if len(embedding) == 1536:  # OpenAI embeddings
                    embedding = embedding[:1024]
                elif len(embedding) != 1024:
                    embedding = embedding + [0.0] * (1024 - len(embedding))
                
                vectors.append(embedding)
            
            print(f"✅ Generated {len(vectors)} embeddings using OpenAI")
            
        except Exception as e:
            print(f"❌ OpenAI embeddings failed: {e}")
            # Create simple dummy embeddings
            vectors = [[0.1] * 1024 for _ in chunks]
            print(f"⚠️  Using dummy embeddings")

        # Pinecone setup
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX", "policy-document")
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Check if index exists
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
        except Exception as e:
            print(f"❌ Error upserting vectors: {e}")
        
        num_chunks = len(chunks)
        
        # Answer questions using similarity search
        answers = []
        if len(body.questions) > 0:
            try:
                print(f"🔍 Answering {len(body.questions)} questions...")
                
                # Answer each question using direct Pinecone query
                for question in body.questions:
                    try:
                        print(f"🤔 Processing question: {question}")
                        
                        # Generate embedding for the question
                        response = client.embeddings.create(
                            model="text-embedding-ada-002",
                            input=question
                        )
                        question_embedding = response.data[0].embedding
                        
                        # Pad embeddings to match Pinecone dimension (1024)
                        if len(question_embedding) == 1536:  # OpenAI embeddings
                            question_embedding = question_embedding[:1024]
                        elif len(question_embedding) != 1024:
                            question_embedding = question_embedding + [0.0] * (1024 - len(question_embedding))
                        
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
                            
                            # Use OpenRouter for LLM
                            try:
                                from openai import OpenAI
                                openrouter_client = OpenAI(
                                    base_url="https://openrouter.ai/api/v1",
                                    api_key=os.getenv("OPENROUTER_API_KEY")
                                )
                                
                                # Create context for LLM
                                context = "\n\n".join(context_chunks[:3])
                                
                                response = openrouter_client.chat.completions.create(
                                    model="mistralai/mistral-7b-instruct",
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a helpful assistant that answers questions based on the provided context. Provide clear, accurate answers using only the information from the context. If the context doesn't contain enough information, say so."
                                        },
                                        {
                                            "role": "user",
                                            "content": f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
                                        }
                                    ],
                                    max_tokens=500,
                                    temperature=0.1
                                )
                                
                                answer = response.choices[0].message.content.strip()
                                
                            except Exception as e:
                                print(f"❌ LLM call failed: {e}")
                                answer = f"Based on the document: {' '.join(context_chunks[:2])}"
                            
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

@app.get("/")
async def root():
    return {"message": "Policy Analysis API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for quick health checks"""
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 