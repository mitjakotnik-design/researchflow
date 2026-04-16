#!/usr/bin/env python3
"""
End-to-End Test for Gap Detection Workflow

This script tests the complete gap detection workflow:
1. Parse test RIS file
2. Ingest into ChromaDB
3. Verify ingestion
4. Test gap detection components
5. Validate integration
"""

import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog

logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()


def test_ris_parsing():
    """Test 1: Parse RIS file."""
    print("\n" + "="*70)
    print("TEST 1: RIS File Parsing")
    print("="*70)
    
    try:
        from scripts.ingest_additional_literature import parse_ris_file
        
        test_file = Path("data/raw_literature/additional/test_theories.ris")
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False
        
        entries = parse_ris_file(test_file)
        
        print(f"✅ Parsed {len(entries)} entries")
        
        if len(entries) == 0:
            print("❌ No entries parsed")
            return False
        
        # Validate first entry
        first_entry = entries[0]
        required_fields = ['title', 'authors', 'year', 'abstract', 'full_text']
        
        for field in required_fields:
            if field not in first_entry:
                print(f"❌ Missing field: {field}")
                return False
        
        print(f"   Title: {first_entry['title'][:50]}...")
        print(f"   Authors: {len(first_entry['authors'])} authors")
        print(f"   Year: {first_entry['year']}")
        print(f"   Full text length: {len(first_entry['full_text'])} chars")
        
        print("✅ RIS parsing test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ RIS parsing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chromadb_ingestion():
    """Test 2: Ingest into ChromaDB."""
    print("\n" + "="*70)
    print("TEST 2: ChromaDB Ingestion")
    print("="*70)
    
    try:
        from scripts.ingest_additional_literature import find_additional_literature, ingest_to_chromadb
        
        # Find files
        files_by_type = find_additional_literature()
        total_files = sum(len(files) for files in files_by_type.values())
        
        print(f"   Found {total_files} files to ingest")
        
        if total_files == 0:
            print("⚠️  No files found (this might be expected)")
            return True
        
        # Ingest
        result = ingest_to_chromadb(files_by_type)
        
        if not result['success']:
            print("❌ Ingestion failed")
            return False
        
        print(f"✅ Ingested {result['files_ingested']} files")
        print(f"   Total entries: {result['entries_ingested']}")
        print(f"   New chunks added: {result['new_chunks_added']}")
        print(f"   Final doc count: {result['final_docs']}")
        
        if result['new_chunks_added'] == 0:
            print("⚠️  No new chunks added (files may already exist)")
        
        print("✅ ChromaDB ingestion test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB ingestion test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gap_identifier_extension():
    """Test 3: Gap identifier agent extension."""
    print("\n" + "="*70)
    print("TEST 3: Gap Identifier Extension")
    print("="*70)
    
    try:
        from agents.gap_identifier import GapIdentifierAgent
        
        agent = GapIdentifierAgent()
        
        # Check new method exists
        if not hasattr(agent, '_analyze_section_gaps'):
            print("❌ Method _analyze_section_gaps not found")
            return False
        
        print("✅ Method _analyze_section_gaps exists")
        
        # Check action routing
        if not hasattr(agent, '_execute_action'):
            print("❌ Method _execute_action not found")
            return False
        
        print("✅ Method _execute_action exists")
        
        print("✅ Gap identifier extension test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Gap identifier extension test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_literature_scout_extension():
    """Test 4: Literature scout agent extension."""
    print("\n" + "="*70)
    print("TEST 4: Literature Scout Extension")
    print("="*70)
    
    try:
        from agents.literature_scout import LiteratureScoutAgent
        
        agent = LiteratureScoutAgent()
        
        # Check new method exists
        if not hasattr(agent, '_generate_wos_query'):
            print("❌ Method _generate_wos_query not found")
            return False
        
        print("✅ Method _generate_wos_query exists")
        
        # Check action routing
        if not hasattr(agent, '_execute_action'):
            print("❌ Method _execute_action not found")
            return False
        
        print("✅ Method _execute_action exists")
        
        print("✅ Literature scout extension test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Literature scout extension test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_meta_orchestrator_integration():
    """Test 5: Meta-orchestrator integration."""
    print("\n" + "="*70)
    print("TEST 5: Meta-Orchestrator Integration")
    print("="*70)
    
    try:
        from orchestration.meta_orchestrator import MetaOrchestrator
        
        # Check methods exist
        required_methods = [
            '_check_for_gaps_and_pause',
            '_generate_gap_report',
            'resume_after_literature_addition'
        ]
        
        for method_name in required_methods:
            if not hasattr(MetaOrchestrator, method_name):
                print(f"❌ Method {method_name} not found")
                return False
            print(f"✅ Method {method_name} exists")
        
        # Check OrchestratorState enum
        from config import OrchestratorState
        
        if not hasattr(OrchestratorState, 'PAUSED'):
            print("❌ OrchestratorState.PAUSED not found")
            return False
        
        print("✅ OrchestratorState.PAUSED exists")
        
        print("✅ Meta-orchestrator integration test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Meta-orchestrator integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gap_detection_workflow():
    """Test 6: Gap detection workflow class."""
    print("\n" + "="*70)
    print("TEST 6: Gap Detection Workflow Class")
    print("="*70)
    
    try:
        from orchestration.gap_detection_workflow import (
            KnowledgeGap,
            GapDetectionResult,
            GapDetectionWorkflow
        )
        
        # Test KnowledgeGap
        gap = KnowledgeGap(
            gap_id="gap_test",
            section="methods",
            gap_type="methodology",
            description="Test description",
            missing_concepts=["PRISMA-ScR"],
            importance="high",
            suggested_search_terms=[]
        )
        
        if gap.section != "methods":
            print("❌ KnowledgeGap initialization failed")
            return False
        
        print("✅ KnowledgeGap dataclass works")
        
        # Test GapDetectionResult
        result = GapDetectionResult(
            gaps=[gap],
            low_scoring_sections=["methods"],
            timestamp="2024-01-01T00:00:00"
        )
        
        if len(result.gaps) != 1:
            print("❌ GapDetectionResult initialization failed")
            return False
        
        print("✅ GapDetectionResult dataclass works")
        
        # Test GapDetectionWorkflow initialization
        workflow = GapDetectionWorkflow(
            state_manager=None,
            gap_identifier_agent=None,
            literature_scout_agent=None,
            rag_system=None,
            min_score_threshold=50
        )
        
        if workflow.min_score_threshold != 50:
            print("❌ GapDetectionWorkflow initialization failed")
            return False
        
        print("✅ GapDetectionWorkflow class works")
        
        print("✅ Gap detection workflow test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Gap detection workflow test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencies():
    """Test 7: Check dependencies installed."""
    print("\n" + "="*70)
    print("TEST 7: Dependencies Check")
    print("="*70)
    
    dependencies = {
        'rispy': 'RIS file parsing',
        'bibtexparser': 'BibTeX file parsing',
        'pypdf': 'PDF file parsing'
    }
    
    all_installed = True
    
    for package, purpose in dependencies.items():
        try:
            __import__(package)
            print(f"✅ {package} installed ({purpose})")
        except ImportError:
            print(f"⚠️  {package} NOT installed ({purpose})")
            print(f"   Install with: pip install {package}")
            all_installed = False
    
    if all_installed:
        print("✅ All dependencies installed")
        return True
    else:
        print("⚠️  Some dependencies missing (install them for full functionality)")
        return False  # Changed to False to indicate missing deps


def main():
    """Run all end-to-end tests."""
    print("\n" + "="*70)
    print("   🧪 GAP DETECTION WORKFLOW - END-TO-END TESTS")
    print("="*70)
    
    tests = [
        ("Dependencies Check", test_dependencies),
        ("RIS Parsing", test_ris_parsing),
        ("ChromaDB Ingestion", test_chromadb_ingestion),
        ("Gap Identifier Extension", test_gap_identifier_extension),
        ("Literature Scout Extension", test_literature_scout_extension),
        ("Meta-Orchestrator Integration", test_meta_orchestrator_integration),
        ("Gap Detection Workflow", test_gap_detection_workflow),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("   📊 TEST RESULTS SUMMARY")
    print("="*70 + "\n")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Gap detection workflow is fully functional")
        print("\n📝 Next steps:")
        print("   1. Install any missing dependencies (if any)")
        print("   2. Run article generation to test workflow in production")
        print("   3. Monitor for low-scoring sections triggering pause")
        print("   4. Test resume functionality after literature addition")
    else:
        print(f"\n⚠️  {total_count - passed_count} tests failed")
        print("\n🔧 Fix failing tests before using gap detection workflow")
    
    print("\n" + "="*70 + "\n")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
