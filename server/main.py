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
try:
    from schemas import UserInfoResponse
except ImportError:
    # Fallback for minimal mode
    class UserInfoResponse:
        pass

# Try to import optional dependencies
try:
    from sqlalchemy.orm import Session
    from database import get_db, engine
    from models import Base, User
    try:
        from schemas import UploadResponse, UploadedFile as UploadedFileSchema
    except ImportError:
        # Fallback for minimal mode
        class UploadResponse:
            pass
        class UploadedFileSchema:
            pass
    from crud import get_or_create_user, create_uploaded_file, get_user_by_firebase_uid
    from models import UploadedFile
    from firebase_auth import get_firebase_uid, get_user_info_from_token
    try:
        from routes.embeddings import router as embeddings_router
        from utils.embeddings_utils import get_embeddings_manager
        HAS_FULL_DEPS = True
    except ImportError:
        embeddings_router = None
        get_embeddings_manager = None
        HAS_FULL_DEPS = False
except ImportError:
    HAS_FULL_DEPS = False
    embeddings_router = None
    get_embeddings_manager = None
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

# Include embeddings router if available
if embeddings_router:
    app.include_router(embeddings_router)
    print("✅ Embeddings router included")
else:
    print("⚠️  Embeddings router not available")

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
    expected_auth = f"Bearer {HACKRX_TOKEN}"
    
    print(f"🔍 Debug - HACKRX_TOKEN from env: '{HACKRX_TOKEN}'")
    print(f"🔍 Debug - Expected auth: '{expected_auth}'")
    print(f"🔍 Debug - Received auth: '{auth_header}'")
    print(f"🔍 Debug - All headers: {dict(request.headers)}")
    
    if auth_header != expected_auth:
        print(f"⚠️  Authorization failed. Expected: '{expected_auth}', Got: '{auth_header}'")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    print(f"✅ Authorization successful!")

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
        
        # Improved text splitting with overlap to capture context better
        chunk_size = 800   # Smaller for faster processing
        overlap = 150      # Less overlap for speed
        chunks = []
        
        # Split by sentences first, then by chunks
        sentences = extracted_text.replace('\n', ' ').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip() + "."
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If chunks are too few, fall back to original method
        if len(chunks) < 3:
            chunks = []
            for i in range(0, len(extracted_text), chunk_size - overlap):
                chunk = extracted_text[i:i + chunk_size]
                if chunk.strip():
                    chunks.append(chunk)
        
        print(f"📄 Created {len(chunks)} chunks from text")
        print(f"📄 First chunk preview: {chunks[0][:200]}...")
        print(f"📄 Last chunk preview: {chunks[-1][:200]}...")

        # Use Hugging Face embeddings with lazy loading
        # Define texts variable outside try block to avoid scope issues
        texts = chunks
        vectors = []
        model = None
        
        # Lazy load the model only when needed
        def get_model():
            global _model_instance
            if not hasattr(get_model, '_model_instance') or get_model._model_instance is None:
                try:
                    from sentence_transformers import SentenceTransformer
                    print("🔄 Loading Hugging Face model...")
                    # Load the model - using a model that generates 1024-dimensional embeddings
                    get_model._model_instance = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # This generates 768-dim embeddings
                    print("✅ Model loaded successfully")
                except Exception as e:
                    print(f"❌ Model loading failed: {e}")
                    get_model._model_instance = None
            return get_model._model_instance
        
        try:
            model = get_model()
            if model is None:
                raise Exception("Failed to load Hugging Face model")
            
            # Test the model with a simple embedding first
            print("🧪 Testing model with sample text...")
            test_embedding = model.encode(["test"], convert_to_tensor=False)
            print(f"✅ Model test successful - embedding dimension: {len(test_embedding[0])}")
            
            # Generate embeddings in batches for efficiency
            embeddings = model.encode(texts, convert_to_tensor=False)
            
            print(f"🔍 Original embedding dimension: {len(embeddings[0])}")
            
            for embedding in embeddings:
                # Convert to list and pad to match Pinecone index dimension (1024)
                embedding_list = embedding.tolist()
                if len(embedding_list) != 1024:
                    if len(embedding_list) > 1024:
                        embedding_list = embedding_list[:1024]
                    else:
                        embedding_list = embedding_list + [0.0] * (1024 - len(embedding_list))
                
                vectors.append(embedding_list)
            
            # Debug: Check if vectors are all zeros (which would cause similarity issues)
            first_vector = vectors[0]
            zero_count = sum(1 for x in first_vector if x == 0.0)
            print(f"🔍 First vector has {zero_count}/{len(first_vector)} zero values")
            print(f"🔍 First vector sample: {first_vector[:10]}")
            
            print(f"🔍 Final embedding dimension: {len(vectors[0])}")
            
            print(f"✅ Generated {len(vectors)} embeddings using Hugging Face (all-mpnet-base-v2)")
            
        except Exception as e:
            print(f"❌ Hugging Face embeddings failed: {e}")
            print(f"⚠️  This might be due to network issues or model download problems")
            error_detail = f"Embedding generation failed: {e}. "
            error_detail += "This is likely due to network connectivity issues preventing the model from downloading. "
            error_detail += "Please ensure you have a stable internet connection and try again. "
            error_detail += "The system requires the Hugging Face model to be downloaded for the first time."
            raise HTTPException(status_code=500, detail=error_detail)

        # Pinecone setup
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_index_name = os.getenv("PINECONE_INDEX", "policy-documents")
        pc = Pinecone(api_key=pinecone_api_key)
        
        # Check if index exists
        try:
            index = pc.Index(pinecone_index_name)
            print(f"✅ Connected to Pinecone index: {pinecone_index_name}")
            
            # Get index stats to check dimension
            try:
                index_stats = index.describe_index_stats()
                print(f"🔍 Index stats: {index_stats}")
            except Exception as e:
                print(f"⚠️  Could not get index stats: {e}")
                
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
            print(f"🔍 Sample vector metadata: {pinecone_vectors[0]['metadata']}")
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
                        
                        # Generate embedding for the question using Hugging Face
                        question_model = get_model()
                        if question_model is None:
                            raise Exception("Model not available for question embedding")
                        question_embedding = question_model.encode([question], convert_to_tensor=False)[0]
                        question_embedding_list = question_embedding.tolist()
                        
                        print(f"🔍 Question embedding dimension: {len(question_embedding_list)}")
                        
                        # Pad embeddings to match Pinecone dimension (1024)
                        if len(question_embedding_list) != 1024:
                            if len(question_embedding_list) > 1024:
                                question_embedding_list = question_embedding_list[:1024]
                            else:
                                question_embedding_list = question_embedding_list + [0.0] * (1024 - len(question_embedding_list))
                        
                        print(f"🔍 Padded question embedding dimension: {len(question_embedding_list)}")
                        
                        # Query Pinecone directly with lower similarity threshold
                        query_response = index.query(
                            vector=question_embedding_list,
                            top_k=5,  # Reduced for faster processing
                            namespace=namespace,
                            include_metadata=True,
                            score_threshold=0.1   # Higher threshold for faster filtering
                        )
                        
                        print(f"🔍 Found {len(query_response.matches)} matches for question")
                        if len(query_response.matches) > 0:
                            print(f"🔍 Top match score: {query_response.matches[0].score}")
                            print(f"🔍 Top match text preview: {query_response.matches[0].metadata.get('text', '')[:150]}...")
                            print(f"🔍 All match scores: {[match.score for match in query_response.matches[:3]]}")
                        else:
                            print(f"🔍 No matches found - this might indicate embedding issues")
                            # Let's try a simple text search as fallback
                            print(f"🔍 Trying simple text search for: {question[:50]}...")
                            simple_matches = []
                            
                            # Extract key terms from question for better matching
                            key_terms = []
                            question_lower = question.lower()
                            
                            # Extract all meaningful words from the question (generic approach)
                            question_words = [word for word in question_lower.split() if len(word) > 2]
                            key_terms.extend(question_words)
                            
                            for i, text in enumerate(texts):
                                text_lower = text.lower()
                                # Count how many key terms are found in this text chunk
                                matches_found = sum(1 for term in key_terms if term in text_lower)
                                # Also check for partial matches (substrings)
                                partial_matches = sum(1 for term in key_terms if any(term in word or word in term for word in text_lower.split()))
                                total_score = matches_found + (partial_matches * 0.5)
                                if total_score >= 1.0:  # Higher threshold for faster processing
                                    simple_matches.append((i, text[:500], total_score))  # Less text for speed
                            
                            # Sort by number of matches (highest first)
                            simple_matches.sort(key=lambda x: x[2], reverse=True)
                            
                            print(f"🔍 Simple text search found {len(simple_matches)} potential matches")
                            if simple_matches:
                                print(f"🔍 Top match score: {simple_matches[0][2]} terms")
                                print(f"🔍 Key terms used: {key_terms[:10]}...")  # Show first 10 key terms
                                print(f"🔍 Sample matches: {[text[:150] for _, text, _ in simple_matches[:2]]}")
                        
                        if query_response.matches:
                            # Extract context chunks and similarity scores
                            context_chunks = []
                            similarity_scores = []
                            
                            # Filter matches by score and take top ones
                            good_matches = [match for match in query_response.matches if match.score > 0.15]
                            if not good_matches:
                                good_matches = query_response.matches[:2]  # Take top 2 if no good matches
                            
                            for match in good_matches:
                                context_chunks.append(match.metadata.get('text', ''))
                                similarity_scores.append(match.score)
                        else:
                            # Fallback to simple text search if no embedding matches
                            print(f"🔍 Using simple text search fallback")
                            context_chunks = []
                            
                            # Use the simple_matches we already found
                            if simple_matches:
                                for i, text, score in simple_matches[:3]:  # Take top 3 matches
                                    context_chunks.append(text)
                                    print(f"🔍 Added chunk with {score} matching terms")
                            else:
                                                                # Use the same improved key terms logic
                                key_terms = []
                                question_lower = question.lower()
                                
                                # Extract all meaningful words from the question (generic approach)
                                question_words = [word for word in question_lower.split() if len(word) > 2]
                                key_terms.extend(question_words)
                            
                            # Find best matching chunks
                            chunk_scores = []
                            for i, text in enumerate(texts):
                                text_lower = text.lower()
                                matches_found = sum(1 for term in key_terms if term in text_lower)
                                # Also check for partial matches (substrings)
                                partial_matches = sum(1 for term in key_terms if any(term in word or word in term for word in text_lower.split()))
                                total_score = matches_found + (partial_matches * 0.5)
                                if total_score >= 1.0:  # Higher threshold for faster processing
                                    chunk_scores.append((i, text, total_score))
                            
                            # Sort by match count and take top chunks
                            chunk_scores.sort(key=lambda x: x[2], reverse=True)
                            for i, text, score in chunk_scores[:5]:  # Take top 5 chunks
                                context_chunks.append(text)
                                if len(context_chunks) >= 3:  # Limit to 3 chunks
                                    break
                        
                        # Call LLM to generate final answer (for both embedding and text search)
                        if context_chunks:
                            print(f"🤖 Calling LLM for question: {question}")
                            
                            # Use OpenRouter for LLM
                            try:
                                from openai import OpenAI
                                openrouter_client = OpenAI(
                                    base_url="https://openrouter.ai/api/v1",
                                    api_key=os.getenv("OPENROUTER_API_KEY")
                                )
                                
                                # Create context for LLM - use fewer chunks for faster processing
                                context = "\n\n".join(context_chunks[:3])  # Use up to 3 chunks
                                print(f"🔍 Context being sent to LLM: {context[:500]}...")
                                print(f"🔍 Number of context chunks: {len(context_chunks)}")
                                
                                response = openrouter_client.chat.completions.create(
                                    model="mistralai/mistral-7b-instruct",
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a document analysis expert. Your task is to extract EXACT information from the provided context to answer questions about any document. Focus on specific numbers, dates, percentages, and precise terms from the document. If the context contains the exact information, provide it word-for-word where possible. If the context doesn't contain the specific information, say 'No relevant information found in the document.' Do not make assumptions or provide generic answers. Be precise and factual. Always include specific numbers, dates, and conditions when they are mentioned in the context."
                                        },
                                        {
                                            "role": "user",
                                            "content": f"Context: {context}\n\nQuestion: {question}\n\nExtract the EXACT information from the context to answer this question. Include specific numbers, dates, percentages, and conditions when mentioned. If the specific information is not in the context, say 'No relevant information found in the document.'"
                                        }
                                    ],
                                    max_tokens=600,   # Reduced for faster responses
                                    temperature=0.0  # Lower temperature for more precise answers
                                )
                                
                                answer = response.choices[0].message.content.strip()
                                
                            except Exception as e:
                                print(f"❌ LLM call failed: {e}")
                                answer = f"Based on the document: {' '.join(context_chunks[:2])}"
                            
                            # Keep source documents for reference
                            if query_response.matches:
                                source_docs = [match.metadata.get('text', '')[:100] + "..." for match in query_response.matches[:2]]
                            else:
                                source_docs = [text[:100] + "..." for text in context_chunks[:2]]
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

    # Extract just the answer strings for the expected response format
    answer_strings = []
    for answer_obj in answers:
        answer_strings.append(answer_obj["answer"])
    
    return {
        "answers": answer_strings
    }

@app.get("/")
async def root():
    return {"status": "ok", "message": "Policy Analysis API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Policy Analysis API is healthy", "timestamp": datetime.now().isoformat()}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for quick health checks"""
    return {"status": "pong", "timestamp": datetime.now().isoformat()}

@app.get("/debug-token")
async def debug_token():
    """Debug endpoint to check the current token (for testing only)"""
    return {
        "token": HACKRX_TOKEN,
        "expected_auth": f"Bearer {HACKRX_TOKEN}",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/show-token")
async def show_token():
    """Simple endpoint to show the current token"""
    return {"token": HACKRX_TOKEN}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False) 