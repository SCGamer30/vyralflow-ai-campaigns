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
        Create compelling, detailed Instagram content based on the following information:
        
        {context}
        
        Generate:
        1. Main post caption (3-4 sentences minimum, storytelling approach, engaging and visual-focused, max 2200 characters)
        2. 6-7 highly relevant hashtags (mix of popular, niche, and industry-specific)
        3. 2 alternative caption variations (also 3-4 sentences each)
        
        Requirements:
        - Write 3-4 full sentences that tell a story or provide value
        - Use emojis strategically (2-3 per post)
        - Include a strong call-to-action
        - Optimize for maximum engagement and shares
        - Match the brand voice perfectly
        - Incorporate trending topics naturally
        - Make it feel authentic and human
        - Focus on benefits and outcomes
        - Create curiosity and emotion
        
        Format your response as JSON:
        {{
            "main_caption": "detailed caption text with 3-4 sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["detailed variation 1 with 3-4 sentences", "detailed variation 2 with 3-4 sentences"]
        }}
        """
    
    def _get_twitter_prompt(self, context: str) -> str:
        """Get Twitter-specific prompt."""
        return f"""
        Create compelling, detailed Twitter content based on the following information:
        
        {context}
        
        Generate:
        1. Main tweet (2-3 sentences, under 280 characters total, but use most of the space for maximum impact)
        2. 6-7 relevant hashtags (mix of trending, industry, and engagement hashtags)
        3. 2 alternative tweet variations (also 2-3 sentences each)
        
        Requirements:
        - Write 2-3 concise but impactful sentences
        - Include powerful, action-oriented language
        - Create urgency or curiosity
        - Encourage retweets and engagement
        - Match the brand voice perfectly
        - Use trending topics strategically
        - Make it highly shareable
        - Include a clear value proposition
        
        Format your response as JSON:
        {{
            "main_tweet": "detailed tweet text with 2-3 sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["detailed variation 1 with 2-3 sentences", "detailed variation 2 with 2-3 sentences"]
        }}
        """
    
    def _get_linkedin_prompt(self, context: str) -> str:
        """Get LinkedIn-specific prompt."""
        return f"""
        Create detailed, professional LinkedIn content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (professional tone, 2-3 full paragraphs with 4-5 sentences each, max 3000 characters)
        2. 6-7 relevant hashtags (professional, industry-focused, and trending business hashtags)
        3. 2 alternative post variations (also 2-3 paragraphs each)
        
        Requirements:
        - Write 2-3 full paragraphs with substantial content
        - Professional and authoritative tone with personality
        - Provide genuine value and insights to professional audience
        - Include industry trends and business implications
        - Match the brand voice while maintaining professionalism
        - Encourage meaningful professional discussion
        - Share actionable insights or lessons
        - Create thought leadership positioning
        - Use storytelling when appropriate
        
        Format your response as JSON:
        {{
            "main_post": "detailed post text with 2-3 full paragraphs",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["detailed variation 1 with 2-3 paragraphs", "detailed variation 2 with 2-3 paragraphs"]
        }}
        """
    
    def _get_facebook_prompt(self, context: str) -> str:
        """Get Facebook-specific prompt."""
        return f"""
        Create engaging, detailed Facebook content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (conversational, community-focused, 3-4 sentences that create connection)
        2. 6-7 relevant hashtags (community, industry, and engagement-focused)
        3. 2 alternative post variations (also 3-4 sentences each)
        
        Requirements:
        - Write 3-4 sentences that feel conversational and authentic
        - Community-focused and relationship-building tone
        - Encourage comments, shares, and meaningful discussion
        - Match the brand voice while being approachable
        - Build genuine community connection
        - Include relatable experiences or stories
        - Ask engaging questions to drive interaction
        - Create emotional connection with audience
        
        Format your response as JSON:
        {{
            "main_post": "detailed post text with 3-4 sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["detailed variation 1 with 3-4 sentences", "detailed variation 2 with 3-4 sentences"]
        }}
        """
    
    def _get_tiktok_prompt(self, context: str) -> str:
        """Get TikTok-specific prompt."""
        return f"""
        Create engaging, detailed TikTok content based on the following information:
        
        {context}
        
        Generate:
        1. Main caption (fun, trendy, but informative - 2-3 sentences, max 150 characters total)
        2. 6-7 trending hashtags (mix of viral, niche, and industry hashtags)
        3. 2 alternative caption variations (also 2-3 sentences each)
        
        Requirements:
        - Write 2-3 short but impactful sentences
        - Fun and trendy tone that's still informative
        - Use current TikTok language and trends
        - Encourage maximum interaction (comments, shares, saves)
        - Match the brand voice while being playful and authentic
        - Create curiosity and entertainment value
        - Use viral phrases and current slang appropriately
        - Make it highly shareable and memorable
        
        Format your response as JSON:
        {{
            "main_caption": "detailed caption text with 2-3 sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["detailed variation 1 with 2-3 sentences", "detailed variation 2 with 2-3 sentences"]
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
                'text': f"🌟 Exciting news from {business_name}! We're thrilled to share that {campaign_goal} This journey represents everything we've been working toward, and we can't wait to see the impact it will have on our community. Join us as we take this bold step forward and revolutionize the way we serve you. What do you think about this exciting development? 💫",
                'hashtags': ['#Business', '#Growth', '#Innovation', '#Community', '#Exciting', '#Future', '#Success'],
                'variations': [
                    f"✨ {business_name} is making incredible moves! Our latest initiative focuses on {campaign_goal} We've put our hearts into this project, and we're confident it will transform how we connect with you. This is just the beginning of an amazing journey together. Ready to be part of something special?",
                    f"🚀 Big things are happening at {business_name}! We're proud to announce that {campaign_goal} Our team has worked tirelessly to bring you something truly remarkable. This milestone marks a new chapter in our story, and we want you to be part of every moment. Let's make magic happen together!"
                ]
            },
            'twitter': {
                'text': f"🎯 Game-changer alert! {business_name} is revolutionizing everything with our focus on {campaign_goal[:150]} This isn't just an update – it's the future happening now. Ready to join the revolution? 🚀",
                'hashtags': ['#Business', '#Innovation', '#Future', '#Revolutionary', '#GameChanger', '#Success', '#Trending'],
                'variations': [
                    f"📢 Breaking: {business_name} just announced something incredible! Our mission to {campaign_goal[:120]} is reshaping the industry. This is what innovation looks like. Are you ready for what's next?",
                    f"🔥 {business_name} is redefining excellence! Our commitment to {campaign_goal[:130]} proves that bold vision creates real change. The future starts today, and we're leading the way."
                ]
            },
            'linkedin': {
                'text': f"We're excited to share a significant milestone at {business_name}. Our strategic focus on {campaign_goal} represents more than just business evolution – it's our commitment to driving meaningful change in our industry. This initiative reflects months of careful planning, innovative thinking, and dedication to excellence that defines our organization.\n\nAs we embark on this journey, we're not just advancing our mission; we're setting new standards for what's possible. Our team's passion and expertise have brought us to this pivotal moment, and we're confident that the impact will extend far beyond our immediate goals.\n\nWe believe that true success comes from creating value that resonates with our community and drives positive change. This milestone is just the beginning of what we can achieve together.",
                'hashtags': ['#Business', '#Innovation', '#Professional', '#Leadership', '#Excellence', '#Growth', '#Success'],
                'variations': [
                    f"At {business_name}, we're proud to announce a transformative step forward in our mission. Our focus on {campaign_goal} demonstrates our unwavering commitment to innovation and excellence. This strategic initiative represents the culmination of extensive research, collaborative planning, and our team's dedication to creating meaningful impact.",
                    f"Professional milestone: {business_name} is advancing with a groundbreaking approach to {campaign_goal} This initiative showcases our commitment to pushing boundaries and delivering exceptional value. We're excited about the possibilities this opens up for our industry and community."
                ]
            },
            'facebook': {
                'text': f"Hey everyone! 👋 We have some incredible news to share from the {business_name} family! Our exciting journey toward {campaign_goal} is officially underway, and we couldn't be more thrilled to have you all along for the ride. This project means the world to us because it's all about creating something amazing for our community. We've poured our hearts into this, and we can't wait to show you what we've been working on! What are you most excited to see from us? 💙",
                'hashtags': ['#Community', '#Family', '#Exciting', '#Journey', '#Together', '#Amazing', '#HeartProject'],
                'variations': [
                    f"Friends, we're bursting with excitement! 🎉 The amazing team at {business_name} has been working on something really special, and our focus on {campaign_goal} is finally coming to life. This isn't just business for us – it's about creating connections and building something meaningful together with all of you.",
                    f"Community update! 🌟 We're so grateful to share this journey with all of you as {business_name} takes on the exciting challenge of {campaign_goal} Your support and enthusiasm fuel everything we do, and we can't wait to celebrate this milestone together with our amazing community."
                ]
            },
            'tiktok': {
                'text': f"✨ {business_name} just dropped something HUGE! Our mission: {campaign_goal[:80]} This is giving main character energy! 🔥",
                'hashtags': ['#fyp', '#viral', '#business', '#gamechanging', '#maincharacter', '#energy', '#huge'],
                'variations': [
                    f"🚀 Plot twist: {business_name} is about to change everything! {campaign_goal[:90]} This hits different! 💯",
                    f"📈 Business glow-up alert! {business_name} said '{campaign_goal[:85]}' and we're here for it! ✨"
                ]
            }
        }
        
        content = fallback_content.get(platform.lower(), fallback_content['instagram'])
        content['character_count'] = len(content['text'])
        
        logger.warning(f"Using fallback content for {platform}")
        return content


# Global service instance
gemini_service = GeminiService()