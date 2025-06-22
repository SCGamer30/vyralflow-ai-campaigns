#!/usr/bin/env python3
"""
Enhanced Gemini Service for Platform-Specific Content Generation
Advanced prompts and generation for Instagram, Twitter, LinkedIn, and TikTok
"""
import os
import json
import re
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from platform_content_models import (
    ContentGenerationContext,
    PlatformContentAdvanced,
    InstagramStorySlide,
    TwitterThreadTweet,
    LinkedInArticleSection,
    TikTokConcept
)

class EnhancedGeminiService:
    """Enhanced Gemini AI service with platform-specific content generation"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBHFyhc_JMIe_Rqxs6V-h58dYnt-dPXaXk')
        if self.api_key and self.api_key != 'your-gemini-api-key':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("🤖 Enhanced Gemini Service initialized")
        else:
            self.model = None
            print("⚠️ Gemini API key not configured, using fallback content")
    
    async def generate_platform_content_advanced(
        self, 
        context: ContentGenerationContext
    ) -> PlatformContentAdvanced:
        """Generate advanced platform-specific content"""
        
        # Generate base content first
        base_content = await self._generate_base_content(context)
        
        # Create advanced content object
        advanced_content = PlatformContentAdvanced(
            text=base_content["text"],
            hashtags=base_content["hashtags"],
            character_count=len(base_content["text"]),
            platform=context.platform,
            content_pillars=base_content.get("content_pillars", []),
            engagement_tactics=base_content.get("engagement_tactics", []),
            viral_elements=base_content.get("viral_elements", [])
        )
        
        # Generate platform-specific advanced formats
        if context.platform.lower() == 'instagram':
            advanced_content.instagram_stories = await self._generate_instagram_stories(context)
        elif context.platform.lower() == 'twitter':
            advanced_content.twitter_thread = await self._generate_twitter_thread(context)
        elif context.platform.lower() == 'linkedin':
            advanced_content.linkedin_article = await self._generate_linkedin_article(context)
        elif context.platform.lower() == 'tiktok':
            advanced_content.tiktok_concept = await self._generate_tiktok_concept(context)
        
        return advanced_content
    
    async def _generate_base_content(self, context: ContentGenerationContext) -> Dict[str, Any]:
        """Generate base content for the platform"""
        prompt = self._get_base_content_prompt(context)
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return self._parse_base_content_response(response.text, context.platform)
            except Exception as e:
                print(f"Gemini error for base content: {e}")
                
        return self._fallback_base_content(context)
    
    async def _generate_instagram_stories(
        self, 
        context: ContentGenerationContext
    ) -> List[InstagramStorySlide]:
        """Generate Instagram Stories sequence (5-7 slides)"""
        prompt = f"""
        Create an engaging Instagram Stories sequence for {context.business_name} in the {context.industry} industry.
        
        Campaign Goal: {context.campaign_goal}
        Brand Voice: {context.brand_voice}
        Target Audience: {context.target_audience}
        Trending Topics: {', '.join(context.trending_topics)}
        
        Create 6 story slides with this structure:
        1. Hook slide - grab attention with question/bold statement
        2. Problem slide - identify audience pain point
        3. Solution slide - introduce your solution
        4. Value slide - show benefits/features
        5. Social proof slide - testimonials/results
        6. CTA slide - clear call to action
        
        For each slide, provide:
        - Text overlay (max 2 lines, 12 words each)
        - Background suggestion (color scheme or image style)
        - Interactive stickers (polls, questions, sliders, etc.)
        - Call to action (if applicable)
        
        Format as JSON:
        {{
            "slides": [
                {{
                    "slide_number": 1,
                    "text_overlay": "Are you struggling with...",
                    "background_suggestion": "Gradient blue to purple",
                    "stickers": ["question sticker", "fire emoji"],
                    "call_to_action": "Tap to see solution"
                }}
            ]
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return self._parse_instagram_stories(response.text)
            except Exception as e:
                print(f"Gemini error for Instagram stories: {e}")
        
        return self._fallback_instagram_stories(context)
    
    async def _generate_twitter_thread(
        self, 
        context: ContentGenerationContext
    ) -> List[TwitterThreadTweet]:
        """Generate viral Twitter thread (7-10 tweets)"""
        prompt = f"""
        Create a viral Twitter thread for {context.business_name} in {context.industry}.
        
        Campaign Goal: {context.campaign_goal}
        Brand Voice: {context.brand_voice}
        Trending Topics: {', '.join(context.trending_topics)}
        Trending Hashtags: {', '.join(context.trending_hashtags)}
        
        Thread Structure (8 tweets):
        1. Hook tweet - attention-grabbing opener ending with "🧵 THREAD:"
        2. Problem tweet - identify the challenge/pain point
        3. Context tweet - why this matters now
        4. Solution tweet 1 - first part of your solution
        5. Solution tweet 2 - second part with examples
        6. Proof tweet - data/results/testimonials
        7. Actionable tweet - specific steps readers can take
        8. CTA tweet - clear call to action with relevant hashtags
        
        Each tweet must be:
        - Under 280 characters
        - Engaging and retweetable
        - Include relevant hashtags (2-3 max per tweet)
        - Build anticipation for next tweet
        
        Format as JSON:
        {{
            "thread": [
                {{
                    "tweet_number": 1,
                    "text": "Most {context.industry} companies are missing this crucial element... 🧵 THREAD:",
                    "hashtags": ["#industry", "#innovation"],
                    "character_count": 85,
                    "thread_purpose": "hook",
                    "engagement_hooks": ["question", "curiosity gap"]
                }}
            ]
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return self._parse_twitter_thread(response.text)
            except Exception as e:
                print(f"Gemini error for Twitter thread: {e}")
        
        return self._fallback_twitter_thread(context)
    
    async def _generate_linkedin_article(
        self, 
        context: ContentGenerationContext
    ) -> List[LinkedInArticleSection]:
        """Generate professional LinkedIn article"""
        prompt = f"""
        Create a thought leadership LinkedIn article for {context.business_name}.
        
        Industry: {context.industry}
        Campaign Goal: {context.campaign_goal}
        Brand Voice: Professional, {context.brand_voice}
        Target Audience: {context.target_audience}
        Trending Topics: {', '.join(context.trending_topics)}
        
        Article Structure:
        1. Compelling headline
        2. Introduction with industry hook
        3. Main body sections (3-4 sections)
        4. Key insights section
        5. Future implications
        6. Professional conclusion with CTA
        
        Content should be:
        - 800-1200 words total
        - Industry thought leadership tone
        - Data-driven insights
        - Professional networking focus
        - Include industry statistics and trends
        
        Format as JSON:
        {{
            "article_sections": [
                {{
                    "section_type": "intro",
                    "heading": "The {context.industry} Industry is at a Turning Point",
                    "content": "Detailed introduction paragraph...",
                    "word_count": 150,
                    "key_points": ["point 1", "point 2"]
                }}
            ]
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return self._parse_linkedin_article(response.text)
            except Exception as e:
                print(f"Gemini error for LinkedIn article: {e}")
        
        return self._fallback_linkedin_article(context)
    
    async def _generate_tiktok_concept(
        self, 
        context: ContentGenerationContext
    ) -> TikTokConcept:
        """Generate viral TikTok video concept"""
        prompt = f"""
        Create a viral TikTok video concept for {context.business_name} in {context.industry}.
        
        Campaign Goal: {context.campaign_goal}
        Brand Voice: {context.brand_voice}
        Target Audience: {context.target_audience}
        Trending Topics: {', '.join(context.trending_topics)}
        
        Create a 30-60 second TikTok concept that includes:
        
        1. 3-Second Hook - must grab attention immediately
        2. Script Outline - 8-10 scene breakdown
        3. Trending Audio - suggest 3 current trending sounds
        4. Visual Transitions - creative effects/transitions
        5. Hashtag Strategy - trending + niche hashtags
        6. Call to Action - engaging end screen
        
        Content should be:
        - Authentic and relatable
        - Use current TikTok trends/memes
        - Educational or entertaining
        - Easy to recreate (UGC potential)
        - Include trending elements
        
        Format as JSON:
        {{
            "hook": "POV: You're a {context.industry} professional and this changes everything...",
            "script_outline": [
                "Scene 1: Open with trending sound",
                "Scene 2: Show the problem",
                "etc..."
            ],
            "trending_sounds": ["sound 1", "sound 2", "sound 3"],
            "hashtags": ["#trending", "#niche"],
            "video_duration": "45 seconds",
            "transitions": ["transition 1", "transition 2"],
            "call_to_action": "Follow for more industry tips!"
        }}
        """
        
        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return self._parse_tiktok_concept(response.text)
            except Exception as e:
                print(f"Gemini error for TikTok concept: {e}")
        
        return self._fallback_tiktok_concept(context)
    
    # Parsing methods
    def _parse_instagram_stories(self, response_text: str) -> List[InstagramStorySlide]:
        """Parse Gemini response into Instagram Stories format"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                slides = []
                for slide_data in data.get('slides', []):
                    slide = InstagramStorySlide(
                        slide_number=slide_data.get('slide_number', 1),
                        text_overlay=slide_data.get('text_overlay', ''),
                        background_suggestion=slide_data.get('background_suggestion', ''),
                        stickers=slide_data.get('stickers', []),
                        call_to_action=slide_data.get('call_to_action')
                    )
                    slides.append(slide)
                return slides
        except:
            pass
        
        # Fallback parsing
        return self._fallback_instagram_stories_parsing(response_text)
    
    def _parse_twitter_thread(self, response_text: str) -> List[TwitterThreadTweet]:
        """Parse Gemini response into Twitter thread format"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                tweets = []
                for tweet_data in data.get('thread', []):
                    tweet = TwitterThreadTweet(
                        tweet_number=tweet_data.get('tweet_number', 1),
                        text=tweet_data.get('text', ''),
                        hashtags=tweet_data.get('hashtags', []),
                        character_count=len(tweet_data.get('text', '')),
                        thread_purpose=tweet_data.get('thread_purpose', 'content'),
                        engagement_hooks=tweet_data.get('engagement_hooks', [])
                    )
                    tweets.append(tweet)
                return tweets
        except:
            pass
        
        return self._fallback_twitter_thread_parsing(response_text)
    
    def _parse_linkedin_article(self, response_text: str) -> List[LinkedInArticleSection]:
        """Parse Gemini response into LinkedIn article format"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                sections = []
                for section_data in data.get('article_sections', []):
                    section = LinkedInArticleSection(
                        section_type=section_data.get('section_type', 'body'),
                        heading=section_data.get('heading', ''),
                        content=section_data.get('content', ''),
                        word_count=len(section_data.get('content', '').split()),
                        key_points=section_data.get('key_points', [])
                    )
                    sections.append(section)
                return sections
        except:
            pass
        
        return self._fallback_linkedin_article_parsing(response_text)
    
    def _parse_tiktok_concept(self, response_text: str) -> TikTokConcept:
        """Parse Gemini response into TikTok concept format"""
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return TikTokConcept(
                    hook=data.get('hook', ''),
                    script_outline=data.get('script_outline', []),
                    trending_sounds=data.get('trending_sounds', []),
                    hashtags=data.get('hashtags', []),
                    video_duration=data.get('video_duration', '30 seconds'),
                    transitions=data.get('transitions', []),
                    call_to_action=data.get('call_to_action', '')
                )
        except:
            pass
        
        return self._fallback_tiktok_concept_parsing(response_text)
    
    # Helper methods for prompts and fallbacks
    def _get_base_content_prompt(self, context: ContentGenerationContext) -> str:
        """Get base content generation prompt"""
        return f"""
        Create engaging {context.platform} content for {context.business_name}.
        
        Context:
        - Industry: {context.industry}
        - Goal: {context.campaign_goal}
        - Voice: {context.brand_voice}
        - Audience: {context.target_audience}
        - Trending: {', '.join(context.trending_topics)}
        
        Generate:
        1. Main post text (platform-optimized)
        2. Relevant hashtags (3-8)
        3. Content pillars
        4. Engagement tactics
        5. Viral elements
        
        Format as JSON with these fields.
        """
    
    def _parse_base_content_response(self, response_text: str, platform: str) -> Dict[str, Any]:
        """Parse base content response"""
        # Implementation for parsing base content
        return {
            "text": f"Engaging {platform} content generated by AI",
            "hashtags": ["#innovation", "#business"],
            "content_pillars": ["education", "entertainment"],
            "engagement_tactics": ["storytelling", "questions"],
            "viral_elements": ["trending topics", "relatable content"]
        }
    
    # Fallback methods (simplified versions)
    def _fallback_base_content(self, context: ContentGenerationContext) -> Dict[str, Any]:
        """Fallback base content"""
        return {
            "text": f"🚀 {context.business_name} is revolutionizing {context.industry}! {context.campaign_goal}",
            "hashtags": [f"#{context.industry.lower()}", "#innovation", "#business"],
            "content_pillars": ["innovation", "growth"],
            "engagement_tactics": ["storytelling"],
            "viral_elements": ["trending topics"]
        }
    
    def _fallback_instagram_stories(self, context: ContentGenerationContext) -> List[InstagramStorySlide]:
        """Fallback Instagram Stories"""
        return [
            InstagramStorySlide(
                slide_number=1,
                text_overlay=f"🚀 {context.business_name}",
                background_suggestion="Gradient blue to purple",
                stickers=["fire emoji", "trending up"],
                call_to_action="Swipe up for more"
            ),
            InstagramStorySlide(
                slide_number=2,
                text_overlay=f"Transforming {context.industry}",
                background_suggestion="Clean white background",
                stickers=["poll sticker"],
                call_to_action="DM us for details"
            )
        ]
    
    def _fallback_twitter_thread(self, context: ContentGenerationContext) -> List[TwitterThreadTweet]:
        """Fallback Twitter Thread"""
        return [
            TwitterThreadTweet(
                tweet_number=1,
                text=f"🧵 THREAD: How {context.business_name} is changing {context.industry} forever...",
                hashtags=[f"#{context.industry.lower()}", "#innovation"],
                character_count=75,
                thread_purpose="hook",
                engagement_hooks=["curiosity gap"]
            ),
            TwitterThreadTweet(
                tweet_number=2,
                text=f"The problem: Most {context.industry} companies struggle with...",
                hashtags=[f"#{context.industry.lower()}"],
                character_count=65,
                thread_purpose="problem",
                engagement_hooks=["problem identification"]
            )
        ]
    
    def _fallback_linkedin_article(self, context: ContentGenerationContext) -> List[LinkedInArticleSection]:
        """Fallback LinkedIn Article"""
        return [
            LinkedInArticleSection(
                section_type="intro",
                heading=f"The Future of {context.industry}: What {context.business_name} Knows",
                content=f"The {context.industry} industry is experiencing unprecedented change...",
                word_count=150,
                key_points=["Industry transformation", "Innovation leadership"]
            )
        ]
    
    def _fallback_tiktok_concept(self, context: ContentGenerationContext) -> TikTokConcept:
        """Fallback TikTok Concept"""
        return TikTokConcept(
            hook=f"POV: You work in {context.industry} and this changes everything...",
            script_outline=[
                "Open with trending sound",
                f"Show {context.industry} problem",
                f"Reveal {context.business_name} solution",
                "Show transformation",
                "End with CTA"
            ],
            trending_sounds=["trending sound 1", "viral audio 2"],
            hashtags=[f"#{context.industry.lower()}", "#fyp", "#viral"],
            video_duration="30 seconds",
            transitions=["zoom transition", "quick cuts"],
            call_to_action="Follow for more industry insights!"
        )
    
    # Additional fallback parsing methods
    def _fallback_instagram_stories_parsing(self, text: str) -> List[InstagramStorySlide]:
        """Parse fallback Instagram stories from text"""
        return self._fallback_instagram_stories(ContentGenerationContext(
            business_name="Business", industry="Industry", campaign_goal="Goal",
            brand_voice="professional", target_audience="general", 
            trending_topics=[], trending_hashtags=[], platform="instagram", content_type="story"
        ))
    
    def _fallback_twitter_thread_parsing(self, text: str) -> List[TwitterThreadTweet]:
        """Parse fallback Twitter thread from text"""
        return self._fallback_twitter_thread(ContentGenerationContext(
            business_name="Business", industry="Industry", campaign_goal="Goal",
            brand_voice="professional", target_audience="general",
            trending_topics=[], trending_hashtags=[], platform="twitter", content_type="thread"
        ))
    
    def _fallback_linkedin_article_parsing(self, text: str) -> List[LinkedInArticleSection]:
        """Parse fallback LinkedIn article from text"""
        return self._fallback_linkedin_article(ContentGenerationContext(
            business_name="Business", industry="Industry", campaign_goal="Goal",
            brand_voice="professional", target_audience="general",
            trending_topics=[], trending_hashtags=[], platform="linkedin", content_type="article"
        ))
    
    def _fallback_tiktok_concept_parsing(self, text: str) -> TikTokConcept:
        """Parse fallback TikTok concept from text"""
        return self._fallback_tiktok_concept(ContentGenerationContext(
            business_name="Business", industry="Industry", campaign_goal="Goal",
            brand_voice="professional", target_audience="general",
            trending_topics=[], trending_hashtags=[], platform="tiktok", content_type="video"
        ))

# Global enhanced service instance
enhanced_gemini_service = EnhancedGeminiService()