"""Quality thresholds and gates configuration."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QualityVerdict(Enum):
    """Quality evaluation verdict."""
    ACCEPT = "accept"
    MINOR_REVISION = "minor_revision"
    MAJOR_REVISION = "major_revision"
    SUBSTANTIAL_REWORK = "substantial_rework"


class BiasRisk(Enum):
    """Bias risk levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceLevel(Enum):
    """PRISMA-ScR compliance level."""
    FULL = "full"           # 22/22
    HIGH = "high"           # 20-21/22
    ACCEPTABLE = "acceptable"  # 18-19/22
    LOW = "low"             # <18/22


@dataclass
class QualityThresholds:
    """Quality score thresholds for sections."""
    
    # Overall section scores
    target_score: int = 85
    minimum_acceptable: int = 75
    stretch_goal: int = 92
    
    # Verdict thresholds
    accept_threshold: int = 85
    minor_revision_min: int = 75
    major_revision_min: int = 65
    
    # Per-criterion thresholds (out of max)
    methodology_rigor_target: int = 26  # out of 30
    synthesis_quality_target: int = 25   # out of 30
    presentation_target: int = 17        # out of 20
    contribution_target: int = 17        # out of 20
    
    def get_verdict(self, score: int) -> QualityVerdict:
        """Determine verdict based on score."""
        if score >= self.accept_threshold:
            return QualityVerdict.ACCEPT
        elif score >= self.minor_revision_min:
            return QualityVerdict.MINOR_REVISION
        elif score >= self.major_revision_min:
            return QualityVerdict.MAJOR_REVISION
        else:
            return QualityVerdict.SUBSTANTIAL_REWORK


@dataclass
class QualityGates:
    """Quality gates that must pass before proceeding."""
    
    # Fact checking
    fact_check_pass_rate: float = 0.95
    max_unverified_claims: int = 2
    max_contradicted_claims: int = 0
    
    # Consistency
    consistency_score_min: float = 0.90
    terminology_consistency_min: float = 0.95
    
    # Citation
    citation_coverage_min: float = 0.90
    citation_density_min: float = 2.0   # citations per paragraph
    citation_density_max: float = 6.0
    
    # Bias
    max_acceptable_bias_risk: BiasRisk = BiasRisk.MODERATE
    
    # PRISMA compliance
    min_prisma_items: int = 18
    
    # Plagiarism
    originality_score_min: float = 0.90
    
    # Iteration limits
    max_iterations_per_section: int = 5
    early_stop_no_improvement: int = 2
    
    def check_fact_check_gate(
        self, 
        verified: int, 
        total: int, 
        unverified: int, 
        contradicted: int
    ) -> tuple[bool, str]:
        """Check if fact checking gate passes."""
        if total == 0:
            return True, "No claims to verify"
        
        pass_rate = verified / total
        
        if contradicted > self.max_contradicted_claims:
            return False, f"Too many contradicted claims: {contradicted}"
        
        if unverified > self.max_unverified_claims:
            return False, f"Too many unverified claims: {unverified}"
        
        if pass_rate < self.fact_check_pass_rate:
            return False, f"Pass rate {pass_rate:.2%} below threshold {self.fact_check_pass_rate:.2%}"
        
        return True, "Fact check passed"
    
    def check_bias_gate(self, bias_risk: BiasRisk) -> tuple[bool, str]:
        """Check if bias gate passes."""
        risk_order = [BiasRisk.LOW, BiasRisk.MODERATE, BiasRisk.HIGH, BiasRisk.CRITICAL]
        current_idx = risk_order.index(bias_risk)
        max_idx = risk_order.index(self.max_acceptable_bias_risk)
        
        if current_idx > max_idx:
            return False, f"Bias risk {bias_risk.value} exceeds maximum {self.max_acceptable_bias_risk.value}"
        
        return True, "Bias check passed"
    
    def check_consistency_gate(self, consistency_score: float) -> tuple[bool, str]:
        """Check if consistency gate passes."""
        if consistency_score < self.consistency_score_min:
            return False, f"Consistency {consistency_score:.2%} below {self.consistency_score_min:.2%}"
        return True, "Consistency check passed"
    
    def check_all_gates(
        self,
        fact_check_result: dict,
        bias_risk: BiasRisk,
        consistency_score: float,
        citation_coverage: float,
        prisma_items: int,
        originality_score: float
    ) -> tuple[bool, list[str]]:
        """Check all quality gates and return aggregated result."""
        failures = []
        
        # Fact check
        fc_pass, fc_msg = self.check_fact_check_gate(
            fact_check_result.get("verified", 0),
            fact_check_result.get("total", 0),
            fact_check_result.get("unverified", 0),
            fact_check_result.get("contradicted", 0)
        )
        if not fc_pass:
            failures.append(f"Fact Check: {fc_msg}")
        
        # Bias
        bias_pass, bias_msg = self.check_bias_gate(bias_risk)
        if not bias_pass:
            failures.append(f"Bias: {bias_msg}")
        
        # Consistency
        cons_pass, cons_msg = self.check_consistency_gate(consistency_score)
        if not cons_pass:
            failures.append(f"Consistency: {cons_msg}")
        
        # Citation coverage
        if citation_coverage < self.citation_coverage_min:
            failures.append(
                f"Citation Coverage: {citation_coverage:.2%} below {self.citation_coverage_min:.2%}"
            )
        
        # PRISMA compliance
        if prisma_items < self.min_prisma_items:
            failures.append(
                f"PRISMA Compliance: {prisma_items}/22 below minimum {self.min_prisma_items}/22"
            )
        
        # Originality
        if originality_score < self.originality_score_min:
            failures.append(
                f"Originality: {originality_score:.2%} below {self.originality_score_min:.2%}"
            )
        
        return len(failures) == 0, failures


@dataclass
class SaturationConfig:
    """Configuration for the saturation loop."""
    
    # Score targets
    target_score: int = 85
    minimum_acceptable: int = 75
    stretch_goal: int = 92
    
    # Iteration controls
    max_iterations: int = 5
    early_stop_if_no_improvement: int = 2
    min_improvement_delta: int = 2
    
    # Parallelization
    parallel_quality_checks: bool = True
    
    # Caching
    cache_research_results: bool = True
    
    # Human review triggers
    human_review_triggers: list[str] = field(default_factory=lambda: [
        "3_iterations_no_improvement",
        "quality_gate_fail",
        "bias_risk_high",
        "fact_check_fail_rate_above_10_percent",
        "score_regression_above_5_points"
    ])
    
    def should_trigger_human_review(
        self,
        iterations_no_improvement: int,
        quality_gates_passed: bool,
        bias_risk: BiasRisk,
        fact_check_fail_rate: float,
        score_regression: int
    ) -> tuple[bool, Optional[str]]:
        """Check if human review should be triggered."""
        
        if iterations_no_improvement >= 3:
            return True, "3_iterations_no_improvement"
        
        if not quality_gates_passed:
            return True, "quality_gate_fail"
        
        if bias_risk in [BiasRisk.HIGH, BiasRisk.CRITICAL]:
            return True, "bias_risk_high"
        
        if fact_check_fail_rate > 0.10:
            return True, "fact_check_fail_rate_above_10_percent"
        
        if score_regression > 5:
            return True, "score_regression_above_5_points"
        
        return False, None
