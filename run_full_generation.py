#!/usr/bin/env python3
"""
ResearchFlow Article Generation - Full Pipeline Execution

This script runs the complete scoping review article generation using:
- Existing vectorized ChromaDB (5977 chunks)
- 17 specialized agents across 3 clusters
- PRISMA-ScR compliant methodology
- Quality gates and iterative refinement

Topic: "Psychosocial Risks and Organizational Culture Implications 
        of AI Implementation Through HR Functions"
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Change to project directory
os.chdir('c:/RaniaDR/scoping-review-agents')
sys.path.insert(0, 'c:/RaniaDR/scoping-review-agents')

from dotenv import load_dotenv
load_dotenv()

import structlog
import logging
logging.basicConfig(level=logging.INFO)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


# Article Configuration
ARTICLE_CONFIG = {
    "title": "From Technostress to Organizational Resilience: A Scoping Review of Psychosocial Risks and Organizational Culture Implications of AI Implementation Through HR Functions",
    "target_journal": "Journal of Occupational Health Psychology",
    "target_word_count": 8000,
    "language": "en",
    "research_question": """
    This scoping review addresses three interconnected research questions:
    
    RQ1: What psychosocial risks have been identified in the literature regarding 
         AI implementation through HR functions, and how are these risks conceptualized?
    
    RQ2: How does AI implementation via HR functions influence organizational culture, 
         and what cultural factors facilitate or hinder successful AI adoption?
    
    RQ3: What strategies, interventions, or frameworks have been proposed or evaluated 
         to mitigate psychosocial risks while fostering positive organizational culture 
         change during HR-mediated AI implementation?
    """,
    "pcc_framework": {
        "population": "Employees and organizations implementing AI through HR functions",
        "concept": "Psychosocial risks, organizational culture, AI/ML technologies in HR",
        "context": "Contemporary workplaces (2015-2026), primarily Western and Asian contexts"
    }
}


async def run_generation():
    """Run the complete article generation."""
    
    print("\n" + "="*70)
    print("   RESEARCHFLOW SCOPING REVIEW ARTICLE GENERATION")
    print("="*70)
    print(f"\nTitle: {ARTICLE_CONFIG['title'][:70]}...")
    print(f"Target: {ARTICLE_CONFIG['target_journal']}")
    print(f"Words: {ARTICLE_CONFIG['target_word_count']}")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    # Import after setting up path
    from config import StateManager, ModelsConfig, QualityThresholds, QualityGates, SaturationConfig
    from orchestration import MetaOrchestrator, OrchestratorConfig, ExecutionMode
    from rag import HybridSearch
    
    # =========================================================================
    # PHASE 1: Initialize Components
    # =========================================================================
    print("\n[PHASE 1] Initializing Components...")
    
    # State Manager
    state_manager = StateManager(data_dir="data")
    
    # Models Config
    models_config = ModelsConfig()
    
    # Orchestrator Config with quality settings + PARALLEL MODE
    orch_config = OrchestratorConfig(
        mode=ExecutionMode.PARALLEL,  # Enable parallel section writing
        saturation_config=SaturationConfig(
            target_score=85,
            minimum_acceptable=75,
            max_iterations=5
        ),
        quality_thresholds=QualityThresholds(),
        quality_gates=QualityGates(),
        verbose=True
    )
    
    # Create orchestrator
    orchestrator = MetaOrchestrator(
        config=orch_config,
        state_manager=state_manager,
        models_config=models_config
    )
    
    print("  [OK] State Manager initialized")
    print("  [OK] Models Config loaded")
    print("  [OK] Orchestrator created")
    
    # =========================================================================
    # PHASE 2: Setup RAG System
    # =========================================================================
    print("\n[PHASE 2] Setting up RAG System...")
    
    hybrid_search = HybridSearch(
        collection_name='scoping_review_articles',
        persist_directory='data/chroma'
    )
    hybrid_search.initialize()
    
    stats = hybrid_search.get_stats()
    print(f"  [OK] ChromaDB loaded: {stats.get('document_count', 0)} chunks")
    
    # Setup RAG in orchestrator
    orchestrator.setup_rag(hybrid_search, reranker=None)
    print("  [OK] RAG system configured")
    
    # =========================================================================
    # PHASE 3: Register Agents
    # =========================================================================
    print("\n[PHASE 3] Registering Agents...")
    
    from agents import (
        # Research cluster
        ResearcherAgent, LiteratureScoutAgent, DataExtractorAgent,
        MetaAnalystAgent, GapIdentifierAgent,
        # Writing cluster
        WriterAgent, SynthesizerAgent, AcademicEditorAgent,
        TerminologyGuardianAgent, CitationManagerAgent, VisualizerAgent,
        # Quality cluster
        MultiEvaluatorAgent, FactCheckerAgent, ConsistencyCheckerAgent,
        BiasAuditorAgent, CriticAgent, MethodologyValidatorAgent,
    )
    
    agents = [
        # Research Cluster (5 agents)
        ResearcherAgent(),
        LiteratureScoutAgent(),
        DataExtractorAgent(),
        MetaAnalystAgent(),
        GapIdentifierAgent(),
        # Writing Cluster (6 agents)
        WriterAgent(),
        SynthesizerAgent(),
        AcademicEditorAgent(),
        TerminologyGuardianAgent(),
        CitationManagerAgent(),
        VisualizerAgent(),
        # Quality Cluster (6 agents)
        MultiEvaluatorAgent(),
        FactCheckerAgent(),
        ConsistencyCheckerAgent(),
        BiasAuditorAgent(),
        CriticAgent(),
        MethodologyValidatorAgent(),
    ]
    
    orchestrator.register_agents(agents)
    print(f"  [OK] Registered {len(agents)} agents")
    print("    - Research Cluster: 5 agents")
    print("    - Writing Cluster: 6 agents")
    print("    - Quality Cluster: 6 agents")
    
    # =========================================================================
    # PHASE 4: Initialize Article
    # =========================================================================
    print("\n[PHASE 4] Initializing Article...")
    
    article_state = await orchestrator.initialize_article(
        title=ARTICLE_CONFIG['title'],
        target_journal=ARTICLE_CONFIG['target_journal']
    )
    
    print(f"  [OK] Article ID: {article_state.article_id}")
    print(f"  [OK] Sections: {list(article_state.sections.keys())}")
    
    # =========================================================================
    # PHASE 5: Run Generation
    # =========================================================================
    print("\n[PHASE 5] Running Article Generation...")
    print("-"*70)
    
    start_time = time.time()
    
    try:
        # Run the main workflow
        final_state = await orchestrator.run()
        
        elapsed = time.time() - start_time
        
        # =====================================================================
        # RESULTS
        # =====================================================================
        print("\n" + "="*70)
        print("   GENERATION COMPLETE")
        print("="*70)
        
        progress = final_state.get_overall_progress()
        print(f"\nPhase: {progress['phase']}")
        print(f"Sections Approved: {progress['sections_approved']}/{len(final_state.sections)}")
        print(f"Progress: {progress['progress_pct']:.1f}%")
        print(f"Time: {elapsed/60:.1f} minutes")
        
        # Section details
        print("\n" + "-"*40)
        print("Section Results:")
        print("-"*40)
        
        total_words = 0
        total_citations = 0
        
        for section_id, section_state in final_state.sections.items():
            status_icon = "[OK]" if section_state.status.value == "approved" else "[ ]" 
            score = section_state.current_score
            words = section_state.word_count
            cites = section_state.citations_count
            iters = section_state.current_iteration
            
            total_words += words
            total_citations += cites
            
            print(f"  {status_icon} {section_id:15} | Score: {score:3}/100 | Words: {words:5} | Cites: {cites:3} | Iters: {iters}")
        
        print("-"*40)
        print(f"  TOTAL              | Words: {total_words:5} | Cites: {total_citations:3}")
        
        # Export
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        export_path = output_dir / f"{article_state.article_id}_final.md"
        state_manager.export_for_review(str(export_path))
        print(f"\n[OK] Exported to: {export_path}")
        
        # Save statistics
        stats_path = output_dir / f"{article_state.article_id}_stats.json"
        import json
        with open(stats_path, 'w') as f:
            json.dump({
                "title": ARTICLE_CONFIG['title'],
                "completed_at": datetime.now().isoformat(),
                "elapsed_minutes": elapsed / 60,
                "total_words": total_words,
                "total_citations": total_citations,
                "sections": {
                    sid: {
                        "status": s.status.value,
                        "score": s.current_score,
                        "words": s.word_count,
                        "citations": s.citations_count,
                        "iterations": s.current_iteration
                    }
                    for sid, s in final_state.sections.items()
                },
                "progress": progress
            }, f, indent=2)
        print(f"[OK] Stats saved to: {stats_path}")
        
        return final_state
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user. Saving checkpoint...")
        orchestrator.pause()
        state_manager.create_checkpoint("interrupted")
        print("Checkpoint saved. Run again to resume.")
        return None
        
    except Exception as e:
        logger.exception("generation_failed")
        print(f"\n✗ Error: {e}")
        
        try:
            state_manager.create_checkpoint("error")
            print("Error checkpoint saved.")
        except:
            pass
        
        raise


if __name__ == "__main__":
    print("\n" + "="*70)
    print("   ResearchFlow: AI-Powered Scoping Review Generation")
    print("   Version 2.1.0 - April 2026")
    print("="*70)
    
    # Run
    asyncio.run(run_generation())
