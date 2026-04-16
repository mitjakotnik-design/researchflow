---
name: "citation-manager"
description: |
  CitationManagerAgent: Citiranje in reference, APA 7, Vancouver.
  Formatiranje, preverjanje, generiranje seznama literature.
  Trigger: citiranje, citation, reference, APA, Vancouver, DOI, bibliography.
argument-hint: "Podaj tekst s citati ali seznam referenc."
user-invocable: false
applyTo: "agents/citation_manager*.py"
---

# Citation Manager Agent

Agent za upravljanje citatov in referenc.

## Vloga

`CitationManagerAgent` upravlja:
- In-text citiranje (APA 7, Vancouver)
- Formatiranje seznama referenc
- Preverjanje DOI in metapodatkov
- Konsistentnost citiranja

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `format` | Formatiraj citate | `text`, `style` |
| `generate_bibliography` | Generiraj seznam | `citations`, `style` |
| `verify` | Preveri citate | `citations` |
| `convert_style` | Pretvori slog | `text`, `from_style`, `to_style` |

## Formati

### APA 7

**In-text:**
- Enostavni avtor: (Smith, 2024)
- Dva avtorja: (Smith & Jones, 2024)
- Trije+: (Smith et al., 2024)
- Direktni citat: (Smith, 2024, p. 15)
- Več virov: (Jones, 2023; Smith, 2024)

**Reference:**
```
Smith, J. A., & Jones, B. C. (2024). Algorithmic management in modern 
    workplaces: A systematic review. Journal of Organizational Behavior, 
    45(3), 234-256. https://doi.org/10.1002/job.2456
```

### Vancouver

**In-text:**
- Številčno: [1], [1,2], [1-3]

**Reference:**
```
1. Smith JA, Jones BC. Algorithmic management in modern workplaces: 
   A systematic review. J Organ Behav. 2024;45(3):234-56. 
   doi: 10.1002/job.2456
```

## Akcija: Format

```python
await citation_manager.execute(
    action="format",
    text=article_text,
    style="apa7",
    verify_dois=True
)
```

Output:
```json
{
  "formatted_text": "...",
  "citations_processed": 47,
  "issues": [
    {
      "citation": "(Smith 2024)",
      "issue": "Missing comma after author",
      "corrected": "(Smith, 2024)"
    }
  ],
  "doi_verification": {
    "verified": 45,
    "not_found": 2,
    "errors": ["Smith2018 - DOI not resolving"]
  }
}
```

## Akcija: Generate Bibliography

```python
await citation_manager.execute(
    action="generate_bibliography",
    citations=extracted_citations,
    style="apa7",
    order="alphabetical",  # ali "appearance"
    include_doi=True,
    include_access_date=False
)
```

## System Prompt

```text
You are an expert bibliographic citation manager.

Your tasks:
1. Format in-text citations according to style guide
2. Generate reference lists with perfect formatting
3. Verify DOIs and correct metadata errors
4. Ensure consistency throughout the manuscript

APA 7 specifics:
- Use "&" in parenthetical, "and" in narrative
- et al. for 3+ authors
- Include DOI as hyperlink when available
- Italicize journal names and volume numbers
- Hanging indent for references

Common errors to fix:
- Missing commas, periods
- Incorrect capitalization
- Inconsistent author name formats
- Missing page numbers for direct quotes
```

## DOI Verification

```python
await citation_manager.execute(
    action="verify",
    citations=references,
    check_doi=True,
    check_metadata=True,
    auto_correct=True
)
```

Output:
```json
{
  "verified": 45,
  "corrections": [
    {
      "original_year": "2023",
      "correct_year": "2024",
      "source": "CrossRef API"
    }
  ],
  "unverifiable": 2
}
```

## Error Handling

| Error | Handling |
|-------|----------|
| Invalid DOI | Flag, attempt title search |
| Missing metadata | Flag, request from user |
| Style mismatch | Auto-convert |
| Duplicate citation | Merge, use consistent key |

## Quality Gates

| Check | Target | Action |
|-------|--------|--------|
| Citation format | 100% compliant | Auto-correct |
| DOI validity | ≥95% | Verify remaining |
| Reference completeness | 100% | Request missing |

---

**Python:** `agents/citation_manager.py` | **Verzija:** 2.0.0
