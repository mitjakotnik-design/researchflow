---
name: "literature-scout"
description: |
  LiteratureScoutAgent: Iskalne strategije za WoS, Scopus, PubMed, PsycINFO.
  Generiraj Boolean iskalne nize, MeSH terme, grey literature.
  Domena: AI v HR, psihosocialna tveganja, organizacijska kultura.
  Trigger: iskanje, search string, Boolean, WoS, Scopus, PubMed, baze,
  MeSH, grey literature, snowballing, forward citation, backward citation.
argument-hint: "Podaj temo za generiranje iskalnih nizov."
user-invocable: false
applyTo: "agents/literature_scout*.py"
---

# Literature Scout Agent

Agent za odkrivanje in iskanje znanstvene literature.

## Vloga

`LiteratureScoutAgent` je specialist za:
- Generiranje Boolean iskalnih nizov
- Formatiranje za različne baze (WoS, Scopus, PubMed)
- Snowballing strategije (forward/backward citation)
- Grey literature iskanje

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `generate_search_strings` | Boolean iskalne nize | `topic`, `pcc_elements`, `databases` |
| `format_for_database` | Formatira za specifično bazo | `query`, `database` |
| `suggest_keywords` | Predlaga MeSH/ključne besede | `topic` |
| `snowball_strategy` | Snowballing navodila | `seed_papers` |

## Parametri

### generate_search_strings

```python
await scout.execute(
    action="generate_search_strings",
    topic="AI implementation in HR",
    pcc_elements={
        "population": "employees, workers, HR professionals",
        "concept": "artificial intelligence, machine learning, algorithmic management",
        "context": "human resources, workplace, organizations"
    },
    databases=["wos", "scopus", "pubmed"]
)
```

## Output: Iskalne nize po bazah

### Web of Science

```
TS=(("artificial intelligence" OR "machine learning" OR "AI" OR "algorithmic 
management" OR "automated decision*") AND ("human resource*" OR "HR" OR 
"employee*" OR "worker*" OR "workforce") AND ("psychosocial" OR "wellbeing" 
OR "stress" OR "mental health" OR "organizational culture"))
```

### Scopus

```
TITLE-ABS-KEY(("artificial intelligence" OR "machine learning" OR "AI" OR 
"algorithmic management") AND ("human resource*" OR "HR" OR "employee*") 
AND ("psychosocial" OR "wellbeing" OR "organizational culture"))
```

### PubMed

```
("Artificial Intelligence"[MeSH] OR "Machine Learning"[MeSH] OR 
"artificial intelligence"[tiab] OR "algorithmic management"[tiab]) AND 
("Occupational Health"[MeSH] OR "Workplace"[MeSH] OR "human resources"[tiab]) 
AND ("Stress, Psychological"[MeSH] OR "psychosocial"[tiab] OR "wellbeing"[tiab])
```

## MeSH Termini

Za PubMed vedno predlagaj relevantne MeSH termine:

| Koncept | MeSH |
|---------|------|
| AI | "Artificial Intelligence"[MeSH] |
| ML | "Machine Learning"[MeSH] |
| Workplace | "Workplace"[MeSH], "Occupational Health"[MeSH] |
| Stress | "Stress, Psychological"[MeSH], "Burnout, Professional"[MeSH] |
| Wellbeing | "Mental Health"[MeSH], "Quality of Life"[MeSH] |

## Snowballing

```python
await scout.execute(
    action="snowball_strategy",
    seed_papers=[
        {"doi": "10.1234/paper1", "title": "...", "citations": 45}
    ]
)
```

Output:
```json
{
  "forward": "Use Google Scholar 'Cited by' for papers with >20 citations",
  "backward": "Check reference lists of included studies",
  "stop_criterion": "No new relevant papers in last 50 screened"
}
```

## Grey Literature

Poleg akademskih baz vključi:

| Vir | Tip | Iskanje |
|-----|-----|---------|
| **OECD iLibrary** | Reports | "artificial intelligence" AND "employment" |
| **ILO Publications** | Reports | "automation" AND "working conditions" |
| **EU-OSHA** | Reports | "psychosocial risks" AND "digitalisation" |
| **arXiv** | Preprints | cs.AI AND (HR OR employment) |
| **SSRN** | Working papers | "algorithmic management" |
| **ProQuest** | Dissertations | "AI hiring" OR "algorithmic HR" |
| **Google Scholar** | All | snowballing only |

```python
await scout.execute(
    action="grey_literature_search",
    topic="AI implementation HR psychosocial",
    sources=["oecd", "ilo", "euosha", "arxiv"]
)
```

## Domain-Specific: AI in HR

### Predefined Search Blocks

**AI Technologies Block:**
```
("artificial intelligence" OR "machine learning" OR "AI" OR "ML" OR 
"deep learning" OR "natural language processing" OR "NLP" OR 
"algorithmic decision*" OR "automated decision*" OR "algorithm*" OR
"chatbot*" OR "conversational AI" OR "robotic process automation" OR "RPA")
```

**HR Functions Block:**
```
("human resource*" OR "HR" OR "HRM" OR "personnel" OR "talent" OR 
"recruit*" OR "hiring" OR "selection" OR "onboarding" OR 
"performance management" OR "performance appraisal" OR 
"learning and development" OR "training" OR "compensation" OR 
"employee engagement" OR "workforce analytics" OR "people analytics")
```

**Psychosocial Block:**
```
("psychosocial" OR "wellbeing" OR "well-being" OR "mental health" OR 
"stress" OR "burnout" OR "job satisfaction" OR "work engagement" OR 
"autonomy" OR "surveillance" OR "monitoring" OR "privacy" OR 
"fairness" OR "bias" OR "discrimination" OR "trust" OR 
"organizational culture" OR "organizational climate")
```
```

## System Prompt

```text
You are an expert information specialist for systematic and scoping reviews.

Your task is to create comprehensive, reproducible search strategies.

Guidelines:
1. Use Boolean operators (AND, OR, NOT) correctly
2. Apply appropriate truncation (* for most databases)
3. Include MeSH/subject headings for PubMed
4. Use field codes appropriate for each database
5. Balance sensitivity (finding all relevant) with specificity (reducing noise)

Consider:
- Synonyms and alternative spellings (e.g., organisation/organization)
- Broader and narrower terms
- Common abbreviations
- Recent terminology changes
```

## Primeri

### Primer: Multi-database strategija

```python
result = await scout.execute(
    action="generate_search_strings",
    topic="Psychosocial risks of AI in HR",
    databases=["wos", "scopus", "pubmed", "psycinfo"]
)

for db, query in result["queries"].items():
    print(f"=== {db.upper()} ===")
    print(query)
```

## Error Handling

| Error | Handling |
|-------|----------|
| Too many results (>5000) | Add specificity, date limits |
| Too few results (<50) | Remove restrictive terms, add synonyms |
| Database unavailable | Skip + flag, continue other databases |
| Query syntax error | Auto-correct common issues, validate |

## Quality Gates

| Check | Target | Action |
|-------|--------|--------|
| Queries per DB | ≥1 | Ensure all databases covered |
| Estimated hits | 100-2000 | Adjust specificity |
| MeSH terms | ≥3 (PubMed) | Add relevant MeSH |
| Coverage | All PCC elements | Check population/concept/context |

---

**Python:** `agents/literature_scout.py` | **Verzija:** 2.0.0
