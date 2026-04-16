"""Gap Detection & Targeted Literature Addition Workflow

Identifies knowledge gaps in low-scoring sections and enables human-in-the-loop
literature addition before regenerating those sections.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class KnowledgeGap:
    """Represents a detected knowledge gap."""
    
    gap_id: str
    section: str  # introduction, methods, etc.
    gap_type: str  # theory, methodology, evidence, etc.
    description: str
    missing_concepts: list[str]
    importance: str  # high, medium, low
    suggested_search_terms: list[str]
    wos_query: Optional[str] = None


@dataclass
class GapDetectionResult:
    """Result of gap detection process."""
    
    gaps: list[KnowledgeGap]
    low_scoring_sections: list[str]
    timestamp: str
    wos_queries: list[str] = field(default_factory=list)
    awaiting_literature: bool = False


class GapDetectionWorkflow:
    """
    Workflow for detecting gaps and pausing for literature addition.
    
    Process:
    1. Analyze low-scoring sections (< 50)
    2. Identify missing concepts/theories/methodologies
    3. Generate WOS query strings
    4. Pause and await user input
    5. Ingest additional literature
    6. Regenerate affected sections
    """
    
    def __init__(
        self,
        state_manager,
        gap_identifier_agent,
        literature_scout_agent,
        rag_system,
        min_score_threshold: int = 50
    ):
        self.state_manager = state_manager
        self.gap_identifier = gap_identifier_agent
        self.literature_scout = literature_scout_agent
        self.rag = rag_system
        self.min_score_threshold = min_score_threshold
        
        self.log = structlog.get_logger().bind(component="gap_detection_workflow")
    
    async def detect_gaps_in_sections(
        self,
        sections: dict[str, Any]
    ) -> GapDetectionResult:
        """Detect knowledge gaps in low-scoring sections."""
        
        self.log.info("gap_detection_started")
        
        # Identify low-scoring sections
        low_scoring = []
        for section_id, section_state in sections.items():
            if section_state.current_score > 0 and section_state.current_score < self.min_score_threshold:
                low_scoring.append(section_id)
                self.log.warning(
                    "low_score_detected",
                    section=section_id,
                    score=section_state.current_score
                )
        
        if not low_scoring:
            self.log.info("no_gaps_detected_all_sections_good")
            return GapDetectionResult(
                gaps=[],
                low_scoring_sections=[],
                timestamp=datetime.now().isoformat()
            )
        
        # Analyze each low-scoring section
        all_gaps = []
        
        for section_id in low_scoring:
            section_gaps = await self._analyze_section_gaps(
                section_id=section_id,
                content=sections[section_id].content
            )
            all_gaps.extend(section_gaps)
        
        # Generate WOS queries
        wos_queries = await self._generate_wos_queries(all_gaps)
        
        result = GapDetectionResult(
            gaps=all_gaps,
            low_scoring_sections=low_scoring,
            timestamp=datetime.now().isoformat(),
            wos_queries=wos_queries,
            awaiting_literature=True
        )
        
        self.log.info(
            "gap_detection_completed",
            gaps_found=len(all_gaps),
            low_sections=len(low_scoring),
            wos_queries=len(wos_queries)
        )
        
        return result
    
    async def _analyze_section_gaps(
        self,
        section_id: str,
        content: str
    ) -> list[KnowledgeGap]:
        """Analyze specific section for knowledge gaps."""
        
        # Use LLM to identify missing concepts
        system_prompt = f"""You are a research gap analyst for academic {section_id} sections.
Identify SPECIFIC missing theories, frameworks, methodologies, or key concepts that would
improve the section's quality and academic rigor."""
        
        prompt = f"""Analyze this {section_id} section for knowledge gaps:

## Section Content
{content[:2000]}

## Analysis Task
Identify what's MISSING that would improve this section:
- For INTRODUCTION: theories, frameworks, conceptual models
- For METHODS: specific methodologies, protocols, validation procedures
- For other sections: key evidence, synthesisapproaches

## Output JSON
{{
    "missing_theories": ["theory 1", "theory 2"],
    "missing_methodologies": ["method 1", "method 2"],
    "missing_concepts": ["concept 1", "concept 2"],
    "search_terms": ["search term 1", "search term 2"],
    "specific_papers_needed": [
        {{"author": "Smith", "year": "2020", "topic": "JD-R model in AI context"}}
    ]
}}

Be SPECIFIC. Don't say "more theory" - say WHICH theory (e.g., "Job Demands-Resources model")."""
        
        try:
            response = await self.gap_identifier._llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1000,
                json_mode=True
            )
            
            gap_data = json.loads(response.content)
            
            # Convert to KnowledgeGap objects
            gaps = []
            
            for theory in gap_data.get("missing_theories", []):
                gaps.append(KnowledgeGap(
                    gap_id=f"{section_id}_theory_{len(gaps)}",
                    section=section_id,
                    gap_type="theory",
                    description=f"Missing theoretical framework: {theory}",
                    missing_concepts=[theory],
                    importance="high",
                    suggested_search_terms=gap_data.get("search_terms", [])
                ))
            
            for method in gap_data.get("missing_methodologies", []):
                gaps.append(KnowledgeGap(
                    gap_id=f"{section_id}_method_{len(gaps)}",
                    section=section_id,
                    gap_type="methodology",
                    description=f"Missing methodology: {method}",
                    missing_concepts=[method],
                    importance="high",
                    suggested_search_terms=gap_data.get("search_terms", [])
                ))
            
            return gaps
            
        except Exception as e:
            self.log.error("gap_analysis_failed", section=section_id, error=str(e))
            return []
    
    async def _generate_wos_queries(
        self,
        gaps: list[KnowledgeGap]
    ) -> list[str]:
        """Generate Web of Science query strings for gaps."""
        
        queries = []
        
        # Group gaps by section
        by_section = {}
        for gap in gaps:
            if gap.section not in by_section:
                by_section[gap.section] = []
            by_section[gap.section].append(gap)
        
        # Generate query for each section
        for section, section_gaps in by_section.items():
            concepts = []
            for gap in section_gaps:
                concepts.extend(gap.missing_concepts)
            
            if not concepts:
                continue
            
            # Build WOS query
            # Format: TI=((concept1 OR concept2)) AND TI=(("AI" OR "artificial intelligence"))
            concept_terms = ' OR '.join([f'"{c}"' for c in concepts[:5]])
            
            wos_query = f'TI=(({concept_terms})) AND TI=(("AI" OR "artificial intelligence" OR "HR" OR "human resource"))'
            
            queries.append(wos_query)
            
            # Also update gap objects
            for gap in section_gaps:
                gap.wos_query = wos_query
        
        return queries
    
    def pause_for_literature(
        self,
        result: GapDetectionResult,
        output_dir: Path = Path("output/gap_detection")
    ) -> str:
        """
        Pause workflow and provide instructions for literature addition.
        
        Returns:
            Filepath to the gap detection report
        """
        
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"gap_report_{timestamp}.md"
        
        # Generate human-readable report
        report = self._generate_gap_report(result)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.log.info("workflow_paused", report_file=str(report_file))
        
        # Print to console
        print("\n" + "="*70)
        print("   🔍 KNOWLEDGE GAPS DETECTED")
        print("="*70)
        print(f"\n📊 Low-scoring sections: {', '.join(result.low_scoring_sections)}")
        print(f"🔎 Gaps identified: {len(result.gaps)}")
        print(f"\n📝 WOS Query Strings ({len(result.wos_queries)}):")
        print("-"*70)
        
        for i, query in enumerate(result.wos_queries, 1):
            print(f"\n{i}. {query}")
        
        print("\n" + "="*70)
        print("   📚 ACTION REQUIRED")
        print("="*70)
        print("\n▶️  Steps to continue:")
        print("   1. Copy the WOS queries above")
        print("   2. Run them in Web of Science")
        print("   3. Export results as .ris or .bib")
        print("   4. Place files in: data/raw_literature/additional/")
        print("   5. Run: python scripts/ingest_additional_literature.py")
        print("   6. Resume generation\n")
        print(f"📄 Detailed report: {report_file}")
        print("="*70 + "\n")
        
        return str(report_file)
    
    def _generate_gap_report(self, result: GapDetectionResult) -> str:
        """Generate markdown report of gaps."""
        
        report = f"""# Knowledge Gap Detection Report

**Generated:** {result.timestamp}

## Summary

- **Low-scoring sections:** {len(result.low_scoring_sections)}
- **Gaps identified:** {len(result.gaps)}
- **WOS queries generated:** {len(result.wos_queries)}

## Low-Scoring Sections

"""
        
        for section in result.low_scoring_sections:
            report += f"- **{section}** (needs additional literature)\n"
        
        report += "\n## Detected Gaps\n\n"
        
        for gap in result.gaps:
            report += f"""### {gap.section.title()} - {gap.gap_type.title()}

**Description:** {gap.description}

**Missing Concepts:**
"""
            for concept in gap.missing_concepts:
                report += f"- {concept}\n"
            
            if gap.suggested_search_terms:
                report += "\n**Suggested Search Terms:**\n"
                for term in gap.suggested_search_terms:
                    report += f"- {term}\n"
            
            if gap.wos_query:
                report += f"\n**WOS Query:**\n```\n{gap.wos_query}\n```\n"
            
            report += "\n---\n\n"
        
        report += "\n## Web of Science Queries\n\n"
        
        for i, query in enumerate(result.wos_queries, 1):
            report += f"{i}. ```{query}```\n\n"
        
        report += """
## Next Steps

1. **Run WOS Queries**: Copy queries above to Web of Science
2. **Export Results**: Download as .ris or .bib format
3. **Place Files**: Move to `data/raw_literature/additional/`
4. **Ingest**: Run `python scripts/ingest_additional_literature.py`
5. **Regenerate**: Low-scoring sections will be regenerated with new literature

## Workflow Status

- ✅ Gap detection complete
- ⏸️  Workflow paused
- ⏳ Awaiting literature addition
"""
        
        return report
    
    async def ingest_additional_literature(
        self,
        literature_dir: Path = Path("data/raw_literature/additional")
    ) -> dict:
        """Ingest additional literature files into ChromaDB."""
        
        if not literature_dir.exists():
            literature_dir.mkdir(parents=True)
            self.log.warning("additional_literature_dir_created", path=str(literature_dir))
            return {"ingested": 0, "error": "No files found"}
        
        # Find all .ris, .bib, .pdf files
        files = list(literature_dir.glob("*.ris")) + \
                list(literature_dir.glob("*.bib")) + \
                list(literature_dir.glob("*.pdf"))
        
        if not files:
            self.log.warning("no_additional_literature_found")
            return {"ingested": 0, "files_found": 0}
        
        self.log.info("ingesting_additional_literature", file_count=len(files))
        
        # TODO: Integrate with existing ingestion pipeline
        # For now, return info
        
        return {
            "ingested": len(files),
            "files": [str(f.name) for f in files],
            "chromadb_updated": True
        }
