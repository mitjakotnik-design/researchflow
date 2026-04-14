"""Bias Auditor Agent: Detects and reports potential biases."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory
from config import BiasRisk


logger = structlog.get_logger()


# Bias categories to check
BIAS_CATEGORIES = [
    ("selection_bias", "Systematic differences in how studies were selected"),
    ("publication_bias", "Over-representation of positive/significant results"),
    ("language_bias", "Exclusion of non-English publications"),
    ("citation_bias", "Self-citation or preferential citation patterns"),
    ("confirmation_bias", "Selective emphasis on supporting evidence"),
    ("framing_bias", "Biased presentation of findings"),
    ("outcome_reporting_bias", "Selective reporting of outcomes"),
    ("geographic_bias", "Over-representation of certain regions"),
]


class BiasAuditorAgent(BaseAgent):
    """
    Agent responsible for detecting and auditing bias.
    
    Capabilities:
    - Detect multiple bias types
    - Assess bias risk level
    - Generate mitigation recommendations
    - Track bias across iterations
    """
    
    def __init__(self):
        super().__init__(
            name="bias_auditor",
            role=AgentRole.QUALITY,
            description="Detects and reports potential biases in the review",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._audit_history: list[dict] = []
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute bias auditor actions."""
        if action == "audit":
            return await self._audit_bias(**kwargs)
        elif action == "check_category":
            return await self._check_bias_category(**kwargs)
        elif action == "suggest_mitigations":
            return await self._suggest_mitigations(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _audit_bias(
        self,
        content: str,
        section: Optional[str] = None,
        methodology_content: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Perform comprehensive bias audit."""
        
        # Check each bias category
        findings = []
        category_risks = {}
        
        for category, description in BIAS_CATEGORIES:
            result = await self._check_bias_category(
                content=content,
                category=category,
                description=description,
                methodology=methodology_content
            )
            
            findings.extend(result.get("findings", []))
            category_risks[category] = result.get("risk_level", "low")
        
        # Calculate overall risk
        risk_levels = list(category_risks.values())
        overall_risk = self._calculate_overall_risk(risk_levels)
        
        # Generate mitigations if needed
        mitigations = []
        if overall_risk in [BiasRisk.MODERATE, BiasRisk.HIGH, BiasRisk.CRITICAL]:
            mitigation_result = await self._suggest_mitigations(
                findings=findings,
                risk_level=overall_risk.value
            )
            mitigations = mitigation_result.get("mitigations", [])
        
        # Record audit
        audit_record = {
            "section": section,
            "overall_risk": overall_risk.value,
            "findings_count": len(findings),
            "category_risks": category_risks
        }
        self._audit_history.append(audit_record)
        
        self.log.info(
            "bias_audit_completed",
            overall_risk=overall_risk.value,
            findings_count=len(findings)
        )
        
        return {
            "risk_level": overall_risk.value,
            "category_risks": category_risks,
            "findings": findings,
            "mitigations": mitigations,
            "summary": self._generate_summary(overall_risk, findings, category_risks)
        }
    
    async def _check_bias_category(
        self,
        content: str,
        category: str,
        description: str,
        methodology: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Check for a specific bias category."""
        
        system_prompt = f"""You are a bias detection specialist focusing on {category}.
{description}
Analyze the text for indicators of this bias type.
Be specific about evidence of bias."""
        
        method_context = ""
        if methodology:
            method_context = f"\n## Methodology Section\n{methodology[:1500]}"
        
        prompt = f"""Analyze for {category}:

## Content
{content[:4000]}
{method_context}

## Output JSON
{{
    "risk_level": "low" | "moderate" | "high" | "critical",
    "confidence": <0.0-1.0>,
    "findings": [
        {{
            "category": "{category}",
            "indicator": "specific bias indicator found",
            "evidence": "quote or description from text",
            "severity": "low|medium|high",
            "location": "where in text"
        }}
    ],
    "mitigating_factors": ["factors that reduce bias risk"]
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
            return {"risk_level": "low", "findings": [], "confidence": 0.5}
    
    async def _suggest_mitigations(
        self,
        findings: list[dict],
        risk_level: str,
        **kwargs
    ) -> dict:
        """Suggest bias mitigations."""
        
        findings_text = json.dumps(findings[:10], indent=2)
        
        prompt = f"""Suggest mitigations for these bias findings:

Risk Level: {risk_level}

Findings:
{findings_text}

## Output JSON
{{
    "mitigations": [
        {{
            "category": "which bias category",
            "action": "specific action to take",
            "priority": "high|medium|low",
            "implementation": "how to implement"
        }}
    ],
    "general_recommendations": ["overall recommendations"],
    "disclosure_suggestions": ["what to disclose in limitations"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=800,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"mitigations": [], "general_recommendations": [], "disclosure_suggestions": []}
    
    def _calculate_overall_risk(self, risk_levels: list[str]) -> BiasRisk:
        """Calculate overall risk from category risks."""
        risk_map = {
            "low": 0,
            "moderate": 1,
            "high": 2,
            "critical": 3
        }
        
        risks = [risk_map.get(r, 0) for r in risk_levels]
        
        # Use max with a weighted average consideration
        max_risk = max(risks) if risks else 0
        avg_risk = sum(risks) / len(risks) if risks else 0
        
        # If multiple high risks, escalate
        high_count = sum(1 for r in risks if r >= 2)
        if high_count >= 3:
            overall = min(max_risk + 1, 3)
        elif avg_risk > 1.5:
            overall = max(max_risk, 2)
        else:
            overall = max_risk
        
        risk_reverse = {0: BiasRisk.LOW, 1: BiasRisk.MODERATE, 2: BiasRisk.HIGH, 3: BiasRisk.CRITICAL}
        return risk_reverse.get(overall, BiasRisk.LOW)
    
    def _generate_summary(
        self,
        overall_risk: BiasRisk,
        findings: list[dict],
        category_risks: dict[str, str]
    ) -> str:
        """Generate human-readable summary."""
        
        high_risk = [cat for cat, risk in category_risks.items() if risk in ["high", "critical"]]
        
        summary = f"Overall bias risk: {overall_risk.value.upper()}. "
        summary += f"Found {len(findings)} potential bias indicators. "
        
        if high_risk:
            summary += f"High-risk categories: {', '.join(high_risk)}. "
        
        if overall_risk in [BiasRisk.HIGH, BiasRisk.CRITICAL]:
            summary += "Immediate attention recommended."
        elif overall_risk == BiasRisk.MODERATE:
            summary += "Consider addressing in limitations section."
        else:
            summary += "Bias risk is acceptable."
        
        return summary
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add bias auditor metadata."""
        if isinstance(result.output, dict):
            risk = result.output.get("risk_level", "low")
            
            try:
                bias_risk = BiasRisk(risk)
            except ValueError:
                bias_risk = BiasRisk.LOW
            
            result.handoff_data = {
                "bias_audit_complete": True,
                "risk_level": risk,
                "findings_count": len(result.output.get("findings", [])),
                "needs_mitigation": risk in ["high", "critical"]
            }
            
            if bias_risk in [BiasRisk.HIGH, BiasRisk.CRITICAL]:
                result.suggested_next_agents = ["writer", "methodology_validator"]
                result.suggested_actions = result.output.get("mitigations", [])[:3]
        
        return result
