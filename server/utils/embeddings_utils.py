import os
import asyncio
from typing import List, Optional
from pathlib import Path
import logging
import uuid
from datetime import datetime
import httpx

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader, UnstructuredEmailLoader
from langchain.schema import Document
import pinecone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def call_llm(question: str, context_chunks: List[str], similarity_scores: List[float]) -> str:
    """
    Call OpenRouter API with Mistral to generate final answer
    
    Args:
        question: The user's question
        context_chunks: List of relevant document chunks
        similarity_scores: List of similarity scores for each chunk
    
    Returns:
        str: The LLM-generated answer
    """
    # Check if we have any relevant chunks - be very permissive
    if not context_chunks or all(score < 0.001 for score in similarity_scores):
        return "No relevant information found in the document."
    
    # Get OpenRouter API key
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("⚠️  OPENROUTER_API_KEY not found in environment variables")
        return "Unable to generate answer: OpenRouter API key not configured."
    
    # Format context chunks with similarity scores
    context_text = ""
    for i, (chunk, score) in enumerate(zip(context_chunks, similarity_scores)):
        context_text += f"Chunk {i+1} (similarity: {score:.3f}):\n{chunk}\n\n"
    
    # Prepare the prompt
    system_prompt = """You are an expert insurance policy analyst. Your job is to provide ACCURATE and SPECIFIC answers based ONLY on the provided context.

**CRITICAL REQUIREMENTS:**
1. **Extract EXACT information** from the provided context that directly answers the user's question
2. **Provide SPECIFIC details** with exact numbers, dates, amounts, and conditions
3. **Be PRECISE** - avoid vague or generic statements
4. **Search thoroughly** - look for any relevant information in the context, even if it's not immediately obvious
5. **Write clean, direct answers without unnecessary formatting**

**Guidelines for HIGH ACCURACY:**
- If asked for amounts: Provide EXACT amount with currency (e.g., "INR 50,000" not "some amount")
- If asked for dates: Provide EXACT date (e.g., "15 days" not "a few days")
- If asked for waiting periods: Provide EXACT duration (e.g., "36 months" not "several months")
- If asked for conditions: List ALL specific conditions mentioned
- If asked for coverage: State EXACTLY what is covered and what is not
- Do NOT mention chunk numbers or section references in your answer
- Look for information even if it's mentioned in passing or in different sections

**For complex insurance questions, provide:**
- Exact policy terms and conditions
- Specific waiting periods and timeframes
- Coverage limits and sub-limits
- Eligibility criteria and requirements
- Benefit details and restrictions

**Answer Quality Standards:**
- Start with a direct answer to the question
- Include specific numbers, dates, and amounts when available
- Write in clean, readable format without excessive line breaks
- If information is incomplete, state what is missing
- Focus only on the information that directly answers the question
- Be thorough in searching the provided context

**Example format:**
"The grace period for premium payment is thirty days. If the due instalment premium is paid within the grace period, coverage shall be available during the grace period. However, if the premium is not paid within the grace period, the policy will be cancelled and no refund will be allowed."
"""
    
    user_prompt = f"Context:\n{context_text}\n\nQuestion:\n{question}"
    
    # Prepare the request payload
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    headers = {
        "Authorization": f"Bearer {openrouter_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Use synchronous httpx for this function
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    answer = result["choices"][0]["message"]["content"]
                    print(f"✅ LLM generated answer: {answer[:100]}...")
                    return answer
                else:
                    print(f"⚠️  Unexpected response format: {result}")
                    return "Unable to generate answer: Unexpected response format."
            else:
                print(f"⚠️  API error ({response.status_code}): {response.text}")
                return f"Unable to generate answer: API error ({response.status_code})"
                
    except Exception as e:
        print(f"❌ Error calling LLM: {str(e)}")
        return f"Unable to generate answer: {str(e)}"

class EmbeddingsManager:
    def __init__(self, pinecone_api_key: Optional[str] = None, pinecone_environment: Optional[str] = None):
        """
        Initialize the embeddings manager with Pinecone.
        
        Args:
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment (e.g., 'us-west1-gcp')
        """
        # Initialize embeddings model with fallback for quota issues
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = None
        
        if openai_api_key and openai_api_key != "your-openai-api-key-here":
            try:
                # Test OpenAI embeddings to check for quota issues
                test_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
                # Try a simple test to see if quota is exceeded
                test_embeddings.embed_query("test")
                self.embeddings = test_embeddings
                logger.info("✅ Using OpenAI embeddings for high-quality semantic search")
            except Exception as e:
                error_msg = str(e).lower()
                if "quota" in error_msg or "429" in error_msg or "insufficient_quota" in error_msg:
                    logger.warning(f"⚠️  OpenAI quota exceeded, falling back to HuggingFace: {e}")
                    # Fallback to HuggingFace when quota is exceeded
                    try:
                        from langchain_community.embeddings import HuggingFaceEmbeddings
                        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                        logger.info("✅ Using HuggingFace embeddings as fallback (free, no quota limits)")
                    except ImportError:
                        logger.error("❌ HuggingFace embeddings not available. Please install sentence-transformers")
                        raise Exception("OpenAI quota exceeded and HuggingFace not available")
                else:
                    logger.warning(f"⚠️  OpenAI embeddings failed (not quota related): {e}")
                    # Try HuggingFace fallback for other OpenAI errors
                    try:
                        from langchain_community.embeddings import HuggingFaceEmbeddings
                        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                        logger.info("✅ Using HuggingFace embeddings as fallback")
                    except ImportError:
                        logger.error("❌ HuggingFace embeddings not available")
                        raise Exception(f"OpenAI failed and HuggingFace not available: {e}")
        else:
            # No OpenAI key provided, use HuggingFace
            try:
                from langchain_community.embeddings import HuggingFaceEmbeddings
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                logger.info("✅ Using HuggingFace embeddings (no OpenAI key provided)")
            except ImportError:
                logger.error("❌ HuggingFace embeddings not available. Please install sentence-transformers or provide OpenAI API key")
                raise Exception("No OpenAI API key and HuggingFace not available")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize Pinecone
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.pinecone_environment = pinecone_environment or os.getenv("PINECONE_ENVIRONMENT")
        
        if not self.pinecone_api_key or not self.pinecone_environment:
            logger.warning("Pinecone credentials not found. Embeddings will not be stored.")
            self.pinecone_index = None
        else:
            self._initialize_pinecone()
    
    def _initialize_pinecone(self):
        """Initialize Pinecone client and index."""
        try:
            from pinecone import Pinecone
            
            # Initialize Pinecone client
            self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
            
            # Create index if it doesn't exist
            index_name = "policy-documents"
            if index_name not in self.pinecone_client.list_indexes().names():
                # Note: You'll need to specify the cloud and region for serverless
                # For now, we'll just connect to existing index
                logger.warning(f"Index {index_name} not found. Please create it manually in Pinecone console.")
                self.pinecone_index = None
            else:
                self.pinecone_index = self.pinecone_client.Index(index_name)
                logger.info(f"Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.pinecone_index = None
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load a document based on its file type.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of Document objects
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.pdf':
                loader = PyPDFLoader(str(file_path))
                documents = loader.load()
                logger.info(f"Loaded PDF document: {file_path}")
                
            elif file_extension in ['.docx', '.doc']:
                loader = UnstructuredFileLoader(str(file_path))
                documents = loader.load()
                logger.info(f"Loaded Word document: {file_path}")
                
            elif file_extension in ['.eml', '.msg']:
                loader = UnstructuredEmailLoader(str(file_path))
                documents = loader.load()
                logger.info(f"Loaded email document: {file_path}")
                
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            raise
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise
    
    async def store_embeddings(self, file_path: str, user_id: str, filename: str, user_email: str) -> dict:
        """
        Process a document and store its embeddings in Pinecone.
        
        Args:
            file_path: Path to the document file
            user_id: User identifier for metadata
            filename: Original filename
            user_email: User's email address
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Load document
            documents = self.load_document(file_path)
            
            # Split into chunks
            chunks = self.split_documents(documents)
            
            if not self.pinecone_index:
                return {
                    "success": False,
                    "message": "Pinecone not configured. Please set PINECONE_API_KEY and PINECONE_ENVIRONMENT.",
                    "error": "Pinecone not initialized"
                }
            
            # Generate embeddings and prepare for Pinecone
            vectors_to_upsert = []
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                if hasattr(self.embeddings, 'embed_query'):
                    # OpenAI or HuggingFace embeddings (both use embed_query)
                    embedding = self.embeddings.embed_query(chunk.page_content)
                else:
                    # Fallback for sentence-transformers
                    embedding = self.embeddings.encode(chunk.page_content).tolist()
                
                # Pad embeddings to match Pinecone index dimension (1024)
                original_dim = len(embedding)
                if original_dim == 1536:  # OpenAI embeddings
                    logger.info(f"Padding OpenAI embeddings from 1536 to 1024 dimensions...")
                    # Take first 1024 dimensions from OpenAI embeddings
                    embedding = embedding[:1024]
                elif original_dim == 384:  # HuggingFace embeddings
                    logger.info(f"Padding HuggingFace embeddings from 384 to 1024 dimensions...")
                    # Pad with zeros to reach 1024 dimensions
                    embedding = embedding + [0.0] * (1024 - original_dim)
                elif original_dim != 1024:
                    logger.info(f"Padding embeddings from {original_dim} to 1024 dimensions...")
                    # Pad with zeros to reach 1024 dimensions
                    embedding = embedding + [0.0] * (1024 - original_dim)
                
                logger.info(f"✅ Final embedding dimension: {len(embedding)}")
                
                # Create unique ID for the vector
                vector_id = f"{user_id}_{filename}_{i}_{uuid.uuid4().hex[:8]}"
                
                # Prepare metadata
                metadata = {
                    "user_id": user_id,
                    "filename": filename,
                    "user_email": user_email,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "upload_date": datetime.now().isoformat(),
                    "content": chunk.page_content[:500],  # First 500 chars for preview
                    "source_file": file_path
                }
                
                vectors_to_upsert.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata
                })
            
            # Upsert to Pinecone
            self.pinecone_index.upsert(vectors=vectors_to_upsert)
            
            logger.info(f"Stored {len(chunks)} embeddings in Pinecone for user {user_id}")
            
            return {
                "success": True,
                "message": f"Successfully processed and stored {len(chunks)} chunks",
                "chunks_count": len(chunks),
                "user_id": user_id,
                "filename": filename,
                "status": "success"
            }
                
        except Exception as e:
            logger.error(f"Error storing embeddings: {e}")
            return {
                "success": False,
                "message": f"Failed to process document: {str(e)}",
                "error": str(e)
            }
    
    def search_similar(self, query: str, user_id: str, k: int = 5, document_filter: str = None) -> List[dict]:
        """
        Search for similar documents in Pinecone.
        
        Args:
            query: Search query
            user_id: User identifier to filter results
            k: Number of results to return
            document_filter: Optional document filename to filter results
            
        Returns:
            List of search results with metadata
        """
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available")
                return []
            
            # Generate query embedding
            if hasattr(self.embeddings, 'embed_query'):
                query_embedding = self.embeddings.embed_query(query)
            else:
                query_embedding = self.embeddings.encode(query).tolist()
            
            # Pad query embedding to match Pinecone index dimension (1024)
            original_dim = len(query_embedding)
            if original_dim == 1536:  # OpenAI embeddings
                query_embedding = query_embedding[:1024]
            elif original_dim == 384:  # HuggingFace embeddings
                query_embedding = query_embedding + [0.0] * (1024 - original_dim)
            elif original_dim != 1024:
                query_embedding = query_embedding + [0.0] * (1024 - original_dim)
            
            # Build filter based on user_id and document_filter
            filter_dict = {}
            if user_id and user_id.strip():
                filter_dict["user_id"] = user_id
            if document_filter:
                filter_dict["filename"] = document_filter
            
            # Search in Pinecone with metadata filter
            if filter_dict:
                results = self.pinecone_index.query(
                    vector=query_embedding,
                    top_k=k,
                    include_metadata=True,
                    filter=filter_dict
                )
            else:
                # No filter for debugging
                results = self.pinecone_index.query(
                    vector=query_embedding,
                    top_k=k,
                    include_metadata=True
                )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "content": match.metadata.get("content", ""),
                    "metadata": match.metadata,
                    "score": match.score
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar documents: {e}")
            return []
    
    def get_user_documents(self, user_id: str) -> List[dict]:
        """
        Get all documents for a specific user from Pinecone.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of user's documents
        """
        try:
            if not self.pinecone_index:
                logger.error("Pinecone index not available")
                return []
            
            # Query Pinecone for user's documents
            results = self.pinecone_index.query(
                vector=[0] * 1536,  # Dummy vector for metadata-only query
                top_k=1000,
                include_metadata=True,
                filter={"user_id": user_id}
            )
            
            # Group by filename
            documents = {}
            for match in results.matches:
                filename = match.metadata.get("filename", "Unknown")
                if filename not in documents:
                    documents[filename] = {
                        "filename": filename,
                        "user_email": match.metadata.get("user_email", ""),
                        "upload_date": match.metadata.get("upload_date", ""),
                        "total_chunks": match.metadata.get("total_chunks", 0),
                        "chunks": []
                    }
                
                documents[filename]["chunks"].append({
                    "content": match.metadata.get("content", ""),
                    "chunk_index": match.metadata.get("chunk_index", 0)
                })
            
            return list(documents.values())
            
        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            return []

# Global embeddings manager instance
embeddings_manager = None

def get_embeddings_manager() -> EmbeddingsManager:
    """Get or create the global embeddings manager instance."""
    global embeddings_manager
    
    if embeddings_manager is None:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT")
        embeddings_manager = EmbeddingsManager(
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment
        )
    
    return embeddings_manager