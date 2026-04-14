"""
Enhanced Base Agent with Dependency Injection and Resilience.

This is a refactored version of BaseAgent that:
- Uses constructor injection for all dependencies
- Implements retry with exponential backoff
- Integrates circuit breaker pattern
- Applies rate limiting for API calls
- Uses Pydantic for request validation
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Generic
from contextlib import asynccontextmanager

import structlog
from pydantic import BaseModel, Field, ValidationError

from core.interfaces import (
    LLMClientProtocol,
    LLMResponse,
    RAGSearchProtocol,
    MetricsProtocol,
    StateManagerProtocol,
    AgentResult,
)
from core.retry import retry_async, retry_llm_call, CircuitBreaker, CircuitBreakerOpen
from core.rate_limiter import RateLimiter, TokenBucketRateLimiter

logger = structlog.get_logger()


# ============================================================================
# Agent Role and Context
# ============================================================================

class AgentRole(Enum):
    """Agent role categories."""
    RESEARCH = "research"
    WRITING = "writing"
    QUALITY = "quality"
    ORCHESTRATION = "orchestration"


@dataclass
class AgentDependencies:
    """
    All dependencies an agent needs, injected via constructor.
    
    This replaces the previous AgentContext which mixed dependencies
    with runtime state.
    """
    
    # Required dependencies
    llm_client: LLMClientProtocol
    
    # Optional dependencies (can have defaults/mocks)
    state_manager: Optional[StateManagerProtocol] = None
    rag_search: Optional[RAGSearchProtocol] = None
    metrics: Optional[MetricsProtocol] = None
    rate_limiter: Optional[RateLimiter] = None
    circuit_breaker: Optional[CircuitBreaker] = None
    
    # Configuration
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    max_retries: int = 3
    timeout_seconds: float = 120.0
    
    # Feature flags
    enable_caching: bool = True
    verbose: bool = False


# ============================================================================
# Request/Response Models (Pydantic Validation)
# ============================================================================

class BaseRequest(BaseModel):
    """Base class for all agent request models."""
    
    class Config:
        extra = "forbid"  # Fail on unexpected fields


class ExecuteRequest(BaseRequest):
    """Request to execute an agent action."""
    
    action: str = Field(..., min_length=1, max_length=100)
    timeout_override: Optional[float] = Field(None, gt=0, le=600)


# ============================================================================
# Enhanced Base Agent
# ============================================================================

class EnhancedBaseAgent(ABC):
    """
    Abstract base class for all agents with DI and resilience.
    
    Key differences from original BaseAgent:
    1. Dependencies injected via constructor (testable)
    2. Built-in retry with exponential backoff
    3. Circuit breaker prevents cascading failures
    4. Rate limiting for API calls
    5. Pydantic validation for inputs
    6. Structured metrics collection
    
    Usage:
        class MyAgent(EnhancedBaseAgent):
            def __init__(self, deps: AgentDependencies):
                super().__init__(
                    name="my_agent",
                    role=AgentRole.WRITING,
                    deps=deps
                )
            
            async def _execute_action(self, action: str, **kwargs) -> Any:
                # Implementation
                pass
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        deps: AgentDependencies,
        description: str = "",
        version: str = "2.0.0"
    ):
        self.name = name
        self.role = role
        self.description = description
        self.version = version
        
        # Injected dependencies
        self._deps = deps
        self._llm = deps.llm_client
        self._state = deps.state_manager
        self._rag = deps.rag_search
        self._metrics = deps.metrics
        self._rate_limiter = deps.rate_limiter or TokenBucketRateLimiter(
            rate=10.0,
            capacity=20
        )
        self._circuit_breaker = deps.circuit_breaker or CircuitBreaker(
            name=f"agent_{name}",
            failure_threshold=5,
            timeout_seconds=60.0
        )
        
        # Logging
        self.log = structlog.get_logger().bind(
            agent=name,
            role=role.value,
            version=version
        )
        
        # Internal state
        self._initialized = False
        self._call_count = 0
        self._error_count = 0
        self._total_latency_ms = 0
        
        # Response cache (if enabled)
        self._cache: dict[str, Any] = {}
    
    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------
    
    @property
    def state(self) -> Optional[StateManagerProtocol]:
        """Get state manager if available."""
        return self._state
    
    @property
    def article_state(self) -> Any:
        """Get current article state."""
        if self._state:
            return self._state.state
        return None
    
    @property
    def is_healthy(self) -> bool:
        """Check if agent is healthy (circuit not open)."""
        return self._circuit_breaker.is_closed
    
    @property
    def stats(self) -> dict:
        """Get agent statistics."""
        avg_latency = (
            self._total_latency_ms / self._call_count 
            if self._call_count > 0 else 0
        )
        return {
            "name": self.name,
            "call_count": self._call_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(1, self._call_count),
            "avg_latency_ms": avg_latency,
            "circuit_state": self._circuit_breaker.state.value,
        }
    
    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    
    def initialize(self) -> None:
        """
        Initialize the agent.
        
        Called once before first use. Subclasses can override
        on_initialize() for custom setup.
        """
        if self._initialized:
            return
        
        self.log.info("agent_initializing")
        self.on_initialize()
        self._initialized = True
        self.log.info("agent_initialized")
    
    def on_initialize(self) -> None:
        """Hook for subclasses to perform additional setup."""
        pass
    
    async def execute(
        self,
        action: str,
        validate: bool = True,
        use_cache: bool = True,
        **kwargs
    ) -> AgentResult:
        """
        Execute an action with full resilience (retry, circuit breaker, rate limit).
        
        Args:
            action: Name of the action to execute
            validate: Whether to validate kwargs with Pydantic
            use_cache: Whether to use cached results if available
            **kwargs: Action-specific parameters
        
        Returns:
            AgentResult with success/failure and output
        """
        if not self._initialized:
            self.initialize()
        
        started_at = datetime.now()
        start_time = time.perf_counter()
        cache_key = f"{action}:{hash(frozenset(kwargs.items()))}"
        
        # Check cache
        if use_cache and self._deps.enable_caching and cache_key in self._cache:
            self.log.debug("cache_hit", action=action)
            return self._cache[cache_key]
        
        self.log.info(
            "action_started",
            action=action,
            kwargs_keys=list(kwargs.keys())
        )
        
        # Track metrics
        if self._metrics:
            self._metrics.increment(
                "agent_calls_total",
                labels={"agent": self.name, "action": action}
            )
        
        try:
            # Rate limiting
            wait_time = await self._rate_limiter.acquire()
            if wait_time > 0:
                self.log.debug("rate_limited", wait_seconds=wait_time)
            
            # Circuit breaker check
            if not await self._circuit_breaker.can_execute():
                raise CircuitBreakerOpen(
                    self._circuit_breaker.name,
                    datetime.now()
                )
            
            # Validate inputs if requested
            if validate:
                kwargs = self._validate_inputs(action, kwargs)
            
            # Execute with retry
            output = await self._execute_with_retry(action, **kwargs)
            
            # Record success
            await self._circuit_breaker.record_success()
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            self._call_count += 1
            self._total_latency_ms += duration_ms
            
            result = AgentResult(
                success=True,
                agent_name=self.name,
                action=action,
                output=output,
                duration_ms=duration_ms,
            )
            
            # Enrich and cache
            result = self._enrich_result(result)
            
            if use_cache and self._deps.enable_caching:
                self._cache[cache_key] = result
            
            # Track latency
            if self._metrics:
                self._metrics.histogram(
                    "agent_latency_ms",
                    duration_ms,
                    labels={"agent": self.name, "action": action}
                )
            
            self.log.info(
                "action_completed",
                action=action,
                duration_ms=duration_ms,
                success=True
            )
            
            return result
            
        except CircuitBreakerOpen as e:
            self.log.warning(
                "circuit_breaker_open",
                agent=self.name,
                until=e.until.isoformat()
            )
            return AgentResult(
                success=False,
                agent_name=self.name,
                action=action,
                error=f"Circuit breaker open: {e}",
                duration_ms=int((time.perf_counter() - start_time) * 1000),
            )
            
        except ValidationError as e:
            self.log.warning(
                "validation_error",
                action=action,
                errors=e.errors()
            )
            return AgentResult(
                success=False,
                agent_name=self.name,
                action=action,
                error=f"Validation error: {e}",
                duration_ms=int((time.perf_counter() - start_time) * 1000),
            )
            
        except Exception as e:
            await self._circuit_breaker.record_failure()
            self._error_count += 1
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            if self._metrics:
                self._metrics.increment(
                    "agent_errors_total",
                    labels={
                        "agent": self.name,
                        "action": action,
                        "error_type": type(e).__name__
                    }
                )
            
            self.log.error(
                "action_failed",
                action=action,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms
            )
            
            return AgentResult(
                success=False,
                agent_name=self.name,
                action=action,
                error=str(e),
                duration_ms=duration_ms,
            )
    
    # -------------------------------------------------------------------------
    # LLM Interaction (with retry)
    # -------------------------------------------------------------------------
    
    @retry_llm_call(max_attempts=3, min_wait=2.0, max_wait=60.0)
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Generate LLM response with automatic retry.
        
        This method wraps the LLM client with retry logic and
        rate limiting.
        """
        return await self._llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            json_mode=json_mode
        )
    
    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        fallback_response: str = "",
    ) -> str:
        """
        Generate with a fallback value on complete failure.
        
        Useful when you need a response even if LLM fails.
        """
        try:
            response = await self.generate(
                prompt=prompt,
                system_prompt=system_prompt
            )
            return response.content
        except Exception as e:
            self.log.warning(
                "llm_fallback_used",
                error=str(e),
                fallback_length=len(fallback_response)
            )
            return fallback_response
    
    # -------------------------------------------------------------------------
    # RAG Integration
    # -------------------------------------------------------------------------
    
    async def query_rag(
        self,
        query: str,
        top_k: int = 10,
        rerank: bool = True
    ) -> list[dict]:
        """
        Query RAG system for relevant documents.
        
        Returns list of document dicts with content and metadata.
        """
        if not self._rag:
            self.log.warning("rag_not_available")
            return []
        
        try:
            results = await self._rag.search_hybrid(
                query=query,
                top_k=top_k * 2 if rerank else top_k  # Get more for reranking
            )
            
            return [
                {
                    "content": r.content,
                    "source": r.source,
                    "score": r.score,
                    "metadata": r.metadata
                }
                for r in results[:top_k]
            ]
            
        except Exception as e:
            self.log.error("rag_query_failed", query=query[:100], error=str(e))
            return []
    
    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------
    
    def _validate_inputs(self, action: str, kwargs: dict) -> dict:
        """
        Validate inputs using Pydantic model if available.
        
        Override get_request_model() to provide action-specific validation.
        """
        model_class = self.get_request_model(action)
        
        if model_class is None:
            return kwargs
        
        # Validate and return parsed model as dict
        validated = model_class(**kwargs)
        return validated.model_dump()
    
    def get_request_model(self, action: str) -> Optional[type[BaseModel]]:
        """
        Get Pydantic model for validating action inputs.
        
        Override in subclasses to provide per-action validation.
        
        Returns:
            Pydantic model class or None for no validation
        """
        return None
    
    async def _execute_with_retry(self, action: str, **kwargs) -> Any:
        """Execute action with retry logic."""
        # The actual retry is handled by @retry_llm_call on LLM calls
        # This method exists for potential custom retry logic per action
        return await self._execute_action(action, **kwargs)
    
    @abstractmethod
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """
        Execute a specific action. Must be implemented by subclasses.
        
        Args:
            action: Name of the action
            **kwargs: Validated action parameters
        
        Returns:
            Action output (will be wrapped in AgentResult)
        """
        pass
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """
        Enrich result with additional metadata.
        
        Override in subclasses to add action-specific data.
        """
        return result
    
    # -------------------------------------------------------------------------
    # Cache Management
    # -------------------------------------------------------------------------
    
    def clear_cache(self) -> int:
        """Clear response cache. Returns number of entries cleared."""
        count = len(self._cache)
        self._cache.clear()
        self.log.info("cache_cleared", entries=count)
        return count
    
    def cache_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "enabled": self._deps.enable_caching,
        }


# ============================================================================
# Migration Helper
# ============================================================================

def migrate_agent_to_v2(
    old_agent_class: type,
    deps: AgentDependencies
) -> EnhancedBaseAgent:
    """
    Helper to migrate old-style agents to new DI-based agents.
    
    This creates an adapter that wraps old agent behavior.
    """
    # Create instance of old agent
    old_instance = old_agent_class()
    
    class MigratedAgent(EnhancedBaseAgent):
        def __init__(self):
            super().__init__(
                name=old_instance.name,
                role=old_instance.role,
                deps=deps,
                description=old_instance.description,
                version=f"{old_instance.version}-migrated"
            )
            self._old_agent = old_instance
        
        async def _execute_action(self, action: str, **kwargs) -> Any:
            # Delegate to old agent
            return await self._old_agent._execute_action(action, **kwargs)
    
    return MigratedAgent()
