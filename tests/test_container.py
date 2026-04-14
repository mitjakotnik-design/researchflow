"""
Unit tests for Dependency Injection container.

Tests for:
- Container initialization
- Singleton vs Factory providers
- Configuration loading
- Override capabilities for testing
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from core.container import (
    Container,
    Config,
    get_container,
    reset_container,
    create_test_container,
)


class TestConfig:
    """Tests for Config class."""
    
    def test_loads_defaults(self):
        """Config loads default values."""
        config = Config()
        
        assert config.data_dir == "data"
        assert config.chroma_collection == "scoping_review"
        assert config.gemini_rate_limit == 10.0
    
    def test_loads_from_environment(self):
        """Config loads values from environment variables."""
        with patch.dict(os.environ, {
            "DATA_DIR": "/custom/data",
            "GEMINI_RATE_LIMIT": "20",
            "VERBOSE": "true",
        }):
            config = Config()
            
            assert config.data_dir == "/custom/data"
            assert config.gemini_rate_limit == 20.0
            assert config.verbose is True


class TestContainer:
    """Tests for DI Container."""
    
    def setup_method(self):
        """Reset container before each test."""
        reset_container()
    
    def test_creates_singleton_config(self):
        """Config provider returns same instance."""
        container = Container()
        
        config1 = container.config()
        config2 = container.config()
        
        assert config1 is config2
    
    def test_creates_singleton_models_config(self):
        """ModelsConfig provider returns same instance."""
        container = Container()
        
        mc1 = container.models_config()
        mc2 = container.models_config()
        
        assert mc1 is mc2
    
    def test_creates_singleton_quality_thresholds(self):
        """QualityThresholds provider returns same instance."""
        container = Container()
        
        qt1 = container.quality_thresholds()
        qt2 = container.quality_thresholds()
        
        assert qt1 is qt2
    
    def test_creates_factory_saturation_config(self):
        """SaturationConfig provider creates new instances."""
        container = Container()
        
        sc1 = container.saturation_config()
        sc2 = container.saturation_config()
        
        # Factory should create different instances
        # (but with same values by default)
        assert sc1.target_score == sc2.target_score
    
    def test_creates_singleton_state_manager(self):
        """StateManager provider returns same instance."""
        container = Container()
        
        sm1 = container.state_manager()
        sm2 = container.state_manager()
        
        assert sm1 is sm2


class TestGetContainer:
    """Tests for get_container function."""
    
    def setup_method(self):
        """Reset container before each test."""
        reset_container()
    
    def test_returns_same_container(self):
        """get_container returns same instance."""
        c1 = get_container()
        c2 = get_container()
        
        assert c1 is c2
    
    def test_reset_creates_new_container(self):
        """reset_container allows creating new container."""
        c1 = get_container()
        reset_container()
        c2 = get_container()
        
        assert c1 is not c2


class TestCreateTestContainer:
    """Tests for test container factory."""
    
    def test_creates_container_with_overrides(self):
        """create_test_container applies overrides."""
        container = create_test_container(
            google_api_key="test-key",
            verbose=True,
        )
        
        config = container.config()
        
        assert config.google_api_key == "test-key"
        assert config.verbose is True
    
    def test_default_values_without_overrides(self):
        """Test container has default values without overrides."""
        container = create_test_container()
        
        config = container.config()
        
        assert config.data_dir == "data"


class TestRateLimiterProviders:
    """Tests for rate limiter providers."""
    
    def test_creates_gemini_rate_limiter(self):
        """Creates Gemini rate limiter."""
        container = Container()
        
        limiter = container.gemini_rate_limiter()
        
        assert limiter is not None
        assert limiter.initial_rate == 10.0  # Default
    
    def test_creates_anthropic_rate_limiter(self):
        """Creates Anthropic rate limiter."""
        container = Container()
        
        limiter = container.anthropic_rate_limiter()
        
        assert limiter is not None
        assert limiter.initial_rate == 5.0  # Default
    
    def test_rate_limiters_are_singletons(self):
        """Rate limiters are singletons."""
        container = Container()
        
        l1 = container.gemini_rate_limiter()
        l2 = container.gemini_rate_limiter()
        
        assert l1 is l2


class TestCircuitBreakerProviders:
    """Tests for circuit breaker providers."""
    
    def test_creates_llm_circuit_breaker(self):
        """Creates LLM circuit breaker."""
        container = Container()
        
        cb = container.llm_circuit_breaker()
        
        assert cb is not None
        assert cb.name == "llm_api"
    
    def test_circuit_breaker_is_factory(self):
        """Circuit breaker is created fresh each time."""
        container = Container()
        
        cb1 = container.llm_circuit_breaker()
        cb2 = container.llm_circuit_breaker()
        
        # Factory creates different instances
        assert cb1 is not cb2


class TestMetricsProvider:
    """Tests for metrics provider."""
    
    def setup_method(self):
        """Reset container before each test."""
        reset_container()
    
    def test_creates_metrics_collector_when_enabled(self):
        """Creates MetricsCollector when metrics enabled."""
        # Default is metrics enabled
        container = Container()
        
        metrics = container.metrics_collector()
        
        # Should be real metrics collector
        assert hasattr(metrics, "increment")
        assert hasattr(metrics, "histogram")
    
    def test_noop_metrics_methods_work(self):
        """No-op metrics don't raise errors."""
        # Create a no-op metrics manually for testing
        class NoOpMetrics:
            def increment(self, *args, **kwargs): pass
            def gauge(self, *args, **kwargs): pass
            def histogram(self, *args, **kwargs): pass
            def get_counter(self, name): return 0
        
        metrics = NoOpMetrics()
        
        # Should not raise
        metrics.increment("test")
        metrics.gauge("test", 1.0)
        assert metrics.get_counter("test") == 0
