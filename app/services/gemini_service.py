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
            self.model = genai.GenerativeModel('gemini-1.5-flash')
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
            'facebook': self._get_facebook_prompt(context)
        }
        
        prompt = platform_prompts.get(platform.lower(), platform_prompts['instagram'])
        
        try:
            # Generate content and hashtags separately for better quality
            content = await self.generate_content(prompt)
            parsed_content = self._parse_content_response(content, platform)
            
            # Generate AI-powered hashtags
            ai_hashtags = await self.generate_hashtags(
                business_name=business_name,
                industry=industry,
                campaign_goal=campaign_goal,
                platform=platform,
                brand_voice=brand_voice,
                target_audience=target_audience,
                trending_topics=trending_topics,
                keywords=keywords
            )
            
            # Replace hashtags with AI-generated ones if we got them
            if ai_hashtags and len(ai_hashtags) > 0:
                parsed_content['hashtags'] = ai_hashtags[:15]  # Use up to 15 AI hashtags
                logger.info(f"Generated {len(ai_hashtags)} AI-powered hashtags for {platform}")
            
            return parsed_content
        except Exception as e:
            logger.error(f"Failed to generate {platform} content: {e}")
            return self._get_fallback_content(platform, business_name, campaign_goal)
    
    async def generate_hashtags(
        self,
        business_name: str,
        industry: str,
        campaign_goal: str,
        platform: str,
        brand_voice: str,
        target_audience: Optional[str] = None,
        trending_topics: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None
    ) -> List[str]:
        """Generate relevant and creative hashtags using Gemini AI."""
        
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
        
        prompt = f"""
        Generate a list of 15-20 highly relevant and creative hashtags for a social media post.
        
        {context}
        
        Requirements:
        - Include a mix of popular, niche, and industry-specific hashtags.
        - Ensure hashtags are relevant to the campaign goal and target audience.
        - Do not include the # symbol in the output.
        
        Format your response as a JSON list of strings:
        [
            "hashtag1",
            "hashtag2",
            "hashtag3"
        ]
        """
        
        try:
            content = await self.generate_content(prompt)
            hashtags = json.loads(content)
            return [f"#{tag}" for tag in hashtags]
        except Exception as e:
            logger.error(f"Failed to generate hashtags: {e}")
            return []
    
    def _get_instagram_prompt(self, context: str) -> str:
        """Get Instagram-specific prompt."""
        return f"""
        Create compelling, detailed Instagram content based on the following information:
        
        {context}
        
        Generate:
        1. Main post caption (8-12 sentences minimum, detailed storytelling approach, engaging and visual-focused, 800-1500 characters)
        2. 10-15 highly relevant hashtags (mix of popular, niche, and industry-specific)
        3. 3 alternative caption variations (also 8-12 sentences each)
        
        Requirements:
        - Write 8-12 full sentences that tell a compelling, detailed story or provide significant value
        - Use emojis strategically (5-8 per post) for visual appeal and engagement
        - Include a strong, compelling call-to-action that drives specific action
        - Create much longer, more engaging content that encourages meaningful interaction
        - Match the brand voice perfectly with authentic personality
        - Incorporate trending topics naturally throughout the narrative
        - Make it feel authentic, human, relatable, and conversational
        - Focus on benefits, outcomes, emotional connection, and personal experiences
        - Create curiosity, emotion, anticipation, and desire to engage
        - Include specific details about the business, campaign, and unique value proposition
        - Add storytelling elements like personal anecdotes, behind-the-scenes insights, or customer stories
        - Use conversation starters and questions to encourage comments
        - Include industry insights, tips, or valuable information
        
        CRITICAL: DO NOT MENTION:
        - AI, artificial intelligence, automation, or technology tools
        - Building solutions, coding, or tech development
        - "Journey to darkness" or overly dramatic language
        - Any reference to using technology to create content
        
        Format your response as JSON:
        {{
            "main_caption": "detailed caption text with 8-12 sentences including emojis, storytelling, and specific business details",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7", "#hashtag8", "#hashtag9", "#hashtag10", "#hashtag11", "#hashtag12", "#hashtag13", "#hashtag14", "#hashtag15"],
            "variations": ["detailed variation 1 with 8-12 sentences", "detailed variation 2 with 8-12 sentences", "detailed variation 3 with 8-12 sentences"]
        }}
        """
    
    def _get_twitter_prompt(self, context: str) -> str:
        """Get Twitter-specific prompt."""
        return f"""
        Create compelling, detailed Twitter content based on the following information:
        
        {context}
        
        Generate:
        1. Main tweet (2-4 sentences, USE FULL 280 characters for maximum impact and engagement)
        2. 8-10 relevant hashtags (mix of trending, industry, and engagement hashtags)
        3. 3 alternative tweet variations (also 2-4 sentences each, utilizing full character limit)
        
        Requirements:
        - Write 2-4 concise but highly impactful sentences that use most of the 280 character limit
        - Include powerful, action-oriented language that drives engagement
        - Create urgency, curiosity, or strong emotional hooks
        - Encourage retweets, replies, and meaningful engagement
        - Match the brand voice perfectly with authentic personality
        - Use trending topics and current events strategically
        - Make it highly shareable with quotable, memorable phrases
        - Include a clear, compelling value proposition or call-to-action
        - Add conversation starters or thought-provoking questions
        - Use strategic emojis (2-3) to increase engagement and visual appeal
        - Include industry insights, tips, or valuable information
        - Create content that begs for responses and discussion
        
        CRITICAL: DO NOT MENTION:
        - AI, artificial intelligence, automation, or technology tools
        - Building solutions, coding, or tech development
        - "Journey to darkness" or overly dramatic language
        - Any reference to using technology to create content
        
        Format your response as JSON:
        {{
            "main_tweet": "impactful tweet text with 2-4 sentences using full character limit for maximum engagement",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7", "#hashtag8", "#hashtag9", "#hashtag10"],
            "variations": ["detailed variation 1 with 2-4 sentences", "detailed variation 2 with 2-4 sentences", "detailed variation 3 with 2-4 sentences"]
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
        
        CRITICAL: DO NOT MENTION:
        - AI, artificial intelligence, automation, or technology tools
        - Building solutions, coding, or tech development
        - "Journey to darkness" or overly dramatic language
        - Any reference to using technology to create content
        
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
        
        CRITICAL: DO NOT MENTION:
        - AI, artificial intelligence, automation, or technology tools
        - Building solutions, coding, or tech development
        - "Journey to darkness" or overly dramatic language
        - Any reference to using technology to create content
        
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
        
        CRITICAL: DO NOT MENTION:
        - AI, artificial intelligence, automation, or technology tools
        - Building solutions, coding, or tech development
        - "Journey to darkness" or overly dramatic language
        - Any reference to using technology to create content
        
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
            # Clean content - remove markdown code blocks
            cleaned_content = content.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_content.startswith('```json'):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith('```'):
                cleaned_content = cleaned_content[3:]
            
            if cleaned_content.endswith('```'):
                cleaned_content = cleaned_content[:-3]
            
            cleaned_content = cleaned_content.strip()
            
            # Try to parse as JSON
            if cleaned_content.startswith('{'):
                data = json.loads(cleaned_content)
                
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
                lines = cleaned_content.split('\n')
                text = lines[0] if lines else cleaned_content
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
    
    async def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic and exponential backoff."""
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    self.executor,
                    self.model.generate_content,
                    prompt
                )
                
                if response and response.text and len(response.text.strip()) > 10:
                    logger.debug(f"AI generation successful on attempt {attempt + 1}")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty or short response on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        logger.error("All generation attempts failed")
        return None
    
    def _get_fallback_content(self, platform: str, business_name: str, campaign_goal: str) -> Dict[str, Any]:
        """Get fallback content when API fails."""
        import random
        import time
        
        # Add randomness to make each fallback unique
        timestamp = int(time.time())
        random.seed(timestamp + hash(business_name + campaign_goal))
        
        # Dynamic content variations
        action_words = random.choice(['revolutionizing', 'transforming', 'innovating', 'advancing', 'pioneering'])
        impact_words = random.choice(['incredible', 'amazing', 'outstanding', 'remarkable', 'extraordinary'])
        future_words = random.choice(['future', 'tomorrow', 'next chapter', 'new era', 'evolution'])
        emoji_sets = [['🌟', '✨', '💫'], ['🚀', '🔥', '⚡'], ['💡', '🎯', '🏆'], ['🌈', '🎉', '💪']]
        emojis = random.choice(emoji_sets)
        
        fallback_content = {
            'instagram': {
                'text': f"{emojis[0]} {impact_words.title()} news from {business_name}! We're {action_words} the way we approach {campaign_goal}. This journey represents months of dedication and innovation, and we're excited to share the results with our community. Join us as we step into the {future_words} and redefine what's possible. What excites you most about this development? {emojis[1]}",
                'hashtags': ['#Business', '#Growth', '#Innovation', '#Community', f'#{action_words.title()}', f'#{future_words.replace(" ", "")}', '#Success'],
                'variations': [
                    f"{emojis[1]} {business_name} is making {impact_words} progress! Our focus on {campaign_goal} represents our commitment to excellence and innovation. We've invested our passion into this project, and we believe it will create meaningful change. This is just the beginning of an exciting journey ahead. Ready to experience something special?",
                    f"{emojis[2]} Big developments at {business_name}! We're thrilled to share our work on {campaign_goal}. Our team has dedicated countless hours to creating something truly valuable for you. This milestone opens up new possibilities and strengthens our mission. Let's build the {future_words} together!"
                ]
            },
            'twitter': {
                'text': f"{emojis[0]} {impact_words.title()} developments! {business_name} is {action_words} our approach to {campaign_goal[:120]}. This represents genuine innovation and commitment to excellence. The {future_words} starts here. Ready to be part of it? {emojis[1]}",
                'hashtags': ['#Business', '#Innovation', f'#{future_words.replace(" ", "")}', f'#{action_words.title()}', f'#{impact_words.title()}', '#Success', '#Trending'],
                'variations': [
                    f"{emojis[1]} Major update: {business_name} unveils {impact_words} progress! Our dedication to {campaign_goal[:100]} is creating real impact in the industry. This is what authentic innovation looks like. What's your take on this development?",
                    f"{emojis[2]} {business_name} is setting new standards! Our work on {campaign_goal[:110]} demonstrates how vision becomes reality. Bold moves create lasting change. The {future_words} is being written today."
                ]
            },
            'linkedin': {
                'text': f"We're pleased to announce {impact_words} progress at {business_name}. Our strategic approach to {campaign_goal} reflects our commitment to {action_words} industry standards and creating meaningful value. This initiative represents extensive research, collaborative planning, and our team's dedication to excellence.\n\nAs we move forward, we're not just advancing our mission – we're establishing new benchmarks for success in our field. Our team's expertise and innovative thinking have positioned us at this pivotal moment, and we're confident the impact will benefit our entire professional community.\n\nWe believe sustainable success comes from creating authentic value and fostering positive industry evolution. This development marks an important step in our continued growth and commitment to professional excellence.",
                'hashtags': ['#Business', '#Innovation', '#Professional', '#Leadership', '#Excellence', f'#{action_words.title()}', '#Success'],
                'variations': [
                    f"At {business_name}, we're announcing a significant advancement in our professional journey. Our focus on {campaign_goal} demonstrates our commitment to innovation and industry leadership. This strategic initiative combines extensive research with practical application, showcasing our dedication to meaningful impact.",
                    f"Professional update: {business_name} continues {action_words} our industry with a comprehensive approach to {campaign_goal}. This initiative highlights our commitment to excellence and our vision for creating lasting value in the professional community."
                ]
            },
            'facebook': {
                'text': f"Hello everyone! {emojis[0]} We have {impact_words} news to share from the {business_name} team! Our journey with {campaign_goal} is gaining momentum, and we're excited to have you be part of this adventure. This project represents our commitment to creating value for our community. We've invested our passion and expertise into this initiative, and we're eager to share the results with you! What aspect interests you most? {emojis[1]}",
                'hashtags': ['#Community', '#Team', f'#{impact_words.title()}', '#Journey', '#Together', f'#{action_words.title()}', '#Growth'],
                'variations': [
                    f"Community update! {emojis[1]} The dedicated team at {business_name} has been {action_words} our approach to {campaign_goal}, and we're thrilled to share this progress with you. This represents months of hard work and innovation, and we believe it will create meaningful value for everyone involved.",
                    f"Friends and supporters! {emojis[2]} We're grateful to share this milestone as {business_name} advances with {campaign_goal}. Your engagement and support inspire everything we do, and we're excited to celebrate this achievement together with our {impact_words} community."
                ]
            },
            'tiktok': {
                'text': f"{emojis[0]} {business_name} just announced something {impact_words}! Our focus: {campaign_goal[:70]}. This energy is unmatched! {emojis[1]}",
                'hashtags': ['#fyp', '#viral', '#business', f'#{action_words}', f'#{impact_words}', '#energy', '#announcement'],
                'variations': [
                    f"{emojis[1]} Major moves: {business_name} is {action_words} everything! {campaign_goal[:80]}. The vibes are {impact_words}! {emojis[2]}",
                    f"{emojis[2]} Success story: {business_name} said '{campaign_goal[:75]}' and delivered! This hits different! {emojis[0]}"
                ]
            }
        }
        
        content = fallback_content.get(platform.lower(), fallback_content['instagram'])
        content['character_count'] = len(content['text'])
        
        logger.warning(f"Using fallback content for {platform}")
        return content


# Global service instance
gemini_service = GeminiService()