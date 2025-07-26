from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentType, AgentInput
from app.models.campaign import ContentResult, PlatformContent, ContentVariation
from app.services.gemini_service import gemini_service
from app.utils.logging import get_logger
from app.utils.helpers import get_platform_character_limits, extract_hashtags, count_characters

logger = get_logger(__name__)


class ContentWriterAgent(BaseAgent):
    """
    Agent responsible for generating platform-specific content using Google Gemini API.
    Creates optimized content for multiple social media platforms based on trends and campaign goals.
    """
    
    def __init__(self):
        super().__init__(AgentType.CONTENT_WRITER, timeout_seconds=240)
        self.logger = get_logger("agent.content_writer")
        self.platform_limits = get_platform_character_limits()
    
    async def _execute_impl(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute content generation for the campaign.
        
        Args:
            agent_input: Campaign input data including trend analysis results
            
        Returns:
            Dict containing generated content for all platforms
        """
        self.logger.info(f"Starting content generation for {agent_input.business_name}")
        
        # Validate input
        if not self._validate_input(agent_input):
            raise ValueError("Invalid input data for content generation")
        
        try:
            # Extract trend data from previous agent results
            trend_data = self._extract_trend_data(agent_input)
            
            # Generate content for each target platform
            platform_contents = {}
            total_platforms = len(agent_input.target_platforms)
            
            for i, platform in enumerate(agent_input.target_platforms):
                await self._update_step_progress(
                    i + 1, 
                    total_platforms, 
                    f"Generating content for {platform}"
                )
                
                platform_content = await self._generate_platform_content(
                    platform, agent_input, trend_data
                )
                platform_contents[platform] = platform_content
                
                # Small delay between platform generations to avoid rate limits
                await asyncio.sleep(0.5)
            
            # Create final content result as dictionary for better compatibility
            content_result = await self._create_content_result(platform_contents)
            
            self.logger.info("Content generation completed successfully")
            return {
                'content': content_result.model_dump(),
                'metadata': {
                    'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                    'platforms_generated': len(platform_contents),
                    'total_variations': self._count_total_variations(platform_contents),
                    'agent_version': '1.0.0'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Content generation failed: {e}")
            return await self._get_fallback_content(agent_input)
    
    def _extract_trend_data(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Extract trend data from previous agent results."""
        trend_data = {
            'trending_topics': [],
            'trending_hashtags': [],
            'analysis_summary': ''
        }
        
        if agent_input.previous_results and 'trends' in agent_input.previous_results:
            trends = agent_input.previous_results['trends']
            if isinstance(trends, dict):
                trend_data.update({
                    'trending_topics': trends.get('trending_topics', []),
                    'trending_hashtags': trends.get('trending_hashtags', []),
                    'analysis_summary': trends.get('analysis_summary', '')
                })
        
        return trend_data
    
    async def _generate_platform_content(
        self,
        platform: str,
        agent_input: AgentInput,
        trend_data: Dict[str, Any]
    ) -> PlatformContent:
        """Generate content for a specific platform."""
        try:
            # Generate main content using Gemini
            content_data = await gemini_service.generate_platform_content(
                business_name=agent_input.business_name,
                industry=agent_input.industry,
                campaign_goal=agent_input.campaign_goal,
                platform=platform,
                brand_voice=agent_input.brand_voice,
                target_audience=agent_input.target_audience,
                trending_topics=trend_data.get('trending_topics', []),
                keywords=agent_input.keywords
            )
            
            # Process and validate the generated content
            main_text = content_data.get('text', '')
            hashtags = content_data.get('hashtags', [])
            variations = content_data.get('variations', [])
            
            # Ensure content fits platform limits
            main_text = self._ensure_platform_compliance(main_text, platform)
            
            # Process variations
            processed_variations = []
            for variation in variations[:3]:  # Limit to 3 variations
                if isinstance(variation, str):
                    processed_text = self._ensure_platform_compliance(variation, platform)
                    processed_variations.append(ContentVariation(
                        text=processed_text,
                        hashtags=extract_hashtags(processed_text) or hashtags[:3],
                        character_count=count_characters(processed_text),
                        engagement_score=self._estimate_engagement_score(processed_text, platform)
                    ))
            
            # Enhance hashtags with trend data
            enhanced_hashtags = self._enhance_hashtags(hashtags, trend_data, platform, agent_input.industry)
            
            return PlatformContent(
                text=main_text,
                hashtags=enhanced_hashtags,
                character_count=count_characters(main_text),
                variations=processed_variations
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate content for {platform}: {e}")
            return self._get_fallback_platform_content(platform, agent_input)
    
    def _ensure_platform_compliance(self, text: str, platform: str) -> str:
        """Ensure content complies with platform character limits."""
        char_limit = self.platform_limits.get(platform.lower(), 2000)
        
        if len(text) <= char_limit:
            return text
        
        # Truncate and add ellipsis
        truncated = text[:char_limit - 3] + "..."
        self.logger.warning(f"Truncated {platform} content from {len(text)} to {len(truncated)} characters")
        
        return truncated
    
    async def _enhance_hashtags(
        self,
        original_hashtags: List[str],
        trend_data: Dict[str, Any],
        platform: str,
        agent_input: AgentInput
    ) -> List[str]:
        """Enhance hashtags with trending data and AI-powered suggestions."""
        try:
            # Get AI-powered hashtag suggestions from Gemini
            ai_hashtags = await gemini_service.generate_hashtags(
                business_name=agent_input.business_name,
                industry=agent_input.industry,
                campaign_goal=agent_input.campaign_goal,
                platform=platform,
                brand_voice=agent_input.brand_voice,
                target_audience=agent_input.target_audience,
                trending_topics=trend_data.get('trending_topics', []),
                keywords=agent_input.keywords
            )
            
            # Combine all hashtag sources
            combined_hashtags = list(original_hashtags)
            combined_hashtags.extend(ai_hashtags)
            combined_hashtags.extend(trend_data.get('trending_hashtags', []))
            
            # Add platform-specific and industry-specific hashtags
            combined_hashtags.extend(self._get_platform_specific_hashtags(platform))
            combined_hashtags.extend(self._get_industry_hashtags(agent_input.industry))
            
            # Remove duplicates and return top hashtags
            unique_hashtags = list(dict.fromkeys(combined_hashtags))
            return unique_hashtags[:15]  # Increased limit to 15 hashtags
        
        except Exception as e:
            self.logger.error(f"Failed to enhance hashtags with AI: {e}")
            # Fallback to original enhancement method
            return self._fallback_enhance_hashtags(original_hashtags, trend_data, platform, agent_input.industry)
    
    def _fallback_enhance_hashtags(
        self,
        original_hashtags: List[str],
        trend_data: Dict[str, Any],
        platform: str,
        industry: str = ""
    ) -> List[str]:
        """Fallback hashtag enhancement logic."""
        enhanced_hashtags = list(original_hashtags)
        
        # Add trending hashtags (more generous)
        trending_hashtags = trend_data.get('trending_hashtags', [])
        for hashtag in trending_hashtags[:5]:  # Add up to 5 trending hashtags
            if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 20:
                enhanced_hashtags.append(hashtag)
        
        # Platform-specific hashtag optimization (more generous)
        platform_hashtags = self._get_platform_specific_hashtags(platform)
        for hashtag in platform_hashtags:
            if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 18:
                enhanced_hashtags.append(hashtag)
        
        # Add industry-specific hashtags
        if industry:
            industry_hashtags = self._get_industry_hashtags(industry)
            for hashtag in industry_hashtags:
                if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 16:
                    enhanced_hashtags.append(hashtag)
        
        # Add engagement-boosting hashtags
        engagement_hashtags = self._get_engagement_hashtags(platform)
        for hashtag in engagement_hashtags:
            if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 15:
                enhanced_hashtags.append(hashtag)
        
        return enhanced_hashtags[:15]  # Increased limit to 15 hashtags
    
    def _get_platform_specific_hashtags(self, platform: str) -> List[str]:
        """Get platform-specific hashtags."""
        platform_hashtags = {
            'instagram': ['#instagood', '#photooftheday', '#follow'],
            'twitter': ['#trending', '#follow', '#retweet'],
            'linkedin': ['#professional', '#business', '#networking'],
            'facebook': ['#like', '#share', '#community'],
        }
        
        return platform_hashtags.get(platform.lower(), [])
    
    def _get_industry_hashtags(self, industry: str) -> List[str]:
        """Get industry-specific hashtags."""
        industry_hashtags = {
            'food & beverage': ['#foodie', '#delicious', '#restaurant', '#chef', '#cuisine'],
            'technology': ['#tech', '#innovation', '#startup', '#digital', '#software'],
            'retail': ['#shopping', '#fashion', '#style', '#deals', '#store'],
            'healthcare': ['#health', '#wellness', '#medical', '#care', '#safety'],
            'finance': ['#finance', '#investment', '#money', '#banking', '#wealth'],
            'education': ['#education', '#learning', '#student', '#knowledge', '#school'],
            'real estate': ['#realestate', '#property', '#home', '#investment', '#luxury'],
            'automotive': ['#automotive', '#cars', '#driving', '#performance', '#luxury']
        }
        
        return industry_hashtags.get(industry.lower(), ['#business', '#professional'])
    
    def _get_engagement_hashtags(self, platform: str) -> List[str]:
        """Get engagement-boosting hashtags."""
        engagement_hashtags = {
            'instagram': ['#love', '#amazing', '#beautiful', '#inspiration', '#motivation'],
            'twitter': ['#MondayMotivation', '#ThrowbackThursday', '#FollowFriday', '#WisdomWednesday', '#TuesdayTips'],
            'linkedin': ['#leadership', '#success', '#growth', '#innovation', '#teamwork'],
            'facebook': ['#ThankfulThursday', '#FeelGoodFriday', '#MotivationalMonday', '#WisdomWednesday', '#transformation'],
        }
        
        return engagement_hashtags.get(platform.lower(), ['#motivation', '#success', '#growth'])
    
    def _estimate_engagement_score(self, text: str, platform: str) -> float:
        """Estimate engagement score for content."""
        score = 0.5  # Base score
        
        # Length scoring
        text_length = len(text)
        optimal_lengths = {
            'twitter': (100, 200),
            'instagram': (125, 300),
            'linkedin': (150, 400),
            'facebook': (100, 250),
        }
        
        optimal_range = optimal_lengths.get(platform.lower(), (100, 300))
        if optimal_range[0] <= text_length <= optimal_range[1]:
            score += 0.2
        
        # Engagement indicators
        if '?' in text:  # Questions encourage engagement
            score += 0.1
        if any(word in text.lower() for word in ['how', 'what', 'why', 'when', 'where']):
            score += 0.1
        if any(word in text.lower() for word in ['share', 'comment', 'like', 'follow']):
            score += 0.1
        if '#' in text:  # Hashtags help discoverability
            score += 0.1
        
        return min(score, 1.0)
    
    async def _create_content_result(self, platform_contents: Dict[str, PlatformContent]) -> ContentResult:
        """Create the final content result object."""
        content_result = ContentResult()
        
        for platform, content in platform_contents.items():
            setattr(content_result, platform.lower(), content)
        
        return content_result
    
    def _count_total_variations(self, platform_contents: Dict[str, PlatformContent]) -> int:
        """Count total number of content variations generated."""
        total = 0
        for content in platform_contents.values():
            total += len(content.variations)
        return total
    
    def _get_fallback_platform_content(
        self,
        platform: str,
        agent_input: AgentInput
    ) -> PlatformContent:
        """Get fallback content for a platform when generation fails."""
        fallback_templates = {
            'instagram': {
                'text': f"Hey everyone! ✨ We're excited to share something amazing at {agent_input.business_name} - {agent_input.campaign_goal}. Our team has been working hard to bring you the best experience, and we can't wait for you to see what we've created! Thanks for all your support - it means the world to us. What do you think? We'd love to hear from you! 😊",
                'hashtags': ['#community', '#learning', '#passionate', '#behindthescenes', '#grateful', '#process', '#teamwork', '#authentic']
            },
            'twitter': {
                'text': f"Excited to share what we've been creating at {agent_input.business_name} - {agent_input.campaign_goal}. Our team's dedication to excellence shows in everything we do, and we're grateful for all the amazing support. Ready to see what's next? Let us know what you think!",
                'hashtags': ['#learning', '#persistence', '#community', '#grateful', '#teamwork', '#authentic']
            },
            'linkedin': {
                'text': f"At {agent_input.business_name}, we're focused on {agent_input.campaign_goal}. Our commitment to excellence and innovation drives everything we do. We believe in delivering outstanding results that exceed expectations, and our team works tirelessly to make that happen. We're excited about what's ahead and grateful for the trust our clients place in us. Looking forward to sharing more exciting developments soon!",
                'hashtags': ['#learning', '#collaboration', '#quality', '#growth', '#authentic', '#teamwork', '#grateful']
            },
            'facebook': {
                'text': f"Hi everyone! 😊 We're thrilled to share what we've been creating at {agent_input.business_name} - {agent_input.campaign_goal}. Our team has been working passionately to deliver something truly special, and we're so grateful for this amazing community's support. Can't wait to show you what's coming next! What do you think so far?",
                'hashtags': ['#community', '#learning', '#grateful', '#authentic', '#teamwork', '#passionate', '#real']
            },
        }
        
        template = fallback_templates.get(platform.lower(), fallback_templates['instagram'])
        text = template['text']
        
        # Ensure compliance with platform limits
        text = self._ensure_platform_compliance(text, platform)
        
        self.logger.warning(f"Using fallback content for {platform}")
        
        return PlatformContent(
            text=text,
            hashtags=template['hashtags'],
            character_count=count_characters(text),
            variations=[
                ContentVariation(
                    text=f"Alternative: {text[:100]}...",
                    hashtags=template['hashtags'][:2],
                    character_count=count_characters(f"Alternative: {text[:100]}..."),
                    engagement_score=0.5
                )
            ]
        )
    
    async def _get_fallback_content(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Get complete fallback content when main generation fails."""
        self.logger.warning("Using fallback content generation")
        
        platform_contents = {}
        for platform in agent_input.target_platforms:
            platform_contents[platform] = self._get_fallback_platform_content(platform, agent_input)
        
        content_result = await self._create_content_result(platform_contents)
        
        return {
            'content': content_result.model_dump(),
            'metadata': {
                'generation_timestamp': datetime.now(timezone.utc).isoformat(),
                'platforms_generated': len(platform_contents),
                'fallback_used': True,
                'reason': 'Primary content generation failed',
                'agent_version': '1.0.0'
            }
        }


# Global agent instance
content_writer_agent = ContentWriterAgent()