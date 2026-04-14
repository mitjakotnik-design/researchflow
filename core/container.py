"""
Dependency Injection Container.

Centralizes all dependency creation and wiring.
Uses the dependency-injector library for a clean, testable architecture.
"""

import os
from typing import Optional

from dependency_injector import containers, providers
import structlog

from config import (
    ModelsConfig,
    QualityThresholds,
    QualityGates,
    SaturationConfig,
    StateManager,
)
from core.rate_limiter import (
    TokenBucketRateLimiter,
    PerKeyRateLimiter,
    AdaptiveRateLimiter,
)
from core.retry import CircuitBreaker


logger = structlog.get_logger()


# ============================================================================
# Application Configuration
# ============================================================================

class Config:
    """Application configuration loaded from environment."""
    
    def __init__(self):
        # API Keys
        self.google_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.cohere_api_key = os.getenv("COHERE_API_KEY", "")
        
        # Vertex AI settings (uses Application Default Credentials)
        self.use_vertex_ai = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
        self.gcp_project = os.getenv("GCP_PROJECT", "")
        self.gcp_location = os.getenv("GCP_LOCATION", "us-central1")
        
        # Paths
        self.data_dir = os.getenv("DATA_DIR", "data")
        self.chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
        self.prompts_dir = os.getenv("PROMPTS_DIR", "prompts")
        
        # RAG settings
        self.chroma_collection = os.getenv("CHROMA_COLLECTION", "scoping_review")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "models/embedding-001")
        
        # Rate limits (per second)
        self.gemini_rate_limit = float(os.getenv("GEMINI_RATE_LIMIT", "10"))
        self.anthropic_rate_limit = float(os.getenv("ANTHROPIC_RATE_LIMIT", "5"))
        self.cohere_rate_limit = float(os.getenv("COHERE_RATE_LIMIT", "10"))
        
        # Circuit breaker settings
        self.circuit_failure_threshold = int(os.getenv("CIRCUIT_FAILURE_THRESHOLD", "5"))
        self.circuit_timeout_seconds = float(os.getenv("CIRCUIT_TIMEOUT_SECONDS", "60"))
        
        # Feature flags
        self.enable_caching = os.getenv("ENABLE_CACHING", "true").lower() == "true"
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.verbose = os.getenv("VERBOSE", "false").lower() == "true"


# ============================================================================
# Dependency Injection Container
# ============================================================================

class Container(containers.DeclarativeContainer):
    """
    Main DI container for the application.
    
    Usage:
        container = Container()
        container.config.from_dict({...})  # Optional config override
        
        # Get singletons
        state_manager = container.state_manager()
        
        # Get factories
        writer_agent = container.writer_agent()
    """
    
    # -------------------------------------------------------------------------
    # Configuration
    # -------------------------------------------------------------------------
    
    config = providers.Singleton(Config)
    
    models_config = providers.Singleton(ModelsConfig)
    
    quality_thresholds = providers.Singleton(QualityThresholds)
    
    quality_gates = providers.Singleton(QualityGates)
    
    saturation_config = providers.Factory(
        SaturationConfig,
        target_score=85,
        minimum_acceptable=75,
        max_iterations=5,
    )
    
    # -------------------------------------------------------------------------
    # Rate Limiters
    # -------------------------------------------------------------------------
    
    gemini_rate_limiter = providers.Singleton(
        AdaptiveRateLimiter,
        initial_rate=providers.Callable(
            lambda c: c.gemini_rate_limit,
            config,
        ),
        min_rate=1.0,
        max_rate=30.0,
    )
    
    anthropic_rate_limiter = providers.Singleton(
        AdaptiveRateLimiter,
        initial_rate=providers.Callable(
            lambda c: c.anthropic_rate_limit,
            config,
        ),
        min_rate=0.5,
        max_rate=20.0,
    )
    
    api_rate_limiters = providers.Singleton(
        PerKeyRateLimiter,
        rate=5.0,
        capacity=10,
    )
    
    # -------------------------------------------------------------------------
    # Circuit Breakers
    # -------------------------------------------------------------------------
    
    llm_circuit_breaker = providers.Factory(
        CircuitBreaker,
        name="llm_api",
        failure_threshold=providers.Callable(
            lambda c: c.circuit_failure_threshold,
            config,
        ),
        timeout_seconds=providers.Callable(
            lambda c: c.circuit_timeout_seconds,
            config,
        ),
    )
    
    rag_circuit_breaker = providers.Factory(
        CircuitBreaker,
        name="rag_search",
        failure_threshold=3,
        timeout_seconds=30.0,
    )
    
    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------
    
    state_manager = providers.Singleton(
        StateManager,
        data_dir=providers.Callable(
            lambda c: c.data_dir,
            config,
        ),
    )
    
    # -------------------------------------------------------------------------
    # LLM Clients (Factories - new instance each time)
    # -------------------------------------------------------------------------
    
    @providers.Factory
    def gemini_client(
        config: Config = providers.Callable(lambda: Container.config()),
        rate_limiter: AdaptiveRateLimiter = providers.Callable(
            lambda: Container.gemini_rate_limiter()
        ),
    ):
        """Create a new Gemini client with rate limiting."""
        from agents.llm_client import GeminiClient
        
        return GeminiClient(
            model="gemini-2.5-flash",
            api_key=config.google_api_key,
        )
    
    @providers.Factory
    def anthropic_client(
        config: Config = providers.Callable(lambda: Container.config()),
        rate_limiter: AdaptiveRateLimiter = providers.Callable(
            lambda: Container.anthropic_rate_limiter()
        ),
    ):
        """Create a new Anthropic client with rate limiting."""
        from agents.llm_client import AnthropicClient
        
        return AnthropicClient(
            model="claude-sonnet-4-20250514",
            api_key=config.anthropic_api_key,
        )
    
    # -------------------------------------------------------------------------
    # RAG Components (Singletons)
    # -------------------------------------------------------------------------
    
    @providers.Singleton
    def hybrid_search(config: Config = providers.Callable(lambda: Container.config())):
        """Create hybrid search singleton."""
        from rag import HybridSearch
        
        return HybridSearch(
            collection_name=config.chroma_collection,
            persist_directory=config.chroma_persist_dir,
            embedding_model=config.embedding_model,
        )
    
    @providers.Singleton
    def reranker(config: Config = providers.Callable(lambda: Container.config())):
        """Create reranker singleton."""
        from rag import CohereReranker, NoOpReranker
        
        if config.cohere_api_key:
            return CohereReranker(api_key=config.cohere_api_key)
        return NoOpReranker()
    
    @providers.Singleton
    def query_decomposer():
        """Create query decomposer singleton."""
        from rag import QueryDecomposer
        
        return QueryDecomposer()
    
    # -------------------------------------------------------------------------
    # Observability
    # -------------------------------------------------------------------------
    
    @providers.Singleton
    def metrics_collector():
        """Create metrics collector."""
        from observability import MetricsCollector
        
        # Get config from container
        config = Container.config()
        
        if config.enable_metrics:
            return MetricsCollector()
        
        # Return a no-op metrics collector
        class NoOpMetrics:
            def increment(self, *args, **kwargs): pass
            def gauge(self, *args, **kwargs): pass
            def histogram(self, *args, **kwargs): pass
            def get_counter(self, name): return 0
        
        return NoOpMetrics()
    
    @providers.Singleton
    def logger():
        """Get configured logger."""
        return structlog.get_logger()


# ============================================================================
# Container Access
# ============================================================================

_container: Optional[Container] = None


def get_container() -> Container:
    """
    Get the global container instance.
    
    Creates a new container on first access.
    Use wire() to inject dependencies into modules.
    """
    global _container
    
    if _container is None:
        _container = Container()
        logger.info("di_container_initialized")
    
    return _container


def reset_container() -> None:
    """Reset the container (useful for testing)."""
    global _container
    _container = None


def wire_modules(modules: list[str]) -> None:
    """
    Wire container to modules for automatic injection.
    
    Example:
        wire_modules(["agents", "orchestration"])
    """
    container = get_container()
    container.wire(modules=modules)
    logger.info("di_container_wired", modules=modules)


# ============================================================================
# Testing Support
# ============================================================================

def create_test_container(**overrides) -> Container:
    """
    Create a test container with mock dependencies.
    
    Example:
        container = create_test_container(
            google_api_key="test-key",
            gemini_rate_limit=100.0,  # No rate limiting in tests
        )
    """
    container = Container()
    
    # Override config values
    config = Config()
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    container.config.override(providers.Object(config))
    
    return container
