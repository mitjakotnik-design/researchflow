# 🔬 KRITIČNA ANALIZA: Research Plan Sections & Evaluation Criteria

**Datum:** 16. April 2026  
**Analitik:** ResearchFlow Critic Agent  
**Namen:** Temeljit pregled strukture raziskovalnega načrta pred implementacijo

---

## 📊 PRIMERJAVA SEKCIJ

### Trenutno v RAZISKOVALNI_NACRT_Review.md (11 sekcij)

| # | Sekcija | Status | Ocena Pokritosti |
|---|---------|--------|------------------|
| 1 | **Predlagani Naslov Članka** | ✅ Odlično | 100% - Vključuje slovenski + 3 alternative |
| 2 | **Raziskovalno Vprašanje** | ✅ Odlično | 100% - Glavno + 5 podvprašanj + PCC implicitno |
| 3 | **Teoretični Okvir** | ✅ Izvrstno | 110% - 5 teorij + konceptualni model + diagram |
| 4 | **Metodologija (Scoping Review)** | ✅ Dobro | 90% - PRISMA-ScR + 5 korakov + utemeljitev |
| 5 | **Vključitveni/Izključitveni Kriteriji** | ✅ Odlično | 100% - Jasne tabele + argumentacija |
| 6 | **Iskalne Strategije** | ✅ Izvrstno | 120% - 6 nizov + kombinirani + WOS specifično |
| 7 | **Identificirane Vrzeli** | ✅ Odlično | 100% - 4 kategorije (teoretične, empirične, metodološke, praktične) |
| 8 | **Pričakovani Prispevek** | ✅ Dobro | 90% - Teoretični, praktični, metodološki |
| 9 | **Časovni Načrt** | ✅ Dobro | 85% - 8 faz, 21 tednov (manjka Gantt diagram) |
| 10 | **Predlagane Revije** | ✅ Odlično | 100% - 6 revij z IF + utemeljitev |
| 11 | **Reference** | ✅ Dobro | 80% - 4 metodološke reference (manjka področje) |

### Predlagano v Implementation Plan (15 sekcij)

| # | Sekcija | V RAZISKOVALNI_NACRT? | Kritičnost |
|---|---------|----------------------|------------|
| 1 | Metadata | ✅ DA (kot Naslov) | Medium |
| 2 | Research Question | ✅ DA (odlično) | High |
| 3 | Theoretical Framework | ✅ DA (izvrstno) | High |
| 4 | Methodology | ✅ DA (dobro) | High |
| 5 | Search Strategy | ✅ DA (izvrstno) | High |
| 6 | Eligibility Criteria | ✅ DA (odlično) | High |
| 7 | Data Extraction | ⚠️ DELNO (v metodologiji) | High |
| 8 | Quality Assessment | ❌ MANJKA | High |
| 9 | Identified Gaps | ✅ DA (odlično) | High |
| 10 | Timeline | ✅ DA (dobro) | Medium |
| 11 | Expected Contributions | ✅ DA (dobro) | Medium |
| 12 | **Resources & Budget** | ❌ **MANJKA** | **HIGH** |
| 13 | **Ethical Considerations** | ❌ **MANJKA** | **MEDIUM** |
| 14 | **Dissemination Strategy** | ❌ **MANJKA** | **MEDIUM** |
| 15 | References | ✅ DA (delno) | Low |

---

## 🚨 KRITIČNE POMANJKLJIVOSTI

### 1. **Resources & Budget** ❌ VISOKA PRIORITETA

**Zakaj je kritično:**
- Financerji (EU, nacionalne agencije) zahtevajo proračun
- PROSPERO registracija lahko zahteva tim in vire
- Realnost izvedbe projekta
- Kredibilnost načrta

**Kaj naj vsebuje:**
```markdown
## 12. Viri in Proračun (Resources & Budget)

### 12.1 Raziskovalna Ekipa
| Vloga | Oseba | FTE | Odgovornosti |
|-------|-------|-----|--------------|
| Glavni raziskovalec (PI) | Dr. [Ime] | 0.4 | Celoten nadzor, pisanje |
| Soraziskovalec 1 | Dr. [Ime] | 0.2 | Metodologija, analiza |
| Soraziskovalec 2 | Prof. [Ime] | 0.1 | Teoretski okvir, supervizija |
| Raziskovalni asistent | [Ime] | 0.5 | Iskanje, ekstrakcija podatkov |
| Knjižničar | [Ime] | 0.1 | Iskalne strategije, baze |
| Statistični svetovalec | [Ime] | 0.05 | Konsultacije po potrebi |

### 12.2 Proračun
| Postavka | Opis | Strošek (€) |
|----------|------|-------------|
| **1. Kadri** | | |
| PI (80h × €50/h) | 10 tednov × 8h | 4,000 |
| RA (420h × €25/h) | 21 tednov × 20h | 10,500 |
| **2. Dostop do baz** | | |
| Scopus/WOS | Institucionalno | 0 |
| PubMed | Brezplačno | 0 |
| **3. Software** | | |
| Covidence/Rayyan | Screening | 200 |
| NVivo | Kvalitativna analiza | 0 (license) |
| **4. Publikacija** | | |
| Jezikovna lektura | Native speaker | 1,500 |
| APC (OA) | Target journal | 2,500 |
| **5. Konferenca** | | |
| EAWOP 2027 | Predstavitev | 1,500 |
| **Skupaj** | | **20,200€** |

### 12.3 Razpoložljivost Dostopa
- ✅ Institucijski dostop: WOS, Scopus, PsycINFO
- ✅ Software licence: NVivo, SPSS, R
- ⚠️ Potrebno zagotoviti: Covidence subscription
- ⚠️ Potrebno planirati: APC budget

### 12.4 Infrastruktura
- Delovna postaja za RA
- Zasebni prostor za sestanke tima
- Secure storage za podatke (GDPR compliant)
```

---

### 2. **Quality Assessment** ❌ VISOKA PRIORITETA

**Zakaj je kritično:**
- PRISMA-ScR priporoča (čeprav ni obvezno)
- Veča zaupanje v rezultate
- Pomaga identificirati šibke študije
- Metodološka strožnost

**Kaj naj vsebuje:**
```markdown
## 8. Ocena Kakovosti (Quality Assessment)

### 8.1 Pristop
Uporabili bomo **JBI Critical Appraisal Tools** prilagojene za scoping review:
- Different tools for quantitative, qualitative, mixed-methods studies
- Two independent appraisers
- Consensus meeting for discrepancies

### 8.2 Kriteriji po Vrsti Študije

**Za kvantitativne študije (JBI Analytical Cross-Sectional):**
1. Ali so vključitveni kriteriji jasno definirani?
2. Ali so participanti in okolje podrobno opisani?
3. Ali je ekspozicija (AI/UI) veljavno in zanesljivo merjena?
4. Ali so objektiven in standarden postopki uporabljeni?
5. Ali so confounders identificirani?
6. Ali so uporabljene strategije za obvladovanje confounders?
7. Ali so izhodi veljavno in zanesljivo merjeni?
8. Ali je uporabljena ustrezna statistična analiza?

**Za kvalitativne študije (JBI Qualitative):**
1. Ali je skladnost med filozofijo raziskave in metodologijo?
2. Ali je skladnost med metodologijo in raziskovalnim vprašanjem?
3. Ali je skladnost med metodologijo in zbiranjem podatkov?
4. Ali je skladnost med metodologijo in reprezentacijo ter analizo podatkov?
5. Ali je skladnost med metodologijo in interpretacijo rezultatov?
6. Ali je pozicioniranost raziskovalca navedena?
7. Ali je vpliv raziskovalca na raziskavo upoštevano?
8. Ali so udeleženci ustrezno reprezentirani?
9. Ali je raziskava etično ustrezna?
10. Ali so sklepi podprti s podatki?

### 8.3 Ocenjevanje
- **Ne bo izključitveni kriterij** (scoping review vključuje vse relevantne študije)
- **Bo uporabljeno za:**
  - Opisno: poročanje o kakovosti vključenih študij
  - Analitično: stratifikacija rezultatov po kakovosti (visoka/srednja/nizka)
  - Interpretativno: identificiranje metodoloških pomanjkljivosti v polju

### 8.4 Poročanje
- PRISMA flow diagram bo vključeval:
  - Število ocenjenih študij
  - Porazdelitev po kategorijah kakovosti
  - Razloge za nizko kakovost
```

---

### 3. **Ethical Considerations** ❌ SREDNJA PRIORITETA

**Zakaj je pomembno:**
- Vedno več revij zahteva izjavo o etiki
- PROSPERO vprašanje
- Transparentnost raziskave
- GDPR compliance za podatke

**Kaj naj vsebuje:**
```markdown
## 13. Etične Presoje (Ethical Considerations)

### 13.1 Etična Odobritev
**Status:** Etična odobritev **ni potrebna** za scoping review, ki analizira objavljeno literaturo.

**Utemeljitev:**
- Ni primarnega zbiranja podatkov od ljudi
- Vsi podatki iz javno dostopnih virov
- Ni intervencij ali eksperimentov

**Opomba:** Če bi projekt vključeval survey ali interviews s HR profesionalci, bi bila potrebna odobritev institucijskega etičnega odbora.

### 13.2 Upravljanje Podatkov (Data Management)

**Hramba podatkov:**
- Vsi zadetki iz baz → Zotero/EndNote biblioteca
- Screening decisions → Covidence/Excel (šifrirano)
- Ekstrahirani podatki → Secure OneDrive (šifriran)
- Trajanje hranjenja: 10 let (v skladu z Evropsko direktivo o odprti znanosti)

**Podatkovni protokol:**
| Vrsta podatka | Lokacija | Backup | Dostop |
|---------------|----------|--------|--------|
| Bibliografske reference | Zotero (cloud) | Auto | Tim |
| Screening data | Covidence | Auto | 2 reviewers |
| Extracted data | OneDrive (encrypted) | Daily | PI + RA |
| Analysis files | Secure server | Weekly | PI |

**GDPR Skladnost:**
- Dokumenti ne vsebujejo osebnih podatkov
- Metadata about authors → publicly available info only
- No sensitive data processing

### 13.3 Transparentnost

**Preregistracija:**
- ✅ PROSPERO registracija pred začetkom iskanja
- ✅ OSF projekt za sharing protokola in materialov

**Odprti podatki (Open Data):**
- Po publikaciji bomo delili:
  - Full search strings
  - Seznam vključenih študij
  - Data extraction form (template)
  - R/Excel kode za analizo
- Platforma: OSF (Open Science Framework)

### 13.4 Konflikti Interesov

**Finančni:**
- Ni finančnih konfliktov - javno financiran raziskovalni projekt
- Če: [navesti vir financiranja]

**Nefinančni:**
- Nekateri avtorji so lahko objavili na področju (full disclosure)
- Mitigacija: neodvisni reviewerji za študije avtorjev tega plana

### 13.5 Avtorstvo

**Kriteriji (ICMJE):**
1. Substancielni prispevek k zasnovi, zbiranju, analizi ali interpretaciji
2. Sodelovanje pri pisanju ali kritični reviziji
3. Končna odobritev verzije za objavo
4. Odgovornost za natančnost in integritet

**Pričakovani avtorji:**
- Glavni avtor: [PI ime]
- Soavtorji: [Sodelavci, ki izpolnjujejo kriterije]
- Priznanja (Acknowledgments): Knjižničar, statistik (podporne vloge)
```

---

### 4. **Dissemination Strategy** ❌ SREDNJA PRIORITETA

**Zakaj je pomembno:**
- Večina financerjev zahteva
- Impact beyond academia (praktiki, policy makers)
- Responsible research in innovation (RRI)
- Družbena relevantnost

**Kaj naj vsebuje:**
```markdown
## 14. Strategija Diseminacije (Dissemination Strategy)

### 14.1 Akademske Audiences

**Peer-Review Publikacija:**
- **Primarna objava:** Target journal (IF 5.0+) → see Section 10
- **Časovnica:** Oddaja do M18, sprejem do M24
- **Format:** Open Access (če možno) za maksimalno dosegljivost

**Konference:**
| Konferenca | Datum | Lokacija | Format |
|------------|-------|----------|--------|
| EAWOP 2027 | Maj 2027 | Stockholm | Oral presentation |
| AoM Annual Meeting | Avg 2027 | Atlanta | Symposium proposal |
| ECDP 2027 | Sep 2027 | Rotterdam | Poster |

**Alternativne publikacije:**
- Policy brief (4-6 strani) → EU-OSHA, EUROFOUND
- Working paper series (če ustrezno)

### 14.2 Praktične Audiences

**HR Profesionalci:**
- **Executive summary** (2 strani, brez žargona)
  - Ključne ugotovitve
  - Actionable recommendations
  - Checklist za HR
- **Webinar** v sodelovanju s:
  - CIPD (Chartered Institute of Personnel and Development)
  - SHRM (Society for Human Resource Management)
  - HRM Slovenija

**Organizacije:**
- **One-page infographic** (vizualno)
  - 5 top psihosocialnih tveganj AI
  - HR strategije za mitigation
  - Deliti na LinkedIn, ResearchGate

**Praktične platforme:**
- LinkedIn article (summary)
- Medium/Substack (accessible version)
- HR podcast intervju (če povabljeni)

### 14.3 Policy Audiences

**EU-OSHA:**
- **Policy brief** z regulatornimi priporočili
- Osredotočenost na:
  - AI Act implementacija (člen 14 - human oversight)
  - OSH direktiva gaps
  - GDPR + psihosocialna tveganja

**Nacionalni nivo:**
- Ministrstvo za delo
- Inšpektorat za delo
- Varnostni inžinirji (ZVIRZI, DI)
- HRM Slovenija (zbornica)

### 14.4 Odprta Znanost (Open Science)

**Preregistracija:**
- PROSPERO → protocol accessible

**Odprti Podatki:**
- OSF repository:
  - Search strings
  - Vključene študije (list)
  - Data extraction template
  - Analysis scripts (R/Python)

**Odprta Publikacija:**
- Target: OA journal ali green OA (self-archiving)
- Preprint: možno na arXiv/SocArXiv pred review

### 14.5 Mediji

**Akademski mediji:**
- The Conversation (če ustrezno)
- University press release

**Splošni mediji:**
- Press release ob publikaciji
- Če povpraševanje: intervjuji (RTV, časopisi)

### 14.6 Uspešnostne Metrike

**Akademski impact:**
- Citations: Target ≥50 v 3 letih (per Google Scholar)
- Altmetric score: Target ≥100
- Downloads: Target ≥1000 v prvi leto

**Praktični impact:**
- Webinar udeleženci: Target ≥100 HR profesionalcev
- Policy mentions: Target ≥2 policy documents citirajo
- Training materials: Target ≥5 organizacij vključi v training

**Družbeni impact:**
- Media mentions: Target ≥5 reportaž
- Social media reach: Target ≥10,000 impressions (LinkedIn + Twitter)
```

---

### 5. **Data Extraction & Charting** ⚠️ DELNO POKRITO

**Status:** Omenjen v metodologiji (Korak 4), ampak ni samostojne razširjene sekcije

**Priporočilo:** Razširiti v samostojno sekcijo z:
```markdown
## 7. Ekstrakcija Podatkov in Kartiranje (Data Extraction & Charting)

### 7.1 Data Charting Form

**Sekcija A: Bibliografski podatki**
- Avtorji, leto, naslov, revija
- DOI, država študije
- Vrsta publikacije (journal article, review, thesis)

**Sekcija B: Metodološki podatki**
| Polje | Vrednosti |
|-------|-----------|
| Dizajn študije | Kvantitativna / Kvalitativna / Mixed-methods |
| Metoda | Survey, Interview, Etnografija, Case study, Eksperiment, RCT |
| Velikost vzorca | N = ? |
| Populacija | Zaposleni (sektor, role, demographics) |

**Sekcija C: Konceptualni podatki**
| Polje | Opis |
|-------|------|
| Vrsta AI/tehnologije | Algoritemski mngmt, Chatbots, AI analytics, Automation |
| HR funkcija | Recruitment, Training, Performance mgmt, Workforce planning |
| Psihosocialna tveganja | Technostress, burnout, anxiety, job insecurity |
| Organizacijska kultura | Digital culture, leadership, trust |
| Teoretski okvir | JD-R, COR, SDT, drugi |

**Sekcija D: Rezultati**
- Ključne ugotovitve (bullet points)
- Statistični rezultati (če relevant)
- Identificirana tveganja
- HR intervencije (če mentioned)

**Sekcija E: Kvaliteta**
- JBI appraisal score
- Limitacije (author-reported)
- Risk of bias

### 7.2 Pilotiranje

**Proces:**
1. Tim razvije draft form
2. Pilot test na **10 random študijah**
3. 2 reviewerja neodvisno ekstrahirajo
4. Primerjava: Inter-rater reliability (Cohen's kappa)
5. Diskusija razhajanj → izboljšave form
6. Final form approval
7. **Training session** za vse data extractors

**Target inter-rater reliability:** κ ≥ 0.80 (substantial agreement)

### 7.3 Ekstrakcijski Proces

**Workflow:**
```
Included Study (n=X)
    ↓
Randomly assign to Reviewer 1 or 2
    ↓
Data extraction in Covidence/Excel
    ↓
10% double extraction (quality check)
    ↓
Weekly team meetings (resolve issues)
    ↓
Data finalized → analysis
```

**Časovna ocena:**
- 30 min per article (povprečno)
- 50 študij = 25 ur
- 2 reviewerji paralelno → 12-13 ur vsak
- Rezerva za kompleksne študije: +30%

### 7.4 Upravljanje Podatkov

**Software:**
- **Covidence:** Integrated screening + extraction
- **Backup:** Excel/Google Sheets (structured template)
- **Analysis:** R/SPSS/NVivo (odvisno od analize)

**Verzioniranje:**
- Data extraction form v1.0, v2.0 (post-pilot)
- Changelog: dokumentirane spremembe
- Git repository za analysis scripts
```

---

## ✅ EVALVACIJSKI KRITERIJI - ANALIZA

### Predlagani v Implementation Plan:

| Kriterij | Utež | Max Score | Subcriteria |
|----------|------|-----------|-------------|
| **Clarity** | 25% | 25 | RQ (8), Objectives (6), Structure (6), Language (5) |
| **Feasibility** | 25% | 25 | Timeline (8), Resources (7), Scope (5), Risks (5) |
| **Rigor** | 30% | 30 | Methodology (10), Search (8), Eligibility (6), QA (6) |
| **Contribution** | 20% | 20 | Novelty (7), Significance (7), Implications (6) |

### 🔬 KRITIČNA OCENA KRITERIJEV

#### ✅ **Je struktura ustrezna?** 
**DA** - To so standardni kriteriji za evalvacijo research proposals v:
- NSF (National Science Foundation)
- H2020/Horizon Europe grant applications
- NIH grant reviews
- Academic research proposal evaluation rubrics

#### ⚠️ **Manjkajoči kriteriji?**

**1. Ethics Considerations (!)** 
- Trenutno NI eksplicitno pod nobenem kriterijem
- **Predlog:** Dodati pod **Rigor** ali kot samostojen kriterij (5%)

**2. Dissemination & Impact**
- Trenutno delno pod "Contribution > Implications"
- **Predlog:** Razširiti "Implications" → "Impact & Dissemination" (jasnejše)

**3. Team Qualifications**
- Trenutno delno pod "Feasibility > Resources"
- **Predlog:** Eksplicitno poudariti v "Feasibility"

#### 📊 **Predlagane Izboljšave:**

**Option A: Conservative (4 kriteriji, redistribucija)**
```python
EVALUATION_CRITERIA_V2 = {
    "clarity": {
        "weight": 0.25,
        "max_score": 25,
        "subcriteria": {
            "research_questions": 8,
            "objectives": 6,
            "structure": 6,
            "language": 5
        }
    },
    "feasibility": {
        "weight": 0.25,
        "max_score": 25,
        "subcriteria": {
            "timeline": 7,
            "resources_budget": 7,  # ✨ Eksplicitno budget
            "team_qualifications": 6,  # ✨ Nov subkriterij
            "scope": 3,
            "risk_mitigation": 2
        }
    },
    "rigor": {
        "weight": 0.30,
        "max_score": 30,
        "subcriteria": {
            "methodology": 9,
            "search_strategy": 8,
            "eligibility_criteria": 5,
            "quality_assessment": 5,
            "ethics_data_mgmt": 3  # ✨ Nov subkriterij
        }
    },
    "contribution": {
        "weight": 0.20,
        "max_score": 20,
        "subcriteria": {
            "novelty": 7,
            "significance": 6,
            "implications_impact": 5,  # ✨ Renamed
            "dissemination": 2  # ✨ Nov subkriterij
        }
    }
}
```

**Option B: Expanded (5 kriterjev)**
```python
EVALUATION_CRITERIA_V2_EXPANDED = {
    "clarity": {"weight": 0.20, "max_score": 20, ...},
    "feasibility": {"weight": 0.20, "max_score": 20, ...},
    "rigor": {"weight": 0.30, "max_score": 30, ...},
    "contribution": {"weight": 0.15, "max_score": 15, ...},
    "ethics_impact": {  # ✨ NOV glavni kriterij
        "weight": 0.15,
        "max_score": 15,
        "subcriteria": {
            "ethical_considerations": 5,
            "data_management": 4,
            "dissemination_plan": 4,
            "societal_impact": 2
        }
    }
}
```

### 📋 **Priporočilo:**

**Izbrati Option A (Conservative)** ker:
1. Ohranja uveljavljeno 4-kriterijsko strukturo
2. Vključuje manjkajoče elemente kot subkriterije
3. Lažje razumljivo za uporabnike
4. Konsistentno z večino grant review rubrics

**Ethics + Dissemination** sta pomembna, ampak ne zaslužita samostojnega glavnega kriterija (5%) - bolje kot subcriteria pod Rigor/Contribution.

---

## 🎯 PRIPOROČILA ZA STRUKTUR RESEARCH PLAN

### **Minimalno Potrebne Sekcije (MVP):** 12 sekcij

1. ✅ Title & Metadata
2. ✅ Research Question (+ PCC)
3. ✅ Theoretical Framework
4. ✅ Methodology (PRISMA-ScR)
5. ✅ Search Strategy
6. ✅ Eligibility Criteria
7. ⚠️ **Data Extraction** (razširiti)
8. ❌ **Quality Assessment** (dodati)
9. ✅ Identified Gaps
10. ✅ Timeline
11. ✅ Expected Contributions
12. ❌ **Resources & Budget** (dodati)

### **Priporočene Dodatne Sekcije (Full Feature):** +3 sekcije

13. ❌ **Ethical Considerations** (dodati)
14. ❌ **Dissemination Strategy** (dodati)
15. ✅ Key References (že ima)

### **Opcijske Izboljšave:**

16. Risk Management (če zahteva financerji)
17. Stakeholder Engagement (če participativna raziskava)
18. Communication Plan (če kompleksni team)

---

## 📝 FINALNI PREDLOG: 15 SEKCIJ

| # | Sekcija | Prioriteta | V Current? | Action |
|---|---------|------------|------------|--------|
| 1 | Title & Metadata | Must-have | ✅ | Keep |
| 2 | Research Question | Must-have | ✅ | Keep |
| 3 | Theoretical Framework | Must-have | ✅ | Keep |
| 4 | Methodology | Must-have | ✅ | Keep |
| 5 | Search Strategy | Must-have | ✅ | Keep |
| 6 | Eligibility Criteria | Must-have | ✅ | Keep |
| 7 | Data Extraction | Must-have | ⚠️ | **Expand** |
| 8 | Quality Assessment | Must-have | ❌ | **ADD** |
| 9 | Identified Gaps | Must-have | ✅ | Keep |
| 10 | Timeline | Must-have | ✅ | Keep (+ Gantt?) |
| 11 | Expected Contributions | Must-have | ✅ | Keep |
| 12 | Resources & Budget | Must-have | ❌ | **ADD** |
| 13 | Ethical Considerations | Recommended | ❌ | **ADD** |
| 14 | Dissemination Strategy | Recommended | ❌ | **ADD** |
| 15 | Key References | Must-have | ✅ | Expand (+ domain refs) |

**TOTAL:** 15 sekcij (12 must-have + 3 recommended)

---

## ✅ ZAKLJUČEK

### **Odgovor na vprašanja:**

**1. So 15 sekcij ustrezne?**
✅ **DA** - To je optimalna struktura za comprehensive research plan. Pokriva vse potrebno za:
- PROSPERO registracijo
- Grant applications
- Institutional approval
- High-quality execution

**2. Ali so evalvacijski kriteriji pravilni?**
✅ **DA (z manjšimi izboljšavami)** - Clarity, Feasibility, Rigor, Contribution so standardni. Priporočam **Option A redistribucijo** da eksplicitno vključi:
- Budget under Feasibility
- Ethics under Rigor
- Dissemination under Contribution

**3. Kaj manjka trenutno?**
❌ **4 sekcije manjkajo ali so nepopolne:**
1. Quality Assessment (dodati)
2. Data Extraction (razširiti)
3. Resources & Budget (dodati)
4. Ethical Considerations (dodati)
5. Dissemination Strategy (dodati)

**4. Ali gremo na Full Feature Set?**
✅ **DA** - 15 sekcij je optimalno. 12 MVP + 3 recommended je right balance med completeness in practical usability.

---

## 🚀 NASLEDNJI KORAKI

**Faza 1: Pregled Odobren ✅**
- Struktura 15 sekcij potrjena
- Evalvacijski kriteriji Option A izbrani

**Faza 2: Implementacija (Start Now)**
1. Dopolniti RESEARCH_PLAN_SECTIONS config (15 sekcij)
2. Posodobiti EVALUATION_CRITERIA_V2 (Option A)
3. Začeti s korakom 1: Agents (Writer + Evaluator)

**Faza 3: Kritik po vsakem koraku**
- Post-implementation review
- Code quality check
- Test execution
- Mikroskopski pregled

**Faza 4: Skills Creation**
- Identificirati potrebne skills
- Ustvariti SKILL.md files
- Testing v 3 fazah

---

**Dokument pripravljen za nadaljnjo akcijo.**

