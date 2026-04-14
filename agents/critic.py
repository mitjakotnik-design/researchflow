"""Critic Agent: Provides critical analysis and constructive feedback."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class CriticAgent(BaseAgent):
    """
    Agent responsible for critical analysis.
    
    Capabilities:
    - Identify weaknesses
    - Evaluate arguments
    - Suggest improvements
    - Challenge assumptions
    """
    
    def __init__(self):
        super().__init__(
            name="critic",
            role=AgentRole.QUALITY,
            description="Provides critical analysis and constructive feedback",
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
        """Execute critic actions."""
        if action == "critique":
            return await self._critique_content(**kwargs)
        elif action == "evaluate_arguments":
            return await self._evaluate_arguments(**kwargs)
        elif action == "identify_weaknesses":
            return await self._identify_weaknesses(**kwargs)
        elif action == "suggest_improvements":
            return await self._suggest_improvements(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _critique_content(
        self,
        content: str,
        section: Optional[str] = None,
        focus: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Provide critical analysis of content."""
        
        system_prompt = """You are a rigorous academic critic and peer reviewer.
Provide constructive but thorough criticism.
Focus on:
- Logical coherence
- Evidence quality
- Argument strength
- Clarity of presentation
- Contribution to field
Be specific and actionable in your feedback."""
        
        focus_text = f"\n## Focus Area: {focus}" if focus else ""
        section_text = f" ({section} section)" if section else ""
        
        prompt = f"""Critically analyze this academic text{section_text}:

{content[:5000]}
{focus_text}

## Output JSON
{{
    "overall_assessment": "summary of main strengths and weaknesses",
    "strengths": [
        {{"point": "what works well", "evidence": "specific example"}}
    ],
    "weaknesses": [
        {{
            "issue": "problem identified",
            "severity": "major|moderate|minor",
            "location": "where in text",
            "impact": "why this matters",
            "suggestion": "how to address"
        }}
    ],
    "argument_quality": {{
        "coherence": <1-10>,
        "evidence_support": <1-10>,
        "originality": <1-10>,
        "clarity": <1-10>
    }},
    "critical_questions": ["questions the author should address"],
    "improvement_priorities": ["ordered list of what to fix first"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            critique = json.loads(response.content)
            
            # Calculate overall score
            quality = critique.get("argument_quality", {})
            if quality:
                scores = [v for v in quality.values() if isinstance(v, (int, float))]
                critique["overall_score"] = sum(scores) * 2.5 if scores else 0  # Scale to 100
            
            self.log.info(
                "critique_completed",
                section=section,
                weaknesses_found=len(critique.get("weaknesses", []))
            )
            
            return critique
            
        except json.JSONDecodeError:
            return {
                "overall_assessment": response.content,
                "weaknesses": [],
                "error": "Parsing failed"
            }
    
    async def _evaluate_arguments(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Evaluate argument quality and logic."""
        
        prompt = f"""Evaluate the arguments in this academic text:

{content[:4000]}

## Output JSON
{{
    "main_arguments": [
        {{
            "argument": "the claim being made",
            "premises": ["supporting premises"],
            "evidence_provided": "type of evidence",
            "logical_validity": true/false,
            "strength": "strong|moderate|weak",
            "issues": ["any logical problems"]
        }}
    ],
    "logical_fallacies": [
        {{"fallacy": "name", "location": "where", "explanation": "why"}}
    ],
    "unsupported_claims": ["claims without evidence"],
    "overall_logic_score": <1-10>
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1200,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"main_arguments": [], "overall_logic_score": 5}
    
    async def _identify_weaknesses(
        self,
        content: str,
        **kwargs
    ) -> list[dict]:
        """Identify specific weaknesses."""
        
        prompt = f"""Identify weaknesses in this academic text:

{content[:4000]}

## Categories to Check
- Methodology rigor
- Evidence quality
- Logical coherence
- Literature coverage
- Writing clarity
- Contribution significance

## Output JSON
[
    {{
        "category": "category name",
        "weakness": "description",
        "severity": "critical|major|moderate|minor",
        "quote": "relevant text excerpt",
        "recommendation": "how to fix"
    }}
]"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            weaknesses = json.loads(response.content)
            return weaknesses if isinstance(weaknesses, list) else []
        except json.JSONDecodeError:
            return []
    
    async def _suggest_improvements(
        self,
        weaknesses: list[dict],
        **kwargs
    ) -> list[dict]:
        """Generate improvement suggestions."""
        
        if not weaknesses:
            return []
        
        weaknesses_text = json.dumps(weaknesses[:10], indent=2)
        
        prompt = f"""Generate specific improvements for these weaknesses:

{weaknesses_text}

## Output JSON
[
    {{
        "weakness_addressed": "which weakness",
        "improvement": "specific action to take",
        "priority": "high|medium|low",
        "effort": "low|medium|high",
        "impact": "expected improvement"
    }}
]"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=800,
            json_mode=True
        )
        
        try:
            improvements = json.loads(response.content)
            return improvements if isinstance(improvements, list) else []
        except json.JSONDecodeError:
            return []
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add critic metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "critique_complete": True,
                "weaknesses_count": len(result.output.get("weaknesses", [])),
                "overall_score": result.output.get("overall_score", 0)
            }
            
            # High severity issues trigger revision
            major_issues = [
                w for w in result.output.get("weaknesses", [])
                if w.get("severity") in ["critical", "major"]
            ]
            if major_issues:
                result.suggested_next_agents = ["writer"]
                result.suggested_actions = [
                    w.get("suggestion", "") for w in major_issues[:3]
                ]
        
        return result
