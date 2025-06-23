from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import random

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentType, AgentInput
from app.models.campaign import VisualResult, ImageSuggestion
from app.services.unsplash_service import unsplash_service
from app.utils.logging import get_logger

logger = get_logger(__name__)


class VisualDesignerAgent(BaseAgent):
    """
    Agent responsible for visual concept suggestions and image recommendations.
    Uses Unsplash API to find relevant images and generates visual design guidelines.
    """
    
    def __init__(self):
        super().__init__(AgentType.VISUAL_DESIGNER, timeout_seconds=180)
        self.logger = get_logger("agent.visual_designer")
    
    async def _execute_impl(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute visual design suggestions for the campaign.
        
        Args:
            agent_input: Campaign input data including content and trend results
            
        Returns:
            Dict containing visual design recommendations
        """
        self.logger.info(f"Starting visual design for {agent_input.business_name}")
        
        # Validate input
        if not self._validate_input(agent_input):
            raise ValueError("Invalid input data for visual design")
        
        try:
            # Step 1: Analyze campaign context for visual themes
            await self._update_step_progress(1, 4, "Analyzing campaign context")
            visual_themes = await self._analyze_visual_context(agent_input)
            
            # Step 2: Generate color palette
            await self._update_step_progress(2, 4, "Generating color palette")
            color_palette = await self._generate_color_palette(agent_input, visual_themes)
            
            # Step 3: Search for relevant images
            await self._update_step_progress(3, 4, "Finding image suggestions")
            image_suggestions = await self._get_image_suggestions(agent_input, visual_themes)
            
            # Step 4: Create visual style recommendations
            await self._update_step_progress(4, 4, "Creating style recommendations")
            style_recommendations = await self._create_style_recommendations(
                agent_input, visual_themes, color_palette
            )
            
            # Compile final visual result as a dictionary
            visual_result = {
                "recommended_style": style_recommendations,
                "image_suggestions": image_suggestions,
                "color_palette": color_palette,
                "visual_themes": visual_themes
            }
            
            self.logger.info("Visual design completed successfully")
            return {
                'visuals': visual_result,
                'metadata': {
                    'design_timestamp': datetime.utcnow().isoformat(),
                    'images_found': len(image_suggestions),
                    'themes_generated': len(visual_themes),
                    'colors_suggested': len(color_palette),
                    'agent_version': '1.0.0'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Visual design failed: {e}")
            return await self._get_fallback_visual_design(agent_input)
    
    async def _analyze_visual_context(self, agent_input: AgentInput) -> List[str]:
        """Analyze campaign context to determine visual themes."""
        themes = []
        
        # Industry-based themes
        industry_themes = {
            'food & beverage': ['warm colors', 'appetizing', 'cozy atmosphere', 'fresh ingredients', 'rustic charm'],
            'technology': ['modern', 'clean lines', 'futuristic', 'professional', 'innovation-focused'],
            'retail': ['trendy', 'lifestyle-focused', 'product-centric', 'fashionable', 'consumer-friendly'],
            'healthcare': ['clean', 'trustworthy', 'calming', 'professional', 'wellness-focused'],
            'finance': ['professional', 'trustworthy', 'sophisticated', 'corporate', 'secure'],
            'education': ['inspiring', 'knowledge-focused', 'bright', 'encouraging', 'scholarly'],
            'real estate': ['aspirational', 'lifestyle', 'architectural', 'luxury', 'home-focused'],
            'automotive': ['dynamic', 'powerful', 'sleek', 'performance-oriented', 'modern']
        }
        
        industry_key = agent_input.industry.lower()
        themes.extend(industry_themes.get(industry_key, ['professional', 'modern', 'clean']))
        
        # Brand voice themes
        voice_themes = {
            'professional': ['corporate', 'clean', 'sophisticated'],
            'friendly': ['warm', 'approachable', 'welcoming'],
            'casual': ['relaxed', 'informal', 'laid-back'],
            'humorous': ['playful', 'fun', 'entertaining'],
            'authoritative': ['strong', 'confident', 'commanding'],
            'inspirational': ['uplifting', 'motivating', 'aspirational']
        }
        
        voice_key = agent_input.brand_voice.lower()
        themes.extend(voice_themes.get(voice_key, ['professional']))
        
        # Campaign goal themes
        goal_lower = agent_input.campaign_goal.lower()
        if 'launch' in goal_lower or 'new' in goal_lower:
            themes.extend(['exciting', 'fresh', 'innovative'])
        elif 'sale' in goal_lower or 'discount' in goal_lower:
            themes.extend(['urgent', 'attractive', 'value-focused'])
        elif 'awareness' in goal_lower:
            themes.extend(['attention-grabbing', 'memorable', 'distinctive'])
        
        # Extract themes from previous results (content/trends)
        if agent_input.previous_results:
            content_themes = self._extract_themes_from_content(agent_input.previous_results)
            themes.extend(content_themes)
        
        # Remove duplicates and return top themes
        unique_themes = list(dict.fromkeys(themes))
        return unique_themes[:8]
    
    def _extract_themes_from_content(self, previous_results: Dict[str, Any]) -> List[str]:
        """Extract visual themes from content and trend analysis."""
        themes = []
        
        # From trend analysis
        if 'trends' in previous_results:
            trends = previous_results['trends']
            if isinstance(trends, dict):
                trending_topics = trends.get('trending_topics', [])
                for topic in trending_topics[:5]:
                    if 'color' in topic.lower():
                        themes.append('colorful')
                    elif 'minimal' in topic.lower():
                        themes.append('minimalist')
                    elif 'retro' in topic.lower():
                        themes.append('vintage')
                    elif 'modern' in topic.lower():
                        themes.append('contemporary')
        
        # From content analysis
        if 'content' in previous_results:
            content = previous_results['content']
            if isinstance(content, dict):
                # Analyze content tone for visual themes
                for platform_content in content.values():
                    if isinstance(platform_content, dict):
                        text = platform_content.get('text', '').lower()
                        if 'exciting' in text or '🎉' in text:
                            themes.append('energetic')
                        if 'professional' in text:
                            themes.append('corporate')
                        if 'cozy' in text or '☕' in text:
                            themes.append('warm')
        
        return themes
    
    async def _generate_color_palette(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[str]:
        """Generate a color palette based on themes and industry."""
        # Industry-specific color palettes
        industry_colors = {
            'food & beverage': ['#D2691E', '#8B4513', '#FF4500', '#F4A460', '#DEB887'],
            'technology': ['#0066CC', '#4A90E2', '#50C878', '#6C7B7F', '#2C3E50'],
            'retail': ['#E91E63', '#9C27B0', '#FF5722', '#FFC107', '#795548'],
            'healthcare': ['#4CAF50', '#2196F3', '#00BCD4', '#009688', '#8BC34A'],
            'finance': ['#1976D2', '#424242', '#37474F', '#546E7A', '#78909C'],
            'education': ['#FF9800', '#F44336', '#9C27B0', '#3F51B5', '#009688'],
            'real estate': ['#795548', '#607D8B', '#9E9E9E', '#CDDC39', '#FF5722'],
            'automotive': ['#212121', '#424242', '#F44336', '#FF5722', '#607D8B']
        }
        
        base_colors = industry_colors.get(agent_input.industry.lower(), ['#2196F3', '#4CAF50', '#FF9800'])
        
        # Theme-based color modifications
        theme_colors = {
            'warm': ['#FF6B35', '#F7931E', '#FFD23F'],
            'cool': ['#4ECDC4', '#44A08D', '#093637'],
            'professional': ['#2C3E50', '#34495E', '#7F8C8D'],
            'energetic': ['#E74C3C', '#F39C12', '#E67E22'],
            'calming': ['#3498DB', '#5DADE2', '#85C1E9'],
            'luxurious': ['#8E44AD', '#9B59B6', '#BB8FCE']
        }
        
        # Add theme-based colors
        final_colors = list(base_colors)
        for theme in visual_themes[:3]:
            theme_key = theme.replace('-', '').replace(' ', '').lower()
            if theme_key in theme_colors:
                final_colors.extend(theme_colors[theme_key][:2])
        
        # Remove duplicates and limit to 6 colors
        unique_colors = list(dict.fromkeys(final_colors))
        return unique_colors[:6]
    
    async def _get_image_suggestions(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[Dict[str, Any]]:
        """Get image suggestions from Unsplash."""
        try:
            # Get photo suggestions based on campaign context
            photos = await unsplash_service.get_photo_suggestions(
                business_name=agent_input.business_name,
                industry=agent_input.industry,
                campaign_goal=agent_input.campaign_goal,
                visual_themes=visual_themes
            )
            
            # Convert to format expected by frontend
            image_suggestions = []
            for photo in photos[:10]:  # Limit to 10 suggestions
                # Format image data to match frontend expectations
                suggestion = {
                    "id": photo.get('id', f"img_{len(image_suggestions)}"),
                    "url": photo.get('urls', {}).get('regular', ''),
                    "description": photo.get('description', '') or photo.get('alt_description', '') or f"Image for {agent_input.business_name}",
                    "alt_description": photo.get('alt_description', '') or photo.get('description', '') or f"Image for {agent_input.business_name}",
                    "photographer": photo.get('user', {}).get('name', 'Unsplash Photographer'),
                    "photographer_url": photo.get('user', {}).get('links', {}).get('html', 'https://unsplash.com'),
                    "likes": photo.get('likes', 0),
                    "width": photo.get('width', 800),
                    "height": photo.get('height', 600)
                }
                image_suggestions.append(suggestion)
            
            self.logger.info(f"Found {len(image_suggestions)} image suggestions")
            return image_suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get image suggestions: {e}")
            return self._get_fallback_image_suggestions(agent_input)
    
    def _get_fallback_image_suggestions(self, agent_input: AgentInput) -> List[Dict[str, Any]]:
        """Get fallback image suggestions when Unsplash fails."""
        fallback_suggestions = [
            {
                "id": "fallback_1",
                "url": 'https://via.placeholder.com/800x600/4a90e2/ffffff?text=Business+Image',
                "description": f'Professional {agent_input.industry} business image',
                "alt_description": f'Professional {agent_input.industry} business image',
                "photographer": 'Stock Photos',
                "photographer_url": 'https://placeholder.com',
                "likes": 0,
                "width": 800,
                "height": 600
            },
            {
                "id": "fallback_2",
                "url": 'https://via.placeholder.com/800x600/50c878/ffffff?text=Campaign+Visual',
                "description": f'{agent_input.business_name} campaign visual',
                "alt_description": f'{agent_input.business_name} campaign visual',
                "photographer": 'Stock Photos',
                "photographer_url": 'https://placeholder.com',
                "likes": 0,
                "width": 800,
                "height": 600
            },
            {
                "id": "fallback_3",
                "url": 'https://via.placeholder.com/800x600/e74c3c/ffffff?text=Brand+Image',
                "description": f'{agent_input.business_name} brand representation',
                "alt_description": f'{agent_input.business_name} brand representation',
                "photographer": 'Stock Photos',
                "photographer_url": 'https://placeholder.com',
                "likes": 0,
                "width": 800,
                "height": 600
            }
        ]
        
        self.logger.warning("Using fallback image suggestions")
        return fallback_suggestions
    
    async def _create_style_recommendations(
        self,
        agent_input: AgentInput,
        visual_themes: List[str],
        color_palette: List[str]
    ) -> str:
        """Create comprehensive style recommendations."""
        recommendations = []
        
        # Overall style direction
        main_themes = visual_themes[:3]
        recommendations.append(f"Visual style should emphasize {', '.join(main_themes)} elements.")
        
        # Color guidance
        primary_color = color_palette[0] if color_palette else '#2196F3'
        recommendations.append(f"Use {primary_color} as the primary brand color with supporting colors from the suggested palette.")
        
        # Industry-specific recommendations
        industry_recs = {
            'food & beverage': 'Focus on appetizing imagery with warm, inviting colors. Use natural lighting and showcase texture and freshness.',
            'technology': 'Emphasize clean, modern aesthetics with plenty of white space. Use geometric shapes and contemporary typography.',
            'retail': 'Highlight products with lifestyle imagery. Use bright, engaging colors that appeal to your target demographic.',
            'healthcare': 'Maintain a clean, trustworthy appearance with calming colors. Use professional imagery that conveys expertise.',
            'finance': 'Project stability and trustworthiness through conservative design choices and professional imagery.',
            'education': 'Use inspiring, bright visuals that convey growth and learning. Include diverse representations.',
            'real estate': 'Showcase aspirational lifestyle imagery with architectural focus. Use natural lighting and spacious compositions.',
            'automotive': 'Emphasize performance and quality through dynamic imagery and bold design elements.'
        }
        
        industry_rec = industry_recs.get(agent_input.industry.lower(), 'Maintain professional appearance with clean, modern design elements.')
        recommendations.append(industry_rec)
        
        # Platform-specific guidance
        if agent_input.target_platforms:
            platform_guidance = []
            if 'instagram' in [p.lower() for p in agent_input.target_platforms]:
                platform_guidance.append('Instagram: Use high-quality, visually striking images with consistent filter/editing style.')
            if 'linkedin' in [p.lower() for p in agent_input.target_platforms]:
                platform_guidance.append('LinkedIn: Professional headshots and corporate imagery work best.')
            if 'facebook' in [p.lower() for p in agent_input.target_platforms]:
                platform_guidance.append('Facebook: Lifestyle images and behind-the-scenes content encourage engagement.')
            if 'twitter' in [p.lower() for p in agent_input.target_platforms]:
                platform_guidance.append('Twitter: Simple, clear images that are easily readable at small sizes.')
            
            if platform_guidance:
                recommendations.append(f"Platform considerations: {' '.join(platform_guidance)}")
        
        # Typography and layout
        recommendations.append('Use consistent typography hierarchy and maintain adequate white space for readability.')
        
        # Brand voice integration
        voice_guidance = {
            'professional': 'Maintain formal composition with structured layouts.',
            'friendly': 'Use approachable imagery with warm, inviting compositions.',
            'casual': 'Embrace relaxed, informal styling with natural, candid imagery.',
            'humorous': 'Incorporate playful elements and unexpected visual combinations.',
            'authoritative': 'Use strong, confident imagery with bold compositional choices.',
            'inspirational': 'Focus on aspirational imagery that motivates and uplifts.'
        }
        
        voice_rec = voice_guidance.get(agent_input.brand_voice.lower(), 'Maintain consistency with brand personality.')
        recommendations.append(voice_rec)
        
        return ' '.join(recommendations)
    
    async def _get_fallback_visual_design(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Get fallback visual design when main process fails."""
        self.logger.warning("Using fallback visual design")
        
        # Basic fallback data
        fallback_themes = ['professional', 'modern', 'clean', 'trustworthy']
        fallback_colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
        fallback_images = self._get_fallback_image_suggestions(agent_input)
        
        fallback_style = f"Professional {agent_input.industry} visual style with modern, clean aesthetics. Use corporate colors and maintain consistent branding across all platforms."
        
        # Create a dictionary directly instead of using VisualResult
        visual_result = {
            "recommended_style": fallback_style,
            "image_suggestions": fallback_images,
            "color_palette": fallback_colors,
            "visual_themes": fallback_themes
        }
        
        return {
            'visuals': visual_result,
            'metadata': {
                'design_timestamp': datetime.utcnow().isoformat(),
                'fallback_used': True,
                'reason': 'Primary visual design process failed',
                'agent_version': '1.0.0'
            }
        }


# Global agent instance
visual_designer_agent = VisualDesignerAgent()