"""
Unit tests for research_plan_evaluation.py

Tests evaluation criteria, personas, scoring, and validation.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config.research_plan_evaluation import (
    get_verdict,
    calculate_weighted_score,
    validate_evaluation,
    get_criterion_max_score,
    get_subcriterion_max_score,
    get_all_criteria_names,
    get_persona_info,
    QualityVerdict,
    EvaluatorPersona,
    EVALUATION_CRITERIA,
    EVALUATOR_PERSONAS,
    SCORE_THRESHOLDS
)


class TestEvaluationStructure:
    """Tests for evaluation criteria structure."""
    
    def test_total_score_is_100(self):
        """Sum of all criterion max scores should be 100."""
        total = sum(c.max_score for c in EVALUATION_CRITERIA.values())
        assert total == 100, f"Total score is {total}, expected 100"
    
    def test_weights_sum_to_1(self):
        """Weights should sum to 1.0."""
        total_weight = sum(c.weight for c in EVALUATION_CRITERIA.values())
        assert abs(total_weight - 1.0) < 0.01, f"Total weight is {total_weight}, expected 1.0"
    
    def test_four_main_criteria(self):
        """Should have exactly 4 main criteria."""
        assert len(EVALUATION_CRITERIA) == 4
        assert "clarity" in EVALUATION_CRITERIA
        assert "feasibility" in EVALUATION_CRITERIA
        assert "rigor" in EVALUATION_CRITERIA
        assert "contribution" in EVALUATION_CRITERIA
    
    def test_subcriteria_sum_to_criterion_max(self):
        """Subcriteria max_scores should sum to criterion max_score."""
        for criterion_id, criterion in EVALUATION_CRITERIA.items():
            subscore_total = sum(
                sub.max_score for sub in criterion.subcriteria.values()
            )
            assert subscore_total == criterion.max_score, (
                f"{criterion_id}: subscores sum to {subscore_total}, "
                f"expected {criterion.max_score}"
            )
    
    def test_all_criteria_have_subcriteria(self):
        """Each criterion should have at least 3 subcriteria."""
        for criterion_id, criterion in EVALUATION_CRITERIA.items():
            assert len(criterion.subcriteria) >= 3, (
                f"{criterion_id} has only {len(criterion.subcriteria)} subcriteria"
            )


class TestPersonas:
    """Tests for evaluator personas."""
    
    def test_four_personas_defined(self):
        """Should have 4 evaluator personas."""
        assert len(EVALUATOR_PERSONAS) == 4
        assert EvaluatorPersona.METHODOLOGY_EXPERT in EVALUATOR_PERSONAS
        assert EvaluatorPersona.RESEARCH_SUPERVISOR in EVALUATOR_PERSONAS
        assert EvaluatorPersona.DOMAIN_EXPERT in EVALUATOR_PERSONAS
        assert EvaluatorPersona.ETHICS_REVIEWER in EVALUATOR_PERSONAS
    
    def test_persona_weights_sum_to_1(self):
        """Persona weights should sum to 1.0."""
        total_weight = sum(p["weight"] for p in EVALUATOR_PERSONAS.values())
        assert abs(total_weight - 1.0) < 0.01, f"Total persona weight is {total_weight}"
    
    def test_methodology_expert_has_highest_weight(self):
        """Methodology Expert should have 40% weight (highest)."""
        methodology_weight = EVALUATOR_PERSONAS[EvaluatorPersona.METHODOLOGY_EXPERT]["weight"]
        assert methodology_weight == 0.40
        
        # Should be highest weight
        all_weights = [p["weight"] for p in EVALUATOR_PERSONAS.values()]
        assert methodology_weight == max(all_weights)
    
    def test_get_persona_info(self):
        """get_persona_info should return persona details."""
        info = get_persona_info(EvaluatorPersona.METHODOLOGY_EXPERT)
        assert "name" in info
        assert "weight" in info
        assert "focus" in info
        assert info["weight"] == 0.40


class TestVerdict:
    """Tests for quality verdict determination."""
    
    def test_excellent_verdict(self):
        """Score ≥95 should be EXCELLENT."""
        assert get_verdict(95) == QualityVerdict.EXCELLENT
        assert get_verdict(100) == QualityVerdict.EXCELLENT
    
    def test_approved_verdict(self):
        """Score 85-94 should be APPROVED."""
        assert get_verdict(85) == QualityVerdict.APPROVED
        assert get_verdict(90) == QualityVerdict.APPROVED
        assert get_verdict(94) == QualityVerdict.APPROVED
    
    def test_minor_revision_verdict(self):
        """Score 75-84 should be MINOR_REVISION."""
        assert get_verdict(75) == QualityVerdict.MINOR_REVISION
        assert get_verdict(80) == QualityVerdict.MINOR_REVISION
        assert get_verdict(84) == QualityVerdict.MINOR_REVISION
    
    def test_major_revision_verdict(self):
        """Score 65-74 should be MAJOR_REVISION."""
        assert get_verdict(65) == QualityVerdict.MAJOR_REVISION
        assert get_verdict(70) == QualityVerdict.MAJOR_REVISION
        assert get_verdict(74) == QualityVerdict.MAJOR_REVISION
    
    def test_substantial_rework_verdict(self):
        """Score <65 should be SUBSTANTIAL_REWORK."""
        assert get_verdict(64) == QualityVerdict.SUBSTANTIAL_REWORK
        assert get_verdict(50) == QualityVerdict.SUBSTANTIAL_REWORK
        assert get_verdict(0) == QualityVerdict.SUBSTANTIAL_REWORK


class TestCalculateWeightedScore:
    """Tests for weighted score calculation."""
    
    def test_perfect_score(self):
        """All max scores should give 100."""
        scores = {
            "clarity": 25,
            "feasibility": 25,
            "rigor": 30,
            "contribution": 20
        }
        total = calculate_weighted_score(scores)
        assert total == 100
    
    def test_half_scores(self):
        """Half of max scores should give 50."""
        scores = {
            "clarity": 12.5,
            "feasibility": 12.5,
            "rigor": 15,
            "contribution": 10
        }
        total = calculate_weighted_score(scores)
        assert total == 50
    
    def test_zero_scores(self):
        """All zero scores should give 0."""
        scores = {
            "clarity": 0,
            "feasibility": 0,
            "rigor": 0,
            "contribution": 0
        }
        total = calculate_weighted_score(scores)
        assert total == 0
    
    def test_mixed_scores(self):
        """Mixed scores should calculate correctly."""
        scores = {
            "clarity": 20,  # 80%
            "feasibility": 20,  # 80%
            "rigor": 25,  # 83%
            "contribution": 15  # 75%
        }
        total = calculate_weighted_score(scores)
        assert total == 80  # Average ~80


class TestValidateEvaluation:
    """Tests for evaluation validation."""
    
    def test_complete_valid_evaluation(self):
        """Complete evaluation with valid scores should pass."""
        evaluation = {
            "clarity": {
                "research_questions": 8,
                "objectives": 6,
                "structure": 6,
                "language": 5
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is True, f"Errors: {errors}"
        assert len(errors) == 0
    
    def test_missing_criterion(self):
        """Missing criterion should fail."""
        evaluation = {
            "clarity": {
                "research_questions": 8,
                "objectives": 6,
                "structure": 6,
                "language": 5
            }
            # Missing feasibility, rigor, contribution
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is False
        assert len(errors) >= 3  # At least 3 missing criteria
        assert any("feasibility" in err.lower() for err in errors)
    
    def test_missing_subcriterion(self):
        """Missing subcriterion should fail."""
        evaluation = {
            "clarity": {
                "research_questions": 8
                # Missing objectives, structure, language
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is False
        assert any("objectives" in err.lower() for err in errors)
    
    def test_score_exceeds_max(self):
        """Score exceeding max should fail."""
        evaluation = {
            "clarity": {
                "research_questions": 10,  # MAX IS 8!
                "objectives": 6,
                "structure": 6,
                "language": 5
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is False
        assert any("exceeds max" in err for err in errors)
    
    def test_negative_score(self):
        """Negative score should fail."""
        evaluation = {
            "clarity": {
                "research_questions": -1,  # NEGATIVE!
                "objectives": 6,
                "structure": 6,
                "language": 5
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is False
        assert any("negative" in err.lower() for err in errors)
    
    def test_non_numeric_score(self):
        """Non-numeric score should fail."""
        evaluation = {
            "clarity": {
                "research_questions": "eight",  # STRING!
                "objectives": 6,
                "structure": 6,
                "language": 5
            },
            "feasibility": {
                "timeline": 7,
                "resources_budget": 7,
                "team_qualifications": 6,
                "scope": 3,
                "risk_mitigation": 2
            },
            "rigor": {
                "methodology": 9,
                "search_strategy": 8,
                "eligibility_criteria": 5,
                "quality_assessment": 5,
                "ethics_data_mgmt": 3
            },
            "contribution": {
                "novelty": 7,
                "significance": 6,
                "implications_impact": 5,
                "dissemination": 2
            }
        }
        valid, errors = validate_evaluation(evaluation)
        assert valid is False
        assert any("numeric" in err.lower() for err in errors)


class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_get_criterion_max_score(self):
        """Should return correct max score for criterion."""
        assert get_criterion_max_score("clarity") == 25
        assert get_criterion_max_score("feasibility") == 25
        assert get_criterion_max_score("rigor") == 30
        assert get_criterion_max_score("contribution") == 20
    
    def test_get_subcriterion_max_score(self):
        """Should return correct max score for subcriterion."""
        assert get_subcriterion_max_score("clarity", "research_questions") == 8
        assert get_subcriterion_max_score("rigor", "methodology") == 9
    
    def test_get_all_criteria_names(self):
        """Should return list of all criteria names."""
        criteria = get_all_criteria_names()
        assert len(criteria) == 4
        assert "clarity" in criteria
        assert "feasibility" in criteria


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
