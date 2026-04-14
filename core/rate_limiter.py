"""
Rate limiting implementations for API calls.

Provides different algorithms for rate limiting:
- Token Bucket: Allows bursts, refills over time
- Sliding Window: Strict limit over rolling time window
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import structlog

logger = structlog.get_logger()


# ============================================================================
# Base Rate Limiter
# ============================================================================

class RateLimiter(ABC):
    """Abstract base class for rate limiters."""
    
    @abstractmethod
    async def acquire(self, tokens: int = 1) -> float:
        """
        Acquire tokens from the rate limiter.
        
        Returns the wait time (0 if no wait needed).
        May block if rate limit would be exceeded.
        """
        pass
    
    @abstractmethod
    async def try_acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens without blocking.
        
        Returns True if acquired, False if would exceed limit.
        """
        pass
    
    @abstractmethod
    def get_wait_time(self) -> float:
        """Get estimated wait time until tokens are available."""
        pass


# ============================================================================
# Token Bucket Rate Limiter
# ============================================================================

@dataclass
class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter.
    
    Allows bursting up to capacity, then refills at a steady rate.
    Good for APIs that allow occasional bursts but enforce overall rate.
    
    Args:
        rate: Tokens added per second
        capacity: Maximum tokens in bucket (burst size)
        
    Example:
        # 10 requests/second with burst of 20
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=20)
        
        await limiter.acquire()  # Get 1 token
        await limiter.acquire(5)  # Get 5 tokens
    """
    
    rate: float  # tokens per second
    capacity: int  # max tokens
    
    _tokens: float = field(init=False)
    _last_update: float = field(init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    
    def __post_init__(self):
        self._tokens = float(self.capacity)
        self._last_update = time.monotonic()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self._last_update
        self._tokens = min(
            self.capacity,
            self._tokens + (elapsed * self.rate)
        )
        self._last_update = now
    
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, waiting if necessary."""
        async with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return 0.0
            
            # Calculate wait time
            deficit = tokens - self._tokens
            wait_time = deficit / self.rate
            
            logger.debug(
                "rate_limiter_waiting",
                limiter="token_bucket",
                tokens_requested=tokens,
                tokens_available=self._tokens,
                wait_seconds=round(wait_time, 3),
            )
        
        # Wait outside lock
        await asyncio.sleep(wait_time)
        
        # Acquire after waiting
        async with self._lock:
            self._refill()
            self._tokens -= tokens
            return wait_time
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens without blocking."""
        async with self._lock:
            self._refill()
            
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False
    
    def get_wait_time(self) -> float:
        """Get time until at least 1 token is available."""
        if self._tokens >= 1:
            return 0.0
        deficit = 1 - self._tokens
        return deficit / self.rate


# ============================================================================
# Sliding Window Rate Limiter
# ============================================================================

@dataclass
class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding window rate limiter.
    
    Enforces strict limit over a rolling time window.
    More predictable than token bucket, no burst allowed.
    
    Args:
        max_requests: Maximum requests in the window
        window_seconds: Size of sliding window in seconds
        
    Example:
        # 100 requests per minute
        limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60.0)
    """
    
    max_requests: int
    window_seconds: float
    
    _timestamps: deque = field(default_factory=deque, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    
    def _clean_old_timestamps(self) -> None:
        """Remove timestamps outside the current window."""
        cutoff = time.monotonic() - self.window_seconds
        
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
    
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire permission for request(s), waiting if necessary."""
        total_wait = 0.0
        
        for _ in range(tokens):
            async with self._lock:
                self._clean_old_timestamps()
                
                if len(self._timestamps) < self.max_requests:
                    self._timestamps.append(time.monotonic())
                    continue
                
                # Calculate wait time until oldest request falls out of window
                oldest = self._timestamps[0]
                wait_time = (oldest + self.window_seconds) - time.monotonic()
                
                if wait_time > 0:
                    logger.debug(
                        "rate_limiter_waiting",
                        limiter="sliding_window",
                        current_requests=len(self._timestamps),
                        max_requests=self.max_requests,
                        wait_seconds=round(wait_time, 3),
                    )
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                total_wait += wait_time
                
                async with self._lock:
                    self._clean_old_timestamps()
                    self._timestamps.append(time.monotonic())
        
        return total_wait
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire without blocking."""
        async with self._lock:
            self._clean_old_timestamps()
            
            if len(self._timestamps) + tokens <= self.max_requests:
                for _ in range(tokens):
                    self._timestamps.append(time.monotonic())
                return True
            return False
    
    def get_wait_time(self) -> float:
        """Get time until a request can be made."""
        if len(self._timestamps) < self.max_requests:
            return 0.0
        
        oldest = self._timestamps[0]
        wait = (oldest + self.window_seconds) - time.monotonic()
        return max(0.0, wait)


# ============================================================================
# Per-Key Rate Limiter
# ============================================================================

@dataclass
class PerKeyRateLimiter:
    """
    Rate limiter that tracks limits per key (e.g., per API, per user).
    
    Example:
        limiter = PerKeyRateLimiter(
            rate=10.0,
            capacity=20,
            limiter_class=TokenBucketRateLimiter
        )
        
        await limiter.acquire("gemini_api")
        await limiter.acquire("anthropic_api")
    """
    
    rate: float
    capacity: int
    limiter_class: type = TokenBucketRateLimiter
    
    _limiters: dict = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    
    async def _get_limiter(self, key: str) -> RateLimiter:
        """Get or create limiter for a key."""
        async with self._lock:
            if key not in self._limiters:
                if self.limiter_class == TokenBucketRateLimiter:
                    self._limiters[key] = TokenBucketRateLimiter(
                        rate=self.rate,
                        capacity=self.capacity
                    )
                else:
                    self._limiters[key] = SlidingWindowRateLimiter(
                        max_requests=self.capacity,
                        window_seconds=self.capacity / self.rate
                    )
            return self._limiters[key]
    
    async def acquire(self, key: str, tokens: int = 1) -> float:
        """Acquire tokens for a specific key."""
        limiter = await self._get_limiter(key)
        return await limiter.acquire(tokens)
    
    async def try_acquire(self, key: str, tokens: int = 1) -> bool:
        """Try to acquire tokens for a specific key."""
        limiter = await self._get_limiter(key)
        return await limiter.try_acquire(tokens)


# ============================================================================
# Composite Rate Limiter (Multiple Limits)
# ============================================================================

@dataclass
class CompositeRateLimiter(RateLimiter):
    """
    Combines multiple rate limiters that must all allow the request.
    
    Useful for APIs with multiple rate limit tiers (e.g., per-second and per-day).
    
    Example:
        # 10/second AND 1000/minute
        limiter = CompositeRateLimiter([
            TokenBucketRateLimiter(rate=10.0, capacity=15),
            SlidingWindowRateLimiter(max_requests=1000, window_seconds=60.0),
        ])
    """
    
    limiters: list[RateLimiter]
    
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire from all limiters."""
        total_wait = 0.0
        
        for limiter in self.limiters:
            wait = await limiter.acquire(tokens)
            total_wait += wait
        
        return total_wait
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire from all limiters (atomic check)."""
        # First check if all would succeed
        results = [
            await limiter.try_acquire(tokens) 
            for limiter in self.limiters
        ]
        
        # If any failed, we need to "return" the tokens to those that succeeded
        # This is a simplified implementation - in production you'd want
        # a proper distributed transaction
        if not all(results):
            # Note: tokens already consumed from some limiters
            # This is a known limitation of this simple implementation
            return False
        
        return True
    
    def get_wait_time(self) -> float:
        """Get maximum wait time across all limiters."""
        return max(limiter.get_wait_time() for limiter in self.limiters)


# ============================================================================
# Adaptive Rate Limiter
# ============================================================================

@dataclass
class AdaptiveRateLimiter(RateLimiter):
    """
    Rate limiter that adapts based on response headers or errors.
    
    Automatically adjusts rate when receiving 429 (Too Many Requests)
    or when rate limit headers indicate remaining quota.
    """
    
    initial_rate: float = 10.0
    min_rate: float = 1.0
    max_rate: float = 100.0
    increase_factor: float = 1.1
    decrease_factor: float = 0.5
    
    _current_rate: float = field(init=False)
    _bucket: TokenBucketRateLimiter = field(init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    _consecutive_successes: int = field(default=0, init=False)
    _success_threshold: int = 10  # Increase rate after this many successes
    
    def __post_init__(self):
        self._current_rate = self.initial_rate
        self._bucket = TokenBucketRateLimiter(
            rate=self._current_rate,
            capacity=int(self._current_rate * 2)
        )
    
    async def acquire(self, tokens: int = 1) -> float:
        """Acquire with current adaptive rate."""
        return await self._bucket.acquire(tokens)
    
    async def try_acquire(self, tokens: int = 1) -> bool:
        """Try to acquire with current adaptive rate."""
        return await self._bucket.try_acquire(tokens)
    
    def get_wait_time(self) -> float:
        """Get wait time based on current rate."""
        return self._bucket.get_wait_time()
    
    async def record_success(self) -> None:
        """Record a successful request, potentially increasing rate."""
        async with self._lock:
            self._consecutive_successes += 1
            
            if self._consecutive_successes >= self._success_threshold:
                new_rate = min(
                    self.max_rate,
                    self._current_rate * self.increase_factor
                )
                
                if new_rate != self._current_rate:
                    logger.info(
                        "rate_limiter_adapted",
                        direction="increase",
                        old_rate=self._current_rate,
                        new_rate=new_rate,
                    )
                    self._current_rate = new_rate
                    self._bucket = TokenBucketRateLimiter(
                        rate=new_rate,
                        capacity=int(new_rate * 2)
                    )
                
                self._consecutive_successes = 0
    
    async def record_rate_limit_error(self, retry_after: Optional[float] = None) -> None:
        """Record a rate limit error, decreasing rate."""
        async with self._lock:
            self._consecutive_successes = 0
            
            new_rate = max(
                self.min_rate,
                self._current_rate * self.decrease_factor
            )
            
            logger.warning(
                "rate_limiter_adapted",
                direction="decrease",
                old_rate=self._current_rate,
                new_rate=new_rate,
                retry_after=retry_after,
            )
            
            self._current_rate = new_rate
            self._bucket = TokenBucketRateLimiter(
                rate=new_rate,
                capacity=int(new_rate * 2)
            )
            
            if retry_after:
                await asyncio.sleep(retry_after)
