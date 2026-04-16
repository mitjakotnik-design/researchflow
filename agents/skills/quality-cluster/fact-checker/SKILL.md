---
name: "fact-checker"
description: |
  FactCheckerAgent: Preverjanje trditev proti virom in RAG.
  Verificira statistike, citate, dejstva.
  Trigger: preveri, verify, fact check, trditev, claim, statistika.
argument-hint: "Podaj trditve ali tekst za preverjanje."
user-invocable: false
applyTo: "agents/fact_checker*.py"
---

# Fact Checker Agent

Agent za preverjanje točnosti trditev v članku.

## Vloga

`FactCheckerAgent` preverja:
- Trditve proti citiranim virom
- Statistične podatke
- Metodološke trditve
- Definicije in terminologijo

## Akcije

| Akcija | Opis | Parametri |
|--------|------|-----------|
| `check` | Preveri trditve | `text`, `claims`, `sources` |
| `extract_claims` | Izvleci trditve | `text` |
| `verify_statistics` | Preveri statistike | `statistics` |
| `verify_citations` | Preveri citate | `citations` |

## Tip trditev

| Tip | Primer | Preverjanje |
|-----|--------|-------------|
| Factual | "AI adoption grew 50% in 2023" | CrossRef, izvirni vir |
| Statistical | "N=234, p<0.05" | Izvirna študija |
| Quoted | "According to Smith..." | Dobesedna primerjava |
| Interpretive | "This suggests that..." | Logična konsistentnost |

## Proces

```python
# 1. Izvleci trditve
claims = await fact_checker.execute(
    action="extract_claims",
    text=manuscript_text
)

# 2. Preveri vsako trditev
for claim in claims:
    result = await fact_checker.execute(
        action="check",
        claim=claim,
        source_ids=claim.cited_sources,
        rag_context=await query_rag(claim.text)
    )
```

## Output Format

```json
{
  "total_claims": 87,
  "verified": 82,
  "unverified": 3,
  "errors": 2,
  "verification_results": [
    {
      "claim": "AI-based hiring tools reduced time-to-hire by 40%",
      "location": "Results, paragraph 3",
      "citation": "Smith et al., 2024",
      "status": "VERIFIED",
      "source_says": "Implementation resulted in 38-42% reduction in time-to-hire",
      "confidence": 0.95
    },
    {
      "claim": "Most employees prefer AI-free performance reviews",
      "location": "Discussion, paragraph 2",
      "citation": "None",
      "status": "UNVERIFIED",
      "issue": "No citation provided for claim",
      "suggestion": "Add citation or rephrase as hypothesis"
    },
    {
      "claim": "The study included 500 participants",
      "location": "Methods, paragraph 4",
      "citation": "Self-reference",
      "status": "ERROR",
      "issue": "Methods section states N=450, inconsistent",
      "severity": "HIGH"
    }
  ]
}
```

## Nivoji resnosti

| Nivo | Opis | Akcija |
|------|------|--------|
| INFO | Manjše neskladje | Log, nadaljuj |
| LOW | Manjkajoč vir | Zahtevaj citat |
| MEDIUM | Netočna interpretacija | Zahtevaj popravek |
| HIGH | Napačen podatek | Blokiraj, zahtevaj popravek |
| CRITICAL | Potencialno zavajanje | Blokiraj, človeški pregled |

## System Prompt

```text
You are a rigorous academic fact-checker.

Your task is to verify:
1. Every factual claim has a valid source
2. Statistics match their cited sources exactly
3. Quotes are accurate and in context
4. Interpretations are supported by evidence

Verification process:
1. Extract the claim
2. Identify the cited source
3. Locate the claim in the source
4. Compare for accuracy
5. Flag any discrepancies

Be conservative:
- If uncertain, mark as "requires verification"
- Note context-dependent claims
- Flag potential misinterpretations

Output must include:
- Exact claim text
- Location in manuscript
- Source reference
- Verification status
- Evidence or issue description
```

## RAG Integration

```python
async def verify_with_rag(claim, cited_source_id):
    # Query RAG for source content
    source_content = await self.query_rag(
        query=f"Source {cited_source_id}: {claim.subject}",
        filters={"source_id": cited_source_id}
    )
    
    # Compare claim to source
    verification = await self._compare_claim_to_source(
        claim=claim.text,
        source=source_content
    )
    
    return verification
```

## Error Handling

| Error | Handling |
|-------|----------|
| Source not in RAG | Flag, check external |
| Ambiguous claim | Extract clearer formulation |
| Multiple sources | Verify against primary |

## Quality Gates

| Check | Threshold | Action |
|-------|-----------|--------|
| Verification rate | ≥95% | Pass |
| Errors | 0 | Must resolve |
| Unverified claims | <5% | Request citations |

---

**Python:** `agents/fact_checker.py` | **Verzija:** 2.0.0
