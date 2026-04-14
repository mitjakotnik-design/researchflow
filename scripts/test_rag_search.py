"""Test RAG search functionality."""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


async def test_rag_search():
    """Test RAG search against the vectorized documents."""
    import vertexai
    from rag.hybrid_search import HybridSearch
    
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    
    print("Initializing Vertex AI...")
    vertexai.init(project=project, location=location)
    
    print("\n" + "=" * 60)
    print("RAG SEARCH TEST")
    print("=" * 60 + "\n")
    
    # Initialize search
    print("Loading ChromaDB collection...")
    search = HybridSearch(
        collection_name="scoping_review_articles",
        persist_directory="data/chroma",
        embedding_model="textembedding-gecko@003"
    )
    search.initialize()
    
    # Get collection stats
    collection = search._collection
    doc_count = collection.count() if collection else 0
    print(f"Documents in collection: {doc_count}")
    
    # Test queries
    test_queries = [
        "artificial intelligence in healthcare",
        "machine learning diagnosis",
        "medical imaging deep learning",
    ]
    
    print("\nTesting search queries:")
    print("-" * 40)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            results = await search.search(query, top_k=3)
            print(f"  Found {len(results)} results")
            
            if results:
                # Show first result preview
                first = results[0]
                content = first.content[:150] if hasattr(first, 'content') else str(first)[:150]
                score = first.score if hasattr(first, 'score') else "N/A"
                source = first.source if hasattr(first, 'source') else "unknown"
                print(f"  Top result (score={score:.3f}):")
                print(f"    Source: {source}")
                print(f"    Preview: {content}...")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("RAG TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rag_search())
