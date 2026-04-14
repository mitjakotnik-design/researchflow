"""Basic tests for the multi-agent system."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch


class TestConfig:
    """Test configuration modules."""
    
    def test_models_config_import(self):
        from config import ModelsConfig, ModelTier
        config = ModelsConfig()
        assert config.get_model_for_agent("writer") is not None
        assert ModelTier.PRO.value == "pro"
    
    def test_quality_thresholds_import(self):
        from config import QualityThresholds, QualityGates, QualityVerdict
        thresholds = QualityThresholds()
        assert thresholds.target_score == 85
        assert thresholds.get_verdict(90) == QualityVerdict.ACCEPT
    
    def test_sections_config_import(self):
        from config import SectionsConfig, REVIEW_SECTIONS
        assert "introduction" in REVIEW_SECTIONS
        assert "methods" in REVIEW_SECTIONS
        assert "results" in REVIEW_SECTIONS
    
    def test_state_manager_import(self):
        from config import StateManager, ArticleState, ArticlePhase
        assert ArticlePhase.WRITING.value == "writing"


class TestAgents:
    """Test agent modules."""
    
    def test_base_agent_import(self):
        from agents import BaseAgent, AgentResult, AgentRole
        assert AgentRole.RESEARCH.value == "research"
        assert AgentRole.WRITING.value == "writing"
        assert AgentRole.QUALITY.value == "quality"
    
    def test_all_agents_import(self):
        from agents import (
            ResearcherAgent,
            LiteratureScoutAgent,
            DataExtractorAgent,
            MetaAnalystAgent,
            GapIdentifierAgent,
            WriterAgent,
            SynthesizerAgent,
            AcademicEditorAgent,
            TerminologyGuardianAgent,
            CitationManagerAgent,
            VisualizerAgent,
            MultiEvaluatorAgent,
            FactCheckerAgent,
            ConsistencyCheckerAgent,
            BiasAuditorAgent,
            CriticAgent,
            MethodologyValidatorAgent,
        )
        
        # Test instantiation
        agents = [
            ResearcherAgent(),
            LiteratureScoutAgent(),
            DataExtractorAgent(),
            MetaAnalystAgent(),
            GapIdentifierAgent(),
            WriterAgent(),
            SynthesizerAgent(),
            AcademicEditorAgent(),
            TerminologyGuardianAgent(),
            CitationManagerAgent(),
            VisualizerAgent(),
            MultiEvaluatorAgent(),
            FactCheckerAgent(),
            ConsistencyCheckerAgent(),
            BiasAuditorAgent(),
            CriticAgent(),
            MethodologyValidatorAgent(),
        ]
        
        assert len(agents) == 17
        
        for agent in agents:
            assert agent.name is not None
            assert agent.role is not None


class TestRAG:
    """Test RAG modules."""
    
    def test_hybrid_search_import(self):
        from rag import HybridSearch, SearchResult
        # Just test import, not initialization (requires API keys)
        assert SearchResult is not None
    
    def test_query_decomposer_import(self):
        from rag import QueryDecomposer
        decomposer = QueryDecomposer()
        assert decomposer is not None
    
    def test_reranker_import(self):
        from rag import Reranker, NoOpReranker
        reranker = NoOpReranker()
        assert reranker is not None


class TestOrchestration:
    """Test orchestration modules."""
    
    def test_orchestrator_import(self):
        from orchestration import MetaOrchestrator, OrchestratorConfig
        config = OrchestratorConfig()
        assert config.max_concurrent_agents == 3
    
    def test_saturation_loop_import(self):
        from orchestration import SaturationLoop, SaturationResult
        assert SaturationResult is not None


class TestObservability:
    """Test observability modules."""
    
    def test_logger_import(self):
        from observability import configure_logging, get_logger
        logger = get_logger("test")
        assert logger is not None
    
    def test_metrics_import(self):
        from observability import MetricsCollector
        metrics = MetricsCollector()
        metrics.increment("test_counter")
        assert metrics.get_counter("test_counter") == 1


class TestIntegration:
    """Integration tests."""
    
    def test_full_import_chain(self):
        """Test that all modules can be imported together."""
        from config import (
            ModelsConfig,
            QualityThresholds,
            StateManager,
            SectionsConfig,
        )
        from agents import (
            BaseAgent,
            WriterAgent,
            MultiEvaluatorAgent,
        )
        from rag import HybridSearch, QueryDecomposer
        from orchestration import MetaOrchestrator, SaturationLoop
        from observability import configure_logging, MetricsCollector
        
        # All imports successful
        assert True
    
    @pytest.mark.asyncio
    async def test_query_decomposer_rule_based(self):
        """Test query decomposer without LLM."""
        from rag import QueryDecomposer
        
        decomposer = QueryDecomposer()
        result = await decomposer.decompose(
            "What is the impact of AI on HR practices?",
            use_llm=False
        )
        
        assert result.original_query is not None
        assert len(result.sub_queries) >= 1
        assert len(result.concepts) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
