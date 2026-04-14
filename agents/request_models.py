"""
Pydantic request/response models for agent actions.

Provides strong typing and validation for all agent inputs.
This ensures invalid data is caught early with clear error messages.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional, Literal

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
)


# ============================================================================
# Base Models
# ============================================================================

class StrictModel(BaseModel):
    """Base model with strict validation."""
    
    model_config = ConfigDict(
        extra="forbid",  # Fail on unexpected fields
        validate_assignment=True,  # Validate on attribute assignment
        str_strip_whitespace=True,  # Strip whitespace from strings
    )


# ============================================================================
# Writer Agent Requests
# ============================================================================

class WriteSectionRequest(StrictModel):
    """Request to write a section of the article."""
    
    section_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique identifier for the section",
        examples=["introduction", "methods", "results"]
    )
    section_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable section name"
    )
    min_words: int = Field(
        ...,
        gt=0,
        lt=10000,
        description="Minimum word count for section"
    )
    max_words: int = Field(
        ...,
        gt=0,
        lt=20000,
        description="Maximum word count for section"
    )
    guidelines: str = Field(
        default="",
        max_length=5000,
        description="Content guidelines for the section"
    )
    avoid: str = Field(
        default="",
        max_length=2000,
        description="Content to avoid in the section"
    )
    research_context: Optional[str] = Field(
        default=None,
        max_length=50000,
        description="Research context from RAG"
    )
    
    @model_validator(mode="after")
    def validate_word_counts(self) -> "WriteSectionRequest":
        if self.max_words <= self.min_words:
            raise ValueError(
                f"max_words ({self.max_words}) must be greater than "
                f"min_words ({self.min_words})"
            )
        return self


class ReviseSectionRequest(StrictModel):
    """Request to revise an existing section."""
    
    section_id: str = Field(..., min_length=1, max_length=50)
    current_content: str = Field(..., min_length=1)
    feedback: str = Field(..., min_length=1, max_length=10000)
    improvement_focus: list[str] = Field(
        default_factory=list,
        description="Specific areas to focus improvements on"
    )
    preserve_citations: bool = Field(
        default=True,
        description="Whether to preserve existing citations"
    )


# ============================================================================
# Researcher Agent Requests
# ============================================================================

class ResearchQueryRequest(StrictModel):
    """Request to perform research on a topic."""
    
    query: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Research query to answer"
    )
    top_k: int = Field(
        default=15,
        ge=1,
        le=100,
        description="Number of documents to retrieve"
    )
    require_citations: bool = Field(
        default=True,
        description="Whether to require source citations"
    )
    min_confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for findings"
    )


class SynthesizeThemeRequest(StrictModel):
    """Request to synthesize research around a theme."""
    
    theme: str = Field(..., min_length=1, max_length=200)
    sources: list[dict] = Field(
        ...,
        min_length=1,
        description="Source documents to synthesize"
    )
    synthesis_approach: Literal["thematic", "narrative", "framework"] = Field(
        default="thematic"
    )
    
    @field_validator("sources")
    @classmethod
    def validate_sources(cls, v: list[dict]) -> list[dict]:
        for i, source in enumerate(v):
            if "content" not in source:
                raise ValueError(f"Source {i} missing 'content' field")
        return v


# ============================================================================
# Evaluator Agent Requests
# ============================================================================

class QualityCriterion(str, Enum):
    METHODOLOGY = "methodology"
    SYNTHESIS = "synthesis"
    PRESENTATION = "presentation"
    CONTRIBUTION = "contribution"


class EvaluateContentRequest(StrictModel):
    """Request to evaluate content quality."""
    
    content: str = Field(
        ...,
        min_length=100,
        description="Content to evaluate"
    )
    section: str = Field(..., min_length=1, max_length=50)
    criteria: list[QualityCriterion] = Field(
        default_factory=lambda: list(QualityCriterion),
        description="Criteria to evaluate"
    )
    iteration: Optional[int] = Field(
        default=None,
        ge=0,
        description="Current iteration number"
    )
    previous_score: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="Score from previous evaluation"
    )


class QuickCheckRequest(StrictModel):
    """Request for quick quality check."""
    
    content: str = Field(..., min_length=50)
    check_types: list[Literal["grammar", "citations", "structure"]] = Field(
        default=["grammar", "citations", "structure"]
    )


# ============================================================================
# Fact Checker Requests
# ============================================================================

class VerifyClaimRequest(StrictModel):
    """Request to verify a specific claim."""
    
    claim: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The claim to verify"
    )
    cited_source: Optional[str] = Field(
        default=None,
        description="Source cited for the claim"
    )
    context: Optional[str] = Field(
        default=None,
        max_length=5000,
        description="Surrounding context"
    )


class FactCheckSectionRequest(StrictModel):
    """Request to fact-check an entire section."""
    
    content: str = Field(..., min_length=100)
    section: str = Field(..., min_length=1, max_length=50)
    strictness: Literal["lenient", "standard", "strict"] = Field(
        default="standard"
    )


# ============================================================================
# Data Extractor Requests
# ============================================================================

class ExtractDataRequest(StrictModel):
    """Request to extract structured data from documents."""
    
    documents: list[dict] = Field(
        ...,
        min_length=1,
        description="Documents to extract data from"
    )
    extraction_schema: dict = Field(
        ...,
        description="Schema defining what to extract"
    )
    include_metadata: bool = Field(default=True)
    
    @field_validator("extraction_schema")
    @classmethod
    def validate_schema(cls, v: dict) -> dict:
        if "fields" not in v:
            raise ValueError("Schema must contain 'fields' key")
        return v


# ============================================================================
# Citation Manager Requests
# ============================================================================

class FormatCitationsRequest(StrictModel):
    """Request to format citations in text."""
    
    content: str = Field(..., min_length=1)
    style: Literal["APA7", "AMA", "Vancouver", "Harvard"] = Field(
        default="APA7"
    )
    bibliography: Optional[list[dict]] = Field(default=None)


class VerifyCitationsRequest(StrictModel):
    """Request to verify citations in text."""
    
    content: str = Field(..., min_length=100)
    available_sources: list[dict] = Field(default_factory=list)
    check_format: bool = Field(default=True)
    check_coverage: bool = Field(default=True)


# ============================================================================
# Consistency Checker Requests
# ============================================================================

class CheckConsistencyRequest(StrictModel):
    """Request to check for consistency issues."""
    
    content: str = Field(..., min_length=100)
    sections: Optional[list[str]] = Field(
        default=None,
        description="Specific sections to check"
    )
    check_types: list[Literal[
        "terminology",
        "numbers",
        "acronyms",
        "tense",
        "logical"
    ]] = Field(
        default=["terminology", "numbers", "acronyms"]
    )
    terminology_glossary: Optional[dict[str, str]] = Field(
        default=None,
        description="Glossary of correct terms"
    )


# ============================================================================
# Bias Auditor Requests
# ============================================================================

class BiasCategory(str, Enum):
    SELECTION = "selection"
    CONFIRMATION = "confirmation"
    PUBLICATION = "publication"
    CULTURAL = "cultural"
    LANGUAGE = "language"
    GENDER = "gender"
    TEMPORAL = "temporal"
    CITATION = "citation"


class AuditBiasRequest(StrictModel):
    """Request to audit content for bias."""
    
    content: str = Field(..., min_length=100)
    categories: list[BiasCategory] = Field(
        default_factory=lambda: list(BiasCategory)
    )
    context: Optional[str] = Field(default=None, max_length=5000)
    include_mitigation: bool = Field(default=True)


# ============================================================================
# Methodology Validator Requests
# ============================================================================

class ValidatePRISMARequest(StrictModel):
    """Request to validate PRISMA-ScR compliance."""
    
    article_content: str = Field(..., min_length=500)
    sections: dict[str, str] = Field(
        ...,
        description="Mapping of section names to content"
    )
    strict_mode: bool = Field(
        default=False,
        description="Whether to require all 22 items"
    )


# ============================================================================
# Visualizer Requests
# ============================================================================

class ChartType(str, Enum):
    PRISMA_FLOW = "prisma_flow"
    BAR = "bar"
    PIE = "pie"
    LINE = "line"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    FOREST_PLOT = "forest_plot"
    SANKEY = "sankey"


class GenerateChartRequest(StrictModel):
    """Request to generate a chart."""
    
    chart_type: ChartType
    data: dict = Field(..., description="Data for the chart")
    title: str = Field(default="", max_length=200)
    options: dict = Field(default_factory=dict)
    output_format: Literal["svg", "png", "pdf", "json"] = Field(
        default="svg"
    )


class GenerateTableRequest(StrictModel):
    """Request to generate a data table."""
    
    data: list[dict] = Field(..., min_length=1)
    columns: list[str] = Field(..., min_length=1)
    title: Optional[str] = Field(default=None, max_length=200)
    format: Literal["markdown", "latex", "html"] = Field(default="markdown")
    include_summary: bool = Field(default=False)
    
    @field_validator("data")
    @classmethod
    def validate_data_columns(cls, v: list[dict], info) -> list[dict]:
        # Validation happens after columns is set
        return v


# ============================================================================
# Response Models
# ============================================================================

class EvaluationResult(StrictModel):
    """Result of content evaluation."""
    
    overall_score: int = Field(..., ge=0, le=100)
    methodology: int = Field(..., ge=0, le=30)
    synthesis: int = Field(..., ge=0, le=30)
    presentation: int = Field(..., ge=0, le=20)
    contribution: int = Field(..., ge=0, le=20)
    verdict: Literal["accept", "minor_revision", "major_revision", "rework"]
    issues: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)


class FactCheckResult(StrictModel):
    """Result of fact checking."""
    
    verified: int = Field(..., ge=0)
    unverified: int = Field(..., ge=0)
    contradicted: int = Field(..., ge=0)
    claims: list[dict] = Field(default_factory=list)
    pass_rate: float = Field(..., ge=0.0, le=1.0)
    gate_passed: bool


class ConsistencyResult(StrictModel):
    """Result of consistency check."""
    
    score: float = Field(..., ge=0.0, le=1.0)
    issues: list[dict] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    gate_passed: bool


class BiasAuditResult(StrictModel):
    """Result of bias audit."""
    
    risk_level: Literal["low", "moderate", "high", "critical"]
    categories_flagged: list[str] = Field(default_factory=list)
    issues: list[dict] = Field(default_factory=list)
    mitigations: list[str] = Field(default_factory=list)
    gate_passed: bool


class PRISMAComplianceResult(StrictModel):
    """Result of PRISMA-ScR compliance check."""
    
    items_present: int = Field(..., ge=0, le=22)
    items_missing: list[str] = Field(default_factory=list)
    items_partial: list[str] = Field(default_factory=list)
    compliance_level: Literal["full", "high", "acceptable", "low"]
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# Request Model Registry
# ============================================================================

REQUEST_MODELS: dict[str, dict[str, type[StrictModel]]] = {
    "writer": {
        "write_section": WriteSectionRequest,
        "revise_section": ReviseSectionRequest,
    },
    "researcher": {
        "research": ResearchQueryRequest,
        "synthesize_theme": SynthesizeThemeRequest,
    },
    "multi_evaluator": {
        "evaluate": EvaluateContentRequest,
        "quick_check": QuickCheckRequest,
    },
    "fact_checker": {
        "verify_claim": VerifyClaimRequest,
        "fact_check_section": FactCheckSectionRequest,
    },
    "data_extractor": {
        "extract_data": ExtractDataRequest,
    },
    "citation_manager": {
        "format_citations": FormatCitationsRequest,
        "verify_citations": VerifyCitationsRequest,
    },
    "consistency_checker": {
        "check_consistency": CheckConsistencyRequest,
    },
    "bias_auditor": {
        "audit_bias": AuditBiasRequest,
    },
    "methodology_validator": {
        "validate_prisma": ValidatePRISMARequest,
    },
    "visualizer": {
        "generate_chart": GenerateChartRequest,
        "generate_table": GenerateTableRequest,
    },
}


def get_request_model(agent_name: str, action: str) -> Optional[type[StrictModel]]:
    """Get the request model for an agent action."""
    agent_models = REQUEST_MODELS.get(agent_name, {})
    return agent_models.get(action)
