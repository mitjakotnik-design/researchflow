"""Data Extractor Agent: Extracts structured data from studies."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


# Default extraction schema for scoping reviews
DEFAULT_EXTRACTION_SCHEMA = {
    "study_characteristics": [
        "authors",
        "year",
        "country",
        "study_design",
        "sample_size",
        "population"
    ],
    "methodology": [
        "data_collection",
        "analysis_method",
        "theoretical_framework"
    ],
    "findings": [
        "main_findings",
        "key_themes",
        "quantitative_results"
    ],
    "quality": [
        "limitations_reported",
        "bias_risk"
    ]
}


class DataExtractorAgent(BaseAgent):
    """
    Agent responsible for extracting data from studies.
    
    Capabilities:
    - Extract structured data using schema
    - Validate extracted data
    - Aggregate extraction results
    - Generate data tables
    """
    
    def __init__(self):
        super().__init__(
            name="data_extractor",
            role=AgentRole.RESEARCH,
            description="Extracts structured data from studies",
            version="1.0.0"
        )
        
        self._llm_client = None
        self._extractions: list[dict] = []
    
    def on_initialize(self) -> None:
        """Initialize LLM client."""
        self._llm_client = LLMClientFactory.create(
            model_name=self._model_name,
            temperature=self._temperature
        )
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute data extractor actions."""
        if action == "extract":
            return await self._extract_data(**kwargs)
        elif action == "extract_single":
            return await self._extract_from_study(**kwargs)
        elif action == "validate":
            return await self._validate_extraction(**kwargs)
        elif action == "aggregate":
            return await self._aggregate_extractions(**kwargs)
        elif action == "generate_table":
            return await self._generate_data_table(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _extract_data(
        self,
        schema: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Extract data from all cached studies."""
        
        schema = schema or DEFAULT_EXTRACTION_SCHEMA
        
        # Get documents from research cache
        cache = self.state.research_cache
        documents = []
        
        # Safely get query results
        if hasattr(cache, 'queries_executed') and isinstance(cache.queries_executed, dict):
            for query, query_results in cache.queries_executed.items():
                if isinstance(query_results, list):
                    documents.extend(query_results)
        
        # Deduplicate
        seen = set()
        unique_docs = []
        for doc in documents:
            if not isinstance(doc, dict):
                continue
                
            # Handle different possible ID field names
            doc_id = doc.get("id") or doc.get("document_id") or doc.get("doc_id", "")
            if doc_id and doc_id not in seen:
                seen.add(doc_id)
                unique_docs.append(doc)
        
        if not unique_docs:
            self.log.warning("no_documents_to_extract", cache_size=len(documents))
            return {
                "extractions_count": 0,
                "extractions": [],
                "aggregated": {},
                "schema_used": schema
            }
        
        # Extract from each document
        extractions = []
        for doc in unique_docs[:50]:  # Limit batch size
            try:
                # Handle different possible content field names
                content = doc.get("content") or doc.get("text") or doc.get("page_content", "")
                
                # Safely extract source from metadata (can be dict or list)
                source = doc.get("source", "")
                if not source:
                    metadata = doc.get("metadata")
                    if isinstance(metadata, dict):
                        source = metadata.get("source", "")
                    elif isinstance(metadata, list) and len(metadata) > 0:
                        # If metadata is list, try first element
                        first_item = metadata[0]
                        if isinstance(first_item, dict):
                            source = first_item.get("source", "")
                if not source:
                    source = doc.get("document", "")
                
                if not content:
                    continue
                    
                extraction = await self._extract_from_study(
                    content=content,
                    source=source,
                    schema=schema
                )
                extractions.append(extraction)
            except Exception as e:
                self.log.error("extraction_failed_for_doc", doc_id=doc.get("id", "unknown"), error=str(e))
                continue
        
        self._extractions = extractions
        
        # Aggregate results
        aggregated = await self._aggregate_extractions(extractions=extractions) if extractions else {}
        
        self.log.info(
            "extraction_completed",
            documents_processed=len(extractions),
            fields_extracted=len(schema)
        )
        
        return {
            "extractions_count": len(extractions),
            "extractions": extractions,
            "aggregated": aggregated,
            "schema_used": schema
        }
    
    async def _extract_from_study(
        self,
        content: str,
        source: str = "",
        schema: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Extract data from a single study."""
        
        schema = schema or DEFAULT_EXTRACTION_SCHEMA
        
        # Build schema description
        schema_text = []
        for category, fields in schema.items():
            schema_text.append(f"\n### {category}")
            for field in fields:
                schema_text.append(f"- {field}")
        
        system_prompt = """You are a systematic review data extractor.
Extract structured data from research studies accurately.
If information is not available, use "NR" (not reported).
Be precise and quote directly when possible."""
        
        prompt = f"""Extract data from this study:

## Source
{source}

## Content
{content[:4000]}

## Extraction Schema
{chr(10).join(schema_text)}

## Output JSON
{{
    "source": "{source}",
    "study_characteristics": {{
        "authors": "author names",
        "year": "publication year",
        "country": "country of study",
        "study_design": "type of study",
        "sample_size": "N or NR",
        "population": "target population"
    }},
    "methodology": {{
        "data_collection": "how data was collected",
        "analysis_method": "analysis approach",
        "theoretical_framework": "framework used or NR"
    }},
    "findings": {{
        "main_findings": "key findings summary",
        "key_themes": ["list of themes"],
        "quantitative_results": "any numbers/statistics"
    }},
    "quality": {{
        "limitations_reported": true/false,
        "bias_risk": "low/moderate/high/unclear"
    }},
    "extraction_confidence": <0.0-1.0>
}}"""
        
        response = await self._llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1000,
            json_mode=True
        )
        
        try:
            extraction = json.loads(response.content)
            extraction["source"] = source
            return extraction
        except json.JSONDecodeError:
            return {
                "source": source,
                "extraction_error": "Failed to parse",
                "extraction_confidence": 0.0
            }
    
    async def _validate_extraction(
        self,
        extraction: dict,
        **kwargs
    ) -> dict:
        """Validate extracted data."""
        
        issues = []
        
        # Check completeness
        required_fields = ["study_characteristics", "findings"]
        for field in required_fields:
            if field not in extraction or not extraction[field]:
                issues.append(f"Missing required field: {field}")
        
        # Check for NR overuse
        nr_count = str(extraction).count('"NR"') + str(extraction).count("'NR'")
        if nr_count > 5:
            issues.append(f"High number of NR values ({nr_count})")
        
        # Check confidence
        confidence = extraction.get("extraction_confidence", 0)
        if confidence < 0.5:
            issues.append(f"Low extraction confidence: {confidence}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "completeness_score": 1.0 - (len(issues) * 0.2)
        }
    
    async def _aggregate_extractions(
        self,
        extractions: Optional[list[dict]] = None,
        **kwargs
    ) -> dict:
        """Aggregate multiple extractions."""
        
        extractions = extractions or self._extractions
        
        if not extractions:
            return {"error": "No extractions to aggregate"}
        
        # Count study designs
        designs = {}
        countries = {}
        years = []
        themes = []
        
        for ext in extractions:
            chars = ext.get("study_characteristics", {})
            
            design = chars.get("study_design", "Unknown")
            designs[design] = designs.get(design, 0) + 1
            
            country = chars.get("country", "Unknown")
            countries[country] = countries.get(country, 0) + 1
            
            year = chars.get("year", "")
            if year and year != "NR":
                try:
                    years.append(int(year))
                except ValueError:
                    pass
            
            findings = ext.get("findings", {})
            themes.extend(findings.get("key_themes", []))
        
        # Theme frequency
        theme_freq = {}
        for theme in themes:
            theme_freq[theme] = theme_freq.get(theme, 0) + 1
        
        top_themes = sorted(theme_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_studies": len(extractions),
            "study_designs": designs,
            "countries": countries,
            "year_range": f"{min(years)}-{max(years)}" if years else "NR",
            "top_themes": [{"theme": t, "count": c} for t, c in top_themes],
            "avg_confidence": sum(
                e.get("extraction_confidence", 0) for e in extractions
            ) / len(extractions) if extractions else 0
        }
    
    async def _generate_data_table(
        self,
        format: str = "markdown",
        **kwargs
    ) -> str:
        """Generate data extraction table."""
        
        if not self._extractions:
            return "No data extracted yet."
        
        if format == "markdown":
            lines = [
                "| Author | Year | Country | Design | Sample | Key Findings |",
                "|--------|------|---------|--------|--------|--------------|"
            ]
            
            for ext in self._extractions[:30]:
                chars = ext.get("study_characteristics", {})
                findings = ext.get("findings", {})
                
                row = [
                    chars.get("authors", "NR")[:20],
                    str(chars.get("year", "NR")),
                    chars.get("country", "NR")[:15],
                    chars.get("study_design", "NR")[:15],
                    str(chars.get("sample_size", "NR")),
                    str(findings.get("main_findings", "NR"))[:50]
                ]
                lines.append("| " + " | ".join(row) + " |")
            
            return "\n".join(lines)
        
        return json.dumps(self._extractions, indent=2)
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add extractor-specific metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "extraction_complete": True,
                "studies_extracted": result.output.get("extractions_count", 0),
                "ready_for_synthesis": True
            }
            result.suggested_next_agents = ["synthesizer", "meta_analyst"]
        return result
