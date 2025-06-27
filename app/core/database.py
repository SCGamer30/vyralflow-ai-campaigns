from google.cloud import firestore
from typing import Optional, Dict, Any, List
import os

from app.core.config import settings
from app.core.exceptions import DatabaseException
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """
    Database manager for Firestore operations.
    Provides centralized database connection and configuration.
    """
    
    def __init__(self):
        """Initialize database manager."""
        self._client: Optional[firestore.Client] = None
        self.project_id = settings.google_cloud_project
        self.logger = get_logger("database")
    
    @property
    def client(self) -> firestore.Client:
        """Get Firestore client, creating it if necessary."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> firestore.Client:
        """Create and configure Firestore client."""
        try:
            # Set up authentication
            if settings.google_application_credentials:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_application_credentials
            
            # Create client
            client = firestore.Client(project=self.project_id)
            
            # Test connection
            self._test_connection(client)
            
            self.logger.info(f"Firestore client initialized for project: {self.project_id}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create Firestore client: {e}")
            raise DatabaseException("client_creation", str(e))
    
    def _test_connection(self, client: firestore.Client) -> None:
        """Test database connection."""
        try:
            # Try to read from a test collection
            test_ref = client.collection('_health_check').document('test')
            test_ref.get()  # This will raise an exception if connection fails
            self.logger.info("Database connection test successful")
        except Exception as e:
            self.logger.warning(f"Database connection test failed: {e}")
            # Don't raise exception - connection might still work for actual operations
    
    async def initialize_collections(self) -> None:
        """Initialize required collections and indexes."""
        try:
            # Create indexes for better query performance
            await self._create_indexes()
            self.logger.info("Database collections initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize collections: {e}")
            raise DatabaseException("collection_init", str(e))
    
    async def _create_indexes(self) -> None:
        """Create database indexes for optimal performance."""
        # Note: In a real application, you would create these indexes
        # through the Firebase console or using the Firebase CLI
        # This is a placeholder for documentation purposes
        
        indexes_to_create = [
            {
                'collection': settings.firestore_collection_campaigns,
                'fields': [
                    {'field': 'status', 'order': 'ASCENDING'},
                    {'field': 'created_at', 'order': 'DESCENDING'}
                ]
            },
            {
                'collection': settings.firestore_collection_campaigns,
                'fields': [
                    {'field': 'business_name', 'order': 'ASCENDING'},
                    {'field': 'created_at', 'order': 'DESCENDING'}
                ]
            }
        ]
        
        self.logger.info(f"Indexes to be created: {len(indexes_to_create)}")
        # In production, these would be created via Firebase CLI or console
    
    def get_collection_ref(self, collection_name: str):
        """Get reference to a collection."""
        return self.client.collection(collection_name)
    
    def get_document_ref(self, collection_name: str, document_id: str):
        """Get reference to a document."""
        return self.client.collection(collection_name).document(document_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform database health check."""
        try:
            # Test basic operations
            test_doc_ref = self.client.collection('_health_check').document('test')
            
            # Write test
            test_data = {'timestamp': firestore.SERVER_TIMESTAMP, 'status': 'healthy'}
            test_doc_ref.set(test_data)
            
            # Read test
            doc = test_doc_ref.get()
            
            # Clean up
            test_doc_ref.delete()
            
            return {
                'status': 'healthy',
                'project_id': self.project_id,
                'connection': 'active',
                'read_write': 'operational'
            }
            
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'project_id': self.project_id,
                'connection': 'failed',
                'error': str(e)
            }
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> str:
        """Create a new campaign in the database."""
        try:
            collection_ref = self.get_collection_ref(settings.firestore_collection_campaigns)
            doc_ref = collection_ref.document()
            
            # Add timestamps and default status
            campaign_data.update({
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'status': 'processing'
            })
            
            doc_ref.set(campaign_data)
            self.logger.info(f"Campaign created with ID: {doc_ref.id}")
            return doc_ref.id
            
        except Exception as e:
            self.logger.error(f"Failed to create campaign: {e}")
            raise DatabaseException("campaign_creation", str(e))
    
    async def get_campaign(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign by ID."""
        try:
            doc_ref = self.get_document_ref(settings.firestore_collection_campaigns, campaign_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get campaign {campaign_id}: {e}")
            raise DatabaseException("campaign_retrieval", str(e))
    
    async def update_campaign(self, campaign_id: str, updates: Dict[str, Any]) -> None:
        """Update campaign data."""
        try:
            doc_ref = self.get_document_ref(settings.firestore_collection_campaigns, campaign_id)
            
            # Add update timestamp
            updates['updated_at'] = firestore.SERVER_TIMESTAMP
            
            doc_ref.update(updates)
            self.logger.info(f"Campaign {campaign_id} updated")
            
        except Exception as e:
            self.logger.error(f"Failed to update campaign {campaign_id}: {e}")
            raise DatabaseException("campaign_update", str(e))
    
    async def update_agent_progress(self, campaign_id: str, agent_type: str, 
                                   step: int, total_steps: int, message: str) -> None:
        """Update agent progress for a campaign."""
        try:
            doc_ref = self.get_document_ref(settings.firestore_collection_campaigns, campaign_id)
            
            # Get current progress data
            doc = doc_ref.get()
            if not doc.exists:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            data = doc.to_dict()
            if 'agent_progress' not in data:
                data['agent_progress'] = {}
            
            # Update agent progress
            data['agent_progress'][agent_type] = {
                'step': step,
                'total_steps': total_steps,
                'message': message,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Update the document
            doc_ref.update({
                'agent_progress': data['agent_progress'],
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            
            self.logger.info(f"Agent progress updated for {campaign_id}: {agent_type} {step}/{total_steps}")
            
        except Exception as e:
            self.logger.error(f"Failed to update agent progress for {campaign_id}: {e}")
            raise DatabaseException("agent_progress_update", str(e))
    
    async def list_campaigns(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List campaigns with optional limit."""
        try:
            collection_ref = self.get_collection_ref(settings.firestore_collection_campaigns)
            query = collection_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)
            
            docs = query.stream()
            campaigns = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                campaigns.append(data)
            
            self.logger.info(f"Retrieved {len(campaigns)} campaigns")
            return campaigns
            
        except Exception as e:
            self.logger.error(f"Failed to list campaigns: {e}")
            raise DatabaseException("campaign_listing", str(e))
    
    def close(self) -> None:
        """Close database connection."""
        if self._client:
            # Firestore client doesn't have explicit close method
            # It will be garbage collected
            self._client = None
            self.logger.info("Database connection closed")


# Global database manager instance
db_manager = DatabaseManager()