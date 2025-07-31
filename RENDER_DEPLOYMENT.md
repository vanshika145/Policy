# Render Deployment Guide with Docker

## 🐳 Docker + Rust + Python Setup

This project uses a multi-stage Docker build to support Rust-based Python packages while keeping the final image slim.

## 📋 Prerequisites

- Docker installed on your system
- Render account with Docker support
- Environment variables configured

## 🚀 Quick Start

### 1. Local Development

```bash
# Build and run with Docker Compose
docker-compose up api-dev

# Or build and run production image
docker-compose up api
```

### 2. Render Deployment

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service**
3. **Configure the service:**
   - **Environment**: Docker
   - **Build Command**: `docker build -t policy-api .`
   - **Start Command**: `docker run -p $PORT:8000 policy-api`

## 🔧 Environment Variables

Set these in your Render dashboard:

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

## 🏗️ Multi-Stage Build Architecture

### Stage 1: Builder
- **Base**: `python:3.10-slim`
- **Rust**: Installed for compiled packages
- **Poetry**: Dependency management
- **Build tools**: All necessary compilation tools

### Stage 2: Runtime
- **Base**: `python:3.10-slim`
- **Minimal**: Only runtime dependencies
- **Security**: Non-root user
- **Health checks**: Built-in monitoring

## 📁 Project Structure

```
.
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Local development
├── .dockerignore          # Excluded files
├── server/
│   ├── pyproject.toml     # Poetry configuration
│   ├── poetry.lock        # Locked dependencies
│   ├── main.py           # FastAPI application
│   └── ...
└── client/               # Frontend (excluded)
```

## 🛠️ Development Commands

### Local Development
```bash
# Start development server with hot reload
docker-compose up api-dev

# Build production image
docker build -t policy-api .

# Run production container
docker run -p 8000:8000 policy-api
```

### Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test webhook
curl -X POST http://localhost:8000/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{
    "documents": "https://example.com/policy.pdf",
    "questions": ["What is the grace period?"]
  }'
```

## 🔍 Troubleshooting

### Common Issues

1. **Build fails with Rust compilation:**
   ```bash
   # Check Rust installation
   docker run --rm policy-api rustc --version
   
   # Rebuild with no cache
   docker build --no-cache -t policy-api .
   ```

2. **Memory issues:**
   ```bash
   # Increase memory limit
   docker run --memory=4g policy-api
   ```

3. **Port conflicts:**
   ```bash
   # Use different port
   docker run -p 8001:8000 policy-api
   ```

### Debugging

```bash
# Access container shell
docker exec -it <container_id> /bin/bash

# View logs
docker logs <container_id>

# Check container resources
docker stats <container_id>
```

## 🚀 Render-Specific Configuration

### Build Settings
- **Build Command**: `docker build -t policy-api .`
- **Start Command**: `docker run -p $PORT:8000 policy-api`
- **Environment**: Docker

### Environment Variables
Set all required environment variables in Render dashboard:
- `HACKRX_TOKEN`
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENVIRONMENT`
- `OPENROUTER_API_KEY`
- `FIREBASE_PROJECT_ID`

### Health Checks
The Dockerfile includes built-in health checks:
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

## ✅ Features

- **Multi-stage build**: Optimized for size and security
- **Rust support**: Handles compiled Python packages
- **Poetry dependency management**: Reproducible builds
- **Security**: Non-root user in runtime
- **Health checks**: Built-in monitoring
- **Hot reload**: Development mode support
- **Production ready**: Optimized for deployment

## 📝 Notes

- **Rust compilation** happens in the builder stage only
- **Runtime image** is slim and secure
- **Poetry** ensures dependency consistency
- **Health checks** help with monitoring
- **Non-root user** improves security
- **Multi-stage build** reduces final image size

## 🎯 Ready for Deployment

Your project is now ready for Render deployment with full Rust and Python support! 