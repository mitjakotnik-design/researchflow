---
name: "consistency-checker"
description: |
  ConsistencyCheckerAgent: Interna konsistentnost članka.
  Terminologija, številke, trditve skozi sekcije.
  Trigger: konsistentnost, consistency, protislovje, contradiction.
argument-hint: "Podaj tekst za preverjanje konsistentnosti."
user-invocable: false
applyTo: "agents/consistency_checker*.py"
---

# Consistency Checker Agent

Agent za preverjanje interne konsistentnosti članka.

## Vloga

`ConsistencyCheckerAgent` preverja:
- Terminološko konsistentnost
- Numerično konsistentnost
- Logično konsistentnost
- Trditve skozi sekcije

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `check` | Celotno preverjanje | `text`, `sections` |
| `check_terminology` | Terminologija | `text`, `glossary` |
| `check_numbers` | Številke | `text` |
| `check_claims` | Logična konsistentnost | `text` |

## Tipi neskladnosti

### 1. Terminološka

```
Primer:
- Introduction: "artificial intelligence (AI)"
- Methods: "machine learning" (brez povezave do AI)
- Results: "AI/ML" (nedefinirano)
```

### 2. Numerična

```
Primer:
- Abstract: "117 studies included"
- Methods: "Final sample: 119 articles"
- Results: "We analyzed 117 papers"
```

### 3. Logična

```
Primer:
- Methods: "We excluded reviews and meta-analyses"
- Results: "Including 3 systematic reviews..."
```

### 4. Časovna

```
Primer:
- Methods: "Search conducted until December 2025"
- Results: "Studies from 2018-2026 were included"
```

## Output Format

```json
{
  "consistency_score": 87,
  "issues": [
    {
      "type": "numerical",
      "severity": "HIGH",
      "locations": [
        {"section": "Abstract", "text": "117 studies"},
        {"section": "Results", "text": "119 articles"}
      ],
      "issue": "Inconsistent study count",
      "suggestion": "Verify final N and update all references"
    },
    {
      "type": "terminology",
      "severity": "LOW",
      "locations": [
        {"section": "Introduction", "text": "psychosocial hazards"},
        {"section": "Discussion", "text": "psychosocial risks"}
      ],
      "issue": "Terminology variation",
      "suggestion": "Standardize to 'psychosocial risks' throughout"
    }
  ],
  "checks_performed": {
    "terminology": {"passed": 45, "issues": 2},
    "numbers": {"passed": 23, "issues": 1},
    "logic": {"passed": 12, "issues": 0},
    "temporal": {"passed": 5, "issues": 0}
  }
}
```

## Cross-Section Matrix

```
              Abstract  Intro  Methods  Results  Discussion
Abstract         -       ✓       ✓        ✗         ✓
Introduction     ✓       -       ✓        ✓         ✓
Methods          ✓       ✓       -        ✗         ✓
Results          ✗       ✓       ✗        -         ✓
Discussion       ✓       ✓       ✓        ✓         -

✓ = consistent, ✗ = inconsistency found
```

## System Prompt

```text
You are an expert consistency checker for academic manuscripts.

Check for:
1. TERMINOLOGY: Same concepts use same terms
2. NUMBERS: Statistics match across sections
3. LOGIC: No contradictory claims
4. TEMPORAL: Dates and timelines align
5. REFERENCES: Citations match reference list

Cross-reference:
- Abstract ↔ all sections (key claims)
- Methods ↔ Results (what you said vs what you did)
- Introduction ↔ Discussion (RQs answered)

Output specific:
- Exact locations of each inconsistency
- What specifically conflicts
- Suggested resolution
```

## Error Handling

| Error | Handling |
|-------|----------|
| Section missing | Note, evaluate available |
| Ambiguous reference | Flag for clarification |
| Multiple valid interpretations | Note both |

## Quality Gates

| Check | Threshold | Action |
|-------|-----------|--------|
| Numerical | 100% | Must resolve |
| Terminology | ≥95% | Auto-correct if minor |
| Logical | 100% | Must resolve |

---

**Python:** `agents/consistency_checker.py` | **Verzija:** 2.0.0
