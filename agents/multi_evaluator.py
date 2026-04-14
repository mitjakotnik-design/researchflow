"""Multi-Evaluator Agent: Evaluates content quality with consensus scoring."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory
from config import QualityVerdict


logger = structlog.get_logger()


# Evaluation criteria based on Architecture v2.0
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


class MultiEvaluatorAgent(BaseAgent):
    """
    Agent responsible for comprehensive quality evaluation.
    
    Uses multiple evaluation personas and consensus scoring.
    
    Capabilities:
    - Multi-criteria evaluation
    - Consensus scoring from multiple perspectives
    - Detailed feedback generation
    - Quality trend analysis
    """
    
    def __init__(self):
        super().__init__(
            name="multi_evaluator",
            role=AgentRole.QUALITY,
            description="Evaluates content quality using consensus scoring",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._evaluation_history: list[dict] = []
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute evaluator actions."""
        if action == "evaluate":
            return await self._evaluate_content(**kwargs)
        elif action == "quick_check":
            return await self._quick_check(**kwargs)
        elif action == "compare_versions":
            return await self._compare_versions(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _evaluate_content(
        self,
        content: str,
        section: str,
        iteration: Optional[int] = None,
        previous_score: Optional[int] = None,
        **kwargs
    ) -> dict:
        """Perform comprehensive evaluation."""
        
        # Get evaluations from multiple personas
        evaluations = await self._multi_persona_evaluation(content, section)
        
        # Consensus scoring
        consensus = self._calculate_consensus(evaluations)
        
        # Generate detailed feedback
        feedback = await self._generate_feedback(
            content=content,
            section=section,
            consensus=consensus
        )
        
        # Determine verdict
        verdict = self._determine_verdict(consensus["overall_score"])
        
        # Record in history
        eval_record = {
            "iteration": iteration,
            "section": section,
            "consensus": consensus,
            "verdict": verdict.value,
            "feedback_count": len(feedback.get("issues", []))
        }
        self._evaluation_history.append(eval_record)
        
        self.log.info(
            "evaluation_completed",
            section=section,
            overall_score=consensus["overall_score"],
            verdict=verdict.value
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
            "confidence": consensus["confidence"]
        }
    
    async def _multi_persona_evaluation(
        self,
        content: str,
        section: str
    ) -> list[dict]:
        """Evaluate from multiple expert personas in PARALLEL."""
        import asyncio
        
        personas = [
            ("Methodology Expert", "Focus on research rigor, reproducibility, and systematic approach"),
            ("Domain Expert", "Focus on content accuracy, relevance, and contribution to the field"),
            ("Academic Editor", "Focus on clarity, structure, and academic writing quality")
        ]
        
        # Create evaluation tasks for parallel execution
        eval_tasks = [
            self._single_persona_evaluation(
                content=content,
                section=section,
                persona_name=persona_name,
                persona_focus=persona_focus
            )
            for persona_name, persona_focus in personas
        ]
        
        # Execute all evaluations in parallel
        evaluations = await asyncio.gather(*eval_tasks, return_exceptions=True)
        
        # Handle any exceptions
        valid_evaluations = []
        for i, eval_result in enumerate(evaluations):
            if isinstance(eval_result, Exception):
                self.log.error(
                    "persona_evaluation_failed",
                    persona=personas[i][0],
                    error=str(eval_result)
                )
                # Add fallback neutral evaluation
                valid_evaluations.append({
                    "persona": personas[i][0],
                    "methodology": {"score": 20, "comments": f"Error: {str(eval_result)}"},
                    "synthesis": {"score": 20, "comments": "Fallback"},
                    "presentation": {"score": 15, "comments": "Fallback"},
                    "contribution": {"score": 15, "comments": "Fallback"}
                })
            else:
                valid_evaluations.append(eval_result)
        
        return valid_evaluations
    
    async def _single_persona_evaluation(
        self,
        content: str,
        section: str,
        persona_name: str,
        persona_focus: str
    ) -> dict:
        """Get evaluation from a single persona."""
        
        system_prompt = f"""You are a {persona_name} reviewing a scientific scoping review.
{persona_focus}
Be objective, critical, and constructive."""
        
        # Build criteria prompt
        criteria_text = []
        for category, info in EVALUATION_CRITERIA.items():
            criteria_text.append(f"\n### {category.title()} (max {info['max_score']} points)")
            for sub, max_pts, desc in info["subcriteria"]:
                criteria_text.append(f"- {sub}: {desc} (0-{max_pts})")
        
        prompt = f"""Evaluate this {section} section:

## Content
{content[:6000]}

## Evaluation Criteria
{"".join(criteria_text)}

## Output JSON Format
{{
    "persona": "{persona_name}",
    "methodology": {{
        "score": <0-30>,
        "subscores": {{"search_strategy": <0-8>, "eligibility_criteria": <0-7>, "data_extraction": <0-8>, "quality_assessment": <0-7>}},
        "comments": "brief comments"
    }},
    "synthesis": {{
        "score": <0-30>,
        "subscores": {{"thematic_analysis": <0-10>, "evidence_integration": <0-10>, "gap_identification": <0-10>}},
        "comments": "brief comments"
    }},
    "presentation": {{
        "score": <0-20>,
        "subscores": {{"clarity": <0-7>, "structure": <0-7>, "visualizations": <0-6>}},
        "comments": "brief comments"
    }},
    "contribution": {{
        "score": <0-20>,
        "subscores": {{"novelty": <0-7>, "implications": <0-7>, "future_directions": <0-6>}},
        "comments": "brief comments"
    }},
    "overall_assessment": "2-3 sentence overall assessment"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            # Return neutral scores on parse failure
            return {
                "persona": persona_name,
                "methodology": {"score": 20, "comments": "Parse error"},
                "synthesis": {"score": 20, "comments": "Parse error"},
                "presentation": {"score": 15, "comments": "Parse error"},
                "contribution": {"score": 15, "comments": "Parse error"}
            }
    
    def _calculate_consensus(self, evaluations: list[dict]) -> dict:
        """Calculate consensus scores from multiple evaluations."""
        
        if not evaluations:
            return {
                "overall_score": 0,
                "methodology": 0,
                "synthesis": 0,
                "presentation": 0,
                "contribution": 0,
                "confidence": 0.0
            }
        
        # Extract scores per category
        categories = ["methodology", "synthesis", "presentation", "contribution"]
        scores = {cat: [] for cat in categories}
        
        for eval_result in evaluations:
            for cat in categories:
                if cat in eval_result and isinstance(eval_result[cat], dict):
                    scores[cat].append(eval_result[cat].get("score", 0))
        
        # Calculate means
        consensus = {}
        for cat in categories:
            if scores[cat]:
                consensus[cat] = int(sum(scores[cat]) / len(scores[cat]))
            else:
                consensus[cat] = 0
        
        consensus["overall_score"] = sum(consensus[cat] for cat in categories)
        
        # Calculate confidence based on score variance
        all_scores = [s for cat_scores in scores.values() for s in cat_scores]
        if len(all_scores) > 1:
            mean = sum(all_scores) / len(all_scores)
            variance = sum((s - mean) ** 2 for s in all_scores) / len(all_scores)
            # Lower variance = higher confidence
            consensus["confidence"] = max(0.5, min(1.0, 1.0 - (variance / 100)))
        else:
            consensus["confidence"] = 0.7
        
        return consensus
    
    async def _generate_feedback(
        self,
        content: str,
        section: str,
        consensus: dict
    ) -> dict:
        """Generate detailed improvement feedback."""
        
        prompt = f"""Based on this {section} section with score {consensus['overall_score']}/100, provide feedback.

## Scores
- Methodology: {consensus['methodology']}/30
- Synthesis: {consensus['synthesis']}/30
- Presentation: {consensus['presentation']}/20
- Contribution: {consensus['contribution']}/20

## Content Preview
{content[:3000]}

## Output JSON
{{
    "issues": [
        {{"category": "methodology|synthesis|presentation|contribution", "severity": "major|minor", "description": "issue description", "location": "where in text", "suggestion": "how to fix"}}
    ],
    "strengths": ["list of 2-4 strengths"],
    "suggestions": ["list of 3-5 actionable improvement suggestions"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"issues": [], "strengths": [], "suggestions": []}
    
    def _determine_verdict(self, score: int) -> QualityVerdict:
        """Determine verdict based on score."""
        thresholds = self.context.quality_thresholds
        return thresholds.get_verdict(score)
    
    async def _quick_check(
        self,
        content: str,
        focus: str = "overall",
        **kwargs
    ) -> dict:
        """Quick quality check without full evaluation."""
        
        prompt = f"""Quick quality check of this content focusing on {focus}:

{content[:2000]}

Rate 1-10 and give one-line assessment:
{{
    "score": <1-10>,
    "assessment": "one line",
    "critical_issue": "most important issue if any"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=200,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"score": 5, "assessment": "Unable to assess", "critical_issue": None}
    
    async def _compare_versions(
        self,
        version_a: str,
        version_b: str,
        **kwargs
    ) -> dict:
        """Compare two versions of content."""
        
        prompt = f"""Compare these two versions and determine which is better:

## Version A
{version_a[:2000]}

## Version B
{version_b[:2000]}

## Output JSON
{{
    "better_version": "A" or "B",
    "improvement_areas": ["what B does better than A"],
    "regression_areas": ["what B does worse than A"],
    "recommendation": "brief recommendation"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=500,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"better_version": "A", "improvement_areas": [], "regression_areas": []}
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add evaluator-specific metadata."""
        if isinstance(result.output, dict):
            result.quality_score = result.output.get("overall_score", 0)
            result.confidence = result.output.get("confidence", 0.7)
            result.handoff_data = {
                "evaluation_ready": True,
                "verdict": result.output.get("verdict", "unknown"),
                "issues_count": len(result.output.get("issues", []))
            }
            
            # Suggest next agents based on issues
            issues = result.output.get("issues", [])
            categories = set(i.get("category") for i in issues)
            
            if "methodology" in categories:
                result.suggested_next_agents.append("methodology_validator")
            if "presentation" in categories:
                result.suggested_next_agents.append("academic_editor")
        
        return result
