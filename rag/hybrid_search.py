"""Hybrid search combining dense and sparse retrieval."""

import hashlib
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import structlog


logger = structlog.get_logger()


@dataclass
class SearchResult:
    """Single search result."""
    
    id: str
    content: str
    score: float
    
    # Metadata
    source: str = ""
    document_title: str = ""
    section: str = ""
    page: int = 0
    
    # Search type that found it
    search_type: str = "hybrid"  # dense, sparse, or hybrid
    
    # Additional metadata
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "score": self.score,
            "source": self.source,
            "document_title": self.document_title,
            "section": self.section,
            "page": self.page,
            "search_type": self.search_type,
        }


class HybridSearch:
    """Hybrid search combining ChromaDB (dense) and BM25 (sparse)."""
    
    def __init__(
        self,
        collection_name: str = "scoping_review",
        persist_directory: str = "data/chroma",
        embedding_model: str = "models/embedding-001",
        bm25_k1: float = 1.5,
        bm25_b: float = 0.75,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5,
        cache_size: int = 100  # LRU cache size for queries
    ):
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.embedding_model = embedding_model
        
        # BM25 parameters
        self.bm25_k1 = bm25_k1
        self.bm25_b = bm25_b
        
        # Fusion weights
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        
        self.log = structlog.get_logger().bind(component="hybrid_search")
        
        # Initialize components
        self._chroma_client = None
        self._collection = None
        self._bm25_index = None
        self._documents: list[dict] = []
        
        self._initialized = False
        
        # Query cache
        self._cache_size = cache_size
        self._query_cache: dict[str, list] = {}  # hash -> results
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _get_cache_key(self, query: str, top_k: int, filters: dict = None) -> str:
        """Generate a cache key for a query."""
        key_parts = f"{query}|{top_k}|{str(filters)}"
        return hashlib.md5(key_parts.encode()).hexdigest()
    
    def get_cache_stats(self) -> dict:
        """Return cache statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._query_cache)
        }
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._query_cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.log.info("query_cache_cleared")
    
    def initialize(self) -> None:
        """Initialize search components."""
        if self._initialized:
            return
        
        self._setup_chroma()
        self._setup_bm25()
        self._initialized = True
        
        self.log.info(
            "hybrid_search_initialized",
            collection=self.collection_name,
            doc_count=len(self._documents)
        )
    
    def _setup_chroma(self) -> None:
        """Set up ChromaDB."""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("chromadb not installed. Run: pip install chromadb")
        
        # Create persist directory
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize client
        self._chroma_client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self._collection = self._chroma_client.get_collection(
                name=self.collection_name
            )
            self.log.info(
                "chroma_collection_loaded",
                name=self.collection_name,
                count=self._collection.count()
            )
        except Exception:
            # Create embedding function
            embedding_function = self._create_embedding_function()
            
            self._collection = self._chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            self.log.info("chroma_collection_created", name=self.collection_name)
    
    def _create_embedding_function(self):
        """Create embedding function for ChromaDB."""
        try:
            import google.generativeai as genai
            from chromadb import Documents, EmbeddingFunction, Embeddings
        except ImportError:
            raise ImportError(
                "Required packages not installed. Run: "
                "pip install google-generativeai chromadb"
            )
        
        use_vertex_ai = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if use_vertex_ai:
            # Use Vertex AI embeddings with Application Default Credentials
            import vertexai
            from vertexai.language_models import TextEmbeddingModel
            
            project = os.getenv("GCP_PROJECT")
            location = os.getenv("GCP_LOCATION", "us-central1")
            if not project:
                raise ValueError("GCP_PROJECT not set for Vertex AI")
            
            vertexai.init(project=project, location=location)
            embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@003")
            
            class VertexEmbeddingFunction(EmbeddingFunction):
                def __init__(self, model):
                    self.model = model
                
                def __call__(self, input: Documents) -> Embeddings:
                    embeddings = []
                    for text in input:
                        result = self.model.get_embeddings([text])
                        embeddings.append(result[0].values)
                    return embeddings
            
            return VertexEmbeddingFunction(embedding_model)
        
        elif api_key:
            # Use Google AI Studio embeddings
            genai.configure(api_key=api_key)
            
            class GeminiEmbeddingFunction(EmbeddingFunction):
                def __init__(self, model: str):
                    self.model = model
                
                def __call__(self, input: Documents) -> Embeddings:
                    embeddings = []
                    for text in input:
                        result = genai.embed_content(
                            model=self.model,
                            content=text,
                            task_type="retrieval_document"
                        )
                        embeddings.append(result["embedding"])
                    return embeddings
            
            return GeminiEmbeddingFunction(self.embedding_model)
        
        else:
            raise ValueError("No Google credentials: set GOOGLE_API_KEY or USE_VERTEX_AI=true")
    
    def _setup_bm25(self) -> None:
        """Set up BM25 index."""
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            raise ImportError("rank-bm25 not installed. Run: pip install rank-bm25")
        
        # Load documents from ChromaDB for BM25 indexing
        if self._collection and self._collection.count() > 0:
            all_docs = self._collection.get(include=["documents", "metadatas"])
            
            self._documents = [
                {
                    "id": all_docs["ids"][i],
                    "content": all_docs["documents"][i],
                    "metadata": all_docs["metadatas"][i] if all_docs["metadatas"] else {}
                }
                for i in range(len(all_docs["ids"]))
            ]
            
            # Tokenize for BM25
            tokenized = [self._tokenize(doc["content"]) for doc in self._documents]
            self._bm25_index = BM25Okapi(tokenized, k1=self.bm25_k1, b=self.bm25_b)
            
            self.log.info("bm25_index_built", doc_count=len(self._documents))
        else:
            self._bm25_index = None
            self.log.info("bm25_index_empty")
    
    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization for BM25."""
        import re
        # Lowercase and split on non-alphanumeric
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens
    
    async def add_documents(
        self,
        documents: list[dict],
        batch_size: int = 100
    ) -> int:
        """Add documents to the search index."""
        if not self._initialized:
            self.initialize()
        
        added = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            ids = [doc.get("id", f"doc_{i+j}") for j, doc in enumerate(batch)]
            contents = [doc["content"] for doc in batch]
            metadatas = [doc.get("metadata", {}) for doc in batch]
            
            # Add to ChromaDB
            self._collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            
            added += len(batch)
            self.log.debug("documents_added", batch_size=len(batch), total=added)
        
        # Rebuild BM25 index
        self._setup_bm25()
        
        return added
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict] = None,
        dense_only: bool = False,
        sparse_only: bool = False,
        use_cache: bool = True
    ) -> list[SearchResult]:
        """Perform hybrid search with optional caching."""
        if not self._initialized:
            self.initialize()
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(query, top_k, filters)
            if cache_key in self._query_cache:
                self._cache_hits += 1
                self.log.debug("cache_hit", query_length=len(query))
                return self._query_cache[cache_key]
            self._cache_misses += 1
        
        results = []
        
        # Dense search (ChromaDB)
        if not sparse_only:
            dense_results = await self._dense_search(query, top_k * 2, filters)
            results.extend(dense_results)
        
        # Sparse search (BM25)
        if not dense_only and self._bm25_index:
            sparse_results = await self._sparse_search(query, top_k * 2)
            results.extend(sparse_results)
        
        # Reciprocal rank fusion
        if not dense_only and not sparse_only:
            results = self._reciprocal_rank_fusion(results, top_k)
        else:
            # Just take top_k
            results = sorted(results, key=lambda x: x.score, reverse=True)[:top_k]
        
        # Store in cache (with LRU eviction)
        if use_cache:
            if len(self._query_cache) >= self._cache_size:
                # Remove oldest entry (simple FIFO, not true LRU)
                oldest_key = next(iter(self._query_cache))
                del self._query_cache[oldest_key]
            self._query_cache[cache_key] = results
        
        self.log.debug(
            "search_completed",
            query_length=len(query),
            results_count=len(results),
            cache_stats=self.get_cache_stats()
        )
        
        return results
    
    async def _dense_search(
        self,
        query: str,
        n_results: int,
        filters: Optional[dict] = None
    ) -> list[SearchResult]:
        """Perform dense vector search."""
        where_filter = None
        if filters:
            where_filter = filters
        
        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                # Convert distance to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                score = 1 / (1 + distance)  # Convert distance to similarity
                
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                
                search_results.append(SearchResult(
                    id=doc_id,
                    content=results["documents"][0][i],
                    score=score,
                    source=metadata.get("source", ""),
                    document_title=metadata.get("title", ""),
                    section=metadata.get("section", ""),
                    page=metadata.get("page", 0),
                    search_type="dense",
                    metadata=metadata
                ))
        
        return search_results
    
    async def _sparse_search(
        self,
        query: str,
        n_results: int
    ) -> list[SearchResult]:
        """Perform sparse BM25 search."""
        if not self._bm25_index or not self._documents:
            return []
        
        tokenized_query = self._tokenize(query)
        scores = self._bm25_index.get_scores(tokenized_query)
        
        # Get top indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:n_results]
        
        search_results = []
        
        for idx in top_indices:
            if scores[idx] > 0:
                doc = self._documents[idx]
                metadata = doc.get("metadata", {})
                
                search_results.append(SearchResult(
                    id=doc["id"],
                    content=doc["content"],
                    score=scores[idx],
                    source=metadata.get("source", ""),
                    document_title=metadata.get("title", ""),
                    section=metadata.get("section", ""),
                    page=metadata.get("page", 0),
                    search_type="sparse",
                    metadata=metadata
                ))
        
        return search_results
    
    def _reciprocal_rank_fusion(
        self,
        results: list[SearchResult],
        top_k: int,
        k: int = 60  # RRF constant
    ) -> list[SearchResult]:
        """Combine results using Reciprocal Rank Fusion."""
        # Group by ID
        doc_scores: dict[str, dict] = {}
        
        for result in results:
            if result.id not in doc_scores:
                doc_scores[result.id] = {
                    "result": result,
                    "dense_rank": None,
                    "sparse_rank": None
                }
            
            # Assign rank based on search type
            if result.search_type == "dense":
                doc_scores[result.id]["dense_rank"] = result.score
            else:
                doc_scores[result.id]["sparse_rank"] = result.score
        
        # Calculate RRF scores
        for doc_id, data in doc_scores.items():
            rrf_score = 0
            
            if data["dense_rank"] is not None:
                # Higher score = better, so use score directly
                rrf_score += self.dense_weight * data["dense_rank"]
            
            if data["sparse_rank"] is not None:
                # Normalize BM25 scores
                rrf_score += self.sparse_weight * (data["sparse_rank"] / 100)
            
            data["result"].score = rrf_score
            data["result"].search_type = "hybrid"
        
        # Sort by RRF score
        fused_results = sorted(
            [d["result"] for d in doc_scores.values()],
            key=lambda x: x.score,
            reverse=True
        )[:top_k]
        
        return fused_results
    
    def get_stats(self) -> dict:
        """Get search index statistics."""
        return {
            "collection_name": self.collection_name,
            "document_count": self._collection.count() if self._collection else 0,
            "bm25_indexed": self._bm25_index is not None,
            "dense_weight": self.dense_weight,
            "sparse_weight": self.sparse_weight,
        }
