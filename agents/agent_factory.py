"""
Agent Factory with Dependency Injection.

Provides a clean way to create agents with all dependencies injected.
Supports both v1 (legacy) and v2 (enhanced) agents.
"""

from typing import Any, Dict, Optional, Type, Union
from dataclasses import dataclass

import structlog

from core.container import Container, get_container
from core.interfaces import LLMClientProtocol, RAGSearchProtocol, MetricsProtocol
from core.retry import CircuitBreaker
from core.rate_limiter import RateLimiter, AdaptiveRateLimiter
from agents.base_agent import BaseAgent, AgentContext
from agents.base_agent_v2 import EnhancedBaseAgent, AgentDependencies, AgentRole


logger = structlog.get_logger()


@dataclass
class AgentConfig:
    """Configuration for creating an agent."""
    
    name: str
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_retries: int = 3
    timeout_seconds: float = 120.0
    enable_caching: bool = True
    
    # Circuit breaker settings
    circuit_failure_threshold: int = 5
    circuit_timeout_seconds: float = 60.0


class AgentFactory:
    """
    Factory for creating agents with dependency injection.
    
    Usage:
        factory = AgentFactory()
        
        # Create v1 agent (legacy)
        writer = factory.create_v1("writer")
        
        # Create v2 agent (enhanced with DI)
        writer_v2 = factory.create_v2(WriterAgentV2, AgentConfig(name="writer"))
        
        # Create all agents
        agents = factory.create_all_v1()
    """
    
    def __init__(self, container: Optional[Container] = None):
        self.container = container or get_container()
        self.log = structlog.get_logger().bind(component="agent_factory")
        
        # Agent registry
        self._v1_agents: Dict[str, Type[BaseAgent]] = {}
        self._v2_agents: Dict[str, Type[EnhancedBaseAgent]] = {}
        
        # Load v1 agents
        self._register_v1_agents()
    
    def _register_v1_agents(self) -> None:
        """Register all v1 agents."""
        from agents import (
            ResearcherAgent,
            LiteratureScoutAgent,
            DataExtractorAgent,
            MetaAnalystAgent,
            GapIdentifierAgent,
            WriterAgent,
            SynthesizerAgent,
            AcademicEditorAgent,
            TerminologyGuardianAgent,
            CitationManagerAgent,
            VisualizerAgent,
            MultiEvaluatorAgent,
            FactCheckerAgent,
            ConsistencyCheckerAgent,
            BiasAuditorAgent,
            CriticAgent,
            MethodologyValidatorAgent,
        )
        
        self._v1_agents = {
            "researcher": ResearcherAgent,
            "literature_scout": LiteratureScoutAgent,
            "data_extractor": DataExtractorAgent,
            "meta_analyst": MetaAnalystAgent,
            "gap_identifier": GapIdentifierAgent,
            "writer": WriterAgent,
            "synthesizer": SynthesizerAgent,
            "academic_editor": AcademicEditorAgent,
            "terminology_guardian": TerminologyGuardianAgent,
            "citation_manager": CitationManagerAgent,
            "visualizer": VisualizerAgent,
            "multi_evaluator": MultiEvaluatorAgent,
            "fact_checker": FactCheckerAgent,
            "consistency_checker": ConsistencyCheckerAgent,
            "bias_auditor": BiasAuditorAgent,
            "critic": CriticAgent,
            "methodology_validator": MethodologyValidatorAgent,
        }
    
    def register_v2(self, name: str, agent_class: Type[EnhancedBaseAgent]) -> None:
        """Register a v2 agent class."""
        self._v2_agents[name] = agent_class
        self.log.debug("v2_agent_registered", name=name)
    
    def create_v1(self, name: str) -> BaseAgent:
        """
        Create a v1 (legacy) agent by name.
        
        Args:
            name: Agent name (e.g., "writer", "researcher")
        
        Returns:
            Instantiated agent
        """
        if name not in self._v1_agents:
            raise ValueError(f"Unknown v1 agent: {name}")
        
        agent = self._v1_agents[name]()
        self.log.debug("v1_agent_created", name=name)
        return agent
    
    def create_v2(
        self,
        agent_class: Type[EnhancedBaseAgent],
        config: AgentConfig
    ) -> EnhancedBaseAgent:
        """
        Create a v2 (enhanced) agent with full DI.
        
        Args:
            agent_class: The v2 agent class
            config: Agent configuration
        
        Returns:
            Instantiated agent with all dependencies
        """
        # Build dependencies from container
        deps = self._build_dependencies(config)
        
        # Create agent
        agent = agent_class(deps=deps)
        
        self.log.info(
            "v2_agent_created",
            name=config.name,
            model=config.model_name or "default"
        )
        
        return agent
    
    def _build_dependencies(self, config: AgentConfig) -> AgentDependencies:
        """Build AgentDependencies from container and config."""
        from agents.llm_client import GeminiClient
        
        # Get model config
        models_config = self.container.models_config()
        model_name = config.model_name or models_config.get_model_for_agent(config.name)
        temperature = config.temperature or models_config.get_temperature(config.name)
        
        # Create LLM client
        app_config = self.container.config()
        llm_client = GeminiClient(
            model=model_name,
            temperature=temperature,
            api_key=app_config.google_api_key
        )
        
        # Get rate limiter
        rate_limiter = self.container.gemini_rate_limiter()
        
        # Create circuit breaker
        circuit_breaker = CircuitBreaker(
            name=f"agent_{config.name}",
            failure_threshold=config.circuit_failure_threshold,
            timeout_seconds=config.circuit_timeout_seconds
        )
        
        # Get other dependencies
        state_manager = self.container.state_manager()
        metrics = self.container.metrics_collector()
        
        # RAG if available
        try:
            rag_search = self.container.hybrid_search()
        except Exception:
            rag_search = None
        
        return AgentDependencies(
            llm_client=llm_client,
            state_manager=state_manager,
            rag_search=rag_search,
            metrics=metrics,
            rate_limiter=rate_limiter,
            circuit_breaker=circuit_breaker,
            model_name=model_name,
            temperature=temperature,
            max_retries=config.max_retries,
            timeout_seconds=config.timeout_seconds,
            enable_caching=config.enable_caching,
            verbose=app_config.verbose,
        )
    
    def create_all_v1(self) -> list[BaseAgent]:
        """Create all v1 agents."""
        agents = []
        for name in self._v1_agents:
            agents.append(self.create_v1(name))
        self.log.info("all_v1_agents_created", count=len(agents))
        return agents
    
    def create_all_v2(self, configs: Optional[Dict[str, AgentConfig]] = None) -> list[EnhancedBaseAgent]:
        """Create all registered v2 agents."""
        agents = []
        
        for name, agent_class in self._v2_agents.items():
            config = configs.get(name) if configs else None
            if not config:
                config = AgentConfig(name=name)
            
            agents.append(self.create_v2(agent_class, config))
        
        self.log.info("all_v2_agents_created", count=len(agents))
        return agents


# Global factory instance
_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """Get the global agent factory."""
    global _factory
    if _factory is None:
        _factory = AgentFactory()
    return _factory


def create_agent(name: str, version: int = 1, **config_kwargs) -> Union[BaseAgent, EnhancedBaseAgent]:
    """
    Convenience function to create an agent.
    
    Args:
        name: Agent name
        version: 1 for legacy, 2 for enhanced
        **config_kwargs: Additional config options
    
    Returns:
        Agent instance
    """
    factory = get_agent_factory()
    
    if version == 1:
        return factory.create_v1(name)
    else:
        config = AgentConfig(name=name, **config_kwargs)
        if name in factory._v2_agents:
            return factory.create_v2(factory._v2_agents[name], config)
        
        raise ValueError(f"No v2 agent registered for: {name}")
