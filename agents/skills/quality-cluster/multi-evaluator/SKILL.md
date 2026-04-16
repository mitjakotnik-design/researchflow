---
name: "multi-evaluator"
description: |
  MultiEvaluatorAgent: Večdimenzionalna evalvacija kvalitete teksta.
  Accuracy, coherence, completeness, style, citations.
  Trigger: evalvacija, evaluate, quality score, ocena, kakovost.
argument-hint: "Podaj tekst za evalvacijo."
user-invocable: false
applyTo: "agents/multi_evaluator*.py"
---

# Multi Evaluator Agent

Agent za večdimenzionalno evalvacijo kvalitete članka.

## Vloga

`MultiEvaluatorAgent` ocenjuje:
- Accuracy (točnost trditev)
- Coherence (logična povezanost)
- Completeness (pokritost tem)
- Style (akademski slog)
- Citations (ustreznost citiranja)

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `evaluate` | Celotna evalvacija | `text`, `section`, `criteria` |
| `evaluate_dimension` | Posamezna dimenzija | `text`, `dimension` |
| `compare` | Primerjaj verzije | `text_v1`, `text_v2` |

## Evalvacijske dimenzije

### 1. Accuracy (0-100)

```python
accuracy_criteria = {
    "claim_verification": 0.4,      # Trditve potrjene z viri
    "statistical_accuracy": 0.2,    # Pravilni statistični podatki
    "citation_accuracy": 0.2,       # Citati ustrezajo virom
    "terminology_accuracy": 0.2     # Pravilna uporaba terminov
}
```

### 2. Coherence (0-100)

```python
coherence_criteria = {
    "logical_flow": 0.3,            # Logičen potek argumentacije
    "paragraph_transitions": 0.25,  # Prehodi med odstavki
    "section_structure": 0.25,      # Struktura sekcije
    "argument_consistency": 0.2     # Konsistentnost argumentov
}
```

### 3. Completeness (0-100)

```python
completeness_criteria = {
    "section_coverage": 0.4,        # Vsi zahtevani elementi
    "topic_depth": 0.3,             # Globina obravnave
    "evidence_coverage": 0.2,       # Pokritost z dokazi
    "word_count": 0.1               # Dosežen word count
}
```

### 4. Style (0-100)

```python
style_criteria = {
    "academic_tone": 0.3,           # Akademski ton
    "clarity": 0.25,                # Jasnost
    "conciseness": 0.25,            # Jedrnastnost
    "grammar": 0.2                  # Slovnica
}
```

### 5. Citations (0-100)

```python
citation_criteria = {
    "density": 0.3,                 # Ustrezna gostota
    "recency": 0.25,                # Aktualnost virov
    "diversity": 0.25,              # Raznolikost virov
    "format_compliance": 0.2        # Skladnost s slogom
}
```

## Output Format

```json
{
  "overall_score": 82,
  "dimensions": {
    "accuracy": {
      "score": 88,
      "details": {
        "claims_verified": 45,
        "claims_unverified": 3,
        "issues": ["Claim on p.5 lacks citation"]
      }
    },
    "coherence": {
      "score": 79,
      "details": {
        "weak_transitions": ["para 4→5", "para 12→13"]
      }
    },
    "completeness": {
      "score": 85,
      "missing": ["Limitations subsection needs expansion"]
    },
    "style": {
      "score": 80,
      "issues": ["Informal language in Methods (2 instances)"]
    },
    "citations": {
      "score": 78,
      "issues": ["Citation density low in Discussion"]
    }
  },
  "recommendation": "Minor revisions needed",
  "priority_fixes": [
    "Add citation for claim on p.5",
    "Improve transitions between thematic sections",
    "Expand Limitations"
  ]
}
```

## System Prompt

```text
You are an expert academic manuscript evaluator.

Evaluate the manuscript across five dimensions:
1. ACCURACY: Are all claims supported by evidence?
2. COHERENCE: Does the argument flow logically?
3. COMPLETENESS: Are all required elements present?
4. STYLE: Is the writing appropriate for academic publication?
5. CITATIONS: Are sources used appropriately?

Scoring guidelines:
- 90-100: Publication ready
- 80-89: Minor revisions needed
- 70-79: Moderate revisions needed
- 60-69: Major revisions needed
- <60: Requires substantial rewriting

Be specific in feedback:
- Cite exact locations of issues
- Provide actionable suggestions
- Prioritize most impactful fixes
```

## Error Handling

| Error | Handling |
|-------|----------|
| Incomplete text | Score completeness accordingly |
| No citations | Flag, still evaluate other dimensions |
| Ambiguous claims | Mark for human review |

## Quality Gates

| Check | Pass threshold | Action if fail |
|-------|---------------|----------------|
| Overall score | ≥70 | Require revision |
| Any dimension | ≥60 | Flag that dimension |
| Critical issues | 0 | Block until resolved |

---

**Python:** `agents/multi_evaluator.py` | **Verzija:** 2.0.0
