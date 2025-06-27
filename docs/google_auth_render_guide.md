# Google Cloud Authentication on Render

## How to Set Up Google Service Account on Render

### Option 1: Using Service Account JSON Content (Recommended)

1. **Get your Service Account JSON file**:

   - Open your service account JSON file in a text editor
   - Copy the ENTIRE content (it should start with `{` and end with `}`)

2. **In Render Dashboard**:

   - Go to your service → Environment
   - Add a new environment variable:
     - **Key**: `GOOGLE_SERVICE_ACCOUNT_JSON`
     - **Value**: Paste the entire JSON content

   Example of what to paste:

   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "...",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "..."
   }
   ```

3. **Also add your Google Cloud Project ID**:
   - **Key**: `GOOGLE_CLOUD_PROJECT`
   - **Value**: Your project ID (e.g., `my-project-123456`)

### Option 2: Without Service Account (Less Secure)

If you want to try without authentication (NOT recommended for production):

1. Make sure your Firestore database has public read/write rules (INSECURE!)
2. Only add `GOOGLE_CLOUD_PROJECT` environment variable

### Important Notes:

- **DO NOT** add `GOOGLE_APPLICATION_CREDENTIALS` with a file path - it won't work on Render
- The app will automatically create a temporary credentials file from the JSON content
- Make sure the service account has these permissions:
  - Firestore User or Firestore Admin
  - Cloud Datastore User (if using Datastore mode)

### Troubleshooting:

If you get authentication errors:

1. Check Render logs for specific error messages
2. Verify the JSON is valid (no extra quotes or escaped characters)
3. Ensure the service account has the right permissions in Google Cloud Console
4. Try regenerating the service account key if needed

### Security Best Practices:

1. Use a service account with minimal permissions
2. Rotate keys regularly
3. Consider using Workload Identity Federation for production
4. Never commit service account keys to Git
