"""
Unit tests for core resilience components.

Tests for:
- Retry decorator with exponential backoff
- Circuit breaker pattern
- Rate limiters (Token Bucket, Sliding Window)
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from core.retry import (
    retry_async,
    retry_llm_call,
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitState,
    with_fallback,
    with_timeout,
    resilient,
)
from core.rate_limiter import (
    TokenBucketRateLimiter,
    SlidingWindowRateLimiter,
    PerKeyRateLimiter,
    AdaptiveRateLimiter,
)


# ============================================================================
# Retry Decorator Tests
# ============================================================================

class TestRetryAsync:
    """Tests for retry_async decorator."""
    
    @pytest.mark.asyncio
    async def test_succeeds_on_first_try(self):
        """Function succeeds immediately without retry."""
        call_count = 0
        
        @retry_async(max_attempts=3)
        async def succeeding_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await succeeding_func()
        
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retries_on_failure_then_succeeds(self):
        """Function fails initially but succeeds on retry."""
        call_count = 0
        
        @retry_async(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await flaky_func()
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self):
        """Function raises exception after exhausting retries."""
        @retry_async(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def always_fails():
            raise ConnectionError("Permanent failure")
        
        with pytest.raises(ConnectionError):
            await always_fails()
    
    @pytest.mark.asyncio
    async def test_no_retry_for_non_retryable_exceptions(self):
        """Non-retryable exceptions are raised immediately."""
        call_count = 0
        
        @retry_async(
            max_attempts=3,
            non_retryable_exceptions=(ValueError,),
            min_wait=0.01
        )
        async def validation_fail():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid input")
        
        with pytest.raises(ValueError):
            await validation_fail()
        
        assert call_count == 1  # No retries
    
    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """on_retry callback is called on each retry."""
        retry_exceptions = []
        
        def track_retry(exc, attempt):
            retry_exceptions.append((type(exc).__name__, attempt))
        
        @retry_async(max_attempts=3, min_wait=0.01, on_retry=track_retry)
        async def flaky():
            if len(retry_exceptions) < 2:
                raise ConnectionError("fail")
            return "success"
        
        result = await flaky()
        
        assert result == "success"
        assert len(retry_exceptions) == 2
        assert retry_exceptions[0] == ("ConnectionError", 1)
        assert retry_exceptions[1] == ("ConnectionError", 2)


class TestRetryLLMCall:
    """Tests for retry_llm_call decorator."""
    
    @pytest.mark.asyncio
    async def test_retries_connection_error(self):
        """Retries on connection errors."""
        attempts = []
        
        @retry_llm_call(max_attempts=3, min_wait=0.01, max_wait=0.1)
        async def call_api():
            attempts.append(1)
            if len(attempts) < 2:
                raise ConnectionError("Network issue")
            return "response"
        
        result = await call_api()
        
        assert result == "response"
        assert len(attempts) == 2


# ============================================================================
# Circuit Breaker Tests
# ============================================================================

class TestCircuitBreaker:
    """Tests for CircuitBreaker."""
    
    @pytest.mark.asyncio
    async def test_starts_closed(self):
        """Circuit starts in closed state."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.is_closed
    
    @pytest.mark.asyncio
    async def test_opens_after_threshold_failures(self):
        """Circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        assert cb.is_closed
        
        # Record failures
        await cb.record_failure()
        await cb.record_failure()
        assert cb.is_closed  # Still closed
        
        await cb.record_failure()
        assert cb.is_open  # Now open
    
    @pytest.mark.asyncio
    async def test_rejects_calls_when_open(self):
        """Open circuit rejects calls."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            timeout_seconds=10.0
        )
        
        # Open the circuit
        await cb.record_failure()
        await cb.record_failure()
        
        assert cb.is_open
        assert not await cb.can_execute()
    
    @pytest.mark.asyncio
    async def test_transitions_to_half_open_after_timeout(self):
        """Circuit transitions to half-open after timeout."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            timeout_seconds=0.1
        )
        
        # Open the circuit
        await cb.record_failure()
        await cb.record_failure()
        assert cb.is_open
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        
        # Should transition to half-open
        can_exec = await cb.can_execute()
        assert can_exec
        assert cb.state == CircuitState.HALF_OPEN
    
    @pytest.mark.asyncio
    async def test_closes_after_successes_in_half_open(self):
        """Circuit closes after successful calls in half-open."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            success_threshold=2,
            timeout_seconds=0.1
        )
        
        # Open and wait for half-open
        await cb.record_failure()
        await cb.record_failure()
        await asyncio.sleep(0.15)
        await cb.can_execute()  # Trigger transition
        
        # Record successes
        await cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN
        
        await cb.record_success()
        assert cb.state == CircuitState.CLOSED
    
    @pytest.mark.asyncio
    async def test_as_context_manager(self):
        """Circuit breaker works as async context manager."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        async with cb:
            pass  # Success
        
        assert cb._failure_count == 0
    
    @pytest.mark.asyncio
    async def test_context_manager_records_failure(self):
        """Context manager records failure on exception."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        with pytest.raises(ValueError):
            async with cb:
                raise ValueError("test error")
        
        assert cb._failure_count == 1
    
    @pytest.mark.asyncio
    async def test_as_decorator(self):
        """Circuit breaker works as decorator."""
        cb = CircuitBreaker(name="test", failure_threshold=2)
        
        @cb
        async def protected_func():
            return "success"
        
        result = await protected_func()
        assert result == "success"


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestTokenBucketRateLimiter:
    """Tests for TokenBucketRateLimiter."""
    
    @pytest.mark.asyncio
    async def test_allows_burst_up_to_capacity(self):
        """Allows burst of requests up to capacity."""
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=5)
        
        # Should all succeed immediately
        for _ in range(5):
            wait_time = await limiter.acquire()
            assert wait_time == 0.0
    
    @pytest.mark.asyncio
    async def test_try_acquire_returns_false_when_empty(self):
        """try_acquire returns False when no tokens available."""
        limiter = TokenBucketRateLimiter(rate=1.0, capacity=2)
        
        # Drain tokens
        assert await limiter.try_acquire()
        assert await limiter.try_acquire()
        
        # Should fail
        assert not await limiter.try_acquire()
    
    @pytest.mark.asyncio
    async def test_refills_over_time(self):
        """Tokens refill over time."""
        limiter = TokenBucketRateLimiter(rate=100.0, capacity=2)
        
        # Drain tokens
        await limiter.acquire()
        await limiter.acquire()
        
        # Wait for refill (at 100/s, 1 token = 0.01s)
        await asyncio.sleep(0.02)
        
        # Should have tokens now
        assert await limiter.try_acquire()


class TestSlidingWindowRateLimiter:
    """Tests for SlidingWindowRateLimiter."""
    
    @pytest.mark.asyncio
    async def test_allows_up_to_max_requests(self):
        """Allows requests up to the limit."""
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=1.0)
        
        for _ in range(3):
            wait_time = await limiter.acquire()
            assert wait_time == 0.0
    
    @pytest.mark.asyncio
    async def test_blocks_over_limit(self):
        """Blocks when limit is exceeded."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=0.1)
        
        # Use up limit
        await limiter.acquire()
        await limiter.acquire()
        
        # Third should fail
        assert not await limiter.try_acquire()


class TestPerKeyRateLimiter:
    """Tests for PerKeyRateLimiter."""
    
    @pytest.mark.asyncio
    async def test_separate_limits_per_key(self):
        """Each key has separate rate limit."""
        limiter = PerKeyRateLimiter(rate=100.0, capacity=2)
        
        # Key A
        await limiter.acquire("key_a")
        await limiter.acquire("key_a")
        assert not await limiter.try_acquire("key_a")
        
        # Key B should be independent
        assert await limiter.try_acquire("key_b")


class TestAdaptiveRateLimiter:
    """Tests for AdaptiveRateLimiter."""
    
    @pytest.mark.asyncio
    async def test_decreases_rate_on_error(self):
        """Rate decreases when rate limit error occurs."""
        limiter = AdaptiveRateLimiter(
            initial_rate=10.0,
            min_rate=1.0,
            decrease_factor=0.5
        )
        
        initial_rate = limiter._current_rate
        await limiter.record_rate_limit_error()
        
        assert limiter._current_rate < initial_rate
        assert limiter._current_rate == initial_rate * 0.5
    
    @pytest.mark.asyncio
    async def test_increases_rate_on_successes(self):
        """Rate increases after consecutive successes."""
        limiter = AdaptiveRateLimiter(
            initial_rate=5.0,
            max_rate=20.0,
            increase_factor=1.2
        )
        limiter._success_threshold = 3
        
        initial_rate = limiter._current_rate
        
        # Record successes
        for _ in range(3):
            await limiter.record_success()
        
        assert limiter._current_rate > initial_rate


# ============================================================================
# Fallback and Timeout Tests
# ============================================================================

class TestWithFallback:
    """Tests for with_fallback decorator."""
    
    @pytest.mark.asyncio
    async def test_returns_result_on_success(self):
        """Returns actual result when function succeeds."""
        @with_fallback(fallback_value="fallback")
        async def succeeds():
            return "success"
        
        result = await succeeds()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_returns_fallback_on_failure(self):
        """Returns fallback when function fails."""
        @with_fallback(fallback_value="fallback")
        async def fails():
            raise ValueError("error")
        
        result = await fails()
        assert result == "fallback"
    
    @pytest.mark.asyncio
    async def test_calls_fallback_func(self):
        """Calls fallback function with exception."""
        @with_fallback(fallback_func=lambda e: f"Error: {e}")
        async def fails():
            raise ValueError("test")
        
        result = await fails()
        assert result == "Error: test"


class TestWithTimeout:
    """Tests for with_timeout decorator."""
    
    @pytest.mark.asyncio
    async def test_completes_within_timeout(self):
        """Function completes within timeout."""
        @with_timeout(1.0)
        async def fast():
            return "done"
        
        result = await fast()
        assert result == "done"
    
    @pytest.mark.asyncio
    async def test_raises_on_timeout(self):
        """Raises TimeoutError when function takes too long."""
        @with_timeout(0.05)
        async def slow():
            await asyncio.sleep(1.0)
            return "done"
        
        with pytest.raises(asyncio.TimeoutError):
            await slow()


# ============================================================================
# Resilient Decorator Tests
# ============================================================================

class TestResilient:
    """Tests for resilient decorator."""
    
    @pytest.mark.asyncio
    async def test_combines_all_patterns(self):
        """Resilient decorator combines retry, timeout, and fallback."""
        attempts = []
        
        @resilient(
            max_retries=2,
            timeout_seconds=1.0,
            fallback_value="fallback"
        )
        async def flaky():
            attempts.append(1)
            if len(attempts) == 1:
                raise ConnectionError("retry me")
            return "success"
        
        result = await flaky()
        assert result == "success"
        assert len(attempts) == 2
