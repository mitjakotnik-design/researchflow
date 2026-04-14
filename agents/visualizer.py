"""Visualizer Agent: Creates data visualizations."""

import json
from typing import Any, Optional

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult
from agents.llm_client import LLMClientFactory


logger = structlog.get_logger()


class VisualizerAgent(BaseAgent):
    """
    Agent responsible for creating visualizations.
    
    Capabilities:
    - Generate PRISMA flow diagrams
    - Create data tables
    - Design concept maps
    - Produce chart specifications
    """
    
    def __init__(self):
        super().__init__(
            name="visualizer",
            role=AgentRole.WRITING,
            description="Creates data visualizations and figures",
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
        """Execute visualizer actions."""
        if action == "generate":
            return await self._generate_visualizations(**kwargs)
        elif action == "prisma_flow":
            return await self._create_prisma_flow(**kwargs)
        elif action == "data_table":
            return await self._create_data_table(**kwargs)
        elif action == "concept_map":
            return await self._create_concept_map(**kwargs)
        elif action == "chart_spec":
            return await self._create_chart_spec(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _generate_visualizations(self, **kwargs) -> dict:
        """Generate all required visualizations."""
        
        visualizations = {}
        
        # PRISMA flow diagram
        prisma = await self._create_prisma_flow(**kwargs)
        visualizations["prisma_flow"] = prisma
        
        # Data extraction table
        table = await self._create_data_table(**kwargs)
        visualizations["data_table"] = table
        
        # Concept map if synthesis available
        concept_map = await self._create_concept_map(**kwargs)
        visualizations["concept_map"] = concept_map
        
        self.log.info(
            "visualizations_generated",
            count=len(visualizations)
        )
        
        return {
            "visualizations": visualizations,
            "generated_count": len(visualizations)
        }
    
    async def _create_prisma_flow(
        self,
        records_identified: int = 0,
        records_screened: int = 0,
        records_excluded: int = 0,
        full_text_assessed: int = 0,
        full_text_excluded: int = 0,
        studies_included: int = 0,
        **kwargs
    ) -> dict:
        """Create PRISMA flow diagram specification."""
        
        # If no data provided, estimate from state
        if records_identified == 0:
            cache = self.state.research_cache
            records_identified = sum(
                len(results) for results in cache.queries_executed.values()
            )
            records_screened = records_identified
            studies_included = len(set(
                doc.get("id")
                for results in cache.queries_executed.values()
                for doc in results
            ))
            records_excluded = records_screened - studies_included
            full_text_assessed = studies_included
        
        # Create Mermaid diagram specification
        mermaid_spec = f"""flowchart TD
    subgraph Identification
        A[Records identified through database searching<br/>n = {records_identified}]
        B[Additional records identified through other sources<br/>n = 0]
    end
    
    subgraph Screening
        C[Records after duplicates removed<br/>n = {records_screened}]
        D[Records screened<br/>n = {records_screened}]
        E[Records excluded<br/>n = {records_excluded}]
    end
    
    subgraph Eligibility
        F[Full-text articles assessed for eligibility<br/>n = {full_text_assessed}]
        G[Full-text articles excluded<br/>n = {full_text_excluded}]
    end
    
    subgraph Included
        H[Studies included in qualitative synthesis<br/>n = {studies_included}]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    F --> G
    F --> H"""
        
        return {
            "type": "prisma_flow",
            "format": "mermaid",
            "specification": mermaid_spec,
            "data": {
                "records_identified": records_identified,
                "records_screened": records_screened,
                "records_excluded": records_excluded,
                "full_text_assessed": full_text_assessed,
                "full_text_excluded": full_text_excluded,
                "studies_included": studies_included
            },
            "caption": "Figure 1: PRISMA-ScR flow diagram showing the study selection process."
        }
    
    async def _create_data_table(
        self,
        extractions: Optional[list[dict]] = None,
        **kwargs
    ) -> dict:
        """Create data extraction table."""
        
        # Get extractions from cache if not provided
        if not extractions:
            cache = self.state.research_cache
            extractions = list(cache.queries_executed.values())
            extractions = [item for sublist in extractions for item in sublist][:30]
        
        # Build table structure
        headers = ["Author", "Year", "Country", "Design", "Sample", "Key Findings"]
        rows = []
        
        for ext in extractions[:30]:
            if isinstance(ext, dict):
                chars = ext.get("study_characteristics", ext.get("metadata", {}))
                findings = ext.get("findings", {})
                
                rows.append([
                    str(chars.get("authors", ext.get("source", "NR")))[:30],
                    str(chars.get("year", "NR")),
                    str(chars.get("country", "NR"))[:15],
                    str(chars.get("study_design", "NR"))[:20],
                    str(chars.get("sample_size", "NR")),
                    str(findings.get("main_findings", ext.get("content", "")))[:100]
                ])
        
        # Generate markdown table
        md_table = "| " + " | ".join(headers) + " |\n"
        md_table += "|" + "|".join(["---"] * len(headers)) + "|\n"
        for row in rows:
            md_table += "| " + " | ".join(row) + " |\n"
        
        return {
            "type": "data_table",
            "format": "markdown",
            "table": md_table,
            "headers": headers,
            "row_count": len(rows),
            "caption": "Table 1: Characteristics of included studies."
        }
    
    async def _create_concept_map(
        self,
        themes: Optional[list[dict]] = None,
        **kwargs
    ) -> dict:
        """Create concept map from themes."""
        
        if not themes:
            # Try to get from synthesis cache
            cache = self.state.research_cache
            synthesis = cache.synthesis_cache.get("synthesis_thematic")
            if synthesis:
                try:
                    synthesis_data = json.loads(synthesis)
                    themes = synthesis_data.get("themes", [])
                except json.JSONDecodeError:
                    themes = []
        
        if not themes:
            return {
                "type": "concept_map",
                "format": "mermaid",
                "specification": "graph TD\n    A[No themes available]",
                "message": "Run synthesis first to generate concept map"
            }
        
        # Build Mermaid concept map
        lines = ["graph TD"]
        lines.append(f"    ROOT[{self.state.title[:50]}]")
        
        for i, theme in enumerate(themes[:6]):
            theme_name = theme.get("theme_name", f"Theme {i+1}")
            theme_id = f"T{i}"
            lines.append(f"    {theme_id}[{theme_name}]")
            lines.append(f"    ROOT --> {theme_id}")
            
            # Add subthemes
            for j, subtheme in enumerate(theme.get("subthemes", [])[:3]):
                sub_name = subtheme.get("name", f"Subtheme {j+1}")
                sub_id = f"S{i}_{j}"
                lines.append(f"    {sub_id}[{sub_name}]")
                lines.append(f"    {theme_id} --> {sub_id}")
        
        mermaid_spec = "\n".join(lines)
        
        return {
            "type": "concept_map",
            "format": "mermaid",
            "specification": mermaid_spec,
            "themes_count": len(themes),
            "caption": "Figure 2: Concept map of main themes and subthemes."
        }
    
    async def _create_chart_spec(
        self,
        chart_type: str = "bar",
        data: Optional[dict] = None,
        **kwargs
    ) -> dict:
        """Create chart specification for Plotly/Vega."""
        
        if not data:
            return {"error": "No data provided for chart"}
        
        if chart_type == "bar":
            spec = {
                "type": "bar",
                "data": {
                    "labels": list(data.keys()),
                    "values": list(data.values())
                },
                "layout": {
                    "title": kwargs.get("title", "Distribution"),
                    "xaxis": {"title": kwargs.get("x_label", "Category")},
                    "yaxis": {"title": kwargs.get("y_label", "Count")}
                }
            }
        elif chart_type == "pie":
            spec = {
                "type": "pie",
                "data": {
                    "labels": list(data.keys()),
                    "values": list(data.values())
                },
                "layout": {
                    "title": kwargs.get("title", "Distribution")
                }
            }
        else:
            spec = {"error": f"Unknown chart type: {chart_type}"}
        
        return {
            "type": "chart",
            "chart_type": chart_type,
            "specification": spec
        }
    
    def _enrich_result(self, result: AgentResult) -> AgentResult:
        """Add visualizer metadata."""
        if isinstance(result.output, dict):
            result.handoff_data = {
                "visualizations_ready": True,
                "count": result.output.get("generated_count", 0)
            }
        return result
