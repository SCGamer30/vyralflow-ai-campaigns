import httpx
from typing import List, Dict, Any, Optional
import asyncio
from urllib.parse import urlencode

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UnsplashService:
    """Service for Unsplash API interactions."""
    
    def __init__(self):
        """Initialize Unsplash service."""
        self.base_url = "https://api.unsplash.com"
        self.access_key = settings.unsplash_access_key
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Unsplash service initialized successfully")
    
    async def search_photos(
        self,
        query: str,
        per_page: int = 10,
        orientation: str = "landscape"
    ) -> List[Dict[str, Any]]:
        """Search for photos on Unsplash."""
        try:
            params = {
                'query': query,
                'per_page': min(per_page, 30),  # Unsplash API limit
                'orientation': orientation,
                'order_by': 'relevant'
            }
            
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            url = f"{self.base_url}/search/photos?{urlencode(params)}"
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            photos = data.get('results', [])
            
            # Process and format the photos
            formatted_photos = []
            for photo in photos:
                formatted_photo = {
                    'id': photo.get('id'),
                    'description': photo.get('description') or photo.get('alt_description', ''),
                    'urls': {
                        'small': photo.get('urls', {}).get('small'),
                        'regular': photo.get('urls', {}).get('regular'),
                        'full': photo.get('urls', {}).get('full')
                    },
                    'user': {
                        'name': photo.get('user', {}).get('name'),
                        'username': photo.get('user', {}).get('username'),
                        'profile_url': photo.get('user', {}).get('links', {}).get('html')
                    },
                    'likes': photo.get('likes', 0),
                    'color': photo.get('color'),
                    'tags': [tag.get('title') for tag in photo.get('tags', [])],
                    'download_url': photo.get('links', {}).get('download')
                }
                formatted_photos.append(formatted_photo)
            
            logger.info(f"Retrieved {len(formatted_photos)} photos for query: {query}")
            return formatted_photos
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                logger.warning("Unsplash API rate limit exceeded, using fallback")
                return self._get_fallback_photos(query, per_page)
            else:
                logger.error(f"Unsplash API error: {e}")
                raise ExternalAPIException("unsplash", f"HTTP {e.response.status_code}: {e}")
        except Exception as e:
            logger.error(f"Failed to search Unsplash photos: {e}")
            return self._get_fallback_photos(query, per_page)
    
    async def get_photo_suggestions(
        self,
        business_name: str,
        industry: str,
        campaign_goal: str,
        visual_themes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get photo suggestions based on campaign context."""
        try:
            # Generate search queries based on context
            search_queries = self._generate_search_queries(
                business_name, industry, campaign_goal, visual_themes
            )
            
            all_photos = []
            
            # Search for photos using different queries
            for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
                photos = await self.search_photos(query, per_page=5)
                all_photos.extend(photos)
                
                # Add small delay between requests
                await asyncio.sleep(0.5)
            
            # Remove duplicates and sort by relevance
            unique_photos = self._deduplicate_photos(all_photos)
            
            # Score and sort photos
            scored_photos = self._score_photos(unique_photos, search_queries)
            
            return scored_photos[:15]  # Return top 15
            
        except Exception as e:
            logger.error(f"Failed to get photo suggestions: {e}")
            return self._get_fallback_photo_suggestions(industry, campaign_goal)
    
    def _generate_search_queries(
        self,
        business_name: str,
        industry: str,
        campaign_goal: str,
        visual_themes: Optional[List[str]] = None
    ) -> List[str]:
        """Generate search queries for photo suggestions."""
        queries = []
        
        # Dynamic industry-based queries for variety
        import random
        import time
        
        # Create unique seed for different results each time
        seed = hash(f"{business_name}_{campaign_goal}_{int(time.time() / 3600)}")
        random.seed(seed)
        
        industry_keyword_options = {
            'food & beverage': [
                ['coffee beans', 'espresso cup', 'cafe interior', 'coffee brewing'],
                ['fresh coffee', 'coffee shop', 'barista', 'coffee roasting'],
                ['coffee mug', 'latte art', 'coffee culture', 'artisan coffee'],
                ['organic coffee', 'coffee plantation', 'coffee grinder', 'specialty coffee']
            ],
            'technology': [
                ['modern office', 'tech startup', 'computer setup', 'digital workspace'],
                ['laptop coding', 'software development', 'tech innovation', 'programmer'],
                ['tech meeting', 'digital transformation', 'modern technology', 'innovation hub']
            ],
            'retail': [
                ['modern store', 'shopping experience', 'retail display', 'boutique interior'],
                ['product showcase', 'customer shopping', 'retail business', 'store front'],
                ['brand display', 'shopping lifestyle', 'retail design', 'commerce']
            ],
            'healthcare': [
                ['healthcare', 'medical', 'wellness', 'health professional'],
                ['clinic', 'fitness', 'health', 'medical technology'],
                ['wellness center', 'care', 'treatment', 'healthy lifestyle']
            ],
            'finance': [
                ['finance', 'business', 'investment', 'financial'],
                ['banking', 'money', 'professional', 'wealth'],
                ['financial planning', 'growth', 'success', 'advisor']
            ],
            'education': [
                ['education', 'learning', 'student', 'academic'],
                ['classroom', 'books', 'study', 'knowledge'],
                ['online learning', 'teaching', 'school', 'educational']
            ],
            'real estate': [
                ['real estate', 'property', 'home', 'house'],
                ['architecture', 'building', 'residential', 'commercial'],
                ['luxury', 'modern home', 'interior', 'design']
            ],
            'automotive': [
                ['automotive', 'cars', 'vehicles', 'transportation'],
                ['driving', 'auto', 'car dealership', 'modern car'],
                ['electric vehicle', 'innovation', 'automotive design', 'performance']
            ]
        }
        
        # Create business-specific queries first
        business_type_keywords = []
        business_lower = business_name.lower()
        
        # Detect business type from name for more targeted searches
        if any(word in business_lower for word in ['cafe', 'coffee', 'espresso', 'brew']):
            business_type_keywords = ['coffee shop interior', 'coffee beans close up', 'espresso machine']
        elif any(word in business_lower for word in ['restaurant', 'bistro', 'eatery']):
            business_type_keywords = ['restaurant interior', 'food plating', 'dining experience']
        elif any(word in business_lower for word in ['bakery', 'pastry', 'bread']):
            business_type_keywords = ['fresh bread', 'bakery interior', 'artisan pastry']
        elif any(word in business_lower for word in ['tech', 'software', 'app', 'digital']):
            business_type_keywords = ['modern office space', 'tech workspace', 'software development']
        elif any(word in business_lower for word in ['boutique', 'fashion', 'style']):
            business_type_keywords = ['boutique interior', 'fashion display', 'clothing store']
        
        # Add business-specific queries if detected
        if business_type_keywords:
            queries.extend(business_type_keywords[:2])
        
        # Select random keyword sets for variety
        industry_options = industry_keyword_options.get(industry.lower(), [['business', 'professional']])
        selected_option = random.choice(industry_options)
        queries.extend(selected_option[:2])
        
        # Dynamic campaign goal-based queries
        goal_keywords = {
            'promote': ['marketing', 'promotion', 'advertising', 'brand visibility'],
            'launch': ['product launch', 'new business', 'startup', 'innovation'],
            'sale': ['sale', 'discount', 'shopping', 'special offer'],
            'awareness': ['brand awareness', 'visibility', 'recognition', 'outreach'],
            'growth': ['business growth', 'expansion', 'success', 'development'],
            'engagement': ['community', 'social media', 'interaction', 'connection']
        }
        
        # Find matching goal keywords
        goal_matches = []
        for key, keywords in goal_keywords.items():
            if key in campaign_goal.lower():
                goal_matches.extend(keywords)
        
        if goal_matches:
            queries.append(random.choice(goal_matches))
        else:
            queries.append(random.choice(['business success', 'professional growth', 'innovation']))
        
        # Enhanced visual theme queries
        if visual_themes:
            theme_variations = {
                'modern': ['modern', 'contemporary', 'sleek', 'minimalist'],
                'professional': ['professional', 'corporate', 'business', 'formal'],
                'creative': ['creative', 'artistic', 'innovative', 'unique'],
                'energetic': ['energetic', 'dynamic', 'vibrant', 'active'],
                'warm': ['warm', 'cozy', 'friendly', 'welcoming'],
                'luxurious': ['luxury', 'premium', 'elegant', 'sophisticated']
            }
            
            for theme in visual_themes[:2]:
                theme_key = theme.lower()
                if theme_key in theme_variations:
                    selected_variation = random.choice(theme_variations[theme_key])
                    if selected_variation.lower() not in [q.lower() for q in queries]:
                        queries.append(selected_variation)
                elif theme.lower() not in [q.lower() for q in queries]:
                    queries.append(theme)
        
        # Dynamic general business queries
        general_options = [
            ['professional business', 'corporate success', 'business meeting'],
            ['modern workspace', 'office environment', 'workplace'],
            ['team collaboration', 'teamwork', 'business team'],
            ['success', 'achievement', 'growth'],
            ['innovation', 'future', 'progress']
        ]
        
        selected_general = random.choice(general_options)
        queries.extend(selected_general[:1])  # Add one general query
        
        # Ensure we have enough unique queries
        unique_queries = list(dict.fromkeys(queries))  # Remove duplicates while preserving order
        return unique_queries[:6]  # Limit to 6 queries
    
    def _deduplicate_photos(self, photos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate photos."""
        seen_ids = set()
        unique_photos = []
        
        for photo in photos:
            photo_id = photo.get('id')
            if photo_id and photo_id not in seen_ids:
                seen_ids.add(photo_id)
                unique_photos.append(photo)
        
        return unique_photos
    
    def _score_photos(
        self,
        photos: List[Dict[str, Any]],
        search_queries: List[str]
    ) -> List[Dict[str, Any]]:
        """Score photos based on relevance and quality."""
        for photo in photos:
            score = 0
            
            # Quality and popularity score
            likes = photo.get('likes', 0)
            if likes > 5000:
                score += 5  # Very popular
            elif likes > 1000:
                score += 4
            elif likes > 500:
                score += 3
            elif likes > 100:
                score += 2
            elif likes > 10:
                score += 1
            
            # Description and tags relevance (enhanced scoring)
            description = (photo.get('description') or '').lower()
            alt_description = (photo.get('alt_description') or '').lower()
            tags = [tag.lower() for tag in photo.get('tags', [])]
            
            # Combined text for searching
            combined_text = f"{description} {alt_description} {' '.join(tags)}"
            
            # Higher scoring for exact query matches
            for query in search_queries:
                query_lower = query.lower()
                if query_lower in combined_text:
                    score += 5  # Exact query match
                
                query_words = query_lower.split()
                word_matches = sum(1 for word in query_words if word in combined_text)
                score += word_matches * 2  # Points per word match
            
            # Bonus for industry-specific terms
            business_terms = ['business', 'professional', 'modern', 'quality', 'premium', 'artisan', 'craft']
            food_terms = ['coffee', 'cafe', 'espresso', 'beans', 'brewing', 'barista', 'latte', 'cappuccino']
            
            if any(term in combined_text for term in business_terms):
                score += 2
            if any(term in combined_text for term in food_terms):
                score += 3  # Extra bonus for food-related terms
            
            # Quality indicators
            if photo.get('urls', {}).get('full'):
                score += 1
            if photo.get('width', 0) >= 1920:  # High resolution
                score += 2
            
            # Penalize generic/irrelevant terms
            generic_terms = ['person holding', 'hand writing', 'whiteboard', 'meeting room', 'office worker']
            if any(term in combined_text for term in generic_terms):
                score -= 3
            
            photo['relevance_score'] = max(score, 0)  # Don't go below 0
        
        # Sort by score, then by likes as tiebreaker
        return sorted(photos, key=lambda x: (x.get('relevance_score', 0), x.get('likes', 0)), reverse=True)
    
    async def get_curated_photos(self, per_page: int = 10) -> List[Dict[str, Any]]:
        """Get curated photos from Unsplash."""
        try:
            params = {
                'per_page': min(per_page, 30),
                'order_by': 'popular'
            }
            
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            url = f"{self.base_url}/photos?{urlencode(params)}"
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            photos = response.json()
            
            # Format photos
            formatted_photos = []
            for photo in photos:
                formatted_photo = {
                    'id': photo.get('id'),
                    'description': photo.get('description') or photo.get('alt_description', ''),
                    'urls': {
                        'small': photo.get('urls', {}).get('small'),
                        'regular': photo.get('urls', {}).get('regular'),
                        'full': photo.get('urls', {}).get('full')
                    },
                    'user': {
                        'name': photo.get('user', {}).get('name'),
                        'username': photo.get('user', {}).get('username')
                    },
                    'likes': photo.get('likes', 0),
                    'color': photo.get('color'),
                    'tags': []
                }
                formatted_photos.append(formatted_photo)
            
            logger.info(f"Retrieved {len(formatted_photos)} curated photos")
            return formatted_photos
            
        except Exception as e:
            logger.error(f"Failed to get curated photos: {e}")
            return self._get_fallback_curated_photos(per_page)
    
    def _get_fallback_photos(self, query: str, per_page: int) -> List[Dict[str, Any]]:
        """Get fallback photos when API fails."""
        fallback_photos = [
            {
                'id': f'fallback_{i}',
                'description': f'Professional {query} image',
                'urls': {
                    'small': 'https://via.placeholder.com/400x300',
                    'regular': 'https://via.placeholder.com/800x600',
                    'full': 'https://via.placeholder.com/1200x900'
                },
                'user': {
                    'name': 'Stock Photo',
                    'username': 'stockphoto'
                },
                'likes': 100,
                'color': '#f0f0f0',
                'tags': [query],
                'relevance_score': 1
            }
            for i in range(min(per_page, 5))
        ]
        
        logger.warning(f"Using fallback photos for query: {query}")
        return fallback_photos
    
    def _get_fallback_photo_suggestions(
        self,
        industry: str,
        campaign_goal: str
    ) -> List[Dict[str, Any]]:
        """Get fallback photo suggestions."""
        suggestions = [
            {
                'id': 'fallback_1',
                'description': f'Professional {industry} business image',
                'urls': {
                    'small': 'https://via.placeholder.com/400x300/4a90e2/ffffff?text=Business',
                    'regular': 'https://via.placeholder.com/800x600/4a90e2/ffffff?text=Business',
                    'full': 'https://via.placeholder.com/1200x900/4a90e2/ffffff?text=Business'
                },
                'user': {'name': 'Business Stock', 'username': 'businessstock'},
                'likes': 150,
                'color': '#4a90e2',
                'tags': [industry, 'business', 'professional'],
                'relevance_score': 3
            },
            {
                'id': 'fallback_2',
                'description': f'{industry} marketing campaign visual',
                'urls': {
                    'small': 'https://via.placeholder.com/400x300/50c878/ffffff?text=Marketing',
                    'regular': 'https://via.placeholder.com/800x600/50c878/ffffff?text=Marketing',
                    'full': 'https://via.placeholder.com/1200x900/50c878/ffffff?text=Marketing'
                },
                'user': {'name': 'Marketing Images', 'username': 'marketingimages'},
                'likes': 200,
                'color': '#50c878',
                'tags': [industry, 'marketing', 'campaign'],
                'relevance_score': 2
            }
        ]
        
        logger.warning(f"Using fallback photo suggestions for {industry}")
        return suggestions
    
    def _get_fallback_curated_photos(self, per_page: int) -> List[Dict[str, Any]]:
        """Get fallback curated photos."""
        return self._get_fallback_photos('business professional', per_page)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global service instance
unsplash_service = UnsplashService()