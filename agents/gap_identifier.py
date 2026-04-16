"""Gap Identifier Agent: Identifies research gaps and future directions."""

import json
from typing import Any, Optional

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class GapIdentifierAgent(BaseAgent):
    """
    Agent responsible for identifying research gaps.
    
    Capabilities:
    - Identify knowledge gaps
    - Map unexplored areas
    - Suggest future research directions
    - Prioritize gaps by importance
    """
    
    def __init__(self):
        super().__init__(
            name="gap_identifier",
            role=AgentRole.RESEARCH,
            description="Identifies research gaps and future directions",
            version="1.0.0"
        )
        
        self._llm_client = None
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute gap identifier actions."""
        if action == "identify_gaps":
            return await self._identify_gaps(**kwargs)
        elif action == "map_coverage":
            return await self._map_coverage(**kwargs)
        elif action == "suggest_directions":
            return await self._suggest_research_directions(**kwargs)
        elif action == "prioritize":
            return await self._prioritize_gaps(**kwargs)
        elif action == "analyze_section_gaps":
            return await self._analyze_section_gaps(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _identify_gaps(
        self,
        synthesis: Optional[dict] = None,
        patterns: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Identify research gaps from synthesis."""
        
        # Get context from state if not provided
        context_parts = []
        
        if synthesis:
            context_parts.append(f"## Synthesis\n{json.dumps(synthesis, indent=2)[:2000]}")
        
        if patterns:
            context_parts.append(f"## Patterns\n{json.dumps(patterns, indent=2)[:1500]}")
        
        # Add article title for context
        context_parts.append(f"## Review Topic\n{self.state.title}")
        
        system_prompt = """You are a research gap analysis specialist.
Identify what is NOT known, NOT studied, or NOT well understood.
Focus on actionable gaps that future research could address.
Consider methodological, population, geographic, and conceptual gaps."""
        
        prompt = f"""Identify research gaps:

{chr(10).join(context_parts)}

## Output JSON
{{
    "knowledge_gaps": [
        {{
            "gap": "description of gap",
            "type": "methodological|population|geographic|conceptual|temporal",
            "importance": "high|medium|low",
            "addressable": true/false,
            "evidence": "how we know this is a gap"
        }}
    ],
    "understudied_areas": [
        {{
            "area": "understudied topic",
            "current_evidence": "what little is known",
            "needed_research": "what research is needed"
        }}
    ],
    "methodological_limitations": [
        "common methodological weaknesses across studies"
    ],
    "conflicting_evidence": [
        "areas where evidence is contradictory"
    ],
    "summary": "overall assessment of the state of knowledge"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            gaps = json.loads(response.content)
            
            # Prioritize gaps
            prioritized = await self._prioritize_gaps(gaps=gaps.get("knowledge_gaps", []))
            gaps["prioritized_gaps"] = prioritized
            
            self.log.info(
                "gaps_identified",
                knowledge_gaps=len(gaps.get("knowledge_gaps", [])),
                understudied_areas=len(gaps.get("understudied_areas", []))
            )
            
            return gaps
            
        except json.JSONDecodeError:
            return {"knowledge_gaps": [], "understudied_areas": [], "error": "Parse failed"}
    
    async def _map_coverage(
        self,
        extractions: Optional[list[dict]] = None,
        **kwargs
    ) -> dict:
        """Map what the literature covers vs. what's missing."""
        
        prompt = f"""Map research coverage for: {self.state.title}

Based on existing literature, create a coverage map.

## Output JSON
{{
    "well_covered": [
        {{"topic": "topic name", "evidence_level": "strong|moderate|limited"}}
    ],
    "partially_covered": [
        {{"topic": "topic", "gaps": "what's missing"}}
    ],
    "not_covered": [
        {{"topic": "topic", "importance": "why it matters"}}
    ],
    "coverage_score": <0.0-1.0>,
    "recommendations": ["what to prioritize in future research"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"coverage_score": 0.5, "well_covered": [], "not_covered": []}
    
    async def _suggest_research_directions(
        self,
        gaps: Optional[list[dict]] = None,
        **kwargs
    ) -> list[dict]:
        """Suggest future research directions based on gaps."""
        
        gaps_text = json.dumps(gaps[:10], indent=2) if gaps else "No specific gaps provided"
        
        prompt = f"""Suggest future research directions based on these gaps:

{gaps_text}

## Review Topic
{self.state.title}

## Output JSON
[
    {{
        "direction": "research direction title",
        "rationale": "why this is important",
        "methodology_suggestions": ["suggested approaches"],
        "priority": "high|medium|low",
        "feasibility": "high|medium|low",
        "expected_impact": "potential contribution"
    }}
]

Suggest 5-8 research directions."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1200,
            json_mode=True
        )
        
        try:
            directions = json.loads(response.content)
            return directions if isinstance(directions, list) else []
        except json.JSONDecodeError:
            return []
    
    async def _prioritize_gaps(
        self,
        gaps: list[dict],
        **kwargs
    ) -> list[dict]:
        """Prioritize gaps by importance and addressability."""
        
        # Score each gap
        prioritized = []
        
        for gap in gaps:
            importance_score = {"high": 3, "medium": 2, "low": 1}.get(
                gap.get("importance", "medium"), 2
            )
            addressable_score = 2 if gap.get("addressable", True) else 1
            
            total_score = importance_score * addressable_score
            
            prioritized.append({
                **gap,
                "priority_score": total_score
            })
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        return prioritized[:10]  # Return top 10
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True
    )
    async def _analyze_section_gaps(
        self,
        section_id: str,
        content: str,
        score: float,
        quality_feedback: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """
        Analyze specific section for missing theoretical concepts or methodologies.
        
        This is targeted gap analysis for low-scoring article sections,
        focusing on identifying what specific literature should be added.
        
        Includes automatic retry logic (3 attempts) for LLM timeouts/connection errors.
        """
        
        # Build context from feedback
        feedback_text = ""
        if quality_feedback:
            weaknesses = quality_feedback.get("weaknesses", [])
            missing_elements = quality_feedback.get("missing_elements", [])
            
            if weaknesses:
                feedback_text += "\n## Identified Weaknesses:\n"
                feedback_text += "\n".join(f"- {w}" for w in weaknesses)
            
            if missing_elements:
                feedback_text += "\n## Missing Elements:\n"
                feedback_text += "\n".join(f"- {m}" for m in missing_elements)
        
        system_prompt = """You are a research literature gap specialist.
Analyze low-scoring article sections to identify SPECIFIC missing theoretical frameworks,
methodologies, or empirical evidence that should be added from literature.

Focus on:
- Missing theoretical frameworks (e.g., "Job Demands-Resources model")
- Missing methodologies (e.g., "PRISMA-ScR guidelines")
- Missing empirical evidence or seminal papers
- Key concepts that are not adequately supported by citations

Output should be ACTIONABLE - name specific theories, models, or research areas."""
        
        prompt = f"""Analyze this {section_id.upper()} section with score {score}/100:

## Section Content Preview (first 1000 chars):
{content[:1000]}

{feedback_text}

## Task
Identify SPECIFIC missing theoretical concepts, frameworks, methodologies, or research areas
that need to be added from literature to improve this section.

## Output JSON
{{
    "section_id": "{section_id}",
    "current_score": {score},
    "missing_theories": [
        {{
            "theory_name": "e.g., Job Demands-Resources Model",
            "why_needed": "why this theory is essential for this section",
            "search_terms": ["alternative names for this theory"],
            "expected_impact": "how adding this will improve the section"
        }}
    ],
    "missing_methodologies": [
        {{
            "methodology_name": "e.g., PRISMA-ScR guidelines",
            "why_needed": "why needed",
            "search_terms": ["related terms"],
            "expected_impact": "improvement expected"
        }}
    ],
    "missing_empirical_evidence": [
        {{
            "research_area": "e.g., longitudinal studies on AI adoption",
            "why_needed": "gap description",
            "search_terms": ["search terms"],
            "expected_impact": "expected improvement"
        }}
    ],
    "priority": "high|medium|low",
    "estimated_improvement": <score increase expected, e.g., 25>,
    "rationale": "overall assessment of why score is low"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            gaps = json.loads(response.content)
            
            self.log.info(
                "section_gaps_analyzed",
                section=section_id,
                score=score,
                missing_theories=len(gaps.get("missing_theories", [])),
                missing_methodologies=len(gaps.get("missing_methodologies", [])),
                missing_evidence=len(gaps.get("missing_empirical_evidence", []))
            )
            
            return gaps
            
        except json.JSONDecodeError as e:
            self.log.error("section_gap_analysis_failed", section=section_id, error=str(e))
            return {
                "section_id": section_id,
                "current_score": score,
                "missing_theories": [],
                "missing_methodologies": [],
                "missing_empirical_evidence": [],
                "error": "Parse failed"
            }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add gap identifier metadata."""
        if isinstance(result.output, dict):
            gaps_count = len(result.output.get("knowledge_gaps", []))
            result.handoff_data = {
                "gaps_identified": True,
                "gaps_count": gaps_count,
                "high_priority_gaps": len([
                    g for g in result.output.get("prioritized_gaps", [])
                    if g.get("importance") == "high"
                ])
            }
            result.suggested_next_agents = ["writer"]
        return result
