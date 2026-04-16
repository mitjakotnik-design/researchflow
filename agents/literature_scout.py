"""Literature Scout Agent: Discovers and retrieves relevant literature."""

import json
from typing import Any, Optional

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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
        elif action == "generate_wos_query":
            return await self._generate_wos_query(**kwargs)
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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),
        reraise=True
    )
    async def _generate_wos_query(
        self,
        missing_concepts: list[dict],
        context: Optional[str] = None,
        **kwargs
    ) -> dict:
        """
        Generate Web of Science search queries for missing concepts.
        
        Args:
            missing_concepts: List of missing theories, methodologies, or research areas
            context: Additional context about the review topic
            
        Returns:
            Dictionary with WOS-formatted queries
            
        Includes automatic retry logic (3 attempts) for LLM timeouts/connection errors.
        """
        
        # Build concept descriptions
        concepts_text = ""
        for concept in missing_concepts:
            concept_name = concept.get('theory_name') or concept.get('methodology_name') or concept.get('research_area', '')
            search_terms = concept.get('search_terms', [])
            why_needed = concept.get('why_needed', '')
            
            concepts_text += f"\n- {concept_name}"
            if search_terms:
                concepts_text += f"\n  Alternative terms: {', '.join(search_terms)}"
            if why_needed:
                concepts_text += f"\n  Reason: {why_needed}"
        
        system_prompt = """You are a Web of Science search query specialist.
Generate precise WOS Advanced Search queries using field tags and Boolean operators.

WOS Field Tags:
- TI= (Title)
- AB= (Abstract)
- AU= (Author)
- SO= (Source/Journal)
- TS= (Topic - searches Title, Abstract, Keywords)

Boolean Operators: AND, OR, NOT
Use quotes for exact phrases: "Job Demands-Resources"
Use parentheses for complex logic: (AI OR "artificial intelligence")
Use wildcards: psycholog* for psychology, psychological, etc.

Format queries for maximum recall while maintaining precision."""
        
        prompt = f"""Generate Web of Science Advanced Search queries for these missing concepts:

{concepts_text}

## Review Context
{context or self.state.title}

## Instructions
Create 1-3 WOS queries that will retrieve relevant literature for the missing concepts.
Combine related concepts into single queries where appropriate.
Use field tags (TI=, TS=, AB=) and Boolean operators.

## Output JSON
{{
    "queries": [
        {{
            "query": "TI=((\\"Job Demands-Resources\\" OR \\"JD-R\\")) AND TS=((\\"AI\\" OR \\"artificial intelligence\\"))",
            "purpose": "Find literature on JD-R model in AI context",
            "expected_results": "10-50",
            "target_concepts": ["Job Demands-Resources", "AI applications"]
        }}
    ],
    "search_strategy": {{
        "approach": "description of search approach",
        "rationale": "why these queries will address gaps",
        "time_span": "recommended years to search",
        "estimated_total_results": <number>
    }},
    "instructions": [
        "Step-by-step instructions for user to execute search in WOS"
    ]
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1500,
            json_mode=True
        )
        
        try:
            wos_queries = json.loads(response.content)
            
            self.log.info(
                "wos_queries_generated",
                num_queries=len(wos_queries.get("queries", [])),
                target_concepts=len(missing_concepts)
            )
            
            return wos_queries
            
        except json.JSONDecodeError as e:
            self.log.error("wos_query_generation_failed", error=str(e))
            return {
                "queries": [],
                "error": "Failed to generate queries"
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
