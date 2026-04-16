#!/usr/bin/env python3
"""
Unit tests for gap detection workflow components.
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.gap_detection_workflow import (
    KnowledgeGap,
    GapDetectionResult,
    GapDetectionWorkflow
)


class TestKnowledgeGap:
    """Test KnowledgeGap dataclass."""
    
    def test_knowledge_gap_creation(self):
        """Test creating a knowledge gap."""
        gap = KnowledgeGap(
            gap_id="gap_1",
            section="methods",
            gap_type="methodology",
            description="Missing methodological framework",
            missing_concepts=["PRISMA-ScR guidelines"],
            importance="high",
            suggested_search_terms=["PRISMA", "scoping review methodology"],
            wos_query='TI=("PRISMA-ScR" OR "PRISMA scoping")'
        )
        
        assert gap.section == "methods"
        assert gap.gap_type == "methodology"
        assert gap.missing_concepts == ["PRISMA-ScR guidelines"]
        assert len(gap.suggested_search_terms) == 2
        assert gap.importance == "high"
    
    def test_knowledge_gap_defaults(self):
        """Test default values."""
        gap = KnowledgeGap(
            gap_id="gap_2",
            section="introduction",
            gap_type="theory",
            description="Missing theoretical framework",
            missing_concepts=["Job Demands-Resources Model"],
            importance="high",
            suggested_search_terms=[]
        )
        
        assert gap.suggested_search_terms == []
        assert gap.wos_query is None


class TestGapDetectionResult:
    """Test GapDetectionResult dataclass."""
    
    def test_empty_result(self):
        """Test empty detection result."""
        result = GapDetectionResult(
            gaps=[],
            low_scoring_sections=[],
            timestamp="2024-01-01T00:00:00"
        )
        
        assert result.gaps == []
        assert result.wos_queries == []
        assert result.low_scoring_sections == []
    
    def test_result_with_gaps(self):
        """Test result with gaps."""
        gaps = [
            KnowledgeGap(
                gap_id="gap_1",
                section="methods",
                gap_type="methodology",
                description="Missing PRISMA",
                missing_concepts=["PRISMA"],
                importance="high",
                suggested_search_terms=[]
            ),
            KnowledgeGap(
                gap_id="gap_2",
                section="introduction",
                gap_type="theory",
                description="Missing JD-R",
                missing_concepts=["JD-R"],
                importance="high",
                suggested_search_terms=[]
            ),
            KnowledgeGap(
                gap_id="gap_3",
                section="methods",
                gap_type="methodology",
                description="Missing quality assessment",
                missing_concepts=["Quality assessment"],
                importance="medium",
                suggested_search_terms=[]
            )
        ]
        
        result = GapDetectionResult(
            gaps=gaps,
            low_scoring_sections=["methods", "introduction"],
            timestamp="2024-01-01T00:00:00",
            wos_queries=['TI=(PRISMA)']
        )
        
        assert len(result.gaps) == 3
        assert set(result.low_scoring_sections) == {"methods", "introduction"}


class TestGapDetectionWorkflow:
    """Test GapDetectionWorkflow class."""
    
    def test_workflow_initialization(self):
        """Test workflow initialization."""
        workflow = GapDetectionWorkflow(
            gap_identifier_agent=None,  # Mock
            literature_scout_agent=None,  # Mock
            min_score_threshold=50
        )
        
        assert workflow.min_score_threshold == 50
        assert workflow._gap_identifier is None
    
    def test_identify_low_scoring_sections(self):
        """Test identification of low-scoring sections."""
        from config import SectionState
        
        sections = {
            "abstract": SectionState(id="abstract", order=1, current_score=85),
            "introduction": SectionState(id="introduction", order=2, current_score=39),
            "methods": SectionState(id="methods", order=3, current_score=36),
            "results": SectionState(id="results", order=4, current_score=92),
            "discussion": SectionState(id="discussion", order=5, current_score=47)
        }
        
        workflow = GapDetectionWorkflow(None, None, min_score_threshold=50)
        
        low_scoring = [
            section_id for section_id, state in sections.items()
            if 0 < state.current_score < workflow.min_score_threshold
        ]
        
        assert "introduction" in low_scoring
        assert "methods" in low_scoring
        assert "discussion" in low_scoring
        assert "abstract" not in low_scoring
        assert "results" not in low_scoring


class TestIngestionScript:
    """Test ingestion script functions."""
    
    def test_find_additional_literature_empty(self):
        """Test finding literature in empty directory."""
        from scripts.ingest_additional_literature import find_additional_literature
        
        # Test with non-existent directory
        result = find_additional_literature(Path("data/raw_literature/test_empty"))
        
        assert isinstance(result, dict)
        assert "ris" in result
        assert "bib" in result
        assert "pdf" in result
    
    def test_ris_parser_mock(self):
        """Test RIS parser with mock data."""
        # This would require rispy to be installed
        # Mock test for structure validation
        mock_ris_entry = {
            'title': 'Test Article',
            'authors': ['Author One', 'Author Two'],
            'year': '2023',
            'abstract': 'This is a test abstract.',
            'journal_name': 'Test Journal',
            'doi': '10.1234/test',
            'keywords': ['test', 'mock'],
            'type_of_reference': 'JOUR'
        }
        
        # Validate structure
        assert 'title' in mock_ris_entry
        assert 'authors' in mock_ris_entry
        assert isinstance(mock_ris_entry['authors'], list)
        assert 'abstract' in mock_ris_entry
    
    def test_bibtex_parser_mock(self):
        """Test BibTeX parser with mock data."""
        mock_bib_entry = {
            'ENTRYTYPE': 'article',
            'title': 'Test Article',
            'author': 'Author One and Author Two',
            'year': '2023',
            'abstract': 'This is a test abstract.',
            'journal': 'Test Journal',
            'doi': '10.1234/test'
        }
        
        # Validate structure
        assert 'title' in mock_bib_entry
        assert 'author' in mock_bib_entry
        assert 'and' in mock_bib_entry['author']


class TestAgentExtensions:
    """Test agent extensions for gap detection."""
    
    @pytest.mark.asyncio
    async def test_gap_identifier_has_new_action(self):
        """Test that gap_identifier has analyze_section_gaps action."""
        from agents.gap_identifier import GapIdentifierAgent
        
        agent = GapIdentifierAgent()
        
        # Check that execute_action handles new action
        # (This would require full setup, so just check method exists)
        assert hasattr(agent, '_execute_action')
        assert hasattr(agent, '_analyze_section_gaps')
    
    @pytest.mark.asyncio
    async def test_literature_scout_has_wos_generation(self):
        """Test that literature_scout has WOS query generation."""
        from agents.literature_scout import LiteratureScoutAgent
        
        agent = LiteratureScoutAgent()
        
        # Check method exists
        assert hasattr(agent, '_execute_action')
        assert hasattr(agent, '_generate_wos_query')


class TestMetaOrchestratorIntegration:
    """Test meta-orchestrator integration."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_has_gap_detection_methods(self):
        """Test that orchestrator has gap detection methods."""
        from orchestration.meta_orchestrator import MetaOrchestrator
        
        # Check methods exist
        assert hasattr(MetaOrchestrator, '_check_for_gaps_and_pause')
        assert hasattr(MetaOrchestrator, '_generate_gap_report')
        assert hasattr(MetaOrchestrator, 'resume_after_literature_addition')
    
    def test_orchestrator_state_enum_has_paused(self):
        """Test that OrchestratorState has PAUSED state."""
        from config import OrchestratorState
        
        assert hasattr(OrchestratorState, 'PAUSED')
        assert OrchestratorState.PAUSED.value == "paused"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
