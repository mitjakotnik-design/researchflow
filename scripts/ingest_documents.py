"""
Document ingestion script for scientific articles.

Reads Markdown files converted from PDFs and indexes them in ChromaDB.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import structlog

from rag import HybridSearch


logger = structlog.get_logger()


@dataclass
class DocumentChunk:
    """A chunk of a document for indexing."""
    
    id: str
    content: str
    source: str
    document_title: str
    section: str = ""
    page: int = 0
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentIngester:
    """
    Ingests Markdown documents into the vector database.
    
    Usage:
        ingester = DocumentIngester(
            documents_dir="C:/RaniaDR/Znanstvena podlaga/Članki"
        )
        await ingester.ingest_all()
    """
    
    def __init__(
        self,
        documents_dir: str,
        hybrid_search: Optional[HybridSearch] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        collection_name: str = "scoping_review_articles"
    ):
        self.documents_dir = Path(documents_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.collection_name = collection_name
        
        self.log = structlog.get_logger().bind(component="document_ingester")
        
        # Initialize or use provided search
        if hybrid_search:
            self._search = hybrid_search
        else:
            self._search = HybridSearch(
                collection_name=collection_name,
                persist_directory="data/chroma"
            )
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "chunks_created": 0,
            "errors": []
        }
    
    async def ingest_all(self, file_pattern: str = "*.md") -> dict:
        """
        Ingest all matching documents from the directory.
        
        Args:
            file_pattern: Glob pattern for files to process
        
        Returns:
            Statistics dict
        """
        self.log.info(
            "starting_ingestion",
            directory=str(self.documents_dir),
            pattern=file_pattern
        )
        
        # Initialize search
        self._search.initialize()
        
        # Find all matching files
        files = list(self.documents_dir.glob(file_pattern))
        self.log.info("files_found", count=len(files))
        
        all_chunks = []
        
        for file_path in files:
            try:
                chunks = await self._process_file(file_path)
                all_chunks.extend(chunks)
                self.stats["files_processed"] += 1
                
                self.log.debug(
                    "file_processed",
                    file=file_path.name,
                    chunks=len(chunks)
                )
                
            except Exception as e:
                self.stats["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                self.log.error(
                    "file_processing_error",
                    file=file_path.name,
                    error=str(e)
                )
        
        # Add all chunks to index
        if all_chunks:
            await self._add_to_index(all_chunks)
        
        self.stats["chunks_created"] = len(all_chunks)
        
        self.log.info(
            "ingestion_completed",
            files=self.stats["files_processed"],
            chunks=self.stats["chunks_created"],
            errors=len(self.stats["errors"])
        )
        
        return self.stats
    
    async def _process_file(self, file_path: Path) -> list[DocumentChunk]:
        """Process a single Markdown file into chunks."""
        
        # Read content
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        # Extract title (from filename or first heading)
        title = self._extract_title(file_path.stem, content)
        
        # Extract metadata
        metadata = self._extract_metadata(content, file_path)
        
        # Clean content
        content = self._clean_content(content)
        
        # Split into chunks
        chunks = self._chunk_content(
            content=content,
            source=file_path.name,
            title=title,
            metadata=metadata
        )
        
        return chunks
    
    def _extract_title(self, filename: str, content: str) -> str:
        """Extract document title."""
        
        # Try from content (first H1)
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Clean filename
        # Remove number prefix like "1. " or "10. "
        title = re.sub(r'^\d+\.\s*', '', filename)
        
        # Remove common suffixes
        title = re.sub(r'\s*-\s*\d{4}.*$', '', title)
        
        return title.strip()
    
    def _extract_metadata(self, content: str, file_path: Path) -> dict:
        """Extract metadata from content."""
        
        metadata = {
            "source_file": file_path.name,
            "file_size": file_path.stat().st_size,
        }
        
        # Extract year if present
        year_match = re.search(r'\b(19|20)\d{2}\b', file_path.name)
        if year_match:
            metadata["year"] = int(year_match.group(0))
        
        # Extract DOI if present
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', content)
        if doi_match:
            metadata["doi"] = doi_match.group(0)
        
        # Extract authors (from common patterns)
        author_patterns = [
            r'Authors?:\s*(.+?)(?:\n|$)',
            r'By:\s*(.+?)(?:\n|$)',
        ]
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["authors"] = match.group(1).strip()
                break
        
        return metadata
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        
        # Remove excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Remove markdown image links (keep alt text)
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', content)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Normalize spaces
        content = re.sub(r' +', ' ', content)
        
        return content.strip()
    
    def _chunk_content(
        self,
        content: str,
        source: str,
        title: str,
        metadata: dict
    ) -> list[DocumentChunk]:
        """Split content into overlapping chunks."""
        
        chunks = []
        
        # Split by sections first
        sections = self._split_by_sections(content)
        
        chunk_id = 0
        for section_name, section_content in sections:
            # Further split large sections
            section_chunks = self._split_text(
                section_content,
                self.chunk_size,
                self.chunk_overlap
            )
            
            for i, chunk_text in enumerate(section_chunks):
                chunk_id += 1
                
                chunks.append(DocumentChunk(
                    id=f"{source}_{chunk_id}",
                    content=chunk_text,
                    source=source,
                    document_title=title,
                    section=section_name,
                    page=i + 1,
                    metadata={
                        **metadata,
                        "chunk_index": chunk_id,
                        "section": section_name,
                    }
                ))
        
        return chunks
    
    def _split_by_sections(self, content: str) -> list[tuple[str, str]]:
        """Split content by markdown headings."""
        
        # Pattern for headings
        heading_pattern = r'^(#{1,3})\s+(.+)$'
        
        lines = content.split('\n')
        sections = []
        current_section = "preamble"
        current_content = []
        
        for line in lines:
            match = re.match(heading_pattern, line)
            if match:
                # Save previous section
                if current_content:
                    sections.append((
                        current_section,
                        '\n'.join(current_content).strip()
                    ))
                
                # Start new section
                current_section = match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_content:
            sections.append((
                current_section,
                '\n'.join(current_content).strip()
            ))
        
        return sections
    
    def _split_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> list[str]:
        """Split text into overlapping chunks."""
        
        if len(text) <= chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Find a good break point (sentence end)
            if end < len(text):
                # Look for sentence end
                for sep in ['. ', '.\n', '! ', '? ', '\n\n']:
                    break_idx = text.rfind(sep, start, end)
                    if break_idx > start + chunk_size // 2:
                        end = break_idx + len(sep)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
            # Avoid infinite loop
            if start >= len(text) - overlap:
                break
        
        return chunks
    
    async def _add_to_index(self, chunks: list[DocumentChunk]) -> None:
        """Add chunks to the vector index."""
        
        # Convert to format expected by HybridSearch
        documents = [
            {
                "id": chunk.id,
                "content": chunk.content,
                "source": chunk.source,
                "document_title": chunk.document_title,
                "section": chunk.section,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]
        
        # Add in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            await self._search.add_documents(batch, batch_size=batch_size)
            
            self.log.debug(
                "batch_indexed",
                start=i,
                count=len(batch)
            )


async def ingest_articles(
    articles_dir: str = "C:/RaniaDR/Znanstvena podlaga/Članki",
    collection_name: str = "scoping_review_articles"
) -> dict:
    """
    Convenience function to ingest all articles.
    
    Usage:
        stats = await ingest_articles()
        print(f"Processed {stats['files_processed']} files")
    """
    ingester = DocumentIngester(
        documents_dir=articles_dir,
        collection_name=collection_name
    )
    
    return await ingester.ingest_all()


def run_ingestion():
    """Run ingestion from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector DB")
    parser.add_argument(
        "--dir",
        default="C:/RaniaDR/Znanstvena podlaga/Članki",
        help="Directory with Markdown files"
    )
    parser.add_argument(
        "--collection",
        default="scoping_review_articles",
        help="ChromaDB collection name"
    )
    
    args = parser.parse_args()
    
    # Run async
    stats = asyncio.run(ingest_articles(args.dir, args.collection))
    
    print(f"\n=== Ingestion Complete ===")
    print(f"Files processed: {stats['files_processed']}")
    print(f"Chunks created: {stats['chunks_created']}")
    print(f"Errors: {len(stats['errors'])}")
    
    if stats['errors']:
        print("\nErrors:")
        for err in stats['errors']:
            print(f"  - {err['file']}: {err['error']}")


if __name__ == "__main__":
    run_ingestion()
