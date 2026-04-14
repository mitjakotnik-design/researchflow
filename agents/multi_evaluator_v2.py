"""
Multi-Evaluator Agent V2: Enhanced quality evaluation with DI and validation.

Uses multiple evaluation personas and consensus scoring.
"""

import json
from typing import Any, Optional
from pydantic import BaseModel

import structlog

from agents.base_agent_v2 import EnhancedBaseAgent, AgentDependencies, AgentRole
from agents.request_models import EvaluateContentRequest, QuickCheckRequest, get_request_model
from config import QualityVerdict


logger = structlog.get_logger()


# Evaluation criteria aligned with Architecture v2.0
EVALUATION_CRITERIA = {
    "methodology": {
        "max_score": 30,
        "subcriteria": [
            ("search_strategy", 8, "Comprehensive and reproducible search"),
            ("eligibility_criteria", 7, "Clear inclusion/exclusion criteria"),
            ("data_extraction", 8, "Systematic data charting"),
            ("quality_assessment", 7, "Appropriate critical appraisal")
        ]
    },
    "synthesis": {
        "max_score": 30,
        "subcriteria": [
            ("thematic_analysis", 10, "Clear identification of themes"),
            ("evidence_integration", 10, "Coherent synthesis of findings"),
            ("gap_identification", 10, "Recognition of research gaps")
        ]
    },
    "presentation": {
        "max_score": 20,
        "subcriteria": [
            ("clarity", 7, "Clear and logical writing"),
            ("structure", 7, "Well-organized sections"),
            ("visualizations", 6, "Effective use of tables/figures")
        ]
    },
    "contribution": {
        "max_score": 20,
        "subcriteria": [
            ("novelty", 7, "Original contribution to field"),
            ("implications", 7, "Practical and theoretical implications"),
            ("future_directions", 6, "Clear research agenda")
        ]
    }
}


# Evaluation personas for diverse perspectives
PERSONAS = [
    {
        "name": "methodologist",
        "focus": "Research rigor, reproducibility, PRISMA-ScR compliance",
        "weight": 0.35
    },
    {
        "name": "domain_expert",
        "focus": "HR and AI content accuracy, theoretical grounding",
        "weight": 0.25
    },
    {
        "name": "editor",
        "focus": "Writing quality, clarity, academic style",
        "weight": 0.20
    },
    {
        "name": "practitioner",
        "focus": "Practical relevance, actionable insights",
        "weight": 0.20
    }
]


class MultiEvaluatorAgentV2(EnhancedBaseAgent):
    """
    Enhanced Multi-Evaluator with consensus scoring and DI.
    
    Capabilities:
    - Multi-criteria evaluation
    - Consensus scoring from multiple perspectives
    - Detailed feedback generation
    - Quality trend analysis
    """
    
    def __init__(self, deps: AgentDependencies):
        super().__init__(
            name="multi_evaluator",
            role=AgentRole.QUALITY,
            deps=deps,
            description="Evaluates content quality using consensus scoring",
            version="2.0.0"
        )
        
        # Evaluation history for trend analysis
        self._evaluation_history: list[dict] = []
        self._max_history = 100  # Prevent memory leak
    
    def get_request_model(self, action: str) -> Optional[type[BaseModel]]:
        """Get Pydantic model for action validation."""
        return get_request_model("multi_evaluator", action)
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute evaluator actions."""
        if action == "evaluate":
            return await self._evaluate_content(**kwargs)
        elif action == "quick_check":
            return await self._quick_check(**kwargs)
        elif action == "compare_versions":
            return await self._compare_versions(**kwargs)
        elif action == "get_trend":
            return self._get_quality_trend(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _evaluate_content(
        self,
        content: str,
        section: str,
        criteria: Optional[list] = None,
        iteration: Optional[int] = None,
        previous_score: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Perform comprehensive evaluation with multi-persona consensus."""
        
        # Get evaluations from multiple personas
        evaluations = await self._multi_persona_evaluation(content, section)
        
        # Calculate consensus
        consensus = self._calculate_consensus(evaluations)
        
        # Generate detailed feedback
        feedback = await self._generate_feedback(
            content=content,
            section=section,
            consensus=consensus
        )
        
        # Determine verdict
        verdict = self._determine_verdict(consensus["overall_score"])
        
        # Check for improvement
        improvement = None
        if previous_score is not None:
            improvement = consensus["overall_score"] - previous_score
        
        # Record in history (with limit)
        eval_record = {
            "iteration": iteration,
            "section": section,
            "overall_score": consensus["overall_score"],
            "verdict": verdict.value,
            "improvement": improvement,
        }
        self._evaluation_history.append(eval_record)
        if len(self._evaluation_history) > self._max_history:
            self._evaluation_history = self._evaluation_history[-self._max_history:]
        
        self.log.info(
            "evaluation_completed",
            section=section,
            overall_score=consensus["overall_score"],
            verdict=verdict.value,
            improvement=improvement
        )
        
        return {
            "overall_score": consensus["overall_score"],
            "methodology": consensus["methodology"],
            "synthesis": consensus["synthesis"],
            "presentation": consensus["presentation"],
            "contribution": consensus["contribution"],
            "verdict": verdict.value,
            "issues": feedback.get("issues", []),
            "strengths": feedback.get("strengths", []),
            "improvement_suggestions": feedback.get("suggestions", []),
            "persona_scores": evaluations,
            "confidence": consensus.get("confidence", 0.8),
            "improvement_from_previous": improvement,
        }
    
    async def _multi_persona_evaluation(
        self,
        content: str,
        section: str
    ) -> list[dict]:
        """Get evaluations from multiple personas."""
        
        evaluations = []
        
        for persona in PERSONAS:
            eval_result = await self._evaluate_as_persona(
                content=content,
                section=section,
                persona=persona
            )
            evaluations.append({
                "persona": persona["name"],
                "weight": persona["weight"],
                "scores": eval_result.get("scores", {}),
                "feedback": eval_result.get("feedback", "")
            })
        
        return evaluations
    
    async def _evaluate_as_persona(
        self,
        content: str,
        section: str,
        persona: dict
    ) -> dict:
        """Evaluate content from a specific persona's perspective."""
        
        criteria_text = "\n".join(
            f"- {name} (max {EVALUATION_CRITERIA[name]['max_score']}): "
            f"{', '.join(f'{s[0]} ({s[1]} pts)' for s in EVALUATION_CRITERIA[name]['subcriteria'])}"
            for name in EVALUATION_CRITERIA
        )
        
        system_prompt = f"""You are a {persona['name']} evaluating a scoping review {section} section.

Your focus: {persona['focus']}

Evaluation criteria:
{criteria_text}

Be rigorous but fair. Provide specific, actionable feedback."""
        
        prompt = f"""Evaluate this {section} section:

## Content
{content[:4000]}

## Evaluation Task
Score each criterion and provide specific feedback.

Output JSON:
{{
    "scores": {{
        "methodology": 0-30,
        "synthesis": 0-30,
        "presentation": 0-20,
        "contribution": 0-20
    }},
    "feedback": "Specific feedback from {persona['name']} perspective",
    "key_issues": ["issue1", "issue2"],
    "strengths": ["strength1", "strength2"]
}}"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "scores": {
                    "methodology": 20,
                    "synthesis": 20,
                    "presentation": 15,
                    "contribution": 15
                },
                "feedback": response.content[:500]
            }
    
    def _calculate_consensus(self, evaluations: list[dict]) -> dict:
        """Calculate weighted consensus from persona evaluations."""
        
        if not evaluations:
            return {
                "overall_score": 0,
                "methodology": 0,
                "synthesis": 0,
                "presentation": 0,
                "contribution": 0,
                "confidence": 0.0
            }
        
        # Weighted average for each criterion
        weighted_scores = {
            "methodology": 0.0,
            "synthesis": 0.0,
            "presentation": 0.0,
            "contribution": 0.0
        }
        total_weight = sum(e["weight"] for e in evaluations)
        
        for eval_data in evaluations:
            weight = eval_data["weight"]
            scores = eval_data.get("scores", {})
            
            for criterion in weighted_scores:
                weighted_scores[criterion] += (
                    scores.get(criterion, 0) * weight / total_weight
                )
        
        # Round scores
        for criterion in weighted_scores:
            weighted_scores[criterion] = round(weighted_scores[criterion])
        
        # Calculate overall
        overall = sum(weighted_scores.values())
        
        # Calculate confidence based on agreement
        score_variance = self._calculate_variance(evaluations)
        confidence = max(0.5, 1.0 - (score_variance / 100))
        
        return {
            "overall_score": overall,
            "methodology": weighted_scores["methodology"],
            "synthesis": weighted_scores["synthesis"],
            "presentation": weighted_scores["presentation"],
            "contribution": weighted_scores["contribution"],
            "confidence": round(confidence, 2)
        }
    
    def _calculate_variance(self, evaluations: list[dict]) -> float:
        """Calculate variance in scores across personas."""
        if len(evaluations) < 2:
            return 0.0
        
        overall_scores = []
        for e in evaluations:
            scores = e.get("scores", {})
            total = sum(scores.values())
            overall_scores.append(total)
        
        if not overall_scores:
            return 0.0
        
        mean = sum(overall_scores) / len(overall_scores)
        variance = sum((s - mean) ** 2 for s in overall_scores) / len(overall_scores)
        
        return variance ** 0.5  # Standard deviation
    
    async def _generate_feedback(
        self,
        content: str,
        section: str,
        consensus: dict
    ) -> dict:
        """Generate detailed feedback based on consensus."""
        
        prompt = f"""Based on these evaluation scores for a {section} section:

Scores:
- Methodology: {consensus['methodology']}/30
- Synthesis: {consensus['synthesis']}/30
- Presentation: {consensus['presentation']}/20
- Contribution: {consensus['contribution']}/20
- Overall: {consensus['overall_score']}/100

Content (first 2000 chars):
{content[:2000]}

Generate specific feedback:

Output JSON:
{{
    "issues": ["specific issue 1", "specific issue 2"],
    "strengths": ["strength 1", "strength 2"],
    "suggestions": [
        {{
            "area": "methodology|synthesis|presentation|contribution",
            "issue": "what's wrong",
            "suggestion": "how to fix it",
            "priority": "high|medium|low"
        }}
    ]
}}"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "issues": [],
                "strengths": [],
                "suggestions": []
            }
    
    def _determine_verdict(self, score: int) -> QualityVerdict:
        """Determine verdict based on score."""
        if score >= 85:
            return QualityVerdict.ACCEPT
        elif score >= 75:
            return QualityVerdict.MINOR_REVISION
        elif score >= 65:
            return QualityVerdict.MAJOR_REVISION
        else:
            return QualityVerdict.SUBSTANTIAL_REWORK
    
    async def _quick_check(
        self,
        content: str,
        check_types: Optional[list[str]] = None,
        **kwargs
    ) -> dict:
        """Perform quick quality check without full evaluation."""
        
        check_types = check_types or ["grammar", "citations", "structure"]
        
        prompt = f"""Quick quality check on this content:

{content[:3000]}

Check for:
{', '.join(check_types)}

Output JSON:
{{
    "passed": true/false,
    "issues": ["issue1", "issue2"],
    "score_estimate": 0-100
}}"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=500,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"passed": True, "issues": [], "score_estimate": 75}
    
    async def _compare_versions(
        self,
        version_a: str,
        version_b: str,
        section: str,
        **kwargs
    ) -> dict:
        """Compare two versions of content."""
        
        prompt = f"""Compare these two versions of a {section} section:

## Version A
{version_a[:2000]}

## Version B
{version_b[:2000]}

Compare and determine which is better:

Output JSON:
{{
    "better_version": "A" or "B",
    "score_diff_estimate": -10 to +10,
    "improvements_in_b": ["improvement1"],
    "regressions_in_b": ["regression1"],
    "recommendation": "use A|use B|merge elements"
}}"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=800,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "better_version": "B",
                "score_diff_estimate": 0,
                "improvements_in_b": [],
                "regressions_in_b": [],
                "recommendation": "review manually"
            }
    
    def _get_quality_trend(self, section: Optional[str] = None) -> dict:
        """Get quality trend from evaluation history."""
        
        relevant = self._evaluation_history
        if section:
            relevant = [e for e in relevant if e.get("section") == section]
        
        if not relevant:
            return {
                "trend": "unknown",
                "evaluations": 0,
                "avg_score": 0,
                "latest_score": 0
            }
        
        scores = [e.get("overall_score", 0) for e in relevant]
        
        # Determine trend
        if len(scores) < 2:
            trend = "insufficient_data"
        else:
            recent_avg = sum(scores[-3:]) / len(scores[-3:])
            older_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else recent_avg
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        
        return {
            "trend": trend,
            "evaluations": len(relevant),
            "avg_score": round(sum(scores) / len(scores), 1),
            "latest_score": scores[-1] if scores else 0,
            "history": relevant[-10:]
        }
