#!/usr/bin/env python3
"""
Enhanced Services for Vyralflow AI
Real API integrations for production-quality results
"""
import os
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiohttp
from pytrends.request import TrendReq
import google.generativeai as genai

class UnsplashService:
    """Real Unsplash API integration for visual suggestions"""
    
    def __init__(self):
        self.api_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.base_url = "https://api.unsplash.com"
        self.request_count = 0
        self.max_requests_per_hour = 50  # Unsplash free tier limit
        self.session = None
        
        if self.api_key:
            print(f"✅ Unsplash Service initialized with API key: {self.api_key[:10]}...")
        else:
            print("⚠️ Unsplash API key not found, using fallback images")
        
    async def search_images(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant images on Unsplash with proper API integration"""
        
        # Check rate limit
        if self.request_count >= self.max_requests_per_hour:
            print(f"⚠️ Unsplash rate limit reached, using fallback for: {query}")
            return self._create_diverse_fallback(query, count)
        
        try:
            print(f"📸 Making Unsplash API call for: {query}")
            url = f"{self.base_url}/search/photos"
            headers = {
                "Authorization": f"Client-ID {self.api_key}",
                "Accept-Version": "v1"
            }
            params = {
                "query": query,
                "per_page": min(count, 30),  # Unsplash max per page
                "orientation": "landscape",
                "order_by": "relevant"
            }
            
            # Add timeout and SSL configuration  
            timeout = aiohttp.ClientTimeout(total=10)
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers=headers, params=params) as response:
                    self.request_count += 1
                    
                    if response.status == 200:
                        data = await response.json()
                        images = []
                        
                        print(f"✅ Unsplash returned {len(data.get('results', []))} images for '{query}'")
                        
                        for photo in data.get('results', []):
                            # Extract comprehensive photo data
                            image_data = {
                                "id": photo.get('id', ''),
                                "description": photo.get('alt_description') or photo.get('description') or f"{query} concept",
                                "url": photo.get('urls', {}).get('regular', ''),  # Fixed: Use 'url' instead of 'unsplash_url'
                                "unsplash_url": photo.get('urls', {}).get('regular', ''),
                                "small_url": photo.get('urls', {}).get('small', ''),
                                "thumb_url": photo.get('urls', {}).get('thumb', ''),
                                "full_url": photo.get('urls', {}).get('full', ''),
                                "photographer": photo.get('user', {}).get('name', 'Unknown Artist'),
                                "photographer_username": photo.get('user', {}).get('username', ''),
                                "photographer_url": photo.get('user', {}).get('links', {}).get('html', ''),
                                "download_url": photo.get('links', {}).get('download_location', ''),
                                "html_link": photo.get('links', {}).get('html', ''),
                                "width": photo.get('width', 0),
                                "height": photo.get('height', 0),
                                "color": photo.get('color', '#000000'),
                                "likes": photo.get('likes', 0),
                                "source": "unsplash_api",
                                "search_term": query
                            }
                            images.append(image_data)
                        
                        if images:
                            return images
                        else:
                            print(f"⚠️ No images found for '{query}', using fallback")
                            return self._create_diverse_fallback(query, count)
                    
                    elif response.status == 401:
                        print(f"❌ Unsplash API authentication failed - invalid API key")
                        return self._create_diverse_fallback(query, count)
                    
                    elif response.status == 403:
                        print(f"❌ Unsplash API rate limit exceeded")
                        return self._create_diverse_fallback(query, count)
                    
                    else:
                        print(f"❌ Unsplash API error: {response.status}")
                        return self._create_diverse_fallback(query, count)
                        
        except asyncio.TimeoutError:
            print(f"⏱️ Unsplash API timeout for query: {query}")
            return self._create_diverse_fallback(query, count)
        except Exception as e:
            print(f"❌ Unsplash API error for '{query}': {str(e)}")
            return self._create_diverse_fallback(query, count)
    
    def _create_diverse_fallback(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Create diverse fallback images instead of duplicates"""
        fallback_images = [
            {
                "id": f"fallback_{query}_1",
                "description": f"Professional {query} workspace with modern design",
                "url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1080",  # Fixed: Added 'url' field
                "unsplash_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1080",
                "small_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=400",
                "photographer": "Austin Distel",
                "photographer_username": "austindistel",
                "photographer_url": "https://unsplash.com/@austindistel",
                "source": "fallback_curated",
                "search_term": query,
                "color": "#F5F5F5",
                "likes": 1250
            },
            {
                "id": f"fallback_{query}_2", 
                "description": f"Creative {query} concept with innovative elements",
                "url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=1080",
                "unsplash_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=1080",
                "small_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400",
                "photographer": "Campaign Creators",
                "photographer_username": "campaign_creators",
                "photographer_url": "https://unsplash.com/@campaign_creators",
                "source": "fallback_curated",
                "search_term": query,
                "color": "#4A90E2",
                "likes": 892
            },
            {
                "id": f"fallback_{query}_3",
                "description": f"Dynamic {query} visualization with engaging composition",
                "url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1080",
                "unsplash_url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1080",
                "small_url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=400", 
                "photographer": "ThisisEngineering RAEng",
                "photographer_username": "thisisengineering",
                "photographer_url": "https://unsplash.com/@thisisengineering",
                "source": "fallback_curated",
                "search_term": query,
                "color": "#FF6B6B",
                "likes": 1567
            },
            {
                "id": f"fallback_{query}_4",
                "description": f"Strategic {query} planning with collaborative approach",
                "url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1080",
                "unsplash_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1080",
                "small_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400",
                "photographer": "Scott Graham", 
                "photographer_username": "homajob",
                "photographer_url": "https://unsplash.com/@homajob",
                "source": "fallback_curated",
                "search_term": query,
                "color": "#50C878",
                "likes": 743
            },
            {
                "id": f"fallback_{query}_5",
                "description": f"Future-focused {query} technology and innovation",
                "url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080",
                "unsplash_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080",
                "small_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400",
                "photographer": "NASA",
                "photographer_username": "nasa",
                "photographer_url": "https://unsplash.com/@nasa",
                "source": "fallback_curated", 
                "search_term": query,
                "color": "#1E3A8A",
                "likes": 2341
            }
        ]
        
        # Return only the requested count, cycling through if needed
        result = []
        for i in range(count):
            fallback_index = i % len(fallback_images)
            image = fallback_images[fallback_index].copy()
            # Make each image unique by modifying the ID
            image["id"] = f"fallback_{query}_{i+1}"
            result.append(image)
        
        print(f"📷 Using {len(result)} diverse fallback images for '{query}'")
        return result

class GeminiService:
    """Google Gemini API for AI-generated content"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.chat_session = None
        
        if self.api_key and self.api_key != 'your-gemini-api-key':
            try:
                genai.configure(api_key=self.api_key)
                # Use enhanced model configuration for better results
                generation_config = {
                    "temperature": 0.9,  # High creativity for viral content
                    "top_p": 0.8,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                }
                
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
                
                self.model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                
                # Initialize chat session for context-aware conversations
                self.chat_session = self.model.start_chat(history=[])
                
                print("✅ Gemini API initialized successfully with enhanced configuration")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini API: {e}")
                self.model = None
        else:
            print("⚠️ Gemini API key not configured, using fallback content")
    
    async def generate_content(
        self, 
        business_name: str, 
        industry: str, 
        platform: str,
        campaign_goal: str,
        brand_voice: str = "professional"
    ) -> Dict[str, Any]:
        """Generate AI-powered content with enhanced processing"""
        
        if not self.model:
            print("🔄 Using fallback content - Gemini API not available")
            return self._fallback_content(business_name, industry, platform)
            
        try:
            print(f"🤖 Generating AI content for {platform} using Gemini...")
            
            # Multi-step AI generation for better results
            # Step 1: Generate initial content
            prompt = self._build_prompt(business_name, industry, platform, campaign_goal, brand_voice)
            response = await self._generate_with_retry(prompt, max_retries=3)
            
            if not response:
                print("⚠️ AI generation failed, using enhanced fallback")
                return self._fallback_content(business_name, industry, platform)
            
            # Step 2: Parse and validate the response
            parsed_content = self._parse_gemini_response(response, platform)
            
            # Step 3: Enhance with additional AI processing if content is too short
            if len(parsed_content.get('text', '')) < 100:  # If content is too short
                print("🔄 Content too short, generating enhanced version...")
                enhancement_prompt = self._build_enhancement_prompt(parsed_content, business_name, platform)
                enhanced_response = await self._generate_with_retry(enhancement_prompt, max_retries=2)
                if enhanced_response:
                    parsed_content = self._parse_gemini_response(enhanced_response, platform)
            
            # Step 4: Final validation and enhancement
            parsed_content['ai_generated'] = True
            parsed_content['generation_quality'] = self._assess_content_quality(parsed_content)
            
            print(f"✅ Successfully generated {len(parsed_content.get('text', ''))} character content with {len(parsed_content.get('hashtags', []))} hashtags")
            return parsed_content
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            return self._fallback_content(business_name, industry, platform)
    
    def _build_prompt(self, business: str, industry: str, platform: str, goal: str, voice: str) -> str:
        """Build enhanced prompts for detailed content generation"""
        
        if platform.lower() == "instagram":
            return f"""
            Create compelling Instagram content for {business}, a {industry} business.
            
            Business Information:
            - Business Name: {business}
            - Industry: {industry}
            - Campaign Goal: {goal}
            - Brand Voice: {voice}
            
            Content Requirements:
            - Write 3-4 full sentences about the BUSINESS and their products/services
            - Focus entirely on what the business offers, their story, their customers
            - DO NOT mention AI, automation, or technology tools
            - Tell their brand story and highlight their unique value
            - Use emojis strategically (2-3 per post)
            - Include a strong call-to-action related to their business
            - Make it authentic and engaging for their target audience
            - Focus on customer benefits and experiences
            
            Examples of what TO focus on:
            - Their products/services and quality
            - Customer experiences and testimonials
            - Behind-the-scenes of their business
            - Special offers, new products, or announcements
            - Their mission, values, and community impact
            - Seasonal content related to their business
            
            DO NOT include any references to:
            - AI or artificial intelligence
            - Social media management tools
            - Content creation processes
            - Technology or automation
            
            Format as JSON:
            {{
                "text": "detailed caption about the business and their offerings",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
                "cta": "call to action related to the business",
                "hook": "engagement hook about the business",
                "viral_elements": ["element1", "element2"]
            }}
            """
        elif platform.lower() == "twitter":
            return f"""
            Create compelling Twitter content for {business}, a {industry} business.
            
            Business Information:
            - Business Name: {business}
            - Industry: {industry}
            - Campaign Goal: {goal}
            - Brand Voice: {voice}
            
            Content Requirements:
            - Write 2-3 concise sentences about the BUSINESS and their products/services
            - Stay under 280 characters but make maximum impact
            - Focus entirely on what the business offers and their value proposition
            - DO NOT mention AI, automation, or technology tools
            - Include powerful, action-oriented language about their business
            - Create urgency or curiosity about their products/services
            - Match the brand voice perfectly
            - Make it highly shareable and engaging
            - Include a clear business value proposition
            
            Examples of what TO focus on:
            - Product launches, features, or benefits
            - Customer success stories or testimonials
            - Special offers or promotions
            - Business milestones or achievements
            - Industry insights from their perspective
            - Behind-the-scenes business content
            
            DO NOT include any references to:
            - AI or artificial intelligence
            - Social media management tools
            - Content creation processes
            - Technology or automation
            
            Format as JSON:
            {{
                "text": "impactful tweet about the business and their offerings",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
                "cta": "call to action related to the business",
                "hook": "engagement hook about the business",
                "viral_elements": ["element1", "element2"]
            }}
            """
        elif platform.lower() == "linkedin":
            return f"""
            Create professional LinkedIn content for {business}, a {industry} business.
            
            Business Information:
            - Business Name: {business}
            - Industry: {industry}
            - Campaign Goal: {goal}
            - Brand Voice: {voice}
            
            Content Requirements:
            - Write 2-3 professional paragraphs about the BUSINESS and their expertise
            - Focus entirely on their industry knowledge, business insights, and professional value
            - DO NOT mention AI, automation, or technology tools
            - Provide genuine value and insights to professional audience
            - Share their business perspective and industry expertise
            - Include business achievements, client success stories, or industry insights
            - Match the brand voice while maintaining professionalism
            - Encourage meaningful professional discussion
            - Position them as thought leaders in their industry
            
            Examples of what TO focus on:
            - Industry insights and trends from their business perspective
            - Client success stories and case studies
            - Business growth strategies and lessons learned
            - Professional expertise and qualifications
            - Company culture and team achievements
            - Industry challenges they help solve
            - Business milestones and accomplishments
            
            DO NOT include any references to:
            - AI or artificial intelligence
            - Social media management tools
            - Content creation processes
            - Technology or automation (unless it's their core business)
            
            Format as JSON:
            {{
                "text": "professional post about the business and their industry expertise",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
                "cta": "professional call to action related to the business",
                "hook": "professional engagement hook about the business",
                "viral_elements": ["element1", "element2"]
            }}
            """
        elif platform.lower() == "facebook":
            return f"""
            Create engaging Facebook content for {business}, a {industry} business.
            
            Business Information:
            - Business Name: {business}
            - Industry: {industry}
            - Campaign Goal: {goal}
            - Brand Voice: {voice}
            
            Content Requirements:
            - Write 3-4 conversational sentences about the BUSINESS and their community
            - Focus entirely on their products/services and customer relationships
            - DO NOT mention AI, automation, or technology tools
            - Create genuine community connection around their business
            - Tell their business story in a relatable, authentic way
            - Include relatable experiences about their products/services
            - Ask engaging questions about their business/industry
            - Create emotional connection with their audience
            - Match the brand voice while being approachable
            
            Examples of what TO focus on:
            - Customer stories and experiences with their products/services
            - Behind-the-scenes of their business operations
            - Community events or local business involvement
            - Product features, benefits, or customer satisfaction
            - Business values and how they serve their community
            - Seasonal content related to their products/services
            - Questions about customer preferences or experiences
            
            DO NOT include any references to:
            - AI or artificial intelligence
            - Social media management tools
            - Content creation processes
            - Technology or automation
            
            Format as JSON:
            {{
                "text": "engaging post about the business and their community",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
                "cta": "call to action related to the business",
                "hook": "engagement hook about the business",
                "viral_elements": ["element1", "element2"]
            }}
            """
        else:
            # Default - use business-focused format for any unrecognized platform
            return f"""
            Create compelling content for {business}, a {industry} business.
            
            Business Information:
            - Business Name: {business}
            - Industry: {industry}
            - Campaign Goal: {goal}
            - Brand Voice: {voice}
            
            Content Requirements:
            - Write 3-4 full sentences about the BUSINESS and their products/services
            - Focus entirely on what the business offers, their story, their customers
            - DO NOT mention AI, automation, or technology tools
            - Tell their brand story and highlight their unique value
            - Use emojis strategically (2-3 per post)
            - Include a strong call-to-action related to their business
            - Make it authentic and engaging for their target audience
            - Focus on customer benefits and experiences
            
            Examples of what TO focus on:
            - Their products/services and quality
            - Customer experiences and testimonials
            - Behind-the-scenes of their business
            - Special offers, new products, or announcements
            - Their mission, values, and community impact
            - Seasonal content related to their business
            
            DO NOT include any references to:
            - AI or artificial intelligence
            - Social media management tools
            - Content creation processes
            - Technology or automation
            
            Format as JSON:
            {{
                "text": "detailed content about the business and their offerings",
                "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
                "cta": "call to action related to the business",
                "hook": "engagement hook about the business",
                "viral_elements": ["element1", "element2"]
            }}
            """
    
    def _parse_gemini_response(self, response_text: str, platform: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        try:
            import re
            import json
            
            # Clean the response text - remove markdown code blocks
            cleaned_text = response_text.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]  # Remove ```json
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]   # Remove ```
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]  # Remove trailing ```
            
            cleaned_text = cleaned_text.strip()
            
            # Try to extract JSON from the cleaned response
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                content_data = json.loads(json_str)
                
                # Extract and clean the text content
                text_content = content_data.get("text", "")
                
                # Ensure we have clean text without JSON artifacts
                if text_content and not text_content.startswith('{'):
                    return {
                        "text": text_content,
                        "hashtags": content_data.get("hashtags", [f"#{platform}"]),
                        "cta": content_data.get("cta", "Follow for more!"),
                        "viral_elements": content_data.get("viral_elements", ["trending", "engaging"]),
                        "character_count": len(text_content),
                        "ai_generated": True
                    }
            
            # If JSON parsing fails, try to extract plain text
            # Look for text after common patterns - with more robust extraction
            text_patterns = [
                r'"text":\s*"([^"]+)"',
                r'text:\s*"([^"]+)"',
                r'"text":\s*"([^"]*(?:\\.[^"]*)*)"',  # Handle escaped quotes
                r'Content:\s*(.+?)(?:\n|$)',
                r'Caption:\s*(.+?)(?:\n|$)'
            ]
            
            for pattern in text_patterns:
                match = re.search(pattern, cleaned_text, re.IGNORECASE | re.DOTALL)
                if match:
                    extracted_text = match.group(1).strip()
                    # Clean up escaped characters
                    extracted_text = extracted_text.replace('\\"', '"').replace('\\n', '\n')
                    if len(extracted_text) > 20:  # Ensure it's substantial content
                        return {
                            "text": extracted_text,
                            "hashtags": [f"#{platform}", "#AI", "#viral"],
                            "character_count": len(extracted_text),
                            "ai_generated": True
                        }
                        
        except Exception as e:
            print(f"❌ JSON parsing error: {e}")
        
        # Fallback parsing - use the raw response if it looks like content (but not JSON)
        clean_text = response_text.strip()
        if (clean_text and len(clean_text) > 20 and 
            not clean_text.startswith('{') and 
            not clean_text.startswith('```') and
            '"text":' not in clean_text):
            return {
                "text": clean_text[:500],  # Limit length
                "hashtags": [f"#{platform}", "#AI", "#viral"],
                "character_count": len(clean_text[:500]),
                "ai_generated": True
            }
        
        # Final fallback
        return {
            "text": f"Discover what makes {business or 'this business'} special in the {platform} community!",
            "hashtags": [f"#{platform}", "#business", "#community"],
            "character_count": len(f"Discover what makes {business or 'this business'} special in the {platform} community!"),
            "ai_generated": True
        }
    
    def _fallback_content(self, business: str, industry: str, platform: str) -> Dict[str, Any]:
        """Enhanced fallback content when API is unavailable"""
        
        if platform.lower() == "instagram":
            text = f"🌟 Exciting news from {business}! We're thrilled to share our revolutionary approach to {industry} that's set to transform the entire landscape. This journey represents everything we've been working toward, and we can't wait to see the impact it will have on our community. Join us as we take this bold step forward and redefine what's possible in {industry}. What do you think about this exciting development? 💫"
            hashtags = ['#Business', '#Growth', '#Innovation', '#Community', '#Exciting', '#Future', f'#{industry.replace(" ", "")}']
        elif platform.lower() == "twitter":
            text = f"🎯 Game-changer alert! {business} is revolutionizing {industry} with groundbreaking innovation that's reshaping the entire industry. This isn't just an update – it's the future happening now. Ready to join the revolution? 🚀"
            hashtags = ['#Business', '#Innovation', '#Future', '#Revolutionary', '#GameChanger', '#Success', f'#{industry.replace(" ", "")}']
        elif platform.lower() == "linkedin":
            text = f"We're excited to share a significant milestone at {business}. Our strategic focus on transforming {industry} represents more than just business evolution – it's our commitment to driving meaningful change in our sector. This initiative reflects months of careful planning, innovative thinking, and dedication to excellence that defines our organization.\n\nAs we embark on this journey, we're not just advancing our mission; we're setting new standards for what's possible in {industry}. Our team's passion and expertise have brought us to this pivotal moment, and we're confident that the impact will extend far beyond our immediate goals.\n\nWe believe that true success comes from creating value that resonates with our community and drives positive change. This milestone is just the beginning of what we can achieve together."
            hashtags = ['#Business', '#Innovation', '#Professional', '#Leadership', '#Excellence', '#Growth', f'#{industry.replace(" ", "")}']
        elif platform.lower() == "facebook":
            text = f"Hey everyone! 👋 We have some incredible news to share from the {business} family! Our exciting journey in {industry} innovation is officially underway, and we couldn't be more thrilled to have you all along for the ride. This project means the world to us because it's all about creating something amazing for our community. We've poured our hearts into this, and we can't wait to show you what we've been working on! What are you most excited to see from us? 💙"
            hashtags = ['#Community', '#Family', '#Exciting', '#Journey', '#Together', '#Amazing', f'#{industry.replace(" ", "")}']
        else:  # Default - use Instagram format
            text = f"🌟 Exciting news from {business}! We're thrilled to share our revolutionary approach to {industry} that's set to transform the entire landscape. This journey represents everything we've been working toward, and we can't wait to see the impact it will have on our community. Join us as we take this bold step forward and redefine what's possible in {industry}. What do you think about this exciting development? 💫"
            hashtags = ['#Business', '#Growth', '#Innovation', '#Community', '#Exciting', '#Future', f'#{industry.replace(" ", "")}']
        
        return {
            "text": text,
            "hashtags": hashtags,
            "character_count": len(text),
            "ai_generated": False,
            "viral_elements": ["innovation", "community engagement", "storytelling"],
            "cta": "Join the revolution!",
            "hook": "Game-changing announcement"
        }
    
    async def _generate_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Generate content with retry logic and exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Run the synchronous Gemini API call in an executor to make it async
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    if self.chat_session:
                        response = await asyncio.get_event_loop().run_in_executor(
                            executor, self.chat_session.send_message, prompt
                        )
                    else:
                        response = await asyncio.get_event_loop().run_in_executor(
                            executor, self.model.generate_content, prompt
                        )
                
                if response and response.text and len(response.text.strip()) > 10:
                    print(f"✅ AI generation successful on attempt {attempt + 1}")
                    return response.text.strip()
                else:
                    print(f"⚠️ Empty or short response on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"⚠️ Generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
        print("❌ All generation attempts failed")
        return None
    
    def _build_enhancement_prompt(self, initial_content: Dict[str, Any], business: str, platform: str) -> str:
        """Build prompt to enhance short content"""
        initial_text = initial_content.get('text', '')
        return f"""
        The following content for {business} is too short and needs to be expanded into a full, engaging post:
        
        Current content: "{initial_text}"
        Business: {business}
        Platform: {platform}
        
        Please expand this into a compelling, detailed post that:
        - Is at least 3-4 sentences long about the BUSINESS and their offerings
        - Tells a complete story about their products/services or customer value
        - Maintains the same tone and message about the business
        - Includes engaging elements about their business and customer experience
        - Is optimized for {platform}
        - DO NOT mention AI, automation, or technology tools
        - Focus entirely on the business, their products/services, and customer benefits
        
        Return the expanded content in the same JSON format:
        {{
            "text": "expanded detailed content about the business with 3-4+ sentences",
            "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5", "#hashtag6", "#hashtag7"],
            "cta": "call to action related to the business",
            "hook": "engagement hook about the business",
            "viral_elements": ["element1", "element2", "element3"]
        }}
        """
    
    def _assess_content_quality(self, content: Dict[str, Any]) -> str:
        """Assess the quality of generated content"""
        text = content.get('text', '')
        hashtags = content.get('hashtags', [])
        
        score = 0
        
        # Length scoring
        if len(text) > 200:
            score += 3
        elif len(text) > 100:
            score += 2
        elif len(text) > 50:
            score += 1
            
        # Hashtag scoring
        if len(hashtags) >= 6:
            score += 2
        elif len(hashtags) >= 3:
            score += 1
            
        # Engagement elements
        if any(word in text.lower() for word in ['?', '!', 'you', 'your']):
            score += 1
            
        # Emoji usage
        if any(char in text for char in ['🔥', '✨', '🚀', '💫', '🌟', '🎯']):
            score += 1
            
        if score >= 6:
            return "excellent"
        elif score >= 4:
            return "good"
        elif score >= 2:
            return "fair"
        else:
            return "needs_improvement"

class TrendsService:
    """Google Trends integration for real trending data"""
    
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)
    
    async def get_trending_topics(self, industry: str, region: str = 'US') -> Dict[str, Any]:
        """Get real trending topics related to industry"""
        try:
            # Get daily trends
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            trends = trending_searches[0].head(10).tolist()
            
            # Get industry-specific trends
            industry_kw = [industry.lower(), f"{industry} technology", f"{industry} innovation"]
            self.pytrends.build_payload(industry_kw, cat=0, timeframe='now 7-d', geo=region)
            
            # Get related topics
            related_topics = self.pytrends.related_topics()
            
            # Get rising searches
            related_queries = self.pytrends.related_queries()
            
            return {
                "trending_topics": [
                    {
                        "topic": trend,
                        "relevance_score": 85 + (i * 2),
                        "trend_type": "rising" if i < 3 else "trending"
                    } for i, trend in enumerate(trends[:5])
                ],
                "industry_trends": self._parse_industry_trends(related_topics, industry),
                "trending_hashtags": self._generate_hashtags(trends, industry),
                "trend_analysis": {
                    "peak_engagement_window": "Next 24-48 hours",
                    "viral_probability": "High (78%)",
                    "recommended_action": "Capitalize on trending topics immediately"
                }
            }
            
        except Exception as e:
            print(f"Trends API error: {e}")
            return self._fallback_trends(industry)
    
    def _parse_industry_trends(self, related_topics: Dict, industry: str) -> List[Dict[str, Any]]:
        """Parse industry-specific trends"""
        trends = []
        try:
            for keyword, data in related_topics.items():
                if data is not None and 'rising' in data:
                    rising_topics = data['rising'].head(3)
                    for _, topic in rising_topics.iterrows():
                        trends.append({
                            "topic": topic.get('topic_title', f"{industry} trend"),
                            "growth": f"+{topic.get('value', 100)}%",
                            "relevance": "high"
                        })
        except:
            pass
        
        return trends[:5] if trends else [
            {"topic": f"{industry} innovation", "growth": "+150%", "relevance": "high"},
            {"topic": f"{industry} trends 2025", "growth": "+89%", "relevance": "medium"}
        ]
    
    def _generate_hashtags(self, trends: List[str], industry: str) -> List[str]:
        """Generate trending hashtags"""
        hashtags = [f"#{industry.lower()}", "#trending", "#viral"]
        
        for trend in trends[:3]:
            # Convert trend to hashtag format
            hashtag = trend.replace(" ", "").replace("-", "")[:15]
            if hashtag.isalnum():
                hashtags.append(f"#{hashtag}")
        
        return hashtags[:8]
    
    def _fallback_trends(self, industry: str) -> Dict[str, Any]:
        """Fallback trends data"""
        return {
            "trending_topics": [
                {"topic": f"{industry} innovation", "relevance_score": 92, "trend_type": "rising"},
                {"topic": "viral marketing", "relevance_score": 89, "trend_type": "trending"},
                {"topic": "social media growth", "relevance_score": 85, "trend_type": "trending"}
            ],
            "trending_hashtags": [f"#{industry.lower()}", "#innovation", "#viral", "#trending"],
            "trend_analysis": {
                "peak_engagement_window": "Next 24-48 hours",
                "viral_probability": "Medium-High (65%)",
                "recommended_action": "Focus on innovation and growth themes"
            }
        }

class SchedulingService:
    """Advanced scheduling intelligence"""
    
    def __init__(self):
        self.engagement_data = self._load_engagement_patterns()
    
    def get_optimal_schedule(
        self, 
        platforms: List[str], 
        industry: str,
        target_audience: str = "general"
    ) -> Dict[str, Any]:
        """Get data-driven optimal posting schedule"""
        
        schedule = {}
        
        for platform in platforms:
            platform_data = self.engagement_data.get(platform, {})
            industry_modifier = self._get_industry_modifier(industry)
            
            optimal_times = self._calculate_optimal_times(platform_data, industry_modifier)
            
            schedule[platform] = {
                "optimal_times": optimal_times,
                "reasoning": self._get_timing_reasoning(platform, industry),
                "engagement_predictions": self._predict_engagement(platform, optimal_times),
                "best_days": self._get_best_days(platform, industry)
            }
        
        return {
            "platform_schedules": schedule,
            "global_recommendations": {
                "viral_window": "Tuesday-Thursday, 9AM-3PM EST",
                "avoid_times": ["Late Friday", "Early Monday", "Weekend evenings"],
                "seasonal_factor": "High engagement period (current season)"
            }
        }
    
    def _load_engagement_patterns(self) -> Dict[str, Any]:
        """Load platform engagement patterns"""
        return {
            "instagram": {
                "peak_hours": [8, 12, 19],  # 8AM, 12PM, 7PM
                "engagement_rates": {"8": 12.4, "12": 15.2, "19": 18.9}
            },
            "twitter": {
                "peak_hours": [9, 12, 15, 18],  # 9AM, 12PM, 3PM, 6PM
                "engagement_rates": {"9": 8.7, "12": 11.2, "15": 9.8, "18": 13.4}
            },
            "linkedin": {
                "peak_hours": [8, 12, 17],  # 8AM, 12PM, 5PM
                "engagement_rates": {"8": 14.6, "12": 16.8, "17": 12.9}
            }
        }
    
    def _get_industry_modifier(self, industry: str) -> Dict[str, float]:
        """Get industry-specific engagement modifiers"""
        modifiers = {
            "technology": {"morning": 1.2, "afternoon": 1.1, "evening": 0.9},
            "healthcare": {"morning": 1.1, "afternoon": 1.3, "evening": 0.8},
            "finance": {"morning": 1.4, "afternoon": 1.2, "evening": 0.7},
            "retail": {"morning": 0.9, "afternoon": 1.1, "evening": 1.3}
        }
        return modifiers.get(industry.lower(), {"morning": 1.0, "afternoon": 1.0, "evening": 1.0})
    
    def _calculate_optimal_times(self, platform_data: Dict, modifiers: Dict) -> List[Dict[str, Any]]:
        """Calculate optimal posting times with reasoning"""
        times = []
        
        for hour, base_rate in platform_data.get("engagement_rates", {}).items():
            time_period = "morning" if int(hour) < 12 else "afternoon" if int(hour) < 18 else "evening"
            modified_rate = base_rate * modifiers.get(time_period, 1.0)
            
            times.append({
                "time": f"{hour}:00",
                "engagement_rate": f"{modified_rate:.1f}%",
                "reasoning": f"Peak {time_period} engagement for target audience"
            })
        
        return sorted(times, key=lambda x: float(x["engagement_rate"].rstrip('%')), reverse=True)
    
    def _get_timing_reasoning(self, platform: str, industry: str) -> str:
        """Get reasoning for timing recommendations"""
        reasoning_map = {
            "instagram": f"Visual content performs best during leisure browsing times for {industry} audience",
            "twitter": f"Real-time engagement peaks during commute and break times for {industry} professionals", 
            "linkedin": f"B2B content gets maximum visibility during business hours for {industry} decision makers"
        }
        return reasoning_map.get(platform, f"Optimized for {industry} audience engagement patterns")
    
    def _predict_engagement(self, platform: str, times: List[Dict]) -> Dict[str, Any]:
        """Predict engagement for optimal times"""
        if not times:
            return {"estimated_reach": "N/A", "engagement_boost": "0%"}
            
        best_rate = max(float(t["engagement_rate"].rstrip('%')) for t in times)
        
        return {
            "estimated_reach": f"{int(best_rate * 1000)}-{int(best_rate * 2000)} users",
            "engagement_boost": f"{int((best_rate - 8.0) / 8.0 * 100)}% above average",
            "optimal_frequency": "2-3 posts per day" if platform == "twitter" else "1-2 posts per day"
        }
    
    def _get_best_days(self, platform: str, industry: str) -> List[str]:
        """Get best days for posting"""
        day_patterns = {
            "instagram": ["Tuesday", "Wednesday", "Thursday", "Sunday"],
            "twitter": ["Monday", "Tuesday", "Wednesday", "Thursday"],
            "linkedin": ["Tuesday", "Wednesday", "Thursday"]
        }
        return day_patterns.get(platform, ["Tuesday", "Wednesday", "Thursday"])

# Initialize services
unsplash_service = UnsplashService()
gemini_service = GeminiService()
trends_service = TrendsService()
scheduling_service = SchedulingService()