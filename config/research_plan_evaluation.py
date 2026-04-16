"""
Research Plan Evaluation Criteria

Defines evaluation criteria for assessing research plan quality,
based on Option A (Conservative) approach from critical analysis.

Option A vs Option B:
- Option A (SELECTED): 4 main criteria with redistributed subcriteria
  - Maintains established grant review structure (NSF, H2020, NIH)
  - Ethics integrated under Rigor, Dissemination under Contribution
  - Easier for reviewers familiar with standard frameworks
- Option B (rejected): 5 criteria with standalone Ethics & Impact
  - Would add complexity without clear benefit
  - Less aligned with established review standards

Evaluation Structure:
- 4 main criteria (Clarity, Feasibility, Rigor, Contribution)
- Each with subcriteria (21 total)
- Total score: 100 points
- Target: ≥85 for approval

Based on:
- NSF grant review criteria
- H2020/Horizon Europe evaluation standards
- CRITICAL_ANALYSIS_Research_Plan_Sections.md (Option A)
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum


class EvaluatorPersona(Enum):
    """Personas for multi-evaluator assessment."""
    METHODOLOGY_EXPERT = "methodology_expert"
    RESEARCH_SUPERVISOR = "research_supervisor"
    DOMAIN_EXPERT = "domain_expert"
    ETHICS_REVIEWER = "ethics_reviewer"


@dataclass
class SubCriterion:
    """Individual sub-criterion within a main criterion."""
    name: str
    max_score: int
    description: str
    evaluation_questions: List[str]


@dataclass
class MainCriterion:
    """Main evaluation criterion."""
    name: str
    weight: float
    max_score: int
    description: str
    subcriteria: Dict[str, SubCriterion]
    primary_persona: EvaluatorPersona


# =============================================================================
# EVALUATION CRITERIA (Option A - Conservative)
# =============================================================================

EVALUATION_CRITERIA = {
    
    # =========================================================================
    # CRITERION 1: CLARITY (25%)
    # =========================================================================
    "clarity": MainCriterion(
        name="Clarity",
        weight=0.25,
        max_score=25,
        description="Clarity of research questions, objectives, structure, and language",
        primary_persona=EvaluatorPersona.RESEARCH_SUPERVISOR,
        subcriteria={
            "research_questions": SubCriterion(
                name="Research Questions",
                max_score=8,
                description="Main RQ and sub-questions are clear, focused, and answerable",
                evaluation_questions=[
                    "Is the main research question clearly stated?",
                    "Are sub-questions specific and aligned with main RQ?",
                    "Is the scope of the review clearly defined?",
                    "Does the PCC/PICOS framework support the RQ?"
                ]
            ),
            "objectives": SubCriterion(
                name="Objectives",
                max_score=6,
                description="Review objectives are specific, measurable, and aligned with RQ",
                evaluation_questions=[
                    "Are objectives explicitly stated?",
                    "Are they specific and measurable?",
                    "Do they logically follow from the RQ?",
                    "Is the scope realistic?"
                ]
            ),
            "structure": SubCriterion(
                name="Structure",
                max_score=6,
                description="Logical flow and organization of the research plan",
                evaluation_questions=[
                    "Is there a clear logical progression?",
                    "Are sections well-organized?",
                    "Do sections build on each other appropriately?",
                    "Is navigation easy for readers?"
                ]
            ),
            "language": SubCriterion(
                name="Language",
                max_score=5,
                description="Academic tone, precision, and absence of ambiguity",
                evaluation_questions=[
                    "Is language precise and unambiguous?",
                    "Is academic tone maintained?",
                    "Are technical terms properly defined?",
                    "Is writing concise yet comprehensive?"
                ]
            )
        }
    ),
    
    # =========================================================================
    # CRITERION 2: FEASIBILITY (25%)
    # =========================================================================
    "feasibility": MainCriterion(
        name="Feasibility",
        weight=0.25,
        max_score=25,
        description="Realistic timeline, adequate resources, manageable scope, and team qualifications",
        primary_persona=EvaluatorPersona.RESEARCH_SUPERVISOR,
        subcriteria={
            "timeline": SubCriterion(
                name="Timeline",
                max_score=7,
                description="Realistic schedule with appropriate phase durations",
                evaluation_questions=[
                    "Is the overall timeline realistic?",
                    "Are phase durations appropriate?",
                    "Are milestones clearly defined?",
                    "Is there contingency time built in?",
                    "Are dependencies between phases considered?"
                ]
            ),
            "resources_budget": SubCriterion(
                name="Resources & Budget",
                max_score=7,
                description="Adequate budget, clear resource allocation, justified costs",
                evaluation_questions=[
                    "Is the budget comprehensive and realistic?",
                    "Are all cost items justified?",
                    "Are resources (databases, software) accessible?",
                    "Is infrastructure adequate?",
                    "Are funding sources identified?"
                ]
            ),
            "team_qualifications": SubCriterion(
                name="Team Qualifications",
                max_score=6,
                description="Team has appropriate expertise and adequate FTE allocation",
                evaluation_questions=[
                    "Does the team have necessary expertise?",
                    "Are roles clearly defined?",
                    "Is FTE allocation realistic?",
                    "Are training needs addressed?",
                    "Is supervision structure clear?"
                ]
            ),
            "scope": SubCriterion(
                name="Scope",
                max_score=3,
                description="Review scope is manageable within constraints",
                evaluation_questions=[
                    "Is the scope neither too broad nor too narrow?",
                    "Can it realistically be completed in the timeline?",
                    "Are boundaries clearly defined?"
                ]
            ),
            "risk_mitigation": SubCriterion(
                name="Risk Mitigation",
                max_score=2,
                description="Risks identified with mitigation strategies",
                evaluation_questions=[
                    "Are potential risks identified?",
                    "Are mitigation strategies proposed?",
                    "Is contingency planning adequate?"
                ]
            )
        }
    ),
    
    # =========================================================================
    # CRITERION 3: RIGOR (30%)
    # =========================================================================
    "rigor": MainCriterion(
        name="Rigor",
        weight=0.30,
        max_score=30,
        description="Methodological soundness, PRISMA-ScR compliance, reproducibility, and ethical considerations",
        primary_persona=EvaluatorPersona.METHODOLOGY_EXPERT,
        subcriteria={
            "methodology": SubCriterion(
                name="Methodology",
                max_score=9,
                description="Sound scoping review methodology aligned with PRISMA-ScR",
                evaluation_questions=[
                    "Is the choice of scoping review justified?",
                    "Does it follow PRISMA-ScR guidelines?",
                    "Is the 5-stage process clearly described?",
                    "Is the approach appropriate for the RQ?",
                    "Will results be reproducible?"
                ]
            ),
            "search_strategy": SubCriterion(
                name="Search Strategy",
                max_score=8,
                description="Comprehensive, reproducible search with appropriate databases and strings",
                evaluation_questions=[
                    "Are databases appropriate and comprehensive?",
                    "Are search strings well-constructed?",
                    "Are Boolean operators used correctly?",
                    "Is the strategy reproducible?",
                    "Is grey literature considered?",
                    "Is search validation planned?"
                ]
            ),
            "eligibility_criteria": SubCriterion(
                name="Eligibility Criteria",
                max_score=5,
                description="Clear, justified inclusion/exclusion criteria",
                evaluation_questions=[
                    "Are criteria clearly defined?",
                    "Are they justified and appropriate?",
                    "Is pilot testing planned?",
                    "Will inter-rater reliability be assessed?"
                ]
            ),
            "quality_assessment": SubCriterion(
                name="Quality Assessment",
                max_score=5,
                description="Appropriate tools and process for critical appraisal",
                evaluation_questions=[
                    "Are appropriate appraisal tools selected?",
                    "Is the appraisal process clearly described?",
                    "Will quality scores be used appropriately?",
                    "Is risk of bias considered?"
                ]
            ),
            "ethics_data_mgmt": SubCriterion(
                name="Ethics & Data Management",
                max_score=3,
                description="Ethical considerations and GDPR-compliant data management",
                evaluation_questions=[
                    "Is ethics approval status clarified?",
                    "Is data management plan adequate?",
                    "Is GDPR compliance addressed?",
                    "Are conflicts of interest declared?"
                ]
            )
        }
    ),
    
    # =========================================================================
    # CRITERION 4: CONTRIBUTION (20%)
    # =========================================================================
    "contribution": MainCriterion(
        name="Contribution",
        weight=0.20,
        max_score=20,
        description="Novelty, significance, practical implications, and dissemination plan",
        primary_persona=EvaluatorPersona.DOMAIN_EXPERT,
        subcriteria={
            "novelty": SubCriterion(
                name="Novelty",
                max_score=7,
                description="Original contribution to knowledge or methodology",
                evaluation_questions=[
                    "Does it address identified research gaps?",
                    "Is there a novel theoretical contribution?",
                    "Does it offer methodological innovation?",
                    "Will it advance the field?"
                ]
            ),
            "significance": SubCriterion(
                name="Significance",
                max_score=6,
                description="Importance and potential impact of findings",
                evaluation_questions=[
                    "Is the topic significant and timely?",
                    "Will findings have theoretical importance?",
                    "Is there potential for practical impact?",
                    "Will it influence policy or practice?"
                ]
            ),
            "implications_impact": SubCriterion(
                name="Implications & Impact",
                max_score=5,
                description="Clear articulation of practical utility and implications",
                evaluation_questions=[
                    "Are implications clearly articulated?",
                    "Is practical utility evident?",
                    "Are recommendations actionable?",
                    "Is impact beyond academia considered?"
                ]
            ),
            "dissemination": SubCriterion(
                name="Dissemination",
                max_score=2,
                description="Strategy for sharing findings with diverse audiences",
                evaluation_questions=[
                    "Is there a clear publication plan?",
                    "Are multiple audiences considered?",
                    "Is open science practiced?",
                    "Are impact metrics defined?"
                ]
            )
        }
    )
}


# =============================================================================
# EVALUATOR PERSONAS
# =============================================================================

EVALUATOR_PERSONAS = {
    EvaluatorPersona.METHODOLOGY_EXPERT: {
        "name": "Methodology Expert",
        "weight": 0.40,
        "focus": "Research rigor, PRISMA-ScR compliance, reproducibility, methodological soundness",
        "primary_criteria": ["rigor"],
        "expertise": [
            "Scoping review methodology",
            "PRISMA-ScR guidelines",
            "Systematic search strategies",
            "Quality appraisal methods",
            "Evidence synthesis"
        ]
    },
    EvaluatorPersona.RESEARCH_SUPERVISOR: {
        "name": "Research Supervisor",
        "weight": 0.30,
        "focus": "Feasibility, timeline realism, clarity of objectives, project management",
        "primary_criteria": ["feasibility", "clarity"],
        "expertise": [
            "Project management",
            "Resource allocation",
            "Timeline planning",
            "Risk management",
            "Team supervision"
        ]
    },
    EvaluatorPersona.DOMAIN_EXPERT: {
        "name": "Domain Expert",
        "weight": 0.20,
        "focus": "Theoretical grounding, content accuracy, significance, contribution to field",
        "primary_criteria": ["contribution"],
        "expertise": [
            "AI and digital transformation",
            "Occupational health psychology",
            "Human resource management",
            "Organizational behavior",
            "Work-related stress"
        ]
    },
    EvaluatorPersona.ETHICS_REVIEWER: {
        "name": "Ethics Reviewer",
        "weight": 0.10,
        "focus": "Ethical considerations, data protection, research integrity, conflicts of interest",
        "primary_criteria": ["rigor"],  # Ethics falls under rigor
        "expertise": [
            "Research ethics",
            "GDPR compliance",
            "Data management",
            "Research integrity",
            "Conflict of interest assessment"
        ]
    }
}


# =============================================================================
# SCORING THRESHOLDS
# =============================================================================

class QualityVerdict(Enum):
    """Quality verdict based on overall score."""
    EXCELLENT = "excellent"  # ≥95
    APPROVED = "approved"  # 85-94
    MINOR_REVISION = "minor_revision"  # 75-84
    MAJOR_REVISION = "major_revision"  # 65-74
    SUBSTANTIAL_REWORK = "substantial_rework"  # <65


SCORE_THRESHOLDS = {
    QualityVerdict.EXCELLENT: 95,
    QualityVerdict.APPROVED: 85,
    QualityVerdict.MINOR_REVISION: 75,
    QualityVerdict.MAJOR_REVISION: 65,
    QualityVerdict.SUBSTANTIAL_REWORK: 0
}


def get_verdict(score: int) -> QualityVerdict:
    """Determine verdict based on score."""
    if score >= 95:
        return QualityVerdict.EXCELLENT
    elif score >= 85:
        return QualityVerdict.APPROVED
    elif score >= 75:
        return QualityVerdict.MINOR_REVISION
    elif score >= 65:
        return QualityVerdict.MAJOR_REVISION
    else:
        return QualityVerdict.SUBSTANTIAL_REWORK


def calculate_weighted_score(criteria_scores: Dict[str, int]) -> int:
    """Calculate overall weighted score from criterion scores."""
    total = 0.0
    for criterion_id, score in criteria_scores.items():
        if criterion_id in EVALUATION_CRITERIA:
            criterion = EVALUATION_CRITERIA[criterion_id]
            # Score is already out of max_score, just sum
            total += score
    return round(total)


def validate_evaluation(evaluation: Dict) -> Tuple[bool, List[str]]:
    """
    Validate that evaluation contains all required scores with correct ranges.
    
    Checks:
    - All main criteria present
    - All subcriteria present
    - All scores are numeric and within valid range (0 to max_score)
    - Criterion totals match expected max_score
    
    Args:
        evaluation: Dictionary with criterion scores
    
    Returns:
        Tuple of (valid: bool, errors: List[str])
    """
    errors = []
    
    # Check all main criteria present
    for criterion_id in EVALUATION_CRITERIA.keys():
        if criterion_id not in evaluation:
            errors.append(f"Missing criterion: {criterion_id}")
            continue
        
        criterion = EVALUATION_CRITERIA[criterion_id]
        criterion_scores = evaluation[criterion_id]
        criterion_total = 0.0
        
        if not isinstance(criterion_scores, dict):
            errors.append(
                f"{criterion_id}: Must be a dictionary, got {type(criterion_scores).__name__}"
            )
            continue
        
        # Check all subcriteria present and validate scores
        for subcriterion_id, subcriterion in criterion.subcriteria.items():
            if subcriterion_id not in criterion_scores:
                errors.append(
                    f"Missing subcriterion: {criterion_id}.{subcriterion_id}"
                )
                continue
            
            score = criterion_scores[subcriterion_id]
            max_score = subcriterion.max_score
            
            # Validate score type
            if not isinstance(score, (int, float)):
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score must be numeric, got {type(score).__name__}"
                )
                continue
            
            # Validate score range
            if score < 0:
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score cannot be negative ({score})"
                )
            elif score > max_score:
                errors.append(
                    f"{criterion_id}.{subcriterion_id}: "
                    f"Score {score} exceeds max {max_score}"
                )
            
            criterion_total += score
        
        # Check criterion total matches expected max_score
        # Allow small floating point tolerance
        if abs(criterion_total - criterion.max_score) > 0.1:
            errors.append(
                f"{criterion_id}: Subscore total {criterion_total:.1f} != "
                f"expected max {criterion.max_score}"
            )
    
    return len(errors) == 0, errors


# =============================================================================
# HELPERS
# =============================================================================

def get_criterion_max_score(criterion_id: str) -> int:
    """Get maximum score for a criterion."""
    return EVALUATION_CRITERIA[criterion_id].max_score


def get_subcriterion_max_score(criterion_id: str, subcriterion_id: str) -> int:
    """Get maximum score for a subcriterion."""
    return EVALUATION_CRITERIA[criterion_id].subcriteria[subcriterion_id].max_score


def get_all_criteria_names() -> List[str]:
    """Get list of all criterion names."""
    return list(EVALUATION_CRITERIA.keys())


def get_persona_info(persona: EvaluatorPersona) -> Dict:
    """Get information about an evaluator persona."""
    return EVALUATOR_PERSONAS[persona]


if __name__ == "__main__":
    # Test: Print evaluation structure
    print("="*70)
    print("   RESEARCH PLAN EVALUATION CRITERIA (Option A)")
    print("="*70 + "\n")
    
    total_score = 0
    for criterion_id, criterion in EVALUATION_CRITERIA.items():
        print(f"\n{criterion.name.upper()} ({criterion.weight*100:.0f}% / {criterion.max_score} points)")
        print(f"Primary Persona: {criterion.primary_persona.value}")
        print(f"Description: {criterion.description}\n")
        
        for subcriterion_id, subcriterion in criterion.subcriteria.items():
            print(f"  • {subcriterion.name:30} {subcriterion.max_score:2} points")
        
        total_score += criterion.max_score
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {total_score} points")
    print(f"Target: ≥85 (Approved)")
    print(f"Minimum Acceptable: ≥75 (Minor Revision)")
    print(f"{'='*70}\n")
    
    # Print personas
    print("\nEVALUATOR PERSONAS:")
    for persona, info in EVALUATOR_PERSONAS.items():
        print(f"\n{info['name']} ({info['weight']*100:.0f}%)")
        print(f"Focus: {info['focus']}")
