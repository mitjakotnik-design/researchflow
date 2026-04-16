"""
Research Plan Section Specifications

Defines all 15 sections of a comprehensive research plan for scoping reviews,
including requirements, target scores, and validation criteria.

Based on:
- PRISMA-ScR guidelines (Tricco et al., 2018)
- PROSPERO registration requirements
- Grant application best practices
- Critical analysis (CRITICAL_ANALYSIS_Research_Plan_Sections.md)
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple


@dataclass
class ResearchPlanSection:
    """Specification for a single research plan section."""
    
    # Identity
    section_id: str
    name: str
    description: str
    
    # Content requirements
    min_words: int
    max_words: int
    required_elements: List[str] = field(default_factory=list)
    optional_elements: List[str] = field(default_factory=list)
    
    # Quality requirements
    target_score: int = 85
    minimum_acceptable: int = 75
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other sections that must be completed first
    
    # Template
    template_path: Optional[str] = None
    examples: List[str] = field(default_factory=list)


# =============================================================================
# SECTION DEFINITIONS (15 SECTIONS)
# =============================================================================

RESEARCH_PLAN_SECTIONS = {
    
    # =========================================================================
    # SECTION 1: METADATA
    # =========================================================================
    "metadata": ResearchPlanSection(
        section_id="metadata",
        name="Title & Metadata",
        description="Basic identifying information for the research plan",
        min_words=50,
        max_words=200,
        required_elements=[
            "title",
            "authors",
            "institution",
            "date",
            "version",
            "status"
        ],
        optional_elements=[
            "alternative_titles",
            "keywords",
            "prospero_id"
        ],
        target_score=85,
        template_path="templates/research_plan/metadata_template.md"
    ),
    
    # =========================================================================
    # SECTION 2: RESEARCH QUESTION
    # =========================================================================
    "research_question": ResearchPlanSection(
        section_id="research_question",
        name="Research Question",
        description="Main research question, sub-questions, and PCC framework",
        min_words=300,
        max_words=600,
        required_elements=[
            "main_research_question",
            "sub_questions",
            "pcc_framework",
            "justification"
        ],
        optional_elements=[
            "picos_framework",
            "conceptual_clarifications"
        ],
        target_score=85,
        template_path="templates/research_plan/research_question_template.md"
    ),
    
    # =========================================================================
    # SECTION 3: THEORETICAL FRAMEWORK
    # =========================================================================
    "theoretical_framework": ResearchPlanSection(
        section_id="theoretical_framework",
        name="Theoretical Framework",
        description="Theories, models, and conceptual frameworks underpinning the review",
        min_words=400,
        max_words=800,
        required_elements=[
            "primary_theories",
            "theoretical_models",
            "conceptual_framework",
            "literature_context"
        ],
        optional_elements=[
            "conceptual_diagram",
            "theoretical_debates",
            "paradigm_position"
        ],
        target_score=85,
        depends_on=["research_question"],
        template_path="templates/research_plan/theoretical_framework_template.md"
    ),
    
    # =========================================================================
    # SECTION 4: METHODOLOGY
    # =========================================================================
    "methodology": ResearchPlanSection(
        section_id="methodology",
        name="Methodology",
        description="Overall review design, PRISMA-ScR rationale, and methodological approach",
        min_words=500,
        max_words=1000,
        required_elements=[
            "review_type",
            "prisma_scr_rationale",
            "study_design",
            "five_stage_process"
        ],
        optional_elements=[
            "comparison_to_systematic_review",
            "protocol_registration",
            "reporting_guidelines"
        ],
        target_score=85,
        depends_on=["research_question", "theoretical_framework"],
        template_path="templates/research_plan/methodology_template.md"
    ),
    
    # =========================================================================
    # SECTION 5: SEARCH STRATEGY
    # =========================================================================
    "search_strategy": ResearchPlanSection(
        section_id="search_strategy",
        name="Search Strategy",
        description="Databases, search strings, Boolean operators, and search documentation",
        min_words=400,
        max_words=800,
        required_elements=[
            "databases",
            "search_strings",
            "boolean_operators",
            "date_range",
            "language_restrictions"
        ],
        optional_elements=[
            "grey_literature",
            "hand_searching",
            "citation_chaining",
            "search_validation"
        ],
        target_score=85,
        depends_on=["methodology"],
        template_path="templates/research_plan/search_strategy_template.md"
    ),
    
    # =========================================================================
    # SECTION 6: ELIGIBILITY CRITERIA
    # =========================================================================
    "eligibility_criteria": ResearchPlanSection(
        section_id="eligibility_criteria",
        name="Eligibility Criteria",
        description="Inclusion and exclusion criteria with rationale",
        min_words=300,
        max_words=600,
        required_elements=[
            "inclusion_criteria",
            "exclusion_criteria",
            "rationale",
            "pilot_testing"
        ],
        optional_elements=[
            "criteria_table",
            "examples",
            "edge_cases"
        ],
        target_score=85,
        depends_on=["research_question", "methodology"],
        template_path="templates/research_plan/eligibility_criteria_template.md"
    ),
    
    # =========================================================================
    # SECTION 7: DATA EXTRACTION & CHARTING
    # =========================================================================
    "data_extraction": ResearchPlanSection(
        section_id="data_extraction",
        name="Data Extraction & Charting",
        description="Data charting form, pilot testing, and extraction process",
        min_words=400,
        max_words=800,
        required_elements=[
            "data_charting_form",
            "extraction_process",
            "pilot_testing",
            "inter_rater_reliability",
            "quality_control"
        ],
        optional_elements=[
            "software_tools",
            "training_protocol",
            "dispute_resolution"
        ],
        target_score=85,
        depends_on=["eligibility_criteria"],
        template_path="templates/research_plan/data_extraction_template.md"
    ),
    
    # =========================================================================
    # SECTION 8: QUALITY ASSESSMENT
    # =========================================================================
    "quality_assessment": ResearchPlanSection(
        section_id="quality_assessment",
        name="Quality Assessment",
        description="Critical appraisal tools and quality evaluation approach",
        min_words=300,
        max_words=600,
        required_elements=[
            "appraisal_tools",
            "quality_criteria",
            "appraisal_process",
            "use_of_quality_scores"
        ],
        optional_elements=[
            "risk_of_bias_assessment",
            "quality_stratification",
            "sensitivity_analysis"
        ],
        target_score=85,
        depends_on=["methodology"],
        template_path="templates/research_plan/quality_assessment_template.md"
    ),
    
    # =========================================================================
    # SECTION 9: IDENTIFIED GAPS
    # =========================================================================
    "identified_gaps": ResearchPlanSection(
        section_id="identified_gaps",
        name="Identified Research Gaps",
        description="Theoretical, empirical, methodological, and practical gaps in literature",
        min_words=400,
        max_words=800,
        required_elements=[
            "theoretical_gaps",
            "empirical_gaps",
            "methodological_gaps",
            "practical_gaps"
        ],
        optional_elements=[
            "priority_ranking",
            "gap_matrix",
            "implications_for_review"
        ],
        target_score=85,
        depends_on=["theoretical_framework"],
        template_path="templates/research_plan/identified_gaps_template.md"
    ),
    
    # =========================================================================
    # SECTION 10: TIMELINE & MILESTONES
    # =========================================================================
    "timeline": ResearchPlanSection(
        section_id="timeline",
        name="Timeline & Milestones",
        description="Project phases, duration, deliverables, and Gantt chart",
        min_words=200,
        max_words=400,
        required_elements=[
            "phases",
            "duration_per_phase",
            "milestones",
            "deliverables"
        ],
        optional_elements=[
            "gantt_chart",
            "critical_path",
            "buffer_time",
            "checkpoints"
        ],
        target_score=85,
        depends_on=["methodology"],
        template_path="templates/research_plan/timeline_template.md"
    ),
    
    # =========================================================================
    # SECTION 11: EXPECTED CONTRIBUTIONS
    # =========================================================================
    "expected_contributions": ResearchPlanSection(
        section_id="expected_contributions",
        name="Expected Contributions",
        description="Theoretical, methodological, practical, and policy contributions",
        min_words=300,
        max_words=600,
        required_elements=[
            "theoretical_contribution",
            "methodological_contribution",
            "practical_contribution"
        ],
        optional_elements=[
            "policy_contribution",
            "novelty_statement",
            "significance_statement"
        ],
        target_score=85,
        depends_on=["identified_gaps"],
        template_path="templates/research_plan/expected_contributions_template.md"
    ),
    
    # =========================================================================
    # SECTION 12: RESOURCES & BUDGET
    # =========================================================================
    "resources_budget": ResearchPlanSection(
        section_id="resources_budget",
        name="Resources & Budget",
        description="Research team, equipment, budget breakdown, and resource availability",
        min_words=300,
        max_words=600,
        required_elements=[
            "research_team",
            "budget_breakdown",
            "resource_availability",
            "infrastructure"
        ],
        optional_elements=[
            "funding_sources",
            "in_kind_contributions",
            "cost_justification"
        ],
        target_score=85,
        template_path="templates/research_plan/resources_budget_template.md"
    ),
    
    # =========================================================================
    # SECTION 13: ETHICAL CONSIDERATIONS
    # =========================================================================
    "ethical_considerations": ResearchPlanSection(
        section_id="ethical_considerations",
        name="Ethical Considerations",
        description="Ethics approval, data management, GDPR compliance, conflicts of interest",
        min_words=200,
        max_words=400,
        required_elements=[
            "ethics_approval_status",
            "data_management",
            "conflicts_of_interest"
        ],
        optional_elements=[
            "gdpr_compliance",
            "data_sharing_plan",
            "authorship_criteria"
        ],
        target_score=85,
        template_path="templates/research_plan/ethical_considerations_template.md"
    ),
    
    # =========================================================================
    # SECTION 14: DISSEMINATION STRATEGY
    # =========================================================================
    "dissemination_strategy": ResearchPlanSection(
        section_id="dissemination_strategy",
        name="Dissemination Strategy",
        description="Publication plan, conferences, stakeholder engagement, open science",
        min_words=300,
        max_words=600,
        required_elements=[
            "publication_plan",
            "conference_presentations",
            "stakeholder_engagement"
        ],
        optional_elements=[
            "open_science_practices",
            "policy_briefs",
            "impact_metrics",
            "media_strategy"
        ],
        target_score=85,
        template_path="templates/research_plan/dissemination_strategy_template.md"
    ),
    
    # =========================================================================
    # SECTION 15: KEY REFERENCES
    # =========================================================================
    "key_references": ResearchPlanSection(
        section_id="key_references",
        name="Key References",
        description="Methodological, theoretical, and domain-specific references",
        min_words=100,
        max_words=300,
        required_elements=[
            "methodological_references",
            "theoretical_references"
        ],
        optional_elements=[
            "domain_references",
            "exemplar_reviews",
            "tool_references"
        ],
        target_score=85,
        template_path="templates/research_plan/key_references_template.md"
    ),
}


# =============================================================================
# SECTION ORDERING & DEPENDENCIES
# =============================================================================

SECTION_ORDER = [
    "metadata",
    "research_question",
    "theoretical_framework",
    "methodology",
    "search_strategy",
    "eligibility_criteria",
    "data_extraction",
    "quality_assessment",
    "identified_gaps",
    "timeline",
    "expected_contributions",
    "resources_budget",
    "ethical_considerations",
    "dissemination_strategy",
    "key_references"
]


def get_section_spec(section_id: str) -> ResearchPlanSection:
    """
    Get section specification by ID with validation.
    
    Args:
        section_id: Section identifier
    
    Returns:
        ResearchPlanSection object
    
    Raises:
        TypeError: If section_id is not a string
        ValueError: If section_id is empty or unknown
    """
    if not isinstance(section_id, str):
        raise TypeError(f"section_id must be str, got {type(section_id).__name__}")
    
    if not section_id or not section_id.strip():
        raise ValueError("section_id cannot be empty")
    
    section_id = section_id.strip().lower()
    
    if section_id not in RESEARCH_PLAN_SECTIONS:
        valid_ids = ", ".join(sorted(RESEARCH_PLAN_SECTIONS.keys()))
        raise ValueError(
            f"Unknown section: '{section_id}'. "
            f"Valid sections: {valid_ids}"
        )
    
    return RESEARCH_PLAN_SECTIONS[section_id]


def get_dependent_sections(section_id: str) -> List[str]:
    """Get list of sections that must be completed before this one."""
    spec = get_section_spec(section_id)
    return spec.depends_on


def validate_section_order(completed_sections: List[str], next_section: str) -> bool:
    """Check if dependencies are satisfied for next section."""
    spec = get_section_spec(next_section)
    dependencies = set(spec.depends_on)
    completed = set(completed_sections)
    return dependencies.issubset(completed)


def get_all_sections() -> List[ResearchPlanSection]:
    """Get all sections in recommended order."""
    return [RESEARCH_PLAN_SECTIONS[sid] for sid in SECTION_ORDER]


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def validate_word_count(content: str, section_id: str) -> Tuple[bool, str]:
    """
    Validate word count against section requirements.
    
    Excludes markdown syntax, code blocks, and other non-content elements
    from word count to provide accurate measurement.
    
    Args:
        content: Markdown content to validate
        section_id: ID of the section
    
    Returns:
        Tuple of (valid: bool, message: str)
    
    Raises:
        ValueError: If section_id is unknown
        TypeError: If inputs are not strings
    """
    if not isinstance(content, str):
        raise TypeError(f"content must be str, got {type(content).__name__}")
    if not isinstance(section_id, str):
        raise TypeError(f"section_id must be str, got {type(section_id).__name__}")
    
    spec = get_section_spec(section_id)
    
    # Clean content for word counting
    content_clean = content
    
    # Remove code blocks (``` ... ```)
    content_clean = re.sub(r'```.*?```', '', content_clean, flags=re.DOTALL)
    
    # Remove inline code (`...`)
    content_clean = re.sub(r'`[^`]+`', '', content_clean)
    
    # Remove markdown headers (#, ##, ###, etc.)
    content_clean = re.sub(r'^#+\s+', '', content_clean, flags=re.MULTILINE)
    
    # Remove markdown formatting (**, __, *, _) but keep text
    content_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', content_clean)  # **bold**
    content_clean = re.sub(r'__([^_]+)__', r'\1', content_clean)  # __bold__
    content_clean = re.sub(r'\*([^*]+)\*', r'\1', content_clean)  # *italic*
    content_clean = re.sub(r'_([^_]+)_', r'\1', content_clean)  # _italic_
    
    # Remove links [text](url) but keep text
    content_clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content_clean)
    
    # Remove HTML tags
    content_clean = re.sub(r'<[^>]+>', '', content_clean)
    
    # Remove bullet points and list markers
    content_clean = re.sub(r'^\s*[-*+]\s+', '', content_clean, flags=re.MULTILINE)
    content_clean = re.sub(r'^\s*\d+\.\s+', '', content_clean, flags=re.MULTILINE)
    
    # Remove horizontal rules (---, ***, ___)
    content_clean = re.sub(r'^[-*_]{3,}\s*$', '', content_clean, flags=re.MULTILINE)
    
    # Split into words and filter out empty strings
    words = content_clean.split()
    word_count = len([w for w in words if w.strip()])
    
    if word_count < spec.min_words:
        return False, f"Too short: {word_count} words (min: {spec.min_words})"
    elif word_count > spec.max_words:
        return False, f"Too long: {word_count} words (max: {spec.max_words})"
    else:
        return True, f"Word count OK: {word_count} words"


def check_required_elements(content: str, section_id: str) -> Tuple[bool, List[str]]:
    """
    Check if required elements are present in content.
    
    Uses pattern matching with common variations and synonyms for better
    detection accuracy.
    
    Args:
        content: Section content to check
        section_id: Section identifier
    
    Returns:
        Tuple of (all_present: bool, missing_elements: List[str])
    
    Raises:
        TypeError: If inputs are not strings
        ValueError: If section_id is unknown
    """
    if not isinstance(content, str):
        raise TypeError(f"content must be str, got {type(content).__name__}")
    if not isinstance(section_id, str):
        raise TypeError(f"section_id must be str, got {type(section_id).__name__}")
    
    spec = get_section_spec(section_id)
    missing = []
    
    # Define patterns for common elements (expandable)
    ELEMENT_PATTERNS = {
        "main_research_question": [
            r"main\s+research\s+question",
            r"primary\s+research\s+question",
            r"overarching\s+question",
            r"main\s+RQ",
            r"RQ:"
        ],
        "sub_questions": [
            r"sub[- ]?questions?",
            r"secondary\s+questions?",
            r"RQ\d+",
            r"research\s+sub[- ]?questions?"
        ],
        "pcc_framework": [
            r"PCC\s+framework",
            r"Population.*?Concept.*?Context",
            r"P-C-C",
            r"PCC\s*\("
        ],
        "theoretical_framework": [
            r"theoretical\s+framework",
            r"conceptual\s+framework",
            r"theoretical\s+background",
            r"theory"
        ],
        "prisma_scr": [
            r"PRISMA[- ]?ScR",
            r"PRISMA.*?scoping\s+review",
            r"scoping\s+review.*?guideline"
        ],
        "search_strings": [
            r"search\s+string",
            r"search\s+term",
            r"Boolean.*?search",
            r"TS\s*=\s*\("
        ],
        "boolean_operators": [
            r"Boolean\s+operator",
            r"\bAND\b.*?\bOR\b",
            r"\bAND\b|\bOR\b|\bNOT\b"
        ],
        "databases": [
            r"database",
            r"Web\s+of\s+Science",
            r"Scopus",
            r"PubMed"
        ],
        "inclusion_criteria": [
            r"inclusion\s+criteria",
            r"included.*?studies",
            r"eligibility.*?inclusion"
        ],
        "exclusion_criteria": [
            r"exclusion\s+criteria",
            r"excluded.*?studies",
            r"eligibility.*?exclusion"
        ],
        "pilot_testing": [
            r"pilot\s+test",
            r"pilot.*?study",
            r"trial\s+run"
        ],
        "inter_rater_reliability": [
            r"inter[- ]?rater\s+reliability",
            r"Cohen.*?kappa",
            r"agreement.*?raters",
            r"IRR"
        ]
    }
    
    content_lower = content.lower()
    
    for element in spec.required_elements:
        found = False
        
        # Try custom patterns first if available
        if element in ELEMENT_PATTERNS:
            for pattern in ELEMENT_PATTERNS[element]:
                if re.search(pattern, content_lower, re.IGNORECASE | re.DOTALL):
                    found = True
                    break
        else:
            # Fallback: simple keyword check
            element_keywords = element.replace("_", " ").split()
            # Check if ANY keyword is present (lenient)
            if any(keyword in content_lower for keyword in element_keywords):
                found = True
        
        if not found:
            missing.append(element)
    
    return len(missing) == 0, missing


if __name__ == "__main__":
    # Test: Print all sections
    print("="*70)
    print("   RESEARCH PLAN SECTIONS")
    print("="*70 + "\n")
    
    for i, section_id in enumerate(SECTION_ORDER, 1):
        spec = RESEARCH_PLAN_SECTIONS[section_id]
        print(f"{i:2}. {spec.name}")
        print(f"    ID: {spec.section_id}")
        print(f"    Words: {spec.min_words}-{spec.max_words}")
        print(f"    Required: {len(spec.required_elements)} elements")
        print(f"    Depends on: {spec.depends_on if spec.depends_on else 'None'}")
        print()
    
    print(f"\nTotal sections: {len(SECTION_ORDER)}")
    print(f"Must-have: 12 | Recommended: 3")
