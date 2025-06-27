from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentType, AgentInput
from app.models.campaign import TrendAnalysisResult
from app.services.trends_service import trends_service
from app.services.reddit_service import reddit_service
from app.utils.logging import get_logger

logger = get_logger(__name__)


class TrendAnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing social media trends using Google Trends and Reddit.
    Provides trend data to inform content creation and campaign strategy.
    """
    
    def __init__(self):
        super().__init__(AgentType.TREND_ANALYZER, timeout_seconds=180)
        self.logger = get_logger("agent.trend_analyzer")
    
    async def _execute_impl(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute trend analysis for the campaign.
        
        Args:
            agent_input: Campaign input data
            
        Returns:
            Dict containing trend analysis results
        """
        self.logger.info(f"Starting trend analysis for {agent_input.business_name}")
        
        # Validate input
        if not self._validate_input(agent_input):
            raise ValueError("Invalid input data for trend analysis")
        
        try:
            # Step 1: Analyze Google Trends
            await self._update_step_progress(1, 4, "Analyzing Google Trends data")
            google_trends_data = await self._analyze_google_trends(agent_input)
            
            # Step 2: Analyze Reddit trends
            await self._update_step_progress(2, 4, "Analyzing Reddit trends")
            reddit_trends_data = await self._analyze_reddit_trends(agent_input)
            
            # Step 3: Combine and analyze all trend data
            await self._update_step_progress(3, 4, "Combining trend data sources")
            combined_trends = await self._combine_trend_data(
                google_trends_data, 
                reddit_trends_data, 
                agent_input
            )
            
            # Step 4: Generate final analysis
            await self._update_step_progress(4, 4, "Generating trend analysis report")
            final_analysis = await self._generate_trend_analysis(combined_trends, agent_input)
            
            self.logger.info("Trend analysis completed successfully")
            return final_analysis
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return await self._get_fallback_trend_analysis(agent_input)
    
    async def _analyze_google_trends(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Analyze Google Trends data."""
        try:
            # Get industry-specific trends
            industry_analysis = await trends_service.analyze_industry_trends(
                agent_input.industry,
                agent_input.keywords
            )
            
            # Get general trending searches
            trending_searches = await trends_service.get_trending_searches()
            
            # Get related topics for keywords
            related_topics = {}
            if agent_input.keywords:
                related_topics = await trends_service.get_related_topics(agent_input.keywords)
            
            # Get interest data
            interest_data = {}
            if agent_input.keywords:
                interest_data = await trends_service.get_interest_over_time(agent_input.keywords)
            
            return {
                'source': 'google_trends',
                'industry_analysis': industry_analysis,
                'trending_searches': trending_searches,
                'related_topics': related_topics,
                'interest_data': interest_data,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Google Trends analysis failed: {e}")
            return {
                'source': 'google_trends',
                'error': str(e),
                'fallback_used': True
            }
    
    async def _analyze_reddit_trends(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Analyze Reddit trends data."""
        try:
            # Get industry-relevant posts
            reddit_posts = await reddit_service.get_industry_relevant_posts(
                agent_input.industry,
                agent_input.keywords,
                limit=20
            )
            
            # Extract trending topics from posts
            trending_topics = await reddit_service.extract_trending_topics(reddit_posts)
            
            # Get engagement insights
            engagement_insights = await reddit_service.get_engagement_insights(reddit_posts)
            
            return {
                'source': 'reddit',
                'posts_analyzed': len(reddit_posts),
                'trending_topics': trending_topics,
                'engagement_insights': engagement_insights,
                'top_posts': reddit_posts[:5],  # Include top 5 posts for context
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Reddit analysis failed: {e}")
            return {
                'source': 'reddit',
                'error': str(e),
                'fallback_used': True
            }
    
    async def _combine_trend_data(
        self,
        google_data: Dict[str, Any],
        reddit_data: Dict[str, Any],
        agent_input: AgentInput
    ) -> Dict[str, Any]:
        """Combine trend data from all sources."""
        try:
            combined_trending_topics = []
            combined_hashtags = []
            data_sources = []
            
            # Process Google Trends data
            if 'industry_analysis' in google_data:
                industry_data = google_data['industry_analysis']
                if 'trending_searches' in industry_data:
                    combined_trending_topics.extend(industry_data['trending_searches'][:10])
                if 'recommended_hashtags' in industry_data:
                    combined_hashtags.extend(industry_data['recommended_hashtags'])
                data_sources.append('Google Trends')
            
            # Process Reddit data
            if 'trending_topics' in reddit_data:
                combined_trending_topics.extend(reddit_data['trending_topics'][:10])
                data_sources.append('Reddit')
            
            # Remove duplicates and prioritize
            unique_topics = list(dict.fromkeys(combined_trending_topics))  # Preserve order
            unique_hashtags = list(dict.fromkeys(combined_hashtags))
            
            # Score and rank topics based on multiple sources
            scored_topics = self._score_trending_topics(unique_topics, google_data, reddit_data)
            
            return {
                'trending_topics': scored_topics[:15],
                'trending_hashtags': unique_hashtags[:10],
                'data_sources': data_sources,
                'google_trends_data': google_data,
                'reddit_data': reddit_data,
                'combination_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to combine trend data: {e}")
            return {
                'trending_topics': [],
                'trending_hashtags': [],
                'data_sources': [],
                'error': str(e)
            }
    
    def _score_trending_topics(
        self,
        topics: List[str],
        google_data: Dict[str, Any],
        reddit_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score and rank trending topics based on multiple factors."""
        topic_scores = {}
        
        for topic in topics:
            score = 0
            topic_lower = topic.lower()
            
            # Score based on Google Trends presence
            if 'industry_analysis' in google_data:
                industry_data = google_data['industry_analysis']
                if 'trending_searches' in industry_data:
                    if topic in industry_data['trending_searches'][:5]:  # Top 5 get higher score
                        score += 3
                    elif topic in industry_data['trending_searches']:
                        score += 2
            
            # Score based on Reddit presence
            if 'trending_topics' in reddit_data:
                if topic in reddit_data['trending_topics'][:5]:
                    score += 2
                elif topic in reddit_data['trending_topics']:
                    score += 1
            
            # Bonus for industry relevance (simple keyword matching)
            industry_keywords = ['business', 'marketing', 'digital', 'social', 'brand', 'customer']
            if any(keyword in topic_lower for keyword in industry_keywords):
                score += 1
            
            topic_scores[topic] = score
        
        # Sort by score and return
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Convert to the format expected by the frontend
        result = []
        for topic, score in sorted_topics:
            # Normalize score to 0-100 range
            normalized_score = min(int((score / 6) * 100), 100)
            
            # Determine trend type based on score
            trend_type = "stable"
            if normalized_score >= 80:
                trend_type = "rising"
            elif normalized_score >= 60:
                trend_type = "trending"
            
            result.append({
                "topic": topic,
                "relevance_score": normalized_score,
                "trend_type": trend_type
            })
            
        return result
    
    async def _generate_trend_analysis(
        self,
        combined_data: Dict[str, Any],
        agent_input: AgentInput
    ) -> Dict[str, Any]:
        """Generate final trend analysis results."""
        try:
            # Calculate confidence score based on data sources
            confidence_score = self._calculate_confidence_score(combined_data)
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(combined_data, agent_input)
            
            # Generate viral probability based on confidence score
            viral_probability = f"{int(confidence_score * 85)}%"
            
            # Generate peak engagement window
            peak_times = ["weekday evenings", "weekend mornings", "Monday-Wednesday", "Thursday-Friday"]
            import random
            peak_engagement_window = random.choice(peak_times)
            
            # Create TrendAnalysisResult
            trend_result = TrendAnalysisResult(
                trending_topics=combined_data.get('trending_topics', []),
                trending_hashtags=combined_data.get('trending_hashtags', []),
                analysis_summary=analysis_summary,
                confidence_score=confidence_score,
                data_sources=combined_data.get('data_sources', []),
                viral_probability=viral_probability,
                peak_engagement_window=peak_engagement_window
            )
            
            return {
                'trends': trend_result.model_dump(),
                'raw_data': {
                    'google_trends': combined_data.get('google_trends_data', {}),
                    'reddit_data': combined_data.get('reddit_data', {})
                },
                'metadata': {
                    'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                    'agent_version': '1.0.0',
                    'data_sources_count': len(combined_data.get('data_sources', [])),
                    'confidence_score': confidence_score
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate trend analysis: {e}")
            return await self._get_fallback_trend_analysis(agent_input)
    
    def _calculate_confidence_score(self, combined_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on available data."""
        score = 0.0
        max_score = 1.0
        
        # Score based on data sources
        data_sources = combined_data.get('data_sources', [])
        if 'Google Trends' in data_sources:
            score += 0.6
        if 'Reddit' in data_sources:
            score += 0.4
        
        # Adjust based on data quality
        trending_topics_count = len(combined_data.get('trending_topics', []))
        if trending_topics_count >= 10:
            score *= 1.0
        elif trending_topics_count >= 5:
            score *= 0.8
        else:
            score *= 0.6
        
        return min(score, max_score)
    
    def _generate_analysis_summary(
        self,
        combined_data: Dict[str, Any],
        agent_input: AgentInput
    ) -> str:
        """Generate a human-readable analysis summary."""
        try:
            summary_parts = []
            
            # Data sources
            data_sources = combined_data.get('data_sources', [])
            if data_sources:
                summary_parts.append(f"Trend analysis based on {', '.join(data_sources)} data.")
            
            # Trending topics
            trending_topics = combined_data.get('trending_topics', [])
            if trending_topics:
                top_topics = trending_topics[:3]
                summary_parts.append(f"Top trending topics for {agent_input.industry}: {', '.join(top_topics)}.")
            
            # Industry insights
            if agent_input.industry:
                summary_parts.append(f"Current trends in {agent_input.industry} show strong engagement with relevant content.")
            
            # Reddit insights
            reddit_data = combined_data.get('reddit_data', {})
            if 'engagement_insights' in reddit_data:
                engagement_data = reddit_data['engagement_insights']
                if 'engagement_insights' in engagement_data:
                    insights = engagement_data['engagement_insights'][:2]  # Top 2 insights
                    if insights:
                        summary_parts.append(f"Key engagement patterns: {', '.join(insights).lower()}.")
            
            # Fallback summary
            if not summary_parts:
                summary_parts.append(f"Trend analysis completed for {agent_input.business_name} in the {agent_input.industry} industry.")
            
            return ' '.join(summary_parts)
            
        except Exception as e:
            self.logger.warning(f"Failed to generate analysis summary: {e}")
            return f"Trend analysis completed for {agent_input.business_name}."
    
    async def _get_fallback_trend_analysis(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Get fallback trend analysis when main analysis fails."""
        self.logger.warning("Using fallback trend analysis")
        
        # Industry-specific fallback trends
        fallback_trends = {
            'food & beverage': {
                'topics': ['foodie culture', 'healthy eating', 'local dining', 'food photography', 'seasonal menus'],
                'hashtags': ['#foodie', '#localeats', '#healthyfood', '#foodphotography', '#seasonalflavors']
            },
            'technology': {
                'topics': ['digital transformation', 'AI innovation', 'remote work', 'cybersecurity', 'cloud computing'],
                'hashtags': ['#tech', '#innovation', '#digitaltransformation', '#AI', '#futureofwork']
            },
            'retail': {
                'topics': ['online shopping', 'sustainable fashion', 'customer experience', 'brand loyalty', 'social commerce'],
                'hashtags': ['#retail', '#ecommerce', '#shopping', '#fashion', '#customerexperience']
            }
        }
        
        industry_key = agent_input.industry.lower()
        fallback_data = fallback_trends.get(industry_key, {
            'topics': ['business growth', 'customer engagement', 'digital marketing', 'brand awareness', 'innovation'],
            'hashtags': ['#business', '#growth', '#marketing', '#branding', '#innovation']
        })
        
        # Convert topics to the expected format
        formatted_topics = []
        for i, topic in enumerate(fallback_data['topics']):
            # Assign different scores and trend types based on position
            score = 90 - (i * 10)  # First topic gets 90, then 80, 70, etc.
            trend_type = "rising" if i < 2 else "trending" if i < 4 else "stable"
            
            formatted_topics.append({
                "topic": topic,
                "relevance_score": score,
                "trend_type": trend_type
            })
        
        trend_result = TrendAnalysisResult(
            trending_topics=formatted_topics,
            trending_hashtags=fallback_data['hashtags'],
            analysis_summary=f"Fallback trend analysis for {agent_input.business_name} in {agent_input.industry}. Current trends show consistent engagement with industry-relevant content.",
            confidence_score=0.3,  # Lower confidence for fallback
            data_sources=['Fallback Data'],
            viral_probability="65%",  # Moderate probability for fallback
            peak_engagement_window="Weekday evenings and weekend mornings"
        )
        
        return {
            'trends': trend_result.model_dump(),
            'raw_data': {
                'fallback_used': True,
                'reason': 'Primary trend analysis sources unavailable'
            },
            'metadata': {
                'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
                'agent_version': '1.0.0',
                'fallback': True,
                'confidence_score': 0.3
            }
        }


# Global agent instance
trend_analyzer_agent = TrendAnalyzerAgent()