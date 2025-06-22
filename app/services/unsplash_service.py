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
        
        # Industry-based queries
        industry_keywords = {
            'food & beverage': ['food photography', 'restaurant', 'coffee', 'dining', 'culinary'],
            'technology': ['technology', 'digital', 'modern office', 'innovation', 'computer'],
            'retail': ['shopping', 'fashion', 'store', 'products', 'retail'],
            'healthcare': ['healthcare', 'medical', 'wellness', 'fitness', 'health'],
            'finance': ['business', 'finance', 'professional', 'office', 'money'],
            'education': ['education', 'learning', 'books', 'classroom', 'study'],
            'real estate': ['real estate', 'home', 'property', 'architecture', 'house'],
            'automotive': ['automotive', 'cars', 'transportation', 'vehicles', 'driving']
        }
        
        industry_terms = industry_keywords.get(industry.lower(), [industry])
        queries.extend(industry_terms[:2])
        
        # Campaign goal-based queries
        if 'promote' in campaign_goal.lower() or 'launch' in campaign_goal.lower():
            queries.append('marketing promotion')
        elif 'sale' in campaign_goal.lower() or 'discount' in campaign_goal.lower():
            queries.append('sale discount shopping')
        elif 'awareness' in campaign_goal.lower():
            queries.append('brand awareness business')
        else:
            queries.append('business success')
        
        # Visual theme queries
        if visual_themes:
            for theme in visual_themes[:2]:
                if theme.lower() not in [q.lower() for q in queries]:
                    queries.append(theme)
        
        # General business queries
        queries.extend(['professional business', 'modern workspace', 'team collaboration'])
        
        return queries[:6]  # Limit to 6 queries
    
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
            
            # Likes score (normalized)
            likes = photo.get('likes', 0)
            if likes > 1000:
                score += 3
            elif likes > 100:
                score += 2
            elif likes > 10:
                score += 1
            
            # Description relevance
            description = (photo.get('description') or '').lower()
            tags = [tag.lower() for tag in photo.get('tags', [])]
            
            for query in search_queries:
                query_words = query.lower().split()
                for word in query_words:
                    if word in description:
                        score += 2
                    if any(word in tag for tag in tags):
                        score += 1
            
            # Quality indicators
            if photo.get('urls', {}).get('full'):
                score += 1
            
            photo['relevance_score'] = score
        
        # Sort by score
        return sorted(photos, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
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