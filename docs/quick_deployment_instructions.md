# Quick Fix Instructions - Get Your App Working for Everyone

## The Problem

Your app works for you because your backend runs on YOUR computer at localhost:8000.
Others can't access your localhost - they need a publicly accessible backend.

## Immediate Solution - Deploy Backend to Render (FREE)

### Step 1: Deploy Backend (5 minutes)

1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub account and select your repository
4. Configure:
   - **Name**: vyralflow-backend
   - **Region**: Choose closest to you
   - **Branch**: main
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

### Step 2: Add Environment Variables in Render

After deployment starts, go to "Environment" tab and add:

- `GOOGLE_CLOUD_PROJECT` = (your project ID)
- `GEMINI_API_KEY` = (your API key)
- `UNSPLASH_ACCESS_KEY` = (your API key)
- `GOOGLE_APPLICATION_CREDENTIALS` = (path to credentials if needed)

### Step 3: Get Your Backend URL

Once deployed (takes ~5 minutes), you'll get a URL like:
`https://vyralflow-backend.onrender.com`

### Step 4: Update Netlify Frontend

1. Go to your Netlify dashboard
2. Site Configuration → Environment Variables
3. Add: `VITE_API_URL` = `https://vyralflow-backend.onrender.com/api`
4. Trigger a redeploy (Site Overview → Trigger Deploy → Deploy Site)

## Alternative: Quick Testing with ngrok (Temporary)

If you need to test RIGHT NOW:

1. Keep your backend running locally
2. Install ngrok: https://ngrok.com/download
3. Run: `ngrok http 8000`
4. Copy the HTTPS URL (like `https://abc123.ngrok.io`)
5. Update Netlify env var: `VITE_API_URL` = `https://abc123.ngrok.io/api`
6. Redeploy Netlify

**Note**: ngrok URLs expire and change each time, so this is only for testing!

## Verification

After deployment:

1. Visit `https://your-backend.onrender.com/api/health` - should show {"status": "healthy"}
2. Try creating a campaign from any device
3. Check backend logs in Render dashboard if issues persist

## Common Issues

- **Still stuck?** Check Render logs for missing environment variables
- **CORS errors?** Your backend already allows all origins, so this shouldn't be an issue
- **Timeout?** Render free tier sleeps after inactivity - first request may be slow
