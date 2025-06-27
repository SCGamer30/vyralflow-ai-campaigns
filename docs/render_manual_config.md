# Manual Render Configuration Guide

## The Problem Analysis

Based on the logs, Render was:

1. **Ignoring our custom build configuration** - Using default instead of our build script
2. **Using Python 3.13 by default** - Ignoring our runtime.txt file
3. **Trying to compile pydantic from source** - Causing Rust/Cargo compilation errors

## Manual Configuration Required

Since Render isn't reading our config files properly, you need to configure everything manually in the dashboard.

## Step-by-Step Manual Setup

### 1. In Render Dashboard Settings

Go to your service → **Settings** → **Build & Deploy**

#### Build Settings:

- **Build Command**: `pip install --only-binary=:all: --prefer-binary -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Runtime Settings:

- **Python Version**: `3.12.0` (if available, otherwise use default but might need different pydantic version)

### 2. Environment Variables

Go to **Environment** tab and add:

| Key                           | Value                                          | Required                      |
| ----------------------------- | ---------------------------------------------- | ----------------------------- |
| `GOOGLE_CLOUD_PROJECT`        | Your Google Cloud project ID                   | ✅ Yes                        |
| `GEMINI_API_KEY`              | Your Gemini API key                            | ✅ Yes                        |
| `UNSPLASH_ACCESS_KEY`         | Your Unsplash API key                          | ✅ Yes                        |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON content of your service account file | ✅ Yes                        |
| `REDDIT_CLIENT_ID`            | Your Reddit client ID                          | ❌ Optional                   |
| `REDDIT_CLIENT_SECRET`        | Your Reddit client secret                      | ❌ Optional                   |
| `PIP_ONLY_BINARY`             | `:all:`                                        | ✅ Yes (prevents compilation) |
| `PIP_PREFER_BINARY`           | `1`                                            | ✅ Yes (prefers wheels)       |

### 3. Important Notes

#### Google Service Account JSON:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  ...
}
```

Copy the ENTIRE JSON content as the value for `GOOGLE_SERVICE_ACCOUNT_JSON`.

#### Build Command Explanation:

- `--only-binary=:all:` - Forces pip to only use pre-compiled wheels
- `--prefer-binary` - Prefers binary packages over source
- This prevents the pydantic compilation error

### 4. Deploy Process

1. **Push your latest changes**:

   ```bash
   git push origin main
   ```

2. **In Render Dashboard**:

   - Trigger manual deploy: **Manual Deploy** → **Deploy latest commit**
   - Watch logs for successful build

3. **Test the deployment**:
   - Visit: `https://your-backend-url.onrender.com/api/health`
   - Should return: `{"status": "healthy"}`

### 5. Update Frontend

Once backend is live:

1. **Go to Netlify Dashboard** → Your site → **Environment variables**
2. **Add/Update**:
   - `VITE_API_URL` = `https://your-backend-url.onrender.com/api`
3. **Redeploy** Netlify site

### 6. Troubleshooting

#### Build Still Fails?

- Check environment variables are set correctly
- Try adding `PIP_NO_BUILD_ISOLATION=1` environment variable
- Consider using `pip install --no-deps -r requirements.txt` in build command

#### App Crashes on Startup?

- Check logs for missing environment variables
- Verify Google service account JSON is valid
- Ensure API keys are correct

#### Slow First Request?

- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes 10-30 seconds to wake up
- Subsequent requests will be fast

## Alternative: If Manual Config Still Fails

If manual configuration doesn't work, try this minimal approach:

1. **Build Command**: `pip install fastapi==0.95.2 uvicorn pydantic==1.10.13 python-dotenv google-cloud-firestore google-generativeai httpx requests aiohttp pytrends praw structlog`

2. **This avoids**:
   - pydantic v2 compilation issues
   - Complex requirements.txt parsing
   - Version conflicts

The app will still work with these core dependencies!
