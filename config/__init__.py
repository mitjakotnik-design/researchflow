"""Configuration module for Scoping Review Agents System."""

from .models_config import ModelsConfig, ModelSpec, ModelTier, ITERATION_MODEL_STRATEGY
from .quality_thresholds import (
    QualityThresholds,
    QualityGates,
    QualityVerdict,
    BiasRisk,
    ComplianceLevel,
    SaturationConfig,
)
from .state_manager import (
    StateManager,
    ArticleState,
    ArticlePhase,
    OrchestratorState,
    ResearchCache,
    QualitySnapshot,
)
from .sections_config import (
    SectionSpec,
    SectionState,
    SectionStatus,
    SectionsConfig,
    PRISMASection,
    REVIEW_SECTIONS,
)

__all__ = [
    # Models
    "ModelsConfig",
    "ModelSpec",
    "ModelTier",
    "ITERATION_MODEL_STRATEGY",
    # Quality
    "QualityThresholds",
    "QualityGates",
    "QualityVerdict",
    "BiasRisk",
    "ComplianceLevel",
    "SaturationConfig",
    # State
    "StateManager",
    "ArticleState",
    "ArticlePhase",
    "OrchestratorState",
    "ResearchCache",
    "QualitySnapshot",
    # Sections
    "SectionSpec",
    "SectionState",
    "SectionStatus",
    "SectionsConfig",
    "PRISMASection",
    "REVIEW_SECTIONS",
]
