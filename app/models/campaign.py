from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    """Campaign status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Agent execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


class BrandVoice(str, Enum):
    """Brand voice options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    AUTHORITATIVE = "authoritative"
    INSPIRATIONAL = "inspirational"


class SupportedPlatform(str, Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"


class CampaignRequest(BaseModel):
    """Request model for creating a new campaign."""
    
    business_name: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Name of the business or brand"
    )
    industry: str = Field(
        ..., 
        min_length=1,
        max_length=50,
        description="Industry or business category"
    )
    campaign_goal: str = Field(
        ..., 
        min_length=10, 
        max_length=500,
        description="Main goal or objective of the campaign"
    )
    target_platforms: List[SupportedPlatform] = Field(
        ..., 
        min_items=1,
        description="List of target social media platforms"
    )
    brand_voice: BrandVoice = Field(
        default=BrandVoice.PROFESSIONAL,
        description="Brand voice and tone"
    )
    target_audience: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Target audience description"
    )
    keywords: Optional[List[str]] = Field(
        default=None,
        description="Relevant keywords for the campaign"
    )
    
    @validator('keywords')
    def validate_keywords(cls, v):
        if v and len(v) > 20:
            raise ValueError("Maximum 20 keywords allowed")
        return v
    
    @validator('target_platforms')
    def validate_platforms(cls, v):
        if len(v) > 5:
            raise ValueError("Maximum 5 platforms allowed")
        return list(set(v))  # Remove duplicates


class AgentProgress(BaseModel):
    """Model for tracking agent execution progress."""
    
    agent_name: str = Field(..., description="Name of the agent")
    status: AgentStatus = Field(default=AgentStatus.PENDING, description="Current status")
    progress_percentage: int = Field(
        default=0, 
        ge=0, 
        le=100,
        description="Progress percentage (0-100)"
    )
    message: str = Field(default="", description="Status message")
    started_at: Optional[datetime] = Field(default=None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    error_details: Optional[str] = Field(default=None, description="Error details if failed")


class TrendingTopic(BaseModel):
    """Trending topic with relevance score and type."""
    
    topic: str
    relevance_score: int = Field(default=0, ge=0, le=100)
    trend_type: str = Field(default="stable")


class TrendAnalysisResult(BaseModel):
    """Results from trend analysis agent."""
    
    trending_topics: List[TrendingTopic] = Field(default_factory=list)
    trending_hashtags: List[str] = Field(default_factory=list)
    analysis_summary: str = Field(default="")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    data_sources: List[str] = Field(default_factory=list)
    viral_probability: str = Field(default="0%")
    peak_engagement_window: str = Field(default="Not available")


class ContentVariation(BaseModel):
    """Content variation for a platform."""
    
    text: str
    hashtags: List[str] = Field(default_factory=list)
    character_count: int
    engagement_score: float = Field(default=0.0, ge=0.0, le=1.0)


class PlatformContent(BaseModel):
    """Content generated for a specific platform."""
    
    text: str
    hashtags: List[str] = Field(default_factory=list)
    character_count: int
    variations: List[ContentVariation] = Field(default_factory=list)


class ContentResult(BaseModel):
    """Results from content writer agent."""
    
    instagram: Optional[PlatformContent] = None
    twitter: Optional[PlatformContent] = None
    linkedin: Optional[PlatformContent] = None
    facebook: Optional[PlatformContent] = None


class ImageSuggestion(BaseModel):
    """Image suggestion from visual designer."""
    
    url: str
    description: str
    tags: List[str] = Field(default_factory=list)
    photographer: Optional[str] = None
    source: str = "unsplash"


class VisualResult(BaseModel):
    """Results from visual designer agent."""
    
    recommended_style: str = Field(default="")
    image_suggestions: List[ImageSuggestion] = Field(default_factory=list)
    color_palette: List[str] = Field(default_factory=list)
    visual_themes: List[str] = Field(default_factory=list)


class PlatformSchedule(BaseModel):
    """Scheduling recommendations for a platform."""
    
    optimal_times: List[str] = Field(default_factory=list)
    best_days: List[str] = Field(default_factory=list)
    posting_frequency: str = Field(default="")


class ScheduleResult(BaseModel):
    """Results from campaign scheduler agent."""
    
    instagram: Optional[PlatformSchedule] = None
    twitter: Optional[PlatformSchedule] = None
    linkedin: Optional[PlatformSchedule] = None
    facebook: Optional[PlatformSchedule] = None
    posting_sequence: List[Dict[str, Any]] = Field(default_factory=list)


class PerformancePredictions(BaseModel):
    """Performance predictions for the campaign."""
    
    viral_probability: str = Field(default="0%")
    estimated_reach: str = Field(default="0")
    engagement_rate: str = Field(default="0%")
    roi_prediction: str = Field(default="0%")
    confidence_score: float = Field(default=0.0, ge=0.0, le=100.0)
    metrics_breakdown: Dict[str, str] = Field(
        default_factory=lambda: {
            "likes_estimate": "0",
            "shares_estimate": "0",
            "comments_estimate": "0",
            "impressions_estimate": "0"
        }
    )


class CampaignResults(BaseModel):
    """Complete campaign results from all agents."""
    
    trends: Optional[Dict[str, Any]] = None
    content: Optional[ContentResult] = None
    visuals: Optional[VisualResult] = None
    schedule: Optional[ScheduleResult] = None
    performance_predictions: Optional[PerformancePredictions] = None


class CampaignResponse(BaseModel):
    """Response model for campaign operations."""
    
    campaign_id: str
    status: CampaignStatus
    agent_progress: List[AgentProgress] = Field(default_factory=list)
    results: Optional[CampaignResults] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class CampaignListResponse(BaseModel):
    """Response model for listing campaigns."""
    
    campaigns: List[CampaignResponse]
    total_count: int
    page: int = 1
    per_page: int = 10


class CampaignStatusResponse(BaseModel):
    """Response model for campaign status check."""
    
    campaign_id: str
    status: CampaignStatus
    agent_progress: List[AgentProgress]
    current_agent: Optional[str] = None
    estimated_completion: Optional[datetime] = None