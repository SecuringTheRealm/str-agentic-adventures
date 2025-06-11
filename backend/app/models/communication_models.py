"""
Communication models for inter-agent messaging and task allocation.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of inter-agent messages."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentMessage(BaseModel):
    """Message passed between agents."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None  # Links related messages
    requires_response: bool = False


class AgentTask(BaseModel):
    """Task that can be allocated to agents."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    agent_type: str  # Which type of agent should handle this
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = {}
    result: Optional[Dict[str, Any]] = None
    assigned_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    dependencies: List[str] = []  # Task IDs this task depends on
    timeout_seconds: Optional[int] = None


class WorkflowStep(BaseModel):
    """A step in a complex multi-agent workflow."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    agent_type: str
    action: str
    parameters: Dict[str, Any] = {}
    dependencies: List[str] = []  # Step IDs this step depends on
    conditions: Dict[str, Any] = {}  # Conditions that must be met
    timeout_seconds: Optional[int] = None


class Workflow(BaseModel):
    """A complex workflow involving multiple agents."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    steps: List[WorkflowStep]
    status: TaskStatus = TaskStatus.PENDING
    current_step: Optional[str] = None
    context: Dict[str, Any] = {}  # Shared context across steps
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AgentCapability(BaseModel):
    """Defines what an agent can do."""
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    estimated_duration: Optional[int] = None  # seconds


class AgentStatus(BaseModel):
    """Current status and capabilities of an agent."""
    agent_id: str
    agent_type: str
    status: str  # "idle", "busy", "offline"
    capabilities: List[AgentCapability]
    current_tasks: List[str] = []  # Task IDs currently being processed
    load: float = 0.0  # 0.0 to 1.0, represents current workload
    last_heartbeat: datetime = Field(default_factory=datetime.now)