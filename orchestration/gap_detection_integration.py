"""
Integration Script - Add Gap Detection to Workflow

Adds gap detection checkpoint after writing phase to pause for literature addition
when sections score below threshold.
"""

# Add this method to MetaOrchestrator class:

async def _check_for_gaps_and_pause(self) -> bool:
    """
    Check if any sections have low scores and pause for literature addition.
    
    Returns:
        bool: True if workflow was paused, False if continuing
    """
    from orchestration.gap_detection_workflow import (
        GapDetectionWorkflow,
        GapDetectionResult
    )
    
    # Initialize gap detection workflow
    gap_workflow = GapDetectionWorkflow(
        state_manager=self.state_manager,
        gap_identifier_agent=self._agents.get("gap_identifier"),
        literature_scout_agent=self._agents.get("literature_scout"),
        rag_system=self._hybrid_search,
        min_score_threshold=50  # Sections below 50 trigger gap detection
    )
    
    # Detect gaps
    result = await gap_workflow.detect_gaps_in_sections(
        sections=self.state_manager.state.sections
    )
    
    # If gaps found, pause
    if result.awaiting_literature:
        report_file = gap_workflow.pause_for_literature(result)
        
        # Save state
        self.state_manager.state.orchestrator_state = OrchestratorState.PAUSED
        self.state_manager.save_state()
        
        self.log.warning(
            "workflow_paused_for_literature",
            gaps=len(result.gaps),
            sections=result.low_scoring_sections,
            report=report_file
        )
        
        return True
    
    return False


# Add to meta_orchestrator.py _run_writing_phase method, after all sections complete:

# After writing phase completes, check for gaps
paused = await self._check_for_gaps_and_pause()

if paused:
    self.log.info("workflow_paused_awaiting_literature")
    return self.state_manager.state  # Return early


# Add resume capability:

async def resume_after_literature_addition(self, sections_to_regenerate: list[str]):
    """
    Resume workflow after additional literature has been ingested.
    
    Args:
        sections_to_regenerate: List of section IDs to regenerate
    """
    
    self.log.info(
        "resuming_workflow_after_literature",
        sections=sections_to_regenerate
    )
    
    # Reload ChromaDB to get new literature
    if self._hybrid_search:
        self._hybrid_search.initialize()
        new_stats = self._hybrid_search.get_stats()
        self.log.info("chromadb_reloaded", docs=new_stats.get('document_count', 0))
    
    # Regenerate low-scoring sections
    for section_id in sections_to_regenerate:
        self.log.info("regenerating_section", section=section_id)
        
        # Get section spec
        section_spec = self._sections_config.sections.get(section_id)
        if not section_spec:
            continue
        
        # Reset section state
        section_state = self.state_manager.state.sections[section_id]
        section_state.current_iteration = 0
        section_state.current_score = 0
        section_state.content = ""
        
        # Re-run saturation loop
        from .saturation_loop import SaturationLoop
        
        saturation_loop = SaturationLoop(
            config=self.config.saturation_config,
            section_spec=section_spec,
            agents=self._agents,
            quality_gates=self.config.quality_gates
        )
        
        result = await saturation_loop.run(section_state)
        
        # Update state
        section_state.status = SectionStatus.APPROVED if result.success else SectionStatus.REVISION_NEEDED
        section_state.content = result.final_content
        section_state.current_score = result.final_score
        
        self.log.info(
            "section_regenerated",
            section=section_id,
            old_score="N/A",
            new_score=result.final_score
        )
    
    # Continue with remaining workflow phases
    self.state_manager.state.orchestrator_state = OrchestratorState.RUNNING
    
    await self._run_qa_phase()
    await self._run_finalization_phase()
    
    self.state_manager.state.current_phase = ArticlePhase.COMPLETED
    self.state_manager.state.orchestrator_state = OrchestratorState.COMPLETED
    
    return self.state_manager.state
