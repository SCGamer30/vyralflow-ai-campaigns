from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import uuid

from app.models.agent import AgentType, AgentInput, AgentOutput
from app.models.campaign import (
    CampaignRequest, CampaignResponse, CampaignStatus, 
    AgentProgress, AgentStatus, CampaignResults,
    PerformancePredictions, TrendingTopic
)
from app.agents.trend_analyzer import trend_analyzer_agent
from app.agents.content_writer import content_writer_agent
from app.agents.visual_designer import visual_designer_agent
from app.agents.campaign_scheduler import campaign_scheduler_agent
from app.services.firestore_service import firestore_service
from app.core.exceptions import AgentExecutionException, CampaignNotFoundException
from app.utils.logging import get_logger
from app.utils.helpers import generate_campaign_id

logger = get_logger(__name__)


class CampaignOrchestrator:
    """
    Main orchestrator class that coordinates all 4 agents in sequence.
    Manages campaign execution flow and provides real-time progress updates.
    """
    
    def __init__(self):
        """Initialize the campaign orchestrator."""
        self.logger = get_logger("orchestrator")
        
        # Agent execution order
        self.agent_sequence = [
            (AgentType.TREND_ANALYZER, trend_analyzer_agent),
            (AgentType.CONTENT_WRITER, content_writer_agent),
            (AgentType.VISUAL_DESIGNER, visual_designer_agent),
            (AgentType.CAMPAIGN_SCHEDULER, campaign_scheduler_agent)
        ]
        
        # Active campaigns tracking
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Campaign orchestrator initialized")
    
    async def create_campaign(self, campaign_request: CampaignRequest) -> CampaignResponse:
        """
        Create and start a new campaign.
        
        Args:
            campaign_request: Campaign request data
            
        Returns:
            CampaignResponse: Initial campaign response with ID and status
        """
        campaign_id = generate_campaign_id()
        self.logger.info(f"Creating campaign {campaign_id} for {campaign_request.business_name}")
        
        try:
            # Initialize agent progress tracking
            agent_progress = []
            for agent_type, _ in self.agent_sequence:
                progress = AgentProgress(
                    agent_name=agent_type.value,
                    status=AgentStatus.PENDING,
                    progress_percentage=0,
                    message="Waiting to start"
                )
                agent_progress.append(progress)
            
            # Create campaign document in database
            campaign_data = {
                'campaign_id': campaign_id,
                'business_name': campaign_request.business_name,
                'industry': campaign_request.industry,
                'campaign_goal': campaign_request.campaign_goal,
                'target_platforms': [p.value for p in campaign_request.target_platforms],
                'brand_voice': campaign_request.brand_voice.value,
                'target_audience': campaign_request.target_audience,
                'keywords': campaign_request.keywords,
                'status': CampaignStatus.PROCESSING.value,
                'agent_progress': [progress.dict() for progress in agent_progress],
                'created_at': datetime.utcnow(),
                'results': None
            }
            
            await firestore_service.create_campaign(campaign_data)
            
            # Add to active campaigns
            self.active_campaigns[campaign_id] = {
                'request': campaign_request,
                'status': CampaignStatus.PROCESSING,
                'current_agent_index': 0,
                'results': {},
                'started_at': datetime.utcnow()
            }
            
            # Start campaign execution asynchronously
            asyncio.create_task(self._execute_campaign(campaign_id, campaign_request))
            
            # Return initial response
            response = CampaignResponse(
                campaign_id=campaign_id,
                status=CampaignStatus.PROCESSING,
                agent_progress=agent_progress,
                created_at=datetime.utcnow()
            )
            
            self.logger.info(f"Campaign {campaign_id} created and started")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to create campaign: {e}")
            raise AgentExecutionException("orchestrator", f"Campaign creation failed: {e}")
    
    async def _execute_campaign(self, campaign_id: str, campaign_request: CampaignRequest) -> None:
        """
        Execute the campaign by running all agents in sequence.
        
        Args:
            campaign_id: Campaign identifier
            campaign_request: Campaign request data
        """
        self.logger.info(f"Starting execution of campaign {campaign_id}")
        
        try:
            agent_results = {}
            
            # Execute each agent in sequence
            for i, (agent_type, agent_instance) in enumerate(self.agent_sequence):
                self.logger.info(f"Executing agent {agent_type.value} for campaign {campaign_id}")
                
                # Update current agent index
                if campaign_id in self.active_campaigns:
                    self.active_campaigns[campaign_id]['current_agent_index'] = i
                
                # Create agent input
                agent_input = AgentInput(
                    campaign_id=campaign_id,
                    business_name=campaign_request.business_name,
                    industry=campaign_request.industry,
                    campaign_goal=campaign_request.campaign_goal,
                    target_platforms=[p.value for p in campaign_request.target_platforms],
                    brand_voice=campaign_request.brand_voice.value,
                    target_audience=campaign_request.target_audience,
                    keywords=campaign_request.keywords,
                    previous_results=agent_results
                )
                
                # Execute agent
                agent_output = await agent_instance.execute(agent_input)
                
                # Store results
                if agent_output.status.value == 'completed' and agent_output.results:
                    agent_results.update(agent_output.results)
                    
                    # Update active campaign results
                    if campaign_id in self.active_campaigns:
                        self.active_campaigns[campaign_id]['results'].update(agent_output.results)
                
                # Check if agent failed
                if agent_output.status.value == 'failed':
                    error_msg = f"Agent {agent_type.value} failed: {agent_output.error_message}"
                    self.logger.error(error_msg)
                    
                    # Update campaign status to failed
                    await self._update_campaign_status(campaign_id, CampaignStatus.FAILED, error_msg)
                    return
                
                self.logger.info(f"Agent {agent_type.value} completed for campaign {campaign_id}")
            
            # All agents completed successfully
            await self._finalize_campaign(campaign_id, agent_results)
            
        except Exception as e:
            error_msg = f"Campaign execution failed: {str(e)}"
            self.logger.error(f"Campaign {campaign_id} failed: {e}")
            await self._update_campaign_status(campaign_id, CampaignStatus.FAILED, error_msg)
        
        finally:
            # Remove from active campaigns
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
    
    async def _finalize_campaign(self, campaign_id: str, agent_results: Dict[str, Any]) -> None:
        """
        Finalize the campaign with all results.
        
        Args:
            campaign_id: Campaign identifier
            agent_results: Combined results from all agents
        """
        self.logger.info(f"Finalizing campaign {campaign_id}")
        
        try:
            # Create final results object
            campaign_results = CampaignResults()
            
            # Map agent results to structured format
            if 'trends' in agent_results:
                campaign_results.trends = agent_results['trends']
            
            if 'content' in agent_results:
                campaign_results.content = agent_results['content']
            
            if 'visuals' in agent_results:
                campaign_results.visuals = agent_results['visuals']
            
            if 'schedule' in agent_results:
                campaign_results.schedule = agent_results['schedule']
                
            # Generate performance predictions based on available data
            performance_predictions = self._generate_performance_predictions(agent_results)
            campaign_results.performance_predictions = performance_predictions
            
            # Update campaign in database
            updates = {
                'status': CampaignStatus.COMPLETED.value,
                'results': campaign_results.dict(),
                'completed_at': datetime.utcnow()
            }
            
            await firestore_service.update_campaign(campaign_id, updates)
            
            self.logger.info(f"Campaign {campaign_id} completed successfully")
            
        except Exception as e:
            error_msg = f"Failed to finalize campaign: {str(e)}"
            self.logger.error(error_msg)
            await self._update_campaign_status(campaign_id, CampaignStatus.FAILED, error_msg)
    
    async def _update_campaign_status(
        self,
        campaign_id: str,
        status: CampaignStatus,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update campaign status in database.
        
        Args:
            campaign_id: Campaign identifier
            status: New campaign status
            error_message: Error message if status is FAILED
        """
        try:
            updates = {'status': status.value}
            
            if status == CampaignStatus.COMPLETED:
                updates['completed_at'] = datetime.utcnow()
            elif status == CampaignStatus.FAILED:
                updates['error_message'] = error_message
                updates['completed_at'] = datetime.utcnow()
            
            await firestore_service.update_campaign(campaign_id, updates)
            
            # Update active campaigns if present
            if campaign_id in self.active_campaigns:
                self.active_campaigns[campaign_id]['status'] = status
            
        except Exception as e:
            self.logger.error(f"Failed to update campaign status: {e}")
    
    async def get_campaign_status(self, campaign_id: str) -> CampaignResponse:
        """
        Get current campaign status.
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            CampaignResponse: Current campaign status and progress
        """
        try:
            # Get campaign from database
            campaign_data = await firestore_service.get_campaign(campaign_id)
            
            if not campaign_data:
                raise CampaignNotFoundException(campaign_id)
            
            # Parse agent progress
            agent_progress = []
            for progress_data in campaign_data.get('agent_progress', []):
                progress = AgentProgress(**progress_data)
                agent_progress.append(progress)
            
            # Parse results if available
            results = None
            if campaign_data.get('results'):
                results = CampaignResults(**campaign_data['results'])
            
            response = CampaignResponse(
                campaign_id=campaign_id,
                status=CampaignStatus(campaign_data['status']),
                agent_progress=agent_progress,
                results=results,
                created_at=campaign_data['created_at'],
                completed_at=campaign_data.get('completed_at'),
                error_message=campaign_data.get('error_message')
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to get campaign status: {e}")
            raise CampaignNotFoundException(campaign_id)
    
    async def get_campaign_results(self, campaign_id: str) -> CampaignResults:
        """
        Get campaign results.
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            CampaignResults: Complete campaign results
        """
        try:
            campaign_data = await firestore_service.get_campaign(campaign_id)
            
            if not campaign_data:
                raise CampaignNotFoundException(campaign_id)
            
            if campaign_data['status'] != CampaignStatus.COMPLETED.value:
                raise AgentExecutionException(
                    "orchestrator",
                    f"Campaign {campaign_id} is not completed. Current status: {campaign_data['status']}"
                )
            
            results_data = campaign_data.get('results')
            if not results_data:
                raise AgentExecutionException(
                    "orchestrator",
                    f"No results available for campaign {campaign_id}"
                )
            
            return CampaignResults(**results_data)
            
        except Exception as e:
            self.logger.error(f"Failed to get campaign results: {e}")
            raise
    
    async def list_campaigns(
        self,
        status: Optional[CampaignStatus] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[CampaignResponse]:
        """
        List campaigns with optional filtering.
        
        Args:
            status: Optional status filter
            limit: Maximum number of campaigns to return
            offset: Offset for pagination
            
        Returns:
            List[CampaignResponse]: List of campaigns
        """
        try:
            status_filter = status.value if status else None
            campaigns_data = await firestore_service.list_campaigns(
                limit=limit,
                offset=offset,
                status=status_filter
            )
            
            campaigns = []
            for campaign_data in campaigns_data:
                # Parse agent progress
                agent_progress = []
                for progress_data in campaign_data.get('agent_progress', []):
                    progress = AgentProgress(**progress_data)
                    agent_progress.append(progress)
                
                # Parse results if available
                results = None
                if campaign_data.get('results'):
                    results = CampaignResults(**campaign_data['results'])
                
                campaign = CampaignResponse(
                    campaign_id=campaign_data['campaign_id'],
                    status=CampaignStatus(campaign_data['status']),
                    agent_progress=agent_progress,
                    results=results,
                    created_at=campaign_data['created_at'],
                    completed_at=campaign_data.get('completed_at'),
                    error_message=campaign_data.get('error_message')
                )
                campaigns.append(campaign)
            
            return campaigns
            
        except Exception as e:
            self.logger.error(f"Failed to list campaigns: {e}")
            raise
    
    async def cancel_campaign(self, campaign_id: str) -> bool:
        """
        Cancel an active campaign.
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            bool: True if cancellation was successful
        """
        try:
            # Check if campaign is active
            if campaign_id not in self.active_campaigns:
                self.logger.warning(f"Campaign {campaign_id} is not active, cannot cancel")
                return False
            
            # Try to cancel current agent execution
            current_agent_index = self.active_campaigns[campaign_id]['current_agent_index']
            if current_agent_index < len(self.agent_sequence):
                _, agent_instance = self.agent_sequence[current_agent_index]
                await agent_instance.cancel_execution()
            
            # Update campaign status
            await self._update_campaign_status(
                campaign_id,
                CampaignStatus.FAILED,
                "Campaign cancelled by user"
            )
            
            # Remove from active campaigns
            if campaign_id in self.active_campaigns:
                del self.active_campaigns[campaign_id]
            
            self.logger.info(f"Campaign {campaign_id} cancelled successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cancel campaign {campaign_id}: {e}")
            return False
    
    async def get_active_campaigns(self) -> List[str]:
        """
        Get list of active campaign IDs.
        
        Returns:
            List[str]: List of active campaign IDs
        """
        return list(self.active_campaigns.keys())
    
    def _generate_performance_predictions(self, agent_results: Dict[str, Any]) -> PerformancePredictions:
        """
        Generate performance predictions based on agent results.
        
        Args:
            agent_results: Combined results from all agents
            
        Returns:
            PerformancePredictions: Generated performance predictions
        """
        # Default values
        viral_probability = "65%"
        estimated_reach = "5,000-10,000"
        engagement_rate = "3.2%"
        roi_prediction = "2.5x"
        confidence_score = 75.0
        
        # Adjust based on trend analysis if available
        if 'trends' in agent_results:
            trends = agent_results['trends']
            
            # Use viral probability from trends if available
            if 'viral_probability' in trends:
                viral_probability = trends['viral_probability']
            
            # Adjust confidence score based on trend confidence
            if 'confidence_score' in trends:
                # Scale from 0-1 to 0-100
                trend_confidence = trends.get('confidence_score', 0.5) * 100
                confidence_score = (confidence_score + trend_confidence) / 2
        
        # Generate metrics breakdown
        metrics_breakdown = {
            "likes_estimate": f"{int(float(viral_probability.replace('%', '')) * 50)}+",
            "shares_estimate": f"{int(float(viral_probability.replace('%', '')) * 10)}+",
            "comments_estimate": f"{int(float(viral_probability.replace('%', '')) * 15)}+",
            "impressions_estimate": estimated_reach
        }
        
        return PerformancePredictions(
            viral_probability=viral_probability,
            estimated_reach=estimated_reach,
            engagement_rate=engagement_rate,
            roi_prediction=roi_prediction,
            confidence_score=confidence_score,
            metrics_breakdown=metrics_breakdown
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the orchestrator and all agents.
        
        Returns:
            Dict: Health status information
        """
        try:
            health_status = {
                'orchestrator': 'healthy',
                'active_campaigns': len(self.active_campaigns),
                'agents': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Check each agent health
            for agent_type, agent_instance in self.agent_sequence:
                try:
                    agent_health = await agent_instance.health_check()
                    health_status['agents'][agent_type.value] = agent_health
                except Exception as e:
                    health_status['agents'][agent_type.value] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'orchestrator': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Global orchestrator instance
campaign_orchestrator = CampaignOrchestrator()