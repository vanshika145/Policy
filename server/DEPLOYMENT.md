# Deployment Guide for Policy Analysis API

## Render Deployment

This guide will help you deploy the Policy Analysis API to Render.

### Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Environment Variables**: You'll need to set up the following environment variables in Render

### Required Environment Variables

Set these in your Render service environment variables:

```
# Database Configuration (Optional for basic functionality)
DATABASE_URL=postgresql://username:password@host/database

# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=config/firebase-service-account-key.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# OpenAI Configuration (for embeddings)
OPENAI_API_KEY=your-openai-api-key-here

# Pinecone Configuration (for vector database)
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp

# OpenRouter Configuration (for Mistral LLM)
OPENROUTER_API_KEY=your-openrouter-api-key-here

# HackRx Token (for webhook authentication)
HACKRX_TOKEN=your-hackrx-token-here
```

### Deployment Steps

1. **Connect to GitHub**: In Render, connect your GitHub repository
2. **Create Web Service**: Choose "Web Service" as the service type
3. **Configure Build Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Set Environment Variables**: Add all the required environment variables listed above
5. **Deploy**: Click "Create Web Service"

### API Endpoints

After deployment, your webhook URL will be:
```
https://your-app-name.onrender.com/hackrx/run
```

### Testing the Deployment

1. **Health Check**: Visit `https://your-app-name.onrender.com/health`
2. **Test Webhook**: Send a POST request to `/hackrx/run` with:
   ```json
   {
     "documents": "https://example.com/policy.pdf",
     "questions": ["What is the grace period?"]
   }
   ```

### Important Notes

- The API uses Pinecone for vector storage
- Mistral LLM is used for answer generation
- File uploads are stored in the `uploads/` directory
- CORS is configured to allow all origins for deployment
- The service will automatically restart if it crashes

### Troubleshooting

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Runtime Errors**: Check the logs in Render dashboard
3. **Environment Variables**: Ensure all required variables are set
4. **Database Issues**: The API works without a database for basic functionality

### Webhook URL Format

Your webhook URL should be submitted as:
```
https://your-app-name.onrender.com/hackrx/run
```

Replace `your-app-name` with your actual Render service name. 