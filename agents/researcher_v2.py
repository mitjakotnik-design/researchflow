"""
Researcher Agent V2: Enhanced version with DI, retry, and validation.

This is the new version of ResearcherAgent that uses:
- Dependency Injection for all dependencies
- Pydantic validation for inputs
- Built-in retry with exponential backoff
- Circuit breaker for resilience
- Rate limiting for API calls
"""

import json
from typing import Any, Optional
from pydantic import BaseModel

import structlog

from agents.base_agent_v2 import EnhancedBaseAgent, AgentDependencies, AgentRole
from agents.request_models import ResearchQueryRequest, SynthesizeThemeRequest, get_request_model


logger = structlog.get_logger()


class ResearcherAgentV2(EnhancedBaseAgent):
    """
    Enhanced Researcher Agent with dependency injection and resilience.
    
    Capabilities:
    - Generate research queries
    - Search literature using RAG
    - Synthesize findings with confidence scoring
    - Identify key themes and gaps
    - Triangulate evidence from multiple sources
    """
    
    def __init__(self, deps: AgentDependencies):
        super().__init__(
            name="researcher",
            role=AgentRole.RESEARCH,
            deps=deps,
            description="Conducts literature research and synthesizes findings",
            version="2.0.0"
        )
        
        # Research cache for the session
        self._query_cache: dict[str, list[dict]] = {}
    
    def get_request_model(self, action: str) -> Optional[type[BaseModel]]:
        """Get Pydantic model for action validation."""
        return get_request_model("researcher", action)
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute researcher actions."""
        if action == "research":
            return await self._conduct_research(**kwargs)
        elif action == "generate_queries":
            return await self._generate_queries(**kwargs)
        elif action == "synthesize":
            return await self._synthesize_findings(**kwargs)
        elif action == "synthesize_theme":
            return await self._synthesize_theme(**kwargs)
        elif action == "identify_themes":
            return await self._identify_themes(**kwargs)
        elif action == "identify_gaps":
            return await self._identify_gaps(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _conduct_research(
        self,
        query: str,
        top_k: int = 15,
        require_citations: bool = True,
        min_confidence: float = 0.7,
        section: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Conduct comprehensive research on a query.
        
        Uses hybrid RAG search with confidence scoring.
        """
        # Check cache first
        cache_key = f"{query}:{top_k}"
        if cache_key in self._query_cache:
            self.log.debug("cache_hit", query=query[:50])
            cached = self._query_cache[cache_key]
            # Re-synthesize even for cached results
            synthesis = await self._synthesize_findings(
                results=cached,
                section=section
            )
            return {
                "query": query,
                "results_count": len(cached),
                "synthesis": synthesis,
                "cached": True,
            }
        
        # Generate sub-queries for comprehensive coverage
        sub_queries = await self._generate_queries(
            topic=query,
            section=section,
            count=3
        )
        
        # Execute RAG searches
        all_results = []
        for q in [query] + sub_queries:
            results = await self.query_rag(
                query=q,
                top_k=top_k
            )
            all_results.extend(results)
        
        # Deduplicate by content hash
        seen = set()
        unique_results = []
        for r in all_results:
            content_hash = hash(r.get("content", "")[:200])
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(r)
        
        # Cache results
        self._query_cache[cache_key] = unique_results
        
        # Synthesize findings with confidence
        synthesis = await self._synthesize_findings(
            results=unique_results,
            section=section,
            require_citations=require_citations,
            min_confidence=min_confidence,
        )
        
        self.log.info(
            "research_completed",
            query=query[:50],
            results_count=len(unique_results),
            themes_found=len(synthesis.get("themes", []))
        )
        
        return {
            "query": query,
            "sub_queries": sub_queries,
            "results_count": len(unique_results),
            "synthesis": synthesis,
            "raw_results": unique_results[:20],
            "cached": False,
        }
    
    async def _generate_queries(
        self,
        topic: str,
        section: Optional[str] = None,
        count: int = 5,
        existing_queries: Optional[list[str]] = None,
        **kwargs
    ) -> list[str]:
        """Generate research queries for a topic."""
        
        system_prompt = """You are a research query specialist for scoping reviews.
Generate precise, searchable queries for academic literature retrieval.
Focus on key concepts, relationships, and evidence.
Each query should target different aspects of the topic."""
        
        context = f" for the {section} section" if section else ""
        existing_text = ""
        if existing_queries:
            existing_text = "\n\nExisting queries (generate different ones):\n" + "\n".join(
                f"- {q}" for q in existing_queries
            )
        
        prompt = f"""Generate {count} research queries{context} on this topic:

Topic: {topic}
{existing_text}

Requirements:
- Each query should target specific evidence
- Include concept combinations
- Cover different aspects of the topic
- Be searchable in academic databases
- Focus on: AI, HR, psychosocial risks, organizational culture

Output as JSON array of strings only:"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            json_mode=True
        )
        
        try:
            queries = json.loads(response.content)
            if isinstance(queries, list):
                return queries[:count]
        except json.JSONDecodeError:
            # Parse from text
            lines = response.content.strip().split("\n")
            queries = [
                line.strip().strip("-").strip('"').strip()
                for line in lines
                if line.strip() and not line.startswith("{")
            ]
            return queries[:count]
        
        return [topic]
    
    async def _synthesize_findings(
        self,
        results: list[dict],
        section: Optional[str] = None,
        focus: Optional[str] = None,
        require_citations: bool = True,
        min_confidence: float = 0.7,
        **kwargs
    ) -> dict:
        """Synthesize research findings with confidence scoring."""
        
        if not results:
            return {
                "summary": "No relevant sources found.",
                "themes": [],
                "evidence_strength": "insufficient",
                "confidence": 0.0,
                "gaps": ["Need more literature"],
                "citations": [],
            }
        
        # Format results for synthesis
        formatted_results = []
        for i, r in enumerate(results[:15], 1):
            source = r.get("source", "Unknown")
            title = r.get("document_title", r.get("source", ""))
            content = r.get("content", "")[:600]
            score = r.get("score", 0.0)
            formatted_results.append(
                f"[{i}] {title} (relevance: {score:.2f})\nSource: {source}\n{content}"
            )
        
        results_text = "\n\n".join(formatted_results)
        
        system_prompt = """You are a research synthesis expert for scoping reviews.
Analyze sources objectively, identify patterns, and assess evidence quality.
Provide confidence scores based on evidence consistency and source quality.
Note contradictions, gaps, and areas of strong consensus."""
        
        prompt = f"""Synthesize these research findings{" for " + section if section else ""}:

## Sources ({len(results)} total, showing top 15)
{results_text}

{f"## Focus Area: {focus}" if focus else ""}

## Output JSON Format
{{
    "summary": "2-3 paragraph synthesis of key findings",
    "themes": [
        {{
            "name": "theme name",
            "description": "brief description",
            "evidence_count": 5,
            "confidence": 0.85  // 0-1 scale
        }}
    ],
    "evidence_strength": "strong|moderate|weak|insufficient",
    "overall_confidence": 0.8,  // 0-1 scale
    "key_findings": ["finding 1", "finding 2"],
    "contradictions": ["any contradictory findings"],
    "gaps": ["identified gaps in literature"],
    "citations": ["Author (Year)", "Author (Year)"]
}}

Return valid JSON only:"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,
            json_mode=True
        )
        
        try:
            synthesis = json.loads(response.content)
            
            # Filter by confidence threshold
            if "themes" in synthesis:
                synthesis["themes"] = [
                    t for t in synthesis["themes"]
                    if t.get("confidence", 0) >= min_confidence
                ]
            
            return synthesis
            
        except json.JSONDecodeError:
            self.log.warning("synthesis_parse_error", content=response.content[:200])
            return {
                "summary": response.content[:1000],
                "themes": [],
                "evidence_strength": "unknown",
                "confidence": 0.5,
                "gaps": [],
                "citations": [],
            }
    
    async def _synthesize_theme(
        self,
        theme: str,
        sources: list[dict],
        synthesis_approach: str = "thematic",
        **kwargs
    ) -> dict:
        """Synthesize research around a specific theme."""
        
        # Format sources
        sources_text = "\n\n".join(
            f"[{i+1}] {s.get('content', '')[:500]}"
            for i, s in enumerate(sources[:10])
        )
        
        system_prompt = f"""You are synthesizing research using {synthesis_approach} analysis.
Focus on the specific theme and extract relevant evidence.
Note patterns, contradictions, and confidence levels."""
        
        prompt = f"""Synthesize evidence for this theme:

## Theme: {theme}

## Sources
{sources_text}

## Synthesis Approach: {synthesis_approach}

Provide:
1. Key findings related to this theme
2. Evidence strength (how many sources, consistency)
3. Gaps or contradictions
4. Confidence level (0-1)

Output as JSON:"""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "theme": theme,
                "synthesis": response.content,
                "confidence": 0.5,
            }
    
    async def _identify_themes(
        self,
        results: list[dict],
        min_occurrences: int = 3,
        **kwargs
    ) -> list[dict]:
        """Identify major themes from research results."""
        
        if not results:
            return []
        
        # Concatenate content
        all_content = "\n\n".join(
            r.get("content", "")[:400] for r in results[:20]
        )
        
        prompt = f"""Identify major themes from this research content:

{all_content}

Requirements:
- Identify 5-10 recurring themes
- Each theme should appear in at least {min_occurrences} sources
- Focus on themes relevant to AI, HR, psychosocial risks

Output as JSON array:
[
    {{
        "name": "Theme Name",
        "description": "Brief description",
        "keywords": ["keyword1", "keyword2"],
        "estimated_occurrences": 5
    }}
]"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            themes = json.loads(response.content)
            return [t for t in themes if t.get("estimated_occurrences", 0) >= min_occurrences]
        except json.JSONDecodeError:
            return []
    
    async def _identify_gaps(
        self,
        results: list[dict],
        research_questions: Optional[list[str]] = None,
        **kwargs
    ) -> dict:
        """Identify gaps in the research literature."""
        
        synthesis = await self._synthesize_findings(results)
        
        rq_text = ""
        if research_questions:
            rq_text = "## Research Questions\n" + "\n".join(
                f"- {rq}" for rq in research_questions
            )
        
        prompt = f"""Identify research gaps based on this synthesis:

## Current Evidence Summary
{synthesis.get('summary', '')}

## Themes Covered
{', '.join(t.get('name', '') for t in synthesis.get('themes', []))}

{rq_text}

Identify:
1. Methodological gaps (what study designs are missing?)
2. Population gaps (what groups are understudied?)
3. Conceptual gaps (what relationships are unexplored?)
4. Temporal gaps (are findings outdated?)
5. Geographic gaps (what regions lack research?)

Output as JSON:
{{
    "methodological": ["gap1", "gap2"],
    "population": ["gap1"],
    "conceptual": ["gap1", "gap2"],
    "temporal": ["gap1"],
    "geographic": ["gap1"],
    "priority_research_directions": ["direction1", "direction2"]
}}"""
        
        response = await self.generate(
            prompt=prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "methodological": [],
                "population": [],
                "conceptual": [],
                "temporal": [],
                "geographic": [],
                "priority_research_directions": [],
            }
    
    def clear_cache(self) -> int:
        """Clear research cache."""
        count = len(self._query_cache)
        self._query_cache.clear()
        self.log.info("research_cache_cleared", entries=count)
        return count
