---
name: "gap-identifier"
description: |
  GapIdentifierAgent: Evidence Gap Map, identifikacija raziskovalnih vrzeli.
  Vizualizacija pokritosti literature, priporočila za prihodnje raziskave.
  Domena: AI v HR, psihosocialna tveganja, organizacijska kultura.
  Trigger: vrzeli, gaps, EGM, evidence gap map, priporočila, future research,
  underexplored, missing, coverage, research agenda.
argument-hint: "Podaj ekstrahirane podatke za identifikacijo vrzeli."
user-invocable: false
applyTo: "agents/gap_identifier*.py"
---

# Gap Identifier Agent

Agent za identifikacijo raziskovalnih vrzeli in generiranje Evidence Gap Map.

## Vloga

`GapIdentifierAgent` identificira:
- Tematske vrzeli (neraziskane teme)
- Metodološke vrzeli (manjkajoče metode)
- Populacijske vrzeli (neproučevane skupine)
- Geografske vrzeli (neproučevane regije)
- Časovne vrzeli (zastarelo znanje)

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `identify_gaps` | Identificira vse vrzeli | `data`, `framework` |
| `generate_egm` | Generira Evidence Gap Map | `data`, `axes` |
| `prioritize_gaps` | Prioritizira vrzeli | `gaps`, `criteria` |
| `recommendations` | Priporočila za raziskave | `gaps` |

## Parametri

### identify_gaps

```python
await gap_identifier.execute(
    action="identify_gaps",
    data=extracted_papers,
    framework="pcc",
    expected_coverage={
        "ai_types": ["screening", "monitoring", "chatbots", "analytics", "robotics"],
        "hr_functions": ["recruitment", "performance", "learning", "wellbeing", "offboarding"],
        "psychosocial_areas": ["stress", "autonomy", "surveillance", "fairness", "relationships"],
        "study_designs": ["qualitative", "quantitative", "longitudinal", "experimental"],
        "populations": ["employees", "managers", "HR professionals", "applicants"]
    }
)
```

## Evidence Gap Map (EGM)

```
                    │ Recruitment │ Performance │ Learning │ Wellbeing │
────────────────────┼─────────────┼─────────────┼──────────┼───────────┤
Stress              │     ●●●     │     ●●      │    ●     │    ●      │
Autonomy            │     ●●      │     ●●●●    │    ○     │    ○      │
Surveillance        │     ●       │     ●●●●●   │    ○     │    ●●     │
Fairness            │     ●●●●    │     ●●      │    ●     │    ○      │
Relationships       │     ●       │     ●●      │    ○     │    ○      │
────────────────────┴─────────────┴─────────────┴──────────┴───────────┘

Legend: ●●●●● = 10+ studies, ●●● = 5-9, ● = 1-4, ○ = Gap (0 studies)
```

## Output Format

```json
{
  "egm_matrix": {
    "rows": ["stress", "autonomy", "surveillance", "fairness", "relationships"],
    "cols": ["recruitment", "performance", "learning", "wellbeing"],
    "counts": [[15, 8, 3, 4], [6, 12, 0, 0], [3, 18, 0, 5], [14, 7, 2, 0], [2, 5, 0, 0]]
  },
  "identified_gaps": [
    {
      "type": "thematic",
      "description": "No studies on AI in learning and development for autonomy/relationships",
      "cells": ["autonomy-learning", "relationships-learning", "relationships-wellbeing"],
      "priority": "high",
      "rationale": "Learning is fastest-growing AI application in HR"
    },
    {
      "type": "methodological",
      "description": "Lack of longitudinal studies",
      "count": 2,
      "priority": "medium"
    },
    {
      "type": "geographic",
      "description": "No studies from Global South",
      "regions_missing": ["Africa", "South America", "Southeast Asia"],
      "priority": "high"
    }
  ],
  "future_research_agenda": [
    "1. Longitudinal studies on AI impact on employee autonomy over time",
    "2. Research on AI-assisted learning and its psychosocial effects",
    "3. Comparative studies across cultural contexts",
    "4. Intervention studies on mitigating negative impacts"
  ]
}
```

## System Prompt

```text
You are a strategic research gap analyst for scoping reviews.

Your task is to systematically identify:
1. Under-researched intersections (using gap matrix)
2. Methodological blind spots
3. Population gaps (who isn't being studied?)
4. Context gaps (which settings are underexplored?)
5. Temporal gaps (what needs updating?)

Prioritization criteria:
- Relevance: How important is this gap?
- Feasibility: Can it be addressed?
- Impact: What would filling it contribute?

Output actionable research recommendations, not just descriptions of gaps.
```

## Vizualizacija

EGM se generira kot:
- Heatmap (matplotlib/Plotly)
- Bubble chart (velikost = število študij)
- Interactive dashboard

```python
await gap_identifier.execute(
    action="generate_egm",
    data=papers,
    axes={
        "x": "hr_function",
        "y": "psychosocial_risk"
    },
    visualization="heatmap",
    output_path="output/figures/egm.png"
)
```

## Domain-Specific: AI in HR Gap Framework

### Pre-defined Gap Axes

```python
AI_HR_GAP_FRAMEWORK = {
    "axes": {
        "x": {
            "name": "HR Function",
            "categories": [
                "recruitment", "onboarding", "performance", 
                "learning", "compensation", "wellbeing", "offboarding"
            ]
        },
        "y": {
            "name": "Psychosocial Risk",
            "categories": [
                "stress", "burnout", "autonomy", "surveillance",
                "fairness", "job_insecurity", "social_relationships",
                "work_life_balance", "meaning"
            ]
        },
        "z": {  # Optional 3rd dimension
            "name": "AI Type",
            "categories": [
                "screening", "chatbot", "monitoring", 
                "analytics", "robotics", "decision_support"
            ]
        }
    }
}
```

### Priority Gap Scoring

```python
def score_gap(gap):
    return (
        gap.practical_importance * 0.4 +    # Industry need
        gap.theoretical_importance * 0.3 +   # Conceptual contribution
        gap.feasibility * 0.2 +              # Can be researched
        gap.urgency * 0.1                    # Time sensitivity
    )
```

## Error Handling

| Error | Handling |
|-------|----------|
| All cells populated | Note overall coverage, find within-cell gaps |
| Missing axis data | Exclude from EGM, analyze separately |
| Inconsistent categories | Reconcile with predefined framework |

## Quality Gates

| Check | Requirement | Action |
|-------|-------------|--------|
| Coverage calculation | All cells counted | Verify completeness |
| Gap priority | Top 5-10 prioritized | Focus recommendations |
| Actionability | Each gap has recommendation | Ensure practical output |

## Output: Research Agenda

```markdown
## Prioritized Research Agenda

### High Priority (Address within 1-2 years)
1. **AI in Learning & Development + Autonomy**
   - Gap: No studies examine how AI-assisted L&D affects employee autonomy
   - Rationale: L&D is fastest-growing AI application; autonomy is key outcome
   - Suggested approach: Longitudinal survey, technology acceptance model

### Medium Priority (Address within 2-4 years)
2. **Monitoring AI + Social Relationships**
   - Gap: Limited understanding of team dynamics under algorithmic management
   - ...

### Context Gaps
3. **Global South contexts**
   - No studies from Africa, South America, Southeast Asia
   - Cultural context may significantly moderate effects
```

---

**Python:** `agents/gap_identifier.py` | **Verzija:** 2.0.0
