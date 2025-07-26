import httpx
from typing import List, Dict, Any, Optional
import asyncio
from urllib.parse import urlencode
import random

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class UnsplashService:
    """Service for Unsplash API interactions with AI-powered search query generation."""
    
    def __init__(self):
        """Initialize Unsplash service."""
        self.base_url = "https://api.unsplash.com"
        self.access_key = settings.unsplash_access_key
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Unsplash service initialized successfully")
    
    async def generate_ai_search_queries(
        self,
        business_name: str,
        industry: str,
        campaign_goal: str,
        visual_themes: Optional[List[str]] = None
    ) -> List[str]:
        """Generate diverse, AI-powered search queries using Gemini."""
        try:
            # Import here to avoid circular imports
            from app.services.gemini_service import gemini_service
            
            # Create a comprehensive prompt for generating diverse search queries
            themes_text = f" with themes: {', '.join(visual_themes)}" if visual_themes else ""
            
            prompt = f"""
            Generate 6 diverse, creative search queries for finding professional images on Unsplash for:
            - Business: {business_name}
            - Industry: {industry}
            - Campaign Goal: {campaign_goal}{themes_text}
            
            Requirements:
            - Each query should target different visual aspects (workspace, products, people, concepts, lifestyle, branding)
            - Use descriptive, visual keywords that photographers typically use
            - Avoid generic terms, be specific and evocative
            - Include lighting, mood, and style descriptors
            - Make queries suitable for professional marketing materials
            
            Format: Return exactly 6 queries, one per line, no numbering or bullets.
            
            Examples of good queries:
            - "modern coffee shop interior warm lighting"
            - "professional team collaboration bright office"
            - "minimalist product photography clean background"
            """
            
            response = await gemini_service.generate_content(prompt)
            
            # Parse the response and clean up queries
            queries = []
            for line in response.strip().split('\n'):
                query = line.strip()
                # Remove any numbering, bullets, or extra formatting
                query = query.lstrip('1234567890.-• ').strip()
                if query and len(query) > 5:  # Ensure meaningful queries
                    queries.append(query)
            
            # Ensure we have exactly 6 queries
            if len(queries) < 6:
                # Add fallback queries based on industry
                fallback_queries = self._get_fallback_queries(business_name, industry, campaign_goal)
                queries.extend(fallback_queries[:6-len(queries)])
            
            # Take only first 6 queries
            final_queries = queries[:6]
            
            logger.info(f"Generated {len(final_queries)} AI search queries: {final_queries}")
            return final_queries
            
        except Exception as e:
            logger.warning(f"AI query generation failed, using fallback: {e}")
            return self._get_fallback_queries(business_name, industry, campaign_goal)
    
    def _get_fallback_queries(self, business_name: str, industry: str, campaign_goal: str) -> List[str]:
        """Generate fallback search queries when AI generation fails."""
        industry_queries = {
            'food & beverage': [
                'modern restaurant interior warm lighting',
                'fresh ingredients food photography',
                'professional chef cooking kitchen',
                'cozy cafe atmosphere customers',
                'artisan food plating elegant',
                'coffee beans close up texture'
            ],
            'technology': [
                'modern tech office space clean',
                'software developer coding laptop',
                'innovative technology concept digital',
                'professional team meeting bright',
                'minimalist workspace setup modern',
                'tech startup collaboration energy'
            ],
            'retail': [
                'modern retail store interior bright',
                'shopping experience lifestyle customers',
                'product display professional lighting',
                'boutique fashion store elegant',
                'retail business owner portrait',
                'brand showcase modern design'
            ],
            'healthcare': [
                'modern medical office clean bright',
                'healthcare professional consultation',
                'wellness lifestyle healthy living',
                'medical technology innovation',
                'fitness wellness center modern',
                'health care team professional'
            ],
            'finance': [
                'professional business meeting modern',
                'financial planning consultation office',
                'modern banking interior clean',
                'business growth concept upward',
                'professional advisor client meeting',
                'financial success lifestyle modern'
            ],
            'education': [
                'modern classroom learning environment',
                'online education technology setup',
                'professional training session bright',
                'educational resources books knowledge',
                'student success learning achievement',
                'innovative learning space modern'
            ],
            'real estate': [
                'modern home interior design luxury',
                'real estate agent professional meeting',
                'beautiful property architecture exterior',
                'luxury living room staging bright',
                'professional property showcase',
                'modern residential architecture clean'
            ],
            'automotive': [
                'modern car showroom professional',
                'automotive technology innovation',
                'professional mechanic service clean',
                'luxury vehicle interior detail',
                'automotive business professional team',
                'modern auto dealership bright'
            ]
        }
        
        return industry_queries.get(industry.lower(), [
            f'{industry} business professional modern',
            f'{business_name} workspace bright clean',
            f'professional {industry} team collaboration',
            f'modern {industry} office interior',
            f'{industry} innovation technology concept',
            f'successful {industry} business lifestyle'
        ])

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
                    'description': photo.get('description') or photo.get('alt_description', f'Professional {query} image'),
                    'url': photo.get('urls', {}).get('regular'),
                    'unsplash_url': photo.get('urls', {}).get('regular'),
                    'small_url': photo.get('urls', {}).get('small'),
                    'thumb_url': photo.get('urls', {}).get('thumb'),
                    'full_url': photo.get('urls', {}).get('full'),
                    'photographer': photo.get('user', {}).get('name'),
                    'photographer_username': photo.get('user', {}).get('username'),
                    'photographer_url': photo.get('user', {}).get('links', {}).get('html'),
                    'likes': photo.get('likes', 0),
                    'color': photo.get('color'),
                    'width': photo.get('width', 0),
                    'height': photo.get('height', 0),
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
        """Get AI-curated photo suggestions based on campaign context."""
        try:
            # Generate diverse AI-powered search queries
            search_queries = await self.generate_ai_search_queries(
                business_name, industry, campaign_goal, visual_themes
            )
            
            all_photos = []
            
            # Search for photos using AI-generated queries
            for i, query in enumerate(search_queries):
                try:
                    photos = await self.search_photos(query, per_page=2)  # Get 2 per query for variety
                    if photos:
                        # Add query context to photos for better tracking
                        for photo in photos:
                            photo['search_query'] = query
                            photo['query_index'] = i
                        all_photos.extend(photos)
                    
                    # Add small delay between requests to be respectful to API
                    await asyncio.sleep(0.3)
                    
                except Exception as e:
                    logger.warning(f"Search failed for query '{query}': {e}")
                    continue
            
            # Remove duplicates and ensure variety
            unique_photos = self._deduplicate_photos(all_photos)
            
            # Score and sort photos for quality and relevance
            scored_photos = self._score_photos(unique_photos, search_queries)
            
            # Ensure we have exactly 6 high-quality images
            final_photos = scored_photos[:6]
            
            # If we don't have enough, fill with high-quality fallbacks
            if len(final_photos) < 6:
                fallback_photos = self._get_diverse_fallback_photos(
                    business_name, industry, 6 - len(final_photos)
                )
                final_photos.extend(fallback_photos)
            
            logger.info(f"Generated {len(final_photos)} curated photo suggestions for {business_name}")
            return final_photos[:6]  # Always return exactly 6
            
        except Exception as e:
            logger.error(f"Failed to get photo suggestions: {e}")
            return self._get_diverse_fallback_photos(business_name, industry, 6)

    def _deduplicate_photos(self, photos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate photos based on ID."""
        seen_ids = set()
        unique_photos = []
        
        for photo in photos:
            photo_id = photo.get('id')
            if photo_id and photo_id not in seen_ids:
                seen_ids.add(photo_id)
                unique_photos.append(photo)
        
        return unique_photos

    def _score_photos(self, photos: List[Dict[str, Any]], queries: List[str]) -> List[Dict[str, Any]]:
        """Score photos based on quality metrics and sort by relevance."""
        scored_photos = []
        
        for photo in photos:
            score = 0
            
            # Higher resolution gets better score
            width = photo.get('width', 0)
            height = photo.get('height', 0)
            if width > 1920 and height > 1080:
                score += 3
            elif width > 1280 and height > 720:
                score += 2
            elif width > 800 and height > 600:
                score += 1
            
            # More likes indicates quality
            likes = photo.get('likes', 0)
            if likes > 1000:
                score += 3
            elif likes > 500:
                score += 2
            elif likes > 100:
                score += 1
            
            # Prefer photos with descriptions
            if photo.get('description'):
                score += 1
            
            # Prefer landscape orientation for most business use
            if width > height:
                score += 1
            
            photo['quality_score'] = score
            scored_photos.append(photo)
        
        # Sort by score (highest first)
        return sorted(scored_photos, key=lambda x: x.get('quality_score', 0), reverse=True)

    def _get_diverse_fallback_photos(self, business_name: str, industry: str, count: int) -> List[Dict[str, Any]]:
        """Generate diverse fallback photos when API fails."""
        fallback_photos = []
        
        # Create varied placeholder images with different themes
        themes = [
            'professional-workspace',
            'business-meeting',
            'modern-office',
            'team-collaboration',
            'innovation-concept',
            'success-lifestyle'
        ]
        
        colors = ['4F46E5', '059669', 'DC2626', 'EA580C', '7C3AED', '0F766E']
        
        for i in range(count):
            theme = themes[i % len(themes)]
            color = colors[i % len(colors)]
            
            photo = {
                'id': f'fallback_{business_name.lower().replace(" ", "_")}_{i}',
                'description': f'Professional {industry} {theme.replace("-", " ")} for {business_name}',
                'url': f'https://via.placeholder.com/800x600/{color}/ffffff?text={theme.replace("-", "+").title()}',
                'unsplash_url': f'https://via.placeholder.com/800x600/{color}/ffffff?text={theme.replace("-", "+").title()}',
                'small_url': f'https://via.placeholder.com/400x300/{color}/ffffff?text={theme.replace("-", "+").title()}',
                'photographer': 'VyralFlow AI',
                'photographer_username': 'vyralflow',
                'photographer_url': '#',
                'likes': random.randint(50, 500),
                'color': f'#{color}',
                'width': 800,
                'height': 600,
                'quality_score': 1
            }
            fallback_photos.append(photo)
        
        return fallback_photos

    def _get_fallback_photos(self, query: str, count: int) -> List[Dict[str, Any]]:
        """Generate fallback photos for a specific query."""
        return self._get_diverse_fallback_photos(f"Query: {query}", "General", count)

    async def get_curated_photos(self, per_page: int = 6) -> List[Dict[str, Any]]:
        """Get curated photos from Unsplash."""
        try:
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            url = f"{self.base_url}/photos?per_page={min(per_page, 30)}&order_by=popular"
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            photos = response.json()
            
            # Format photos similar to search results
            formatted_photos = []
            for photo in photos:
                formatted_photo = {
                    'id': photo.get('id'),
                    'description': photo.get('description') or photo.get('alt_description', 'Curated professional image'),
                    'url': photo.get('urls', {}).get('regular'),
                    'unsplash_url': photo.get('urls', {}).get('regular'),
                    'small_url': photo.get('urls', {}).get('small'),
                    'photographer': photo.get('user', {}).get('name'),
                    'photographer_username': photo.get('user', {}).get('username'),
                    'photographer_url': photo.get('user', {}).get('links', {}).get('html'),
                    'likes': photo.get('likes', 0),
                    'color': photo.get('color'),
                    'width': photo.get('width', 0),
                    'height': photo.get('height', 0)
                }
                formatted_photos.append(formatted_photo)
            
            logger.info(f"Retrieved {len(formatted_photos)} curated photos")
            return formatted_photos
            
        except Exception as e:
            logger.error(f"Failed to get curated photos: {e}")
            return self._get_diverse_fallback_photos("Curated", "Business", per_page)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global service instance
unsplash_service = UnsplashService()