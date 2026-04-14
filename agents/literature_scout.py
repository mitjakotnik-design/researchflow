"""Literature Scout Agent: Discovers and retrieves relevant literature."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class LiteratureScoutAgent(BaseAgent):
    """
    Agent responsible for finding relevant literature.
    
    Capabilities:
    - Generate search strategies
    - Execute systematic searches
    - Screen abstracts
    - Track search coverage
    """
    
    def __init__(self):
        super().__init__(
            name="literature_scout",
            role=AgentRole.RESEARCH,
            description="Discovers and retrieves relevant literature",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._search_history: list[dict] = []
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute literature scout actions."""
        if action == "scout":
            return await self._scout_literature(**kwargs)
        elif action == "generate_search_strategy":
            return await self._generate_search_strategy(**kwargs)
        elif action == "screen_abstracts":
            return await self._screen_abstracts(**kwargs)
        elif action == "assess_coverage":
            return await self._assess_coverage(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _scout_literature(
        self,
        research_questions: str,
        databases: Optional[list[str]] = None,
        **kwargs
    ) -> dict:
        """Scout for relevant literature."""
        
        databases = databases or ["PubMed", "Scopus", "Web of Science"]
        
        # Generate search strategy
        strategy = await self._generate_search_strategy(
            research_questions=research_questions,
            databases=databases
        )
        
        # Execute searches via RAG
        all_results = []
        for query in strategy.get("queries", []):
            results = await self.query_rag(query=query, top_k=15)
            all_results.extend(results)
        
        # Deduplicate
        seen_ids = set()
        unique_results = []
        for r in all_results:
            rid = r.get("id", "")
            if rid not in seen_ids:
                seen_ids.add(rid)
                unique_results.append(r)
        
        # Screen for relevance
        screened = await self._screen_abstracts(
            abstracts=unique_results,
            criteria=strategy.get("inclusion_criteria", [])
        )
        
        # Record search
        self._search_history.append({
            "queries": strategy.get("queries", []),
            "results_found": len(unique_results),
            "included": len([s for s in screened if s.get("include")])
        })
        
        self.log.info(
            "scouting_completed",
            total_found=len(unique_results),
            included=len([s for s in screened if s.get("include")])
        )
        
        return {
            "strategy": strategy,
            "total_found": len(unique_results),
            "screened_results": screened,
            "included_count": len([s for s in screened if s.get("include")]),
            "search_history": self._search_history
        }
    
    async def _generate_search_strategy(
        self,
        research_questions: str,
        databases: list[str],
        **kwargs
    ) -> dict:
        """Generate systematic search strategy."""
        
        system_prompt = """You are a systematic review search specialist.
Create comprehensive search strategies following PRISMA guidelines.
Use Boolean operators, MeSH terms, and wildcards appropriately."""
        
        prompt = f"""Create a search strategy for this scoping review:

## Research Questions
{research_questions}

## Target Databases
{', '.join(databases)}

## Output JSON
{{
    "search_concept": "main concept being searched",
    "pico_elements": {{
        "population": "target population",
        "concept": "main concept",
        "context": "context/setting"
    }},
    "queries": [
        "database-agnostic search queries with Boolean operators"
    ],
    "mesh_terms": ["relevant MeSH/controlled vocabulary terms"],
    "inclusion_criteria": ["criteria for including studies"],
    "exclusion_criteria": ["criteria for excluding studies"],
    "date_range": "recommended date range",
    "language_restrictions": "language limitations if any"
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1200,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "queries": [research_questions],
                "inclusion_criteria": [],
                "exclusion_criteria": []
            }
    
    async def _screen_abstracts(
        self,
        abstracts: list[dict],
        criteria: list[str],
        **kwargs
    ) -> list[dict]:
        """Screen abstracts against inclusion criteria."""
        
        screened = []
        
        for abstract in abstracts[:30]:  # Limit batch size
            content = abstract.get("content", "")[:800]
            
            prompt = f"""Screen this abstract against inclusion criteria:

## Abstract
{content}

## Inclusion Criteria
{chr(10).join(f"- {c}" for c in criteria) if criteria else "- Relevant to the research topic"}

## Output JSON
{{
    "include": true/false,
    "confidence": <0.0-1.0>,
    "reason": "brief reason for decision",
    "relevant_themes": ["themes identified"]
}}"""
            
            response = await self._llm_client.generate(
                prompt=prompt,
                max_tokens=200,
                json_mode=True
            )
            
            try:
                result = json.loads(response.content)
                result["id"] = abstract.get("id", "")
                result["source"] = abstract.get("source", "")
                screened.append(result)
            except json.JSONDecodeError:
                screened.append({
                    "id": abstract.get("id", ""),
                    "include": False,
                    "reason": "Screening failed"
                })
        
        return screened
    
    async def _assess_coverage(self, **kwargs) -> dict:
        """Assess search coverage and saturation."""
        
        if not self._search_history:
            return {
                "coverage_adequate": False,
                "reason": "No searches performed yet"
            }
        
        total_found = sum(s.get("results_found", 0) for s in self._search_history)
        total_included = sum(s.get("included", 0) for s in self._search_history)
        
        coverage_adequate = total_included >= 20 and len(self._search_history) >= 2
        
        return {
            "coverage_adequate": coverage_adequate,
            "total_searches": len(self._search_history),
            "total_found": total_found,
            "total_included": total_included,
            "inclusion_rate": total_included / total_found if total_found > 0 else 0,
            "recommendation": "Continue searching" if not coverage_adequate else "Coverage adequate"
        }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add scout-specific metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "scouting_complete": True,
                "included_count": result.output.get("included_count", 0),
                "ready_for_extraction": result.output.get("included_count", 0) > 0
            }
            result.suggested_next_agents = ["data_extractor"]
        return result
