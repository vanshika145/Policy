# Deployment Checklist for Policy Analysis API

## ✅ Pre-Deployment Checklist

### 1. Files Created/Updated
- [x] `Procfile` - Created for Render deployment
- [x] `runtime.txt` - Python version specified (3.11.0)
- [x] `build.sh` - Build script created with error handling
- [x] `requirements.txt` - Simplified to avoid Rust compilation
- [x] `requirements-minimal.txt` - Minimal requirements for testing
- [x] `main.py` - Updated with proper environment variable handling
- [x] `DEPLOYMENT.md` - Deployment guide created
- [x] `.gitignore` - Proper exclusions set

### 2. Environment Variables Required
- [ ] `DATABASE_URL` - PostgreSQL connection string (optional)
- [ ] `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` - Firebase config path
- [ ] `FIREBASE_PROJECT_ID` - Firebase project ID
- [ ] `OPENAI_API_KEY` - OpenAI API key for embeddings
- [ ] `PINECONE_API_KEY` - Pinecone API key
- [ ] `PINECONE_ENVIRONMENT` - Pinecone environment (e.g., us-west1-gcp)
- [ ] `OPENROUTER_API_KEY` - OpenRouter API key for Mistral LLM
- [ ] `HACKRX_TOKEN` - Token for webhook authentication

### 3. API Endpoints Available
- [x] `GET /` - Root endpoint
- [x] `GET /health` - Health check
- [x] `POST /hackrx/run` - Main webhook endpoint
- [x] `POST /hackrx/run-simple` - Simple webhook endpoint
- [x] `POST /upload` - File upload (PDF only)
- [x] `POST /query` - Document querying

### 4. Dependencies Included (Minimal)
- [x] FastAPI and Uvicorn
- [x] SQLAlchemy (SQLite fallback)
- [x] Firebase Admin SDK
- [x] LangChain and OpenAI
- [x] Pinecone client
- [x] HTTP client (httpx)
- [x] **PDF processing only** (PyPDF2)
- [x] **No Rust compilation dependencies**

### 5. Configuration Updates
- [x] CORS configured for deployment (allow all origins)
- [x] Environment variables loaded properly
- [x] Error handling for missing database
- [x] Uploads directory creation
- [x] Proper logging and debugging
- [x] **PDF-only file support** (to avoid Rust compilation)
- [x] **SQLite fallback** for database

## 🚀 Deployment Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Use minimal requirements to avoid Rust compilation"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Set all required environment variables
6. Deploy

### 3. Test Deployment
1. Check health endpoint: `https://your-app.onrender.com/health`
2. Test webhook: `https://your-app.onrender.com/hackrx/run`

## 📋 Webhook URL Format

Your webhook URL will be:
```
https://your-app-name.onrender.com/hackrx/run
```

## 🔧 Troubleshooting

### If Build Still Fails:
1. **Try minimal requirements**: Use `requirements-minimal.txt` instead
2. **Check logs**: Look for specific package causing Rust compilation
3. **Remove problematic packages**: One by one until build succeeds

### Common Issues:
1. **Build Failures**: Try minimal requirements first
2. **Runtime Errors**: Check logs in Render dashboard
3. **Environment Variables**: Ensure all required vars are set
4. **Database Issues**: API works with SQLite fallback

### Testing Commands:
```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Test webhook
curl -X POST https://your-app.onrender.com/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-hackrx-token" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period?"]
  }'
```

## ⚠️ Important Notes

- **PDF files only** - Word documents and emails not supported
- **SQLite fallback** - Database works without PostgreSQL
- **Minimal dependencies** - Only essential packages included
- **Test first** - Try minimal requirements if full requirements fail

## ✅ Ready for Deployment!

Your backend is now ready for deployment to Render. If the main requirements.txt still fails, try using requirements-minimal.txt for a basic deployment. 