---
name: "methodology-validator"
description: |
  MethodologyValidatorAgent: PRISMA-ScR compliance, JBI metodologija.
  Preverjanje skladnosti z metodološkimi standardi.
  Trigger: PRISMA, metodologija, methodology, compliance, JBI, checklist.
argument-hint: "Podaj tekst za preverjanje PRISMA-ScR compliance."
user-invocable: false
applyTo: "agents/methodology_validator*.py"
---

# Methodology Validator Agent

Agent za preverjanje skladnosti z metodološkimi standardi.

## Vloga

`MethodologyValidatorAgent` preverja:
- PRISMA-ScR checklist (22 items)
- JBI scoping review metodologijo
- Arksey & O'Malley framework
- Levac et al. enhancements

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `validate` | Celotna validacija | `text`, `checklist` |
| `check_prisma` | PRISMA-ScR | `text` |
| `check_jbi` | JBI framework | `text` |
| `generate_checklist` | Generiraj izpolnjen checklist | `text` |

## PRISMA-ScR Checklist (22 items)

### Title (1 item)
| # | Item | Requirement |
|---|------|-------------|
| 1 | Title | Identify report as scoping review |

### Abstract (1 item)
| # | Item | Requirement |
|---|------|-------------|
| 2 | Structured summary | Background, objectives, eligibility, sources, charting, results, conclusions |

### Introduction (2 items)
| # | Item | Requirement |
|---|------|-------------|
| 3 | Rationale | Describe rationale, what scoping review will add |
| 4 | Objectives | State objectives/questions with PCC elements |

### Methods (9 items)
| # | Item | Requirement |
|---|------|-------------|
| 5 | Protocol | State if protocol exists, access info |
| 6 | Eligibility | Inclusion/exclusion criteria with rationale |
| 7 | Information sources | All sources, date of last search |
| 8 | Search | Full search strategy for at least one database |
| 9 | Selection of sources | Selection process, reviewers, software |
| 10 | Data charting | Charting variables, process, pilot status |
| 11 | Data items | All variables charted |
| 12 | Critical appraisal | If done, methods used (optional for scoping) |
| 13 | Synthesis | How results were collated and summarized |

### Results (3 items)
| # | Item | Requirement |
|---|------|-------------|
| 14 | Selection | Results of search, selection (PRISMA flow) |
| 15 | Characteristics | Extent, nature, distribution of evidence |
| 16 | Results | Synthesis results, relate to questions |

### Discussion (4 items)
| # | Item | Requirement |
|---|------|-------------|
| 17 | Summary | Main findings, relate to objectives |
| 18 | Limitations | Limitations of evidence and process |
| 19 | Conclusions | Interpretation, implications |
| 20 | Funding | Describe funding sources and roles |

### Other (2 items)
| # | Item | Requirement |
|---|------|-------------|
| 21 | Registration | Registration number if applicable |
| 22 | Availability | Statement about data/material availability |

## Validation Process

```python
await validator.execute(
    action="validate",
    text=full_manuscript,
    checklist="prisma_scr"
)
```

## Output Format

```json
{
  "checklist": "PRISMA-ScR",
  "total_items": 22,
  "complete": 19,
  "partial": 2,
  "missing": 1,
  "compliance_rate": 86.4,
  "details": [
    {
      "item": 1,
      "name": "Title",
      "status": "COMPLETE",
      "evidence": "Title contains 'scoping review'",
      "location": "Title page"
    },
    {
      "item": 8,
      "name": "Search",
      "status": "PARTIAL",
      "evidence": "Full strategy for PubMed provided",
      "missing": "Complete strategies for Scopus, WoS not shown",
      "location": "Methods, p. 5",
      "suggestion": "Add full search strings for all databases or reference supplementary material"
    },
    {
      "item": 21,
      "name": "Registration",
      "status": "MISSING",
      "suggestion": "Add statement: 'Protocol registered on OSF/PROSPERO (registration number)' or 'No protocol was registered'"
    }
  ],
  "overall_assessment": "Near complete compliance. Address 3 items for full compliance."
}
```

## JBI Framework Validation

Arksey & O'Malley + Levac enhancements:

| Stage | Check |
|-------|-------|
| 1. Research question | Clear, PCC format |
| 2. Identifying studies | Comprehensive strategy |
| 3. Study selection | Two reviewers, criteria |
| 4. Charting data | Standardized form |
| 5. Collating results | Narrative + numerical |
| 6. Consultation | Stakeholder input (optional) |

## System Prompt

```text
You are an expert in scoping review methodology.

Validate against:
1. PRISMA-ScR extension (2018) - 22 items
2. JBI scoping review manual (2020)
3. Arksey & O'Malley (2005) framework
4. Levac et al. (2010) enhancements

For each checklist item:
- Locate evidence in manuscript
- Rate: COMPLETE / PARTIAL / MISSING
- Provide specific location
- Suggest how to address gaps

Be precise:
- Quote relevant sections
- Note page/paragraph numbers
- Distinguish must-have from nice-to-have
```

## Auto-fixes

```python
# Generate missing sections
await validator.execute(
    action="generate_missing",
    text=manuscript,
    missing_items=["registration_statement", "data_availability"]
)
```

Output:
```json
{
  "generated": {
    "registration_statement": "This review was not registered. The protocol was developed iteratively during the review process.",
    "data_availability": "All data generated during this review are available within the article and supplementary materials. The charting data extraction form is available from the corresponding author upon request."
  }
}
```

## Error Handling

| Error | Handling |
|-------|----------|
| Section not found | Mark as missing, note |
| Partial compliance | Specify what's missing |
| Ambiguous compliance | Mark partial, explain |

## Quality Gates

| Check | Threshold | Action |
|-------|-----------|--------|
| Total compliance | ≥90% | Pass |
| Critical items (1-4) | 100% | Must complete |
| Methods items (5-13) | ≥90% | Must address |

---

**Python:** `agents/methodology_validator.py` | **Verzija:** 2.0.0
