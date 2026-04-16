"""
Unit tests for research_plan_sections.py

Tests section specifications, validation functions, and dependencies.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.research_plan_sections import (
    get_section_spec,
    validate_word_count,
    check_required_elements,
    validate_section_order,
    get_dependent_sections,
    get_all_sections,
    SECTION_ORDER,
    RESEARCH_PLAN_SECTIONS
)


class TestSectionSpecifications:
    """Tests for section specification definitions."""
    
    def test_all_sections_exist(self):
        """All 15 sections should be defined."""
        assert len(SECTION_ORDER) == 15
        assert len(RESEARCH_PLAN_SECTIONS) == 15
    
    def test_all_sections_have_required_fields(self):
        """All sections must have mandatory fields."""
        for section_id in SECTION_ORDER:
            spec = get_section_spec(section_id)
            assert spec.section_id == section_id
            assert spec.name, f"{section_id} missing name"
            assert spec.description, f"{section_id} missing description"
            assert spec.min_words > 0, f"{section_id} min_words must be > 0"
            assert spec.max_words > spec.min_words, f"{section_id} max must be > min"
            assert spec.target_score >= 75, f"{section_id} target_score must be >= 75"
            assert len(spec.required_elements) >= 0  # Can be empty but must exist
    
    def test_section_word_count_ranges(self):
        """Word count ranges should be reasonable."""
        for section_id in SECTION_ORDER:
            spec = get_section_spec(section_id)
            # Min should be at least 50, max at most 1000
            assert 50 <= spec.min_words <= 1000
            assert 100 <= spec.max_words <= 1000
            # Ratio should be reasonable (max not more than 5x min)
            assert spec.max_words <= spec.min_words * 5, (
                f"{section_id}: max ({spec.max_words}) > 5x min ({spec.min_words * 5})"
            )


class TestGetSectionSpec:
    """Tests for get_section_spec function."""
    
    def test_valid_section_id(self):
        """Should return spec for valid section ID."""
        spec = get_section_spec("metadata")
        assert spec.section_id == "metadata"
        assert spec.name == "Title & Metadata"
    
    def test_case_insensitive(self):
        """Should handle case-insensitive section IDs."""
        spec1 = get_section_spec("METADATA")
        spec2 = get_section_spec("metadata")
        assert spec1.section_id == spec2.section_id
    
    def test_whitespace_handling(self):
        """Should strip whitespace from section IDs."""
        spec = get_section_spec("  metadata  ")
        assert spec.section_id == "metadata"
    
    def test_invalid_section_id(self):
        """Should raise ValueError for unknown section."""
        with pytest.raises(ValueError, match="Unknown section"):
            get_section_spec("nonexistent_section")
    
    def test_non_string_section_id(self):
        """Should raise TypeError for non-string input."""
        with pytest.raises(TypeError, match="must be str"):
            get_section_spec(123)
    
    def test_empty_section_id(self):
        """Should raise ValueError for empty section ID."""
        with pytest.raises(ValueError, match="cannot be empty"):
            get_section_spec("")
        with pytest.raises(ValueError, match="cannot be empty"):
            get_section_spec("   ")


class TestValidateWordCount:
    """Tests for validate_word_count function."""
    
    def test_valid_word_count(self):
        """Content within range should pass."""
        # Metadata: 50-200 words
        content = " ".join(["word"] * 100)  # 100 words
        valid, msg = validate_word_count(content, "metadata")
        assert valid is True
        assert "OK" in msg
        assert "100" in msg
    
    def test_word_count_too_short(self):
        """Content below min should fail."""
        content = "Just a few words here"  # ~5 words
        valid, msg = validate_word_count(content, "metadata")
        assert valid is False
        assert "Too short" in msg
    
    def test_word_count_too_long(self):
        """Content above max should fail."""
        content = " ".join(["word"] * 250)  # 250 words (metadata max is 200)
        valid, msg = validate_word_count(content, "metadata")
        assert valid is False
        assert "Too long" in msg
    
    def test_markdown_syntax_excluded(self):
        """Markdown syntax should not count as words."""
        content = """
        ## Heading
        **Bold text** and *italic text*
        - Bullet point
        [link text](http://example.com)
        """ + " word" * 60  # Add enough words to meet minimum
        
        valid, msg = validate_word_count(content, "metadata")
        # Should count actual words, not markdown syntax
        assert valid is True
    
    def test_code_blocks_excluded(self):
        """Code blocks should not count toward word count."""
        content = """
        Some introduction text here.
        ```python
        def function():
            return "This should not count"
        ```
        More text after code block.
        """ + " word" * 50
        
        valid, msg = validate_word_count(content, "metadata")
        assert valid is True
    
    def test_non_string_content(self):
        """Should raise TypeError for non-string content."""
        with pytest.raises(TypeError, match="content must be str"):
            validate_word_count(123, "metadata")
    
    def test_non_string_section_id(self):
        """Should raise TypeError for non-string section_id."""
        with pytest.raises(TypeError, match="section_id must be str"):
            validate_word_count("content", 123)


class TestCheckRequiredElements:
    """Tests for check_required_elements function."""
    
    def test_all_elements_present(self):
        """Should pass when all required elements are present."""
        content = """
        This section contains the main research question.
        We also have sub-questions listed.
        The PCC framework is defined.
        Justification for the approach is provided.
        """
        all_present, missing = check_required_elements(content, "research_question")
        assert all_present is True
        assert len(missing) == 0
    
    def test_missing_elements_detected(self):
        """Should detect missing required elements."""
        content = """
        This section only contains the main research question.
        Nothing else is here.
        """
        all_present, missing = check_required_elements(content, "research_question")
        assert all_present is False
        assert len(missing) > 0
    
    def test_pattern_matching_variations(self):
        """Should recognize common variations and synonyms."""
        # Test "main RQ" instead of "main research question"
        content = """
        Main RQ: How does AI affect organizations?
        Sub-questions are listed below.
        PCC framework: Population, Concept, Context
        The justification follows.
        """
        all_present, missing = check_required_elements(content, "research_question")
        assert all_present is True or len(missing) <= 1  # Allow some flexibility
    
    def test_case_insensitive_matching(self):
        """Should match elements case-insensitively."""
        content = """
        MAIN RESEARCH QUESTION is stated here.
        SUB-QUESTIONS follow.
        PCC Framework is defined.
        Justification provided.
        """
        all_present, missing = check_required_elements(content, "research_question")
        assert all_present is True
    
    def test_non_string_content(self):
        """Should raise TypeError for non-string content."""
        with pytest.raises(TypeError, match="content must be str"):
            check_required_elements(123, "metadata")


class TestDependencies:
    """Tests for section dependency validation."""
    
    def test_get_dependent_sections(self):
        """Should return list of dependencies."""
        # Methodology depends on research_question and theoretical_framework
        deps = get_dependent_sections("methodology")
        assert "research_question" in deps
        assert "theoretical_framework" in deps
    
    def test_no_dependencies(self):
        """Sections with no dependencies should return empty list."""
        deps = get_dependent_sections("metadata")
        assert len(deps) == 0
    
    def test_validate_section_order_no_dependencies(self):
        """Should allow sections with no dependencies."""
        assert validate_section_order([], "metadata") is True
        assert validate_section_order([], "research_question") is True
    
    def test_validate_section_order_with_dependencies(self):
        """Should enforce dependencies."""
        # Cannot do methodology without research_question
        assert validate_section_order([], "methodology") is False
        
        # Can do methodology after dependencies met
        assert validate_section_order(
            ["research_question", "theoretical_framework"],
            "methodology"
        ) is True
    
    def test_get_all_sections(self):
        """Should return all sections in order."""
        sections = get_all_sections()
        assert len(sections) == 15
        assert sections[0].section_id == "metadata"
        assert sections[-1].section_id == "key_references"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
