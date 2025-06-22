from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of agents in the system."""
    TREND_ANALYZER = "trend_analyzer"
    CONTENT_WRITER = "content_writer"
    VISUAL_DESIGNER = "visual_designer"
    CAMPAIGN_SCHEDULER = "campaign_scheduler"


class AgentExecutionStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    agent_type: AgentType
    timeout_seconds: int = Field(default=300, ge=1)
    retry_attempts: int = Field(default=3, ge=0)
    enable_fallback: bool = Field(default=True)
    fallback_data: Optional[Dict[str, Any]] = None


class AgentInput(BaseModel):
    """Input data for agent execution."""
    
    campaign_id: str
    business_name: str
    industry: str
    campaign_goal: str
    target_platforms: List[str]
    brand_voice: str
    target_audience: Optional[str] = None
    keywords: Optional[List[str]] = None
    previous_results: Optional[Dict[str, Any]] = None


class AgentOutput(BaseModel):
    """Output data from agent execution."""
    
    agent_type: AgentType
    campaign_id: str
    status: AgentExecutionStatus
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentMetrics(BaseModel):
    """Metrics for agent performance."""
    
    agent_type: AgentType
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    success_rate: float = 0.0


class AgentMessage(BaseModel):
    """Message between agents."""
    
    from_agent: AgentType
    to_agent: AgentType
    campaign_id: str
    message_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)