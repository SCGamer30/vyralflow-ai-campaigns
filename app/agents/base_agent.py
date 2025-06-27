from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio
import traceback
import uuid

from app.models.agent import AgentType, AgentInput, AgentOutput, AgentExecutionStatus
from app.models.campaign import AgentProgress, AgentStatus
from app.core.database import db_manager
from app.utils.logging import get_logger
from app.utils.helpers import calculate_progress_percentage

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents in the Vyralflow system.
    Provides common functionality for agent execution, progress tracking, and error handling.
    """
    
    def __init__(self, agent_type: AgentType, timeout_seconds: int = 300):
        """
        Initialize the base agent.
        
        Args:
            agent_type: Type of agent (from AgentType enum)
            timeout_seconds: Maximum execution time in seconds
        """
        self.agent_type = agent_type
        self.agent_name = agent_type.value
        self.timeout_seconds = timeout_seconds
        self.execution_id = None
        self.logger = get_logger(f"agent.{self.agent_name}")
        
        # Agent state
        self.current_campaign_id = None
        self.execution_start_time = None
        self.progress_percentage = 0
        self.status = AgentStatus.PENDING
        self.current_message = "Waiting to start"
        
        self.logger.info(f"Initialized {self.agent_name} agent")
    
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """
        Execute the agent with the given input.
        
        Args:
            agent_input: Input data for the agent
            
        Returns:
            AgentOutput: Results of the agent execution
        """
        self.execution_id = str(uuid.uuid4())
        self.current_campaign_id = agent_input.campaign_id
        self.execution_start_time = datetime.now(timezone.utc)
        
        self.logger.info(f"Starting execution for campaign {agent_input.campaign_id}")
        
        try:
            # Update status to running
            await self._update_progress(AgentStatus.RUNNING, 0, "Starting execution")
            
            # Execute the agent with timeout
            result = await asyncio.wait_for(
                self._execute_impl(agent_input),
                timeout=self.timeout_seconds
            )
            
            # Update final status
            await self._update_progress(AgentStatus.COMPLETED, 100, "Execution completed successfully")
            
            execution_time = (datetime.now(timezone.utc) - self.execution_start_time).total_seconds()
            
            output = AgentOutput(
                agent_type=self.agent_type,
                campaign_id=agent_input.campaign_id,
                status=AgentExecutionStatus.COMPLETED,
                results=result,
                execution_time_seconds=execution_time,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.logger.info(f"Completed execution for campaign {agent_input.campaign_id} in {execution_time:.2f}s")
            return output
            
        except asyncio.TimeoutError:
            error_msg = f"Agent execution timed out after {self.timeout_seconds} seconds"
            self.logger.error(error_msg)
            await self._update_progress(AgentStatus.ERROR, self.progress_percentage, error_msg)
            
            return AgentOutput(
                agent_type=self.agent_type,
                campaign_id=agent_input.campaign_id,
                status=AgentExecutionStatus.FAILED,
                error_message=error_msg,
                execution_time_seconds=self.timeout_seconds,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            error_msg = f"Agent execution failed: {str(e)}"
            error_details = traceback.format_exc()
            self.logger.error(f"{error_msg}\n{error_details}")
            
            await self._update_progress(AgentStatus.ERROR, self.progress_percentage, error_msg)
            
            execution_time = (datetime.now(timezone.utc) - self.execution_start_time).total_seconds()
            
            return AgentOutput(
                agent_type=self.agent_type,
                campaign_id=agent_input.campaign_id,
                status=AgentExecutionStatus.FAILED,
                error_message=error_msg,
                execution_time_seconds=execution_time,
                timestamp=datetime.now(timezone.utc)
            )
    
    @abstractmethod
    async def _execute_impl(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Implement the specific agent logic.
        
        Args:
            agent_input: Input data for the agent
            
        Returns:
            Dict containing the agent's results
        """
        pass
    
    async def _update_progress(
        self,
        status: AgentStatus,
        progress: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the agent's progress in the database.
        
        Args:
            status: Current status of the agent
            progress: Progress percentage (0-100)
            message: Status message
            details: Additional details about the progress
        """
        try:
            self.status = status
            self.progress_percentage = progress
            self.current_message = message
            
            progress_data = {
                'status': status.value,
                'progress_percentage': progress,
                'message': message,
                'started_at': self.execution_start_time,
                'updated_at': datetime.now(timezone.utc)
            }
            
            if status == AgentStatus.COMPLETED:
                progress_data['completed_at'] = datetime.now(timezone.utc)
            elif status == AgentStatus.ERROR:
                progress_data['error_details'] = message
            
            if details:
                progress_data['details'] = details
            
            # Try to update Firestore, but don't block if it fails
            try:
                await asyncio.wait_for(
                    db_manager.update_agent_progress(
                        self.current_campaign_id,
                        self.agent_name,
                        progress_data
                    ),
                    timeout=5.0  # 5 second timeout
                )
            except asyncio.TimeoutError:
                self.logger.warning(f"Database progress update timed out for {self.agent_name}")
            except Exception as db_error:
                self.logger.warning(f"Database progress update failed for {self.agent_name}: {db_error}")
            
            self.logger.debug(f"Updated progress: {progress}% - {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to update progress: {e}")
    
    async def _update_step_progress(self, current_step: int, total_steps: int, step_message: str) -> None:
        """
        Update progress for a specific step within the agent execution.
        
        Args:
            current_step: Current step number (1-based)
            total_steps: Total number of steps
            step_message: Message describing the current step
        """
        progress = calculate_progress_percentage(current_step, total_steps)
        await self._update_progress(
            AgentStatus.RUNNING,
            progress,
            f"Step {current_step}/{total_steps}: {step_message}"
        )
    
    def _validate_input(self, agent_input: AgentInput) -> bool:
        """
        Validate the agent input.
        
        Args:
            agent_input: Input to validate
            
        Returns:
            bool: True if input is valid
        """
        required_fields = ['campaign_id', 'business_name', 'industry', 'campaign_goal']
        
        for field in required_fields:
            if not getattr(agent_input, field, None):
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def _get_fallback_result(self, agent_input: AgentInput) -> Dict[str, Any]:
        """
        Get fallback result when agent execution fails.
        
        Args:
            agent_input: Original input data
            
        Returns:
            Dict containing fallback results
        """
        return {
            'status': 'fallback',
            'message': f'{self.agent_name} used fallback data due to execution failure',
            'campaign_id': agent_input.campaign_id,
            'agent_type': self.agent_type.value,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent.
        
        Returns:
            Dict containing health status
        """
        try:
            # Basic health check - can be overridden by specific agents
            return {
                'agent_name': self.agent_name,
                'status': 'healthy',
                'last_execution': self.execution_start_time.isoformat() if self.execution_start_time else None,
                'current_status': self.status.value,
                'timeout_seconds': self.timeout_seconds
            }
        except Exception as e:
            return {
                'agent_name': self.agent_name,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the agent.
        
        Returns:
            Dict containing agent information
        """
        return {
            'agent_name': self.agent_name,
            'agent_type': self.agent_type.value,
            'timeout_seconds': self.timeout_seconds,
            'current_campaign_id': self.current_campaign_id,
            'execution_id': self.execution_id,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'current_message': self.current_message
        }
    
    async def cancel_execution(self) -> bool:
        """
        Cancel the current execution.
        
        Returns:
            bool: True if cancellation was successful
        """
        try:
            if self.status == AgentStatus.RUNNING:
                await self._update_progress(
                    AgentStatus.ERROR,
                    self.progress_percentage,
                    "Execution cancelled by user"
                )
                self.logger.info(f"Cancelled execution for campaign {self.current_campaign_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel execution: {e}")
            return False


class AgentError(Exception):
    """Custom exception for agent-specific errors."""
    
    def __init__(self, agent_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.agent_name = agent_name
        self.message = message
        self.details = details or {}
        super().__init__(f"{agent_name}: {message}")


class AgentTimeoutError(AgentError):
    """Exception for agent timeout errors."""
    pass


class AgentValidationError(AgentError):
    """Exception for agent input validation errors."""
    pass