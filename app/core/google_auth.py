"""Google Cloud authentication helper for production environments."""
import os
import json
import tempfile
from pathlib import Path
from app.utils.logging import get_logger

logger = get_logger(__name__)


def setup_google_auth():
    """Set up Google authentication from environment variables."""
    # Check if JSON content is provided as environment variable
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if service_account_json:
        try:
            # Create a temporary file to store the credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                # Write the JSON content to the file
                f.write(service_account_json)
                temp_path = f.name
            
            # Set the environment variable to point to this file
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_path
            logger.info("Google authentication configured from JSON content")
            return temp_path
            
        except Exception as e:
            logger.error(f"Failed to set up Google auth from JSON: {e}")
            # Continue without credentials - might work with other auth methods
    
    # Check if credentials path is already set
    elif os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if Path(path).exists():
            logger.info(f"Using existing Google credentials from: {path}")
        else:
            logger.warning(f"Google credentials file not found: {path}")
    
    else:
        logger.warning("No Google credentials configured - will try Application Default Credentials") 