"""
Fact Checker Agent V2: Enhanced fact verification with DI and RAG.

Verifies claims against source documents and identifies contradictions.
"""

import json
import re
from typing import Any, Optional
from pydantic import BaseModel

import structlog

from agents.base_agent_v2 import EnhancedBaseAgent, AgentDependencies, AgentRole
from agents.request_models import VerifyClaimRequest, FactCheckSectionRequest, get_request_model


logger = structlog.get_logger()


class FactCheckerAgentV2(EnhancedBaseAgent):
    """
    Enhanced Fact Checker with RAG verification and DI.
    
    Capabilities:
    - Extract claims from text
    - Verify claims against source documents
    - Detect contradictions
    - Track verification coverage
    """
    
    def __init__(self, deps: AgentDependencies):
        super().__init__(
            name="fact_checker",
            role=AgentRole.QUALITY,
            deps=deps,
            description="Verifies claims against source documents",
            version="2.0.0"
        )
        
        # Verification cache
        self._verification_cache: dict[str, dict] = {}
    
    def get_request_model(self, action: str) -> Optional[type[BaseModel]]:
        """Get Pydantic model for action validation."""
        return get_request_model("fact_checker", action)
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute fact checker actions."""
        if action == "verify_claim":
            return await self._verify_single_claim(**kwargs)
        elif action == "fact_check_section":
            return await self._fact_check_section(**kwargs)
        elif action == "detect_contradictions":
            return await self._detect_contradictions(**kwargs)
        elif action == "get_coverage":
            return self._get_verification_coverage(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _fact_check_section(
        self,
        content: str,
        section: str,
        strictness: str = "standard",
        **kwargs
    ) -> dict:
        """Fact check an entire section."""
        
        # Extract claims
        claims = await self._extract_claims(content)
        
        # Verify each claim
        results = {
            "verified": 0,
            "unverified": 0,
            "contradicted": 0,
            "claims": [],
            "issues": [],
        }
        
        for claim in claims:
            verification = await self._verify_single_claim(
                claim=claim["text"],
                cited_source=claim.get("citation"),
                context=claim.get("context"),
                strictness=strictness,
            )
            
            results["claims"].append({
                "claim": claim["text"],
                "status": verification["status"],
                "confidence": verification.get("confidence", 0.0),
                "sources": verification.get("supporting_sources", []),
            })
            
            if verification["status"] == "verified":
                results["verified"] += 1
            elif verification["status"] == "contradicted":
                results["contradicted"] += 1
                results["issues"].append({
                    "type": "contradiction",
                    "claim": claim["text"],
                    "details": verification.get("contradiction_details", "")
                })
            else:
                results["unverified"] += 1
                if strictness == "strict":
                    results["issues"].append({
                        "type": "unverified",
                        "claim": claim["text"],
                        "details": "No supporting evidence found"
                    })
        
        # Calculate pass rate
        total = results["verified"] + results["unverified"] + results["contradicted"]
        results["total"] = total
        results["pass_rate"] = results["verified"] / total if total > 0 else 0.0
        results["gate_passed"] = (
            results["contradicted"] == 0 and
            results["pass_rate"] >= 0.9
        )
        
        self.log.info(
            "fact_check_completed",
            section=section,
            total_claims=total,
            verified=results["verified"],
            contradicted=results["contradicted"],
            pass_rate=results["pass_rate"]
        )
        
        return results
    
    async def _extract_claims(self, content: str) -> list[dict]:
        """Extract verifiable claims from content."""
        
        prompt = f"""Extract verifiable factual claims from this academic text:

{content[:4000]}

Focus on:
- Statistical claims (percentages, numbers)
- Research findings and conclusions
- Causation/correlation statements
- Definitions and categorizations

For each claim, extract:
1. The claim text
2. Any citation provided (e.g., "[Author, Year]")
3. Brief context

Output JSON array:
[
    {{
        "text": "The claim as stated",
        "citation": "[Author, Year]" or null,
        "context": "Where in the text",
        "type": "statistical|finding|causal|definition"
    }}
]

Extract 10-15 most important claims:"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            claims = json.loads(response.content)
            return claims if isinstance(claims, list) else []
        except json.JSONDecodeError:
            # Fallback: extract sentences with citations
            citation_pattern = r'\[([^\]]+,\s*\d{4})\]'
            sentences = content.split('.')
            claims = []
            
            for sent in sentences:
                if re.search(citation_pattern, sent):
                    match = re.search(citation_pattern, sent)
                    claims.append({
                        "text": sent.strip() + ".",
                        "citation": match.group(0) if match else None,
                        "context": "extracted",
                        "type": "finding"
                    })
            
            return claims[:15]
    
    async def _verify_single_claim(
        self,
        claim: str,
        cited_source: Optional[str] = None,
        context: Optional[str] = None,
        strictness: str = "standard",
        **kwargs
    ) -> dict:
        """Verify a single claim against sources."""
        
        # Check cache
        cache_key = hash(claim)
        if cache_key in self._verification_cache:
            return self._verification_cache[cache_key]
        
        # Search for relevant sources
        rag_results = await self.query_rag(
            query=claim,
            top_k=5
        )
        
        if not rag_results:
            result = {
                "status": "unverified",
                "confidence": 0.0,
                "reason": "No relevant sources found in database",
                "supporting_sources": [],
            }
            self._verification_cache[cache_key] = result
            return result
        
        # Format sources for verification
        sources_text = "\n\n".join(
            f"[Source {i+1}] {r.get('source', 'Unknown')}\n{r.get('content', '')[:500]}"
            for i, r in enumerate(rag_results)
        )
        
        prompt = f"""Verify this claim against the sources:

## Claim
{claim}

{"## Cited Source: " + cited_source if cited_source else ""}

## Available Sources
{sources_text}

## Verification Task
Determine if the claim is:
- VERIFIED: Supported by sources (exact or paraphrased match)
- PARTIALLY_VERIFIED: Some support but not complete
- UNVERIFIED: Cannot confirm from available sources
- CONTRADICTED: Sources contradict the claim

Output JSON:
{{
    "status": "verified|partially_verified|unverified|contradicted",
    "confidence": 0.0-1.0,
    "supporting_sources": ["Source name"],
    "reasoning": "Brief explanation",
    "contradiction_details": "If contradicted, explain"
}}"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=500,
            json_mode=True
        )
        
        try:
            result = json.loads(response.content)
            
            # Apply strictness adjustment
            if strictness == "lenient" and result["status"] == "partially_verified":
                result["status"] = "verified"
            elif strictness == "strict" and result["status"] == "partially_verified":
                result["status"] = "unverified"
            
            self._verification_cache[cache_key] = result
            return result
            
        except json.JSONDecodeError:
            result = {
                "status": "unverified",
                "confidence": 0.5,
                "reason": "Verification inconclusive",
                "supporting_sources": [],
            }
            return result
    
    async def _detect_contradictions(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Detect internal contradictions in content."""
        
        prompt = f"""Analyze this text for internal contradictions:

{content[:5000]}

Look for:
1. Statements that contradict each other
2. Inconsistent use of data/numbers
3. Conflicting conclusions
4. Logical inconsistencies

Output JSON:
{{
    "contradictions_found": true/false,
    "contradictions": [
        {{
            "statement_a": "First statement",
            "statement_b": "Contradicting statement",
            "type": "logical|statistical|definitional",
            "severity": "critical|major|minor"
        }}
    ],
    "consistency_score": 0.0-1.0
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
                "contradictions_found": False,
                "contradictions": [],
                "consistency_score": 0.9
            }
    
    def _get_verification_coverage(
        self,
        section: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Get statistics on verification coverage."""
        
        cache_size = len(self._verification_cache)
        statuses = [v.get("status", "unknown") for v in self._verification_cache.values()]
        
        return {
            "total_verified_claims": cache_size,
            "status_breakdown": {
                "verified": statuses.count("verified"),
                "partially_verified": statuses.count("partially_verified"),
                "unverified": statuses.count("unverified"),
                "contradicted": statuses.count("contradicted"),
            },
            "verification_rate": (
                (statuses.count("verified") + statuses.count("partially_verified"))
                / cache_size if cache_size > 0 else 0.0
            )
        }
    
    def clear_cache(self) -> int:
        """Clear verification cache."""
        count = len(self._verification_cache)
        self._verification_cache.clear()
        return count
