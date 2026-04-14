"""Base agent class with common functionality."""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

import structlog
from pydantic import BaseModel

from config import (
    ModelsConfig,
    StateManager,
    ArticleState,
    QualityThresholds,
)


logger = structlog.get_logger()


class AgentRole(Enum):
    """Agent role categories."""
    RESEARCH = "research"
    WRITING = "writing"
    QUALITY = "quality"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentContext:
    """Context provided to agents for execution."""
    
    # Core state
    state_manager: StateManager
    models_config: ModelsConfig
    quality_thresholds: QualityThresholds
    
    # Current task
    current_section: Optional[str] = None
    current_iteration: int = 0
    
    # RAG interface
    rag_query: Optional[Callable] = None
    
    # Communication
    send_to_agent: Optional[Callable] = None
    
    # Observability
    log: structlog.BoundLogger = field(
        default_factory=lambda: structlog.get_logger()
    )
    
    # Feature flags
    parallel_quality_checks: bool = True
    cache_research: bool = True
    verbose: bool = False


@dataclass
class AgentResult:
    """Standardized result from agent execution."""
    
    success: bool
    agent_name: str
    action: str
    
    # Primary output
    output: Any = None
    output_type: str = "text"
    
    # Metrics
    confidence: float = 0.0
    quality_score: Optional[int] = None
    
    # Timing
    started_at: str = ""
    completed_at: str = ""
    duration_ms: int = 0
    
    # Token usage
    tokens_input: int = 0
    tokens_output: int = 0
    model_used: str = ""
    
    # Errors and warnings
    error: Optional[str] = None
    warnings: list[str] = field(default_factory=list)
    
    # Follow-up suggestions
    suggested_next_agents: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    
    # Handoff data
    handoff_data: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "agent_name": self.agent_name,
            "action": self.action,
            "output_type": self.output_type,
            "confidence": self.confidence,
            "quality_score": self.quality_score,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "model_used": self.model_used,
            "error": self.error,
            "warnings": self.warnings,
            "suggested_next_agents": self.suggested_next_agents,
        }


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str,
        version: str = "1.0.0"
    ):
        self.name = name
        self.role = role
        self.description = description
        self.version = version
        
        self.log = structlog.get_logger().bind(agent=name)
        
        # Will be set by context
        self._context: Optional[AgentContext] = None
        self._llm_client: Optional[Any] = None
    
    @property
    def context(self) -> AgentContext:
        """Get current context."""
        if self._context is None:
            raise RuntimeError(f"Agent {self.name} not initialized with context")
        return self._context
    
    @property
    def state(self) -> ArticleState:
        """Shortcut to article state."""
        return self.context.state_manager.state
    
    def initialize(self, context: AgentContext) -> None:
        """Initialize agent with context."""
        self._context = context
        self.log = context.log.bind(agent=self.name)
        self._setup_llm_client()
        self.on_initialize()
    
    def _setup_llm_client(self) -> None:
        """Set up LLM client based on model config."""
        model_spec = self.context.models_config.get_model_for_agent(self.name)
        model_name = model_spec.name if hasattr(model_spec, 'name') else str(model_spec)
        temperature = self.context.models_config.get_temperature_for_agent(self.name)
        
        # Lazy import to avoid circular dependencies
        # Actual client setup will be done by subclasses
        self._model_name = model_name
        self._temperature = temperature
        
        self.log.info(
            "llm_configured",
            model=model_name,
            temperature=temperature
        )
    
    def on_initialize(self) -> None:
        """Hook for subclasses to perform additional initialization."""
        pass
    
    async def execute(self, action: str, **kwargs) -> AgentResult:
        """Execute an action and return standardized result."""
        started_at = datetime.now()
        start_time = time.perf_counter()
        
        self.log.info("action_started", action=action, kwargs=list(kwargs.keys()))
        
        try:
            # Call the abstract method
            output = await self._execute_action(action, **kwargs)
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            result = AgentResult(
                success=True,
                agent_name=self.name,
                action=action,
                output=output,
                started_at=started_at.isoformat(),
                completed_at=datetime.now().isoformat(),
                duration_ms=duration_ms,
                model_used=self._model_name,
            )
            
            # Let subclass enrich result
            result = self._enrich_result(result)
            
            self.log.info(
                "action_completed",
                action=action,
                duration_ms=duration_ms,
                success=True
            )
            
            # Log to state
            self.state.log_agent_call(
                agent_name=self.name,
                action=action,
                input_summary=str(kwargs)[:200],
                output_summary=str(output)[:200] if output else "",
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            self.log.error(
                "action_failed",
                action=action,
                error=str(e),
                duration_ms=duration_ms
            )
            
            # Log error to state
            self.state.log_error(
                agent=self.name,
                error_type=type(e).__name__,
                message=str(e)
            )
            
            return AgentResult(
                success=False,
                agent_name=self.name,
                action=action,
                error=str(e),
                started_at=started_at.isoformat(),
                completed_at=datetime.now().isoformat(),
                duration_ms=duration_ms,
                model_used=self._model_name,
            )
    
    @abstractmethod
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Implement action execution. Override in subclasses."""
        pass
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Hook for subclasses to enrich result with additional data."""
        return result
    
    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> str:
        """Call the LLM with the configured model."""
        # This is a placeholder - actual implementation will use
        # google.generativeai or anthropic SDK based on model
        
        # For now, log the call
        self.log.debug(
            "llm_call",
            model=self._model_name,
            prompt_length=len(prompt),
            max_tokens=max_tokens,
            json_mode=json_mode
        )
        
        # Actual implementation to be added
        raise NotImplementedError(
            "LLM calling not yet implemented - "
            "subclasses should override or use LangChain"
        )
    
    async def query_rag(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None
    ) -> list[dict]:
        """Query the RAG system."""
        if self.context.rag_query is None:
            self.log.warning("rag_not_configured")
            return []
        
        return await self.context.rag_query(
            query=query,
            top_k=top_k,
            filters=filters
        )
    
    async def send_message(
        self,
        to_agent: str,
        message: dict
    ) -> Optional[AgentResult]:
        """Send a message to another agent."""
        if self.context.send_to_agent is None:
            self.log.warning("messaging_not_configured")
            return None
        
        return await self.context.send_to_agent(
            from_agent=self.name,
            to_agent=to_agent,
            message=message
        )
    
    def get_section_state(self, section_id: Optional[str] = None):
        """Get state for a section."""
        sid = section_id or self.context.current_section
        if sid is None:
            raise ValueError("No section specified")
        return self.state.sections.get(sid)
    
    def validate_input(self, **kwargs) -> list[str]:
        """Validate input parameters. Override in subclasses."""
        return []  # No errors by default
    
    def get_prompt_template(self, action: str) -> str:
        """Get prompt template for an action. Override in subclasses."""
        return ""
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, role={self.role.value})"


# Type variable for typed agent results
T = TypeVar("T", bound=AgentResult)
