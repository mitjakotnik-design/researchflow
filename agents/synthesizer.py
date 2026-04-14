"""Synthesizer Agent: Synthesizes findings across studies."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class SynthesizerAgent(BaseAgent):
    """
    Agent responsible for synthesizing findings.
    
    Capabilities:
    - Thematic synthesis
    - Narrative synthesis
    - Framework synthesis
    - Evidence mapping
    """
    
    def __init__(self):
        super().__init__(
            name="synthesizer",
            role=AgentRole.WRITING,
            description="Synthesizes findings across studies",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._synthesis_cache: dict[str, dict] = {}
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute synthesizer actions."""
        if action == "synthesize":
            return await self._synthesize_findings(**kwargs)
        elif action == "thematic_synthesis":
            return await self._thematic_synthesis(**kwargs)
        elif action == "narrative_synthesis":
            return await self._narrative_synthesis(**kwargs)
        elif action == "create_evidence_map":
            return await self._create_evidence_map(**kwargs)
        elif action == "detect_saturation":
            return await self._detect_saturation(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _synthesize_findings(
        self,
        extractions: Optional[list[dict]] = None,
        synthesis_type: str = "thematic",
        **kwargs
    ) -> dict:
        """Synthesize findings from extractions."""
        
        # Get extractions from cache if not provided
        if not extractions:
            cache = self.state.research_cache
            # Flatten all query results
            extractions = []
            for results in cache.queries_executed.values():
                extractions.extend(results)
        
        if not extractions:
            return {
                "synthesis_complete": False,
                "reason": "No data to synthesize"
            }
        
        # Choose synthesis approach
        if synthesis_type == "thematic":
            synthesis = await self._thematic_synthesis(extractions=extractions)
        else:
            synthesis = await self._narrative_synthesis(extractions=extractions)
        
        # Cache synthesis
        cache_key = f"synthesis_{synthesis_type}"
        self._synthesis_cache[cache_key] = synthesis
        self.state.research_cache.synthesis_cache[cache_key] = json.dumps(synthesis)
        
        # Detect saturation
        saturation = await self._detect_saturation(synthesis=synthesis)
        synthesis["saturation"] = saturation
        
        self.log.info(
            "synthesis_completed",
            type=synthesis_type,
            themes_count=len(synthesis.get("themes", []))
        )
        
        return synthesis
    
    async def _thematic_synthesis(
        self,
        extractions: list[dict],
        **kwargs
    ) -> dict:
        """Perform thematic synthesis."""
        
        # Prepare findings for synthesis
        findings_text = []
        for i, ext in enumerate(extractions[:25], 1):
            if isinstance(ext, dict):
                finding = ext.get("findings", {})
                if isinstance(finding, dict):
                    main = finding.get("main_findings", "")
                    themes = finding.get("key_themes", [])
                    findings_text.append(
                        f"Study {i}: {main[:300]} | Themes: {', '.join(themes[:3]) if themes else 'NR'}"
                    )
                else:
                    findings_text.append(f"Study {i}: {str(ext)[:300]}")
        
        system_prompt = """You are a qualitative synthesis expert.
Perform rigorous thematic synthesis following Thomas & Harden's approach:
1. Line-by-line coding
2. Development of descriptive themes
3. Generation of analytical themes
Be systematic and evidence-based."""
        
        prompt = f"""Perform thematic synthesis on these findings:

## Review Topic
{self.state.title}

## Study Findings
{chr(10).join(findings_text)}

## Output JSON
{{
    "themes": [
        {{
            "theme_name": "analytical theme name",
            "description": "what this theme captures",
            "subthemes": [
                {{
                    "name": "descriptive subtheme",
                    "description": "details",
                    "supporting_studies": [1, 5, 12]
                }}
            ],
            "prevalence": "high|medium|low",
            "evidence_strength": "strong|moderate|weak"
        }}
    ],
    "theme_relationships": [
        {{
            "theme1": "first theme",
            "theme2": "second theme",
            "relationship": "how they relate"
        }}
    ],
    "overarching_narrative": "2-3 sentence overall synthesis",
    "key_insights": ["main takeaways from synthesis"],
    "limitations_of_synthesis": ["methodological limitations"]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            json_mode=True
        )
        
        try:
            synthesis = json.loads(response.content)
            synthesis["synthesis_type"] = "thematic"
            synthesis["studies_synthesized"] = len(extractions)
            return synthesis
        except json.JSONDecodeError:
            return {
                "themes": [],
                "synthesis_type": "thematic",
                "error": "Synthesis parsing failed"
            }
    
    async def _narrative_synthesis(
        self,
        extractions: list[dict],
        **kwargs
    ) -> dict:
        """Perform narrative synthesis."""
        
        # Prepare study summaries
        summaries = []
        for i, ext in enumerate(extractions[:20], 1):
            if isinstance(ext, dict):
                chars = ext.get("study_characteristics", {})
                findings = ext.get("findings", {})
                summaries.append({
                    "study": i,
                    "design": chars.get("study_design", "NR"),
                    "population": chars.get("population", "NR"),
                    "findings": findings.get("main_findings", "NR")[:200]
                })
        
        prompt = f"""Create a narrative synthesis:

## Review Topic
{self.state.title}

## Studies
{json.dumps(summaries, indent=2)}

## Output JSON
{{
    "narrative_sections": [
        {{
            "section_title": "section heading",
            "narrative": "synthesized narrative paragraph",
            "studies_cited": [1, 3, 5]
        }}
    ],
    "key_findings": ["main findings across studies"],
    "areas_of_consensus": ["what studies agree on"],
    "areas_of_disagreement": ["conflicting findings"],
    "synthesis_summary": "overall narrative summary"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            synthesis = json.loads(response.content)
            synthesis["synthesis_type"] = "narrative"
            synthesis["studies_synthesized"] = len(extractions)
            return synthesis
        except json.JSONDecodeError:
            return {
                "narrative_sections": [],
                "synthesis_type": "narrative",
                "error": "Synthesis parsing failed"
            }
    
    async def _create_evidence_map(
        self,
        synthesis: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Create evidence map from synthesis."""
        
        if not synthesis:
            synthesis = self._synthesis_cache.get("synthesis_thematic", {})
        
        themes = synthesis.get("themes", [])
        
        evidence_map = {
            "map_type": "theme_evidence",
            "nodes": [],
            "edges": []
        }
        
        # Create nodes for themes
        for i, theme in enumerate(themes):
            evidence_map["nodes"].append({
                "id": f"theme_{i}",
                "type": "theme",
                "label": theme.get("theme_name", f"Theme {i+1}"),
                "strength": theme.get("evidence_strength", "moderate")
            })
            
            # Create nodes for subthemes
            for j, subtheme in enumerate(theme.get("subthemes", [])):
                sub_id = f"subtheme_{i}_{j}"
                evidence_map["nodes"].append({
                    "id": sub_id,
                    "type": "subtheme",
                    "label": subtheme.get("name", ""),
                    "studies": subtheme.get("supporting_studies", [])
                })
                
                # Edge from theme to subtheme
                evidence_map["edges"].append({
                    "source": f"theme_{i}",
                    "target": sub_id,
                    "type": "contains"
                })
        
        # Add theme relationships as edges
        for rel in synthesis.get("theme_relationships", []):
            # Find theme IDs
            theme1_idx = next(
                (i for i, t in enumerate(themes) 
                 if t.get("theme_name") == rel.get("theme1")),
                None
            )
            theme2_idx = next(
                (i for i, t in enumerate(themes) 
                 if t.get("theme_name") == rel.get("theme2")),
                None
            )
            
            if theme1_idx is not None and theme2_idx is not None:
                evidence_map["edges"].append({
                    "source": f"theme_{theme1_idx}",
                    "target": f"theme_{theme2_idx}",
                    "type": "relates",
                    "label": rel.get("relationship", "")
                })
        
        return evidence_map
    
    async def _detect_saturation(
        self,
        synthesis: dict,
        **kwargs
    ) -> dict:
        """Detect thematic saturation."""
        
        themes = synthesis.get("themes", [])
        
        # Calculate saturation indicators
        theme_count = len(themes)
        avg_studies_per_theme = 0
        
        if themes:
            study_counts = []
            for theme in themes:
                for subtheme in theme.get("subthemes", []):
                    study_counts.append(len(subtheme.get("supporting_studies", [])))
            avg_studies_per_theme = sum(study_counts) / len(study_counts) if study_counts else 0
        
        # Saturation criteria
        saturation_reached = (
            theme_count >= 4 and
            avg_studies_per_theme >= 2 and
            all(theme.get("prevalence") != "low" for theme in themes[:3])
        )
        
        return {
            "saturation_reached": saturation_reached,
            "theme_count": theme_count,
            "avg_studies_per_theme": round(avg_studies_per_theme, 1),
            "confidence": 0.8 if saturation_reached else 0.5,
            "recommendation": (
                "Saturation achieved, ready for writing"
                if saturation_reached
                else "Consider additional literature search"
            )
        }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add synthesizer metadata."""
        if isinstance(result.output, dict):
            saturation = result.output.get("saturation", {})
            result.handoff_data = {
                "synthesis_complete": True,
                "themes_count": len(result.output.get("themes", [])),
                "saturation_reached": saturation.get("saturation_reached", False),
                "ready_for_writing": saturation.get("saturation_reached", False)
            }
            
            if saturation.get("saturation_reached"):
                result.suggested_next_agents = ["writer"]
            else:
                result.suggested_next_agents = ["literature_scout"]
        
        return result
