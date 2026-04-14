"""
Protocol interfaces for dependency injection.

These interfaces define contracts that implementations must follow.
Using Protocol (structural subtyping) instead of ABC allows for
more flexible duck typing while maintaining type safety.
"""

from typing import (
    Any,
    AsyncIterator,
    Callable,
    Optional,
    Protocol,
    Sequence,
    TypeVar,
    runtime_checkable,
)
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# LLM Client Protocol
# ============================================================================

@dataclass
class LLMResponse:
    """Standardized LLM response."""
    
    content: str
    model: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    finish_reason: str = ""
    cached: bool = False


@runtime_checkable
class LLMClientProtocol(Protocol):
    """
    Protocol for LLM clients.
    
    Any class implementing these methods can be used as an LLM client.
    """
    
    model: str
    temperature: float
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
        stop_sequences: Optional[list[str]] = None
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        ...
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM."""
        ...


# ============================================================================
# RAG Search Protocol
# ============================================================================

@dataclass
class SearchResult:
    """Single search result from RAG."""
    
    id: str
    content: str
    score: float
    source: str = ""
    document_title: str = ""
    section: str = ""
    page: int = 0
    search_type: str = "hybrid"
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@runtime_checkable
class RAGSearchProtocol(Protocol):
    """Protocol for RAG search implementations."""
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None
    ) -> list[SearchResult]:
        """Search for relevant documents."""
        ...
    
    async def search_hybrid(
        self,
        query: str,
        top_k: int = 10,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> list[SearchResult]:
        """Hybrid search combining dense and sparse retrieval."""
        ...
    
    async def add_documents(
        self,
        documents: list[dict],
        batch_size: int = 100
    ) -> int:
        """Add documents to the index. Returns count added."""
        ...


@runtime_checkable
class RerankerProtocol(Protocol):
    """Protocol for reranking search results."""
    
    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Rerank search results based on query relevance."""
        ...


# ============================================================================
# State Manager Protocol
# ============================================================================

@runtime_checkable
class StateManagerProtocol(Protocol):
    """Protocol for article state management."""
    
    @property
    def state(self) -> Any:
        """Get current state."""
        ...
    
    def create_state(
        self,
        article_id: str,
        title: str,
        **kwargs
    ) -> Any:
        """Create a new article state."""
        ...
    
    def save_checkpoint(self, label: Optional[str] = None) -> str:
        """Save a checkpoint. Returns checkpoint ID."""
        ...
    
    def rollback(self, checkpoint_id: str) -> bool:
        """Rollback to a checkpoint."""
        ...
    
    def get_section_content(self, section_id: str) -> Optional[str]:
        """Get content for a section."""
        ...
    
    def update_section(
        self,
        section_id: str,
        content: str,
        score: Optional[int] = None
    ) -> None:
        """Update a section's content and score."""
        ...


# ============================================================================
# Metrics Protocol
# ============================================================================

@runtime_checkable
class MetricsProtocol(Protocol):
    """Protocol for metrics collection."""
    
    def increment(
        self,
        name: str,
        value: int = 1,
        labels: Optional[dict] = None
    ) -> None:
        """Increment a counter metric."""
        ...
    
    def gauge(
        self,
        name: str,
        value: float,
        labels: Optional[dict] = None
    ) -> None:
        """Set a gauge metric."""
        ...
    
    def histogram(
        self,
        name: str,
        value: float,
        labels: Optional[dict] = None
    ) -> None:
        """Record a histogram observation."""
        ...
    
    def timer(self, name: str, labels: Optional[dict] = None):
        """Context manager for timing operations."""
        ...


# ============================================================================
# Agent Protocol
# ============================================================================

@dataclass
class AgentResult:
    """Standardized result from agent execution."""
    
    success: bool
    agent_name: str
    action: str
    output: Any = None
    output_type: str = "text"
    confidence: float = 0.0
    quality_score: Optional[int] = None
    error: Optional[str] = None
    warnings: list = None
    duration_ms: int = 0
    tokens_used: int = 0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol for agents in the system."""
    
    name: str
    role: str
    
    def initialize(self, context: Any) -> None:
        """Initialize agent with context."""
        ...
    
    async def execute(self, action: str, **kwargs) -> AgentResult:
        """Execute an action and return result."""
        ...


# ============================================================================
# Cache Protocol
# ============================================================================

@runtime_checkable
class CacheProtocol(Protocol):
    """Protocol for caching implementations."""
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        ...
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """Set a value in cache."""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        ...
    
    async def clear(self) -> None:
        """Clear all cached values."""
        ...


# ============================================================================
# Event Bus Protocol
# ============================================================================

EventHandler = Callable[[str, Any], None]


@runtime_checkable
class EventBusProtocol(Protocol):
    """Protocol for event-driven communication."""
    
    def subscribe(self, event_type: str, handler: EventHandler) -> str:
        """Subscribe to events. Returns subscription ID."""
        ...
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        ...
    
    async def publish(self, event_type: str, data: Any) -> None:
        """Publish an event."""
        ...


# ============================================================================
# Factory Protocol
# ============================================================================

T = TypeVar("T")


@runtime_checkable
class FactoryProtocol(Protocol[T]):
    """Generic factory protocol."""
    
    def create(self, **kwargs) -> T:
        """Create an instance."""
        ...
    
    def register(self, name: str, creator: Callable[..., T]) -> None:
        """Register a creator function."""
        ...
