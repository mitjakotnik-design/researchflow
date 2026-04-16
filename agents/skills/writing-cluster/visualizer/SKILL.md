---
name: "visualizer"
description: |
  VisualizerAgent: PRISMA diagram, Evidence Gap Map, grafikoni.
  Plotly interaktivno, matplotlib statično, export za publikacije.
  Trigger: diagram, graf, vizualizacija, PRISMA, EGM, heatmap, chart.
argument-hint: "Vrsta vizualizacije in podatki."
user-invocable: false
applyTo: "agents/visualizer*.py"
---

# Visualizer Agent

Agent za generiranje vizualizacij za znanstvene članke.

## Vloga

`VisualizerAgent` generira:
- PRISMA flow diagram
- Evidence Gap Map (heatmap)
- Tematske grafikone
- Časovne trende
- Publikacijski grafikoni

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `generate` | Generiraj vizualizacijo | `type`, `data`, `style` |
| `prisma` | PRISMA 2020 diagram | `flow_data` |
| `egm` | Evidence Gap Map | `matrix`, `axes` |
| `chart` | Splošni grafikon | `data`, `chart_type` |

## PRISMA 2020 Flow Diagram

```python
await visualizer.execute(
    action="prisma",
    flow_data={
        "identification": {
            "databases": 1847,
            "other_sources": 23
        },
        "screening": {
            "duplicates_removed": 412,
            "title_abstract_screened": 1458,
            "title_abstract_excluded": 1102
        },
        "eligibility": {
            "full_text_assessed": 356,
            "excluded_with_reasons": {
                "wrong_population": 45,
                "wrong_concept": 89,
                "wrong_study_type": 67,
                "no_full_text": 23,
                "other": 15
            }
        },
        "included": {
            "final_count": 117,
            "quantitative": 68,
            "qualitative": 42,
            "mixed": 7
        }
    },
    output_format="svg",  # "svg", "png", "pdf"
    style="prisma_2020"
)
```

## Evidence Gap Map

```python
await visualizer.execute(
    action="egm",
    matrix={
        "rows": ["stress", "autonomy", "surveillance", "fairness"],
        "cols": ["recruitment", "performance", "learning", "wellbeing"],
        "values": [
            [15, 8, 3, 4],
            [6, 12, 0, 0],
            [3, 18, 0, 5],
            [14, 7, 2, 0]
        ]
    },
    axes={
        "x_label": "HR Function",
        "y_label": "Psychosocial Risk"
    },
    style={
        "colormap": "YlOrRd",
        "annotate": True,
        "highlight_gaps": True,  # Highlight cells with 0
        "figsize": (10, 8)
    },
    output_path="figures/egm.png"
)
```

## Grafikoni za članek

### Bar Chart - Studies by Year

```python
await visualizer.execute(
    action="chart",
    chart_type="bar",
    data={
        "x": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
        "y": [2, 5, 8, 15, 23, 42, 22]
    },
    labels={
        "x": "Publication Year",
        "y": "Number of Studies"
    },
    style="publication",  # Clean, B&W friendly
    output_path="figures/studies_by_year.png"
)
```

### Sankey Diagram - AI Type → HR Function → Risk

```python
await visualizer.execute(
    action="chart",
    chart_type="sankey",
    data={
        "nodes": ["Screening", "Monitoring", "Chatbots", 
                  "Recruitment", "Performance", 
                  "Stress", "Autonomy", "Surveillance"],
        "links": [
            {"source": 0, "target": 3, "value": 25},
            {"source": 1, "target": 4, "value": 30},
            ...
        ]
    },
    output_format="html"  # Interactive
)
```

## Slog za publikacijo

```python
PUBLICATION_STYLE = {
    "font_family": "Arial",
    "font_size": 12,
    "title_size": 14,
    "dpi": 300,
    "figsize": (8, 6),
    "colormap": "viridis",  # Colorblind friendly
    "grid": True,
    "spine": False,
    "legend_loc": "upper right"
}
```

## System Prompt

```text
You are an expert scientific visualization specialist.

Requirements:
1. Generate publication-ready figures (300 DPI)
2. Use colorblind-friendly palettes
3. Include clear labels and legends
4. Follow APA figure formatting guidelines
5. Export in multiple formats (PNG, SVG, PDF)

For PRISMA diagrams:
- Follow PRISMA 2020 template exactly
- Include all required boxes and arrows
- Use consistent fonts and sizes

For Evidence Gap Maps:
- Use heatmap with clear intensity scale
- Annotate cell counts
- Highlight gaps (zero cells)
```

## Output Format

```json
{
  "figure_path": "figures/prisma_flow.svg",
  "dimensions": {"width": 800, "height": 1000},
  "format": "svg",
  "alt_text": "PRISMA flow diagram showing 1847 records identified...",
  "caption": "Figure 1. PRISMA flow diagram of the study selection process."
}
```

## Error Handling

| Error | Handling |
|-------|----------|
| Invalid data | Validate, request correction |
| Missing values | Fill with 0 or exclude |
| File conflict | Increment filename |
| Memory limit | Reduce resolution/size |

## Quality Gates

| Check | Target | Action |
|-------|--------|--------|
| Resolution | ≥300 DPI | Upscale |
| Color accessibility | WCAG AA | Use accessible palette |
| File size | <5MB | Compress |

---

**Python:** `agents/visualizer.py` | **Verzija:** 2.0.0
