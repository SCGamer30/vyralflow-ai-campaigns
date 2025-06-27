# VyralFlow Deployment Fix Guide

## Issue: "Creating Campaign" Stuck for Other Users

### Problem Identified

The frontend is deployed on Netlify but is hardcoded to connect to `http://localhost:8000/api`, which only works on your local machine. Other users' browsers try to connect to their own localhost, which has no backend server running.

### Solution Options

## Option 1: Deploy Backend to a Cloud Service (Recommended)

### A. Deploy to Render (Free Tier Available)

1. Create account at https://render.com
2. Connect your GitHub repository
3. Create a new Web Service:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Once deployed, you'll get a URL like: `https://your-app.onrender.com`

### B. Deploy to Railway

1. Create account at https://railway.app
2. Connect GitHub and select your repo
3. Add environment variables if needed
4. Railway will auto-detect Python and deploy
5. Get your deployment URL

### C. Deploy to Heroku

1. Create a `Procfile` in root directory:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. Deploy using Heroku CLI or GitHub integration

## Option 2: Use Netlify Functions (Serverless)

This requires rewriting your backend as serverless functions.

## Option 3: Quick Testing Solution

For quick testing with others, you can use ngrok to expose your local backend:

1. Install ngrok: `brew install ngrok` (Mac) or download from ngrok.com
2. Run your backend locally: `python run_server.py`
3. In another terminal: `ngrok http 8000`
4. Use the ngrok URL in your frontend

## Implementing the Fix

### Step 1: Update Frontend Environment Configuration

Create a file `frontend/.env.production` with:

```
VITE_API_URL=https://your-deployed-backend-url/api
```

### Step 2: Update Netlify Environment Variables

1. Go to Netlify Dashboard > Site Settings > Environment Variables
2. Add: `VITE_API_URL` = `https://your-deployed-backend-url/api`
3. Redeploy your site

### Step 3: Configure CORS in Backend

Make sure your backend allows requests from your Netlify domain:

```python
# In app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vyralflowai.shauryac.com",
        "http://localhost:5173",  # for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the Fix

1. Deploy your backend to one of the cloud services
2. Update the VITE_API_URL in Netlify environment variables
3. Redeploy your Netlify site
4. Test from different devices/networks

## Important Notes

- The backend MUST be publicly accessible for other users to use the app
- Ensure all API keys and secrets are properly configured in the deployed backend
- Monitor your backend logs for any errors
- Consider adding rate limiting for production use
