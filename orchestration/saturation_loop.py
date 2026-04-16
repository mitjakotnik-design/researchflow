"""Saturation Loop: Iterative improvement until quality targets met."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

import structlog

from config import (
    SaturationConfig,
    SectionSpec,
    SectionState,
    SectionStatus,
    QualityGates,
    QualityVerdict,
    BiasRisk,
)
from agents import BaseAgent, AgentResult


logger = structlog.get_logger()


@dataclass
class IterationResult:
    """Result of a single iteration."""
    
    iteration: int
    content: str
    score: int
    
    # Quality breakdown
    methodology_score: int = 0
    synthesis_score: int = 0
    presentation_score: int = 0
    contribution_score: int = 0
    
    # Gate results
    gates_passed: bool = False
    gate_failures: list[str] = field(default_factory=list)
    
    # Feedback
    issues: list[dict] = field(default_factory=list)
    improvements_made: list[str] = field(default_factory=list)
    
    # Metadata
    duration_ms: int = 0
    tokens_used: int = 0


@dataclass
class SaturationResult:
    """Final result of saturation loop."""
    
    success: bool
    section_id: str
    
    # Quality
    final_score: int
    target_score: int
    iterations_used: int
    
    # Content
    final_content: str
    word_count: int
    
    # History
    iteration_history: list[IterationResult] = field(default_factory=list)
    
    # Human review
    needs_human_review: bool = False
    human_review_reason: str = ""
    
    # Timing
    total_duration_ms: int = 0


class SaturationLoop:
    """
    Iteratively improves a section until quality targets are met.
    
    Process:
    1. Writer generates initial draft
    2. Quality agents evaluate
    3. If below threshold, identify improvements
    4. Writer revises based on feedback
    5. Repeat until satisfied or max iterations
    """
    
    def __init__(
        self,
        config: SaturationConfig,
        section_spec: SectionSpec,
        agents: dict[str, BaseAgent],
        quality_gates: QualityGates
    ):
        self.config = config
        self.section_spec = section_spec
        self.agents = agents
        self.quality_gates = quality_gates
        
        self.log = structlog.get_logger().bind(
            component="saturation_loop",
            section=section_spec.id
        )
    
    async def run(self, section_state: SectionState) -> SaturationResult:
        """Run the saturation loop."""
        import time
        start_time = time.perf_counter()
        
        iteration_history = []
        current_content = section_state.content or ""
        current_score = section_state.current_score
        
        no_improvement_count = 0
        
        for iteration in range(1, self.config.max_iterations + 1):
            self.log.info("iteration_started", iteration=iteration)
            
            iter_start = time.perf_counter()
            
            # Step 1: Generate or revise content
            if iteration == 1 and not current_content:
                current_content = await self._generate_initial_draft()
            else:
                # Get feedback from previous iteration
                feedback = iteration_history[-1].issues if iteration_history else []
                current_content = await self._revise_content(
                    current_content,
                    feedback,
                    iteration
                )
            
            # Step 2: Evaluate quality
            eval_result = await self._evaluate_quality(current_content)
            
            # Step 3: Check gates
            gates_passed, gate_failures = await self._check_gates(
                current_content,
                eval_result
            )
            
            # Create iteration result
            iter_result = IterationResult(
                iteration=iteration,
                content=current_content,
                score=eval_result.get("overall_score", 0),
                methodology_score=eval_result.get("methodology", 0),
                synthesis_score=eval_result.get("synthesis", 0),
                presentation_score=eval_result.get("presentation", 0),
                contribution_score=eval_result.get("contribution", 0),
                gates_passed=gates_passed,
                gate_failures=gate_failures,
                issues=eval_result.get("issues", []),
                duration_ms=int((time.perf_counter() - iter_start) * 1000)
            )
            
            iteration_history.append(iter_result)
            
            # Update section state
            score_delta = section_state.update_score(iter_result.score)
            section_state.content = current_content
            section_state.word_count = len(current_content.split())
            section_state.gates_passed = gates_passed
            section_state.gate_failures = gate_failures
            section_state.current_iteration = iteration
            
            self.log.info(
                "iteration_completed",
                iteration=iteration,
                score=iter_result.score,
                delta=score_delta,
                gates_passed=gates_passed
            )
            
            # Check stopping conditions
            
            # Success: Target met and gates passed
            if iter_result.score >= self.config.target_score and gates_passed:
                self.log.info("target_reached", score=iter_result.score)
                break
            
            # No improvement tracking
            if score_delta <= self.config.min_improvement_delta:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
            
            # Early stop: No improvement
            if no_improvement_count >= self.config.early_stop_if_no_improvement:
                self.log.warning(
                    "early_stop_no_improvement",
                    iterations_without_improvement=no_improvement_count
                )
                break
            
            current_score = iter_result.score
        
        total_duration = int((time.perf_counter() - start_time) * 1000)
        
        # IMPROVEMENT: Use BEST iteration (highest score) instead of last
        best_iteration = None
        best_content = current_content
        
        if iteration_history:
            # Find iteration with highest score
            best_iteration = max(iteration_history, key=lambda x: x.score)
            best_content = best_iteration.content
            
            self.log.info(
                "best_iteration_selected",
                best_iteration=best_iteration.iteration,
                best_score=best_iteration.score,
                last_iteration=iteration_history[-1].iteration,
                last_score=iteration_history[-1].score
            )
        else:
            best_iteration = None
        
        final_score = best_iteration.score if best_iteration else 0
        
        success = (
            final_score >= self.config.minimum_acceptable and
            (best_iteration.gates_passed if best_iteration else False)
        )
        
        needs_human_review, review_reason = self._check_human_review_needed(
            final_score,
            iteration_history,
            no_improvement_count
        )
        
        return SaturationResult(
            success=success,
            section_id=self.section_spec.id,
            final_score=final_score,
            target_score=self.config.target_score,
            iterations_used=len(iteration_history),
            final_content=best_content,
            word_count=len(best_content.split()),
            iteration_history=iteration_history,
            needs_human_review=needs_human_review,
            human_review_reason=review_reason,
            total_duration_ms=total_duration
        )
    
    async def _generate_initial_draft(self) -> str:
        """Generate initial section draft."""
        writer = self.agents.get("writer")
        if not writer:
            raise RuntimeError("Writer agent not available")
        
        result = await writer.execute(
            "write_section",
            section_id=self.section_spec.id,
            section_name=self.section_spec.name,
            min_words=self.section_spec.min_words,
            max_words=self.section_spec.max_words,
            guidelines=self.section_spec.content_guidelines,
            avoid=self.section_spec.avoid_guidelines
        )
        
        return result.output if result.success else ""
    
    async def _revise_content(
        self,
        content: str,
        feedback: list[dict],
        iteration: int
    ) -> str:
        """Revise content based on feedback."""
        writer = self.agents.get("writer")
        if not writer:
            return content
        
        # Format feedback for writer
        feedback_text = "\n".join([
            f"- {f.get('category', 'General')}: {f.get('description', '')}"
            for f in feedback[:10]  # Limit to top 10 issues
        ])
        
        result = await writer.execute(
            "revise_section",
            section_id=self.section_spec.id,
            current_content=content,
            feedback=feedback_text,
            iteration=iteration,
            focus_areas=[f.get("category") for f in feedback[:5]]
        )
        
        return result.output if result.success else content
    
    async def _evaluate_quality(self, content: str) -> dict:
        """Evaluate content quality using quality agents."""
        evaluations = {}
        
        # Run evaluators in parallel if configured
        agents_to_run = []
        
        if "multi_evaluator" in self.agents:
            agents_to_run.append(("multi_evaluator", "evaluate"))
        
        if "critic" in self.agents:
            agents_to_run.append(("critic", "critique"))
        
        tasks = [
            self.agents[name].execute(action, content=content, section=self.section_spec.id)
            for name, action in agents_to_run
        ]
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for (name, _), result in zip(agents_to_run, results):
                if isinstance(result, AgentResult) and result.success:
                    evaluations[name] = result.output
        
        # Aggregate scores
        overall_score = 0
        issues = []
        
        if "multi_evaluator" in evaluations:
            eval_data = evaluations["multi_evaluator"]
            if isinstance(eval_data, dict):
                overall_score = eval_data.get("overall_score", 0)
                issues.extend(eval_data.get("issues", []))
        
        if "critic" in evaluations:
            critic_data = evaluations["critic"]
            if isinstance(critic_data, dict):
                issues.extend(critic_data.get("issues", []))
        
        return {
            "overall_score": overall_score,
            "methodology": evaluations.get("multi_evaluator", {}).get("methodology", 0),
            "synthesis": evaluations.get("multi_evaluator", {}).get("synthesis", 0),
            "presentation": evaluations.get("multi_evaluator", {}).get("presentation", 0),
            "contribution": evaluations.get("multi_evaluator", {}).get("contribution", 0),
            "issues": issues,
            "raw_evaluations": evaluations
        }
    
    async def _check_gates(
        self,
        content: str,
        eval_result: dict
    ) -> tuple[bool, list[str]]:
        """Check quality gates."""
        failures = []
        
        # Fact checking gate
        if "fact_checker" in self.agents:
            fc_result = await self.agents["fact_checker"].execute(
                "check",
                content=content
            )
            
            if fc_result.success and isinstance(fc_result.output, dict):
                fc_data = fc_result.output
                passed, msg = self.quality_gates.check_fact_check_gate(
                    verified=fc_data.get("verified", 0),
                    total=fc_data.get("total", 0),
                    unverified=fc_data.get("unverified", 0),
                    contradicted=fc_data.get("contradicted", 0)
                )
                if not passed:
                    failures.append(f"Fact Check: {msg}")
        
        # Consistency gate
        if "consistency_checker" in self.agents:
            cc_result = await self.agents["consistency_checker"].execute(
                "check",
                content=content
            )
            
            if cc_result.success and isinstance(cc_result.output, dict):
                score = cc_result.output.get("consistency_score", 1.0)
                passed, msg = self.quality_gates.check_consistency_gate(score)
                if not passed:
                    failures.append(f"Consistency: {msg}")
        
        # Bias gate
        if "bias_auditor" in self.agents:
            ba_result = await self.agents["bias_auditor"].execute(
                "audit",
                content=content
            )
            
            if ba_result.success and isinstance(ba_result.output, dict):
                risk_str = ba_result.output.get("risk_level", "low")
                try:
                    risk = BiasRisk(risk_str)
                except ValueError:
                    risk = BiasRisk.LOW
                
                passed, msg = self.quality_gates.check_bias_gate(risk)
                if not passed:
                    failures.append(f"Bias: {msg}")
        
        return len(failures) == 0, failures
    
    def _check_human_review_needed(
        self,
        final_score: int,
        history: list[IterationResult],
        no_improvement_count: int
    ) -> tuple[bool, str]:
        """Check if human review is needed."""
        
        # Score too low
        if final_score < self.config.minimum_acceptable:
            return True, f"Final score {final_score} below minimum {self.config.minimum_acceptable}"
        
        # No improvement for too long
        if no_improvement_count >= self.config.early_stop_if_no_improvement:
            return True, f"No improvement for {no_improvement_count} iterations"
        
        # Gate failures in final iteration
        if history and not history[-1].gates_passed:
            return True, f"Gates failed: {', '.join(history[-1].gate_failures)}"
        
        # Score regression
        if len(history) >= 2:
            scores = [h.score for h in history]
            if scores[-1] < scores[-2] - 5:
                return True, f"Score regressed from {scores[-2]} to {scores[-1]}"
        
        return False, ""
