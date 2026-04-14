"""Reranker module using Cohere API."""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import structlog

from .hybrid_search import SearchResult


logger = structlog.get_logger()


class Reranker(ABC):
    """Abstract base class for rerankers."""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Rerank search results."""
        pass


class CohereReranker(Reranker):
    """Reranker using Cohere Rerank API."""
    
    def __init__(
        self,
        model: str = "rerank-english-v3.0",
        api_key: Optional[str] = None
    ):
        self.model = model
        self.log = structlog.get_logger().bind(component="cohere_reranker")
        
        try:
            import cohere
        except ImportError:
            raise ImportError("cohere not installed. Run: pip install cohere")
        
        api_key = api_key or os.getenv("COHERE_API_KEY")
        
        if not api_key:
            raise ValueError("COHERE_API_KEY not set")
        
        self.client = cohere.AsyncClient(api_key)
        self.log.info("cohere_reranker_initialized", model=model)
    
    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Rerank results using Cohere."""
        if not results:
            return []
        
        # Prepare documents for reranking
        documents = [r.content for r in results]
        
        try:
            response = await self.client.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_n=min(top_k, len(results)),
                return_documents=False
            )
            
            # Reorder results based on reranking
            reranked = []
            for result in response.results:
                original = results[result.index]
                # Update score with rerank relevance score
                original.score = result.relevance_score
                original.metadata["rerank_score"] = result.relevance_score
                original.metadata["original_index"] = result.index
                reranked.append(original)
            
            self.log.debug(
                "rerank_completed",
                input_count=len(results),
                output_count=len(reranked)
            )
            
            return reranked
            
        except Exception as e:
            self.log.error("rerank_failed", error=str(e))
            # Fall back to original order
            return results[:top_k]


class NoOpReranker(Reranker):
    """No-op reranker that returns results unchanged."""
    
    async def rerank(
        self,
        query: str,
        results: list[SearchResult],
        top_k: int = 10
    ) -> list[SearchResult]:
        """Return top_k results without reranking."""
        return results[:top_k]


@dataclass
class RerankConfig:
    """Configuration for reranking."""
    
    enabled: bool = True
    model: str = "rerank-english-v3.0"
    min_results_to_rerank: int = 5
    
    def create_reranker(self) -> Reranker:
        """Create appropriate reranker based on config."""
        if not self.enabled:
            return NoOpReranker()
        
        try:
            return CohereReranker(model=self.model)
        except (ImportError, ValueError) as e:
            logger.warning(
                "cohere_unavailable_falling_back",
                error=str(e)
            )
            return NoOpReranker()
