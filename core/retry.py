"""
Retry utilities with exponential backoff and circuit breaker.

Provides resilient execution patterns for LLM calls and other external services.
"""

import asyncio
import functools
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional, Sequence, Type, TypeVar, Union

import structlog
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    wait_random_exponential,
    before_sleep_log,
    after_log,
)

logger = structlog.get_logger()


# ============================================================================
# Retry Decorators
# ============================================================================

def retry_async(
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
    non_retryable_exceptions: tuple[Type[Exception], ...] = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
    ),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for async functions with exponential backoff retry.
    
    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time between retries (seconds)
        max_wait: Maximum wait time between retries (seconds)
        exponential_base: Base for exponential backoff
        retryable_exceptions: Exceptions that trigger retry
        non_retryable_exceptions: Exceptions that should not be retried
        on_retry: Optional callback called on each retry
    
    Example:
        @retry_async(max_attempts=3, min_wait=1.0)
        async def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except non_retryable_exceptions as e:
                    # Don't retry these
                    logger.warning(
                        "non_retryable_error",
                        function=func.__name__,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                    raise
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            "max_retries_exceeded",
                            function=func.__name__,
                            attempts=max_attempts,
                            error=str(e),
                        )
                        raise
                    
                    # Calculate wait time with exponential backoff + jitter
                    wait_time = min(
                        max_wait,
                        min_wait * (exponential_base ** (attempt - 1))
                    )
                    # Add jitter (±25%)
                    import random
                    wait_time *= (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=attempt,
                        max_attempts=max_attempts,
                        wait_seconds=round(wait_time, 2),
                        error=str(e),
                    )
                    
                    if on_retry:
                        on_retry(e, attempt)
                    
                    await asyncio.sleep(wait_time)
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def retry_llm_call(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 120.0,
):
    """
    Specialized retry decorator for LLM API calls.
    
    Handles common LLM API errors:
    - Rate limiting (429)
    - Server errors (5xx)
    - Timeout errors
    - Connection errors
    """
    # Common LLM API exceptions
    try:
        import google.api_core.exceptions as google_exc
        import httpx
        import aiohttp
        
        retryable = (
            google_exc.ResourceExhausted,  # Rate limit
            google_exc.ServiceUnavailable,
            google_exc.DeadlineExceeded,
            google_exc.InternalServerError,
            httpx.TimeoutException,
            httpx.ConnectError,
            aiohttp.ClientError,
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
    except ImportError:
        retryable = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
    
    return retry_async(
        max_attempts=max_attempts,
        min_wait=min_wait,
        max_wait=max_wait,
        retryable_exceptions=retryable,
    )


# ============================================================================
# Circuit Breaker
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, name: str, until: datetime):
        self.name = name
        self.until = until
        super().__init__(
            f"Circuit breaker '{name}' is open until {until.isoformat()}"
        )


@dataclass
class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by "opening" the circuit after
    a threshold of failures, rejecting subsequent calls until
    a recovery period has passed.
    
    Usage:
        breaker = CircuitBreaker(name="llm_api", failure_threshold=5)
        
        @breaker
        async def call_api():
            ...
        
        # Or manually:
        async with breaker:
            result = await call_api()
    """
    
    name: str
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 3
    
    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: Optional[datetime] = field(default=None, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)."""
        return self._state == CircuitState.OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return True
        
        elapsed = datetime.now() - self._last_failure_time
        return elapsed.total_seconds() >= self.timeout_seconds
    
    async def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state
        
        logger.info(
            "circuit_breaker_transition",
            name=self.name,
            from_state=old_state.value,
            to_state=new_state.value,
            failure_count=self._failure_count,
        )
        
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._half_open_calls = 0
            self._success_count = 0
    
    async def record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                
                if self._success_count >= self.success_threshold:
                    await self._transition_to(CircuitState.CLOSED)
            
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = max(0, self._failure_count - 1)
    
    async def record_failure(self) -> None:
        """Record a failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            
            if self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                await self._transition_to(CircuitState.OPEN)
                
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    await self._transition_to(CircuitState.OPEN)
    
    async def can_execute(self) -> bool:
        """Check if a call can be executed."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    await self._transition_to(CircuitState.HALF_OPEN)
                    return True
                return False
            
            # Half-open: allow limited calls
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            
            return False
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not await self.can_execute():
            reset_time = (
                self._last_failure_time + timedelta(seconds=self.timeout_seconds)
                if self._last_failure_time
                else datetime.now()
            )
            raise CircuitBreakerOpen(self.name, reset_time)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is None:
            await self.record_success()
        else:
            await self.record_failure()
        return False  # Don't suppress exceptions
    
    def __call__(self, func: Callable) -> Callable:
        """Use as a decorator."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                return await func(*args, **kwargs)
        return wrapper


# ============================================================================
# Fallback Pattern
# ============================================================================

def with_fallback(
    fallback_value: Any = None,
    fallback_func: Optional[Callable] = None,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator that provides a fallback value/function on failure.
    
    Args:
        fallback_value: Static value to return on failure
        fallback_func: Function to call on failure (receives exception)
        exceptions: Exception types to catch
    
    Example:
        @with_fallback(fallback_value="Default response")
        async def call_api():
            ...
        
        @with_fallback(fallback_func=lambda e: f"Error: {e}")
        async def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:
                logger.warning(
                    "fallback_triggered",
                    function=func.__name__,
                    error=str(e),
                )
                
                if fallback_func:
                    return fallback_func(e)
                return fallback_value
                
        return wrapper
    return decorator


# ============================================================================
# Timeout Wrapper
# ============================================================================

def with_timeout(seconds: float):
    """
    Decorator that adds a timeout to async functions.
    
    Example:
        @with_timeout(30.0)
        async def slow_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    "operation_timeout",
                    function=func.__name__,
                    timeout_seconds=seconds,
                )
                raise
        return wrapper
    return decorator


# ============================================================================
# Combined Resilience Decorator
# ============================================================================

def resilient(
    max_retries: int = 3,
    timeout_seconds: float = 60.0,
    circuit_breaker: Optional[CircuitBreaker] = None,
    fallback_value: Any = None,
):
    """
    Combined resilience decorator with retry, timeout, circuit breaker, and fallback.
    
    Example:
        @resilient(max_retries=3, timeout_seconds=30.0)
        async def call_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Apply decorators in order (innermost first)
        wrapped = func
        
        # 1. Retry (innermost - will be executed first)
        wrapped = retry_async(max_attempts=max_retries)(wrapped)
        
        # 2. Timeout
        wrapped = with_timeout(timeout_seconds)(wrapped)
        
        # 3. Circuit breaker
        if circuit_breaker:
            wrapped = circuit_breaker(wrapped)
        
        # 4. Fallback (outermost)
        if fallback_value is not None:
            wrapped = with_fallback(fallback_value=fallback_value)(wrapped)
        
        return wrapped
    return decorator
