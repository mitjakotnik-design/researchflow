---
name: "data-extractor"
description: |
  DataExtractorAgent: Strukturirana ekstrakcija podatkov iz člankov.
  PCC tabele, charting forms, kodiranje podatkov. JBI metodologija.
  Domena: AI v HR, psihosocialna tveganja, organizacijska kultura.
  Trigger: ekstrakcija, charting, tabela, podatki, kodiranje, PCC,
  extraction form, data charting, kvalitativno kodiranje.
argument-hint: "Podaj dokumente za ekstrakcijo ali charting template."
user-invocable: false
applyTo: "agents/data_extractor*.py"
---

# Data Extractor Agent

Agent za strukturirano ekstrakcijo podatkov iz znanstvenih člankov.

## Vloga

`DataExtractorAgent` ekstrahira:
- Bibliografske podatke
- Metodološke karakteristike
- Ključne ugotovitve
- PCC elemente (Population, Concept, Context)

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `extract` | Ekstrahira po predlogi | `document`, `template` |
| `batch_extract` | Batch ekstrakcija | `documents`, `template` |
| `validate` | Validira ekstrakcijo | `extracted_data` |
| `export` | Izvozi v format | `data`, `format` |

## Charting Template

### Generic Template
```python
CHARTING_TEMPLATE = {
    # Bibliografski podatki
    "author": str,
    "year": int,
    "title": str,
    "journal": str,
    "doi": str,
    
    # Metodologija
    "study_design": ["qualitative", "quantitative", "mixed", "review"],
    "sample_size": int,
    "country": str,
    "setting": str,
    
    # PCC elementi
    "population": str,
    "concept": str,
    "context": str,
    
    # Ugotovitve
    "key_findings": list[str],
    "ai_type": list[str],
    "hr_function": list[str],
    "psychosocial_risk": list[str],
    "organizational_outcome": list[str],
    
    # Kvaliteta
    "limitations": list[str],
    "quality_notes": str
}
```

### Domain-Specific: AI in HR Template

```python
AI_HR_CHARTING_TEMPLATE = {
    # === BIBLIOGRAFIJA ===
    "id": str,                          # Unikatni ID (e.g., "Smith2024a")
    "author": str,
    "year": int,
    "title": str,
    "journal": str,
    "doi": str,
    "open_access": bool,
    
    # === METODOLOGIJA ===
    "study_design": {
        "type": ["qualitative", "quantitative", "mixed", "conceptual", "review"],
        "subtype": str,                 # e.g., "case study", "survey", "RCT"
        "data_collection": list[str],   # e.g., ["interviews", "survey"]
        "analysis_method": str          # e.g., "thematic analysis", "SEM"
    },
    "sample": {
        "size": int,
        "response_rate": float,         # Če relevantno
        "demographics": str
    },
    "context": {
        "country": list[str],
        "industry": list[str],
        "organization_size": str,       # "SME", "large", "mixed"
        "setting": str                  # "private", "public", "both"
    },
    
    # === AI TEHNOLOGIJA ===
    "ai_technology": {
        "type": list[str],              # ["resume screening", "chatbot", "monitoring"]
        "vendor": str,                  # Če navedeno
        "implementation_stage": str,    # "pilot", "full", "planned"
        "automation_level": str         # "decision support", "automated", "autonomous"
    },
    
    # === HR FUNKCIJA ===
    "hr_function": {
        "primary": list[str],           # ["recruitment", "performance"]
        "secondary": list[str],
        "hr_role_affected": list[str]   # ["HR manager", "recruiter", "employee"]
    },
    
    # === PSIHOSOCIALNI KONSTRUKTI ===
    "psychosocial": {
        "risks_identified": list[str],
        "protective_factors": list[str],
        "theoretical_framework": str,   # e.g., "JD-R model", "stress-coping"
        "measurement_instruments": list[str]  # e.g., ["COPSOQ", "MBI", "UWES"]
    },
    
    # === UGOTOVITVE ===
    "findings": {
        "key_results": list[str],
        "effect_direction": str,        # "positive", "negative", "mixed", "null"
        "effect_magnitude": str,        # Če kvantitativno
        "moderators": list[str],
        "mediators": list[str]
    },
    
    # === ORGANIZACIJSKI OUTCOMES ===
    "organizational_outcomes": {
        "culture_impact": str,
        "trust_impact": str,
        "resistance_factors": list[str],
        "success_factors": list[str]
    },
    
    # === KVALITETA ===
    "quality": {
        "limitations": list[str],
        "bias_risk": str,               # "low", "moderate", "high"
        "generalizability": str,
        "notes": str
    }
}
```

## Parametri

### extract

```python
await extractor.execute(
    action="extract",
    document={
        "id": "paper_001",
        "title": "AI in Hiring: Employee Perspectives",
        "abstract": "...",
        "full_text": "..."
    },
    template="scoping_review"
)
```

### batch_extract

```python
await extractor.execute(
    action="batch_extract",
    documents=included_papers,  # List of documents
    template="scoping_review",
    parallel=True               # Parallel processing
)
```

## Output Format

```json
{
  "paper_id": "paper_001",
  "extraction": {
    "author": "Smith et al.",
    "year": 2024,
    "title": "AI in Hiring: Employee Perspectives",
    "study_design": "qualitative",
    "sample_size": 42,
    "country": "USA",
    "population": "HR professionals and job applicants",
    "concept": "AI-powered resume screening",
    "context": "Corporate hiring processes",
    "key_findings": [
      "Employees reported concerns about fairness",
      "Transparency increased acceptance by 40%"
    ],
    "ai_type": ["resume screening", "candidate ranking"],
    "hr_function": ["recruitment", "selection"],
    "psychosocial_risk": ["perceived unfairness", "lack of control"],
    "organizational_outcome": ["trust reduction", "resistance to change"]
  },
  "confidence": 0.92,
  "extraction_notes": "Full text available, clear methodology section"
}
```

## System Prompt

```text
You are a meticulous data extraction specialist for scoping reviews.

Your task is to:
1. Extract information ONLY from the provided document
2. Use exact quotes when possible
3. Mark uncertain extractions with [UNCERTAIN]
4. Note when information is not reported [NR]

Guidelines:
- Be conservative: don't infer beyond what's stated
- Distinguish between primary and secondary outcomes
- Note methodological limitations
- Flag potential conflicts of interest

Quality checks:
- Verify extracted data against source text
- Cross-reference numbers and statistics
- Note any inconsistencies within the paper
```

## Validacija

```python
await extractor.execute(
    action="validate",
    extracted_data=batch_results,
    validation_rules={
        "required_fields": ["author", "year", "key_findings"],
        "year_range": [2015, 2026],
        "sample_size_min": 1
    }
)
```

## Export formati

```python
await extractor.execute(
    action="export",
    data=extractions,
    format="excel"  # "excel", "csv", "json", "ris"
)
```

## Error Handling

| Error | Handling |
|-------|----------|
| Missing abstract | Extract from full text if available |
| No full text | Mark as "abstract only", extract available |
| Unclear methodology | Mark [UNCERTAIN], flag for human review |
| Multiple studies in paper | Create separate entries |
| Non-English paper | Use translation, note original language |

```python
try:
    extraction = await self._extract(document)
except MissingFieldError as e:
    extraction[e.field] = "[NR]"  # Not Reported
    extraction["extraction_notes"].append(f"{e.field} not reported")
except AmbiguousDataError as e:
    extraction[e.field] = f"[UNCERTAIN: {e.options}]"
    extraction["requires_human_review"] = True
```

## Quality Gates

| Check | Requirement | Action if fail |
|-------|-------------|----------------|
| Required fields | author, year, study_design | Block, request source |
| Year range | 2015-2026 | Verify, may include if seminal |
| Confidence | ≥0.7 per field | Flag for human review |
| Consistency | Internal logic | Auto-validate, flag issues |

## Inter-Rater Reliability

Za pilot ekstrakcijo (prvih 10%) preveri:

```python
kappa = calculate_kappa(extractor_1, extractor_2)
if kappa < 0.8:
    # Calibration meeting needed
    await notify_human(
        "Kappa below threshold",
        kappa=kappa,
        disagreements=get_disagreements()
    )
```

---

**Python:** `agents/data_extractor.py` | **Verzija:** 2.0.0
