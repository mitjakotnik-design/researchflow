---
name: "research-cluster"
description: |
  Research cluster za scoping review: RAG poizvedbe, iskanje literature, 
  ekstrakcija podatkov, meta-analiza, identifikacija vrzeli.
  Trigger: raziskava, literatura, iskanje, RAG, poizvedba, viri, baze, 
  PubMed, Scopus, WoS, ekstrakcija, snowballing, gaps, charting, Boolean,
  MeSH, search string, evidence gap map, EGM, trend, frekvence.
argument-hint: "Kaj želiš raziskati? Podaj temo ali raziskovalno vprašanje."
user-invocable: true
applyTo: "agents/**"
tools:
  - read_file
  - semantic_search
  - grep_search
  - run_in_terminal
model: gemini-2.5-pro
---

# Research Cluster

Entry point za vse raziskovalne agente v ResearchFlow sistemu.

## Pregled

Research cluster vsebuje 5 specializiranih agentov za fazo raziskovanja:

| Agent | Python razred | Namen |
|-------|---------------|-------|
| **Researcher** | `ResearcherAgent` | Glavni koordinator RAG poizvedb |
| **Literature Scout** | `LiteratureScoutAgent` | Odkrivanje virov po bazah |
| **Data Extractor** | `DataExtractorAgent` | Strukturirana ekstrakcija |
| **Meta Analyst** | `MetaAnalystAgent` | Kvantitativna analiza |
| **Gap Identifier** | `GapIdentifierAgent` | Evidence Gap Map |

## Routing

Glede na uporabnikovo potrebo izberi ustreznega agenta:

| Uporabnikova potreba | Agent | Akcija | Naloži |
|---------------------|-------|--------|--------|
| "Poišči literaturo o X" | researcher | `research` | [researcher/SKILL.md](researcher/SKILL.md) |
| "Generiraj iskalne nize" | literature_scout | `generate_search_strings` | [literature-scout/SKILL.md](literature-scout/SKILL.md) |
| "Izvleci podatke iz člankov" | data_extractor | `extract` | [data-extractor/SKILL.md](data-extractor/SKILL.md) |
| "Analiziraj učinke" | meta_analyst | `analyze` | [meta-analyst/SKILL.md](meta-analyst/SKILL.md) |
| "Poišči vrzeli" | gap_identifier | `identify_gaps` | [gap-identifier/SKILL.md](gap-identifier/SKILL.md) |

## Skupni koncepti

### RAG Pipeline

Vsi research agenti uporabljajo skupen RAG sistem:

```python
# Poizvedba
results = await agent.query_rag(
    query="...",
    top_k=15,
    filters={"year_min": 2020}
)
```

Komponente:
- **HybridSearch**: Semantic + BM25 iskanje
- **CohereReranker**: Reranking rezultatov
- **QueryDecomposer**: Razčlenitev kompleksnih poizvedb

### Caching

Research rezultati se cachirajo v `state.research_cache`:

```python
state.research_cache.add_query_result(query, results)
cached = state.research_cache.get_results(query)
```

### Metrike

Vsak agent beleži:
- `queries_executed`: Število poizvedb
- `documents_retrieved`: Število najdenih dokumentov
- `cache_hits`: Število zadetkov v cache

## Workflow

Tipičen raziskovalni workflow:

```
1. [Literature Scout] → Generira iskalne nize (WoS, Scopus, PubMed)
2. [Researcher] → RAG poizvedbe po lokalnih dokumentih
3. [Data Extractor] → Strukturirana ekstrakcija v tabele
4. [Meta Analyst] → Kvantitativna analiza (če primerno)
5. [Gap Identifier] → Evidence Gap Map
```

## Konfiguracija

Nastavitve v `config/models_config.py`:

```python
RESEARCH_AGENTS = {
    "researcher": {
        "model": "gemini-2.5-pro",
        "temperature": 0.3,
        "max_tokens": 8192
    },
    "literature_scout": {
        "model": "gemini-2.5-flash",
        "temperature": 0.2
    }
}
```

## Primer uporabe

```python
from agents import ResearcherAgent

researcher = ResearcherAgent()
researcher.initialize(context)

result = await researcher.execute(
    action="research",
    section="introduction",
    research_questions=[
        "What are psychosocial risks of AI in HR?",
        "How does algorithmic management affect employee wellbeing?"
    ]
)
```

## Integracija z obstoječimi skills

Ta cluster se povezuje z generičnimi metodološkimi skills:

| Generični skill | Uporaba |
|-----------------|---------|
| `.github/skills/review-article/` | Metodologija scoping review |
| `.github/skills/hypothesis-formulation/` | PCC/PICO vprašanja |
| `.github/skills/research-methodology/` | PRISMA-ScR smernice |

## Error Handling

### Pričakovane napake

| Error | Vzrok | Recovery |
|-------|-------|----------|
| `RAGTimeoutError` | Chroma ne odgovarja | Retry 3x z exponential backoff |
| `EmptyResultsError` | Ni zadetkov za query | Razširi iskanje, zmanjšaj filters |
| `RateLimitError` | API limit presežen | Čakaj `retry_after`, circuit breaker |
| `LLMResponseError` | Model timeout/error | Fallback na manjši model |
| `ExtractionError` | Neveljaven dokument | Skip + log, nadaljuj batch |

### Circuit Breaker

```python
# Po 5 zaporednih napakah se aktivira circuit breaker
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout_seconds=60,
    expected_exceptions=[RAGTimeoutError, RateLimitError]
)
```

## Inter-Agent komunikacija

### Protokol

```python
# Pošiljanje sporočila drugemu agentu
await context.send_to_agent(
    target="data_extractor",
    action="extract",
    payload={"documents": rag_results}
)

# Čakanje na odgovor
response = await context.receive_from_agent(
    source="data_extractor",
    timeout=120
)
```

### Message Types

| Tip | Smer | Vsebina |
|-----|------|---------|
| `TASK` | orchestrator → agent | Nova naloga |
| `RESULT` | agent → orchestrator | Rezultat akcije |
| `HANDOFF` | agent → agent | Prenos dela |
| `FEEDBACK` | quality → agent | Zahteva za popravek |

## Quality Gates

Pred nadaljevanjem v naslednji fazi preveri:

| Gate | Minimum | Blokira če |
|------|---------|-----------|
| RAG relevance | 0.7 | Pod 0.5 |
| Extraction confidence | 0.8 | Pod 0.6 |
| Source count | 10 | Pod 5 |
| Cache hit rate | N/A | N/A (info) |

```python
quality_gate = QualityGate(
    name="research_complete",
    checks=[
        Check("min_sources", lambda r: r.source_count >= 10),
        Check("relevance", lambda r: r.avg_relevance >= 0.7)
    ],
    on_fail="pause_for_human"  # ali "retry", "skip"
)
```

## Rate Limiting

### API Limits (Gemini)

| Tier | Requests/min | Tokens/min |
|------|--------------|------------|
| Free | 15 | 32,000 |
| Pay-as-you-go | 360 | 4,000,000 |
| Enterprise | Unlimited | Custom |

### Adaptive Rate Limiter

```python
rate_limiter = AdaptiveRateLimiter(
    base_rpm=60,
    burst_multiplier=1.5,
    backoff_factor=2.0
)
```

## Observability

### Structured Logging

```python
log.info(
    "research_completed",
    agent="researcher",
    section="introduction",
    queries=5,
    documents=28,
    duration_ms=4523,
    cache_hits=2
)
```

### Metrics (Prometheus)

- `research_queries_total{agent, status}`
- `research_documents_retrieved{agent}`
- `research_duration_seconds{agent, action}`
- `research_cache_hit_ratio{agent}`

## Timeouts

| Operacija | Default | Max |
|-----------|---------|-----|
| RAG query | 30s | 60s |
| LLM call | 45s | 120s |
| Batch extraction | 300s | 600s |
| Full research | 600s | 1200s |

```python
@timeout(seconds=120)
async def execute(self, action: str, **kwargs):
    ...
```

## Compatibility

- **Python:** 3.11+
- **Models:** Gemini 2.5 Pro/Flash, GPT-4o (fallback)
- **ChromaDB:** 0.4+
- **Dependencies:** See `requirements.txt`

---

**Verzija:** 2.0.0 | **Zadnja posodobitev:** 2026-04-16
