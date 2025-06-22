import google.generativeai as genai
from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import json

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeminiService:
    """Service for Google Gemini API interactions."""
    
    def __init__(self):
        """Initialize Gemini client."""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.executor = ThreadPoolExecutor(max_workers=5)
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise ExternalAPIException("gemini", str(e))
    
    async def generate_content(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content using Gemini API."""
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    self.executor,
                    self.model.generate_content,
                    prompt
                )
                
                if response.text:
                    logger.debug(f"Generated content successfully (attempt {attempt + 1})")
                    return response.text.strip()
                else:
                    raise ExternalAPIException("gemini", "Empty response from Gemini API")
                    
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise ExternalAPIException("gemini", f"All attempts failed: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def generate_platform_content(
        self,
        business_name: str,
        industry: str,
        campaign_goal: str,
        platform: str,
        brand_voice: str,
        target_audience: Optional[str] = None,
        trending_topics: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate platform-specific content."""
        
        # Build context
        context_parts = [
            f"Business: {business_name}",
            f"Industry: {industry}",
            f"Campaign Goal: {campaign_goal}",
            f"Platform: {platform}",
            f"Brand Voice: {brand_voice}"
        ]
        
        if target_audience:
            context_parts.append(f"Target Audience: {target_audience}")
        
        if trending_topics:
            context_parts.append(f"Trending Topics: {', '.join(trending_topics[:5])}")
        
        if keywords:
            context_parts.append(f"Keywords: {', '.join(keywords[:10])}")
        
        context = "\n".join(context_parts)
        
        # Platform-specific prompts
        platform_prompts = {
            'instagram': self._get_instagram_prompt(context),
            'twitter': self._get_twitter_prompt(context),
            'linkedin': self._get_linkedin_prompt(context),
            'facebook': self._get_facebook_prompt(context),
            'tiktok': self._get_tiktok_prompt(context)
        }
        
        prompt = platform_prompts.get(platform.lower(), platform_prompts['instagram'])
        
        try:
            content = await self.generate_content(prompt)
            return self._parse_content_response(content, platform)
        except Exception as e:
            logger.error(f"Failed to generate {platform} content: {e}")
            return self._get_fallback_content(platform, business_name, campaign_goal)
    
    def _get_instagram_prompt(self, context: str) -> str:
        """Get Instagram-specific prompt."""
        return f"""
        Create engaging Instagram content based on the following information:
        
        {context}
        
        Generate:
        1. Main post caption (engaging, visual-focused, max 2200 characters)
        2. 5-10 relevant hashtags (mix of popular and niche)
        3. 2 alternative caption variations
        
        Requirements:
        - Use emojis appropriately
        - Include call-to-action
        - Optimize for engagement
        - Match the brand voice
        - Incorporate trending topics naturally
        
        Format your response as JSON:
        {{
            "main_caption": "caption text",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "variations": ["variation 1", "variation 2"]
        }}
        """
    
    def _get_twitter_prompt(self, context: str) -> str:
        """Get Twitter-specific prompt."""
        return f"""
        Create compelling Twitter content based on the following information:
        
        {context}
        
        Generate:
        1. Main tweet (under 280 characters, engaging and shareable)
        2. 3-5 relevant hashtags
        3. 2 alternative tweet variations
        
        Requirements:
        - Concise and punchy
        - Include relevant hashtags
        - Encourage retweets and engagement
        - Match the brand voice
        - Use trending topics appropriately
        
        Format your response as JSON:
        {{
            "main_tweet": "tweet text",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "variations": ["variation 1", "variation 2"]
        }}
        """
    
    def _get_linkedin_prompt(self, context: str) -> str:
        """Get LinkedIn-specific prompt."""
        return f"""
        Create professional LinkedIn content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (professional tone, 1-3 paragraphs, max 3000 characters)
        2. 3-5 relevant hashtags (professional/industry-focused)
        3. 2 alternative post variations
        
        Requirements:
        - Professional and authoritative tone
        - Provide value to professional audience
        - Include industry insights
        - Match the brand voice
        - Encourage professional discussion
        
        Format your response as JSON:
        {{
            "main_post": "post text",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "variations": ["variation 1", "variation 2"]
        }}
        """
    
    def _get_facebook_prompt(self, context: str) -> str:
        """Get Facebook-specific prompt."""
        return f"""
        Create engaging Facebook content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (conversational, community-focused)
        2. 3-5 relevant hashtags
        3. 2 alternative post variations
        
        Requirements:
        - Conversational and community-focused
        - Encourage comments and sharing
        - Match the brand voice
        - Build community connection
        
        Format your response as JSON:
        {{
            "main_post": "post text",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "variations": ["variation 1", "variation 2"]
        }}
        """
    
    def _get_tiktok_prompt(self, context: str) -> str:
        """Get TikTok-specific prompt."""
        return f"""
        Create engaging TikTok content based on the following information:
        
        {context}
        
        Generate:
        1. Main caption (fun, trendy, max 150 characters)
        2. 3-5 trending hashtags
        3. 2 alternative caption variations
        
        Requirements:
        - Fun and trendy tone
        - Use current TikTok language
        - Encourage interaction
        - Match the brand voice while being playful
        
        Format your response as JSON:
        {{
            "main_caption": "caption text",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "variations": ["variation 1", "variation 2"]
        }}
        """
    
    def _parse_content_response(self, content: str, platform: str) -> Dict[str, Any]:
        """Parse the AI response and extract structured content."""
        try:
            # Try to parse as JSON
            if content.strip().startswith('{'):
                data = json.loads(content)
                
                # Standardize keys based on platform
                if platform.lower() == 'twitter':
                    main_text = data.get('main_tweet', data.get('main_caption', ''))
                elif platform.lower() == 'linkedin':
                    main_text = data.get('main_post', data.get('main_caption', ''))
                else:
                    main_text = data.get('main_caption', data.get('main_post', data.get('main_tweet', '')))
                
                return {
                    'text': main_text,
                    'hashtags': data.get('hashtags', []),
                    'variations': data.get('variations', []),
                    'character_count': len(main_text)
                }
            else:
                # Fallback: parse manually
                lines = content.strip().split('\n')
                text = lines[0] if lines else content
                return {
                    'text': text,
                    'hashtags': [],
                    'variations': [],
                    'character_count': len(text)
                }
                
        except Exception as e:
            logger.warning(f"Failed to parse content response: {e}")
            return {
                'text': content[:500],  # Truncate if needed
                'hashtags': [],
                'variations': [],
                'character_count': len(content)
            }
    
    def _get_fallback_content(self, platform: str, business_name: str, campaign_goal: str) -> Dict[str, Any]:
        """Get fallback content when API fails."""
        fallback_content = {
            'instagram': {
                'text': f"🌟 Exciting news from {business_name}! {campaign_goal} #Business #Growth #Innovation",
                'hashtags': ['#Business', '#Growth', '#Innovation'],
                'variations': [
                    f"✨ {business_name} is making moves! {campaign_goal}",
                    f"🚀 Big things happening at {business_name}! {campaign_goal}"
                ]
            },
            'twitter': {
                'text': f"🎯 {business_name}: {campaign_goal[:200]} #Business",
                'hashtags': ['#Business', '#News'],
                'variations': [
                    f"📢 Update from {business_name}: {campaign_goal[:180]}",
                    f"🔥 {business_name} news: {campaign_goal[:190]}"
                ]
            },
            'linkedin': {
                'text': f"We're excited to share that {business_name} is focused on {campaign_goal}. This initiative represents our commitment to innovation and excellence in our industry.",
                'hashtags': ['#Business', '#Innovation', '#Professional'],
                'variations': [
                    f"At {business_name}, we're proud to announce our focus on {campaign_goal}.",
                    f"Professional update: {business_name} is advancing with {campaign_goal}."
                ]
            }
        }
        
        content = fallback_content.get(platform.lower(), fallback_content['instagram'])
        content['character_count'] = len(content['text'])
        
        logger.warning(f"Using fallback content for {platform}")
        return content


# Global service instance
gemini_service = GeminiService()