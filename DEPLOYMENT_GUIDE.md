# 🚀 Optimal Deployment Guide for Policy Analysis API

## 🎯 **Recommended: Render with Standard Python Environment**

This is the **best deployment option** for your project because it:
- ✅ **Handles Rust compilation** properly
- ✅ **Supports all dependencies** (transformers, sentence-transformers, etc.)
- ✅ **Simple configuration** - no Docker complexity
- ✅ **Reliable deployment** - works consistently on Render
- ✅ **Full functionality** - PDF processing, embeddings, LLM integration

## 📋 **Prerequisites**

1. **GitHub Repository**: Your code is already on GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Environment Variables**: Set up your API keys

## 🚀 **Step-by-Step Deployment**

### **Step 1: Create Render Service**

1. **Go to Render Dashboard**
2. **Click "New +" → "Web Service"**
3. **Connect your GitHub repository**: `https://github.com/vanshika145/Policy`
4. **Configure the service:**

### **Step 2: Configure Build Settings**

```yaml
# Build Command
bash server/build-render.sh

# Start Command  
uvicorn server.main:app --host 0.0.0.0 --port $PORT

# Environment
Python 3.13.4 (default)
```

### **Step 3: Set Environment Variables**

In your Render dashboard, add these environment variables:

```bash
# Required for webhook authentication
HACKRX_TOKEN=your_actual_hackrx_token

# For OpenAI embeddings
OPENAI_API_KEY=your_openai_api_key

# For Pinecone vector database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# For OpenRouter LLM access
OPENROUTER_API_KEY=your_openrouter_api_key

# For Firebase authentication (optional)
FIREBASE_PROJECT_ID=your_firebase_project_id
```

### **Step 4: Deploy**

1. **Click "Create Web Service"**
2. **Wait for build to complete** (5-10 minutes)
3. **Check logs** for any issues
4. **Test your webhook**

## 🔧 **What the Build Script Does**

### **`server/build-render.sh`:**
1. **Upgrades pip, setuptools, wheel**
2. **Installs Rust** for compiled packages
3. **Installs all dependencies** including:
   - FastAPI, Uvicorn
   - SQLAlchemy, Firebase Admin
   - LangChain, OpenAI, Pinecone
   - Transformers, Sentence-transformers
   - PyPDF2, Unstructured
4. **Creates uploads directory**
5. **Verifies imports work**

## 🧪 **Testing Your Deployment**

### **1. Health Check**
```bash
curl https://your-app-name.onrender.com/health
```

### **2. Test Webhook**
```bash
curl -X POST https://your-app-name.onrender.com/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_hackrx_token" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period?"]
  }'
```

## 📊 **Expected Response**

```json
{
  "message": "Authorized and processed",
  "documents": "https://example.com/policy.pdf",
  "questions": ["What is the grace period?"],
  "num_chunks": 15,
  "pinecone_namespace": "hackrx-abc12345",
  "extracted_text_preview": "This policy document contains...",
  "answers": [
    {
      "question": "What is the grace period?",
      "answer": "The grace period is 30 days from the due date...",
      "source_documents": ["The grace period is 30 days...", "..."]
    }
  ]
}
```

## 🔍 **Troubleshooting**

### **Common Issues:**

1. **Build Fails with Rust Compilation:**
   - ✅ **Solution**: The build script handles this automatically
   - ✅ **Fallback**: Uses HuggingFace embeddings if OpenAI fails

2. **Memory Issues:**
   - ✅ **Solution**: Render provides adequate memory for this setup
   - ✅ **Optimization**: Uses efficient text chunking

3. **Environment Variables Missing:**
   - ✅ **Solution**: Set all required variables in Render dashboard
   - ✅ **Check**: Verify API keys are correct

4. **Pinecone Connection Issues:**
   - ✅ **Solution**: Ensure Pinecone index exists and is accessible
   - ✅ **Check**: Verify PINECONE_API_KEY and PINECONE_ENVIRONMENT

### **Debugging Commands:**

```bash
# Check build logs
# View in Render dashboard

# Test individual components
curl https://your-app.onrender.com/health

# Check environment variables
# View in Render dashboard → Environment tab
```

## 🎯 **Why This Approach is Best**

### **✅ Advantages:**
- **Full Rust Support**: Handles transformers, sentence-transformers
- **Complete Functionality**: PDF processing, embeddings, LLM
- **Reliable**: Standard Python environment on Render
- **Scalable**: Can handle multiple requests
- **Production Ready**: Health checks, error handling

### **✅ Features Working:**
- **PDF Text Extraction**: PyMuPDF or pdfminer
- **Text Chunking**: 1000-character chunks
- **Embeddings**: OpenAI or HuggingFace fallback
- **Vector Storage**: Pinecone integration
- **LLM Integration**: OpenRouter with Mistral
- **Webhook Authentication**: Bearer token validation

## 🚀 **Ready for HackRx Submission**

Once deployed, your webhook URL will be:
```
https://your-app-name.onrender.com/hackrx/run
```

**This setup provides:**
- ✅ **Complete PDF processing**
- ✅ **Semantic search with embeddings**
- ✅ **LLM-powered question answering**
- ✅ **Production-ready webhook**
- ✅ **Proper error handling**

## 📝 **Next Steps**

1. **Deploy to Render** using the configuration above
2. **Test your webhook** with sample PDFs
3. **Submit to HackRx** with your webhook URL
4. **Monitor logs** for any issues

**Your project is now ready for production deployment!** 🎯 