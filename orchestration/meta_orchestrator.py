"""Meta-Orchestrator: Central controller for the multi-agent system."""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
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
    gap_detection_threshold: int = 50  # Minimum score to trigger gap detection
    
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
        
        # IMPROVEMENT: Process independent sections in parallel
        ordered_sections = self._sections_config.get_ordered_sections()
        
        # Group sections by dependency
        # Parallel group 1: abstract, methods, results (independent)
        # Sequential: introduction -> discussion -> conclusion
        
        parallel_group = []
        sequential_group = []
        
        for section_spec in ordered_sections:
            if section_spec.id in ["abstract", "methods", "results"]:
                parallel_group.append(section_spec)
            else:
                sequential_group.append(section_spec)
        
        # Process parallel group concurrently
        if parallel_group and self.config.mode == ExecutionMode.PARALLEL:
            self.log.info("parallel_sections_started", count=len(parallel_group))
            tasks = [
                self._process_section(spec)
                for spec in parallel_group
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # Fallback to sequential if not in parallel mode
            for section_spec in parallel_group:
                await self._process_section(section_spec)
        
        # Process sequential sections one by one
        for section_spec in sequential_group:
            await self._process_section(section_spec)
        
        # Check for knowledge gaps after writing all sections
        await self._check_for_gaps_and_pause()
    
    async def _check_for_gaps_and_pause(self) -> None:
        """
        Check for knowledge gaps in low-scoring sections.
        If gaps detected, pause for literature addition.
        """
        state = self.state_manager.state
        
        # Find low-scoring sections
        min_score_threshold = self.config.gap_detection_threshold
        low_scoring = []
        
        for section_id, section_state in state.sections.items():
            if 0 < section_state.current_score < min_score_threshold:
                low_scoring.append({
                    'section_id': section_id,
                    'score': section_state.current_score,
                    'content': section_state.content,
                    'quality_feedback': section_state.quality_feedback
                })
        
        if not low_scoring:
            self.log.info("no_gaps_detected", message="All sections above threshold")
            return
        
        self.log.warning("low_scoring_sections_detected", count=len(low_scoring))
        
        # Analyze gaps using gap_identifier agent
        gap_identifier = self._agents.get("gap_identifier")
        if not gap_identifier:
            self.log.error("gap_identifier_not_available")
            return
        
        all_missing_concepts = []
        
        for section_info in low_scoring:
            result = await gap_identifier.execute(
                action="analyze_section_gaps",
                section_id=section_info['section_id'],
                content=section_info['content'],
                score=section_info['score'],
                quality_feedback=section_info['quality_feedback']
            )
            
            if result.success and result.output:
                gap_data = result.output
                all_missing_concepts.extend(gap_data.get("missing_theories", []))
                all_missing_concepts.extend(gap_data.get("missing_methodologies", []))
                all_missing_concepts.extend(gap_data.get("missing_empirical_evidence", []))
                
                self.log.info(
                    "section_gaps_analyzed",
                    section=section_info['section_id'],
                    theories=len(gap_data.get("missing_theories", [])),
                    methodologies=len(gap_data.get("missing_methodologies", [])),
                    evidence=len(gap_data.get("missing_empirical_evidence", []))
                )
        
        if not all_missing_concepts:
            self.log.info("no_specific_gaps_identified")
            return
        
        # Generate WOS queries using literature_scout
        literature_scout = self._agents.get("literature_scout")
        if not literature_scout:
            self.log.error("literature_scout_not_available")
            return
        
        wos_result = await literature_scout.execute(
            action="generate_wos_query",
            missing_concepts=all_missing_concepts,
            context=state.title
        )
        
        if not wos_result.success or not wos_result.output:
            self.log.error("wos_query_generation_failed")
            return
        
        wos_queries = wos_result.output
        
        # Generate gap report
        report_path = self._generate_gap_report(low_scoring, all_missing_concepts, wos_queries)
        
        # Pause orchestrator
        state.orchestrator_state = OrchestratorState.PAUSED
        self.state_manager.save_state()
        
        self.log.warning("orchestrator_paused_for_literature_addition",
                        sections_affected=len(low_scoring),
                        gaps_total=len(all_missing_concepts))
        
        # Print instructions to console
        print("\n" + "="*70)
        print("   ⏸️  ORCHESTRATOR PAUSED - ACTION REQUIRED")
        print("="*70)
        print(f"\n🔍 Knowledge gaps detected in {len(low_scoring)} sections:")
        for s in low_scoring:
            print(f"   - {s['section_id'].upper()}: score {s['score']}/100")
        print(f"\n📚 Total missing concepts: {len(all_missing_concepts)}")
        print(f"\n📝 Gap report saved to: {report_path}")
        print("\n✅ NEXT STEPS:")
        print("   1. Review gap report for WOS search queries")
        print("   2. Execute searches in Web of Science")
        print("   3. Download results as .ris or .bib files")
        print("   4. Place files in: data/raw_literature/additional/")
        print("   5. Run ingestion: python scripts/ingest_additional_literature.py")
        print("   6. Resume generation: orchestrator.resume_after_literature_addition()")
        print("\n" + "="*70 + "\n")
    
    def _generate_gap_report(
        self,
        low_scoring: list[dict],
        missing_concepts: list[dict],
        wos_queries: dict
    ) -> Path:
        """
        Generate markdown report with gap analysis and WOS queries.
        
        Returns:
            Path to the generated report file
        """
        state = self.state_manager.state
        
        # Create reports directory
        reports_dir = Path("data/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Add timestamp to prevent overwriting previous reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"gap_report_{state.article_id}_{timestamp}.md"
        
        report_lines = [
            "# Knowledge Gap Analysis Report",
            f"\n**Article:** {state.title}",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Article ID:** {state.article_id}",
            "\n---\n",
            "## Summary",
            f"\n- **Low-scoring sections:** {len(low_scoring)}",
            f"- **Total gaps identified:** {len(missing_concepts)}",
            f"- **WOS queries generated:** {len(wos_queries.get('queries', []))}",
            "\n## Low-Scoring Sections\n"
        ]
        
        for section_info in low_scoring:
            report_lines.append(f"### {section_info['section_id'].upper()}")
            report_lines.append(f"**Score:** {section_info['score']}/100\n")
        
        report_lines.append("\n## Missing Concepts\n")
        
        for i, concept in enumerate(missing_concepts, 1):
            concept_name = (concept.get('theory_name') or 
                          concept.get('methodology_name') or 
                          concept.get('research_area', 'Unknown'))
            report_lines.append(f"### {i}. {concept_name}")
            report_lines.append(f"**Why needed:** {concept.get('why_needed', 'N/A')}")
            report_lines.append(f"**Search terms:** {', '.join(concept.get('search_terms', []))}")
            report_lines.append(f"**Expected impact:** {concept.get('expected_impact', 'N/A')}\n")
        
        report_lines.append("\n## Web of Science Queries\n")
        
        for i, query_info in enumerate(wos_queries.get('queries', []), 1):
            report_lines.append(f"### Query {i}")
            report_lines.append(f"```\n{query_info.get('query', 'N/A')}\n```")
            report_lines.append(f"**Purpose:** {query_info.get('purpose', 'N/A')}")
            report_lines.append(f"**Expected results:** {query_info.get('expected_results', 'N/A')}\n")
        
        strategy = wos_queries.get('search_strategy', {})
        if strategy:
            report_lines.append("\n## Search Strategy\n")
            report_lines.append(f"**Approach:** {strategy.get('approach', 'N/A')}")
            report_lines.append(f"**Rationale:** {strategy.get('rationale', 'N/A')}")
            report_lines.append(f"**Time span:** {strategy.get('time_span', 'N/A')}")
            report_lines.append(f"**Estimated results:** {strategy.get('estimated_total_results', 'N/A')}")
        
        report_lines.append("\n## Instructions\n")
        for instruction in wos_queries.get('instructions', []):
            report_lines.append(f"- {instruction}")
        
        # Write report
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')
        
        self.log.info("gap_report_generated", path=str(report_path))
        
        return report_path
    
    async def resume_after_literature_addition(self) -> None:
        """
        Resume article generation after new literature has been ingested.
        Regenerates low-scoring sections only.
        """
        state = self.state_manager.state
        
        if state.orchestrator_state != OrchestratorState.PAUSED:
            self.log.warning("resume_called_but_not_paused", state=state.orchestrator_state.value)
            return
        
        self.log.info("resuming_after_literature_addition")
        
        # Resume orchestrator
        state.orchestrator_state = OrchestratorState.RUNNING
        
        # Find sections that need regeneration
        min_score_threshold = self.config.gap_detection_threshold
        sections_to_regenerate = []
        
        for section_id, section_state in state.sections.items():
            if 0 < section_state.current_score < min_score_threshold:
                sections_to_regenerate.append(section_id)
        
        if not sections_to_regenerate:
            self.log.info("no_sections_to_regenerate")
            state.orchestrator_state = OrchestratorState.COMPLETED
            return
        
        self.log.info("regenerating_sections", count=len(sections_to_regenerate))
        
        # Regenerate each section
        for section_id in sections_to_regenerate:
            section_spec = self._sections_config.get_section_spec(section_id)
            if section_spec:
                self.log.info("regenerating_section", section=section_id)
                await self._process_section(section_spec)
        
        # Continue with remaining workflow
        await self._run_qa_phase()
        await self._run_finalization_phase()
        
        state.orchestrator_state = OrchestratorState.COMPLETED
        self.log.info("article_generation_completed_after_resume")
    
    async def _process_section(self, section_spec) -> None:
        """Process a single section through saturation loop."""
        state = self.state_manager.state
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
