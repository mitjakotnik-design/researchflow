#!/usr/bin/env python3
"""Check ChromaDB status."""
import os
os.chdir('c:/RaniaDR/scoping-review-agents')

from rag import HybridSearch

hs = HybridSearch(collection_name='scoping_review_articles', persist_directory='data/chroma')
hs.initialize()
stats = hs.get_stats()

print('ChromaDB Statistics:')
print(f"  Collection: {stats.get('collection_name', 'unknown')}")
print(f"  Documents: {stats.get('document_count', 0)}")
print(f"  Chunks: {stats.get('chunk_count', 0)}")

# Test a query
results = hs.search("AI implementation in HR psychosocial risks", k=3)
print(f"\nTest query returned {len(results)} results")
if results:
    for i, r in enumerate(results[:3]):
        print(f"  {i+1}. Score: {r.score:.3f} - {r.metadata.get('source', 'unknown')[:50]}...")
