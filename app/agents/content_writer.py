from typing import Dict, Any, List, Optional
from datetime import datetime
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
            
            # Create final content result
            content_result = await self._create_content_result(platform_contents)
            
            self.logger.info("Content generation completed successfully")
            return {
                'content': content_result,
                'metadata': {
                    'generation_timestamp': datetime.utcnow().isoformat(),
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
            enhanced_hashtags = self._enhance_hashtags(hashtags, trend_data, platform)
            
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
    
    def _enhance_hashtags(
        self,
        original_hashtags: List[str],
        trend_data: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Enhance hashtags with trending data."""
        enhanced_hashtags = list(original_hashtags)
        
        # Add trending hashtags
        trending_hashtags = trend_data.get('trending_hashtags', [])
        for hashtag in trending_hashtags[:3]:  # Add up to 3 trending hashtags
            if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 10:
                enhanced_hashtags.append(hashtag)
        
        # Platform-specific hashtag optimization
        platform_hashtags = self._get_platform_specific_hashtags(platform)
        for hashtag in platform_hashtags:
            if hashtag not in enhanced_hashtags and len(enhanced_hashtags) < 8:
                enhanced_hashtags.append(hashtag)
        
        return enhanced_hashtags[:10]  # Limit to 10 hashtags
    
    def _get_platform_specific_hashtags(self, platform: str) -> List[str]:
        """Get platform-specific hashtags."""
        platform_hashtags = {
            'instagram': ['#instagood', '#photooftheday', '#follow'],
            'twitter': ['#trending', '#follow', '#retweet'],
            'linkedin': ['#professional', '#business', '#networking'],
            'facebook': ['#like', '#share', '#community'],
            'tiktok': ['#fyp', '#viral', '#trending']
        }
        
        return platform_hashtags.get(platform.lower(), [])
    
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
            'tiktok': (50, 120)
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
                'text': f"🌟 Exciting updates from {agent_input.business_name}! {agent_input.campaign_goal[:100]}... Follow us for more! #business #update",
                'hashtags': ['#business', '#update', '#follow', '#exciting']
            },
            'twitter': {
                'text': f"📢 {agent_input.business_name}: {agent_input.campaign_goal[:150]} #business #news",
                'hashtags': ['#business', '#news', '#update']
            },
            'linkedin': {
                'text': f"Professional update from {agent_input.business_name}: We're focused on {agent_input.campaign_goal}. This initiative demonstrates our commitment to excellence in the {agent_input.industry} industry.",
                'hashtags': ['#business', '#professional', '#industry', '#growth']
            },
            'facebook': {
                'text': f"Hello everyone! {agent_input.business_name} has some exciting news to share: {agent_input.campaign_goal[:200]}... Stay tuned for more updates!",
                'hashtags': ['#business', '#news', '#community', '#update']
            },
            'tiktok': {
                'text': f"✨ {agent_input.business_name} vibes! {agent_input.campaign_goal[:80]}... #fyp #business",
                'hashtags': ['#fyp', '#business', '#trending', '#viral']
            }
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
            'content': content_result.dict(),
            'metadata': {
                'generation_timestamp': datetime.utcnow().isoformat(),
                'platforms_generated': len(platform_contents),
                'fallback_used': True,
                'reason': 'Primary content generation failed',
                'agent_version': '1.0.0'
            }
        }


# Global agent instance
content_writer_agent = ContentWriterAgent()