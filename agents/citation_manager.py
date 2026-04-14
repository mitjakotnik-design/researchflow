"""Citation Manager Agent: Manages references and citations."""

import json
import re
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class CitationManagerAgent(BaseAgent):
    """
    Agent responsible for citation management.
    
    Capabilities:
    - Track citations
    - Verify citation accuracy
    - Check citation coverage
    - Format references
    """
    
    def __init__(self):
        super().__init__(
            name="citation_manager",
            role=AgentRole.WRITING,
            description="Manages references and citations",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._citations: dict[str, dict] = {}
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute citation manager actions."""
        if action == "check":
            return await self._check_citations(**kwargs)
        elif action == "extract":
            return await self._extract_citations(**kwargs)
        elif action == "verify":
            return await self._verify_citations(**kwargs)
        elif action == "format":
            return await self._format_references(**kwargs)
        elif action == "finalize":
            return await self._finalize_citations(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _check_citations(
        self,
        content: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Check citation quality and coverage."""
        
        if not content:
            all_content = []
            for section_state in self.state.sections.values():
                if section_state.content:
                    all_content.append(section_state.content)
            content = "\n\n".join(all_content)
        
        if not content:
            return {"error": "No content to check"}
        
        # Extract citations
        citations = await self._extract_citations(content=content)
        
        # Calculate coverage
        paragraphs = content.split("\n\n")
        paragraphs_with_citations = 0
        
        for para in paragraphs:
            if len(para) > 100:  # Skip short paragraphs
                if re.search(r'\[[\w\s,&]+,\s*\d{4}\]|\(\w+\s+et\s+al\.,?\s*\d{4}\)', para):
                    paragraphs_with_citations += 1
        
        total_paragraphs = len([p for p in paragraphs if len(p) > 100])
        coverage = paragraphs_with_citations / total_paragraphs if total_paragraphs > 0 else 0
        
        # Calculate density
        word_count = len(content.split())
        citation_count = len(citations.get("citations", []))
        density = (citation_count / (word_count / 250)) if word_count > 0 else 0  # per 250 words
        
        self.log.info(
            "citation_check_completed",
            citations_found=citation_count,
            coverage=f"{coverage:.1%}"
        )
        
        return {
            "citation_count": citation_count,
            "coverage_percentage": round(coverage * 100, 1),
            "density_per_paragraph": round(density, 2),
            "citations": citations.get("citations", []),
            "issues": citations.get("issues", []),
            "coverage_adequate": coverage >= 0.7,
            "density_adequate": 1.5 <= density <= 6.0
        }
    
    async def _extract_citations(
        self,
        content: str,
        **kwargs
    ) -> dict:
        """Extract citations from content."""
        
        # Pattern for various citation formats
        patterns = [
            r'\[([^\]]+,\s*\d{4}[a-z]?)\]',  # [Author, 2020]
            r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?(?:\s+&\s+[A-Z][a-z]+)?,\s*\d{4}[a-z]?)\)',  # (Author et al., 2020)
            r'\(([A-Z][a-z]+\s+and\s+[A-Z][a-z]+,\s*\d{4})\)',  # (Author and Author, 2020)
        ]
        
        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            citations.extend(matches)
        
        # Deduplicate and standardize
        unique_citations = list(set(citations))
        
        # Identify potential issues
        issues = []
        
        # Check for self-citation patterns
        # Check for missing years
        for cite in unique_citations:
            if not re.search(r'\d{4}', cite):
                issues.append(f"Citation missing year: {cite}")
            if "et al" in cite.lower() and "." not in cite:
                issues.append(f"Missing period after 'et al': {cite}")
        
        self._citations = {c: {"count": citations.count(c)} for c in unique_citations}
        
        return {
            "citations": unique_citations,
            "total_count": len(citations),
            "unique_count": len(unique_citations),
            "issues": issues
        }
    
    async def _verify_citations(
        self,
        citations: list[str],
        **kwargs
    ) -> dict:
        """Verify citations against sources."""
        
        # This would typically check against a reference database
        # For now, do format verification
        
        verified = []
        problematic = []
        
        for cite in citations:
            # Check basic format
            if re.match(r'^[A-Z][a-z]+', cite):
                if re.search(r'\d{4}', cite):
                    verified.append(cite)
                else:
                    problematic.append({"citation": cite, "issue": "Missing year"})
            else:
                problematic.append({"citation": cite, "issue": "Invalid format"})
        
        return {
            "verified": verified,
            "problematic": problematic,
            "verification_rate": len(verified) / len(citations) if citations else 0
        }
    
    async def _format_references(
        self,
        style: str = "APA7",
        **kwargs
    ) -> str:
        """Format reference list."""
        
        if not self._citations:
            return "No citations extracted yet."
        
        prompt = f"""Format these citations as a reference list in {style} style:

## Citations
{chr(10).join(self._citations.keys())}

## Output
Return formatted reference list entries.
Each entry should be on a new line.
Sort alphabetically by first author."""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=len(self._citations) * 100
        )
        
        return response.content.strip()
    
    async def _finalize_citations(self, **kwargs) -> dict:
        """Finalize citations for all sections."""
        
        results = {
            "sections_processed": 0,
            "total_citations": 0,
            "issues_found": []
        }
        
        for section_id, section_state in self.state.sections.items():
            if section_state.content:
                check_result = await self._check_citations(content=section_state.content)
                results["sections_processed"] += 1
                results["total_citations"] += check_result.get("citation_count", 0)
                
                for issue in check_result.get("issues", []):
                    results["issues_found"].append({
                        "section": section_id,
                        "issue": issue
                    })
        
        # Generate reference list
        if self._citations:
            results["reference_list"] = await self._format_references()
        
        self.log.info(
            "citations_finalized",
            sections=results["sections_processed"],
            citations=results["total_citations"]
        )
        
        return results
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add citation manager metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "citations_checked": True,
                "citation_count": result.output.get("citation_count", 0),
                "coverage_adequate": result.output.get("coverage_adequate", False)
            }
        return result
