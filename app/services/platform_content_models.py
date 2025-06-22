#!/usr/bin/env python3
"""
Platform-Specific Content Models for Vyralflow AI
Advanced content formats for Instagram, Twitter, LinkedIn, and TikTok
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class InstagramStorySlide(BaseModel):
    """Individual Instagram Story slide"""
    slide_number: int
    text_overlay: str
    background_suggestion: str
    stickers: List[str]
    call_to_action: Optional[str] = None
    duration: str = "5 seconds"
    
class TwitterThreadTweet(BaseModel):
    """Individual tweet in a Twitter thread"""
    tweet_number: int
    text: str
    hashtags: List[str]
    character_count: int
    thread_purpose: str  # "hook", "explanation", "value", "cta", "closing"
    engagement_hooks: List[str]

class LinkedInArticleSection(BaseModel):
    """Section of a LinkedIn article"""
    section_type: str  # "intro", "body", "conclusion", "key_insights"
    heading: str
    content: str
    word_count: int
    key_points: List[str]

class TikTokConcept(BaseModel):
    """TikTok video concept and script"""
    hook: str  # First 3 seconds
    script_outline: List[str]
    trending_sounds: List[str]
    hashtags: List[str]
    video_duration: str
    transitions: List[str]
    call_to_action: str

class PlatformContentAdvanced(BaseModel):
    """Advanced platform-specific content with all formats"""
    # Base content (existing)
    text: str
    hashtags: List[str]
    character_count: int
    platform: str
    
    # Platform-specific advanced formats
    instagram_stories: Optional[List[InstagramStorySlide]] = None
    twitter_thread: Optional[List[TwitterThreadTweet]] = None
    linkedin_article: Optional[List[LinkedInArticleSection]] = None
    tiktok_concept: Optional[TikTokConcept] = None
    
    # Enhanced metadata
    content_pillars: List[str] = []
    engagement_tactics: List[str] = []
    viral_elements: List[str] = []
    target_metrics: Dict[str, str] = {}
    optimal_posting_time: Optional[str] = None

class ContentGenerationContext(BaseModel):
    """Context for generating platform-specific content"""
    business_name: str
    industry: str
    campaign_goal: str
    brand_voice: str
    target_audience: str
    trending_topics: List[str]
    trending_hashtags: List[str]
    platform: str
    content_type: str  # "post", "story", "thread", "article", "video"

class AdvancedContentResponse(BaseModel):
    """Complete response with all platform content"""
    campaign_id: str
    platform_content: Dict[str, PlatformContentAdvanced]
    content_strategy: Dict[str, Any]
    cross_platform_synergy: List[str]
    content_calendar_suggestions: List[str]
    performance_predictions: Dict[str, Any]