# Search Documentation Template

Predloga za dokumentiranje iskalne strategije v scoping review.

## 1. Pregled iskalne strategije

| Polje | Vrednost |
|-------|----------|
| **Naslov pregleda** | |
| **Datum zadnje posodobitve** | `[YYYY-MM-DD]` |
| **Informacijski specialist** | `[ime, če je vključen]` |
| **Recenzent iskanja** | |

## 2. Raziskovalna vprašanja

### Primarno vprašanje
```
[Celotno primarno raziskovalno vprašanje]
```

### PCC Framework

| Element | Opis |
|---------|------|
| **Population** | |
| **Concept** | |
| **Context** | |

## 3. Kriteriji vključitve/izključitve

### Vključitveni kriteriji

| Kriterij | Specifike | Utemeljitev |
|----------|-----------|-------------|
| Populacija | | |
| Koncept | | |
| Kontekst | | |
| Tip študije | | |
| Jezik | | |
| Časovno obdobje | | |

### Izključitveni kriteriji

| Kriterij | Specifike | Utemeljitev |
|----------|-----------|-------------|
| | | |
| | | |
| | | |

## 4. Baze podatkov

### Iskane baze

| Baza | Platforma | Datum iskanja | Št. zadetkov |
|------|-----------|---------------|--------------|
| Web of Science | Clarivate | | |
| Scopus | Elsevier | | |
| PubMed | NLM | | |
| PsycINFO | APA/EBSCO | | |
| ERIC | EBSCO | | |
| Business Source | EBSCO | | |

### Dodatni viri

| Vir | Tip | Datum iskanja | Št. zadetkov |
|-----|-----|---------------|--------------|
| Google Scholar | Backward/Forward | | |
| Referenčni seznami | Snowballing | | |
| Grey literature | | | |

## 5. Iskalne strategije po bazah

### 5.1 Web of Science

**Datum iskanja:** `[YYYY-MM-DD]`  
**Časovna omejitev:** `[npr. 2015-2026]`  
**Druge omejitve:** `[jezik, tip dokumenta]`

```
[CELOTNA ISKALNA STRATEGIJA]

Primer:
TS=(("artificial intelligence" OR "machine learning" OR "AI" OR "algorithmic 
management" OR "automated decision*") AND ("human resource*" OR "HR" OR 
"employee*" OR "worker*" OR "workforce") AND ("psychosocial" OR "wellbeing" 
OR "stress" OR "mental health" OR "organizational culture"))

Filters applied:
- Document types: Article, Review, Proceedings Paper
- Languages: English
- Years: 2015-2026
```

**Število zadetkov:** `[N]`

---

### 5.2 Scopus

**Datum iskanja:** `[YYYY-MM-DD]`

```
[CELOTNA ISKALNA STRATEGIJA]

Primer:
TITLE-ABS-KEY(("artificial intelligence" OR "machine learning" OR "AI" OR 
"algorithmic management") AND ("human resource*" OR "HR" OR "employee*") 
AND ("psychosocial" OR "wellbeing" OR "organizational culture"))

Filters:
- Document type: Article, Conference Paper, Review
- Language: English
- Year: 2015-2026
```

**Število zadetkov:** `[N]`

---

### 5.3 PubMed

**Datum iskanja:** `[YYYY-MM-DD]`

```
[CELOTNA ISKALNA STRATEGIJA Z MeSH]

Primer:
("Artificial Intelligence"[MeSH] OR "Machine Learning"[MeSH] OR 
"artificial intelligence"[tiab] OR "algorithmic management"[tiab]) AND 
("Occupational Health"[MeSH] OR "Workplace"[MeSH] OR "human resources"[tiab]) 
AND ("Stress, Psychological"[MeSH] OR "psychosocial"[tiab] OR "wellbeing"[tiab])

Filters:
- Publication date: 2015/01/01 - 2026/12/31
- Species: Humans
- Language: English
```

**Število zadetkov:** `[N]`

---

### 5.4 PsycINFO (EBSCO)

**Datum iskanja:** `[YYYY-MM-DD]`

```
[CELOTNA ISKALNA STRATEGIJA S THESAURUS TERMINI]

Primer:
DE "Artificial Intelligence" OR DE "Machine Learning" OR 
TI ("artificial intelligence" OR "AI" OR "algorithmic management") AND
DE "Human Resource Management" OR DE "Personnel" OR 
TI ("human resource*" OR "HR" OR "employee*") AND
DE "Occupational Stress" OR DE "Work Life Balance" OR 
TI ("psychosocial" OR "wellbeing" OR "stress")

Limiters:
- Publication Year: 2015-2026
- Language: English
- Peer Reviewed: Yes
```

**Število zadetkov:** `[N]`

---

## 6. Grey Literature

### 6.1 Iskani viri

| Vir | URL | Iskalni termini | Zadetki |
|-----|-----|-----------------|---------|
| OECD iLibrary | oecd-ilibrary.org | | |
| ILO Publications | ilo.org/publications | | |
| EU-OSHA | osha.europa.eu | | |
| WHO | who.int | | |
| arXiv | arxiv.org | | |
| SSRN | ssrn.com | | |
| ProQuest Dissertations | proquest.com | | |

### 6.2 Organizacije in poročila

| Organizacija | Tip vira | Št. pregledanih |
|--------------|----------|-----------------|
| | | |

## 7. Snowballing

### Forward Citation

| Seed Paper | Google Scholar "Cited by" | Relevantni zadetki |
|------------|---------------------------|-------------------|
| | | |

### Backward Citation

| Vključena študija | Pregled referenc | Novi zadetki |
|-------------------|------------------|--------------|
| | | |

## 8. Povzetek iskanja

| Metrika | Število |
|---------|---------|
| **Skupaj iz baz** | |
| **Skupaj iz grey lit.** | |
| **Skupaj iz snowballing** | |
| **SKUPAJ PRED DEDUPLIKACIJO** | |
| **Duplikati odstranjeni** | |
| **SKUPAJ ZA SCREENING** | |

## 9. Kontrolni seznam

- [ ] Iskalna strategija preverjena s knjižničarjem/informacijskim specialistom
- [ ] Vse baze dokumentirane s polnimi iskalnimi nizi
- [ ] Grey literatura sistematično iskana
- [ ] Snowballing izvedeno
- [ ] Deduplikacija opravljena
- [ ] Iskanje reprodukibilno dokumentirano

## 10. Spremembe protokola

| Datum | Sprememba | Utemeljitev |
|-------|-----------|-------------|
| | | |

---

**Verzija predloge:** 1.0.0  
**Skladnost:** PRISMA-ScR Item 7, 8
