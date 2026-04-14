"""Fact Checker Agent: Verifies claims against source literature."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class FactCheckerAgent(BaseAgent):
    """
    Agent responsible for verifying factual claims.
    
    Capabilities:
    - Extract claims from text
    - Verify claims against RAG sources
    - Identify unsupported or contradicted claims
    - Generate verification report
    """
    
    def __init__(self):
        super().__init__(
            name="fact_checker",
            role=AgentRole.QUALITY,
            description="Verifies factual claims against source literature",
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
        """Execute fact checker actions."""
        if action == "check":
            return await self._check_facts(**kwargs)
        elif action == "extract_claims":
            return await self._extract_claims(**kwargs)
        elif action == "verify_claim":
            return await self._verify_single_claim(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _check_facts(
        self,
        content: str,
        strict: bool = False,
        **kwargs
    ) -> dict:
        """Check all factual claims in content."""
        
        # Extract claims
        claims = await self._extract_claims(content=content)
        
        if not claims:
            return {
                "total": 0,
                "verified": 0,
                "unverified": 0,
                "contradicted": 0,
                "claims": [],
                "summary": "No verifiable claims found."
            }
        
        # Verify each claim
        results = []
        verified = 0
        unverified = 0
        contradicted = 0
        
        for claim in claims:
            result = await self._verify_single_claim(
                claim=claim["claim"],
                context=claim.get("context", "")
            )
            
            results.append({
                **claim,
                "verification": result
            })
            
            status = result.get("status", "unverified")
            if status == "verified":
                verified += 1
            elif status == "contradicted":
                contradicted += 1
            else:
                unverified += 1
        
        # Generate summary
        total = len(claims)
        pass_rate = verified / total if total > 0 else 0
        
        summary = f"Checked {total} claims: {verified} verified ({pass_rate:.0%}), "
        summary += f"{unverified} unverified, {contradicted} contradicted."
        
        self.log.info(
            "fact_check_completed",
            total=total,
            verified=verified,
            unverified=unverified,
            contradicted=contradicted
        )
        
        return {
            "total": total,
            "verified": verified,
            "unverified": unverified,
            "contradicted": contradicted,
            "pass_rate": pass_rate,
            "claims": results,
            "summary": summary,
            "critical_issues": [
                c for c in results 
                if c["verification"].get("status") == "contradicted"
            ]
        }
    
    async def _extract_claims(
        self,
        content: str,
        max_claims: int = 20,
        **kwargs
    ) -> list[dict]:
        """Extract verifiable claims from content."""
        
        system_prompt = """You are a fact extraction specialist.
Identify specific, verifiable claims that can be checked against literature.
Focus on:
- Statistical claims (percentages, numbers)
- Research findings
- Causal relationships
- Definitions of terms
Skip opinions, hedged statements, and general knowledge."""
        
        prompt = f"""Extract verifiable claims from this text:

{content[:5000]}

## Output JSON
[
    {{
        "claim": "The specific claim text",
        "type": "statistical|finding|causal|definitional",
        "citation_present": true/false,
        "importance": "high|medium|low",
        "context": "surrounding context"
    }}
]

Extract up to {max_claims} most important claims."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            claims = json.loads(response.content)
            return claims if isinstance(claims, list) else []
        except json.JSONDecodeError:
            return []
    
    async def _verify_single_claim(
        self,
        claim: str,
        context: str = "",
        **kwargs
    ) -> dict:
        """Verify a single claim against sources."""
        
        # Search for supporting evidence
        if self.context.rag_query:
            evidence = await self.query_rag(
                query=f"Evidence for: {claim}",
                top_k=5
            )
        else:
            evidence = []
        
        if not evidence:
            return {
                "status": "unverified",
                "confidence": 0.0,
                "reason": "No relevant sources found",
                "sources": []
            }
        
        # Evaluate evidence
        evidence_text = "\n\n".join([
            f"Source {i+1}: {e.get('content', '')[:400]}"
            for i, e in enumerate(evidence[:3])
        ])
        
        prompt = f"""Verify this claim against the sources:

## Claim
{claim}

## Context
{context}

## Sources
{evidence_text}

## Output JSON
{{
    "status": "verified" | "partially_verified" | "unverified" | "contradicted",
    "confidence": <0.0-1.0>,
    "reason": "explanation",
    "supporting_quotes": ["relevant quotes from sources"],
    "contradicting_quotes": ["if any contradict the claim"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=500,
            json_mode=True
        )
        
        try:
            result = json.loads(response.content)
            result["sources"] = [e.get("source", "") for e in evidence[:3]]
            return result
        except json.JSONDecodeError:
            return {
                "status": "unverified",
                "confidence": 0.0,
                "reason": "Verification failed",
                "sources": []
            }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add fact checker metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "fact_check_complete": True,
                "pass_rate": result.output.get("pass_rate", 0),
                "critical_issues": len(result.output.get("critical_issues", []))
            }
            
            # Need revision if contradicted claims exist
            if result.output.get("contradicted", 0) > 0:
                result.suggested_next_agents = ["writer"]
                result.suggested_actions = ["Revise contradicted claims"]
        
        return result
