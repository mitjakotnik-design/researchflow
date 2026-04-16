# 🚀 GAP DETECTION WORKFLOW - Quick Start Guide
**Verzija:** 2.0 (Production Ready)  
**Status:** ✅ Fully Tested & Improved

---

## 📖 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Configuration](#configuration)
4. [Workflow Steps](#workflow-steps)
5. [Error Handling](#error-handling)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 OVERVIEW

Gap detection workflow avtomatsko:
- 🔍 Detektira low-scoring sections (< threshold)
- 🧠 Identificira manjkajoče teorije/metodologije
- 📝 Generira WOS search queries
- ⏸️ Pausira orchestrator
- 📚 Omogoča dodajanje literature
- 🔄 Regenerira affected sections

**Celoten proces:** ~20-30 minut (odvisno od WOS search)

---

## ✅ PREREQUISITES

### 1. Dependencies Installed
```bash
pip install rispy bibtexparser tenacity
```

### 2. Directory Structure
```
data/
├── raw_literature/
│   └── additional/          # ← Place new .ris/.bib files here
├── reports/                 # ← Gap reports saved here
└── chroma/                  # ← ChromaDB storage
```

### 3. Existing ChromaDB
- ✅ At least 5000+ chunks ingested
- ✅ Article generation started

---

## ⚙️ CONFIGURATION

### Default Settings (Optional)

**File:** `orchestration/meta_orchestrator.py`

```python
config = OrchestratorConfig(
    gap_detection_threshold=50,  # Score below which to trigger gap detection
    # ... other settings
)
```

**Recommended values:**
- **Conservative:** 40 (detects more gaps)
- **Default:** 50 (balanced)
- **Aggressive:** 60 (only severe gaps)

---

## 📋 WORKFLOW STEPS

### Step 1: Start Article Generation

```bash
cd c:\RaniaDR\scoping-review-agents
python run_full_generation.py
```

**Monitor console:**
```
✅ Abstract: score 86/100
✅ Results: score 92/100
⚠️ Methods: score 36/100
⚠️ Introduction: score 39/100
```

---

### Step 2: Automatic Pause (if gaps detected)

**Console output:**
```
======================================================================
   ⏸️  ORCHESTRATOR PAUSED - ACTION REQUIRED
======================================================================

🔍 Knowledge gaps detected in 2 sections:
   - METHODS: score 36/100
   - INTRODUCTION: score 39/100

📚 Total missing concepts: 8

📝 Gap report saved to: data/reports/gap_report_article_20260416_131705_145923.md

✅ NEXT STEPS:
   1. Review gap report for WOS search queries
   2. Execute searches in Web of Science
   3. Download results as .ris or .bib files
   4. Place files in: data/raw_literature/additional/
   5. Run ingestion: python scripts/ingest_additional_literature.py
   6. Resume generation: orchestrator.resume_after_literature_addition()
======================================================================
```

---

### Step 3: Review Gap Report

**Open:** `data/reports/gap_report_article_20260416_131705_145923.md`

**Find section:**
```markdown
## Web of Science Queries

### Query 1
```
TI=(("PRISMA-ScR" OR "PRISMA scoping")) 
AND TS=(("scoping review" OR "systematic review"))
```
**Purpose:** Find PRISMA-ScR methodology literature  
**Expected results:** 10-50
```

---

### Step 4: Execute WOS Search

1. **Odpri:** [Web of Science](https://www.webofscience.com)
2. **Izberi:** Advanced Search
3. **Kopiraj query** iz gap report
4. **Paste** v WOS search box
5. **Izvedi search**
6. **Download rezultate:**
   - Format: RIS or BibTeX
   - Include: Full Record and Cited References
   - Save to: `data/raw_literature/additional/theories_prisma.ris`

**Primer filename convention:**
```
data/raw_literature/additional/
├── theories_jdr_model.ris          # Teorije za introduction
├── methodology_prisma.ris           # Metodologija za methods
└── empirical_ai_adoption.ris       # Empirična literatura
```

---

### Step 5: Ingest Additional Literature

```bash
cd c:\RaniaDR\scoping-review-agents
python scripts/ingest_additional_literature.py
```

**Expected output:**
```
======================================================================
   📚 ADDITIONAL LITERATURE INGESTION
======================================================================

✅ Found 3 files to ingest:
   - 2 RIS files
   - 1 BIB files

▶️  Starting ingestion...

✅ Ingested theories_jdr_model.ris
   - 5 entries, 8 chunks

✅ Ingested methodology_prisma.ris
   - 3 entries, 4 chunks

======================================================================
   ✅ INGESTION COMPLETE
======================================================================

📊 Results:
   - Files ingested: 3
   - Entries ingested: 8
   - New chunks added: 12
   - Total documents in ChromaDB: 5995

📝 Details:
   - theories_jdr_model.ris_20260416_a3f8b12c_entry_0: The Job Demands-Resources Model... (2 chunks)
   - [...]
```

**Verification:**
- ✅ `new_chunks_added` > 0 (nove literature dodana)
- ✅ No errors logged
- ✅ BM25 index rebuilt

---

### Step 6: Resume Generation

**Option A: Python script**
```python
from orchestration.meta_orchestrator import MetaOrchestrator

# Load existing state
state_manager = StateManager()
state_manager.load_state("article_20260416_131705")

# Resume
orchestrator = MetaOrchestrator(config, state_manager, models_config)
await orchestrator.resume_after_literature_addition()
```

**Option B: Interactive**
```python
# In running Python session:
await orchestrator.resume_after_literature_addition()
```

**Expected behavior:**
- ✅ Regenerates only low-scoring sections (Methods, Introduction)
- ✅ Uses NEW literature from ChromaDB
- ✅ Continues with QA phase → Finalization

---

### Step 7: Monitor Regeneration

**Console output:**
```
🔄 Resuming after literature addition...
   Sections to regenerate: 2 (methods, introduction)

📝 Regenerating: methods
   Iteration 1: score 52 (+16 from 36)
   Iteration 2: score 67 (+15)
   Iteration 3: score 71 (+4)
   ✅ TARGET REACHED (>65)

📝 Regenerating: introduction
   Iteration 1: score 58 (+19 from 39)
   Iteration 2: score 69 (+11)
   ✅ TARGET REACHED (>65)

✅ Article generation completed after resume
```

---

## 🛡️ ERROR HANDLING

### Improved Error Messages (v2.0)

**Before:**
```
ERROR: ris_parse_failed - test.ris
```

**After v2.0:**
```
ERROR: ris_encoding_error - test.ris
  Error: 'utf-8' codec can't decode byte 0xff
  Hint: Try saving file with UTF-8 encoding
```

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `rispy_not_installed` | Missing dependency | `pip install rispy` |
| `ris_file_corrupt` | Malformed RIS file | Re-download from WOS |
| `ris_encoding_error` | Wrong encoding | Save as UTF-8 |
| `chromadb_connection_error` | ChromaDB not initialized | Check `data/chroma/` exists |
| `llm_timeout` (auto-resolved) | API timeout | Automatic retry (3x) |

### LLM Retry Logic (v2.0)

**Automatic retry on:**
- TimeoutError
- ConnectionError

**Retry strategy:**
- Attempt 1: Immediate
- Attempt 2: Wait 2s
- Attempt 3: Wait 4s
- Fail: Raise exception

**User action:** None (transparent)

---

## 🔧 TROUBLESHOOTING

### Issue 1: No gaps detected (expected gaps)

**Check:**
```bash
# View current scores
python -c "
from config import StateManager
sm = StateManager()
state = sm.load_state('article_20260416_131705')
for sid, sec in state.sections.items():
    print(f'{sid}: {sec.current_score}')
"
```

**Solution:**
- Lower `gap_detection_threshold` in config (e.g., 55 → 45)

---

### Issue 2: Ingestion adds 0 chunks

**Možne vzroki:**
1. Files že ingestan (unique IDs preprečijo duplicates)
2. Files prazni ali corrupt

**Check:**
```bash
# List files
ls data/raw_literature/additional/

# Check file content
head -20 data/raw_literature/additional/theories.ris
```

**Solution:**
- Če files že ingestan: OK (prevent duplicates = feature!)
- Če files prazni: Re-download from WOS

---

### Issue 3: Gap report not found

**Check timestamp:**
```bash
ls -lt data/reports/ | head -5
```

**Expected:**
```
gap_report_article_20260416_131705_145923.md  ← Najnovejši
gap_report_article_20260416_131705_143012.md  ← Prejšnji pause
```

**Solution:**
- Uporabi najnovejši report (highest timestamp)

---

### Issue 4: Low score persists after resume

**Možni vzroki:**
1. Literatura ni relevant
2. Premalo literature dodane
3. Quality threshold previsok

**Check:**
```bash
# Verify ChromaDB increase
python -c "
from rag import HybridSearch
hs = HybridSearch()
hs.initialize()
print(hs.get_stats())
"
```

**Solution:**
- Dodaj več relevant literature
- Lower quality threshold
- Manually review regenerated content

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- [IMPROVEMENTS_IMPLEMENTED.md](IMPROVEMENTS_IMPLEMENTED.md) - Technical details
- [CHANGELOG_v2.0.md](CHANGELOG_v2.0.md) - What changed
- [GAP_DETECTION_WORKFLOW.md](GAP_DETECTION_WORKFLOW.md) - Original design

### Key Files
- `orchestration/meta_orchestrator.py` - Main orchestrator logic
- `scripts/ingest_additional_literature.py` - Ingestion script
- `agents/gap_identifier.py` - Gap analysis agent
- `agents/literature_scout.py` - WOS query generation

### Configuration Files
- `config/quality_thresholds.py` - Quality settings
- `config/sections_config.py` - Section definitions
- `orchestration/meta_orchestrator.py` - `OrchestratorConfig`

---

## 🎯 BEST PRACTICES

### 1. Literature Selection
- ✅ **DO:** Focus on high-impact journals
- ✅ **DO:** Include seminal papers (high citations)
- ✅ **DO:** Match publication year range (recent + classic)
- ❌ **DON'T:** Add unrelated literature (noise)

### 2. WOS Query Tuning
- ✅ **DO:** Use provided queries as starting point
- ✅ **DO:** Adjust if results too broad/narrow
- ❌ **DON'T:** Drastically change query intent

### 3. File Organization
```
data/raw_literature/additional/
├── theories/
│   ├── jdr_model.ris
│   └── cor_theory.ris
├── methodology/
│   └── prisma_scr.ris
└── empirical/
    └── ai_adoption.ris
```

### 4. Monitoring
- 📊 Check score improvements (before/after)
- 📊 Track ingestion stats (chunks added)
- 📊 Review gap reports (are gaps addressed?)

---

## ✅ SUCCESS CHECKLIST

**Before starting:**
- [ ] Dependencies installed (`rispy`, `bibtexparser`, `tenacity`)
- [ ] ChromaDB initialized (5000+ chunks)
- [ ] config/quality_thresholds.py configured

**During gap detection:**
- [ ] Console shows pause message
- [ ] Gap report generated in `data/reports/`
- [ ] WOS queries present in report

**During literature addition:**
- [ ] Files downloaded from WOS (.ris or .bib)
- [ ] Files placed in `data/raw_literature/additional/`
- [ ] Ingestion script run successfully
- [ ] ChromaDB chunk count increased

**After resume:**
- [ ] Low-scoring sections regenerated
- [ ] Scores improved (target: +20-30 points)
- [ ] QA phase completed
- [ ] Final article generated

---

## 🏆 EXPECTED OUTCOMES

**Methods section:**
- Before: 36/100 (missing PRISMA-ScR)
- After: 65-75/100 (+29-39 points)

**Introduction section:**
- Before: 39/100 (missing JD-R, COR theories)
- After: 70-80/100 (+31-41 points)

**Overall article quality:**
- Before: ~50-60% (incomplete)
- After: 85-95% (publication-ready)

---

## 💡 TIPS & TRICKS

### Tip 1: Batch Processing
Add all literature at once instead of multiple pause cycles:
```bash
# Download all WOS results first
# Then run single ingestion
python scripts/ingest_additional_literature.py
```

### Tip 2: Preview Before Resume
```python
# Check what will be regenerated
state = state_manager.load_state("article_20260416_131705")
low_scoring = [s for s, state in state.sections.items() 
               if state.current_score < config.gap_detection_threshold]
print(f"Will regenerate: {low_scoring}")
```

### Tip 3: Custom Threshold Per Section
Not supported yet, but you can manually trigger:
```python
# Force regeneration of specific section
state.sections["methods"].current_score = 45  # Below threshold
await orchestrator.resume_after_literature_addition()
```

---

## 🆘 SUPPORT

**Issues?**
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in console output
3. Verify ChromaDB stats
4. Check gap report for clues

**Contact:**
- GitHub Issues: [repository link]
- Documentation: `docs/` folder

---

*Last updated: 2026-04-16*  
*Version: 2.0 - Production Ready*  
*Status: ✅ Fully Tested*
