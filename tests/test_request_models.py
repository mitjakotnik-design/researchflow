"""
Unit tests for Pydantic request models.

Tests for:
- Field validation
- Cross-field validation
- Custom validators
- Request model registry
"""

import pytest
from pydantic import ValidationError

from agents.request_models import (
    # Writer
    WriteSectionRequest,
    ReviseSectionRequest,
    # Researcher
    ResearchQueryRequest,
    SynthesizeThemeRequest,
    # Evaluator
    EvaluateContentRequest,
    QuickCheckRequest,
    QualityCriterion,
    # Fact Checker
    VerifyClaimRequest,
    FactCheckSectionRequest,
    # Data Extractor
    ExtractDataRequest,
    # Citation Manager
    FormatCitationsRequest,
    VerifyCitationsRequest,
    # Consistency
    CheckConsistencyRequest,
    # Bias
    AuditBiasRequest,
    BiasCategory,
    # Methodology
    ValidatePRISMARequest,
    # Visualizer
    GenerateChartRequest,
    GenerateTableRequest,
    ChartType,
    # Registry
    get_request_model,
    REQUEST_MODELS,
)


# ============================================================================
# Writer Request Tests
# ============================================================================

class TestWriteSectionRequest:
    """Tests for WriteSectionRequest validation."""
    
    def test_valid_request(self):
        """Valid request passes validation."""
        req = WriteSectionRequest(
            section_id="introduction",
            section_name="Introduction",
            min_words=500,
            max_words=1000,
            guidelines="Be clear and concise",
            avoid="Jargon"
        )
        
        assert req.section_id == "introduction"
        assert req.min_words == 500
    
    def test_max_words_must_exceed_min_words(self):
        """max_words must be greater than min_words."""
        with pytest.raises(ValidationError) as exc_info:
            WriteSectionRequest(
                section_id="intro",
                section_name="Introduction",
                min_words=1000,
                max_words=500  # Invalid: less than min
            )
        
        assert "max_words" in str(exc_info.value)
    
    def test_section_id_required(self):
        """section_id is required."""
        with pytest.raises(ValidationError):
            WriteSectionRequest(
                section_name="Introduction",
                min_words=500,
                max_words=1000
            )
    
    def test_section_id_cannot_be_empty(self):
        """section_id cannot be empty string."""
        with pytest.raises(ValidationError):
            WriteSectionRequest(
                section_id="",
                section_name="Introduction",
                min_words=500,
                max_words=1000
            )
    
    def test_min_words_must_be_positive(self):
        """min_words must be positive."""
        with pytest.raises(ValidationError):
            WriteSectionRequest(
                section_id="intro",
                section_name="Introduction",
                min_words=-100,
                max_words=1000
            )
    
    def test_whitespace_stripped(self):
        """Whitespace is stripped from strings."""
        req = WriteSectionRequest(
            section_id="  introduction  ",
            section_name="  Introduction  ",
            min_words=500,
            max_words=1000
        )
        
        assert req.section_id == "introduction"
        assert req.section_name == "Introduction"


class TestReviseSectionRequest:
    """Tests for ReviseSectionRequest validation."""
    
    def test_valid_request(self):
        """Valid revision request passes."""
        req = ReviseSectionRequest(
            section_id="methods",
            current_content="Current content here...",
            feedback="Add more detail about sampling"
        )
        
        assert req.section_id == "methods"
        assert req.preserve_citations is True  # Default
    
    def test_feedback_required(self):
        """Feedback is required."""
        with pytest.raises(ValidationError):
            ReviseSectionRequest(
                section_id="methods",
                current_content="Content"
            )


# ============================================================================
# Researcher Request Tests
# ============================================================================

class TestResearchQueryRequest:
    """Tests for ResearchQueryRequest validation."""
    
    def test_valid_request(self):
        """Valid research query passes."""
        req = ResearchQueryRequest(
            query="What are the effects of AI on HR practices?",
            top_k=20
        )
        
        assert req.top_k == 20
        assert req.require_citations is True
    
    def test_query_minimum_length(self):
        """Query must meet minimum length."""
        with pytest.raises(ValidationError):
            ResearchQueryRequest(query="AI")  # Too short
    
    def test_top_k_bounds(self):
        """top_k must be within bounds."""
        with pytest.raises(ValidationError):
            ResearchQueryRequest(
                query="Valid query here",
                top_k=200  # Exceeds max of 100
            )
    
    def test_confidence_threshold_bounds(self):
        """Confidence must be between 0 and 1."""
        with pytest.raises(ValidationError):
            ResearchQueryRequest(
                query="Valid query",
                min_confidence=1.5  # Invalid
            )


class TestSynthesizeThemeRequest:
    """Tests for SynthesizeThemeRequest validation."""
    
    def test_valid_request(self):
        """Valid synthesis request passes."""
        req = SynthesizeThemeRequest(
            theme="Technostress in remote work",
            sources=[
                {"content": "Study 1 findings..."},
                {"content": "Study 2 findings..."}
            ]
        )
        
        assert req.synthesis_approach == "thematic"
    
    def test_sources_must_have_content(self):
        """Each source must have content field."""
        with pytest.raises(ValidationError) as exc_info:
            SynthesizeThemeRequest(
                theme="Test theme",
                sources=[
                    {"title": "Missing content field"}
                ]
            )
        
        assert "content" in str(exc_info.value)
    
    def test_sources_required(self):
        """At least one source required."""
        with pytest.raises(ValidationError):
            SynthesizeThemeRequest(
                theme="Test theme",
                sources=[]
            )


# ============================================================================
# Evaluator Request Tests
# ============================================================================

class TestEvaluateContentRequest:
    """Tests for EvaluateContentRequest validation."""
    
    def test_valid_request(self):
        """Valid evaluation request passes."""
        req = EvaluateContentRequest(
            content="A" * 200,  # Meet minimum length
            section="methods",
            criteria=[QualityCriterion.METHODOLOGY]
        )
        
        assert len(req.criteria) == 1
    
    def test_content_minimum_length(self):
        """Content must meet minimum length."""
        with pytest.raises(ValidationError):
            EvaluateContentRequest(
                content="Too short",
                section="methods"
            )
    
    def test_default_criteria(self):
        """Default criteria includes all."""
        req = EvaluateContentRequest(
            content="A" * 200,
            section="methods"
        )
        
        assert len(req.criteria) == 4
    
    def test_previous_score_bounds(self):
        """Previous score must be 0-100."""
        with pytest.raises(ValidationError):
            EvaluateContentRequest(
                content="A" * 200,
                section="methods",
                previous_score=150  # Invalid
            )


# ============================================================================
# Data Extractor Request Tests
# ============================================================================

class TestExtractDataRequest:
    """Tests for ExtractDataRequest validation."""
    
    def test_valid_request(self):
        """Valid extraction request passes."""
        req = ExtractDataRequest(
            documents=[{"content": "Doc 1"}],
            extraction_schema={"fields": ["author", "year"]}
        )
        
        assert req.include_metadata is True
    
    def test_schema_must_have_fields(self):
        """Schema must contain fields key."""
        with pytest.raises(ValidationError):
            ExtractDataRequest(
                documents=[{"content": "Doc 1"}],
                extraction_schema={"columns": ["a"]}  # Wrong key
            )


# ============================================================================
# Citation Manager Request Tests
# ============================================================================

class TestFormatCitationsRequest:
    """Tests for FormatCitationsRequest validation."""
    
    def test_valid_request(self):
        """Valid citation format request passes."""
        req = FormatCitationsRequest(
            content="Text with (Author, 2023) citation.",
            style="APA7"
        )
        
        assert req.style == "APA7"
    
    def test_valid_styles(self):
        """Only valid citation styles accepted."""
        for style in ["APA7", "AMA", "Vancouver", "Harvard"]:
            req = FormatCitationsRequest(content="Text", style=style)
            assert req.style == style
        
        with pytest.raises(ValidationError):
            FormatCitationsRequest(content="Text", style="MLA")  # Invalid


# ============================================================================
# Bias Auditor Request Tests
# ============================================================================

class TestAuditBiasRequest:
    """Tests for AuditBiasRequest validation."""
    
    def test_valid_request(self):
        """Valid bias audit request passes."""
        req = AuditBiasRequest(
            content="A" * 200,
            categories=[BiasCategory.SELECTION, BiasCategory.PUBLICATION]
        )
        
        assert len(req.categories) == 2
    
    def test_default_categories(self):
        """Default includes all bias categories."""
        req = AuditBiasRequest(content="A" * 200)
        
        assert len(req.categories) == len(BiasCategory)


# ============================================================================
# PRISMA Validation Request Tests
# ============================================================================

class TestValidatePRISMARequest:
    """Tests for ValidatePRISMARequest validation."""
    
    def test_valid_request(self):
        """Valid PRISMA validation request passes."""
        req = ValidatePRISMARequest(
            article_content="A" * 1000,
            sections={
                "introduction": "Intro content...",
                "methods": "Methods content..."
            }
        )
        
        assert req.strict_mode is False
    
    def test_article_content_minimum(self):
        """Article content must meet minimum length."""
        with pytest.raises(ValidationError):
            ValidatePRISMARequest(
                article_content="Too short",
                sections={"intro": "Content"}
            )


# ============================================================================
# Visualizer Request Tests
# ============================================================================

class TestGenerateChartRequest:
    """Tests for GenerateChartRequest validation."""
    
    def test_valid_request(self):
        """Valid chart request passes."""
        req = GenerateChartRequest(
            chart_type=ChartType.BAR,
            data={"labels": ["A", "B"], "values": [1, 2]},
            title="Test Chart"
        )
        
        assert req.output_format == "svg"
    
    def test_chart_types(self):
        """All chart types are valid."""
        for chart_type in ChartType:
            req = GenerateChartRequest(
                chart_type=chart_type,
                data={}
            )
            assert req.chart_type == chart_type


class TestGenerateTableRequest:
    """Tests for GenerateTableRequest validation."""
    
    def test_valid_request(self):
        """Valid table request passes."""
        req = GenerateTableRequest(
            data=[{"col1": "a", "col2": "b"}],
            columns=["col1", "col2"]
        )
        
        assert req.format == "markdown"
    
    def test_data_required(self):
        """Data cannot be empty."""
        with pytest.raises(ValidationError):
            GenerateTableRequest(
                data=[],
                columns=["col1"]
            )
    
    def test_columns_required(self):
        """Columns cannot be empty."""
        with pytest.raises(ValidationError):
            GenerateTableRequest(
                data=[{"col1": "a"}],
                columns=[]
            )


# ============================================================================
# Request Model Registry Tests
# ============================================================================

class TestRequestModelRegistry:
    """Tests for request model registry."""
    
    def test_get_existing_model(self):
        """get_request_model returns model for known agent/action."""
        model = get_request_model("writer", "write_section")
        assert model is WriteSectionRequest
    
    def test_get_nonexistent_model(self):
        """get_request_model returns None for unknown agent/action."""
        model = get_request_model("unknown_agent", "unknown_action")
        assert model is None
    
    def test_registry_contains_all_agents(self):
        """Registry contains models for main agents."""
        expected_agents = [
            "writer",
            "researcher",
            "multi_evaluator",
            "fact_checker",
            "data_extractor",
            "citation_manager",
            "consistency_checker",
            "bias_auditor",
            "methodology_validator",
            "visualizer",
        ]
        
        for agent in expected_agents:
            assert agent in REQUEST_MODELS


# ============================================================================
# Extra Fields Rejection Tests
# ============================================================================

class TestStrictValidation:
    """Tests that extra fields are rejected."""
    
    def test_rejects_extra_fields(self):
        """Extra fields cause validation error."""
        with pytest.raises(ValidationError) as exc_info:
            WriteSectionRequest(
                section_id="intro",
                section_name="Introduction",
                min_words=500,
                max_words=1000,
                unknown_field="should fail"  # Extra field
            )
        
        assert "extra" in str(exc_info.value).lower()
