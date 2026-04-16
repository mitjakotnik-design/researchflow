---
name: "terminology-guardian"
description: |
  TerminologyGuardianAgent: Konsistentna terminologija, definicije, glosar.
  Preveri uporabo terminov, predlagaj standardizacijo.
  Trigger: terminologija, terminology, definicije, glossary, konsistenca.
argument-hint: "Podaj tekst za preverjanje terminologije."
user-invocable: false
applyTo: "agents/terminology_guardian*.py"
---

# Terminology Guardian Agent

Agent za zagotavljanje konsistentne terminologije.

## Vloga

`TerminologyGuardianAgent` skrbi za:
- Konsistentno uporabo terminov
- Definicije ključnih konceptov
- Glosar za članek
- Standardizacijo akronimov

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `check` | Preveri terminologijo | `text`, `glossary` |
| `standardize` | Standardiziraj termine | `text`, `rules` |
| `extract_terms` | Izvleci ključne termine | `text` |
| `build_glossary` | Zgradi glosar | `text`, `domain` |

## Domain Glossary: AI in HR

```python
AI_HR_GLOSSARY = {
    # AI terminologija
    "artificial intelligence": {
        "abbreviation": "AI",
        "first_use": "artificial intelligence (AI)",
        "subsequent": "AI",
        "definition": "Computer systems performing tasks requiring human intelligence"
    },
    "algorithmic management": {
        "abbreviation": None,
        "variants": ["algorithmic control", "algorithmic HRM"],
        "preferred": "algorithmic management",
        "definition": "Use of algorithms to manage, control, and evaluate workers"
    },
    "machine learning": {
        "abbreviation": "ML",
        "note": "Use 'AI' unless specifically discussing ML techniques"
    },
    
    # HR terminologija
    "human resources": {
        "abbreviation": "HR",
        "note": "Prefer 'HR' after first use"
    },
    "human resource management": {
        "abbreviation": "HRM",
        "variants": ["HR management"],
        "preferred": "HRM"
    },
    
    # Psihosocialni konstrukti
    "psychosocial risks": {
        "definition": "Aspects of work design and management that may cause psychological or physical harm",
        "note": "Define on first use in Introduction"
    },
    "job autonomy": {
        "variants": ["work autonomy", "employee autonomy"],
        "preferred": "job autonomy",
        "definition": "Degree of control over how work is performed"
    },
    "surveillance": {
        "variants": ["monitoring", "tracking"],
        "note": "Use 'surveillance' for perception-focused, 'monitoring' for practice-focused"
    }
}
```

## Akcija: Check

```python
await guardian.execute(
    action="check",
    text=article_text,
    glossary=AI_HR_GLOSSARY
)
```

Output:
```json
{
  "issues": [
    {
      "term": "machine learning",
      "location": "paragraph 3",
      "issue": "Used without abbreviation after first use",
      "suggestion": "Use 'ML' or 'AI' depending on context"
    },
    {
      "term": "employee monitoring",
      "location": "paragraph 7",
      "issue": "Inconsistent with 'surveillance' used elsewhere",
      "suggestion": "Standardize to 'AI-enabled monitoring' or 'employee surveillance'"
    }
  ],
  "consistency_score": 0.87,
  "terms_found": 45,
  "terms_standardized": 39
}
```

## Akcija: Build Glossary

```python
await guardian.execute(
    action="build_glossary",
    text=full_article,
    domain="ai_hr_psychosocial",
    output_format="apa_table"
)
```

Output za članek:
```
| Term | Definition | First Used |
|------|------------|------------|
| AI | Computer systems performing tasks... | Introduction, p. 2 |
| Algorithmic management | Use of algorithms to manage... | Introduction, p. 3 |
```

## System Prompt

```text
You are an expert in scientific terminology standardization.

Your tasks:
1. Identify all domain-specific terms
2. Check consistency of term usage throughout
3. Verify abbreviations are defined at first use
4. Suggest preferred terms based on current literature

Rules:
- Define abbreviations at first use: "artificial intelligence (AI)"
- Use abbreviated form consistently after definition
- Prefer established terminology over novel coinages
- Maintain consistency with cited sources

Flag issues:
- Undefined abbreviations
- Inconsistent term variants
- Ambiguous usage
- Outdated terminology
```

## Error Handling

| Error | Handling |
|-------|----------|
| Unknown term | Flag for human review |
| Conflicting definitions | Use most cited source |
| Abbreviation collision | Expand one instance |

## Quality Gates

| Check | Target | Action |
|-------|--------|--------|
| Term consistency | 100% | Auto-correct |
| Abbreviation definition | 100% | Insert definition |
| Glossary completeness | ≥90% domain terms | Add missing |

---

**Python:** `agents/terminology_guardian.py` | **Verzija:** 2.0.0
