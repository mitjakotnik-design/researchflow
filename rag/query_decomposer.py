"""Query decomposition for complex research questions."""

import json
import re
from dataclasses import dataclass, field
from typing import Optional

import structlog


logger = structlog.get_logger()


@dataclass
class DecomposedQuery:
    """Result of query decomposition."""
    
    original_query: str
    sub_queries: list[str] = field(default_factory=list)
    
    # Query components
    concepts: list[str] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)  # AND, OR, NOT
    
    # Search parameters
    suggested_filters: dict = field(default_factory=dict)
    search_depth: str = "normal"  # shallow, normal, deep
    
    # Metadata
    complexity: str = "simple"  # simple, moderate, complex
    confidence: float = 0.8


class QueryDecomposer:
    """Decomposes complex queries into sub-queries for better retrieval."""
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.log = structlog.get_logger().bind(component="query_decomposer")
    
    async def decompose(
        self,
        query: str,
        context: Optional[str] = None,
        use_llm: bool = True
    ) -> DecomposedQuery:
        """Decompose a query into searchable components."""
        
        # Estimate complexity
        complexity = self._estimate_complexity(query)
        
        if complexity == "simple" or not use_llm or not self.llm_client:
            # Use rule-based decomposition
            return self._rule_based_decomposition(query, complexity)
        
        # Use LLM for complex queries
        return await self._llm_decomposition(query, context, complexity)
    
    def _estimate_complexity(self, query: str) -> str:
        """Estimate query complexity."""
        # Count indicators of complexity
        indicators = 0
        
        # Multiple questions
        if query.count("?") > 1:
            indicators += 1
        
        # Boolean operators
        if any(op in query.upper() for op in ["AND", "OR", "NOT", "BUT"]):
            indicators += 1
        
        # Multiple concepts (commas, semicolons)
        if query.count(",") > 2 or ";" in query:
            indicators += 1
        
        # Length
        if len(query.split()) > 30:
            indicators += 1
        
        # Comparative language
        if any(word in query.lower() for word in [
            "compare", "versus", "vs", "difference", "relationship",
            "correlation", "impact", "effect"
        ]):
            indicators += 1
        
        if indicators == 0:
            return "simple"
        elif indicators <= 2:
            return "moderate"
        else:
            return "complex"
    
    def _rule_based_decomposition(
        self,
        query: str,
        complexity: str
    ) -> DecomposedQuery:
        """Rule-based query decomposition."""
        
        result = DecomposedQuery(
            original_query=query,
            complexity=complexity
        )
        
        # Extract concepts (noun phrases, quoted terms)
        result.concepts = self._extract_concepts(query)
        
        # Extract operators
        result.operators = self._extract_operators(query)
        
        # Generate sub-queries
        if complexity == "simple":
            result.sub_queries = [query]
        else:
            result.sub_queries = self._generate_sub_queries(query, result.concepts)
        
        # Suggest search depth
        result.search_depth = "normal" if complexity == "simple" else "deep"
        
        return result
    
    def _extract_concepts(self, query: str) -> list[str]:
        """Extract key concepts from query."""
        concepts = []
        
        # Extract quoted phrases
        quoted = re.findall(r'"([^"]+)"', query)
        concepts.extend(quoted)
        
        # Extract key noun phrases (simplified)
        # In production, use spaCy or similar
        important_words = []
        skip_words = {
            "the", "a", "an", "is", "are", "was", "were", "what", "how",
            "why", "when", "where", "which", "who", "does", "do", "can",
            "could", "would", "should", "will", "has", "have", "had",
            "been", "being", "be", "this", "that", "these", "those",
            "with", "from", "for", "and", "or", "not", "but", "in", "on",
            "at", "to", "of", "by", "as", "if", "then", "than", "because"
        }
        
        words = query.lower().split()
        for word in words:
            # Clean word
            clean = re.sub(r'[^\w]', '', word)
            if clean and clean not in skip_words and len(clean) > 2:
                important_words.append(clean)
        
        concepts.extend(important_words[:10])  # Limit to 10 concepts
        
        return list(set(concepts))
    
    def _extract_operators(self, query: str) -> list[str]:
        """Extract boolean operators from query."""
        operators = []
        
        if " AND " in query.upper():
            operators.append("AND")
        if " OR " in query.upper():
            operators.append("OR")
        if " NOT " in query.upper():
            operators.append("NOT")
        
        return operators
    
    def _generate_sub_queries(
        self,
        query: str,
        concepts: list[str]
    ) -> list[str]:
        """Generate sub-queries from concepts."""
        sub_queries = [query]  # Always include original
        
        # Generate concept-focused queries
        for i, concept in enumerate(concepts[:5]):
            sub_queries.append(f"What is {concept}?")
            
            if i < len(concepts) - 1:
                next_concept = concepts[i + 1]
                sub_queries.append(
                    f"How does {concept} relate to {next_concept}?"
                )
        
        return sub_queries
    
    async def _llm_decomposition(
        self,
        query: str,
        context: Optional[str],
        complexity: str
    ) -> DecomposedQuery:
        """Use LLM for query decomposition."""
        
        system_prompt = """You are a research query decomposition expert. 
Given a complex research question, break it down into simpler, searchable sub-queries.

Return JSON with:
{
    "sub_queries": ["list of 3-7 simpler queries"],
    "concepts": ["key concepts to search"],
    "suggested_filters": {"optional filters like date_range, document_type"},
    "search_depth": "shallow|normal|deep"
}"""
        
        prompt = f"""Decompose this research query:

Query: {query}

{"Context: " + context if context else ""}

Return valid JSON only."""
        
        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                json_mode=True
            )
            
            result_data = json.loads(response.content)
            
            return DecomposedQuery(
                original_query=query,
                sub_queries=result_data.get("sub_queries", [query]),
                concepts=result_data.get("concepts", []),
                suggested_filters=result_data.get("suggested_filters", {}),
                search_depth=result_data.get("search_depth", "normal"),
                complexity=complexity,
                confidence=0.9
            )
            
        except Exception as e:
            self.log.warning(
                "llm_decomposition_failed",
                error=str(e),
                falling_back_to_rules=True
            )
            return self._rule_based_decomposition(query, complexity)
    
    def merge_results(
        self,
        query_results: dict[str, list]
    ) -> list:
        """Merge results from multiple sub-queries."""
        # Deduplicate by ID
        seen_ids = set()
        merged = []
        
        for sub_query, results in query_results.items():
            for result in results:
                if result.id not in seen_ids:
                    seen_ids.add(result.id)
                    merged.append(result)
        
        # Sort by score
        merged.sort(key=lambda x: x.score, reverse=True)
        
        return merged
