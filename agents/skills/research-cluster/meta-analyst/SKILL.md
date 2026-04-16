---
name: "meta-analyst"
description: |
  MetaAnalystAgent: Kvantitativna analiza, effect sizes, heterogeneity.
  Za scoping review: deskriptivna statistika, vzorci, trendi.
  Domena: AI v HR, psihosocialna tveganja, organizacijska kultura.
  Trigger: analiza, statistika, vzorci, trendi, frekvence, deskriptivna,
  crosstab, temporal, distribucija, patterns.
argument-hint: "Podaj ekstrahirane podatke za analizo."
user-invocable: false
applyTo: "agents/meta_analyst*.py"
---

# Meta Analyst Agent

Agent za kvantitativno in deskriptivno analizo ekstrahiranih podatkov.

## Vloga

`MetaAnalystAgent` opravlja:
- Deskriptivno statistiko (za scoping review)
- Analizo vzorcev in trendov
- Frekvenčne analize
- Časovne trende
- *Opcijsko:* Meta-analizo effect sizes (za systematic review)

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `analyze` | Celotna analiza | `data`, `analysis_type` |
| `descriptive_stats` | Deskriptivna statistika | `data`, `variables` |
| `trend_analysis` | Časovni trendi | `data`, `time_variable` |
| `pattern_detection` | Vzorci v podatkih | `data`, `grouping_vars` |
| `frequency_analysis` | Frekvence kategorij | `data`, `categorical_vars` |

## Parametri

### analyze (scoping review)

```python
await analyst.execute(
    action="analyze",
    data=extracted_papers,
    analysis_type="scoping",  # "scoping" ali "systematic"
    variables={
        "categorical": ["study_design", "country", "ai_type", "hr_function"],
        "temporal": "year",
        "grouping": ["psychosocial_risk", "organizational_outcome"]
    }
)
```

## Output Format

```json
{
  "descriptive": {
    "total_studies": 47,
    "year_range": "2018-2025",
    "median_year": 2023,
    "countries": {
      "USA": 15,
      "UK": 8,
      "Germany": 6,
      "China": 5,
      "Other": 13
    },
    "study_designs": {
      "qualitative": 18,
      "quantitative": 21,
      "mixed": 6,
      "review": 2
    }
  },
  "patterns": {
    "ai_types_by_hr_function": {
      "recruitment": ["resume screening", "video interviews", "chatbots"],
      "performance_management": ["monitoring software", "productivity tracking"],
      "learning": ["personalized training", "skill assessment"]
    },
    "risk_outcome_associations": [
      {
        "risk": "reduced autonomy",
        "outcomes": ["job dissatisfaction", "turnover intention"],
        "frequency": 12
      }
    ]
  },
  "trends": {
    "publications_by_year": {
      "2018": 2, "2019": 3, "2020": 5, "2021": 7, 
      "2022": 10, "2023": 12, "2024": 8
    },
    "trend": "Increasing interest, peak in 2023"
  }
}
```

## Vizualizacije

Agent generira podatke za vizualizacije:

```python
await analyst.execute(
    action="analyze",
    data=papers,
    generate_charts=True,
    chart_types=["bar", "trend_line", "heatmap", "sankey"]
)
```

Rezultati se posredujejo `VisualizerAgent` za izris.

## System Prompt

```text
You are a quantitative research analyst specializing in scoping reviews.

For SCOPING REVIEWS, focus on:
1. Descriptive statistics (counts, percentages, ranges)
2. Distribution patterns across categories
3. Temporal trends in publication
4. Geographic distribution
5. Conceptual mapping of themes

Do NOT perform:
- Effect size calculations (unless specifically asked)
- Meta-regression
- Publication bias statistics

Present findings in clear tables and suggest appropriate visualizations.
```

## Primeri

### Primer: Analiza AI tipov po HR funkcijah

```python
result = await analyst.execute(
    action="pattern_detection",
    data=papers,
    grouping_vars=["ai_type", "hr_function"],
    output_format="crosstab"
)

# Vrne:
#                  recruitment  performance  learning  wellbeing
# resume_screening      15           0          0          0
# monitoring             2          18          0          5
# chatbots               8           3          5          2
```

## Domain Analysis: AI in HR

### Pre-defined Analyses

```python
# 1. AI type × HR function × Psychosocial risk 3-way crosstab
await analyst.execute(
    action="pattern_detection",
    data=papers,
    analysis="ai_hr_psych_crosstab"
)

# 2. Temporal trend by AI type
await analyst.execute(
    action="trend_analysis",
    data=papers,
    group_by="ai_type",
    time_var="year"
)

# 3. Geographic distribution with GDP context
await analyst.execute(
    action="descriptive_stats",
    data=papers,
    variables=["country"],
    enrich=["gdp_category", "labor_law_type"]
)
```

## Error Handling

| Error | Handling |
|-------|----------|
| Insufficient data (<10) | Warn, provide limited analysis |
| Missing variables | Exclude from that analysis, note |
| Outliers | Flag, include sensitivity analysis |
| Sparse crosstab cells | Collapse categories if logical |

## Quality Gates

| Check | Minimum | Action |
|-------|---------|--------|
| Sample for analysis | ≥10 studies | Warn if fewer |
| Category coverage | ≥3 per major category | Note sparse areas |
| Temporal span | ≥3 years | Limit trend claims |

---

**Python:** `agents/meta_analyst.py` | **Verzija:** 2.0.0
