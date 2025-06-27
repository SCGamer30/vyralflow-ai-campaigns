from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }
    
    # App Configuration
    app_name: str = Field(default="Vyralflow AI", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    version: str = "1.0.0"
    
    # Google Cloud Configuration
    google_cloud_project: str = Field(..., env="GOOGLE_CLOUD_PROJECT")
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # AI APIs
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    
    # Image APIs
    unsplash_access_key: str = Field(..., env="UNSPLASH_ACCESS_KEY")
    
    # Reddit API (optional)
    reddit_client_id: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    reddit_client_secret: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(
        default="VyralflowAI/1.0 by VyralflowTeam", env="REDDIT_USER_AGENT"
    )
    
    # Database
    firestore_collection_campaigns: str = "campaigns"
    firestore_collection_agent_progress: str = "agent_progress"
    
    # API Configuration
    api_v1_prefix: str = "/api"
    cors_origins: list = ["*"]  # Configure for production
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_requests_per_hour: int = 1000
    
    # External API Timeouts
    external_api_timeout: int = 30
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._setup_google_credentials()
    
    def _setup_google_credentials(self):
        """Set up Google Cloud credentials."""
        if self.google_application_credentials:
            credentials_path = Path(self.google_application_credentials)
            if credentials_path.exists():
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(credentials_path.absolute())
            else:
                print(f"Warning: Google credentials file not found: {credentials_path}")
        
    def validate_required_keys(self) -> list:
        """Validate that required API keys are present."""
        missing_keys = []
        
        if not self.google_cloud_project:
            missing_keys.append("GOOGLE_CLOUD_PROJECT")
        
        if not self.gemini_api_key:
            missing_keys.append("GEMINI_API_KEY")
        
        if not self.unsplash_access_key:
            missing_keys.append("UNSPLASH_ACCESS_KEY")
        
        return missing_keys


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings