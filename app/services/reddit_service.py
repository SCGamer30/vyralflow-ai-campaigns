import praw
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.exceptions import ExternalAPIException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RedditService:
    """Service for Reddit API interactions (backup trend source)."""
    
    def __init__(self):
        """Initialize Reddit client."""
        self.reddit = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Initialize Reddit client if credentials are available
        if settings.reddit_client_id and settings.reddit_client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=settings.reddit_client_id,
                    client_secret=settings.reddit_client_secret,
                    user_agent=settings.reddit_user_agent
                )
                logger.info("Reddit service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit service: {e}")
        else:
            logger.info("Reddit credentials not provided, using fallback data")
    
    async def get_trending_posts(
        self,
        subreddits: List[str],
        limit: int = 10,
        time_filter: str = 'day'
    ) -> List[Dict[str, Any]]:
        """Get trending posts from specified subreddits."""
        if not self.reddit:
            return self._get_fallback_trending_posts(subreddits)
        
        try:
            loop = asyncio.get_event_loop()
            trending_posts = await loop.run_in_executor(
                self.executor,
                self._get_trending_posts_sync,
                subreddits,
                limit,
                time_filter
            )
            
            logger.info(f"Retrieved {len(trending_posts)} trending posts from Reddit")
            return trending_posts
            
        except Exception as e:
            logger.warning(f"Failed to get trending posts from Reddit: {e}")
            return self._get_fallback_trending_posts(subreddits)
    
    def _get_trending_posts_sync(
        self,
        subreddits: List[str],
        limit: int,
        time_filter: str
    ) -> List[Dict[str, Any]]:
        """Synchronous method to get trending posts."""
        try:
            trending_posts = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get hot posts
                    hot_posts = subreddit.hot(limit=limit)
                    
                    for post in hot_posts:
                        if post.stickied:  # Skip stickied posts
                            continue
                        
                        trending_posts.append({
                            'title': post.title,
                            'subreddit': subreddit_name,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'url': post.url,
                            'selftext': post.selftext[:500] if post.selftext else '',
                            'upvote_ratio': post.upvote_ratio,
                            'author': str(post.author) if post.author else '[deleted]'
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to get posts from r/{subreddit_name}: {e}")
                    continue
            
            # Sort by score and return top posts
            trending_posts.sort(key=lambda x: x['score'], reverse=True)
            return trending_posts[:limit]
            
        except Exception as e:
            logger.error(f"Error in _get_trending_posts_sync: {e}")
            return []
    
    async def get_industry_relevant_posts(
        self,
        industry: str,
        keywords: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get posts relevant to a specific industry."""
        # Map industries to relevant subreddits
        industry_subreddits = {
            'food & beverage': ['food', 'recipes', 'cooking', 'restaurant', 'coffee'],
            'technology': ['technology', 'programming', 'startups', 'MachineLearning', 'artificial'],
            'retail': ['retail', 'fashion', 'shopping', 'ecommerce', 'smallbusiness'],
            'healthcare': ['health', 'medicine', 'fitness', 'nutrition', 'wellness'],
            'finance': ['finance', 'investing', 'personalfinance', 'cryptocurrency', 'stocks'],
            'education': ['education', 'teachers', 'learning', 'academia', 'studytips'],
            'real estate': ['realestate', 'investing', 'homeowners', 'realestateinvesting'],
            'automotive': ['cars', 'automotive', 'electricvehicles', 'trucks', 'motorcycles']
        }
        
        subreddits = industry_subreddits.get(industry.lower(), ['business', 'entrepreneur'])
        
        try:
            posts = await self.get_trending_posts(subreddits, limit)
            
            # Filter posts by keywords if provided
            if keywords:
                filtered_posts = []
                for post in posts:
                    text_content = f"{post['title']} {post['selftext']}".lower()
                    if any(keyword.lower() in text_content for keyword in keywords):
                        filtered_posts.append(post)
                
                return filtered_posts[:limit//2] + posts[:limit//2]  # Mix filtered and general
            
            return posts
            
        except Exception as e:
            logger.error(f"Failed to get industry relevant posts: {e}")
            return self._get_fallback_industry_posts(industry)
    
    async def extract_trending_topics(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract trending topics from Reddit posts."""
        try:
            # Simple keyword extraction from titles
            keywords = {}
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'cannot', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
            
            for post in posts:
                title_words = post['title'].lower().split()
                for word in title_words:
                    # Clean word
                    word = ''.join(char for char in word if char.isalnum())
                    if len(word) > 3 and word not in common_words:
                        keywords[word] = keywords.get(word, 0) + post['score']
            
            # Sort by weighted score and return top topics
            sorted_topics = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
            return [topic[0] for topic in sorted_topics[:15]]
            
        except Exception as e:
            logger.error(f"Failed to extract trending topics: {e}")
            return ['trending', 'popular', 'viral', 'engaging', 'content']
    
    async def get_engagement_insights(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze engagement patterns from Reddit posts."""
        try:
            if not posts:
                return {}
            
            total_posts = len(posts)
            total_score = sum(post['score'] for post in posts)
            total_comments = sum(post['num_comments'] for post in posts)
            
            avg_score = total_score / total_posts
            avg_comments = total_comments / total_posts
            
            # Analyze upvote ratios
            upvote_ratios = [post['upvote_ratio'] for post in posts if 'upvote_ratio' in post]
            avg_upvote_ratio = sum(upvote_ratios) / len(upvote_ratios) if upvote_ratios else 0.8
            
            # Find most engaging content types
            high_engagement_posts = [post for post in posts if post['score'] > avg_score]
            
            return {
                'total_posts_analyzed': total_posts,
                'average_score': avg_score,
                'average_comments': avg_comments,
                'average_upvote_ratio': avg_upvote_ratio,
                'high_engagement_posts': len(high_engagement_posts),
                'engagement_insights': self._generate_engagement_insights(posts, avg_score, avg_comments)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement: {e}")
            return {}
    
    def _generate_engagement_insights(
        self,
        posts: List[Dict[str, Any]],
        avg_score: float,
        avg_comments: float
    ) -> List[str]:
        """Generate insights about what drives engagement."""
        insights = []
        
        # Analyze titles
        high_engagement_titles = [post['title'] for post in posts if post['score'] > avg_score]
        
        if high_engagement_titles:
            # Look for patterns in high-engagement titles
            if any('how to' in title.lower() for title in high_engagement_titles):
                insights.append("How-to content performs well")
            
            if any('?' in title for title in high_engagement_titles):
                insights.append("Question-based titles drive engagement")
            
            if any(len(title) < 50 for title in high_engagement_titles):
                insights.append("Shorter titles tend to perform better")
        
        # Analyze comment engagement
        high_comment_posts = [post for post in posts if post['num_comments'] > avg_comments]
        if len(high_comment_posts) > len(posts) * 0.3:
            insights.append("Discussion-worthy content gets more comments")
        
        if not insights:
            insights.append("Consistent posting and community engagement are key")
        
        return insights
    
    def _get_fallback_trending_posts(self, subreddits: List[str]) -> List[Dict[str, Any]]:
        """Get fallback trending posts when Reddit API is unavailable."""
        fallback_posts = [
            {
                'title': 'Latest trends in digital marketing',
                'subreddit': 'marketing',
                'score': 1250,
                'num_comments': 85,
                'created_utc': datetime.now() - timedelta(hours=2),
                'url': 'https://reddit.com',
                'selftext': 'Discussion about current digital marketing trends...',
                'upvote_ratio': 0.92,
                'author': 'marketingpro'
            },
            {
                'title': 'How to build brand awareness on social media',
                'subreddit': 'socialmedia',
                'score': 980,
                'num_comments': 67,
                'created_utc': datetime.now() - timedelta(hours=5),
                'url': 'https://reddit.com',
                'selftext': 'Tips and strategies for social media branding...',
                'upvote_ratio': 0.89,
                'author': 'socialmediaguru'
            },
            {
                'title': 'Customer engagement strategies that work',
                'subreddit': 'business',
                'score': 756,
                'num_comments': 43,
                'created_utc': datetime.now() - timedelta(hours=8),
                'url': 'https://reddit.com',
                'selftext': 'Proven methods to increase customer engagement...',
                'upvote_ratio': 0.87,
                'author': 'businessowner'
            }
        ]
        
        return fallback_posts
    
    def _get_fallback_industry_posts(self, industry: str) -> List[Dict[str, Any]]:
        """Get fallback industry-specific posts."""
        industry_posts = {
            'food & beverage': [
                {'title': 'New food trends taking over 2024', 'score': 1100, 'num_comments': 78},
                {'title': 'Restaurant marketing strategies that work', 'score': 890, 'num_comments': 52},
                {'title': 'Coffee shop branding tips', 'score': 675, 'num_comments': 34}
            ],
            'technology': [
                {'title': 'AI adoption in small businesses', 'score': 1450, 'num_comments': 95},
                {'title': 'Tech startup marketing on a budget', 'score': 1120, 'num_comments': 67},
                {'title': 'Software company content strategies', 'score': 890, 'num_comments': 45}
            ]
        }
        
        posts = industry_posts.get(industry.lower(), [
            {'title': f'{industry} business growth strategies', 'score': 950, 'num_comments': 62},
            {'title': f'Marketing tips for {industry} companies', 'score': 780, 'num_comments': 41}
        ])
        
        # Add metadata to fallback posts
        for i, post in enumerate(posts):
            post.update({
                'subreddit': industry.replace(' ', '').lower(),
                'created_utc': datetime.now() - timedelta(hours=i*2),
                'url': 'https://reddit.com',
                'selftext': f'Discussion about {industry} trends and strategies...',
                'upvote_ratio': 0.85 + (i * 0.02),
                'author': 'industry_expert'
            })
        
        return posts


# Global service instance
reddit_service = RedditService()