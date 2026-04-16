"""Agents module."""

from .base_agent import BaseAgent, AgentResult, AgentContext, AgentRole
from .base_agent_v2 import EnhancedBaseAgent, AgentDependencies
from .llm_client import LLMClientFactory, GeminiClient, AnthropicClient, LLMResponse
from .request_models import (
    WriteSectionRequest,
    ReviseSectionRequest,
    ResearchQueryRequest,
    EvaluateContentRequest,
    FactCheckSectionRequest,
    AuditBiasRequest,
    ValidatePRISMARequest,
    get_request_model,
    REQUEST_MODELS,
)
from .agent_factory import AgentFactory, AgentConfig, get_agent_factory, create_agent

# Research agents (v1)
from .researcher import ResearcherAgent
from .literature_scout import LiteratureScoutAgent
from .data_extractor import DataExtractorAgent
from .meta_analyst import MetaAnalystAgent
from .gap_identifier import GapIdentifierAgent

# Writing agents (v1)
from .writer import WriterAgent
from .synthesizer import SynthesizerAgent
from .academic_editor import AcademicEditorAgent
from .terminology_guardian import TerminologyGuardianAgent
from .citation_manager import CitationManagerAgent
from .visualizer import VisualizerAgent

# Quality agents (v1)
from .multi_evaluator import MultiEvaluatorAgent
from .fact_checker import FactCheckerAgent
from .consistency_checker import ConsistencyCheckerAgent
from .bias_auditor import BiasAuditorAgent
from .critic import CriticAgent
from .methodology_validator import MethodologyValidatorAgent

# V2 Enhanced Agents
from .writer_v2 import WriterAgentV2
from .researcher_v2 import ResearcherAgentV2
from .multi_evaluator_v2 import MultiEvaluatorAgentV2
from .fact_checker_v2 import FactCheckerAgentV2

# Skill Loader
from .skill_loader import (
    SkillLoader,
    SkillMetadata,
    get_skill,
    get_system_prompt,
    list_all_skills,
    load_config,
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentResult",
    "AgentContext",
    "AgentRole",
    # Enhanced Base (v2)
    "EnhancedBaseAgent",
    "AgentDependencies",
    # Factory
    "AgentFactory",
    "AgentConfig",
    "get_agent_factory",
    "create_agent",
    # LLM
    "LLMClientFactory",
    "GeminiClient",
    "AnthropicClient",
    "LLMResponse",
    # Request Models
    "WriteSectionRequest",
    "ReviseSectionRequest",
    "ResearchQueryRequest",
    "EvaluateContentRequest",
    "FactCheckSectionRequest",
    "AuditBiasRequest",
    "ValidatePRISMARequest",
    "get_request_model",
    "REQUEST_MODELS",
    # Research (v1)
    "ResearcherAgent",
    "LiteratureScoutAgent",
    "DataExtractorAgent",
    "MetaAnalystAgent",
    "GapIdentifierAgent",
    # Writing (v1)
    "WriterAgent",
    "SynthesizerAgent",
    "AcademicEditorAgent",
    "TerminologyGuardianAgent",
    "CitationManagerAgent",
    "VisualizerAgent",
    # Quality (v1)
    "MultiEvaluatorAgent",
    "FactCheckerAgent",
    "ConsistencyCheckerAgent",
    "BiasAuditorAgent",
    "CriticAgent",
    "MethodologyValidatorAgent",
    # V2 Enhanced Agents
    "WriterAgentV2",
    "ResearcherAgentV2",
    "MultiEvaluatorAgentV2",
    "FactCheckerAgentV2",
    # Skill Loader
    "SkillLoader",
    "SkillMetadata",
    "get_skill",
    "get_system_prompt",
    "list_all_skills",
    "load_config",
]

