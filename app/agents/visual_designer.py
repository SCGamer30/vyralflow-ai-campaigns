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
        """Generate a cohesive color palette based on themes and industry."""
        # Industry-specific cohesive color palettes (each palette works harmoniously together)
        industry_palettes = {
            'food & beverage': {
                'primary': '#D2691E',  # Warm orange
                'palette': ['#D2691E', '#E67E22', '#F39C12', '#F7DC6F', '#FADBD8', '#FDEAA7']  # Warm orange tones
            },
            'technology': {
                'primary': '#3498DB',  # Tech blue
                'palette': ['#3498DB', '#5DADE2', '#85C1E9', '#AED6F1', '#D6EAF8', '#EBF5FB']  # Blue gradient
            },
            'retail': {
                'primary': '#E91E63',  # Vibrant pink
                'palette': ['#E91E63', '#F06292', '#F8BBD9', '#FCE4EC', '#AD1457', '#880E4F']  # Pink tones
            },
            'healthcare': {
                'primary': '#4CAF50',  # Medical green
                'palette': ['#4CAF50', '#66BB6A', '#81C784', '#A5D6A7', '#C8E6C9', '#E8F5E8']  # Green gradient
            },
            'finance': {
                'primary': '#1976D2',  # Trust blue
                'palette': ['#1976D2', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB', '#E3F2FD']  # Professional blue
            },
            'education': {
                'primary': '#FF9800',  # Knowledge orange
                'palette': ['#FF9800', '#FFB74D', '#FFCC02', '#FFE082', '#FFF3C4', '#FFF8E1']  # Warm learning tones
            },
            'real estate': {
                'primary': '#8D6E63',  # Earthy brown
                'palette': ['#8D6E63', '#A1887F', '#BCAAA4', '#D7CCC8', '#EFEBE9', '#F3E5F5']  # Natural earth tones
            },
            'automotive': {
                'primary': '#424242',  # Sleek gray
                'palette': ['#424242', '#616161', '#757575', '#9E9E9E', '#BDBDBD', '#E0E0E0']  # Metallic grays
            }
        }
        
        # Get the industry palette or default
        industry_key = agent_input.industry.lower()
        selected_palette = industry_palettes.get(industry_key, {
            'primary': '#3498DB',
            'palette': ['#3498DB', '#5DADE2', '#85C1E9', '#AED6F1', '#D6EAF8', '#EBF5FB']
        })
        
        # Determine theme adjustments for more cohesive colors
        theme_adjustments = {
            'warm': 'warmer',
            'cool': 'cooler', 
            'professional': 'muted',
            'energetic': 'vibrant',
            'calming': 'softer',
            'luxurious': 'richer'
        }
        
        # Apply theme modifications to create variations of the base palette
        primary_theme = None
        for theme in visual_themes[:3]:
            theme_key = theme.replace('-', '').replace(' ', '').lower()
            if theme_key in theme_adjustments:
                primary_theme = theme_adjustments[theme_key]
                break
        
        # Generate harmonious palette based on primary color and theme
        base_palette = selected_palette['palette']
        
        if primary_theme == 'warmer':
            # Shift towards warmer variants of the same colors
            final_palette = base_palette[:4] + [self._adjust_color_warmth(base_palette[0], 0.1), self._adjust_color_warmth(base_palette[1], 0.1)]
        elif primary_theme == 'cooler':
            # Shift towards cooler variants
            final_palette = base_palette[:4] + [self._adjust_color_warmth(base_palette[0], -0.1), self._adjust_color_warmth(base_palette[1], -0.1)]
        elif primary_theme == 'vibrant':
            # Use more saturated versions of the same colors
            final_palette = [base_palette[0], base_palette[1]] + [self._adjust_color_saturation(color, 0.2) for color in base_palette[:4]]
        elif primary_theme == 'softer':
            # Use more muted versions
            final_palette = [self._adjust_color_saturation(color, -0.3) for color in base_palette]
        else:
            # Use the original harmonious palette
            final_palette = base_palette
        
        return final_palette[:6]
    
    def _adjust_color_warmth(self, hex_color: str, adjustment: float) -> str:
        """Adjust color warmth while maintaining harmony."""
        # Simple warmth adjustment - in a real implementation, you'd convert to HSL and adjust hue
        # For now, return a predetermined warmer/cooler variant
        warm_variants = {
            '#3498DB': '#3F51B5',  # Blue to indigo
            '#4CAF50': '#8BC34A',  # Green to lime
            '#E91E63': '#F44336',  # Pink to red
        }
        return warm_variants.get(hex_color, hex_color)
    
    def _adjust_color_saturation(self, hex_color: str, adjustment: float) -> str:
        """Adjust color saturation while maintaining harmony."""
        # Simple saturation adjustment
        if adjustment > 0:
            # More vibrant
            vibrant_variants = {
                '#3498DB': '#2980B9',
                '#4CAF50': '#388E3C',
                '#E91E63': '#C2185B',
            }
            return vibrant_variants.get(hex_color, hex_color)
        else:
            # More muted
            muted_variants = {
                '#3498DB': '#5DADE2',
                '#4CAF50': '#81C784',
                '#E91E63': '#F06292',
            }
            return muted_variants.get(hex_color, hex_color)
    
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