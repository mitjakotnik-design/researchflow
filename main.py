"""
Scoping Review Multi-Agent System

Main entry point for running the article generation pipeline.
"""

import asyncio
import os
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


def setup_environment(require_llm_keys: bool = True):
    """Load environment variables and validate configuration."""
    load_dotenv()
    
    if require_llm_keys:
        # Check for either GOOGLE_API_KEY or Vertex AI credentials
        google_api_key = os.getenv("GOOGLE_API_KEY")
        use_vertex_ai = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
        gcp_project = os.getenv("GCP_PROJECT")
        
        if not google_api_key and not use_vertex_ai:
            logger.error("missing_google_credentials")
            print("Error: No Google credentials configured.")
            print("Either set GOOGLE_API_KEY or USE_VERTEX_AI=true with GCP_PROJECT")
            sys.exit(1)
        
        if use_vertex_ai and not gcp_project:
            logger.error("missing_gcp_project")
            print("Error: USE_VERTEX_AI=true but GCP_PROJECT not set")
            sys.exit(1)
        
        auth_mode = "vertex_ai" if use_vertex_ai else "api_key"
        logger.info("google_auth_configured", mode=auth_mode)
    
    logger.info("environment_configured", llm_keys_required=require_llm_keys)


def create_agents():
    """Create and return all agents."""
    from agents import (
        # Research cluster
        ResearcherAgent,
        LiteratureScoutAgent,
        DataExtractorAgent,
        MetaAnalystAgent,
        GapIdentifierAgent,
        # Writing cluster
        WriterAgent,
        SynthesizerAgent,
        AcademicEditorAgent,
        TerminologyGuardianAgent,
        CitationManagerAgent,
        VisualizerAgent,
        # Quality cluster
        MultiEvaluatorAgent,
        FactCheckerAgent,
        ConsistencyCheckerAgent,
        BiasAuditorAgent,
        CriticAgent,
        MethodologyValidatorAgent,
    )
    
    agents = [
        # Research cluster
        ResearcherAgent(),
        LiteratureScoutAgent(),
        DataExtractorAgent(),
        MetaAnalystAgent(),
        GapIdentifierAgent(),
        # Writing cluster
        WriterAgent(),
        SynthesizerAgent(),
        AcademicEditorAgent(),
        TerminologyGuardianAgent(),
        CitationManagerAgent(),
        VisualizerAgent(),
        # Quality cluster
        MultiEvaluatorAgent(),
        FactCheckerAgent(),
        ConsistencyCheckerAgent(),
        BiasAuditorAgent(),
        CriticAgent(),
        MethodologyValidatorAgent(),
    ]
    
    logger.info("agents_created", count=len(agents))
    return agents


def create_orchestrator():
    """Create and configure the meta-orchestrator."""
    from config import (
        StateManager,
        ModelsConfig,
        QualityThresholds,
        QualityGates,
        SaturationConfig,
    )
    from orchestration import MetaOrchestrator, OrchestratorConfig
    
    # Initialize state manager
    state_manager = StateManager(data_dir="data")
    
    # Initialize models config
    models_config = ModelsConfig()
    
    # Create orchestrator config
    orch_config = OrchestratorConfig(
        saturation_config=SaturationConfig(
            target_score=85,
            minimum_acceptable=75,
            max_iterations=5
        ),
        quality_thresholds=QualityThresholds(),
        quality_gates=QualityGates(),
        verbose=os.getenv("VERBOSE", "false").lower() == "true"
    )
    
    # Create orchestrator
    orchestrator = MetaOrchestrator(
        config=orch_config,
        state_manager=state_manager,
        models_config=models_config
    )
    
    # Register agents
    agents = create_agents()
    orchestrator.register_agents(agents)
    
    logger.info("orchestrator_created")
    return orchestrator


def setup_rag(orchestrator):
    """Set up RAG system if documents are available."""
    from rag import HybridSearch, CohereReranker, RerankConfig
    
    data_dir = Path("data")
    chroma_dir = data_dir / "chroma"
    
    try:
        # Initialize hybrid search
        hybrid_search = HybridSearch(
            collection_name="scoping_review",
            persist_directory=str(chroma_dir)
        )
        hybrid_search.initialize()
        
        # Initialize reranker if Cohere available
        reranker = None
        if os.getenv("COHERE_API_KEY"):
            try:
                reranker = CohereReranker()
                logger.info("reranker_enabled", provider="cohere")
            except Exception as e:
                logger.warning("reranker_unavailable", error=str(e))
        
        # Configure orchestrator with RAG
        orchestrator.setup_rag(hybrid_search, reranker)
        
        logger.info(
            "rag_configured",
            documents=hybrid_search.get_stats().get("document_count", 0)
        )
        
    except Exception as e:
        logger.warning("rag_setup_failed", error=str(e))
        print(f"Warning: RAG system not available: {e}")
        print("The system will run without literature retrieval.")


async def run_article_generation(title: str, target_journal: str = ""):
    """Run the complete article generation workflow."""
    
    logger.info("starting_article_generation", title=title)
    print(f"\n{'='*60}")
    print(f"Scoping Review Article Generation")
    print(f"{'='*60}")
    print(f"Title: {title}")
    if target_journal:
        print(f"Target Journal: {target_journal}")
    print(f"{'='*60}\n")
    
    # Create orchestrator
    orchestrator = create_orchestrator()
    
    # Setup RAG
    setup_rag(orchestrator)
    
    # Initialize article
    article_state = await orchestrator.initialize_article(
        title=title,
        target_journal=target_journal
    )
    
    print(f"Article ID: {article_state.article_id}")
    print(f"Sections: {list(article_state.sections.keys())}")
    print("\nStarting generation...\n")
    
    try:
        # Run the workflow
        final_state = await orchestrator.run()
        
        # Print results
        print(f"\n{'='*60}")
        print("Generation Complete!")
        print(f"{'='*60}")
        
        progress = final_state.get_overall_progress()
        print(f"Phase: {progress['phase']}")
        print(f"Sections Approved: {progress['sections_approved']}")
        print(f"Progress: {progress['progress_pct']:.1f}%")
        
        # Print section scores
        print("\nSection Scores:")
        for section_id, section_state in final_state.sections.items():
            status = "✓" if section_state.status.value == "approved" else "○"
            print(f"  {status} {section_id}: {section_state.current_score}/100")
        
        # Export for review
        export_path = Path("output") / f"{article_state.article_id}_review.md"
        export_path.parent.mkdir(exist_ok=True)
        orchestrator.state_manager.export_for_review(str(export_path))
        print(f"\nExported review to: {export_path}")
        
        return final_state
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Saving state...")
        orchestrator.pause()
        orchestrator.state_manager.create_checkpoint("interrupted")
        print("State saved. You can resume later.")
        return None
        
    except Exception as e:
        logger.error("generation_failed", error=str(e))
        print(f"\nError during generation: {e}")
        
        # Try to save state
        try:
            orchestrator.state_manager.create_checkpoint("error")
            print("Error checkpoint saved.")
        except:
            pass
        
        raise


async def ingest_documents(documents_dir: str, collection_name: str = "scoping_review_articles"):
    """Ingest documents into the RAG system using enhanced ingester."""
    from scripts.ingest_documents import DocumentIngester
    
    logger.info("starting_document_ingestion", directory=documents_dir)
    print(f"Ingesting documents from: {documents_dir}")
    print(f"Collection: {collection_name}")
    
    docs_path = Path(documents_dir)
    if not docs_path.exists():
        print(f"Error: Directory not found: {documents_dir}")
        return
    
    # Count files
    md_files = list(docs_path.glob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    
    if not md_files:
        print("No markdown files found.")
        print("Did you convert PDFs to Markdown first?")
        print("Run: python -m markitdown <file.pdf> -o <file.md>")
        return
    
    # Use enhanced ingester
    ingester = DocumentIngester(
        documents_dir=str(docs_path),
        chunk_size=1000,
        chunk_overlap=200,
        collection_name=collection_name
    )
    
    stats = await ingester.ingest_all(file_pattern="*.md")
    
    print(f"\n{'='*50}")
    print("Ingestion Complete!")
    print(f"{'='*50}")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    
    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for err in stats['errors'][:5]:
            print(f"  - {err['file']}: {err['error']}")


# Default paths
DEFAULT_ARTICLES_DIR = r"C:\RaniaDR\Znanstvena podlaga\Članki"


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scoping Review Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an article
  python main.py generate --title "AI in Healthcare: A Scoping Review"
  
  # Ingest documents (with default path)
  python main.py ingest
  
  # Ingest from custom directory
  python main.py ingest --documents "./literature"
  
  # Generate with target journal
  python main.py generate --title "Review Title" --journal "Nature Reviews"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate an article")
    gen_parser.add_argument("--title", required=True, help="Article title")
    gen_parser.add_argument("--journal", default="", help="Target journal")
    gen_parser.add_argument("--use-v2", action="store_true", help="Use v2 enhanced agents")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument(
        "--documents", 
        default=DEFAULT_ARTICLES_DIR,
        help=f"Documents directory (default: {DEFAULT_ARTICLES_DIR})"
    )
    ingest_parser.add_argument(
        "--collection",
        default="scoping_review_articles",
        help="ChromaDB collection name"
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_environment()
    
    if args.command == "generate":
        asyncio.run(run_article_generation(
            title=args.title,
            target_journal=args.journal
        ))
    
    elif args.command == "ingest":
        asyncio.run(ingest_documents(
            documents_dir=args.documents,
            collection_name=args.collection
        ))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
