"""Meta-Analyst Agent: Performs meta-analysis and statistical synthesis."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class MetaAnalystAgent(BaseAgent):
    """
    Agent responsible for meta-analysis and quantitative synthesis.
    
    Capabilities:
    - Analyze effect sizes and heterogeneity
    - Identify patterns across studies
    - Generate forest plot data
    - Assess publication bias
    """
    
    def __init__(self):
        super().__init__(
            name="meta_analyst",
            role=AgentRole.RESEARCH,
            description="Performs meta-analysis and statistical synthesis",
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
        """Execute meta-analyst actions."""
        if action == "analyze":
            return await self._analyze_studies(**kwargs)
        elif action == "identify_patterns":
            return await self._identify_patterns(**kwargs)
        elif action == "assess_heterogeneity":
            return await self._assess_heterogeneity(**kwargs)
        elif action == "generate_summary":
            return await self._generate_quantitative_summary(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _analyze_studies(
        self,
        extractions: Optional[list[dict]] = None,
        **kwargs
    ) -> dict:
        """Analyze extracted study data."""
        
        # Get extractions from state if not provided
        if not extractions:
            cache = self.state.research_cache
            extractions = list(cache.synthesis_cache.values()) if cache.synthesis_cache else []
        
        if not extractions:
            return {
                "analysis_possible": False,
                "reason": "No extraction data available"
            }
        
        # Identify patterns
        patterns = await self._identify_patterns(extractions=extractions)
        
        # Assess heterogeneity
        heterogeneity = await self._assess_heterogeneity(extractions=extractions)
        
        # Generate summary
        summary = await self._generate_quantitative_summary(
            extractions=extractions,
            patterns=patterns
        )
        
        self.log.info(
            "meta_analysis_completed",
            studies_analyzed=len(extractions),
            patterns_found=len(patterns.get("patterns", []))
        )
        
        return {
            "studies_analyzed": len(extractions),
            "patterns": patterns,
            "heterogeneity": heterogeneity,
            "summary": summary,
            "meta_analysis_feasible": heterogeneity.get("meta_analysis_appropriate", False)
        }
    
    async def _identify_patterns(
        self,
        extractions: list[dict],
        **kwargs
    ) -> dict:
        """Identify patterns across studies."""
        
        # Prepare summary of extractions
        studies_summary = []
        for i, ext in enumerate(extractions[:20], 1):
            chars = ext.get("study_characteristics", {})
            findings = ext.get("findings", {})
            studies_summary.append(
                f"Study {i}: {chars.get('study_design', 'Unknown')} - "
                f"{findings.get('main_findings', 'NR')[:200]}"
            )
        
        prompt = f"""Identify patterns across these studies:

## Studies
{chr(10).join(studies_summary)}

## Output JSON
{{
    "patterns": [
        {{
            "pattern": "description of pattern",
            "evidence_strength": "strong|moderate|weak",
            "studies_supporting": [1, 2, 3],
            "pattern_type": "methodological|finding|population|contextual"
        }}
    ],
    "contradictions": [
        {{
            "topic": "what studies disagree on",
            "studies": [1, 5],
            "nature": "description of contradiction"
        }}
    ],
    "gaps": ["areas where evidence is lacking"],
    "consensus_areas": ["areas of agreement"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"patterns": [], "contradictions": [], "gaps": []}
    
    async def _assess_heterogeneity(
        self,
        extractions: list[dict],
        **kwargs
    ) -> dict:
        """Assess heterogeneity across studies."""
        
        # Analyze study characteristics for heterogeneity
        designs = set()
        populations = set()
        countries = set()
        
        for ext in extractions:
            chars = ext.get("study_characteristics", {})
            designs.add(chars.get("study_design", "Unknown"))
            populations.add(chars.get("population", "Unknown"))
            countries.add(chars.get("country", "Unknown"))
        
        # Assess clinical heterogeneity
        clinical_heterogeneity = "high" if len(populations) > 5 else "moderate" if len(populations) > 2 else "low"
        
        # Assess methodological heterogeneity
        methodological_heterogeneity = "high" if len(designs) > 4 else "moderate" if len(designs) > 2 else "low"
        
        # Determine if meta-analysis appropriate
        meta_analysis_appropriate = (
            clinical_heterogeneity != "high" and
            methodological_heterogeneity != "high" and
            len(extractions) >= 3
        )
        
        return {
            "clinical_heterogeneity": clinical_heterogeneity,
            "methodological_heterogeneity": methodological_heterogeneity,
            "study_designs": list(designs),
            "populations": list(populations)[:10],
            "geographic_spread": len(countries),
            "meta_analysis_appropriate": meta_analysis_appropriate,
            "recommendation": (
                "Quantitative meta-analysis feasible" if meta_analysis_appropriate
                else "Narrative synthesis recommended due to heterogeneity"
            )
        }
    
    async def _generate_quantitative_summary(
        self,
        extractions: list[dict],
        patterns: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Generate quantitative summary."""
        
        # Count statistics
        total_studies = len(extractions)
        
        # Sample sizes
        sample_sizes = []
        for ext in extractions:
            chars = ext.get("study_characteristics", {})
            size = chars.get("sample_size", "")
            if size and size != "NR":
                try:
                    sample_sizes.append(int(str(size).replace(",", "")))
                except ValueError:
                    pass
        
        # Study designs
        design_counts = {}
        for ext in extractions:
            design = ext.get("study_characteristics", {}).get("study_design", "Unknown")
            design_counts[design] = design_counts.get(design, 0) + 1
        
        # Quality assessment
        quality_counts = {"low": 0, "moderate": 0, "high": 0, "unclear": 0}
        for ext in extractions:
            risk = ext.get("quality", {}).get("bias_risk", "unclear")
            quality_counts[risk] = quality_counts.get(risk, 0) + 1
        
        return {
            "total_studies": total_studies,
            "total_participants": sum(sample_sizes) if sample_sizes else "NR",
            "sample_size_range": f"{min(sample_sizes)}-{max(sample_sizes)}" if sample_sizes else "NR",
            "median_sample_size": sorted(sample_sizes)[len(sample_sizes)//2] if sample_sizes else "NR",
            "study_design_distribution": design_counts,
            "quality_distribution": quality_counts,
            "key_patterns_count": len(patterns.get("patterns", [])) if patterns else 0
        }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add meta-analyst metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "analysis_complete": True,
                "meta_analysis_feasible": result.output.get("meta_analysis_feasible", False)
            }
            result.suggested_next_agents = ["synthesizer", "gap_identifier"]
        return result
