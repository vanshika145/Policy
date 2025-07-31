# Docker Deployment Guide

## 🐳 Docker Setup

This project includes Docker configuration for easy deployment and development.

## 📋 Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the API:**
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs

### Option 2: Using Docker directly

1. **Build the image:**
   ```bash
   docker build -t policy-api .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -e HACKRX_TOKEN=your_token \
     -e OPENAI_API_KEY=your_openai_key \
     -e PINECONE_API_KEY=your_pinecone_key \
     -e PINECONE_ENVIRONMENT=your_pinecone_env \
     -e OPENROUTER_API_KEY=your_openrouter_key \
     policy-api
   ```

## 🔧 Environment Variables

Set these environment variables for full functionality:

```bash
# Required for webhook authentication
HACKRX_TOKEN=your_hackrx_token

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

## 📁 Project Structure

```
.
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Files to exclude from Docker build
├── server/                # Backend code
│   ├── main.py           # Main FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── ...
└── client/               # Frontend code (excluded from Docker)
```

## 🛠️ Development

### Local Development with Docker

1. **Start the development environment:**
   ```bash
   docker-compose up --build
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

3. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Building for Production

1. **Build optimized image:**
   ```bash
   docker build -t policy-api:production .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name policy-api \
     -p 8000:8000 \
     --restart unless-stopped \
     -e HACKRX_TOKEN=your_token \
     policy-api:production
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Change the port mapping
   docker run -p 8001:8000 policy-api
   ```

2. **Memory issues with transformers:**
   ```bash
   # Increase memory limit
   docker run --memory=4g policy-api
   ```

3. **Build fails:**
   ```bash
   # Clean build
   docker system prune -a
   docker build --no-cache -t policy-api .
   ```

### Logs and Debugging

```bash
# View container logs
docker logs <container_id>

# Access container shell
docker exec -it <container_id> /bin/bash

# Check container resources
docker stats <container_id>
```

## 🚀 Deployment Options

### 1. Render (Recommended)
- Use the existing Render configuration
- Build command: `docker build -t policy-api .`
- Start command: `docker run -p $PORT:8000 policy-api`

### 2. AWS ECS
- Push to ECR
- Deploy using ECS Fargate

### 3. Google Cloud Run
- Build and push to Container Registry
- Deploy using Cloud Run

### 4. Azure Container Instances
- Push to Azure Container Registry
- Deploy using Container Instances

## ✅ Features

- **Rust support** for transformers and other compiled packages
- **Multi-stage builds** for optimized images
- **Environment variable** configuration
- **Volume mounting** for persistent data
- **Health checks** and monitoring
- **Production-ready** configuration

## 📝 Notes

- The Dockerfile uses Python 3.10 for better compatibility
- Rust is installed to support transformers and other compiled packages
- The image includes all necessary system dependencies
- Environment variables can be set at runtime
- Uploads directory is mounted as a volume for persistence 