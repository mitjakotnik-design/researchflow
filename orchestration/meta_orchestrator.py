"""Meta-Orchestrator: Central controller for the multi-agent system."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

import structlog

from config import (
    StateManager,
    ArticleState,
    ArticlePhase,
    OrchestratorState,
    ModelsConfig,
    QualityThresholds,
    QualityGates,
    SaturationConfig,
    SectionsConfig,
    SectionStatus,
    REVIEW_SECTIONS,
)
from agents import BaseAgent, AgentContext, AgentResult
from rag import HybridSearch, CohereReranker, QueryDecomposer


logger = structlog.get_logger()


class ExecutionMode(Enum):
    """Orchestrator execution modes."""
    SEQUENTIAL = "sequential"      # One section at a time
    PARALLEL = "parallel"          # Independent sections in parallel
    INTERACTIVE = "interactive"    # Pause for human input


@dataclass
class OrchestratorConfig:
    """Configuration for the Meta-Orchestrator."""
    
    # Execution
    mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    max_concurrent_agents: int = 3
    
    # Timeouts
    section_timeout_seconds: int = 600
    agent_timeout_seconds: int = 120
    
    # Quality
    saturation_config: SaturationConfig = field(default_factory=SaturationConfig)
    quality_thresholds: QualityThresholds = field(default_factory=QualityThresholds)
    quality_gates: QualityGates = field(default_factory=QualityGates)
    
    # Recovery
    max_retries_per_agent: int = 3
    checkpoint_frequency: int = 1  # Checkpoint every N sections
    
    # Observability
    verbose: bool = False
    log_agent_calls: bool = True


class MetaOrchestrator:
    """
    Central orchestrator managing the entire article writing workflow.
    
    Responsibilities:
    - Coordinate agent execution across phases
    - Manage state transitions and checkpoints
    - Handle error recovery and rollback
    - Trigger human review when needed
    - Track progress and quality metrics
    """
    
    def __init__(
        self,
        config: OrchestratorConfig,
        state_manager: StateManager,
        models_config: ModelsConfig
    ):
        self.config = config
        self.state_manager = state_manager
        self.models_config = models_config
        
        self.log = structlog.get_logger().bind(component="meta_orchestrator")
        
        # Agent registry
        self._agents: dict[str, BaseAgent] = {}
        
        # RAG components
        self._hybrid_search: Optional[HybridSearch] = None
        self._reranker: Optional[CohereReranker] = None
        self._query_decomposer: Optional[QueryDecomposer] = None
        
        # Sections config
        self._sections_config = SectionsConfig()
        
        # Execution tracking
        self._current_section: Optional[str] = None
        self._sections_completed: int = 0
        
        # Agent dependency graph
        self._agent_dependencies = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> dict[str, list[str]]:
        """Build agent dependency graph."""
        return {
            # Research cluster - can run in parallel
            "researcher": [],
            "literature_scout": [],
            
            # Data cluster - depends on research
            "data_extractor": ["researcher"],
            "meta_analyst": ["data_extractor"],
            "gap_identifier": ["researcher", "meta_analyst"],
            
            # Writing cluster
            "writer": ["researcher", "data_extractor"],
            "synthesizer": ["data_extractor", "meta_analyst"],
            
            # Quality cluster - depends on content
            "multi_evaluator": ["writer"],
            "critic": ["writer"],
            "fact_checker": ["writer"],
            "consistency_checker": ["writer"],
            "bias_auditor": ["synthesizer"],
            "methodology_validator": ["writer"],
            
            # Editing cluster
            "academic_editor": ["writer", "multi_evaluator"],
            "terminology_guardian": ["writer"],
            "citation_manager": ["writer"],
            "visualizer": ["data_extractor", "synthesizer"],
        }
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self._agents[agent.name] = agent
        self.log.info("agent_registered", agent=agent.name, role=agent.role.value)
    
    def register_agents(self, agents: list[BaseAgent]) -> None:
        """Register multiple agents."""
        for agent in agents:
            self.register_agent(agent)
    
    def setup_rag(
        self,
        hybrid_search: HybridSearch,
        reranker: Optional[CohereReranker] = None
    ) -> None:
        """Set up RAG components."""
        self._hybrid_search = hybrid_search
        self._reranker = reranker
        self._query_decomposer = QueryDecomposer()
        self.log.info("rag_configured")
    
    async def initialize_article(
        self,
        title: str,
        article_id: Optional[str] = None,
        target_journal: str = "",
        language: str = "en"
    ) -> ArticleState:
        """Initialize a new article."""
        article_id = article_id or f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create article state
        article_state = self.state_manager.create_new_article(
            article_id=article_id,
            title=title,
            target_journal=target_journal,
            language=language
        )
        
        # Initialize sections
        self._sections_config.initialize_states()
        
        # Initialize all agents
        context = self._create_agent_context()
        for agent in self._agents.values():
            agent.initialize(context)
        
        # Create initial checkpoint
        self.state_manager.create_checkpoint("initial")
        
        self.log.info(
            "article_initialized",
            article_id=article_id,
            title=title,
            agent_count=len(self._agents)
        )
        
        return article_state
    
    def _create_agent_context(self) -> AgentContext:
        """Create context for agents."""
        return AgentContext(
            state_manager=self.state_manager,
            models_config=self.models_config,
            quality_thresholds=self.config.quality_thresholds,
            rag_query=self._rag_query if self._hybrid_search else None,
            send_to_agent=self._route_message,
            parallel_quality_checks=self.config.mode == ExecutionMode.PARALLEL,
            verbose=self.config.verbose
        )
    
    async def _rag_query(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None
    ) -> list[dict]:
        """Execute RAG query."""
        if not self._hybrid_search:
            return []
        
        results = await self._hybrid_search.search(
            query=query,
            top_k=top_k * 2,
            filters=filters
        )
        
        # Optionally rerank
        if self._reranker and len(results) > 5:
            results = await self._reranker.rerank(query, results, top_k)
        
        return [r.to_dict() for r in results[:top_k]]
    
    async def _route_message(
        self,
        from_agent: str,
        to_agent: str,
        message: dict
    ) -> Optional[AgentResult]:
        """Route message between agents."""
        if to_agent not in self._agents:
            self.log.warning("unknown_agent", agent=to_agent)
            return None
        
        target_agent = self._agents[to_agent]
        action = message.get("action", "process")
        
        return await target_agent.execute(action, **message)
    
    async def run(self) -> ArticleState:
        """Run the complete article writing workflow."""
        state = self.state_manager.state
        state.orchestrator_state = OrchestratorState.RUNNING
        
        try:
            # Phase 1: Research
            await self._run_research_phase()
            
            # Phase 2: Data Extraction
            await self._run_extraction_phase()
            
            # Phase 3: Synthesis
            await self._run_synthesis_phase()
            
            # Phase 4: Writing
            await self._run_writing_phase()
            
            # Phase 5: Quality Assurance
            await self._run_qa_phase()
            
            # Phase 6: Finalization
            await self._run_finalization_phase()
            
            state.current_phase = ArticlePhase.COMPLETED
            state.orchestrator_state = OrchestratorState.COMPLETED
            
            self.log.info("article_completed", article_id=state.article_id)
            
        except Exception as e:
            state.orchestrator_state = OrchestratorState.ERROR
            state.log_error("meta_orchestrator", "workflow_error", str(e))
            self.log.error("workflow_failed", error=str(e))
            raise
        
        finally:
            self.state_manager.save_state()
        
        return state
    
    async def _run_research_phase(self) -> None:
        """Run research phase."""
        self.log.info("phase_started", phase="research")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.RESEARCH
        
        # Run researcher and literature scout in parallel
        tasks = []
        
        if "researcher" in self._agents:
            tasks.append(self._agents["researcher"].execute(
                "research",
                section="introduction"
            ))
        
        if "literature_scout" in self._agents:
            tasks.append(self._agents["literature_scout"].execute(
                "scout",
                research_questions=state.title
            ))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    self.log.error("research_agent_failed", error=str(r))
        
        self.log.info("phase_completed", phase="research")
    
    async def _run_extraction_phase(self) -> None:
        """Run data extraction phase."""
        self.log.info("phase_started", phase="extraction")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.DATA_EXTRACTION
        
        if "data_extractor" in self._agents:
            await self._agents["data_extractor"].execute("extract")
        
        if "meta_analyst" in self._agents:
            await self._agents["meta_analyst"].execute("analyze")
        
        self.log.info("phase_completed", phase="extraction")
    
    async def _run_synthesis_phase(self) -> None:
        """Run synthesis phase."""
        self.log.info("phase_started", phase="synthesis")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.SYNTHESIS
        
        if "synthesizer" in self._agents:
            await self._agents["synthesizer"].execute("synthesize")
        
        if "gap_identifier" in self._agents:
            await self._agents["gap_identifier"].execute("identify_gaps")
        
        self.log.info("phase_completed", phase="synthesis")
    
    async def _run_writing_phase(self) -> None:
        """Run writing phase for all sections."""
        self.log.info("phase_started", phase="writing")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.WRITING
        
        # Process sections in order
        ordered_sections = self._sections_config.get_ordered_sections()
        
        for section_spec in ordered_sections:
            section_id = section_spec.id
            self._current_section = section_id
            
            self.log.info("section_started", section=section_id)
            
            # Import saturation loop
            from .saturation_loop import SaturationLoop
            
            saturation_loop = SaturationLoop(
                config=self.config.saturation_config,
                section_spec=section_spec,
                agents=self._agents,
                quality_gates=self.config.quality_gates
            )
            
            # Initialize section state
            section_state = state.sections.get(section_id)
            if section_state:
                section_state.status = SectionStatus.IN_PROGRESS
            
            # Run saturation loop
            result = await saturation_loop.run(section_state)
            
            # Update state
            if result.success:
                section_state.status = SectionStatus.APPROVED
                section_state.content = result.final_content
                section_state.current_score = result.final_score
            else:
                section_state.status = SectionStatus.REVISION_NEEDED
                
                # Check if human review needed
                if result.needs_human_review:
                    state.request_human_review(
                        reason=result.human_review_reason,
                        context={"section": section_id}
                    )
            
            # Checkpoint after each section
            if self._sections_completed % self.config.checkpoint_frequency == 0:
                self.state_manager.create_checkpoint(f"section_{section_id}")
            
            self._sections_completed += 1
            self.log.info(
                "section_completed",
                section=section_id,
                score=section_state.current_score if section_state else 0
            )
        
        self.log.info("phase_completed", phase="writing")
    
    async def _run_qa_phase(self) -> None:
        """Run quality assurance phase."""
        self.log.info("phase_started", phase="qa")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.QUALITY_ASSURANCE
        
        # Run quality checks in parallel
        qa_agents = ["fact_checker", "consistency_checker", "bias_auditor"]
        tasks = []
        
        for agent_name in qa_agents:
            if agent_name in self._agents:
                tasks.append(self._agents[agent_name].execute("check"))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    self.log.error("qa_agent_failed", error=str(r))
        
        # Final methodology validation
        if "methodology_validator" in self._agents:
            await self._agents["methodology_validator"].execute("validate")
        
        self.log.info("phase_completed", phase="qa")
    
    async def _run_finalization_phase(self) -> None:
        """Run finalization phase."""
        self.log.info("phase_started", phase="finalization")
        state = self.state_manager.state
        state.current_phase = ArticlePhase.FINALIZATION
        
        # Academic editing
        if "academic_editor" in self._agents:
            await self._agents["academic_editor"].execute("edit")
        
        # Generate visualizations
        if "visualizer" in self._agents:
            await self._agents["visualizer"].execute("generate")
        
        # Final citation check
        if "citation_manager" in self._agents:
            await self._agents["citation_manager"].execute("finalize")
        
        # Take final quality snapshot
        state.take_quality_snapshot()
        
        # Create final checkpoint
        self.state_manager.create_checkpoint("final")
        
        self.log.info("phase_completed", phase="finalization")
    
    async def rollback_to(self, checkpoint_name: str) -> ArticleState:
        """Rollback to a previous checkpoint."""
        self.log.info("rollback_initiated", checkpoint=checkpoint_name)
        
        state = self.state_manager.rollback_to_checkpoint(checkpoint_name)
        
        # Reinitialize agents with restored state
        context = self._create_agent_context()
        for agent in self._agents.values():
            agent.initialize(context)
        
        return state
    
    def get_status(self) -> dict:
        """Get current orchestrator status."""
        state = self.state_manager.state
        
        return {
            "article_id": state.article_id,
            "phase": state.current_phase.value,
            "state": state.orchestrator_state.value,
            "progress": state.get_overall_progress(),
            "current_section": self._current_section,
            "sections_completed": self._sections_completed,
            "registered_agents": list(self._agents.keys()),
            "checkpoints": self.state_manager.list_checkpoints(),
        }
    
    def pause(self) -> None:
        """Pause orchestration."""
        self.state_manager.state.orchestrator_state = OrchestratorState.PAUSED
        self.state_manager.save_state()
        self.log.info("orchestrator_paused")
    
    def resume(self) -> None:
        """Resume orchestration."""
        self.state_manager.state.orchestrator_state = OrchestratorState.RUNNING
        self.log.info("orchestrator_resumed")
