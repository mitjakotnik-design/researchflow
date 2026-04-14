"""Sections configuration for scientific review articles."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SectionStatus(Enum):
    """Section processing status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    REVISION_NEEDED = "revision_needed"
    APPROVED = "approved"


class PRISMASection(Enum):
    """PRISMA-ScR checklist sections."""
    TITLE = "title"
    ABSTRACT = "abstract"
    RATIONALE = "rationale"
    OBJECTIVES = "objectives"
    PROTOCOL = "protocol"
    ELIGIBILITY = "eligibility"
    INFORMATION_SOURCES = "information_sources"
    SEARCH = "search"
    SELECTION = "selection"
    DATA_CHARTING = "data_charting"
    DATA_ITEMS = "data_items"
    CRITICAL_APPRAISAL = "critical_appraisal"
    SYNTHESIS = "synthesis"
    STUDY_SELECTION = "study_selection"
    STUDY_CHARACTERISTICS = "study_characteristics"
    CRITICAL_APPRAISAL_RESULTS = "critical_appraisal_results"
    INDIVIDUAL_RESULTS = "individual_results"
    SYNTHESIS_RESULTS = "synthesis_results"
    LIMITATIONS = "limitations"
    CONCLUSIONS = "conclusions"
    FUNDING = "funding"
    CONFLICTS = "conflicts"


@dataclass
class SectionSpec:
    """Specification for an article section."""
    
    id: str
    name: str
    name_sl: str  # Slovenian name
    order: int
    
    # Content specs
    min_words: int
    max_words: int
    target_citations: int
    
    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    
    # PRISMA mapping
    prisma_items: list[PRISMASection] = field(default_factory=list)
    
    # Agent assignments
    primary_writer: str = "writer"
    supporting_agents: list[str] = field(default_factory=list)
    
    # Quality targets
    target_score: int = 85
    
    # Instructions
    content_guidelines: str = ""
    avoid_guidelines: str = ""


# Standard sections for scoping review
REVIEW_SECTIONS: dict[str, SectionSpec] = {
    "abstract": SectionSpec(
        id="abstract",
        name="Abstract",
        name_sl="Povzetek",
        order=0,
        min_words=200,
        max_words=300,
        target_citations=0,
        depends_on=[],  # Paradoxically, often written last
        prisma_items=[PRISMASection.ABSTRACT],
        supporting_agents=["synthesizer"],
        content_guidelines="""
        - Background: 2-3 sentences on the topic importance
        - Objective: Clear research question
        - Methods: Data sources, selection criteria, synthesis method
        - Results: Key quantitative findings
        - Conclusions: Main implications
        """,
        avoid_guidelines="Avoid citations in abstract. No new information not in body."
    ),
    
    "introduction": SectionSpec(
        id="introduction",
        name="Introduction",
        name_sl="Uvod",
        order=1,
        min_words=800,
        max_words=1200,
        target_citations=15,
        depends_on=[],
        prisma_items=[PRISMASection.RATIONALE, PRISMASection.OBJECTIVES],
        supporting_agents=["researcher", "gap_identifier"],
        content_guidelines="""
        - Start broad: Establish field context
        - Progressive narrowing: Move to specific topic
        - Knowledge gap: What's missing in current research
        - Research questions: Clearly stated, focused
        - Scope rationale: Why scoping review methodology
        """,
        avoid_guidelines="Avoid results preview. No methodology details (save for methods)."
    ),
    
    "methods": SectionSpec(
        id="methods",
        name="Methods",
        name_sl="Metode",
        order=2,
        min_words=1500,
        max_words=2500,
        target_citations=8,
        depends_on=["introduction"],
        prisma_items=[
            PRISMASection.PROTOCOL,
            PRISMASection.ELIGIBILITY,
            PRISMASection.INFORMATION_SOURCES,
            PRISMASection.SEARCH,
            PRISMASection.SELECTION,
            PRISMASection.DATA_CHARTING,
            PRISMASection.DATA_ITEMS,
            PRISMASection.CRITICAL_APPRAISAL,
            PRISMASection.SYNTHESIS
        ],
        supporting_agents=["methodology_validator", "citation_manager"],
        content_guidelines="""
        - Protocol registration: Where registered
        - Eligibility criteria: Inclusion/exclusion with rationale
        - Information sources: All databases, date ranges
        - Search strategy: Full search string from at least one database
        - Selection process: Screening steps, reviewers
        - Data charting: What data extracted and how
        - Synthesis: How data will be analyzed/presented
        """,
        avoid_guidelines="Avoid results. Be specific and reproducible."
    ),
    
    "results": SectionSpec(
        id="results",
        name="Results",
        name_sl="Rezultati",
        order=3,
        min_words=2000,
        max_words=4000,
        target_citations=30,
        depends_on=["methods"],
        prisma_items=[
            PRISMASection.STUDY_SELECTION,
            PRISMASection.STUDY_CHARACTERISTICS,
            PRISMASection.CRITICAL_APPRAISAL_RESULTS,
            PRISMASection.INDIVIDUAL_RESULTS,
            PRISMASection.SYNTHESIS_RESULTS
        ],
        supporting_agents=[
            "data_extractor", "synthesizer", "meta_analyst", 
            "visualizer", "fact_checker"
        ],
        content_guidelines="""
        - PRISMA flow diagram description
        - Study characteristics summary
        - Thematic synthesis with clear themes
        - Quantitative summary where appropriate
        - Tables and figures referenced
        - Evidence strength indicated
        """,
        avoid_guidelines="No interpretation (save for discussion). Report objectively."
    ),
    
    "discussion": SectionSpec(
        id="discussion",
        name="Discussion",
        name_sl="Razprava",
        order=4,
        min_words=1500,
        max_words=2500,
        target_citations=20,
        depends_on=["results"],
        prisma_items=[PRISMASection.LIMITATIONS, PRISMASection.CONCLUSIONS],
        supporting_agents=[
            "synthesizer", "critic", "bias_auditor", "gap_identifier"
        ],
        content_guidelines="""
        - Principal findings: Summary of main results
        - Comparison with literature: How findings relate to prior work
        - Implications: Theoretical and practical
        - Strengths: What the review does well
        - Limitations: Honest assessment of weaknesses
        - Future research: Specific directions
        """,
        avoid_guidelines="Avoid repeating all results. Balance critique with contribution."
    ),
    
    "conclusion": SectionSpec(
        id="conclusion",
        name="Conclusion",
        name_sl="Zaključek",
        order=5,
        min_words=200,
        max_words=400,
        target_citations=2,
        depends_on=["discussion"],
        prisma_items=[PRISMASection.CONCLUSIONS],
        supporting_agents=["synthesizer"],
        content_guidelines="""
        - Concise answer to research questions
        - Key takeaways
        - Call to action if appropriate
        """,
        avoid_guidelines="No new information. Don't just repeat abstract."
    )
}


@dataclass
class SectionState:
    """Runtime state for a section."""
    
    section_id: str
    status: SectionStatus = SectionStatus.PENDING
    current_iteration: int = 0
    
    # Content
    content: str = ""
    word_count: int = 0
    
    # Quality
    current_score: int = 0
    score_history: list[int] = field(default_factory=list)
    quality_issues: list[dict] = field(default_factory=list)
    
    # Gates
    gates_passed: bool = False
    gate_failures: list[str] = field(default_factory=list)
    
    # Metadata
    citations_count: int = 0
    last_modified: Optional[str] = None
    reviewer_comments: list[str] = field(default_factory=list)
    
    def update_score(self, new_score: int) -> int:
        """Update score and return delta."""
        delta = new_score - self.current_score if self.current_score > 0 else 0
        self.score_history.append(self.current_score)
        self.current_score = new_score
        return delta
    
    def get_improvement_trend(self, last_n: int = 3) -> str:
        """Analyze recent score improvement trend."""
        if len(self.score_history) < 2:
            return "insufficient_data"
        
        recent = self.score_history[-last_n:] + [self.current_score]
        diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        
        if all(d > 0 for d in diffs):
            return "improving"
        elif all(d < 0 for d in diffs):
            return "declining"
        elif all(d == 0 for d in diffs):
            return "stalled"
        else:
            return "fluctuating"


@dataclass
class SectionsConfig:
    """Configuration manager for all sections."""
    
    sections: dict[str, SectionSpec] = field(default_factory=lambda: REVIEW_SECTIONS.copy())
    section_states: dict[str, SectionState] = field(default_factory=dict)
    
    def initialize_states(self) -> None:
        """Initialize state tracking for all sections."""
        for section_id in self.sections:
            self.section_states[section_id] = SectionState(section_id=section_id)
    
    def get_ordered_sections(self) -> list[SectionSpec]:
        """Get sections in processing order."""
        return sorted(self.sections.values(), key=lambda s: s.order)
    
    def get_ready_sections(self) -> list[str]:
        """Get sections ready for processing (dependencies met)."""
        ready = []
        for section_id, spec in self.sections.items():
            state = self.section_states.get(section_id)
            if state and state.status != SectionStatus.PENDING:
                continue
            
            # Check dependencies
            deps_met = all(
                self.section_states.get(dep, SectionState(section_id=dep)).status == SectionStatus.APPROVED
                for dep in spec.depends_on
            )
            
            if deps_met:
                ready.append(section_id)
        
        return ready
    
    def get_section_progress(self) -> dict[str, dict]:
        """Get progress summary for all sections."""
        return {
            section_id: {
                "status": state.status.value,
                "iteration": state.current_iteration,
                "score": state.current_score,
                "word_count": state.word_count,
                "gates_passed": state.gates_passed
            }
            for section_id, state in self.section_states.items()
        }
    
    def all_approved(self) -> bool:
        """Check if all sections are approved."""
        return all(
            state.status == SectionStatus.APPROVED
            for state in self.section_states.values()
        )
    
    def calculate_total_progress(self) -> float:
        """Calculate overall progress percentage."""
        if not self.section_states:
            return 0.0
        
        status_weights = {
            SectionStatus.PENDING: 0.0,
            SectionStatus.IN_PROGRESS: 0.25,
            SectionStatus.UNDER_REVIEW: 0.50,
            SectionStatus.REVISION_NEEDED: 0.40,
            SectionStatus.APPROVED: 1.0
        }
        
        total = sum(
            status_weights[state.status]
            for state in self.section_states.values()
        )
        
        return total / len(self.section_states)
