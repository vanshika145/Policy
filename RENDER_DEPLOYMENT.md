# Render Deployment Guide

## Overview
This guide will help you deploy your FastAPI application to Render using Docker.

## Prerequisites
- GitHub repository with your code
- Render account
- Environment variables ready

## Step 1: Prepare Your Repository

### Files Required:
- `Dockerfile` ✅ (Created)
- `requirements.txt` ✅ (Updated)
- `.dockerignore` ✅ (Created)
- `docker-compose.yml` ✅ (Created for local testing)

### Key Features:
- ✅ Multi-stage Docker build
- ✅ Rust/C++ compilation support
- ✅ Python 3.10 with build tools
- ✅ Optimized for Render's environment

## Step 2: Deploy to Render

### 2.1 Create New Web Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository

### 2.2 Configure Service Settings

**Basic Settings:**
- **Name**: `policy-analysis-api` (or your preferred name)
- **Environment**: `Docker`
- **Region**: Choose closest to your users
- **Branch**: `main`

**Build Settings:**
- **Build Command**: Leave empty (Docker handles this)
- **Start Command**: Leave empty (Dockerfile CMD handles this)

**Environment Variables:**
Add these environment variables:
```
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
HACKRX_TOKEN=your_hackrx_token
```

### 2.3 Advanced Settings
- **Health Check Path**: `/health`
- **Auto-Deploy**: Enabled
- **Build Filter**: `main` branch only

## Step 3: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build your Docker image
   - Install all dependencies
   - Start your application
   - Run health checks

## Step 4: Verify Deployment

### Health Check
Your app should respond to: `https://your-app-name.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-01T19:14:12.918736"
}
```

### API Documentation
Access your API docs at: `https://your-app-name.onrender.com/docs`

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check Docker logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Dockerfile syntax

2. **Health Check Failures**
   - Ensure `/health` endpoint exists
   - Check application logs
   - Verify port configuration

3. **Memory Issues**
   - Render provides 512MB RAM by default
   - Consider upgrading if needed
   - Optimize Docker image size

### Debug Commands:

**Local Testing:**
```bash
# Build and run locally
docker build -t policy-api .
docker run -p 8000:8000 policy-api

# Or use docker-compose
docker-compose up --build
```

**Check Logs:**
```bash
# In Render dashboard or locally
docker logs <container_id>
```

## Environment Variables

Make sure to set these in Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Yes |
| `PINECONE_API_KEY` | Pinecone API key for vector DB | Yes |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Yes |
| `HACKRX_TOKEN` | HackRx API token | Yes |

## Performance Tips

1. **Docker Optimization:**
   - Multi-stage builds (already implemented)
   - Layer caching (requirements.txt copied first)
   - Minimal base image (python:3.10-slim)

2. **Render Optimization:**
   - Use appropriate instance type
   - Enable auto-scaling if needed
   - Monitor resource usage

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test all endpoints
3. ✅ Configure custom domain (optional)
4. ✅ Set up monitoring
5. ✅ Configure auto-scaling

## Support

If you encounter issues:
1. Check Render logs in dashboard
2. Verify environment variables
3. Test locally with Docker
4. Check application logs

Your FastAPI application is now ready for Render deployment! 🚀 