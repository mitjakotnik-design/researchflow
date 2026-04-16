---
name: "quality-cluster"
description: |
  Quality cluster za scoping review: evalvacija, preverjanje dejstev,
  konsistentnost, bias detekcija, kritika, metodološka validacija.
  Trigger: kvaliteta, quality, preveri, check, evalvacija, evaluate,
  bias, konsistentnost, dejstva, facts, metodologija, PRISMA.
argument-hint: "Kaj želiš preveriti ali evalvirati?"
user-invocable: true
applyTo: "agents/**"
tools:
  - read_file
  - semantic_search
  - grep_search
model: gemini-2.5-pro
---

# Quality Cluster

Entry point za vse agente za zagotavljanje kakovosti v ResearchFlow.

## Pregled

Quality cluster vsebuje 6 specializiranih agentov:

| Agent | Python razred | Namen |
|-------|---------------|-------|
| **Multi Evaluator** | `MultiEvaluatorAgent` | Večdimenzionalna evalvacija |
| **Fact Checker** | `FactCheckerAgent` | Preverjanje trditev |
| **Consistency Checker** | `ConsistencyCheckerAgent` | Interna konsistentnost |
| **Bias Auditor** | `BiasAuditorAgent` | Detekcija pristranskosti |
| **Critic** | `CriticAgent` | Konstruktivna kritika |
| **Methodology Validator** | `MethodologyValidatorAgent` | PRISMA-ScR compliance |

## Routing

| Uporabnikova potreba | Agent | Akcija | Naloži |
|---------------------|-------|--------|--------|
| "Oceni kakovost" | multi_evaluator | `evaluate` | [multi-evaluator/SKILL.md](multi-evaluator/SKILL.md) |
| "Preveri dejstva" | fact_checker | `check` | [fact-checker/SKILL.md](fact-checker/SKILL.md) |
| "Preveri konsistentnost" | consistency_checker | `check` | [consistency-checker/SKILL.md](consistency-checker/SKILL.md) |
| "Preveri bias" | bias_auditor | `audit` | [bias-auditor/SKILL.md](bias-auditor/SKILL.md) |
| "Kritično oceni" | critic | `critique` | [critic/SKILL.md](critic/SKILL.md) |
| "Preveri PRISMA" | methodology_validator | `validate` | [methodology-validator/SKILL.md](methodology-validator/SKILL.md) |

## Quality Dimensions

| Dimenzija | Meritev | Prag |
|-----------|---------|------|
| Accuracy | Fact verification rate | ≥95% |
| Coherence | Logical flow score | ≥80/100 |
| Completeness | Section coverage | 100% |
| Consistency | Terminology match | ≥95% |
| Citation validity | DOI verification | ≥90% |
| PRISMA compliance | Checklist items | ≥95% |

## Quality Gates Workflow

```
[Writer] → draft
    ↓
[Parallel Quality Checks]
    ├── MultiEvaluator → quality score
    ├── FactChecker → claim verification
    ├── ConsistencyChecker → internal consistency
    └── BiasAuditor → bias flags
    ↓
[Aggregate Results]
    ↓
ALL PASS? ──Yes──→ [Proceed to next phase]
    │
    No
    ↓
[Critic] → constructive feedback
    ↓
[Writer] → revision
    ↓
[Loop until pass or max iterations]
```

## Parallel Execution

Quality checks tečejo paralelno:

```python
quality_results = await asyncio.gather(
    evaluator.execute(action="evaluate", text=draft),
    fact_checker.execute(action="check", claims=extract_claims(draft)),
    consistency.execute(action="check", text=draft),
    bias_auditor.execute(action="audit", text=draft),
    return_exceptions=True
)

aggregated = aggregate_quality(quality_results)
if aggregated.overall_score < threshold:
    feedback = await critic.execute(
        action="critique",
        text=draft,
        quality_results=aggregated
    )
    draft = await writer.execute(action="revise", feedback=feedback)
```

## Quality Score Calculation

```python
def calculate_overall_score(results):
    weights = {
        "accuracy": 0.25,
        "coherence": 0.20,
        "completeness": 0.15,
        "consistency": 0.15,
        "citation_validity": 0.15,
        "bias_free": 0.10
    }
    return sum(results[dim] * weight for dim, weight in weights.items())
```

## Error Handling

| Error | Handling |
|-------|----------|
| Checker timeout | Use cached result, flag |
| Conflicting results | Human review required |
| Below threshold | Block publication, iterate |

## Human-in-the-Loop

| Trigger | Action |
|---------|--------|
| Score < 60 | Mandatory human review |
| Fact check fail | Human verification required |
| Bias detected | Human assessment required |
| 3+ iterations | Human intervention |

## Konfiguracija

```python
QUALITY_CONFIG = {
    "thresholds": {
        "publish_ready": 85,
        "needs_revision": 70,
        "major_issues": 60
    },
    "max_iterations": 5,
    "parallel_checks": True,
    "human_review_trigger": 60
}
```

## Integracija z obstoječimi skills

| Generični skill | Uporaba |
|-----------------|---------|
| `.github/skills/review-article/` | Quality kriteriji za preglede |
| `.github/skills/research-methodology/` | Metodološki standardi |

---

**Verzija:** 2.0.0 | **Zadnja posodobitev:** 2026-04-16
