"""Model configuration for different agent tiers."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import os


class ModelTier(Enum):
    """Model tiers based on capability and cost."""
    LITE = "lite"       # Simple, repetitive tasks
    FAST = "fast"       # Volume tasks, RAG queries
    PRO = "pro"         # Complex reasoning, writing
    PREMIUM = "premium" # Critical analysis, evaluation


@dataclass
class ModelSpec:
    """Specification for a model."""
    name: str
    provider: str
    cost_per_1m_input: float
    cost_per_1m_output: float
    max_tokens: int
    default_temperature: float
    supports_json_mode: bool = True
    supports_vision: bool = False


# Available Models
MODELS = {
    # Google Gemini Models
    "gemini-2.5-flash-lite": ModelSpec(
        name="gemini-2.5-flash-lite",
        provider="google",
        cost_per_1m_input=0.075,
        cost_per_1m_output=0.30,
        max_tokens=8192,
        default_temperature=0.0,
    ),
    "gemini-2.5-flash": ModelSpec(
        name="gemini-2.5-flash",
        provider="google",
        cost_per_1m_input=0.15,
        cost_per_1m_output=0.60,
        max_tokens=8192,
        default_temperature=0.0,
    ),
    "gemini-2.5-pro": ModelSpec(
        name="gemini-2.5-pro",
        provider="google",
        cost_per_1m_input=1.25,
        cost_per_1m_output=5.00,
        max_tokens=16384,
        default_temperature=0.3,
    ),
    "gemini-3.1-pro-preview": ModelSpec(
        name="gemini-3.1-pro-preview",
        provider="google",
        cost_per_1m_input=2.50,
        cost_per_1m_output=10.00,
        max_tokens=32768,
        default_temperature=0.1,
    ),
    # Anthropic Models
    "claude-opus-4.5": ModelSpec(
        name="claude-opus-4.5",
        provider="anthropic",
        cost_per_1m_input=15.00,
        cost_per_1m_output=75.00,
        max_tokens=16384,
        default_temperature=0.2,
        supports_vision=True,
    ),
    "claude-sonnet-4": ModelSpec(
        name="claude-sonnet-4",
        provider="anthropic",
        cost_per_1m_input=3.00,
        cost_per_1m_output=15.00,
        max_tokens=8192,
        default_temperature=0.3,
    ),
}


@dataclass
class ModelsConfig:
    """Configuration for model selection per agent type."""
    
    # Default model per tier
    tier_models: dict[ModelTier, str] = field(default_factory=lambda: {
        ModelTier.LITE: "gemini-2.5-flash-lite",
        ModelTier.FAST: "gemini-2.5-flash",
        ModelTier.PRO: "gemini-3.1-pro-preview",
        ModelTier.PREMIUM: "gemini-3.1-pro-preview",
    })
    
    # Agent-specific model overrides
    agent_models: dict[str, str] = field(default_factory=lambda: {
        # Research Cluster
        "researcher": "gemini-2.5-flash",
        "literature_scout": "gemini-2.5-flash",
        "data_extractor": "gemini-2.5-flash",
        "meta_analyst": "gemini-3.1-pro-preview",
        "gap_identifier": "gemini-3.1-pro-preview",
        
        # Writing Cluster
        "writer": "gemini-3.1-pro-preview",
        "synthesizer": "gemini-3.1-pro-preview",
        "academic_editor": "gemini-3.1-pro-preview",
        "terminology_guardian": "gemini-2.5-flash-lite",
        "citation_manager": "gemini-2.5-flash-lite",
        "visualizer": "gemini-3.1-pro-preview",
        
        # Quality Cluster
        "multi_evaluator": "gemini-3.1-pro-preview",
        "critic": "gemini-3.1-pro-preview",
        "fact_checker": "gemini-3.1-pro-preview",
        "bias_auditor": "gemini-3.1-pro-preview",
        "consistency_checker": "gemini-2.5-flash",
        "methodology_validator": "gemini-2.5-flash",
        
        # Orchestration
        "meta_orchestrator": "gemini-3.1-pro-preview",
    })
    
    # Temperature overrides per agent
    agent_temperatures: dict[str, float] = field(default_factory=lambda: {
        "researcher": 0.0,
        "data_extractor": 0.0,
        "fact_checker": 0.0,
        "consistency_checker": 0.0,
        "terminology_guardian": 0.0,
        "citation_manager": 0.0,
        "methodology_validator": 0.0,
        "writer": 0.7,
        "synthesizer": 0.5,
        "gap_identifier": 0.5,
        "visualizer": 0.5,
        "academic_editor": 0.4,
        "meta_analyst": 0.3,
        "critic": 0.3,
        "meta_orchestrator": 0.2,
        "multi_evaluator": 0.1,
        "bias_auditor": 0.1,
    })
    
    def get_model_for_agent(self, agent_name: str) -> ModelSpec:
        """Get the model specification for a given agent."""
        model_name = self.agent_models.get(agent_name)
        if not model_name:
            raise ValueError(f"Unknown agent: {agent_name}")
        return MODELS[model_name]
    
    def get_temperature_for_agent(self, agent_name: str) -> float:
        """Get the temperature setting for a given agent."""
        return self.agent_temperatures.get(
            agent_name, 
            MODELS[self.agent_models[agent_name]].default_temperature
        )
    
    def get_model_for_tier(self, tier: ModelTier) -> ModelSpec:
        """Get the default model for a tier."""
        model_name = self.tier_models[tier]
        return MODELS[model_name]
    
    def estimate_cost(
        self, 
        agent_name: str, 
        input_tokens: int, 
        output_tokens: int
    ) -> float:
        """Estimate the cost for an agent call."""
        model = self.get_model_for_agent(agent_name)
        input_cost = (input_tokens / 1_000_000) * model.cost_per_1m_input
        output_cost = (output_tokens / 1_000_000) * model.cost_per_1m_output
        return input_cost + output_cost


# Iteration-based model escalation strategy
ITERATION_MODEL_STRATEGY = {
    1: {
        "writer": "gemini-2.5-pro",
        "evaluator": "gemini-2.5-pro",
    },
    2: {
        "writer": "gemini-2.5-pro",
        "evaluator": "gemini-2.5-pro",  # Stricter evaluation
    },
    3: {
        "writer": "gemini-2.5-pro",
        "evaluator": "gemini-2.5-pro",
    },
    4: {
        "writer": "gemini-2.5-pro",  # Premium for difficult fixes
        "evaluator": "gemini-2.5-pro",
    },
    5: {
        "writer": "gemini-2.5-pro",
        "evaluator": "gemini-2.5-pro",
    },
}
