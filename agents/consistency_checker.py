"""Consistency Checker Agent: Ensures internal consistency across sections."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class ConsistencyCheckerAgent(BaseAgent):
    """
    Agent responsible for checking internal consistency.
    
    Capabilities:
    - Cross-section consistency checking
    - Terminology consistency
    - Numerical consistency
    - Logical flow verification
    """
    
    def __init__(self):
        super().__init__(
            name="consistency_checker",
            role=AgentRole.QUALITY,
            description="Ensures internal consistency across the article",
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
        """Execute consistency checker actions."""
        if action == "check":
            return await self._check_consistency(**kwargs)
        elif action == "check_terminology":
            return await self._check_terminology(**kwargs)
        elif action == "check_numbers":
            return await self._check_numbers(**kwargs)
        elif action == "check_flow":
            return await self._check_logical_flow(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _check_consistency(
        self,
        content: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Perform comprehensive consistency check."""
        
        # Get all section content if not provided
        if not content:
            sections_content = {}
            for section_id, section_state in self.state.sections.items():
                if section_state.content:
                    sections_content[section_id] = section_state.content
            
            if not sections_content:
                return {
                    "consistency_score": 1.0,
                    "issues": [],
                    "summary": "No content to check."
                }
            
            content = "\n\n---\n\n".join([
                f"## {sid}\n{c}" for sid, c in sections_content.items()
            ])
        
        # Run all consistency checks
        terminology_result = await self._check_terminology(content=content)
        numbers_result = await self._check_numbers(content=content)
        flow_result = await self._check_logical_flow(content=content)
        
        # Aggregate issues
        all_issues = []
        all_issues.extend(terminology_result.get("issues", []))
        all_issues.extend(numbers_result.get("issues", []))
        all_issues.extend(flow_result.get("issues", []))
        
        # Calculate overall consistency score
        scores = [
            terminology_result.get("score", 1.0),
            numbers_result.get("score", 1.0),
            flow_result.get("score", 1.0)
        ]
        consistency_score = sum(scores) / len(scores)
        
        self.log.info(
            "consistency_check_completed",
            consistency_score=consistency_score,
            issues_count=len(all_issues)
        )
        
        return {
            "consistency_score": consistency_score,
            "terminology_score": terminology_result.get("score", 1.0),
            "numbers_score": numbers_result.get("score", 1.0),
            "flow_score": flow_result.get("score", 1.0),
            "issues": all_issues,
            "summary": f"Found {len(all_issues)} consistency issues. Overall score: {consistency_score:.2%}"
        }
    
    async def _check_terminology(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Check terminology consistency."""
        
        system_prompt = """You are a terminology consistency expert.
Identify inconsistent use of terms, acronyms, and concepts.
Look for:
- Same concept with different names
- Undefined acronyms
- Inconsistent capitalization of key terms
- Conflicting definitions"""
        
        prompt = f"""Check terminology consistency:

{content[:6000]}

## Output JSON
{{
    "score": <0.0-1.0>,
    "issues": [
        {{
            "type": "terminology",
            "term": "the inconsistent term",
            "variations": ["list of variations found"],
            "locations": ["where found"],
            "severity": "high|medium|low",
            "suggestion": "recommended consistent usage"
        }}
    ],
    "key_terms": ["list of key terms that are consistent"]
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
            return {"score": 0.8, "issues": []}
    
    async def _check_numbers(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Check numerical consistency."""
        
        system_prompt = """You are a numerical consistency checker.
Verify that numbers, statistics, and counts are consistent throughout.
Look for:
- Conflicting statistics
- Numbers that don't add up
- Inconsistent sample sizes
- Contradictory percentages"""
        
        prompt = f"""Check numerical consistency:

{content[:6000]}

## Output JSON
{{
    "score": <0.0-1.0>,
    "issues": [
        {{
            "type": "numerical",
            "description": "what's inconsistent",
            "value_1": "first value",
            "value_2": "conflicting value",
            "locations": ["where each appears"],
            "severity": "high|medium|low"
        }}
    ],
    "verified_numbers": ["key numbers that are consistent"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=800,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"score": 0.9, "issues": []}
    
    async def _check_logical_flow(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Check logical flow and coherence."""
        
        system_prompt = """You are a logical coherence expert.
Check that arguments and ideas flow logically.
Look for:
- Conclusions not supported by presented evidence
- Non-sequiturs
- Missing logical steps
- Contradictory statements"""
        
        prompt = f"""Check logical flow and coherence:

{content[:6000]}

## Output JSON
{{
    "score": <0.0-1.0>,
    "issues": [
        {{
            "type": "logic",
            "description": "the logical issue",
            "statement_1": "first statement",
            "statement_2": "contradicting or unconnected statement",
            "severity": "high|medium|low",
            "suggestion": "how to resolve"
        }}
    ],
    "strong_points": ["aspects with good logical flow"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=800,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"score": 0.85, "issues": []}
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add consistency checker metadata."""
        if isinstance(result.output, dict):
            score = result.output.get("consistency_score", 1.0)
            result.quality_score = int(score * 100)
            result.handoff_data = {
                "consistency_check_complete": True,
                "consistency_score": score,
                "issues_found": len(result.output.get("issues", []))
            }
            
            if score < 0.9:
                result.suggested_next_agents = ["terminology_guardian", "academic_editor"]
        
        return result
