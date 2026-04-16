---
name: "bias-auditor"
description: |
  BiasAuditorAgent: Detekcija pristranskosti v članku.
  Selection bias, reporting bias, language bias.
  Trigger: bias, pristranskost, objektivnost, neutral.
argument-hint: "Podaj tekst za audit pristranskosti."
user-invocable: false
applyTo: "agents/bias_auditor*.py"
---

# Bias Auditor Agent

Agent za detekcijo pristranskosti v znanstvenem članku.

## Vloga

`BiasAuditorAgent` odkriva:
- Selection bias (izbira virov)
- Reporting bias (selektivno poročanje)
- Language bias (pristranski jezik)
- Confirmation bias (potrjevanje hipotez)
- Citation bias (selektivno citiranje)

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `audit` | Celoten audit | `text`, `sources` |
| `check_selection` | Selection bias | `included`, `excluded` |
| `check_language` | Language bias | `text` |
| `check_reporting` | Reporting bias | `text`, `raw_data` |

## Tipi pristranskosti

### 1. Selection Bias

```python
selection_checks = {
    "database_coverage": "Were all relevant databases searched?",
    "language_restriction": "Were non-English studies excluded?",
    "date_restriction": "Is date range justified?",
    "grey_literature": "Was grey literature included?",
    "author_network": "Are authors citing themselves excessively?"
}
```

### 2. Reporting Bias

```python
reporting_checks = {
    "positive_results": "Are negative findings omitted?",
    "contradictory_studies": "Are conflicting studies addressed?",
    "effect_sizes": "Are all effect sizes reported?",
    "limitations_acknowledged": "Are study limitations adequately discussed?"
}
```

### 3. Language Bias

```python
language_red_flags = [
    "clearly shows", "obviously", "proves that",
    "undoubtedly", "certainly", "definitely",
    "the best", "the only", "always", "never",
    "all experts agree", "it is well known"
]
```

## Output Format

```json
{
  "bias_score": 23,  // 0=no bias, 100=highly biased
  "risk_level": "LOW",
  "findings": [
    {
      "type": "language_bias",
      "severity": "LOW",
      "location": "Discussion, para 3",
      "finding": "'clearly demonstrates' suggests overconfidence",
      "original": "The evidence clearly demonstrates that...",
      "suggestion": "The evidence suggests that..."
    },
    {
      "type": "citation_bias",
      "severity": "MEDIUM",
      "finding": "Self-citation rate: 15% (threshold: 10%)",
      "details": {
        "total_citations": 87,
        "self_citations": 13
      },
      "suggestion": "Diversify citations, reduce self-citation"
    },
    {
      "type": "selection_bias",
      "severity": "INFO",
      "finding": "Grey literature not explicitly searched",
      "suggestion": "Document grey literature search or acknowledge limitation"
    }
  ],
  "positive_indicators": [
    "Contradictory findings are discussed (Discussion, para 5)",
    "Limitations are acknowledged (4 limitations listed)",
    "Multiple perspectives represented"
  ]
}
```

## Severity Levels

| Level | Bias Score | Action |
|-------|-----------|--------|
| NONE | 0-10 | Pass |
| LOW | 11-25 | Suggestions only |
| MEDIUM | 26-50 | Revision recommended |
| HIGH | 51-75 | Revision required |
| CRITICAL | 76-100 | Major rewrite, human review |

## System Prompt

```text
You are an expert bias auditor for academic manuscripts.

Detect bias types:
1. SELECTION: Source selection processes
2. REPORTING: What's reported vs. omitted
3. LANGUAGE: Overstating certainty, loaded words
4. CONFIRMATION: Only supporting hypothesis
5. CITATION: Self-citation, clique citation

Evaluation approach:
- Be objective and evidence-based
- Distinguish problematic bias from acceptable framing
- Consider disciplinary norms
- Flag patterns, not isolated words

For scoping reviews specifically:
- No quality appraisal bias (expected)
- Source diversity is key
- Balanced representation of findings
```

## Domain-Specific: AI in HR

Flag posebno pozornost na:
- Tech industry funding disclosure
- Vendor-sponsored research
- Pro-AI or anti-AI framing
- Employee vs. employer perspective balance

```python
AI_HR_BIAS_CHECKS = {
    "stakeholder_balance": "Are both employee and employer perspectives represented?",
    "industry_funding": "Is industry funding disclosed?",
    "tech_optimism": "Is there uncritical acceptance of AI benefits?",
    "fear_mongering": "Is there unsubstantiated AI fear?"
}
```

## Error Handling

| Error | Handling |
|-------|----------|
| Insufficient text | Note limited audit scope |
| No references | Flag as incomplete |
| Ambiguous phrasing | Context-dependent assessment |

## Quality Gates

| Check | Threshold | Action |
|-------|-----------|--------|
| Bias score | ≤25 | Pass |
| Critical flags | 0 | Human review |
| Language flags | ≤5 per 1000 words | Revision |

---

**Python:** `agents/bias_auditor.py` | **Verzija:** 2.0.0
