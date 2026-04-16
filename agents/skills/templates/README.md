# ResearchFlow Templates

Standardizirane predloge za scoping review po PRISMA-ScR in JBI metodologiji.

## 📋 Predloge

| Predloga | Namen | PRISMA-ScR Item |
|----------|-------|-----------------|
| [data-charting-form.md](data-charting-form.md) | Ekstrakcija podatkov iz člankov | 10, 11 |
| [search-documentation.md](search-documentation.md) | Dokumentiranje iskalne strategije | 7, 8 |
| [screening-form.md](screening-form.md) | Title/Abstract in Full-text screening | 9, 14 |
| [prisma-scr-checklist.md](prisma-scr-checklist.md) | PRISMA-ScR skladnost (22 items) | Vsi |
| [study-characteristics-summary.md](study-characteristics-summary.md) | Sumarne tabele karakteristik | 15, 16, 17 |
| [conflict-resolution-form.md](conflict-resolution-form.md) | Razreševanje nesoglasij | 9 |

## 📊 JSON Sheme

| Shema | Namen |
|-------|-------|
| [schemas/data-charting-schema.json](schemas/data-charting-schema.json) | Validacija ekstrakcije |

## 🔧 Python skripte

| Skripta | Namen | Uporaba |
|---------|-------|---------|
| [scripts/irr_calculator.py](scripts/irr_calculator.py) | Cohen's Kappa | `python irr_calculator.py --r1 "1,1,0" --r2 "1,0,0"` |
| [scripts/prisma_generator.py](scripts/prisma_generator.py) | PRISMA diagram | `python prisma_generator.py --format mermaid` |

## 🎯 Uporaba

### 1. Pred začetkom iskanja
```bash
# 1. Izpolni search-documentation.md z iskalnimi nizi
# 2. Pripravi screening-form.md s kriteriji vključitve/izključitve
# 3. Izvedi pilot screening (20-50 zapisov)

# Preveri inter-rater reliability:
python scripts/irr_calculator.py --file pilot_screening.csv
```

### 2. Med ekstrakcijo
```bash
# 1. Kopiraj data-charting-form.md za vsak vključen članek
# 2. Dvoje neodvisno ekstrahirata
# 3. Preveri Kappa po prvih 10% (target: ≥0.8)

# Validiraj JSON ekstrakcije:
python -c "import json, jsonschema; ..."
```

### 3. Pred oddajo
```bash
# Generiraj PRISMA diagram:
python scripts/prisma_generator.py --format mermaid --output prisma.md

# Izpolni prisma-scr-checklist.md
# Pripravi study-characteristics-summary.md
```

## 📊 Domain-Specific: AI v HR

Predloge so prilagojene za temo:
> **"Psychosocial Risks and Organizational Culture Implications of AI Implementation Through HR Functions"**

Specifični elementi:
- AI tipi (RS, VI, CB, MN, AN, RB, DS)
- HR funkcije (REC, ONB, PER, L&D, COM, WEL, OFF)
- Psihosocialni konstrukti (STR, BRN, AUT, SUR, FAI, JOB, SOC, WLB, MEA)

## 🔄 Integracija z agenti

| Agent | Uporabljena predloga |
|-------|---------------------|
| `data_extractor` | data-charting-form.md |
| `literature_scout` | search-documentation.md |
| `methodology_validator` | prisma-scr-checklist.md |
| `visualizer` | study-characteristics-summary.md |

## 📚 Reference

- PRISMA-ScR: [doi:10.7326/M18-0850](https://doi.org/10.7326/M18-0850)
- JBI Scoping Review Manual: [doi:10.1097/XEB.0000000000000050](https://doi.org/10.1097/XEB.0000000000000050)

---

**Verzija:** 1.0.0 | **Datum:** 2026-04-16
