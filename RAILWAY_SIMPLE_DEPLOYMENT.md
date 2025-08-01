# Railway Simple Deployment Guide (No Docker)

## 🚀 Deploy Your FastAPI Backend to Railway - Simple Method

This guide uses Railway's native Python runtime without Docker for easier deployment.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Environment Variables**: Prepare your API keys and tokens

## 🔧 Step 1: Prepare Your Repository

### 1.1 Verify Files Are Ready
Your repository should have:
- ✅ `railway.json` (configured for Python runtime)
- ✅ `main.py` (entry point)
- ✅ `requirements.txt` (dependencies)
- ✅ `server/main.py` (your FastAPI app)

### 1.2 Update Requirements (if needed)
Make sure your `requirements.txt` has all necessary packages:

```txt
fastapi==0.95.2
uvicorn[standard]==0.22.0
python-dotenv==1.0.0
httpx>=0.24.0
pydantic==1.10.13
sqlalchemy==2.0.23
firebase-admin==6.2.0
openai>=1.10.0
pinecone==7.3.0
PyPDF2==3.0.1
```

### 1.3 Commit and Push Changes
```bash
git add .
git commit -m "Add Railway Python deployment configuration"
git push origin main
```

## 🚀 Step 2: Deploy to Railway

### 2.1 Connect Your Repository

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Railway Auto-Detection**
   - Railway will automatically detect it's a Python project
   - It will use the `railway.json` configuration
   - No Docker build required!

### 2.2 Set Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

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

### 2.3 Deploy

1. **Automatic Deployment**
   - Railway will automatically deploy when you push to your main branch
   - No manual build process needed

2. **Monitor Deployment**
   - Watch the deployment logs in the Railway dashboard
   - Railway will install Python dependencies automatically

## 🔍 Step 3: Verify Deployment

### 3.1 Check Health Endpoint
Once deployed, test your API:
```bash
curl https://your-app-name.railway.app/health
```

### 3.2 Test API Documentation
Visit: `https://your-app-name.railway.app/docs`

### 3.3 Check Logs
- Go to your Railway project dashboard
- Click on your service
- Check the "Logs" tab for any errors

## 🛠️ Step 4: Custom Domain (Optional)

1. **Add Custom Domain**
   - Go to your Railway project
   - Click "Settings" → "Domains"
   - Add your custom domain

2. **Configure DNS**
   - Point your domain to Railway's servers
   - Follow Railway's DNS configuration instructions

## 🔧 Troubleshooting

### Common Issues

1. **Python Version Issues**
   - Railway automatically detects Python version
   - If needed, add `runtime.txt` with your Python version:
   ```
   python-3.10.12
   ```

2. **Dependency Issues**
   - Check your `requirements.txt` is up to date
   - Railway will show build errors in logs

3. **Environment Variables Missing**
   - Verify all required variables are set in Railway dashboard
   - Check variable names match your code

4. **Port Issues**
   - Railway automatically sets the `PORT` environment variable
   - Your app uses `$PORT` automatically

### Debug Commands

```bash
# Test locally
python main.py

# Check requirements
pip install -r requirements.txt

# Test with Railway environment
PORT=8000 uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📊 Monitoring

### Railway Dashboard Features
- **Real-time logs**: Monitor your application
- **Metrics**: CPU, memory, and network usage
- **Deployments**: Track deployment history
- **Environment variables**: Manage configuration

### Health Checks
Your app includes a health check endpoint:
- URL: `/health`
- Railway will monitor this endpoint
- Automatic restarts on failure

## 🔄 Continuous Deployment

### Automatic Deployments
- Railway automatically deploys on every push to main branch
- You can configure branch-specific deployments
- Rollback to previous deployments if needed

### Manual Deployments
- Trigger manual deployments from Railway dashboard
- Deploy specific commits or branches

## 💰 Cost Optimization

### Railway Pricing
- **Free tier**: Limited usage
- **Pro plan**: More resources and features
- **Team plan**: Collaboration features

### Tips to Reduce Costs
1. **Use appropriate instance sizes**
2. **Monitor resource usage**
3. **Use Railway's sleep mode for development**

## 🎉 Success!

Your FastAPI backend is now deployed on Railway using the simple Python runtime!

### Advantages of This Method
- ✅ **Faster builds** - No Docker build process
- ✅ **Simpler configuration** - Less files to manage
- ✅ **Automatic dependency detection** - Railway handles Python packages
- ✅ **Easier debugging** - Direct Python logs
- ✅ **Better resource usage** - No container overhead

### Next Steps
1. **Test all endpoints** thoroughly
2. **Set up monitoring** and alerts
3. **Configure custom domain** if needed
4. **Set up CI/CD** for automated testing

### Useful Links
- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Your App URL]: `https://your-app-name.railway.app` 