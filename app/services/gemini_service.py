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
        Create authentic, engaging Instagram content based on the following information:
        
        {context}
        
        Generate:
        1. Main post caption (8-12 sentences, natural storytelling approach, engaging and visual-focused, 800-1500 characters)
        2. 10-15 highly relevant hashtags (mix of popular, niche, and industry-specific)
        3. 3 alternative caption variations (also 8-12 sentences each)
        
        Requirements:
        - Write naturally like a real person would, not like marketing copy
        - Use authentic, conversational language that sounds human
        - Avoid hyperbolic words like "revolutionizing", "transforming", "incredible", "amazing", "game-changing"
        - Instead use natural expressions like "excited to share", "working on", "proud of", "passionate about"
        - Share genuine experiences, insights, or behind-the-scenes moments
        - Use specific, concrete details rather than vague claims
        - Make it relatable and down-to-earth, not overly promotional
        - Include honest perspectives and real challenges when appropriate
        - Focus on the actual value or benefit to customers, not grandiose claims
        - Use emojis naturally (3-5 per post) where they feel authentic
        - Include genuine questions that spark real conversations
        - Match the brand voice while staying authentic and human
        
        AVOID:
        - Overusing superlatives (amazing, incredible, revolutionary, game-changing)
        - Generic marketing speak ("We're thrilled to announce", "Proud to present")
        - Claims about "revolutionizing" or "transforming" entire industries
        - Overly dramatic language or artificial enthusiasm
        - AI, artificial intelligence, automation references
        - Technical jargon unless it's natural for the industry
        
        INSTEAD USE:
        - Natural expressions like "Here's what we've been working on", "Something we're excited about"
        - Specific details about the actual product/service/experience
        - Real customer benefits without exaggeration
        - Honest, authentic voice that sounds like a real person
        
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
        Create authentic, engaging Twitter content based on the following information:
        
        {context}
        
        Generate:
        1. Main tweet (2-4 sentences, use most of the 280 character limit for impact)
        2. 8-10 relevant hashtags (mix of trending, industry, and engagement hashtags)
        3. 3 alternative tweet variations (also 2-4 sentences each)
        
        Requirements:
        - Write naturally like a real person would tweet, not like corporate marketing
        - Use authentic, conversational language that sounds human
        - Share genuine insights, observations, or experiences
        - Avoid hyperbolic words like "revolutionizing", "transforming", "incredible", "game-changing"
        - Instead use natural expressions like "excited about", "working on", "learned something", "worth sharing"
        - Make it relatable and authentic, not overly promotional
        - Include specific, concrete details rather than vague claims
        - Use emojis naturally (1-3) where they feel authentic
        - Create genuine conversation starters
        - Focus on real value or insights, not grandiose claims
        - Make it shareable because it's genuinely interesting or useful
        
        AVOID:
        - Overusing superlatives (amazing, incredible, revolutionary, game-changing)
        - Generic corporate speak ("We're thrilled to announce", "Proud to unveil")
        - Claims about "revolutionizing" or "transforming" entire industries
        - Overly dramatic language or artificial enthusiasm
        - AI, artificial intelligence, automation references
        - Technical jargon unless natural for the industry
        
        INSTEAD USE:
        - Natural expressions like "Just tried", "Been thinking about", "Here's what I noticed"
        - Specific observations or experiences
        - Real insights without exaggeration
        - Conversational tone that sounds like a real person
        
        Format your response as JSON:
        {{
            "main_tweet": "authentic tweet text with 2-4 sentences using most of the character limit",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7", "#hashtag8", "#hashtag9", "#hashtag10"],
            "variations": ["authentic variation 1 with 2-4 sentences", "authentic variation 2 with 2-4 sentences", "authentic variation 3 with 2-4 sentences"]
        }}
        """
    
    def _get_linkedin_prompt(self, context: str) -> str:
        """Get LinkedIn-specific prompt."""
        return f"""
        Create authentic, professional LinkedIn content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (professional but human tone, 2-3 paragraphs with 4-5 sentences each, max 3000 characters)
        2. 6-7 relevant hashtags (professional, industry-focused, and trending business hashtags)
        3. 2 alternative post variations (also 2-3 paragraphs each)
        
        Requirements:
        - Write professionally but authentically, like a real industry professional would
        - Use natural, conversational business language, not corporate jargon
        - Share genuine insights, experiences, or observations from the industry
        - Avoid hyperbolic words like "revolutionizing", "transforming", "disrupting", "game-changing"
        - Instead use professional but natural expressions like "developing", "improving", "focused on", "passionate about"
        - Provide real value through specific insights, lessons learned, or industry observations
        - Include concrete examples and practical applications
        - Make it relatable to other professionals in the field
        - Focus on actual business challenges and solutions
        - Use storytelling to illustrate points, but keep it grounded and realistic
        - Encourage meaningful professional discussion with thoughtful questions
        
        AVOID:
        - Corporate buzzwords (synergy, leverage, disrupt, paradigm shift)
        - Grandiose claims about "revolutionizing" entire industries
        - Generic professional speak ("We're excited to announce", "Proud to share")
        - Overly promotional language
        - AI, artificial intelligence, automation references unless directly relevant
        - Technical jargon unless it's natural for the specific industry
        
        INSTEAD USE:
        - Natural professional language like "Here's what we've learned", "Something worth considering"
        - Specific industry insights and practical examples
        - Real challenges and thoughtful approaches
        - Authentic professional voice that sounds like a real person
        
        Format your response as JSON:
        {{
            "main_post": "authentic professional post with 2-3 paragraphs",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["authentic variation 1 with 2-3 paragraphs", "authentic variation 2 with 2-3 paragraphs"]
        }}
        """
    
    def _get_facebook_prompt(self, context: str) -> str:
        """Get Facebook-specific prompt."""
        return f"""
        Create authentic, community-focused Facebook content based on the following information:
        
        {context}
        
        Generate:
        1. Main post (conversational, community-focused, 3-4 sentences that create genuine connection)
        2. 6-7 relevant hashtags (community, industry, and engagement-focused)
        3. 2 alternative post variations (also 3-4 sentences each)
        
        Requirements:
        - Write like a real person talking to friends and community members
        - Use warm, conversational language that feels authentic and approachable
        - Share genuine experiences, stories, or behind-the-scenes moments
        - Avoid hyperbolic words like "incredible", "amazing", "revolutionizing", "transforming"
        - Instead use natural expressions like "excited to share", "something we're working on", "proud of"
        - Focus on building real community connections
        - Include relatable experiences that others can connect with
        - Ask genuine questions that spark meaningful conversations
        - Make it feel personal and authentic, not corporate or promotional
        - Share specific details that make the story interesting and relatable
        - Use a tone that's warm, friendly, and inviting
        
        AVOID:
        - Corporate marketing speak ("We're thrilled to announce", "Excited to unveil")
        - Overusing superlatives (amazing, incredible, outstanding, phenomenal)
        - Claims about "revolutionizing" or "transforming" entire industries
        - Overly promotional language
        - AI, artificial intelligence, automation references
        - Generic enthusiasm that doesn't feel genuine
        
        INSTEAD USE:
        - Natural expressions like "Here's something cool we've been up to", "Wanted to share this with you"
        - Personal stories and specific experiences
        - Genuine enthusiasm about real aspects of the business
        - Conversational tone that feels like talking to a friend
        
        Format your response as JSON:
        {{
            "main_post": "authentic, conversational post with 3-4 sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "variations": ["authentic variation 1 with 3-4 sentences", "authentic variation 2 with 3-4 sentences"]
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
        
        # Natural content variations
        action_words = random.choice(['working on', 'developing', 'focused on', 'improving', 'building'])
        impact_words = random.choice(['exciting', 'interesting', 'valuable', 'helpful', 'useful'])
        future_words = random.choice(['ahead', 'coming up', 'next steps', 'moving forward', 'what\'s next'])
        emoji_sets = [['✨', '😊'], ['🌱', '💪'], ['📈', '🎯'], ['🤝', '💼']]
        emojis = random.choice(emoji_sets)
        
        fallback_content = {
            'instagram': {
                'text': f"Hey everyone! {emojis[0]} We've been {action_words} something {impact_words} at {business_name} - our approach to {campaign_goal}. It's been a journey of learning and growth, and we're excited to share what we've discovered with our community. There's still more work {future_words}, but we wanted to give you a behind-the-scenes look at what we're passionate about. What questions do you have about this? {emojis[1]}",
                'hashtags': ['#business', '#growth', '#community', '#passion', '#behindthescenes', '#learning', '#progress'],
                'variations': [
                    f"{emojis[1]} Something we've been passionate about at {business_name}: {campaign_goal}. It's been {impact_words} to see how this has evolved, and we're grateful for the support from our community. Every step teaches us something new about what really matters. What's been your experience with this?",
                    f"Update from the {business_name} team! {emojis[0]} We've been {action_words} {campaign_goal}, and it's been quite the learning experience. There are challenges, but also moments that remind us why we love what we do. Looking forward to sharing more as we continue moving forward."
                ]
            },
            'twitter': {
                'text': f"Been {action_words} something {impact_words} at {business_name} - our approach to {campaign_goal[:120]}. It's been a learning process, but we're excited about where it's headed. {future_words.title()}, we're hoping to share more insights with the community. What are your thoughts? {emojis[0]}",
                'hashtags': ['#business', '#learning', '#community', '#insights', '#progress', '#passion', '#growth'],
                'variations': [
                    f"Quick update from {business_name}: We've been {action_words} {campaign_goal[:100]} and learning a lot along the way. It's {impact_words} to see how each step teaches us something new. What's been your experience with similar challenges?",
                    f"Something we've been passionate about at {business_name}: {campaign_goal[:110]}. There are ups and downs, but that's what makes it real. Looking forward to sharing more about what we've learned. {emojis[1]}"
                ]
            },
            'linkedin': {
                'text': f"We've been {action_words} something {impact_words} at {business_name} - our approach to {campaign_goal}. It's been a process of learning, adapting, and discovering what really works in our industry. The journey has taught us valuable lessons about collaboration, patience, and staying focused on what matters most to our clients.\n\nWhat we've found particularly rewarding is how this work has brought our team together and helped us better understand the challenges our customers face. Each step forward has been earned through honest effort and genuine commitment to improvement.\n\nLooking {future_words}, we're excited to continue this work and share what we learn along the way. The real measure of success isn't just in what we achieve, but in how we can help others in our industry grow as well.",
                'hashtags': ['#business', '#learning', '#teamwork', '#growth', '#industry', '#collaboration', '#progress'],
                'variations': [
                    f"Here's what we've been {action_words} at {business_name}: {campaign_goal}. It's been an {impact_words} learning experience that's taught us a lot about our industry and ourselves. The process has been as valuable as the outcomes, and we're grateful for the insights gained along the way.",
                    f"Professional update from {business_name}: Our focus on {campaign_goal} has been both challenging and rewarding. We've learned that sustainable progress comes from consistent effort, honest evaluation, and staying connected to what our industry really needs."
                ]
            },
            'facebook': {
                'text': f"Hey everyone! {emojis[0]} Wanted to share something we've been {action_words} at {business_name} - our approach to {campaign_goal}. It's been quite the journey, with lots of learning moments and a few surprises along the way. We're grateful for this community and the support you've shown us. What's been your experience with similar challenges? {emojis[1]}",
                'hashtags': ['#community', '#learning', '#grateful', '#journey', '#support', '#growth', '#teamwork'],
                'variations': [
                    f"Quick update from our team! {emojis[1]} We've been {action_words} {campaign_goal}, and it's been both challenging and rewarding. There are days when everything clicks, and others when we're back to the drawing board - but that's what makes it real. Thanks for being part of this journey with us.",
                    f"Something we wanted to share with our community: We've been passionate about {campaign_goal} at {business_name}, and while it's not always easy, it's been {impact_words} to see how much we've learned. Your encouragement means more than you know! {emojis[0]}"
                ]
            },
            'tiktok': {
                'text': f"POV: {action_words} something {impact_words} at {business_name} {emojis[0]} Our focus: {campaign_goal[:70]}. The process has been wild but worth it! {emojis[1]}",
                'hashtags': ['#fyp', '#business', '#learning', '#process', '#growth', '#passionate', '#real'],
                'variations': [
                    f"When you're {action_words} {campaign_goal[:80]} and it's actually {impact_words} {emojis[1]} The {business_name} journey continues!",
                    f"That feeling when you're passionate about {campaign_goal[:75]} at {business_name} {emojis[0]} It's been a process but we're here for it!"
                ]
            }
        }
        
        content = fallback_content.get(platform.lower(), fallback_content['instagram'])
        content['character_count'] = len(content['text'])
        
        logger.warning(f"Using fallback content for {platform}")
        return content


# Global service instance
gemini_service = GeminiService()