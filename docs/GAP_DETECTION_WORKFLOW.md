# Gap Detection & Targeted Literature Addition

## Overview

This workflow automatically detects knowledge gaps in low-scoring article sections and enables human-in-the-loop literature addition to improve quality.

## Problem Solved

When certain sections (Introduction, Methods) score below 50, it often indicates missing:
- Theoretical frameworks
- Specific methodologies  
- Key conceptual models
- Foundational research

Rather than letting the system generate low-quality content, this workflow:
1. Detects specific gaps
2. Generates targeted search queries
3. Pauses for human literature addition
4. Regenerates sections with enriched knowledge base

## Workflow Steps

### 1. Automatic Gap Detection

After the writing phase, the system automatically:
- Identifies sections with score < 50
- Analyzes what concepts/theories are missing
- Generates Web of Science (WOS) query strings

```python
# Example detected gap
{
  "section": "introduction",
  "missing_concepts": ["Job Demands-Resources model", "Conservation of Resources theory"],
  "wos_query": 'TI=(("Job Demands-Resources" OR "JD-R")) AND TI=(("AI" OR "artificial intelligence"))'
}
```

### 2. Workflow Pause

When gaps are detected, the system:
- Pauses execution
- Generates a gap report (`output/gap_detection/gap_report_TIMESTAMP.md`)
- Displays WOS queries in the console
- Saves workflow state

**Console Output:**
```
🔍 KNOWLEDGE GAPS DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Low-scoring sections: introduction, methods
🔎 Gaps identified: 4

📝 WOS Query Strings (2):
────────────────────────────────────────────

1. TI=(("Job Demands-Resources" OR "Conservation of Resources")) AND TI=(("AI" OR "artificial intelligence"))

2. TI=(("PRISMA-ScR" OR "systematic review methodology")) AND TI=(("scoping review"))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   📚 ACTION REQUIRED

▶️  Steps to continue:
   1. Copy the WOS queries above
   2. Run them in Web of Science
   3. Export results as .ris or .bib
   4. Place files in: data/raw_literature/additional/
   5. Run: python scripts/ingest_additional_literature.py
   6. Resume generation
```

### 3. Literature Addition (Human Step)

**3.1 Run WOS Queries**
- Go to [Web of Science](https://www.webofscience.com/)
- Paste the generated query
- Refine if needed
- Export results

**3.2 Export Options**
Supported formats:
- `.ris` (recommended - RIS format)
- `.bib` (BibTeX format)
- `.txt` (plain text with structure)

**3.3 Place Files**
```bash
# Copy exported files to:
data/raw_literature/additional/

# Example:
data/raw_literature/additional/
├── jdr_model_ai.ris
├── cor_theory_workplace.ris
└── prisma_scr_method.bib
```

### 4. Ingest Additional Literature

Run the ingestion script:

```bash
python scripts/ingest_additional_literature.py
```

**Output:**
```
📚 ADDITIONAL LITERATURE INGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Found 3 files to ingest:
   - 2 RIS files
   - 1 BIB files

▶️  Starting ingestion...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ INGESTION COMPLETE

📊 Results:
   - Files ingested: 3
   - New chunks added: 247
   - Total documents: 6224

📝 Ingested files:
   - jdr_model_ai.ris: 89 chunks
   - cor_theory_workplace.ris: 102 chunks
   - prisma_scr_method.bib: 56 chunks

▶️  Next step:
   Run article generation again to regenerate low-scoring sections
```

### 5. Resume & Regenerate

Two options:

**Option A: Resume Existing Workflow** (Recommended)
```python
# In Python
from orchestration import MetaOrchestrator

# Load existing state
orchestrator = MetaOrchestrator.load_state("article_20260416_131705")

# Resume and regenerate low-scoring sections
await orchestrator.resume_after_literature_addition(
    sections_to_regenerate=["introduction", "methods"]
)
```

**Option B: Full Regeneration**
```bash
# Re-run full generation
python run_full_generation.py

# System will use enriched ChromaDB (6224 chunks instead of 5977)
# Low-scoring sections should improve significantly
```

##Configuration

### Adjust Gap Detection Threshold

```python
# In orchestration/gap_detection_workflow.py
GapDetectionWorkflow(
    min_score_threshold=50  # Default: 50. Lower = more strict
)
```

### Customize WOS Query Format

Edit `_generate_wos_queries()` method to change query structure:

```python
# Current format:
TI=(("concept1" OR "concept2")) AND TI=(("AI" OR "artificial intelligence"))

# Alternatives:
- TS=(...) for topic search (broader)
- AB=(...) for abstract search
- Add year constraints: AND PY=(2015-2026)
```

## Expected Improvements

| Section | Before | After | Improvement |
|---------|--------|-------|-------------|
| Introduction | 36-39 | 65-75 | +30-40 points |
| Methods | 30-36 | 55-70 | +25-40 points |

**Why It Works:**
- LLM has specific theoretical content to cite
- Reduces fact-checking contradictions
- Provides methodological details
- Grounds content in established literature

## Troubleshooting

**Problem: No gaps detected but scores are low**
```python
# Lower the threshold
min_score_threshold=60  # instead of 50
```

**Problem: WOS queries return no results**
- Try broader terms
- Remove restrictive AND clauses
- Use topic search (TS=) instead of title (TI=)

**Problem: Ingested files not appearing in ChromaDB**
- Check file encoding (should be UTF-8)
- Verify file format (.ris, .bib have proper structure)
- Check logs for specific ingestion errors

**Problem: Regenerated sections still low-scoring**
- May need MORE literature (check if enough relevant chunks)
- Verify ingested literature is actually relevant
- Consider manual section editing

## Integration with Existing Workflow

The gap detection is automatically triggered after the writing phase. To disable:

```python
# In meta_orchestrator.py _run_writing_phase()
# Comment out:
# paused = await self._check_for_gaps_and_pause()
```

## Files Created

```
orchestration/
├── gap_detection_workflow.py      # Core workflow logic
└── gap_detection_integration.py   # Integration with meta_orchestrator

scripts/
└── ingest_additional_literature.py # Ingestion script

output/gap_detection/
└── gap_report_TIMESTAMP.md         # Generated report

data/raw_literature/additional/
└── (user-added .ris, .bib files)
```

## API Usage

```python
from orchestration.gap_detection_workflow import GapDetectionWorkflow, KnowledgeGap

# Initialize
workflow = GapDetectionWorkflow(
    state_manager=state_manager,
    gap_identifier_agent=gap_agent,
    literature_scout_agent=scout_agent,
    rag_system=hybrid_search,
    min_score_threshold=50
)

# Detect gaps
result = await workflow.detect_gaps_in_sections(sections)

# Pause for literature
report_file = workflow.pause_for_literature(result)

# Later: Ingest
await workflow.ingest_additional_literature()
```

## Future Enhancements

- [ ] Automatic gray literature search (arXiv, SSRN)
- [ ] Semantic Scholar API integration
- [ ] Citation network expansion
- [ ] Automated relevance filtering
- [ ] Real-time gap detection during writing

## Related Documentation

- [ChromaDB Documentation](../rag/README.md)
- [Agent System Overview](../agents/README.md)
- [Meta Orchestrator Guide](../orchestration/README.md)

---

**Questions?** Open an issue or contact the development team.
