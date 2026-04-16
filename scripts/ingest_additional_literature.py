#!/usr/bin/env python3
"""
Ingest Additional Literature - Hot Reload ChromaDB

Handles ingestion of additional literature files (.ris, .bib, .pdf) 
that were added to fill knowledge gaps.

Uses proper parsers for structured literature formats:
- RIS files: rispy library
- BibTeX files: bibtexparser library
- PDF files: pypdf library
"""

import asyncio
import sys
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rag import HybridSearch
import structlog

# Import parsers
try:
    import rispy
except ImportError:
    rispy = None
    
try:
    import bibtexparser
except ImportError:
    bibtexparser = None
    
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger()


def generate_unique_doc_id(file_stem: str, entry_index: int, title: str) -> str:
    """
    Generate unique document ID with hash to prevent collisions.
    
    Args:
        file_stem: Base filename without extension
        entry_index: Index of entry in file
        title: Document title for hash generation
        
    Returns:
        Unique document ID
    """
    # Create hash from title to ensure uniqueness even if same file ingested twice
    title_hash = hashlib.md5(title.encode('utf-8', errors='ignore')).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"{file_stem}_{timestamp}_{title_hash}_entry_{entry_index}"


def chunk_text_generator(text: str, chunk_size: int = 2000, overlap: int = 200):
    """
    Generate text chunks with overlap for better context preservation.
    Memory-efficient generator pattern for large documents.
    
    Args:
        text: Full text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Yields:
        Text chunks
    """
    if len(text) <= chunk_size:
        yield text
        return
    
    start = 0
    while start < len(text):
        end = start + chunk_size
        yield text[start:end]
        start += (chunk_size - overlap)


def parse_ris_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse RIS file and extract structured metadata."""
    if not rispy:
        logger.error("rispy_not_installed", file=file_path.name)
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            entries = rispy.load(f)
        
        parsed_entries = []
        for entry in entries:
            # Extract key fields
            parsed = {
                'title': entry.get('title', entry.get('primary_title', '')),
                'authors': entry.get('authors', []),
                'year': entry.get('year', ''),
                'abstract': entry.get('abstract', ''),
                'journal': entry.get('journal_name', entry.get('secondary_title', '')),
                'doi': entry.get('doi', ''),
                'keywords': entry.get('keywords', []),
                'type': entry.get('type_of_reference', 'JOUR'),
                'raw_entry': entry
            }
            
            # Create full text representation
            full_text_parts = []
            if parsed['title']:
                full_text_parts.append(f"Title: {parsed['title']}")
            if parsed['authors']:
                authors_str = ', '.join(parsed['authors'])
                full_text_parts.append(f"Authors: {authors_str}")
            if parsed['year']:
                full_text_parts.append(f"Year: {parsed['year']}")
            if parsed['abstract']:
                full_text_parts.append(f"Abstract: {parsed['abstract']}")
            if parsed['keywords']:
                keywords_str = ', '.join(parsed['keywords'])
                full_text_parts.append(f"Keywords: {keywords_str}")
            
            parsed['full_text'] = '\n\n'.join(full_text_parts)
            parsed_entries.append(parsed)
        
        logger.info("ris_parsed", file=file_path.name, entries=len(parsed_entries))
        return parsed_entries
    
    except ImportError as e:
        logger.error("rispy_import_failed", file=file_path.name, error=str(e))
        return []
    except (ValueError, KeyError) as e:
        logger.error("ris_file_corrupt", file=file_path.name, error=str(e), 
                    hint="File may be malformed or not a valid RIS format")
        return []
    except UnicodeDecodeError as e:
        logger.error("ris_encoding_error", file=file_path.name, error=str(e),
                    hint="Try saving file with UTF-8 encoding")
        return []
    except IOError as e:
        logger.error("ris_file_read_failed", file=file_path.name, error=str(e))
        return []
    except Exception as e:
        logger.error("ris_parse_unexpected_error", file=file_path.name, error=str(e))
        return []


def parse_bibtex_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse BibTeX file and extract structured metadata."""
    if not bibtexparser:
        logger.error("bibtexparser_not_installed", file=file_path.name)
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            bib_database = bibtexparser.load(f)
        
        parsed_entries = []
        for entry in bib_database.entries:
            # Extract key fields
            parsed = {
                'title': entry.get('title', ''),
                'authors': entry.get('author', '').split(' and ') if entry.get('author') else [],
                'year': entry.get('year', ''),
                'abstract': entry.get('abstract', ''),
                'journal': entry.get('journal', ''),
                'doi': entry.get('doi', ''),
                'keywords': entry.get('keywords', '').split(', ') if entry.get('keywords') else [],
                'type': entry.get('ENTRYTYPE', 'article'),
                'raw_entry': entry
            }
            
            # Create full text representation
            full_text_parts = []
            if parsed['title']:
                full_text_parts.append(f"Title: {parsed['title']}")
            if parsed['authors']:
                authors_str = ', '.join(parsed['authors'])
                full_text_parts.append(f"Authors: {authors_str}")
            if parsed['year']:
                full_text_parts.append(f"Year: {parsed['year']}")
            if parsed['abstract']:
                full_text_parts.append(f"Abstract: {parsed['abstract']}")
            if parsed['keywords']:
                keywords_str = ', '.join(parsed['keywords'])
                full_text_parts.append(f"Keywords: {keywords_str}")
            
            parsed['full_text'] = '\n\n'.join(full_text_parts)
            parsed_entries.append(parsed)
        
        logger.info("bibtex_parsed", file=file_path.name, entries=len(parsed_entries))
        return parsed_entries
    
    except ImportError as e:
        logger.error("bibtexparser_import_failed", file=file_path.name, error=str(e))
        return []
    except (ValueError, KeyError) as e:
        logger.error("bibtex_file_corrupt", file=file_path.name, error=str(e),
                    hint="File may be malformed or not valid BibTeX format")
        return []
    except UnicodeDecodeError as e:
        logger.error("bibtex_encoding_error", file=file_path.name, error=str(e),
                    hint="Try saving file with UTF-8 encoding")
        return []
    except IOError as e:
        logger.error("bibtex_file_read_failed", file=file_path.name, error=str(e))
        return []
    except Exception as e:
        logger.error("bibtex_parse_unexpected_error", file=file_path.name, error=str(e))
        return []


def parse_pdf_file(file_path: Path) -> List[Dict[str, Any]]:
    """Parse PDF file and extract text."""
    if not PdfReader:
        logger.error("pypdf_not_installed", file=file_path.name)
        return []
    
    try:
        reader = PdfReader(file_path)
        
        # Extract text from all pages
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())
        
        full_text = '\n\n'.join(text_parts)
        
        # Extract metadata if available
        metadata = reader.metadata if reader.metadata else {}
        
        parsed = {
            'title': metadata.get('/Title', file_path.stem),
            'authors': [metadata.get('/Author', '')] if metadata.get('/Author') else [],
            'year': '',
            'abstract': '',
            'journal': '',
            'doi': '',
            'keywords': [],
            'type': 'pdf',
            'full_text': full_text,
            'raw_entry': metadata
        }
        
        logger.info("pdf_parsed", file=file_path.name, pages=len(reader.pages))
        return [parsed]
    
    except ImportError as e:
        logger.error("pypdf_import_failed", file=file_path.name, error=str(e))
        return []
    except (ValueError, KeyError) as e:
        logger.error("pdf_file_corrupt", file=file_path.name, error=str(e),
                    hint="PDF may be encrypted, corrupted, or not a valid PDF")
        return []
    except IOError as e:
        logger.error("pdf_file_read_failed", file=file_path.name, error=str(e))
        return []
    except Exception as e:
        logger.error("pdf_parse_unexpected_error", file=file_path.name, error=str(e))
        return []


def find_additional_literature(base_dir: Path = Path("data/raw_literature/additional")) -> dict:
    """Find all new literature files."""
    
    if not base_dir.exists():
        base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("created_additional_literature_dir", path=str(base_dir))
        return {}
    
    files_by_type = {
        "ris": list(base_dir.glob("*.ris")),
        "bib": list(base_dir.glob("*.bib")),
        "pdf": list(base_dir.glob("*.pdf")),
        "txt": list(base_dir.glob("*.txt")),
        "docx": list(base_dir.glob("*.docx"))
    }
    
    total = sum(len(files) for files in files_by_type.values())
    
    logger.info(
        "literature_files_found",
        total=total,
        ris=len(files_by_type["ris"]),
        bib=len(files_by_type["bib"]),
        pdf=len(files_by_type["pdf"])
    )
    
    return files_by_type


def ingest_to_chromadb(files_by_type: dict) -> dict:
    """Ingest files into ChromaDB using proper parsers."""
    
    # Initialize ChromaDB
    hybrid_search = HybridSearch(
        collection_name='scoping_review_articles',
        persist_directory='data/chroma'
    )
    hybrid_search.initialize()
    
    # Get initial stats
    initial_stats = hybrid_search.get_stats()
    initial_count = initial_stats.get('document_count', 0)
    
    logger.info("chromadb_initialized", initial_docs=initial_count)
    
    # Process each file type with proper parsers
    ingested = []
    
    # Process RIS files
    for file_path in files_by_type.get("ris", []):
        entries = parse_ris_file(file_path)
        for i, entry in enumerate(entries):
            try:
                # Generate unique ID with hash to prevent collisions
                doc_id = generate_unique_doc_id(file_path.stem, i, entry['title'])
                
                # Use full_text as main document content
                document_text = entry['full_text']
                
                if len(document_text) < 50:
                    logger.warning("empty_entry", file=file_path.name, entry=i)
                    continue
                
                # Use generator for memory-efficient chunking
                chunks = list(chunk_text_generator(document_text, chunk_size=2000, overlap=200))
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                    
                    hybrid_search._collection.add(
                        documents=[chunk],
                        metadatas=[{
                            "source": file_path.name,
                            "title": entry['title'],
                            "authors": ', '.join(entry['authors'][:3]),  # First 3 authors
                            "year": str(entry['year']),
                            "journal": entry['journal'],
                            "doi": entry['doi'],
                            "file_type": "ris",
                            "additional_literature": True,
                            "chunk_id": chunk_idx,
                            "total_chunks": len(chunks)
                        }],
                        ids=[chunk_id]
                    )
                
                ingested.append({
                    "file": file_path.name,
                    "entry": i,
                    "chunks": len(chunks),
                    "title": entry['title'][:50]
                })
                
                logger.info("ris_entry_ingested", 
                           file=file_path.name, 
                           entry=i,
                           title=entry['title'][:50],
                           chunks=len(chunks))
                
            except Exception as e:
                logger.error("ris_entry_failed", file=file_path.name, entry=i, error=str(e))
    
    # Process BibTeX files
    for file_path in files_by_type.get("bib", []):
        entries = parse_bibtex_file(file_path)
        for i, entry in enumerate(entries):
            try:
                # Generate unique ID with hash
                doc_id = generate_unique_doc_id(file_path.stem, i, entry['title'])
                
                document_text = entry['full_text']
                
                if len(document_text) < 50:
                    logger.warning("empty_entry", file=file_path.name, entry=i)
                    continue
                
                # Use generator for memory-efficient chunking
                chunks = list(chunk_text_generator(document_text, chunk_size=2000, overlap=200))
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                    
                    hybrid_search._collection.add(
                        documents=[chunk],
                        metadatas=[{
                            "source": file_path.name,
                            "title": entry['title'],
                            "authors": ', '.join(entry['authors'][:3]),
                            "year": str(entry['year']),
                            "journal": entry['journal'],
                            "doi": entry['doi'],
                            "file_type": "bibtex",
                            "additional_literature": True,
                            "chunk_id": chunk_idx,
                            "total_chunks": len(chunks)
                        }],
                        ids=[chunk_id]
                    )
                
                ingested.append({
                    "file": file_path.name,
                    "entry": i,
                    "chunks": len(chunks),
                    "title": entry['title'][:50]
                })
                
                logger.info("bibtex_entry_ingested", 
                           file=file_path.name, 
                           entry=i,
                           title=entry['title'][:50],
                           chunks=len(chunks))
                
            except Exception as e:
                logger.error("bibtex_entry_failed", file=file_path.name, entry=i, error=str(e))
    
    # Process PDF files
    for file_path in files_by_type.get("pdf", []):
        entries = parse_pdf_file(file_path)
        for i, entry in enumerate(entries):
            try:
                # Generate unique ID with hash (use filename as title for PDFs without metadata)
                doc_id = generate_unique_doc_id(file_path.stem, i, entry['title'])
                
                document_text = entry['full_text']
                
                if len(document_text) < 100:
                    logger.warning("empty_pdf", file=file_path.name)
                    continue
                
                # Use generator for memory-efficient chunking (PDFs typically large)
                chunks = list(chunk_text_generator(document_text, chunk_size=2000, overlap=200))
                
                for chunk_idx, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{chunk_idx}"
                    
                    hybrid_search._collection.add(
                        documents=[chunk],
                        metadatas=[{
                            "source": file_path.name,
                            "title": entry['title'],
                            "authors": ', '.join(entry['authors']) if entry['authors'] else '',
                            "file_type": "pdf",
                            "additional_literature": True,
                            "chunk_id": chunk_idx,
                            "total_chunks": len(chunks)
                        }],
                        ids=[chunk_id]
                    )
                
                ingested.append({
                    "file": file_path.name,
                    "chunks": len(chunks),
                    "title": entry['title'][:50]
                })
                
                logger.info("pdf_ingested", 
                           file=file_path.name, 
                           chunks=len(chunks))
                
            except Exception as e:
                logger.error("pdf_failed", file=file_path.name, error=str(e))
    
    # Rebuild BM25 index
    logger.info("rebuilding_bm25_index")
    hybrid_search._setup_bm25()
    
    # Get final stats
    final_stats = hybrid_search.get_stats()
    final_count = final_stats.get('document_count', 0)
    
    result = {
        "success": True,
        "files_ingested": len(set(item['file'] for item in ingested)),
        "entries_ingested": len(ingested),
        "files_detail": ingested,
        "initial_docs": initial_count,
        "final_docs": final_count,
        "new_chunks_added": final_count - initial_count
    }
    
    logger.info(
        "ingestion_completed",
        files=result['files_ingested'],
        entries=result['entries_ingested'],
        new_chunks=result["new_chunks_added"],
        total_docs=final_count
    )
    
    return result


def main():
    """Main ingestion workflow."""
    
    print("\n" + "="*70)
    print("   📚 ADDITIONAL LITERATURE INGESTION")
    print("="*70 + "\n")
    
    # Find files
    files_by_type = find_additional_literature()
    
    total_files = sum(len(files) for files in files_by_type.values())
    
    if total_files == 0:
        print("❌ No additional literature files found in data/raw_literature/additional/")
        print("\n   Please add.ris, .bib, or .txt files to that directory.\n")
        return
    
    print(f"✅ Found {total_files} files to ingest:")
    for file_type, files in files_by_type.items():
        if files:
            print(f"   - {len(files)} {file_type.upper()} files")
    
    print("\n▶️  Starting ingestion...")
    
    # Ingest
    result = ingest_to_chromadb(files_by_type)
    
    # Report
    print("\n" + "="*70)
    print("   ✅ INGESTION COMPLETE")
    print("="*70)
    print(f"\n📊 Results:")
    print(f"   - Files ingested: {result['files_ingested']}")
    print(f"   - Entries ingested: {result['entries_ingested']}")
    print(f"   - New chunks added: {result['new_chunks_added']}")
    print(f"   - Total documents in ChromaDB: {result['final_docs']}")
    print(f"\n📝 Details:")
    for item in result['files_detail'][:10]:  # Show first 10
        print(f"   - {item['file']}: {item.get('title', 'N/A')[:40]}... ({item['chunks']} chunks)")
    if len(result['files_detail']) > 10:
        print(f"   ... and {len(result['files_detail']) - 10} more entries")
    print("\n")
    

if __name__ == "__main__":
    main()
    print(f"   - Total documents: {result['final_docs']}")
    
    print("\n📝 Ingested files:")
    for detail in result['files_detail']:
        print(f"   - {detail['file']}: {detail['chunks']} chunks")
    
    print("\n▶️  Next step:")
    print("   Run article generation again to regenerate low-scoring sections")
    print("   with the new literature.\n")


if __name__ == "__main__":
    main()
