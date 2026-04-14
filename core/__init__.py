"""Core module with interfaces and dependency injection."""

from core.interfaces import (
    LLMClientProtocol,
    RAGSearchProtocol,
    RerankerProtocol,
    StateManagerProtocol,
    MetricsProtocol,
)
from core.container import Container, get_container
from core.retry import (
    retry_async,
    retry_llm_call,
    CircuitBreaker,
    CircuitBreakerOpen,
)
from core.rate_limiter import (
    RateLimiter,
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
)

__all__ = [
    # Interfaces
    "LLMClientProtocol",
    "RAGSearchProtocol",
    "RerankerProtocol",
    "StateManagerProtocol",
    "MetricsProtocol",
    # DI Container
    "Container",
    "get_container",
    # Retry & Circuit Breaker
    "retry_async",
    "retry_llm_call",
    "CircuitBreaker",
    "CircuitBreakerOpen",
    # Rate Limiting
    "RateLimiter",
    "TokenBucketRateLimiter",
    "SlidingWindowRateLimiter",
]
