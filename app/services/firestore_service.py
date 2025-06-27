from google.cloud import firestore
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.core.exceptions import DatabaseException
from app.models.campaign import CampaignResponse, AgentProgress
from app.utils.logging import get_logger

logger = get_logger(__name__)


class FirestoreService:
    """Service for Firestore database operations."""
    
    def __init__(self):
        """Initialize Firestore client."""
        try:
            self.db = firestore.Client(project=settings.google_cloud_project)
            self.executor = ThreadPoolExecutor(max_workers=10)
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise DatabaseException("firestore_init", str(e))
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new campaign document."""
        try:
            campaign_ref = self.db.collection(settings.firestore_collection_campaigns).document()
            campaign_id = campaign_ref.id
            
            campaign_data.update({
                'campaign_id': campaign_id,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            })
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                campaign_ref.set,
                campaign_data
            )
            
            logger.info(f"Created campaign: {campaign_id}")
            return campaign_id
            
        except Exception as e:
            logger.error(f"Failed to create campaign: {e}")
            raise DatabaseException("create_campaign", str(e))
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign by ID."""
        try:
            campaign_ref = self.db.collection(settings.firestore_collection_campaigns).document(campaign_id)
            
            loop = asyncio.get_event_loop()
            doc = await loop.run_in_executor(
                self.executor,
                campaign_ref.get
            )
            
            if doc.exists:
                data = doc.to_dict()
                logger.debug(f"Retrieved campaign: {campaign_id}")
                return data
            else:
                logger.warning(f"Campaign not found: {campaign_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get campaign {campaign_id}: {e}")
            raise DatabaseException("get_campaign", str(e))
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> bool:
        """Update campaign data."""
        try:
            campaign_ref = self.db.collection(settings.firestore_collection_campaigns).document(campaign_id)
            
            updates['updated_at'] = datetime.now(timezone.utc)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                campaign_ref.update,
                updates
            )
            
            logger.info(f"Updated campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update campaign {campaign_id}: {e}")
            raise DatabaseException("update_campaign", str(e))
    
    async def update_agent_progress(
        self,
        campaign_id: str,
        agent_name: str,
        progress_data: Dict[str, Any]
    ) -> bool:
        """Update agent progress for a campaign."""
        try:
            # Update the agent progress in the campaign document
            campaign_ref = self.db.collection(settings.firestore_collection_campaigns).document(campaign_id)
            
            # Get current campaign data
            loop = asyncio.get_event_loop()
            doc = await loop.run_in_executor(self.executor, campaign_ref.get)
            
            if not doc.exists:
                raise DatabaseException("update_agent_progress", f"Campaign {campaign_id} not found")
            
            campaign_data = doc.to_dict()
            agent_progress = campaign_data.get('agent_progress', [])
            
            # Find and update the specific agent's progress
            updated = False
            for i, agent in enumerate(agent_progress):
                if agent['agent_name'] == agent_name:
                    agent_progress[i].update(progress_data)
                    agent_progress[i]['updated_at'] = datetime.now(timezone.utc)
                    updated = True
                    break
            
            if not updated:
                # Add new agent progress entry
                progress_data.update({
                    'agent_name': agent_name,
                    'created_at': datetime.now(timezone.utc),
                    'updated_at': datetime.now(timezone.utc)
                })
                agent_progress.append(progress_data)
            
            # Update the campaign document
            await loop.run_in_executor(
                self.executor,
                campaign_ref.update,
                {
                    'agent_progress': agent_progress,
                    'updated_at': datetime.now(timezone.utc)
                }
            )
            
            logger.info(f"Updated agent progress for {agent_name} in campaign {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update agent progress: {e}")
            raise DatabaseException("update_agent_progress", str(e))
    
    async def list_campaigns(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List campaigns with pagination and filtering."""
        try:
            query = self.db.collection(settings.firestore_collection_campaigns)
            
            if status:
                query = query.where('status', '==', status)
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
            query = query.limit(limit).offset(offset)
            
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                self.executor,
                lambda: list(query.stream())
            )
            
            campaigns = []
            for doc in docs:
                data = doc.to_dict()
                campaigns.append(data)
            
            logger.debug(f"Retrieved {len(campaigns)} campaigns")
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to list campaigns: {e}")
            raise DatabaseException("list_campaigns", str(e))
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign."""
        try:
            campaign_ref = self.db.collection(settings.firestore_collection_campaigns).document(campaign_id)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                campaign_ref.delete
            )
            
            logger.info(f"Deleted campaign: {campaign_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete campaign {campaign_id}: {e}")
            raise DatabaseException("delete_campaign", str(e))
    
    async def get_campaigns_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all campaigns with a specific status."""
        try:
            query = self.db.collection(settings.firestore_collection_campaigns)
            query = query.where('status', '==', status)
            
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                self.executor,
                lambda: list(query.stream())
            )
            
            campaigns = []
            for doc in docs:
                data = doc.to_dict()
                campaigns.append(data)
            
            logger.debug(f"Retrieved {len(campaigns)} campaigns with status {status}")
            return campaigns
            
        except Exception as e:
            logger.error(f"Failed to get campaigns by status {status}: {e}")
            raise DatabaseException("get_campaigns_by_status", str(e))


# Global service instance
firestore_service = FirestoreService()