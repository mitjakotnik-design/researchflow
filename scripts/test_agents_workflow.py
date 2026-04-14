"""Comprehensive agent and workflow tests."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


async def test_v1_agents():
    """Test v1 agents individually."""
    import vertexai
    from agents.agent_factory import AgentFactory
    from config import ModelsConfig, StateManager, QualityThresholds
    from agents.base_agent import AgentContext
    from rag.hybrid_search import HybridSearch
    
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    
    print("Initializing Vertex AI...")
    vertexai.init(project=project, location=location)
    
    print("\n" + "=" * 60)
    print("V1 AGENTS TEST")
    print("=" * 60 + "\n")
    
    # Create context
    state_manager = StateManager()
    
    # Initialize article state - THIS IS REQUIRED
    state_manager.create_new_article(
        article_id="test_article",
        title="Artificial Intelligence in Medical Diagnosis: A Scoping Review",
        target_journal="Journal of Medical AI",
        language="en"
    )
    
    models_config = ModelsConfig()
    quality_thresholds = QualityThresholds()
    
    # Initialize RAG
    print("Loading RAG...")
    rag = HybridSearch(
        collection_name="scoping_review_articles",
        persist_directory="data/chroma",
        embedding_model="textembedding-gecko@003"
    )
    rag.initialize()
    
    # Create RAG query function with correct signature
    async def rag_query(query: str, top_k: int = 5, filters: dict = None) -> list[dict]:
        results = await rag.search(query, top_k=top_k, filters=filters)
        return [r.to_dict() for r in results]
    
    context = AgentContext(
        state_manager=state_manager,
        models_config=models_config,
        quality_thresholds=quality_thresholds,
        rag_query=rag_query,
        verbose=True
    )
    
    # Test agents
    factory = AgentFactory()
    
    # Define test cases per agent with correct parameters
    test_cases = {
        "researcher": {
            "action": "research",
            "kwargs": {
                "section": "introduction",
                "research_questions": ["artificial intelligence medical diagnosis"],
                "depth": "normal"
            }
        },
        "writer": {
            "action": "write_section",
            "kwargs": {
                "section_id": "introduction",
                "section_name": "Introduction",
                "min_words": 100,
                "max_words": 300,
                "guidelines": "Provide background on AI in healthcare.",
                "avoid": "Do not use jargon.",
                "research_context": "AI is transforming healthcare through improved diagnosis accuracy."
            }
        },
        "multi_evaluator": {
            "action": "evaluate",
            "kwargs": {
                "content": "Artificial intelligence (AI) is revolutionizing healthcare by enabling more accurate and faster diagnosis. Machine learning algorithms can analyze medical images with high precision.",
                "section": "introduction",
                "iteration": 1
            }
        }
    }

    results = {}
    
    for agent_name, test_config in test_cases.items():
        print(f"\nTesting {agent_name}...")
        print("-" * 40)
        
        try:
            agent = factory.create_v1(agent_name)
            
            # Initialize agent with context
            agent.initialize(context)
            
            # Execute test
            result = await agent.execute(
                action=test_config["action"],
                **test_config["kwargs"]
            )
            
            results[agent_name] = {
                "status": "OK" if result.success else "FAILED",
                "confidence": result.confidence,
                "tokens": result.tokens_input + result.tokens_output,
                "duration_ms": result.duration_ms,
                "output_preview": str(result.output)[:200] if result.output else None,
                "error": result.error
            }
            
            if result.success:
                print(f"  ✓ OK (confidence={result.confidence:.2f}, {result.duration_ms}ms)")
                if result.output:
                    print(f"    Output: {str(result.output)[:100]}...")
            else:
                print(f"  ✗ FAILED: {result.error}")
                
        except Exception as e:
            results[agent_name] = {
                "status": "ERROR",
                "error": str(e)
            }
            import traceback
            print(f"  ✗ ERROR: {e}")
            traceback.print_exc()
    
    return results


async def test_workflow_pipeline():
    """Test a complete scoping review workflow."""
    import vertexai
    from agents.agent_factory import AgentFactory
    from config import ModelsConfig, StateManager, QualityThresholds
    from agents.base_agent import AgentContext
    from rag.hybrid_search import HybridSearch
    
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    
    print("\n" + "=" * 60)
    print("WORKFLOW PIPELINE TEST")
    print("=" * 60 + "\n")
    
    vertexai.init(project=project, location=location)
    
    # Initialize components
    state_manager = StateManager()
    
    # Initialize article state - THIS IS REQUIRED
    state_manager.create_new_article(
        article_id="workflow_test_article",
        title="Artificial Intelligence in Medical Diagnosis: A Scoping Review",
        target_journal="Journal of Medical AI",
        language="en"
    )
    
    models_config = ModelsConfig()
    quality_thresholds = QualityThresholds()
    
    # Initialize RAG
    rag = HybridSearch(
        collection_name="scoping_review_articles",
        persist_directory="data/chroma",
        embedding_model="textembedding-gecko@003"
    )
    rag.initialize()
    
    async def rag_query(query: str, top_k: int = 5, filters: dict = None) -> list[dict]:
        results = await rag.search(query, top_k=top_k, filters=filters)
        return [r.to_dict() for r in results]
    
    context = AgentContext(
        state_manager=state_manager,
        models_config=models_config,
        quality_thresholds=quality_thresholds,
        rag_query=rag_query,
        current_section="introduction",
        current_iteration=1,
        verbose=True
    )
    
    factory = AgentFactory()
    
    # Workflow: Research → Write → Evaluate
    workflow_results = []
    
    # Step 1: Research
    print("Step 1: Research Phase")
    print("-" * 40)
    try:
        researcher = factory.create_v1("researcher")
        researcher.initialize(context)
        
        research_result = await researcher.execute(
            action="research",
            section="introduction",
            research_questions=["artificial intelligence diagnostic imaging healthcare"],
            depth="normal"
        )
        workflow_results.append({
            "step": "research",
            "status": "OK" if research_result.success else "FAILED",
            "output": research_result.output
        })
        print(f"  Research: {'✓' if research_result.success else '✗'}")
    except Exception as e:
        workflow_results.append({"step": "research", "status": "ERROR", "error": str(e)})
        print(f"  Research: ERROR - {e}")
    
    # Step 2: Write
    print("\nStep 2: Writing Phase")
    print("-" * 40)
    try:
        writer = factory.create_v1("writer")
        writer.initialize(context)
        
        # Use research output as context
        research_context = ""
        if workflow_results and workflow_results[-1].get("output"):
            research_output = workflow_results[-1]["output"]
            if isinstance(research_output, dict):
                research_context = str(research_output.get("synthesis", ""))[:2000]
            else:
                research_context = str(research_output)[:2000]
        
        write_result = await writer.execute(
            action="write_section",
            section_id="introduction",
            section_name="Introduction",
            min_words=150,
            max_words=400,
            guidelines="Provide background on AI in healthcare diagnosis.",
            avoid="Avoid jargon and speculation.",
            research_context=research_context or "AI improves diagnostic accuracy in healthcare."
        )
        workflow_results.append({
            "step": "write",
            "status": "OK" if write_result.success else "FAILED",
            "output": write_result.output
        })
        print(f"  Writing: {'✓' if write_result.success else '✗'}")
        if write_result.output:
            print(f"    Preview: {str(write_result.output)[:150]}...")
    except Exception as e:
        workflow_results.append({"step": "write", "status": "ERROR", "error": str(e)})
        print(f"  Writing: ERROR - {e}")
    
    # Step 3: Evaluate
    print("\nStep 3: Evaluation Phase")
    print("-" * 40)
    try:
        evaluator = factory.create_v1("multi_evaluator")
        evaluator.initialize(context)
        
        written_text = ""
        if len(workflow_results) > 1 and workflow_results[-1].get("output"):
            written_text = str(workflow_results[-1]["output"])[:3000]
        
        eval_result = await evaluator.execute(
            action="evaluate",
            content=written_text or "Sample introduction text about AI in healthcare for evaluation.",
            section="introduction",
            iteration=1
        )
        workflow_results.append({
            "step": "evaluate",
            "status": "OK" if eval_result.success else "FAILED",
            "output": eval_result.output
        })
        print(f"  Evaluation: {'✓' if eval_result.success else '✗'}")
        if eval_result.quality_score is not None:
            print(f"    Quality Score: {eval_result.quality_score}")
    except Exception as e:
        workflow_results.append({"step": "evaluate", "status": "ERROR", "error": str(e)})
        print(f"  Evaluation: ERROR - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("WORKFLOW SUMMARY")
    print("=" * 60)
    
    for result in workflow_results:
        status_icon = "✓" if result["status"] == "OK" else "✗"
        print(f"{status_icon} {result['step'].upper()}: {result['status']}")
    
    return workflow_results


async def main():
    """Run all tests."""
    print("=" * 60)
    print("SCOPING REVIEW AGENTS - COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test v1 agents
    agent_results = await test_v1_agents()
    
    # Test workflow
    workflow_results = await test_workflow_pipeline()
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    agent_ok = sum(1 for r in agent_results.values() if r.get("status") == "OK")
    workflow_ok = sum(1 for r in workflow_results if r.get("status") == "OK")
    
    print(f"\nAgents tested: {len(agent_results)}, Successful: {agent_ok}")
    print(f"Workflow steps: {len(workflow_results)}, Successful: {workflow_ok}")
    
    # List issues
    issues = []
    for name, result in agent_results.items():
        if result.get("status") != "OK":
            issues.append(f"Agent {name}: {result.get('error', 'Unknown error')}")
    
    for result in workflow_results:
        if result.get("status") != "OK":
            issues.append(f"Workflow {result['step']}: {result.get('error', 'Unknown error')}")
    
    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✓ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
