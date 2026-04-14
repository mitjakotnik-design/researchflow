"""Researcher Agent: Conducts literature research using RAG."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class ResearcherAgent(BaseAgent):
    """
    Agent responsible for conducting literature research.
    
    Capabilities:
    - Generate research queries
    - Search literature using RAG
    - Synthesize findings
    - Identify key themes
    """
    
    def __init__(self):
        super().__init__(
            name="researcher",
            role=AgentRole.RESEARCH,
            description="Conducts literature research and synthesizes findings",
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
        """Execute researcher actions."""
        if action == "research":
            return await self._conduct_research(**kwargs)
        elif action == "generate_queries":
            return await self._generate_queries(**kwargs)
        elif action == "synthesize":
            return await self._synthesize_findings(**kwargs)
        elif action == "identify_themes":
            return await self._identify_themes(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _conduct_research(
        self,
        section: str,
        research_questions: Optional[list[str]] = None,
        depth: str = "normal",
        **kwargs
    ) -> dict:
        """Conduct research for a section."""
        
        # Generate queries if not provided
        if not research_questions:
            research_questions = await self._generate_queries(
                topic=self.state.title,
                section=section
            )
        
        # Execute RAG searches
        all_results = []
        for query in research_questions:
            results = await self.query_rag(
                query=query,
                top_k=10 if depth == "normal" else 20
            )
            all_results.extend(results)
        
        # Deduplicate by ID
        seen_ids = set()
        unique_results = []
        for r in all_results:
            if r.get("id") not in seen_ids:
                seen_ids.add(r.get("id"))
                unique_results.append(r)
        
        # Cache results
        if self.context.cache_research:
            for query in research_questions:
                self.state.research_cache.add_query_result(query, unique_results)
        
        # Synthesize findings
        synthesis = await self._synthesize_findings(
            results=unique_results,
            section=section
        )
        
        self.log.info(
            "research_completed",
            section=section,
            queries_count=len(research_questions),
            results_count=len(unique_results)
        )
        
        return {
            "queries": research_questions,
            "results_count": len(unique_results),
            "synthesis": synthesis,
            "raw_results": unique_results[:20]  # Limit for state storage
        }
    
    async def _generate_queries(
        self,
        topic: str,
        section: Optional[str] = None,
        existing_queries: Optional[list[str]] = None,
        **kwargs
    ) -> list[str]:
        """Generate research queries for a topic."""
        
        system_prompt = """You are a research query specialist.
Generate precise, searchable queries for academic literature retrieval.
Focus on key concepts, relationships, and evidence."""
        
        context = f" for the {section} section" if section else ""
        
        prompt = f"""Generate 5-7 research queries{context} on this topic:

Topic: {topic}

{"Existing queries to build upon:\n" + chr(10).join(f"- {q}" for q in existing_queries) if existing_queries else ""}

Requirements:
- Each query should target specific evidence
- Include concept combinations
- Cover different aspects of the topic
- Be searchable in academic databases

Output as JSON array of strings:"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2000,  # Increased for Gemini thinking tokens
            json_mode=True
        )
        
        try:
            queries = json.loads(response.content)
            if isinstance(queries, list):
                return queries
        except json.JSONDecodeError:
            # Parse from text
            lines = response.content.strip().split("\n")
            queries = [line.strip().strip("-").strip() for line in lines if line.strip()]
            return queries[:7]
        
        return [topic]
    
    async def _synthesize_findings(
        self,
        results: list[dict],
        section: Optional[str] = None,
        focus: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Synthesize research findings."""
        
        if not results:
            return {
                "summary": "No relevant sources found.",
                "key_themes": [],
                "evidence_strength": "insufficient",
                "gaps": ["Need more literature"]
            }
        
        # Format results for synthesis
        formatted_results = []
        for i, r in enumerate(results[:15], 1):
            source = r.get("source", "Unknown")
            title = r.get("document_title", "")
            content = r.get("content", "")[:600]
            formatted_results.append(f"[{i}] {title} ({source})\n{content}")
        
        results_text = "\n\n".join(formatted_results)
        
        system_prompt = """You are a research synthesis expert.
Analyze sources and identify patterns, themes, and evidence quality.
Be objective and note contradictions or gaps."""
        
        prompt = f"""Synthesize these research findings{" for " + section if section else ""}:

## Sources
{results_text}

{f"## Focus Area: {focus}" if focus else ""}

## Output JSON Format
{{
    "summary": "2-3 paragraph synthesis of main findings",
    "key_themes": ["list of 4-6 main themes identified"],
    "evidence_strength": "strong|moderate|weak|mixed",
    "consensus_points": ["points where sources agree"],
    "conflicts": ["any contradictory findings"],
    "gaps": ["areas needing more research"],
    "citation_map": {{"theme": ["source numbers"]}}
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000,  # Increased for Gemini thinking tokens
            json_mode=True
        )
        
        try:
            synthesis = json.loads(response.content)
            return synthesis
        except json.JSONDecodeError:
            return {
                "summary": response.content,
                "key_themes": [],
                "evidence_strength": "unknown",
                "gaps": []
            }
    
    async def _identify_themes(
        self,
        content: str,
        min_themes: int = 3,
        max_themes: int = 8,
        **kwargs
    ) -> list[dict]:
        """Identify themes from content."""
        
        system_prompt = """You are a qualitative research analyst.
Identify themes using thematic analysis principles.
Look for patterns, concepts, and recurring ideas."""
        
        prompt = f"""Identify {min_themes}-{max_themes} themes from this content:

{content[:4000]}

## Output JSON Format
[
    {{
        "theme": "Theme name",
        "description": "Brief description",
        "prevalence": "high|medium|low",
        "key_quotes": ["supporting quotes from text"],
        "sub_themes": ["related sub-themes if any"]
    }}
]"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=4000,  # Increased for Gemini thinking tokens
            json_mode=True
        )
        
        try:
            themes = json.loads(response.content)
            return themes if isinstance(themes, list) else []
        except json.JSONDecodeError:
            return []
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add researcher-specific metadata with confidence scoring."""
        if isinstance(result.output, dict):
            # Calculate confidence based on research quality indicators
            confidence_factors = []
            
            # 1. Number of results found
            results_count = result.output.get("results_count", 0)
            results_factor = min(1.0, results_count / 10)  # Expect 10+ results
            confidence_factors.append(results_factor)
            
            # 2. Synthesis quality (presence of key synthesis fields)
            synthesis = result.output.get("synthesis", {})
            if synthesis:
                has_themes = bool(synthesis.get("key_themes", []))
                has_summary = bool(synthesis.get("summary", ""))
                has_gaps = bool(synthesis.get("research_gaps", []))
                synthesis_factor = (int(has_themes) + int(has_summary) + int(has_gaps)) / 3
            else:
                synthesis_factor = 0.3
            confidence_factors.append(synthesis_factor)
            
            # 3. Query coverage (did we execute all planned queries?)
            queries = result.output.get("queries", [])
            query_factor = min(1.0, len(queries) / 3)  # Expect ~3 queries
            confidence_factors.append(query_factor)
            
            # 4. Evidence strength indicator
            evidence_map = {"strong": 1.0, "moderate": 0.7, "weak": 0.4, "unknown": 0.5}
            evidence_strength = result.output.get("evidence_strength", "unknown")
            evidence_factor = evidence_map.get(evidence_strength, 0.5)
            confidence_factors.append(evidence_factor)
            
            # Average confidence
            result.confidence = sum(confidence_factors) / len(confidence_factors)
            
            result.handoff_data = {
                "research_ready": results_count >= 5,
                "results_count": results_count,
                "queries_executed": len(queries),
                "themes_identified": len(synthesis.get("key_themes", [])) if synthesis else 0,
                "evidence_strength": evidence_strength,
                "confidence_breakdown": {
                    "results_factor": results_factor,
                    "synthesis_factor": synthesis_factor,
                    "query_factor": query_factor,
                    "evidence_factor": evidence_factor
                }
            }
            result.suggested_next_agents = ["data_extractor", "synthesizer"]
        return result
