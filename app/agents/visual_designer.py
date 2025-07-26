from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
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
            
            # Step 2: Generate color palette (use AI-powered method with fallback)
            await self._update_step_progress(2, 4, "Generating color palette")
            color_palette = await self._generate_color_palette(agent_input, visual_themes)
            
            # Step 3: Search for relevant images (use Unsplash API)
            await self._update_step_progress(3, 4, "Finding image suggestions")
            raw_image_suggestions = await self._get_image_suggestions(agent_input, visual_themes)
            
            # Convert to proper ImageSuggestion format and ensure exactly 6 images
            image_suggestions = self._format_image_suggestions(raw_image_suggestions, agent_input)
            
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
            
            self.logger.info(f"Visual design completed successfully with {len(image_suggestions)} images")
            return {
                'visuals': visual_result,
                'metadata': {
                    'design_timestamp': datetime.now(timezone.utc).isoformat(),
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
        """Generate a dynamic, unique color palette using Gemini AI with fallback to algorithmic generation."""
        # First try to generate using Gemini AI with enhanced error handling
        try:
            self.logger.info("🎨 Attempting AI-powered color palette generation...")
            ai_palette = await self._generate_ai_color_palette(agent_input, visual_themes)
            if ai_palette and len(ai_palette) >= 4:
                self.logger.info(f"✅ AI color palette generated successfully with {len(ai_palette)} colors")
                return ai_palette
            else:
                self.logger.warning("❌ AI color palette generation returned insufficient colors")
        except Exception as e:
            self.logger.warning(f"❌ AI color palette generation failed with error: {e}")
        
        # Fallback to enhanced algorithmic generation
        self.logger.info("🔧 Using enhanced algorithmic color palette generation as fallback")
        return self._generate_enhanced_color_palette(agent_input, visual_themes)
    
    def _generate_enhanced_color_palette(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[str]:
        """Generate an enhanced, vibrant color palette without AI dependencies but with intelligent business context."""
        import random
        import hashlib
        
        # Create unique seed based on business for consistency
        business_seed = hashlib.md5(agent_input.business_name.encode()).hexdigest()
        random.seed(int(business_seed[:8], 16))
        
        # Define industry-appropriate vibrant color schemes
        industry_palettes = {
            'food & beverage': [
                ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#4ECDC4', '#45B7D1'],  # Warm & fresh
                ['#E74C3C', '#F39C12', '#2ECC71', '#3498DB', '#9B59B6', '#1ABC9C'],  # Vibrant mix
                ['#FF5722', '#FF9800', '#4CAF50', '#2196F3', '#9C27B0', '#00BCD4']   # Bold colors
            ],
            'technology': [
                ['#0077BE', '#00A8FF', '#7B68EE', '#40E0D0', '#32CD32', '#FF6347'],  # Tech blues & greens
                ['#3498DB', '#9B59B6', '#1ABC9C', '#F39C12', '#E74C3C', '#2ECC71'],  # Modern tech
                ['#2196F3', '#673AB7', '#009688', '#FF5722', '#4CAF50', '#FF9800']   # Digital colors
            ],
            'retail': [
                ['#E91E63', '#9C27B0', '#673AB7', '#3F51B5', '#2196F3', '#00BCD4'],  # Fashion purples & blues
                ['#FF4081', '#7C4DFF', '#536DFE', '#448AFF', '#40C4FF', '#18FFFF'],  # Trendy neons
                ['#F06292', '#BA68C8', '#9575CD', '#7986CB', '#64B5F6', '#4FC3F7']   # Soft fashion
            ],
            'healthcare': [
                ['#4CAF50', '#2196F3', '#00BCD4', '#009688', '#8BC34A', '#CDDC39'],  # Health greens & blues
                ['#66BB6A', '#42A5F5', '#26C6DA', '#66BB6A', '#9CCC65', '#D4E157'],  # Calming health
                ['#81C784', '#64B5F6', '#4DD0E1', '#81C784', '#AED581', '#DCE775']   # Wellness palette
            ],
            'finance': [
                ['#1976D2', '#388E3C', '#7B1FA2', '#303F9F', '#0288D1', '#0097A7'],  # Trust & stability
                ['#1565C0', '#2E7D32', '#6A1B9A', '#283593', '#0277BD', '#00838F'],  # Professional
                ['#0D47A1', '#1B5E20', '#4A148C', '#1A237E', '#01579B', '#006064']   # Deep professional
            ],
            'education': [
                ['#FF9800', '#F44336', '#9C27B0', '#3F51B5', '#2196F3', '#009688'],  # Learning colors
                ['#FFB74D', '#EF5350', '#BA68C8', '#7986CB', '#64B5F6', '#4DB6AC'],  # Bright education
                ['#FFCC02', '#FF5722', '#9C27B0', '#3F51B5', '#03A9F4', '#00BCD4']   # Inspiring palette
            ],
            'real estate': [
                ['#795548', '#607D8B', '#4CAF50', '#2196F3', '#FF9800', '#9C27B0'],  # Earthy modern
                ['#8D6E63', '#78909C', '#66BB6A', '#42A5F5', '#FFB74D', '#BA68C8'],  # Sophisticated
                ['#A1887F', '#90A4AE', '#81C784', '#64B5F6', '#FFCC02', '#CE93D8']   # Upscale palette
            ],
            'automotive': [
                ['#424242', '#F44336', '#2196F3', '#FF9800', '#4CAF50', '#9C27B0'],  # Power colors
                ['#616161', '#E53935', '#1E88E5', '#FB8C00', '#43A047', '#8E24AA'],  # Dynamic
                ['#757575', '#D32F2F', '#1976D2', '#F57C00', '#388E3C', '#7B1FA2']   # Performance
            ]
        }
        
        # Get industry key and select random palette
        industry_key = agent_input.industry.lower().replace(' ', ' ')
        available_palettes = industry_palettes.get(industry_key, industry_palettes['technology'])
        selected_palette = random.choice(available_palettes)
        
        # Add some variation based on brand voice
        voice_modifiers = {
            'professional': 0,
            'friendly': 1,
            'casual': 2,
            'humorous': 1,
            'authoritative': 0,
            'inspirational': 2
        }
        
        voice_key = agent_input.brand_voice.lower()
        modifier = voice_modifiers.get(voice_key, 0)
        
        # Rotate the palette based on brand voice for variety
        if modifier > 0:
            selected_palette = selected_palette[modifier:] + selected_palette[:modifier]
        
        # Add some randomization while keeping it deterministic
        final_palette = selected_palette.copy()
        random.shuffle(final_palette)
        
        self.logger.info(f"Generated reliable color palette for {agent_input.business_name}: {final_palette}")
        return final_palette
    
    def _get_reliable_image_suggestions(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: This method is no longer used. Use _get_image_suggestions instead."""
        # Redirect to the new method
        import asyncio
        return asyncio.create_task(self._get_image_suggestions(agent_input, visual_themes))

    async def _generate_ai_color_palette(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[str]:
        """Generate color palette using Gemini AI for intelligent, contextual colors."""
        try:
            from app.services.gemini_service import gemini_service
            
            # Create prompt for color palette generation
            themes_str = ', '.join(visual_themes[:5])
            
            import time
            import hashlib
            import random
            
            # Create multiple uniqueness factors to ensure different palettes each time
            timestamp = int(time.time() * 1000)  # Millisecond precision
            random_factor = random.randint(1000, 9999)
            business_hash = hashlib.md5(agent_input.business_name.encode()).hexdigest()[:6]
            unique_seed = f"{business_hash}_{timestamp}_{random_factor}"
            
            # Enhanced color inspirations that avoid brown/beige combinations
            vibrant_color_inspirations = [
                'electric sapphire', 'neon emerald', 'cosmic purple', 'vibrant coral', 'aurora green',
                'deep ocean teal', 'midnight indigo', 'crimson fire', 'royal violet', 'jade bamboo',
                'sunset magenta', 'arctic cyan', 'forest pine', 'ruby red', 'golden amber',
                'steel blue', 'lavender mist', 'lime zest', 'plum wine', 'turquoise wave',
                'cherry bloom', 'mint fresh', 'copper rust', 'navy storm', 'rose gold',
                'peacock teal', 'sunset orange', 'violet storm', 'forest moss', 'ocean spray',
                'tropical lime', 'berry burst', 'moonstone blue', 'flame orange', 'sage green',
                'dusty rose', 'charcoal gray', 'ivory cream', 'bronze metal', 'silver shine'
            ]
            
            # Extract any color preferences from previous results or campaign context
            user_color_preferences = self._extract_color_preferences(agent_input)
            
            # Use business-specific seed for consistent but unique inspiration
            business_seed = hashlib.md5(f"{agent_input.business_name}_{unique_seed}".encode()).hexdigest()
            inspiration_index = int(business_seed[:2], 16) % len(vibrant_color_inspirations)
            inspiration_color = vibrant_color_inspirations[inspiration_index]
            
            prompt = f"""
            Create a COMPLETELY UNIQUE and VIBRANT color palette for {agent_input.business_name}.
            
            DETAILED BUSINESS CONTEXT:
            - Company: {agent_input.business_name}
            - Industry: {agent_input.industry}
            - Campaign Goal: {agent_input.campaign_goal}
            - Brand Voice: {agent_input.brand_voice}
            - Target Audience: {agent_input.target_audience}
            - Target Platforms: {', '.join(agent_input.target_platforms)}
            - Visual Themes: {themes_str}
            - Color Inspiration: {inspiration_color}
            - Unique Seed: {unique_seed}
            
            USER-SPECIFIC CONSIDERATIONS:
            - Design colors that appeal specifically to {agent_input.target_audience}
            - Ensure colors work well on {', '.join(agent_input.target_platforms)} platforms
            - Reflect the {agent_input.brand_voice} brand personality through color choices
            - Support the {agent_input.campaign_goal} objective with strategic color psychology
            {f"- User Color Preferences: {user_color_preferences}" if user_color_preferences else ""}
            
            STRICT COLOR REQUIREMENTS:
            1. Create 6 DISTINCT colors with HIGH VISUAL CONTRAST
            2. ABSOLUTELY AVOID ALL brown, beige, tan, cream, and warm earth tones
            3. Use VIBRANT, SATURATED colors from different hue families
            4. Include blues, greens, purples, reds, oranges - but NOT browns
            5. Ensure colors work well together but are visually distinct
            6. Make the palette memorable and unique to {agent_input.business_name}
            
            COLOR DIVERSITY REQUIREMENTS:
            - Primary color: Bold blue, green, purple, or red (NO brown/orange)
            - Secondary color: Complementary bright color from different hue family
            - Accent color: High contrast electric or neon color
            - Neutral color: Cool gray or white (NEVER beige/cream)
            - Background color: Light cool tone (NEVER warm beige)
            - Text color: Dark gray or navy (NEVER brown)
            
            ABSOLUTELY FORBIDDEN COLORS:
            - ALL browns: #A0522D, #8B4513, #D2691E, #CD853F
            - ALL beiges: #DEB887, #F5F5DC, #FAEBD7, #D2B48C, #F4A460
            - ALL tans and creams: #BC9A6A, #C19A6B, #F5E6D3
            - Warm oranges that look brownish
            - Any color with RGB pattern where Red > Green > Blue in warm tones
            
            ENSURE ACCESSIBILITY:
            - Text color must have good contrast with background
            - Colors should be distinguishable for colorblind users
            
            Return ONLY this JSON format:
            {{
                "primary_color": "#RRGGBB",
                "secondary_color": "#RRGGBB",
                "accent_color": "#RRGGBB",
                "neutral_color": "#RRGGBB",
                "background_color": "#RRGGBB",
                "text_color": "#RRGGBB"
            }}
            """
            
            # Generate using Gemini AI with enhanced retry logic
            self.logger.info("🤖 Sending prompt to Gemini AI for color generation...")
            response = await gemini_service._generate_with_retry(prompt, max_retries=3)
            
            if response:
                self.logger.info(f"📝 Received AI response (length: {len(response)}): {response[:200]}...")
                # Parse the AI response with enhanced error recovery
                palette = self._parse_ai_color_response_enhanced(response)
                if palette and len(palette) >= 4:
                    self.logger.info(f"🎨 Successfully parsed palette: {palette}")
                    # Enhanced diversity check
                    if self._validate_enhanced_color_diversity(palette):
                        self.logger.info(f"✅ Generated vibrant AI color palette with {len(palette)} colors: {palette}")
                        return palette
                    else:
                        self.logger.warning(f"⚠️ AI palette lacks diversity: {palette}, trying alternative approach")
                        # Try with more specific vibrant requirement
                        vibrant_prompt = prompt.replace("VIBRANT, SATURATED colors", "EXTREMELY VIBRANT, HIGH-SATURATION colors with MAXIMUM visual impact")
                        retry_response = await gemini_service._generate_with_retry(vibrant_prompt, max_retries=1)
                        if retry_response:
                            retry_palette = self._parse_ai_color_response_enhanced(retry_response)
                            if retry_palette and len(retry_palette) >= 4:
                                self.logger.info(f"✅ Generated enhanced diverse palette on retry: {retry_palette}")
                                return retry_palette
                else:
                    self.logger.warning(f"❌ Failed to parse AI response into valid color palette. Raw response: {response}")
            else:
                self.logger.warning("❌ No response received from Gemini AI")
                    
        except Exception as e:
            self.logger.warning(f"AI color palette generation failed: {e}")
        
        return None
    
    def _extract_color_preferences(self, agent_input: AgentInput) -> str:
        """Extract color preferences from user input and previous results."""
        preferences = []
        
        # Check business name for color hints
        business_name_lower = agent_input.business_name.lower()
        color_hints = {
            'green': ['green', 'eco', 'organic', 'natural', 'leaf', 'mint', 'sage'],
            'blue': ['blue', 'ocean', 'sky', 'water', 'azure', 'navy', 'sapphire'],
            'red': ['red', 'fire', 'ruby', 'crimson', 'cherry', 'rose'],
            'purple': ['purple', 'violet', 'lavender', 'royal', 'plum'],
            'orange': ['orange', 'sunset', 'amber', 'coral'],
            'yellow': ['yellow', 'gold', 'sunny', 'bright', 'lemon'],
            'pink': ['pink', 'rose', 'magenta', 'blush']
        }
        
        for color, hints in color_hints.items():
            if any(hint in business_name_lower for hint in hints):
                preferences.append(f"incorporate {color} tones")
        
        # Check campaign goal for color psychology
        goal_lower = agent_input.campaign_goal.lower()
        if 'trust' in goal_lower or 'professional' in goal_lower:
            preferences.append("use trustworthy blues")
        elif 'energy' in goal_lower or 'exciting' in goal_lower:
            preferences.append("use energetic colors")
        elif 'calm' in goal_lower or 'relax' in goal_lower:
            preferences.append("use calming colors")
        elif 'luxury' in goal_lower or 'premium' in goal_lower:
            preferences.append("use sophisticated colors")
        
        # Check brand voice for color personality
        voice_lower = agent_input.brand_voice.lower()
        if 'friendly' in voice_lower:
            preferences.append("use warm, approachable colors")
        elif 'professional' in voice_lower:
            preferences.append("use professional, corporate colors")
        elif 'playful' in voice_lower or 'fun' in voice_lower:
            preferences.append("use vibrant, playful colors")
        elif 'elegant' in voice_lower or 'sophisticated' in voice_lower:
            preferences.append("use refined, elegant colors")
        
        # Check industry-specific color associations
        industry_lower = agent_input.industry.lower()
        if 'health' in industry_lower:
            preferences.append("incorporate healing greens and calming blues")
        elif 'food' in industry_lower:
            preferences.append("use appetizing colors that enhance food appeal")
        elif 'tech' in industry_lower:
            preferences.append("use modern, digital-friendly colors")
        elif 'finance' in industry_lower:
            preferences.append("use trustworthy, stable colors")
        
        return '; '.join(preferences) if preferences else ""
    
    def _extract_color_preferences(self, agent_input: AgentInput) -> str:
        """Extract color preferences from user input and previous results."""
        preferences = []
        
        # Check business name for color hints
        business_name_lower = agent_input.business_name.lower()
        color_hints = {
            'green': ['green', 'eco', 'organic', 'natural', 'leaf', 'mint', 'sage'],
            'blue': ['blue', 'ocean', 'sky', 'water', 'azure', 'navy', 'sapphire'],
            'red': ['red', 'fire', 'ruby', 'crimson', 'cherry', 'rose'],
            'purple': ['purple', 'violet', 'lavender', 'royal', 'plum'],
            'orange': ['orange', 'sunset', 'amber', 'coral'],
            'yellow': ['yellow', 'gold', 'sunny', 'bright', 'lemon'],
            'pink': ['pink', 'rose', 'magenta', 'blush']
        }
        
        for color, hints in color_hints.items():
            if any(hint in business_name_lower for hint in hints):
                preferences.append(f"incorporate {color} tones")
        
        # Check campaign goal for color psychology
        goal_lower = agent_input.campaign_goal.lower()
        if 'trust' in goal_lower or 'professional' in goal_lower:
            preferences.append("use trustworthy blues")
        elif 'energy' in goal_lower or 'exciting' in goal_lower:
            preferences.append("use energetic colors")
        elif 'calm' in goal_lower or 'relax' in goal_lower:
            preferences.append("use calming colors")
        elif 'luxury' in goal_lower or 'premium' in goal_lower:
            preferences.append("use sophisticated colors")
        
        # Check brand voice for color personality
        voice_lower = agent_input.brand_voice.lower()
        if 'friendly' in voice_lower:
            preferences.append("use warm, approachable colors")
        elif 'professional' in voice_lower:
            preferences.append("use professional, corporate colors")
        elif 'playful' in voice_lower or 'fun' in voice_lower:
            preferences.append("use vibrant, playful colors")
        elif 'elegant' in voice_lower or 'sophisticated' in voice_lower:
            preferences.append("use refined, elegant colors")
        
        # Check industry-specific color associations
        industry_lower = agent_input.industry.lower()
        if 'health' in industry_lower:
            preferences.append("incorporate healing greens and calming blues")
        elif 'food' in industry_lower:
            preferences.append("use appetizing colors that enhance food appeal")
        elif 'tech' in industry_lower:
            preferences.append("use modern, digital-friendly colors")
        elif 'finance' in industry_lower:
            preferences.append("use trustworthy, stable colors")
        
        return '; '.join(preferences) if preferences else ""
    
    def _parse_ai_color_response_enhanced(self, response_text: str) -> List[str]:
        """Enhanced parsing with error recovery for common AI response issues."""
        try:
            # First try standard parsing
            result = self._parse_ai_color_response(response_text)
            if result and len(result) >= 4:
                return result
        except:
            pass
        
        # Enhanced error recovery parsing
        try:
            import re
            import json
            
            # Start with original text
            cleaned = response_text.strip()
            
            # Remove markdown code blocks
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            elif cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Fix common JSON issues
            # 1. Remove comments (// style)
            cleaned = re.sub(r'//.*?\n', '\n', cleaned)
            cleaned = re.sub(r'//.*?$', '', cleaned, flags=re.MULTILINE)
            
            # 2. Replace single quotes with double quotes (be careful with apostrophes)
            cleaned = re.sub(r"'([^']*)':", r'"\1":', cleaned)
            cleaned = re.sub(r": '([^']*)'", r': "\1"', cleaned)
            
            # 3. Remove trailing commas before } or ]
            cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            
            # 4. Try to extract JSON again
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                color_data = json.loads(json_match.group())
                
                # Extract colors
                palette = []
                color_keys = ['primary_color', 'secondary_color', 'accent_color', 
                             'neutral_color', 'background_color', 'text_color']
                
                for key in color_keys:
                    if key in color_data and color_data[key]:
                        color = str(color_data[key]).strip()
                        if color.startswith('#') and len(color) == 7:
                            try:
                                # Validate hex color
                                int(color[1:], 16)
                                palette.append(color.upper())
                            except ValueError:
                                continue
                
                # Fallback: extract all hex colors if not enough structured colors
                if len(palette) < 4:
                    hex_pattern = r'#[0-9A-Fa-f]{6}'
                    all_colors = re.findall(hex_pattern, cleaned)
                    for color in all_colors:
                        if color.upper() not in palette:
                            palette.append(color.upper())
                            if len(palette) >= 6:
                                break
                
                return palette[:6] if len(palette) >= 4 else None
                
        except Exception as e:
            self.logger.warning(f"Enhanced parsing also failed: {e}")
        
        return None
    
    def _validate_enhanced_color_diversity(self, colors: List[str]) -> bool:
        """Enhanced validation for color palette diversity and vibrancy."""
        if not colors or len(colors) < 4:
            return False
        
        try:
            # Check for excessive brown/orange/beige colors
            brown_beige_count = 0
            gray_count = 0
            vibrant_count = 0
            very_similar_count = 0
            
            for i, color in enumerate(colors[:4]):  # Check first 4 colors
                # Check in order: gray first (since some grays might be misclassified as beige)
                if self._is_gray_color(color):
                    gray_count += 1
                elif self._is_brown_beige_color(color):
                    brown_beige_count += 1
                
                # Check vibrancy separately
                if self._is_vibrant_color(color):
                    vibrant_count += 1
                
                # Check for very similar colors
                for j, other_color in enumerate(colors[:4]):
                    if i != j and self._colors_too_similar(color, other_color):
                        very_similar_count += 1
            
            # Enhanced diversity requirements
            max_brown_beige = 1  # Allow max 1 brown/beige
            max_gray = 2  # Allow max 2 grays
            min_vibrant = 2  # Require at least 2 vibrant colors
            max_similar = 1  # Allow max 1 similar pair
            
            diversity_ok = (
                brown_beige_count <= max_brown_beige and 
                gray_count <= max_gray and
                vibrant_count >= min_vibrant and
                very_similar_count <= max_similar
            )
            
            if not diversity_ok:
                self.logger.debug(f"Enhanced diversity check failed: {brown_beige_count} brown/beige, {gray_count} grays, {vibrant_count} vibrant, {very_similar_count} similar")
            
            return diversity_ok
            
        except Exception as e:
            self.logger.warning(f"Enhanced color diversity validation failed: {e}")
            return True  # Default to accepting if validation fails
    
    def _is_brown_beige_color(self, hex_color: str) -> bool:
        """Check if a color is in the brown/beige family."""
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            return False
            
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Define known problematic brown/beige hex colors
            problematic_colors = {
                '#A0522D', '#DEB887', '#F5F5DC', '#FAEBD7', '#D2691E', 
                '#CD853F', '#DEB887', '#8B4513', '#D2B48C', '#F4A460',
                '#BC9A6A', '#C19A6B', '#A0522D'
            }
            
            # Check exact matches first
            if hex_color.upper() in [c.upper() for c in problematic_colors]:
                return True
            
            # Brown/beige characteristics: 
            # 1. Classic brown: high red, medium green, low blue with red > green > blue
            # 2. Beige/tan: high values but close to each other, warm tones
            # 3. Light brown: similar to beige but slightly more brown
            
            # Classic brown pattern (like #A0522D)
            if (r > 120 and g > 60 and b < 100 and r > g and g > b and (r - b) > 50):
                return True
                
            # Beige/tan pattern (like #DEB887, #F5F5DC)
            if (r > 180 and g > 150 and b > 100 and 
                abs(r - g) < 60 and r >= g and g >= b and 
                (r + g + b) > 450):  # High overall brightness
                return True
                
            # Very light beige (like #FAEBD7, #F5F5DC) 
            if (r > 240 and g > 220 and b > 200 and 
                r >= g and g >= b and abs(r - g) < 30):
                return True
                    
        except ValueError:
            return False
            
        return False
    
    def _is_gray_color(self, hex_color: str) -> bool:
        """Check if a color is in the gray family."""
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            return False
            
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Gray characteristics: R, G, B values are very close to each other
            max_diff = max(abs(r-g), abs(g-b), abs(r-b))
            
            # True grays have very small differences between RGB values
            # Also check that it's not a warm-toned "gray" (which could be beige)
            is_neutral_gray = (max_diff < 15 and  # Very close RGB values
                             not (r > g and g > b and r > 150))  # Not warm-toned
            
            return is_neutral_gray
                    
        except ValueError:
            return False
    
    def _is_vibrant_color(self, hex_color: str) -> bool:
        """Check if a color is vibrant (high saturation)."""
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            return False
            
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            
            # Vibrant colors have high saturation (big difference between max and min RGB)
            rgb_values = [r, g, b]
            max_val = max(rgb_values)
            min_val = min(rgb_values)
            
            # High saturation means big difference between max and min
            saturation_diff = max_val - min_val
            return saturation_diff > 80 and max_val > 100  # Vibrant threshold
                    
        except ValueError:
            return False

    def _validate_color_diversity(self, colors: List[str]) -> bool:
        """Validate that color palette has good diversity and isn't too monochromatic."""
        if not colors or len(colors) < 4:
            return False
        
        try:
            # Check for excessive brown/orange colors (allow some for food businesses)
            brown_orange_count = 0
            very_similar_count = 0
            
            for i, color in enumerate(colors[:4]):  # Check first 4 colors
                if self._is_brown_orange_color(color):
                    brown_orange_count += 1
                
                # Check for very similar colors (same hue family)
                for j, other_color in enumerate(colors[:4]):
                    if i != j and self._colors_too_similar(color, other_color):
                        very_similar_count += 1
            
            # Allow up to 2 brown/orange colors for food businesses, 1 for others
            max_brown_orange = 2 
            
            # Allow some similar colors but not too many
            max_similar = 2
            
            diversity_ok = (brown_orange_count <= max_brown_orange and 
                          very_similar_count <= max_similar)
            
            if not diversity_ok:
                self.logger.debug(f"Color diversity check failed: {brown_orange_count} brown/orange, {very_similar_count} similar")
            
            return diversity_ok
            
        except Exception as e:
            self.logger.warning(f"Color diversity validation failed: {e}")
            return True  # Default to accepting if validation fails
    
    def _is_brown_orange_color(self, hex_color: str) -> bool:
        """Check if a color is in the brown/orange family."""
        # Use the enhanced brown/beige detection
        return self._is_brown_beige_color(hex_color)
    
    def _colors_too_similar(self, color1: str, color2: str) -> bool:
        """Check if two colors are too similar (same hue family)."""
        if not color1 or not color2:
            return False
            
        try:
            # Convert both to RGB
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            
            # Calculate Euclidean distance in RGB space
            distance = ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)**0.5
            
            # Colors are too similar if distance is very small
            return distance < 50  # Threshold for similarity
            
        except (ValueError, IndexError):
            return False
    
    def _parse_ai_color_response(self, response_text: str) -> List[str]:
        """Parse AI response to extract color palette."""
        try:
            import re
            import json
            
            # Clean the response text - remove markdown code blocks
            cleaned_text = response_text.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            cleaned_text = cleaned_text.strip()
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                color_data = json.loads(json_match.group())
                
                # Extract colors in preferred order
                palette = []
                color_keys = ['primary_color', 'secondary_color', 'accent_color', 
                             'neutral_color', 'background_color', 'text_color']
                
                for key in color_keys:
                    if key in color_data and color_data[key]:
                        color = color_data[key].strip()
                        if color.startswith('#') and len(color) == 7:
                            palette.append(color)
                
                # If we don't have enough colors, try to extract all hex colors from response
                if len(palette) < 4:
                    hex_pattern = r'#[0-9A-Fa-f]{6}'
                    all_colors = re.findall(hex_pattern, cleaned_text)
                    for color in all_colors:
                        if color not in palette:
                            palette.append(color)
                            if len(palette) >= 6:
                                break
                
                return palette[:6] if len(palette) >= 4 else None
                
        except Exception as e:
            self.logger.warning(f"Failed to parse AI color response: {e}")
        
        return None
    
    def _generate_complementary_colors(self, base_color: str) -> List[str]:
        """Generate complementary colors based on a base color."""
        # Convert hex to RGB
        hex_color = base_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Generate complementary and analogous colors
        complementary = self._get_complementary_rgb(rgb)
        analogous1 = self._shift_hue_rgb(rgb, 30)
        analogous2 = self._shift_hue_rgb(rgb, -30)
        
        return [
            self._rgb_to_hex(complementary),
            self._rgb_to_hex(analogous1),
            self._rgb_to_hex(analogous2)
        ]
    
    def _get_complementary_rgb(self, rgb: tuple) -> tuple:
        """Get complementary color."""
        return (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
    
    def _shift_hue_rgb(self, rgb: tuple, degrees: int) -> tuple:
        """Shift hue by degrees (simplified)."""
        # Simple hue shift approximation
        shift_factor = degrees / 360.0
        r, g, b = rgb
        
        # Rotate RGB values
        if degrees > 0:
            return (min(255, int(r * (1 + shift_factor))), g, min(255, int(b * (1 + shift_factor))))
        else:
            return (max(0, int(r * (1 + shift_factor))), g, max(0, int(b * (1 + shift_factor))))
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB to hex."""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def _generate_tint_or_shade(self, hex_color: str, factor: float) -> str:
        """Generate a tint or shade of a color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        if factor > 0:  # Tint (lighter)
            new_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        else:  # Shade (darker)
            new_rgb = tuple(max(0, int(c * (1 + factor))) for c in rgb)
        
        return self._rgb_to_hex(new_rgb)
    
    def _shift_color_temperature(self, hex_color: str, direction: str) -> str:
        """Shift color temperature."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = rgb
        
        if direction == 'warm':
            # Increase red, decrease blue
            new_rgb = (min(255, r + 20), g, max(0, b - 15))
        else:  # cool
            # Decrease red, increase blue
            new_rgb = (max(0, r - 20), g, min(255, b + 15))
        
        return self._rgb_to_hex(new_rgb)
    
    def _deepen_color(self, hex_color: str) -> str:
        """Make color deeper and richer."""
        return self._generate_tint_or_shade(hex_color, -0.2)
    
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
    
    def _create_simple_fallback_images(self, agent_input: AgentInput) -> List[Dict[str, Any]]:
        """Create 6 simple placeholder images as a guaranteed fallback."""
        colors = ['4F46E5', '059669', 'DC2626', 'EA580C', '7C3AED', '0F766E']
        themes = ['Workspace', 'Team', 'Innovation', 'Growth', 'Success', 'Professional']
        
        images = []
        for i in range(6):
            image = {
                'id': f'fallback_{i+1}',
                'url': f'https://via.placeholder.com/800x600/{colors[i]}/ffffff?text={themes[i]}',
                'description': f'{themes[i]} - {agent_input.industry} imagery for {agent_input.business_name}',
                'tags': [agent_input.industry, 'business', themes[i].lower()],
                'photographer': 'VyralFlow AI',
                'source': 'placeholder',
                'unsplash_url': f'https://via.placeholder.com/800x600/{colors[i]}/ffffff?text={themes[i]}',
                'small_url': f'https://via.placeholder.com/400x300/{colors[i]}/ffffff?text={themes[i]}',
                'photographer_url': '#',
                'likes': 100 + i * 50,
                'color': f'#{colors[i]}',
                'width': 800,
                'height': 600
            }
            images.append(image)
        
        return images

    async def _get_image_suggestions(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[Dict[str, Any]]:
        """Get 6 diverse, curated image suggestions using real Unsplash API with AI-generated queries."""
        try:
            self.logger.info(f"🖼️ Generating curated image suggestions for {agent_input.business_name}")
            
            # Try to use the real Unsplash service if available
            try:
                image_suggestions = await unsplash_service.get_photo_suggestions(
                    business_name=agent_input.business_name,
                    industry=agent_input.industry,
                    campaign_goal=agent_input.campaign_goal,
                    visual_themes=visual_themes
                )
                
                if image_suggestions and len(image_suggestions) >= 1:
                    self.logger.info(f"✅ Retrieved {len(image_suggestions)} images from Unsplash API")
                    
                    # Ensure we have exactly 6 images
                    if len(image_suggestions) < 6:
                        fallback_count = 6 - len(image_suggestions)
                        fallback_images = self._create_simple_fallback_images(agent_input)
                        image_suggestions.extend(fallback_images[:fallback_count])
                    
                    return image_suggestions[:6]
                else:
                    raise Exception("No images returned from Unsplash")
                    
            except Exception as unsplash_error:
                self.logger.warning(f"Unsplash API failed: {unsplash_error}")
                
                # Use simple fallback images
                fallback_images = self._create_simple_fallback_images(agent_input)
                self.logger.info(f"🔄 Using simple fallback: generated {len(fallback_images)} placeholder images")
                return fallback_images
                
        except Exception as e:
            self.logger.error(f"❌ All image generation failed: {e}")
            
            # Final guarantee - create simple placeholder images
            fallback_images = self._create_simple_fallback_images(agent_input)
            self.logger.info(f"🛡️ Emergency fallback: created {len(fallback_images)} simple images")
            return fallback_images

    def _format_image_suggestions(self, raw_suggestions: List[Dict[str, Any]], agent_input: AgentInput) -> List[Dict[str, Any]]:
        """
        Formats raw image suggestions into the correct format for the frontend.
        Ensures exactly 6 images are returned.
        """
        formatted_suggestions = []
        
        # If we don't have enough suggestions, create fallbacks
        if len(raw_suggestions) < 6:
            raw_suggestions.extend(self._get_enhanced_fallback_images(agent_input, [])[:6-len(raw_suggestions)])
        
        for i, raw_suggestion in enumerate(raw_suggestions[:6]):  # Take only first 6
            # Extract the URL with fallbacks
            url = (raw_suggestion.get('url') or 
                   raw_suggestion.get('unsplash_url') or 
                   raw_suggestion.get('urls', {}).get('regular') or
                   raw_suggestion.get('urls', {}).get('small') or
                   f'https://via.placeholder.com/800x600/4F46E5/ffffff?text=Image+{i+1}')
            
            # Extract description
            description = (raw_suggestion.get('description') or 
                          raw_suggestion.get('alt_description') or
                          f'Professional {agent_input.industry} image for {agent_input.business_name}')
            
            # Extract photographer
            photographer = (raw_suggestion.get('photographer') or
                           raw_suggestion.get('user', {}).get('name') if raw_suggestion.get('user') else None or
                           'Professional Stock')
            
            # Extract tags
            tags = raw_suggestion.get('tags', [])
            if isinstance(tags, list) and len(tags) > 0:
                if isinstance(tags[0], dict):
                    tags = [tag.get('title', str(tag)) for tag in tags]
            else:
                tags = [agent_input.industry, 'business', 'professional']
            
            # Create the formatted suggestion matching the ImageSuggestion model
            formatted_suggestion = {
                'url': url,
                'description': description[:200],  # Truncate long descriptions
                'tags': tags[:5],  # Limit tags
                'photographer': photographer,
                'source': 'unsplash',
                # Add extra fields that the frontend expects
                'id': raw_suggestion.get('id', f'img_{i}'),
                'unsplash_url': url,
                'small_url': raw_suggestion.get('small_url', url),
                'photographer_url': raw_suggestion.get('photographer_url', '#'),
                'likes': raw_suggestion.get('likes', 0),
                'color': raw_suggestion.get('color', '#CCCCCC'),
                'width': raw_suggestion.get('width', 800),
                'height': raw_suggestion.get('height', 600)
            }
            
            formatted_suggestions.append(formatted_suggestion)
        
        self.logger.info(f"Formatted {len(formatted_suggestions)} image suggestions")
        return formatted_suggestions

    def _get_enhanced_fallback_images(
        self,
        agent_input: AgentInput,
        visual_themes: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate 6 diverse, high-quality fallback images when API fails."""
        import random
        import hashlib
        import time
        
        # Create deterministic but varied suggestions using business context
        business_seed = hashlib.md5(agent_input.business_name.encode()).hexdigest()
        time_seed = int(time.time() / 3600)  # Changes every hour for variety
        random.seed(int(business_seed[:8], 16) + time_seed)
        
        # Industry-specific image themes for professional variety
        industry_themes = {
            'food & beverage': [
                ('modern-restaurant-interior', 'Modern Restaurant Interior', '3D4A5C'),
                ('fresh-ingredients-display', 'Fresh Ingredients Display', '2ECC71'),
                ('professional-chef-cooking', 'Professional Chef Cooking', 'E74C3C'),
                ('cozy-cafe-atmosphere', 'Cozy Cafe Atmosphere', 'F39C12'),
                ('artisan-food-plating', 'Artisan Food Plating', '9B59B6'),
                ('coffee-brewing-process', 'Coffee Brewing Process', '34495E')
            ],
            'technology': [
                ('modern-tech-office', 'Modern Tech Office', '3498DB'),
                ('software-development-team', 'Software Development Team', '2ECC71'),
                ('innovative-workspace', 'Innovative Workspace', 'E74C3C'),
                ('digital-collaboration', 'Digital Collaboration', 'F39C12'),
                ('tech-startup-energy', 'Tech Startup Energy', '9B59B6'),
                ('ai-innovation-concept', 'AI Innovation Concept', '1ABC9C')
            ],
            'retail': [
                ('modern-store-interior', 'Modern Store Interior', '3498DB'),
                ('shopping-experience', 'Shopping Experience', '2ECC71'),
                ('product-showcase', 'Product Showcase', 'E74C3C'),
                ('boutique-elegance', 'Boutique Elegance', 'F39C12'),
                ('retail-customer-service', 'Retail Customer Service', '9B59B6'),
                ('brand-display-modern', 'Brand Display Modern', '34495E')
            ],
            'healthcare': [
                ('modern-medical-office', 'Modern Medical Office', '3498DB'),
                ('healthcare-consultation', 'Healthcare Consultation', '2ECC71'),
                ('wellness-lifestyle', 'Wellness Lifestyle', 'E74C3C'),
                ('medical-technology', 'Medical Technology', 'F39C12'),
                ('fitness-wellness-center', 'Fitness Wellness Center', '9B59B6'),
                ('health-professional-team', 'Health Professional Team', '1ABC9C')
            ],
            'finance': [
                ('professional-business-meeting', 'Professional Business Meeting', '2C3E50'),
                ('financial-consultation', 'Financial Consultation', '27AE60'),
                ('modern-banking-interior', 'Modern Banking Interior', '3498DB'),
                ('business-growth-concept', 'Business Growth Concept', 'F39C12'),
                ('investment-advisory', 'Investment Advisory', '9B59B6'),
                ('financial-success-lifestyle', 'Financial Success Lifestyle', '1ABC9C')
            ],
            'education': [
                ('modern-learning-environment', 'Modern Learning Environment', '3498DB'),
                ('online-education-setup', 'Online Education Setup', '2ECC71'),
                ('professional-training', 'Professional Training', 'E74C3C'),
                ('knowledge-resources', 'Knowledge Resources', 'F39C12'),
                ('student-success', 'Student Success', '9B59B6'),
                ('innovative-classroom', 'Innovative Classroom', '34495E')
            ],
            'real estate': [
                ('luxury-home-interior', 'Luxury Home Interior', '2C3E50'),
                ('real-estate-consultation', 'Real Estate Consultation', '27AE60'),
                ('modern-property-exterior', 'Modern Property Exterior', '3498DB'),
                ('elegant-living-space', 'Elegant Living Space', 'F39C12'),
                ('property-showcase', 'Property Showcase', '9B59B6'),
                ('architectural-design', 'Architectural Design', '1ABC9C')
            ],
            'automotive': [
                ('modern-car-showroom', 'Modern Car Showroom', '2C3E50'),
                ('automotive-innovation', 'Automotive Innovation', '27AE60'),
                ('professional-auto-service', 'Professional Auto Service', '3498DB'),
                ('luxury-vehicle-interior', 'Luxury Vehicle Interior', 'F39C12'),
                ('automotive-technology', 'Automotive Technology', '9B59B6'),
                ('dealership-professional', 'Dealership Professional', '34495E')
            ]
        }
        
        # Get industry-specific themes or use generic business themes
        industry_key = agent_input.industry.lower()
        themes = industry_themes.get(industry_key, [
            ('professional-workspace', 'Professional Workspace', '3498DB'),
            ('business-meeting-modern', 'Business Meeting Modern', '2ECC71'),
            ('office-collaboration', 'Office Collaboration', 'E74C3C'),
            ('team-success-concept', 'Team Success Concept', 'F39C12'),
            ('innovation-lifestyle', 'Innovation Lifestyle', '9B59B6'),
            ('corporate-professional', 'Corporate Professional', '34495E')
        ])
        
        # Generate 6 diverse fallback images
        fallback_images = []
        selected_themes = random.sample(themes, min(6, len(themes)))
        
        for i, (theme_key, theme_title, color) in enumerate(selected_themes):
            # Create varied dimensions for visual interest
            dimensions = [(800, 600), (1000, 700), (900, 650), (850, 625)]
            width, height = random.choice(dimensions)
            
            image = {
                'id': f'fallback_{agent_input.business_name.lower().replace(" ", "_")}_{theme_key}_{i}',
                'description': f'{theme_title} - Professional {agent_input.industry} imagery for {agent_input.business_name}',
                'url': f'https://via.placeholder.com/{width}x{height}/{color}/ffffff?text={theme_title.replace(" ", "+")}',
                'unsplash_url': f'https://via.placeholder.com/{width}x{height}/{color}/ffffff?text={theme_title.replace(" ", "+")}',
                'small_url': f'https://via.placeholder.com/400x300/{color}/ffffff?text={theme_title.replace(" ", "+")}',
                'thumb_url': f'https://via.placeholder.com/200x150/{color}/ffffff?text={theme_title.replace(" ", "+")}',
                'photographer': 'VyralFlow AI',
                'photographer_username': 'vyralflow_ai',
                'photographer_url': '#',
                'likes': random.randint(100, 800),
                'color': f'#{color}',
                'width': width,
                'height': height,
                'quality_score': random.randint(3, 5),
                'search_query': f'{agent_input.industry} {theme_title.lower()}',
                'is_fallback': True
            }
            fallback_images.append(image)
        
        # Shuffle for variety while maintaining quality
        random.shuffle(fallback_images)
        
        return fallback_images[:6]
    
    
    def _get_reliable_working_images(
        self,
        agent_input: AgentInput,
        existing_count: int
    ) -> List[Dict[str, Any]]:
        """DEPRECATED: This method is no longer used. Use _get_enhanced_fallback_images instead."""
        # Redirect to the new method
        return self._get_enhanced_fallback_images(agent_input, [])
    
    async def _get_fallback_visual_design(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Generate fallback visual design when main execution fails."""
        self.logger.warning("Using fallback visual design - generating 6 images")
        
        # Basic visual themes based on industry
        visual_themes = ["professional", "modern", "clean"]
        if agent_input.industry.lower() in ["food", "restaurant"]:
            visual_themes = ["appetizing", "warm", "inviting"]
        elif agent_input.industry.lower() in ["tech", "technology"]:
            visual_themes = ["innovative", "futuristic", "sleek"]
        
        # Basic color palette
        color_palette = ["#2E86C1", "#28B463", "#E74C3C"]
        
        # Use the 6-image fallback method instead of 1 image  
        image_suggestions = self._create_simple_fallback_images(agent_input)
        
        # Basic style recommendations
        style_recommendations = f"Clean and professional design suitable for {agent_input.industry} industry"
        
        return {
            'visuals': {
                "recommended_style": style_recommendations,
                "image_suggestions": image_suggestions,
                "color_palette": color_palette,
                "visual_themes": visual_themes
            },
            'metadata': {
                'design_timestamp': datetime.now(timezone.utc).isoformat(),
                'images_found': len(image_suggestions),
                'themes_generated': len(visual_themes),
                'colors_suggested': len(color_palette),
                'agent_version': '1.0.0',
                'fallback_mode': True
            }
        }


# Global agent instance
visual_designer_agent = VisualDesignerAgent()
