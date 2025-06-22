from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random

from app.agents.base_agent import BaseAgent
from app.models.agent import AgentType, AgentInput
from app.models.campaign import ScheduleResult, PlatformSchedule
from app.utils.logging import get_logger

logger = get_logger(__name__)


class CampaignSchedulerAgent(BaseAgent):
    """
    Agent responsible for optimizing posting times and creating scheduling recommendations.
    Analyzes optimal posting times for each platform and creates a coordinated posting strategy.
    """
    
    def __init__(self):
        super().__init__(AgentType.CAMPAIGN_SCHEDULER, timeout_seconds=120)
        self.logger = get_logger("agent.campaign_scheduler")
        
        # Platform-specific optimal posting data
        self.platform_data = {
            'instagram': {
                'optimal_days': ['Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'optimal_hours': [11, 13, 17, 19],  # 11 AM, 1 PM, 5 PM, 7 PM
                'posting_frequency': 'Daily',
                'peak_engagement_windows': [(11, 13), (17, 19)]
            },
            'twitter': {
                'optimal_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'optimal_hours': [9, 12, 15, 18],  # 9 AM, 12 PM, 3 PM, 6 PM
                'posting_frequency': '3-5 times daily',
                'peak_engagement_windows': [(9, 10), (12, 13), (17, 18)]
            },
            'linkedin': {
                'optimal_days': ['Tuesday', 'Wednesday', 'Thursday'],
                'optimal_hours': [8, 10, 12, 14, 17],  # 8 AM, 10 AM, 12 PM, 2 PM, 5 PM
                'posting_frequency': '2-3 times weekly',
                'peak_engagement_windows': [(8, 10), (17, 18)]
            },
            'facebook': {
                'optimal_days': ['Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                'optimal_hours': [9, 13, 15, 20],  # 9 AM, 1 PM, 3 PM, 8 PM
                'posting_frequency': 'Daily',
                'peak_engagement_windows': [(13, 15), (20, 21)]
            },
            'tiktok': {
                'optimal_days': ['Tuesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                'optimal_hours': [6, 10, 19, 20],  # 6 AM, 10 AM, 7 PM, 8 PM
                'posting_frequency': 'Daily',
                'peak_engagement_windows': [(6, 10), (19, 21)]
            }
        }
    
    async def _execute_impl(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Execute campaign scheduling optimization.
        
        Args:
            agent_input: Campaign input data including content from previous agents
            
        Returns:
            Dict containing scheduling recommendations for all platforms
        """
        self.logger.info(f"Starting campaign scheduling for {agent_input.business_name}")
        
        # Validate input
        if not self._validate_input(agent_input):
            raise ValueError("Invalid input data for campaign scheduling")
        
        try:
            # Step 1: Analyze target audience and industry timing patterns
            await self._update_step_progress(1, 4, "Analyzing audience timing patterns")
            audience_analysis = await self._analyze_audience_timing(agent_input)
            
            # Step 2: Generate platform-specific schedules
            await self._update_step_progress(2, 4, "Creating platform schedules")
            platform_schedules = await self._create_platform_schedules(agent_input, audience_analysis)
            
            # Step 3: Create coordinated posting sequence
            await self._update_step_progress(3, 4, "Optimizing posting sequence")
            posting_sequence = await self._create_posting_sequence(agent_input, platform_schedules)
            
            # Step 4: Generate final scheduling recommendations
            await self._update_step_progress(4, 4, "Finalizing schedule recommendations")
            schedule_result = await self._create_schedule_result(platform_schedules, posting_sequence)
            
            self.logger.info("Campaign scheduling completed successfully")
            return {
                'schedule': schedule_result.dict(),
                'metadata': {
                    'scheduling_timestamp': datetime.utcnow().isoformat(),
                    'platforms_scheduled': len(agent_input.target_platforms),
                    'posting_events_created': len(posting_sequence),
                    'optimization_factors': audience_analysis.get('factors_considered', []),
                    'agent_version': '1.0.0'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Campaign scheduling failed: {e}")
            return await self._get_fallback_schedule(agent_input)
    
    async def _analyze_audience_timing(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Analyze audience behavior patterns to optimize timing."""
        analysis = {
            'factors_considered': [],
            'adjustments': {},
            'confidence_score': 0.8
        }
        
        # Industry-specific timing adjustments
        industry_adjustments = {
            'food & beverage': {
                'peak_hours': [11, 12, 17, 18, 19],  # Meal times
                'weekend_boost': True,
                'factors': ['meal times', 'weekend dining']
            },
            'technology': {
                'peak_hours': [9, 10, 14, 15, 16],  # Business hours
                'weekend_boost': False,
                'factors': ['business hours', 'weekday focus']
            },
            'retail': {
                'peak_hours': [10, 12, 15, 18, 20],  # Shopping times
                'weekend_boost': True,
                'factors': ['shopping hours', 'weekend activity']
            },
            'healthcare': {
                'peak_hours': [8, 9, 12, 17, 18],  # Professional hours
                'weekend_boost': False,
                'factors': ['professional hours', 'health awareness times']
            },
            'finance': {
                'peak_hours': [8, 9, 12, 17],  # Market hours
                'weekend_boost': False,
                'factors': ['market hours', 'business schedule']
            },
            'education': {
                'peak_hours': [8, 12, 15, 18],  # School schedule
                'weekend_boost': False,
                'factors': ['academic schedule', 'learning times']
            },
            'real estate': {
                'peak_hours': [10, 12, 17, 19],  # Viewing times
                'weekend_boost': True,
                'factors': ['viewing times', 'weekend house hunting']
            },
            'automotive': {
                'peak_hours': [9, 12, 17, 19],  # Commute and leisure
                'weekend_boost': True,
                'factors': ['commute times', 'weekend activities']
            }
        }
        
        industry_key = agent_input.industry.lower()
        if industry_key in industry_adjustments:
            industry_data = industry_adjustments[industry_key]
            analysis['adjustments']['peak_hours'] = industry_data['peak_hours']
            analysis['adjustments']['weekend_boost'] = industry_data['weekend_boost']
            analysis['factors_considered'].extend(industry_data['factors'])
        
        # Target audience adjustments
        if agent_input.target_audience:
            audience_lower = agent_input.target_audience.lower()
            
            if 'young' in audience_lower or 'millennial' in audience_lower or 'gen z' in audience_lower:
                analysis['adjustments']['evening_preference'] = True
                analysis['adjustments']['weekend_active'] = True
                analysis['factors_considered'].append('younger audience preferences')
            
            if 'professional' in audience_lower or 'business' in audience_lower:
                analysis['adjustments']['business_hours_focus'] = True
                analysis['factors_considered'].append('professional audience schedule')
            
            if 'parent' in audience_lower or 'family' in audience_lower:
                analysis['adjustments']['early_evening'] = True
                analysis['factors_considered'].append('family schedule considerations')
        
        # Campaign goal timing considerations
        goal_lower = agent_input.campaign_goal.lower()
        if 'urgent' in goal_lower or 'sale' in goal_lower or 'limited' in goal_lower:
            analysis['adjustments']['frequent_posting'] = True
            analysis['factors_considered'].append('urgency requires frequent posting')
        
        if 'awareness' in goal_lower:
            analysis['adjustments']['consistent_schedule'] = True
            analysis['factors_considered'].append('awareness campaign needs consistency')
        
        return analysis
    
    async def _create_platform_schedules(
        self,
        agent_input: AgentInput,
        audience_analysis: Dict[str, Any]
    ) -> Dict[str, PlatformSchedule]:
        """Create optimized schedules for each platform."""
        platform_schedules = {}
        
        for platform in agent_input.target_platforms:
            platform_lower = platform.lower()
            
            if platform_lower not in self.platform_data:
                self.logger.warning(f"No scheduling data for platform: {platform}")
                continue
            
            base_data = self.platform_data[platform_lower]
            
            # Get optimal times with audience adjustments
            optimal_times = self._optimize_times_for_audience(
                base_data['optimal_hours'],
                audience_analysis.get('adjustments', {})
            )
            
            # Get optimal days
            optimal_days = self._optimize_days_for_audience(
                base_data['optimal_days'],
                audience_analysis.get('adjustments', {})
            )
            
            # Adjust posting frequency
            posting_frequency = self._adjust_posting_frequency(
                base_data['posting_frequency'],
                audience_analysis.get('adjustments', {}),
                agent_input
            )
            
            platform_schedule = PlatformSchedule(
                optimal_times=[f"{hour}:00" for hour in optimal_times],
                best_days=optimal_days,
                posting_frequency=posting_frequency
            )
            
            platform_schedules[platform_lower] = platform_schedule
        
        return platform_schedules
    
    def _optimize_times_for_audience(
        self,
        base_hours: List[int],
        adjustments: Dict[str, Any]
    ) -> List[int]:
        """Optimize posting times based on audience analysis."""
        optimized_hours = list(base_hours)
        
        if adjustments.get('peak_hours'):
            # Merge and prioritize audience-specific peak hours
            audience_peaks = adjustments['peak_hours']
            for hour in audience_peaks:
                if hour not in optimized_hours:
                    optimized_hours.append(hour)
        
        if adjustments.get('evening_preference'):
            # Add more evening hours for younger audiences
            evening_hours = [18, 19, 20, 21]
            for hour in evening_hours:
                if hour not in optimized_hours:
                    optimized_hours.append(hour)
        
        if adjustments.get('business_hours_focus'):
            # Filter to business hours only
            business_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
            optimized_hours = [h for h in optimized_hours if h in business_hours]
        
        # Sort and limit to top 5 times
        optimized_hours.sort()
        return optimized_hours[:5]
    
    def _optimize_days_for_audience(
        self,
        base_days: List[str],
        adjustments: Dict[str, Any]
    ) -> List[str]:
        """Optimize posting days based on audience analysis."""
        optimized_days = list(base_days)
        
        if adjustments.get('weekend_boost'):
            # Add weekend days if not present
            weekend_days = ['Saturday', 'Sunday']
            for day in weekend_days:
                if day not in optimized_days:
                    optimized_days.append(day)
        
        if adjustments.get('business_hours_focus'):
            # Focus on weekdays only
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            optimized_days = [day for day in optimized_days if day in weekdays]
        
        return optimized_days[:5]  # Limit to 5 days
    
    def _adjust_posting_frequency(
        self,
        base_frequency: str,
        adjustments: Dict[str, Any],
        agent_input: AgentInput
    ) -> str:
        """Adjust posting frequency based on campaign needs."""
        if adjustments.get('frequent_posting'):
            frequency_map = {
                'Daily': '2-3 times daily',
                '2-3 times weekly': 'Daily',
                '3-5 times daily': '5-7 times daily'
            }
            return frequency_map.get(base_frequency, base_frequency)
        
        if adjustments.get('consistent_schedule'):
            # Ensure consistent daily posting for awareness campaigns
            if 'weekly' in base_frequency.lower():
                return 'Daily'
        
        return base_frequency
    
    async def _create_posting_sequence(
        self,
        agent_input: AgentInput,
        platform_schedules: Dict[str, PlatformSchedule]
    ) -> List[Dict[str, Any]]:
        """Create a coordinated posting sequence across platforms."""
        posting_sequence = []
        
        # Generate posting events for the next 7 days
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            day_name = current_date.strftime('%A')
            
            for platform, schedule in platform_schedules.items():
                if day_name in schedule.best_days:
                    # Create posting events for this platform on this day
                    for time_str in schedule.optimal_times:
                        hour = int(time_str.split(':')[0])
                        posting_time = current_date.replace(hour=hour)
                        
                        # Only include future times
                        if posting_time > datetime.now():
                            posting_event = {
                                'platform': platform,
                                'scheduled_time': posting_time.isoformat(),
                                'day_of_week': day_name,
                                'hour': hour,
                                'content_type': self._determine_content_type(platform, hour),
                                'priority': self._calculate_priority(platform, hour, day_name)
                            }
                            posting_sequence.append(posting_event)
        
        # Sort by priority and time
        posting_sequence.sort(key=lambda x: (x['priority'], x['scheduled_time']), reverse=True)
        
        # Limit to reasonable number of posts
        return posting_sequence[:50]
    
    def _determine_content_type(self, platform: str, hour: int) -> str:
        """Determine appropriate content type based on platform and time."""
        if platform == 'linkedin':
            if 8 <= hour <= 10:
                return 'professional_insight'
            elif 12 <= hour <= 14:
                return 'industry_news'
            else:
                return 'thought_leadership'
        
        elif platform == 'instagram':
            if 6 <= hour <= 10:
                return 'lifestyle'
            elif 11 <= hour <= 15:
                return 'product_showcase'
            else:
                return 'behind_scenes'
        
        elif platform == 'twitter':
            if 9 <= hour <= 12:
                return 'news_commentary'
            elif 15 <= hour <= 18:
                return 'engagement_post'
            else:
                return 'casual_update'
        
        elif platform == 'facebook':
            if 13 <= hour <= 15:
                return 'community_post'
            elif 20 <= hour <= 21:
                return 'entertainment'
            else:
                return 'general_update'
        
        elif platform == 'tiktok':
            if 6 <= hour <= 10:
                return 'morning_motivation'
            elif 19 <= hour <= 21:
                return 'entertainment'
            else:
                return 'trending_content'
        
        return 'general_content'
    
    def _calculate_priority(self, platform: str, hour: int, day: str) -> int:
        """Calculate posting priority based on platform, time, and day."""
        priority = 50  # Base priority
        
        # Platform-specific priority adjustments
        platform_priorities = {
            'instagram': 10,
            'facebook': 8,
            'linkedin': 7,
            'twitter': 9,
            'tiktok': 8
        }
        priority += platform_priorities.get(platform, 5)
        
        # Time-based adjustments
        if platform in self.platform_data:
            peak_windows = self.platform_data[platform].get('peak_engagement_windows', [])
            for start_hour, end_hour in peak_windows:
                if start_hour <= hour <= end_hour:
                    priority += 15
                    break
        
        # Day-based adjustments
        if day in ['Saturday', 'Sunday']:
            if platform in ['instagram', 'facebook', 'tiktok']:
                priority += 5  # Weekend boost for visual platforms
            else:
                priority -= 5  # Weekday focus for professional platforms
        
        return priority
    
    async def _create_schedule_result(
        self,
        platform_schedules: Dict[str, PlatformSchedule],
        posting_sequence: List[Dict[str, Any]]
    ) -> ScheduleResult:
        """Create the final schedule result object."""
        schedule_result = ScheduleResult()
        
        # Set platform schedules
        for platform, schedule in platform_schedules.items():
            setattr(schedule_result, platform, schedule)
        
        # Set posting sequence
        schedule_result.posting_sequence = posting_sequence
        
        return schedule_result
    
    async def _get_fallback_schedule(self, agent_input: AgentInput) -> Dict[str, Any]:
        """Get fallback schedule when main scheduling fails."""
        self.logger.warning("Using fallback campaign schedule")
        
        # Create basic schedules for each platform
        fallback_schedules = {}
        for platform in agent_input.target_platforms:
            platform_lower = platform.lower()
            
            if platform_lower in self.platform_data:
                base_data = self.platform_data[platform_lower]
                fallback_schedule = PlatformSchedule(
                    optimal_times=[f"{hour}:00" for hour in base_data['optimal_hours'][:3]],
                    best_days=base_data['optimal_days'][:3],
                    posting_frequency=base_data['posting_frequency']
                )
            else:
                # Generic fallback
                fallback_schedule = PlatformSchedule(
                    optimal_times=['9:00', '12:00', '17:00'],
                    best_days=['Tuesday', 'Wednesday', 'Thursday'],
                    posting_frequency='Daily'
                )
            
            fallback_schedules[platform_lower] = fallback_schedule
        
        # Create basic posting sequence
        fallback_sequence = [
            {
                'platform': platform,
                'scheduled_time': (datetime.now() + timedelta(days=1)).replace(hour=12).isoformat(),
                'day_of_week': 'Tomorrow',
                'hour': 12,
                'content_type': 'general_content',
                'priority': 50
            }
            for platform in agent_input.target_platforms
        ]
        
        schedule_result = ScheduleResult()
        for platform, schedule in fallback_schedules.items():
            setattr(schedule_result, platform, schedule)
        schedule_result.posting_sequence = fallback_sequence
        
        return {
            'schedule': schedule_result.dict(),
            'metadata': {
                'scheduling_timestamp': datetime.utcnow().isoformat(),
                'fallback_used': True,
                'reason': 'Primary scheduling process failed',
                'agent_version': '1.0.0'
            }
        }


# Global agent instance
campaign_scheduler_agent = CampaignSchedulerAgent()