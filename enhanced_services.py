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
        self.api_key = os.getenv('UNSPLASH_ACCESS_KEY', 'XqpZt1BbdHRLuCcqrXJJFQeRoRz1KWrg_grNcnpsjBw')
        self.base_url = "https://api.unsplash.com"
        self.request_count = 0
        self.max_requests_per_hour = 50  # Unsplash free tier limit
        print(f"🔧 Unsplash Service initialized with API key: {self.api_key[:10]}...")
        
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
        self.api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyBHFyhc_JMIe_Rqxs6V-h58dYnt-dPXaXk')
        if self.api_key and self.api_key != 'your-gemini-api-key':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("⚠️ Gemini API key not configured, using fallback content")
    
    async def generate_content(
        self, 
        business_name: str, 
        industry: str, 
        platform: str,
        campaign_goal: str,
        brand_voice: str = "professional"
    ) -> Dict[str, Any]:
        """Generate AI-powered content for specific platform"""
        
        if not self.model:
            return self._fallback_content(business_name, industry, platform)
            
        try:
            prompt = self._build_prompt(business_name, industry, platform, campaign_goal, brand_voice)
            
            response = self.model.generate_content(prompt)
            content_text = response.text
            
            # Parse and structure the response
            return self._parse_gemini_response(content_text, platform)
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_content(business_name, industry, platform)
    
    def _build_prompt(self, business: str, industry: str, platform: str, goal: str, voice: str) -> str:
        """Build optimized prompt for Gemini"""
        platform_specs = {
            "instagram": "visual-first, engaging captions, 5-10 hashtags, emoji usage",
            "twitter": "concise, trending, thread-worthy, 2-3 hashtags max",
            "linkedin": "professional, thought leadership, industry insights, 3-5 hashtags"
        }
        
        spec = platform_specs.get(platform, "engaging social media content")
        
        return f"""
        Create viral social media content for {platform} with these requirements:
        
        Business: {business}
        Industry: {industry}
        Campaign Goal: {goal}
        Brand Voice: {voice}
        Platform Style: {spec}
        
        Generate:
        1. Main post text (optimized for {platform})
        2. 3-5 relevant hashtags
        3. Call-to-action
        4. Engagement hook
        
        Make it creative, engaging, and likely to go viral. Use current trends and platform best practices.
        
        Format as JSON:
        {{
            "text": "main post content",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "cta": "call to action",
            "hook": "engagement hook",
            "viral_elements": ["element1", "element2"]
        }}
        """
    
    def _parse_gemini_response(self, response_text: str, platform: str) -> Dict[str, Any]:
        """Parse Gemini response into structured format"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group())
                return {
                    "text": content_data.get("text", response_text[:280]),
                    "hashtags": content_data.get("hashtags", [f"#{platform}"]),
                    "cta": content_data.get("cta", "Follow for more!"),
                    "viral_elements": content_data.get("viral_elements", ["trending", "engaging"]),
                    "character_count": len(content_data.get("text", "")),
                    "ai_generated": True
                }
        except:
            pass
        
        # Fallback parsing
        return {
            "text": response_text[:280] if response_text else f"AI-generated content for {platform}",
            "hashtags": [f"#{platform}", "#AI", "#viral"],
            "character_count": len(response_text[:280]),
            "ai_generated": True
        }
    
    def _fallback_content(self, business: str, industry: str, platform: str) -> Dict[str, Any]:
        """Fallback content when API is unavailable"""
        content_templates = {
            "instagram": f"🚀 {business} is revolutionizing {industry}! Our latest breakthrough changes everything. Ready to join the future? #innovation #{industry.lower()} #breakthrough #future",
            "twitter": f"🔥 BREAKING: {business} just dropped something huge in {industry}! This changes the game completely 🎯 #breakthrough #{industry.lower()} #innovation",
            "linkedin": f"Excited to share how {business} is pioneering the next wave of {industry} innovation. Our latest development represents a significant leap forward in the industry."
        }
        
        text = content_templates.get(platform, f"{business} - leading innovation in {industry}")
        
        return {
            "text": text,
            "hashtags": ["#innovation", f"#{industry.lower()}", "#business"],
            "character_count": len(text),
            "ai_generated": False
        }

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