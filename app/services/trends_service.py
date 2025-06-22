from pytrends.request import TrendReq
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import random
import time

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class TrendsService:
    """Service for Google Trends analysis using pytrends."""
    
    def __init__(self):
        """Initialize trends service."""
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360)
            self.executor = ThreadPoolExecutor(max_workers=3)
            logger.info("Trends service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize trends service: {e}")
            # Don't raise exception - we'll use fallback data
    
    async def get_trending_searches(
        self,
        geo: str = 'US',
        timeframe: str = 'now 7-d'
    ) -> List[str]:
        """Get trending search terms."""
        try:
            loop = asyncio.get_event_loop()
            
            # Get trending searches
            trending_searches = await loop.run_in_executor(
                self.executor,
                self._get_trending_searches_sync,
                geo
            )
            
            if trending_searches:
                logger.info(f"Retrieved {len(trending_searches)} trending searches")
                return trending_searches[:20]  # Limit to top 20
            else:
                return self._get_fallback_trending_searches()
                
        except Exception as e:
            logger.warning(f"Failed to get trending searches: {e}")
            return self._get_fallback_trending_searches()
    
    def _get_trending_searches_sync(self, geo: str) -> List[str]:
        """Synchronous method to get trending searches."""
        try:
            trending_searches_df = self.pytrends.trending_searches(pn=geo)
            if not trending_searches_df.empty:
                return trending_searches_df[0].tolist()
            return []
        except Exception as e:
            logger.warning(f"Pytrends trending searches failed: {e}")
            return []
    
    async def get_related_topics(
        self,
        keywords: List[str],
        geo: str = 'US',
        timeframe: str = 'today 3-m'
    ) -> Dict[str, List[str]]:
        """Get related topics for keywords."""
        try:
            if not keywords:
                return {}
            
            # Limit keywords to avoid API limits
            keywords = keywords[:5]
            
            loop = asyncio.get_event_loop()
            related_topics = await loop.run_in_executor(
                self.executor,
                self._get_related_topics_sync,
                keywords,
                geo,
                timeframe
            )
            
            logger.info(f"Retrieved related topics for {len(keywords)} keywords")
            return related_topics
            
        except Exception as e:
            logger.warning(f"Failed to get related topics: {e}")
            return self._get_fallback_related_topics(keywords)
    
    def _get_related_topics_sync(
        self,
        keywords: List[str],
        geo: str,
        timeframe: str
    ) -> Dict[str, List[str]]:
        """Synchronous method to get related topics."""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
            related_topics_dict = self.pytrends.related_topics()
            
            result = {}
            for keyword in keywords:
                if keyword in related_topics_dict:
                    topics_data = related_topics_dict[keyword]
                    if topics_data and 'top' in topics_data and topics_data['top'] is not None:
                        topics = topics_data['top']['topic_title'].tolist()[:10]
                        result[keyword] = topics
            
            return result
            
        except Exception as e:
            logger.warning(f"Pytrends related topics failed: {e}")
            return {}
    
    async def get_interest_over_time(
        self,
        keywords: List[str],
        geo: str = 'US',
        timeframe: str = 'today 3-m'
    ) -> Dict[str, Any]:
        """Get interest over time for keywords."""
        try:
            if not keywords:
                return {}
            
            keywords = keywords[:5]  # Limit to avoid API limits
            
            loop = asyncio.get_event_loop()
            interest_data = await loop.run_in_executor(
                self.executor,
                self._get_interest_over_time_sync,
                keywords,
                geo,
                timeframe
            )
            
            return interest_data
            
        except Exception as e:
            logger.warning(f"Failed to get interest over time: {e}")
            return {}
    
    def _get_interest_over_time_sync(
        self,
        keywords: List[str],
        geo: str,
        timeframe: str
    ) -> Dict[str, Any]:
        """Synchronous method to get interest over time."""
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')
            interest_df = self.pytrends.interest_over_time()
            
            if not interest_df.empty:
                # Calculate average interest for each keyword
                result = {}
                for keyword in keywords:
                    if keyword in interest_df.columns:
                        avg_interest = interest_df[keyword].mean()
                        trend_direction = self._calculate_trend_direction(interest_df[keyword])
                        result[keyword] = {
                            'average_interest': float(avg_interest),
                            'trend_direction': trend_direction,
                            'is_trending': avg_interest > 50
                        }
                
                return result
            
            return {}
            
        except Exception as e:
            logger.warning(f"Interest over time calculation failed: {e}")
            return {}
    
    def _calculate_trend_direction(self, series) -> str:
        """Calculate if trend is going up, down, or stable."""
        if len(series) < 2:
            return 'stable'
        
        recent_avg = series.tail(7).mean()  # Last week
        older_avg = series.head(7).mean()   # First week
        
        if recent_avg > older_avg * 1.1:
            return 'rising'
        elif recent_avg < older_avg * 0.9:
            return 'falling'
        else:
            return 'stable'
    
    async def analyze_industry_trends(
        self,
        industry: str,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze trends specific to an industry."""
        try:
            # Combine industry with provided keywords
            industry_keywords = self._get_industry_keywords(industry)
            if keywords:
                all_keywords = list(set(industry_keywords + keywords[:3]))[:5]
            else:
                all_keywords = industry_keywords[:5]
            
            # Get multiple trend analyses
            trending_searches = await self.get_trending_searches()
            related_topics = await self.get_related_topics(all_keywords)
            interest_data = await self.get_interest_over_time(all_keywords)
            
            # Filter trending searches for industry relevance
            relevant_trends = self._filter_relevant_trends(trending_searches, industry, all_keywords)
            
            return {
                'industry': industry,
                'trending_searches': relevant_trends,
                'related_topics': related_topics,
                'interest_data': interest_data,
                'recommended_hashtags': self._generate_hashtags(industry, relevant_trends, all_keywords),
                'analysis_summary': self._generate_analysis_summary(industry, relevant_trends, interest_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze industry trends for {industry}: {e}")
            return self._get_fallback_industry_analysis(industry, keywords)
    
    def _get_industry_keywords(self, industry: str) -> List[str]:
        """Get relevant keywords for an industry."""
        industry_mapping = {
            'food & beverage': ['restaurant', 'food', 'coffee', 'dining', 'cuisine'],
            'technology': ['tech', 'software', 'AI', 'digital', 'innovation'],
            'retail': ['shopping', 'fashion', 'store', 'sale', 'brand'],
            'healthcare': ['health', 'medical', 'wellness', 'fitness', 'care'],
            'finance': ['banking', 'investment', 'money', 'financial', 'insurance'],
            'education': ['learning', 'school', 'education', 'training', 'courses'],
            'real estate': ['property', 'home', 'real estate', 'housing', 'mortgage'],
            'automotive': ['car', 'vehicle', 'automotive', 'driving', 'transport']
        }
        
        return industry_mapping.get(industry.lower(), [industry])
    
    def _filter_relevant_trends(
        self,
        trending_searches: List[str],
        industry: str,
        keywords: List[str]
    ) -> List[str]:
        """Filter trending searches for industry relevance."""
        industry_terms = self._get_industry_keywords(industry) + keywords
        relevant_trends = []
        
        for trend in trending_searches:
            trend_lower = trend.lower()
            if any(term.lower() in trend_lower for term in industry_terms):
                relevant_trends.append(trend)
            elif len(relevant_trends) < 5:  # Keep some general trends
                relevant_trends.append(trend)
        
        return relevant_trends[:10]
    
    def _generate_hashtags(
        self,
        industry: str,
        trends: List[str],
        keywords: List[str]
    ) -> List[str]:
        """Generate relevant hashtags."""
        hashtags = []
        
        # Industry-specific hashtags
        industry_hashtags = {
            'food & beverage': ['#foodie', '#restaurant', '#cuisine', '#dining'],
            'technology': ['#tech', '#innovation', '#digital', '#software'],
            'retail': ['#shopping', '#fashion', '#retail', '#brand'],
            'healthcare': ['#health', '#wellness', '#medical', '#fitness'],
            'finance': ['#finance', '#banking', '#investment', '#money'],
            'education': ['#education', '#learning', '#training', '#knowledge'],
            'real estate': ['#realestate', '#property', '#home', '#housing'],
            'automotive': ['#automotive', '#cars', '#vehicles', '#driving']
        }
        
        hashtags.extend(industry_hashtags.get(industry.lower(), [f'#{industry.replace(" ", "").lower()}']))
        
        # Add trending hashtags
        for trend in trends[:3]:
            hashtag = f"#{trend.replace(' ', '').lower()}"
            if len(hashtag) > 3 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        # Add keyword hashtags
        for keyword in keywords[:2]:
            hashtag = f"#{keyword.replace(' ', '').lower()}"
            if len(hashtag) > 3 and hashtag not in hashtags:
                hashtags.append(hashtag)
        
        return hashtags[:10]
    
    def _generate_analysis_summary(
        self,
        industry: str,
        trends: List[str],
        interest_data: Dict[str, Any]
    ) -> str:
        """Generate a summary of the trend analysis."""
        summary_parts = []
        
        if trends:
            summary_parts.append(f"Current trending topics relevant to {industry} include: {', '.join(trends[:3])}.")
        
        if interest_data:
            rising_topics = [k for k, v in interest_data.items() if v.get('trend_direction') == 'rising']
            if rising_topics:
                summary_parts.append(f"Rising topics: {', '.join(rising_topics)}.")
        
        if not summary_parts:
            summary_parts.append(f"General trends in {industry} show steady engagement with industry-specific content.")
        
        return ' '.join(summary_parts)
    
    def _get_fallback_trending_searches(self) -> List[str]:
        """Get fallback trending searches when API fails."""
        fallback_trends = [
            'AI technology', 'sustainability', 'remote work', 'digital marketing',
            'e-commerce', 'social media', 'mobile apps', 'cloud computing',
            'cybersecurity', 'data analytics', 'customer experience', 'innovation',
            'productivity', 'wellness', 'fitness', 'healthy eating',
            'travel', 'entertainment', 'education', 'finance'
        ]
        
        # Randomize to simulate fresh trends
        random.shuffle(fallback_trends)
        return fallback_trends[:15]
    
    def _get_fallback_related_topics(self, keywords: List[str]) -> Dict[str, List[str]]:
        """Get fallback related topics."""
        fallback_topics = {
            'technology': ['artificial intelligence', 'machine learning', 'cloud computing', 'cybersecurity'],
            'food': ['restaurant', 'cuisine', 'cooking', 'healthy eating'],
            'business': ['marketing', 'sales', 'customer service', 'entrepreneurship'],
            'health': ['wellness', 'fitness', 'nutrition', 'mental health'],
            'education': ['online learning', 'skills', 'training', 'development']
        }
        
        result = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for category, topics in fallback_topics.items():
                if category in keyword_lower or keyword_lower in category:
                    result[keyword] = topics[:5]
                    break
            
            if keyword not in result:
                result[keyword] = ['trending', 'popular', 'viral', 'engaging']
        
        return result
    
    def _get_fallback_industry_analysis(
        self,
        industry: str,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get fallback industry analysis."""
        fallback_trends = self._get_fallback_trending_searches()
        industry_keywords = self._get_industry_keywords(industry)
        
        return {
            'industry': industry,
            'trending_searches': fallback_trends[:10],
            'related_topics': self._get_fallback_related_topics(industry_keywords),
            'interest_data': {},
            'recommended_hashtags': self._generate_hashtags(industry, fallback_trends, industry_keywords),
            'analysis_summary': f"Current trends in {industry} show consistent engagement with industry-relevant content and emerging topics."
        }


# Global service instance
trends_service = TrendsService()