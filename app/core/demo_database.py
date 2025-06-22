"""
Demo database - in-memory storage for hackathon demo
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import uuid

from app.utils.logging import get_logger

logger = get_logger(__name__)


class DemoDatabase:
    """In-memory database for demo purposes."""
    
    def __init__(self):
        """Initialize demo database."""
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("demo_database")
        self.logger.info("Demo database initialized (in-memory)")
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new campaign."""
        campaign_id = campaign_data.get('campaign_id', f"demo_{uuid.uuid4().hex[:8]}")
        campaign_data['campaign_id'] = campaign_id
        campaign_data['created_at'] = datetime.utcnow()
        campaign_data['updated_at'] = datetime.utcnow()
        
        self.campaigns[campaign_id] = campaign_data
        self.logger.info(f"Created demo campaign: {campaign_id}")
        return campaign_id
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign by ID."""
        return self.campaigns.get(campaign_id)
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign data."""
        if campaign_id in self.campaigns:
            self.campaigns[campaign_id].update(updates)
            self.campaigns[campaign_id]['updated_at'] = datetime.utcnow()
            self.logger.info(f"Updated demo campaign: {campaign_id}")
            return True
        return False
    
    async def update_agent_progress(
        self,
        campaign_id: str,
        agent_name: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Update agent progress."""
        if campaign_id not in self.campaigns:
            return False
        
        campaign = self.campaigns[campaign_id]
        agent_progress = campaign.get('agent_progress', [])
        
        # Find and update the specific agent's progress
        updated = False
        for i, agent in enumerate(agent_progress):
            if agent.get('agent_name') == agent_name:
                agent_progress[i].update(progress_data)
                agent_progress[i]['updated_at'] = datetime.utcnow()
                updated = True
                break
        
        if not updated:
            # Add new agent progress entry
            progress_data.update({
                'agent_name': agent_name,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
            agent_progress.append(progress_data)
        
        campaign['agent_progress'] = agent_progress
        campaign['updated_at'] = datetime.utcnow()
        
        self.logger.info(f"Updated agent progress for {agent_name} in campaign {campaign_id}")
        return True
    
    async def list_campaigns(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List campaigns."""
        campaigns = list(self.campaigns.values())
        
        if status:
            campaigns = [c for c in campaigns if c.get('status') == status]
        
        # Sort by created_at
        campaigns.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        # Apply pagination
        return campaigns[offset:offset + limit]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for demo database."""
        return {
            'status': 'healthy',
            'mode': 'demo',
            'campaigns_count': len(self.campaigns),
            'message': 'Demo in-memory database'
        }


# Global demo database instance
demo_db = DemoDatabase()