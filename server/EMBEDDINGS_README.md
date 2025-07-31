# Embeddings Generation System

This system processes uploaded documents (PDF, DOCX, EML) and stores their embeddings in Pinecone vector database for AI-powered search and analysis.

## Features

- ✅ **Multi-format Support**: PDF, DOCX, DOC, EML files
- ✅ **Text Extraction**: Using LangChain document loaders
- ✅ **Smart Chunking**: RecursiveCharacterTextSplitter for optimal text segmentation
- ✅ **Vector Storage**: Pinecone vector database for scalable storage
- ✅ **Metadata Storage**: PostgreSQL for file metadata and user information
- ✅ **Background Processing**: Async processing for large documents
- ✅ **Search Capability**: Semantic search across user documents

## Setup

### 1. Environment Variables

Create a `.env` file in the `server/` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/policy_db

# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=config/firebase-service-account-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your-openai-api-key-here

# Pinecone Configuration (for vector database)
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Pinecone Setup

1. Create a Pinecone account at [https://app.pinecone.io/](https://app.pinecone.io/)
2. Get your API key from the Pinecone console
3. Note your environment (e.g., `us-west1-gcp`)
4. The system will automatically create the `policy-documents` index

### 4. Test the Setup

```bash
python test_embeddings.py
```

## API Endpoints

### Upload and Process Document

**POST** `/upload`

Uploads a file and automatically generates embeddings.

**Request:**
- `file`: PDF, DOCX, DOC, or EML file
- `Authorization`: Bearer token (Firebase ID token)

**Response:**
```json
{
  "filename": "document.pdf",
  "number_of_chunks": 15,
  "status": "success",
  "message": "Successfully processed and stored 15 chunks"
}
```

### Generate Embeddings for Existing File

**POST** `/embeddings/generate-embeddings`

Generates embeddings for an already uploaded file.

**Request:**
```json
{
  "file_id": 123
}
```

**Response:**
```json
{
  "success": true,
  "message": "Embeddings generation started in background",
  "file_id": 123,
  "user_id": 1,
  "status": "processing"
}
```

### Search Documents

**GET** `/embeddings/search?query=your search query&k=5`

Searches through user's embedded documents.

**Response:**
```json
{
  "success": true,
  "query": "your search query",
  "results": [
    {
      "content": "Relevant document content...",
      "metadata": {
        "filename": "document.pdf",
        "user_email": "user@example.com",
        "upload_date": "2024-01-01T00:00:00"
      },
      "score": 0.95
    }
  ],
  "count": 1
}
```

## Architecture

### File Processing Pipeline

1. **File Upload**: User uploads document via `/upload` endpoint
2. **Text Extraction**: LangChain loaders extract text based on file type
3. **Text Chunking**: RecursiveCharacterTextSplitter divides text into manageable chunks
4. **Embedding Generation**: OpenAI embeddings convert text chunks to vectors
5. **Vector Storage**: Vectors stored in Pinecone with metadata
6. **Metadata Storage**: File info stored in PostgreSQL

### Supported File Types

| File Type | Loader | Description |
|-----------|--------|-------------|
| PDF | `PyPDFLoader` | Extracts text from PDF documents |
| DOCX/DOC | `UnstructuredFileLoader` | Handles Word documents |
| EML/MSG | `UnstructuredEmailLoader` | Processes email files |

### Vector Database Schema

**Pinecone Index**: `policy-documents`
- **Dimension**: 1536 (OpenAI embeddings)
- **Metric**: Cosine similarity
- **Metadata**:
  - `user_id`: User identifier
  - `filename`: Original filename
  - `user_email`: User's email
  - `chunk_index`: Position in document
  - `total_chunks`: Total number of chunks
  - `upload_date`: Upload timestamp
  - `content`: First 500 characters for preview

## Usage Examples

### Frontend Integration

```typescript
// Upload file with embeddings generation
const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/upload', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  const result = await response.json();
  console.log(`Processed ${result.number_of_chunks} chunks`);
};

// Search documents
const searchDocuments = async (query: string) => {
  const response = await fetch(`/embeddings/search?query=${encodeURIComponent(query)}`);
  const results = await response.json();
  return results.results;
};
```

### Backend Testing

```python
# Test embeddings generation
from utils.embeddings_utils import get_embeddings_manager

async def test_embeddings():
    manager = get_embeddings_manager()
    result = await manager.store_embeddings(
        file_path="document.pdf",
        user_id="user123",
        filename="document.pdf",
        user_email="user@example.com"
    )
    print(f"Generated {result['chunks_count']} embeddings")
```

## Error Handling

The system includes comprehensive error handling:

- **File Type Validation**: Only supported formats are processed
- **Pinecone Connection**: Graceful fallback if Pinecone is unavailable
- **OpenAI API**: Fallback to sentence-transformers if OpenAI is unavailable
- **Background Processing**: Non-blocking processing for large files
- **Metadata Validation**: Ensures all required fields are present

## Performance Considerations

- **Chunk Size**: 1000 characters with 200 character overlap
- **Batch Processing**: Vectors are upserted in batches to Pinecone
- **Async Processing**: Large documents are processed in background
- **Caching**: Embeddings manager is cached globally
- **Error Recovery**: Failed uploads are cleaned up automatically

## Monitoring

The system includes logging for monitoring:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

Key metrics logged:
- Document loading success/failure
- Chunk generation statistics
- Embedding generation progress
- Pinecone storage operations
- Search query performance

## Troubleshooting

### Common Issues

1. **Pinecone Connection Failed**
   - Check API key and environment
   - Verify network connectivity
   - Ensure index exists

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check rate limits
   - Ensure sufficient credits

3. **File Processing Errors**
   - Check file format is supported
   - Verify file is not corrupted
   - Ensure sufficient disk space

4. **Memory Issues**
   - Reduce chunk size for large documents
   - Process documents in smaller batches
   - Monitor system resources

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- **Authentication**: All endpoints require Firebase authentication
- **User Isolation**: Documents are filtered by user_id
- **API Key Security**: Store keys in environment variables
- **File Validation**: Only supported file types are processed
- **Metadata Sanitization**: User data is properly escaped

## Future Enhancements

- [ ] **Batch Processing**: Process multiple files simultaneously
- [ ] **Progress Tracking**: Real-time progress updates
- [ ] **Document Versioning**: Track document updates
- [ ] **Advanced Search**: Filters and faceted search
- [ ] **Export Functionality**: Export search results
- [ ] **Analytics**: Usage statistics and performance metrics