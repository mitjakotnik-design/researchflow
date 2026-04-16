---
name: "synthesizer"
description: |
  SynthesizerAgent: Narativna sinteza literature po tematski/framework metodi.
  Integracija ugotovitev, identifikacija vzorcev, konsistentna pripoved.
  Trigger: sinteza, synthesis, integrate, narativna, tematsko, framework.
argument-hint: "Podaj ekstrahirane ugotovitve za sintezo."
user-invocable: false
applyTo: "agents/synthesizer*.py"
---

# Synthesizer Agent

Agent za narativno sintezo literature.

## Vloga

`SynthesizerAgent` sintetizira:
- Tematska sinteza (induktivne teme)
- Framework sinteza (deduktivne kategorije)
- Realistična sinteza (mehanizmi, konteksti, izidi)
- Konceptualno kartiranje

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `synthesize` | Celotna sinteza | `findings`, `method`, `framework` |
| `thematic` | Tematska sinteza | `findings`, `theme_level` |
| `framework` | Framework sinteza | `findings`, `framework_categories` |
| `narrative_integration` | Narativna integracija | `themes`, `output_style` |

## Metode sinteze

### Tematska sinteza

```python
await synthesizer.execute(
    action="thematic",
    findings=extracted_findings,
    theme_level="descriptive",  # "descriptive" ali "analytical"
    approach="inductive"        # "inductive" ali "deductive"
)
```

Output:
```json
{
  "themes": [
    {
      "name": "Autonomy erosion through algorithmic control",
      "description": "Consistent finding that AI monitoring reduces perceived autonomy",
      "supporting_studies": ["Smith2024", "Jones2023", "Lee2022"],
      "subthemes": [
        "Real-time tracking anxiety",
        "Predictive scheduling constraints"
      ],
      "exemplar_quotes": [
        {"study": "Smith2024", "quote": "Workers reported feeling 'watched'..."}
      ]
    }
  ],
  "theme_hierarchy": "Organizational control → Algorithmic control → [subthemes]"
}
```

### Framework sinteza

Za AI v HR uporabi predefiniran framework:

```python
AI_HR_FRAMEWORK = {
    "AI_technology": ["screening", "monitoring", "chatbots", "analytics"],
    "HR_function": ["recruitment", "performance", "learning", "wellbeing"],
    "psychosocial_risk": ["stress", "autonomy", "surveillance", "fairness"],
    "organizational_outcome": ["trust", "culture", "resistance", "efficiency"],
    "moderators": ["transparency", "employee_voice", "training", "culture"]
}
```

```python
await synthesizer.execute(
    action="framework",
    findings=extracted_findings,
    framework=AI_HR_FRAMEWORK
)
```

### Realist Synthesis

```python
await synthesizer.execute(
    action="realist",
    findings=extracted_findings,
    cmo_structure=True  # Context-Mechanism-Outcome
)
```

Output:
```json
{
  "cmo_configurations": [
    {
      "context": "Large tech companies with young workforce",
      "mechanism": "Perceived fairness of AI decisions",
      "outcome": "Higher acceptance of AI in recruitment",
      "confidence": "moderate (3 studies)"
    }
  ]
}
```

## System Prompt

```text
You are an expert in qualitative evidence synthesis for scoping reviews.

Your task is to synthesize findings across studies while:
1. Identifying patterns, themes, and relationships
2. Preserving nuance and context
3. Noting areas of agreement and disagreement
4. Maintaining traceability to source studies

For scoping reviews, focus on:
- BREADTH of evidence (what exists?)
- MAPPING concepts to categories
- Identifying GAPS for future research

Do NOT:
- Make causal claims without strong evidence
- Oversimplify complex findings
- Ignore contradictory evidence
- Weight by study quality (scoping review principle)
```

## Narativna integracija

Pretvori teme v tekoče sekcije članka:

```python
await synthesizer.execute(
    action="narrative_integration",
    themes=identified_themes,
    output_style="academic",
    target_section="results",
    word_target=2000
)
```

## Error Handling

| Error | Handling |
|-------|----------|
| Insufficient studies | Note limitation, synthesize available |
| Conflicting findings | Present both, note tension |
| Theme overlap | Merge or hierarchically organize |
| Missing context | Flag, include as "not reported" |

## Quality Gates

| Check | Target | Action |
|-------|--------|--------|
| Theme coverage | ≥80% of studies | Expand themes |
| Source attribution | 100% claims traced | Verify citations |
| Balance | No single study dominates | Diversify |

---

**Python:** `agents/synthesizer.py` | **Verzija:** 2.0.0
