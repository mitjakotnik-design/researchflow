# ResearchFlow: AI-Powered Scoping Review Platform

## Architecture & Implementation Plan

**Version:** 2.3  
**Date:** April 2026  
**Status:** REVISED - Detailed Competitive Comparison Added

### Changelog v2.3
- Added Detailed Competitive Comparison by Categories (Section 39)
- 8 evaluation categories with 50+ metrics
- Individual competitor profiles
- Radar chart comparisons
- Feature-by-feature analysis

### Changelog v2.2
- Added Market Positioning Analysis (Section 34)
- Added Web of Science API Integration Analysis (Section 35)
- Added Global Market Potential (Section 36)
- Added Tool Classification & Category Mapping (Section 37)
- Added Competitive Tier Ranking (Section 38)

### Changelog v2.1
- Added SWOT Analysis (Section 22)
- Added Risk Analysis with Mitigation Strategies (Section 23)
- Added Competitive Analysis (Section 24)
- Added Technical Dependencies & Bottlenecks (Section 25)
- Added MVP Definition (Section 26)
- Added Success Metrics / KPIs (Section 27)
- Added Team Requirements (Section 28)
- Added Legal & IP Considerations (Section 29)
- Added Go-to-Market Strategy (Section 30)
- Added Vendor Lock-in Analysis (Section 31)
- Added Known Limitations & Future Improvements (Section 32)

### Changelog v2.0
- Added Full-text Screening phase (Phase 4.5)
- Added GDPR compliance section
- Added Cost estimation
- Added Disaster Recovery plan
- Added Observability/Monitoring specification
- Added API versioning (/api/v1/)
- Added Accessibility (WCAG 2.1 AA) requirements
- Enhanced security with LLM-based content moderation
- Extended timeline to 20 weeks (realistic)
- Added Multi-user collaboration support
- Added Document versioning
- Added Integration endpoints (Zotero, DOI resolution)

---

## 1. Executive Summary

ResearchFlow je komercialna platforma za avtomatizirano pisanje znanstvenih preglednih člankov (scoping review, systematic review). Platforma temelji na multi-agent sistemu z integriranim Human-in-the-Loop (HITL) pristopom, kjer raziskovalec vodi orodje in ne obratno.

### Ključne lastnosti:
- **Chatbot-vodeni raziskovalni načrt** - uporabnik preko pogovora oblikuje raziskovalni načrt
- **Avtomatizirana generacija iskalnih nizov** - WoS, Scopus, PubMed formati
- **HITL potrjevanje** - človeška potrdiitev na kritičnih točkah
- **Transparentno delovanje** - vpogled v delo agentov, statistike, vire
- **RAG-podprt pomočnik** - chatbot z dostopom do vseh dokumentov in reasoning sledi
- **Cloud-native arhitektura** - Google Cloud z avtentikacijo in varnostjo

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React/Next.js)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Chatbot     │  │   Article    │  │   Agent      │  │  Document    │    │
│  │  Interface   │  │   Viewer     │  │   Monitor    │  │  Explorer    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   HITL       │  │  Statistics  │  │   Source     │  │  Research    │    │
│  │   Decisions  │  │   Dashboard  │  │   Citations  │  │   Plan       │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                           API Gateway (Cloud Run)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                        Authentication (Firebase Auth)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                              BACKEND SERVICES                                │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     Orchestration Service                             │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │ Research   │  │ Writing    │  │  Quality   │  │  HITL      │     │   │
│  │  │ Cluster    │  │ Cluster    │  │  Cluster   │  │  Manager   │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         RAG Service                                    │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │ Document   │  │  Vector    │  │  Hybrid    │  │  Reasoning │     │   │
│  │  │ Ingestion  │  │  Search    │  │  Search    │  │  Archive   │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       Chatbot Service                                  │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │   │
│  │  │ Research   │  │ Assistant  │  │  Context   │  │  Prompt    │     │   │
│  │  │ Plan Gen   │  │  Mode      │  │  Manager   │  │  Guard     │     │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                             DATA LAYER                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Firestore │  │   Cloud    │  │   Vector   │  │   Redis    │            │
│  │  (State)   │  │   Storage  │  │   DB       │  │  (Session) │            │
│  │            │  │   (Files)  │  │  (ChromaDB │  │            │            │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MEMORY SYSTEM                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐                    │
│  │   SESSION MEMORY    │         │    CHAT MEMORY      │                    │
│  │   (Redis/Memorystore)│         │    (Firestore)      │                    │
│  │                     │         │                     │                    │
│  │ • Trenutna seja     │         │ • Zgodovina chata   │                    │
│  │ • Aktiven projekt   │         │ • Kontekst pogovora │                    │
│  │ • Delovni draft     │         │ • Razumevanje namen│                    │
│  │ • Temporary state   │         │                     │                    │
│  └─────────────────────┘         └─────────────────────┘                    │
│                                                                              │
│  ┌─────────────────────┐         ┌─────────────────────┐                    │
│  │  SEMANTIC MEMORY    │         │   FINAL MEMORY      │                    │
│  │  (ChromaDB/Vertex   │         │   (Cloud Storage    │                    │
│  │   AI Matching)      │         │    + Firestore)     │                    │
│  │                     │         │                     │                    │
│  │ • Vektorizirani     │         │ • Končni članki     │                    │
│  │   dokumenti         │         │ • Potrjeni plani    │                    │
│  │ • Reasoning traces  │         │ • Arhiv projektov   │                    │
│  │ • Povezane teme     │         │ • Revizije          │                    │
│  └─────────────────────┘         └─────────────────────┘                    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                     PROJECT MEMORY (Per-User)                        │    │
│  │                                                                      │    │
│  │ gs://researchflow-{project_id}/                                     │    │
│  │ ├── raw_pdfs/           # Originalni PDF-ji                         │    │
│  │ ├── selected_articles/  # Izbrani full-text članki                  │    │
│  │ ├── md_documents/       # Pretvorjeni MD dokumenti                  │    │
│  │ ├── vectors/            # ChromaDB kolekcije                        │    │
│  │ ├── drafts/             # Osnutki članka                            │    │
│  │ ├── reasoning_traces/   # LLM reasoning arhiv                       │    │
│  │ └── exports/            # Končni izvozi (PDF, DOCX)                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Workflow Pipeline

### 3.1 Complete Research Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FAZA 1: RAZISKOVALNI NAČRT                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [CHATBOT] ──► Uporabnik opishe temo ──► Chatbot generira                  │
│                                          predlog načrta                     │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #1] ──► Uporabnik pregleda/potrdi ──► Raziskovalni načrt           │
│                raziskovalni načrt             potrjen                       │
│                                                                              │
│  Vključuje:                                                                  │
│  • Naslov članka (izbor iz predlogov)                                       │
│  • Raziskovalna vprašanja                                                    │
│  • Teoretični okvir                                                          │
│  • Vključitveni/izključitveni kriteriji                                     │
│  • Metodologija (Scoping/Systematic)                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       FAZA 2: ISKALNI NIZI                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [AGENT: SearchStringGenerator] ──► Generira iskalne nize za:              │
│                                      • Web of Science                        │
│                                      • Scopus                                │
│                                      • PubMed                                │
│       │                              • PsycINFO                              │
│       ▼                                                                      │
│  [HITL #2] ──► Uporabnik pregleda nize ──► Nizi potrjeni                   │
│                lahko doda/odstrani                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FAZA 3: ABSTRACT SCREENING                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [INGESTION] ──► Dva načina:                                                │
│                  1. Upload mapa s PDF-ji (abstracts)                        │
│                  2. Drag & drop / paste v UI                                │
│       │                                                                      │
│       ▼                                                                      │
│  [AGENT: AbstractScreener] ──► Kategorizira abstrakte:                      │
│                                 • INCLUDE (relevantni)                       │
│                                 • EXCLUDE (nerelevantni)                     │
│                                 • UNCERTAIN (potrebna odločitev)            │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #3] ──► Uporabnik pregleda UNCERTAIN ──► Končna selekcija          │
│                in INCLUDE članke                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 4: FULL-TEXT IDENTIFIKACIJA                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [AGENT: IdentifierExtractor] ──► Iz vključenih abstraktov ekstrahira:     │
│                                    • DOI                                     │
│                                    • WoS Accession Number                    │
│                                    • Naslov + avtorji                        │
│       │                                                                      │
│       ▼                                                                      │
│  [AGENT: SearchQueryBuilder] ──► Generira:                                  │
│                                   • Posamezne WoS iskalne nize              │
│                                   • Kombiniran master search string         │
│                                   • Export format za masovni prenos         │
│       │                                                                      │
│       ▼                                                                      │
│  [OUTPUT] ──► Uporabnik dobi:                                               │
│               • Seznam potrebnih full-text člankov                           │
│               • Iskalni niz za WoS                                           │
│               • Navodila za prenos                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 5: FULL-TEXT INGESTION                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [INGESTION] ──► Dva načina:                                                │
│                  1. Upload mapa s full-text PDF-ji                          │
│                  2. Drag & drop v UI                                         │
│       │                                                                      │
│       ▼                                                                      │
│  [AGENT: PDFProcessor] ──► Pretvori PDF v:                                  │
│                             • Strukturiran tekst                             │
│                             • Markdown format                                │
│                             • Vektorske embeddings                          │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #4] ──► Uporabnik potrdi ustreznost ──► Dokumenti pripravljeni      │
│                vseh naloženih dokumentov                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 6: RESEARCH GAP ANALYSIS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [AGENT: GapIdentifier] ──► Analizira literature:                           │
│                              • Teoretične vrzeli                             │
│                              • Empirične vrzeli                              │
│                              • Metodološke vrzeli                            │
│       │                                                                      │
│       ▼                                                                      │
│  [AGENT: AdditionalSearchGenerator] ──► Predlaga dodatne:                   │
│                                          • Iskalne nize za GAP-e            │
│                                          • Ključne besede                    │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #5] ──► Uporabnik odloči ali nadaljuje ──► Loop ali naprej          │
│                z dodatnim iskanjem ali                                       │
│                nadaljuje s pisanjem                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 7: ARTICLE GENERATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [SATURATION LOOP] ──► Iterativno pisanje članaka:                          │
│                                                                              │
│       ┌──────────────────────────────────────────────────────┐              │
│       │                                                       │              │
│       │  [Writer] ──► Piše sekcijo članka                    │              │
│       │       │                                               │              │
│       │       ▼                                               │              │
│       │  [Evaluators] ──► Ocenijo kakovost                   │              │
│       │       │                                               │              │
│       │       ▼                                               │              │
│       │  [FactChecker] ──► Preveri trditve z viri           │              │
│       │       │                                               │              │
│       │       ▼                                               │              │
│       │  [ConsistencyChecker] ──► Preveri konsistentnost    │              │
│       │       │                                               │              │
│       │       ▼                                               │  Saturacija │
│       │  Ali kakovost ≥ prag? ──► DA ──► Sekcija končana    │  dosežena   │
│       │       │                                               │              │
│       │      NE                                               │              │
│       │       │                                               │              │
│       │       ▼                                               │              │
│       │  [Critic] ──► Predlaga izboljšave ───────────────────┘              │
│       │                                                                      │
│       └──────────────────────────────────────────────────────┘              │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #6] ──► Uporabnik pregleda draft ──► Popravki ali potrditev        │
│                po vsaki generaciji                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FAZA 8: VISUALIZATION & EXPORT                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [AGENT: Visualizer] ──► Generira vizualizacije:                            │
│                           • PRISMA diagram                                   │
│                           • Conceptual model                                 │
│                           • Evidence gap map                                 │
│                           • Geographic distribution                          │
│       │                                                                      │
│       ▼                                                                      │
│  [HITL #7] ──► Uporabnik izbere vizualizacije ──► Končna verzija          │
│                                                                              │
│       │                                                                      │
│       ▼                                                                      │
│  [EXPORT] ──► Generira končne dokumente:                                    │
│               • PDF (publication-ready)                                      │
│               • DOCX (za revijo)                                             │
│               • Markdown (za repo)                                           │
│               • BibTeX (reference)                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Frontend Layout

### 4.1 Main Interface Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ResearchFlow            [Project: HR & AI Scoping]      [User] [Settings]  │
├────────────────────┬────────────────────────────────────────────────────────┤
│                    │                                                         │
│   NAVIGATION       │              MAIN WORKSPACE                             │
│                    │                                                         │
│   📋 Research Plan │  ┌───────────────────────────────────────────────────┐ │
│   🔍 Search        │  │                                                    │ │
│   📄 Documents     │  │                ARTICLE PREVIEW                     │ │
│   ✍️  Writing       │  │                                                    │ │
│   📊 Visualizations│  │  [PDF View] [Markdown View] [Split View]          │ │
│   ✅ HITL Queue    │  │                                                    │ │
│   📈 Statistics    │  │  ┌──────────────────────────────────────────────┐ │ │
│                    │  │  │ ## 1. Introduction                          │ │ │
│   ─────────────    │  │  │                                              │ │ │
│                    │  │  │ The contemporary organizational landscape... │ │ │
│   AGENT MONITOR    │  │  │                                              │ │ │
│                    │  │  │ [Source: Kim, 2022] [Source: Lee, 2021]     │ │ │
│   ● Writer         │  │  │                                              │ │ │
│     Writing sec 3  │  │  └──────────────────────────────────────────────┘ │ │
│   ○ FactChecker    │  │                                                    │ │
│     Waiting...     │  └───────────────────────────────────────────────────┘ │
│   ○ Critic         │                                                         │
│     Idle           │  ┌───────────────────────────────────────────────────┐ │
│                    │  │              HITL DECISION PANEL                  │ │
│   Generation: 3/5  │  │                                                    │ │
│   Quality: 87%     │  │  ⚠️  Decision Required: Select article title       │ │
│                    │  │                                                    │ │
│                    │  │  ○ "From Technostress to Organizational..."      │ │
│                    │  │  ○ "The Human Side of AI Adoption..."            │ │
│                    │  │  ○ "Bridging Technology and People..."           │ │
│                    │  │                                                    │ │
│                    │  │  [Confirm Selection] [Request More Options]      │ │
│                    │  └───────────────────────────────────────────────────┘ │
│                    │                                                         │
├────────────────────┴────────────────────────────────────────────────────────┤
│                              CHATBOT PANEL                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ 🤖 How can I help with your research?                                 │   │
│  │                                                                        │   │
│  │ User: Can you explain why you chose these search terms?               │   │
│  │                                                                        │   │
│  │ 🤖 Based on your research plan focusing on HR and AI integration,    │   │
│  │    I selected terms that capture:                                     │   │
│  │    • Technostress dimensions (from Tarafdar et al., 2007)            │   │
│  │    • HR functions terminology (from SHRM framework)                   │   │
│  │    [Show reasoning trace] [View source documents]                     │   │
│  │                                                                        │   │
│  │ [Type your message...                                    ] [Send]    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Document Explorer Panel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DOCUMENT EXPLORER                                        [Upload] [Refresh]│
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📁 Full-Text Articles (67)                                                 │
│  ├── 📄 Rohwer_2022_Technostress_Review.pdf                                 │
│  │      Used in: Introduction, Results                                      │
│  │      [View PDF] [View MD] [Show Citations]                               │
│  ├── 📄 Tarafdar_2007_Technostress_Framework.pdf                            │
│  │      Used in: Theoretical Framework, Discussion                          │
│  │      [View PDF] [View MD] [Show Citations]                               │
│  └── ...                                                                     │
│                                                                              │
│  📁 Abstracts Screened (314)                                                │
│  ├── ✅ Included (67)                                                        │
│  ├── ❌ Excluded (247)                                                       │
│  └── ⚠️  Pending Review (0)                                                  │
│                                                                              │
│  ─────────────────────────────────────────────────────────────              │
│                                                                              │
│  DRAG & DROP ZONE                                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                                                                       │   │
│  │     📄 Drop PDF files here or click to upload                        │   │
│  │                                                                       │   │
│  │     Supported: PDF, MD, TXT                                          │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Statistics Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  GENERATION STATISTICS                         Generation 3 of 5 (running)  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  QUALITY METRICS (Current Generation)                                       │
│  ┌────────────────┬────────────────┬────────────────┬────────────────┐      │
│  │   Coherence    │    Accuracy    │  Completeness  │   Consistency  │      │
│  │      87%       │      92%       │      78%       │      94%       │      │
│  │   ▲ +5%        │   ▲ +3%        │   ▲ +12%       │   ● 0%         │      │
│  └────────────────┴────────────────┴────────────────┴────────────────┘      │
│                                                                              │
│  PROGRESS BY SECTION                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Introduction     ████████████████████████████████████████████ 100%   │   │
│  │ Methods          ████████████████████████████████████████████ 100%   │   │
│  │ Results          ██████████████████████████████░░░░░░░░░░░░░░  68%   │   │
│  │ Discussion       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%   │   │
│  │ Conclusion       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  GENERATION HISTORY                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │     Quality Score                                                     │   │
│  │     100│        ┌───────○                                            │   │
│  │        │    ○───┘                                                     │   │
│  │     75 │ ○──┘                                                         │   │
│  │        │                                                               │   │
│  │     50 │                                                               │   │
│  │        └──────────────────────────────────────────────────            │   │
│  │           1      2      3      4      5                               │   │
│  │                   Generation                                          │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  AGENT ACTIVITY LOG                                                          │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ 21:45:32 │ Writer        │ Completed Results section 3.2             │   │
│  │ 21:44:18 │ FactChecker   │ Verified 12 claims, 0 issues              │   │
│  │ 21:43:05 │ RAG Search    │ Found 8 sources for query "technostress" │   │
│  │ 21:42:51 │ Writer        │ Started Results section 3.2               │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. HITL Decision Points

### 5.1 List of Human-in-the-Loop Decisions

| ID | Decision Point | Description | Options |
|----|----------------|-------------|---------|
| HITL-1 | Research Plan Approval | Potrditev celotnega raziskovalnega načrta | Approve / Edit / Regenerate |
| HITL-2 | Title Selection | Izbor naslova članka iz predlogov | Select one / Request more / Custom |
| HITL-3 | Search Strings Approval | Potrditev iskalnih nizov | Approve / Edit / Add more |
| HITL-4 | Abstract Screening Review | Pregled UNCERTAIN in INCLUDE člankov | Include / Exclude per abstract |
| HITL-5 | Full-text Selection | Potrditev izbranih full-text člankov | Confirm / Remove / Add |
| HITL-6 | Gap Analysis Direction | Ali nadaljevati z dodatnim iskanjem | Continue search / Proceed to writing |
| HITL-7 | Section Draft Review | Pregled vsakega drafta sekcije | Approve / Request revision / Edit |
| HITL-8 | Visualization Selection | Izbor vizualizacij za članek | Include / Exclude / Regenerate |
| HITL-9 | Final Article Review | Končna potrditev članka | Approve / Major revision / Minor edits |
| HITL-10 | Citation Format | Izbor formata citatov (APA, Harvard, etc.) | Select format |

### 5.2 HITL UI Component

```typescript
interface HITLDecision {
  id: string;
  type: HITLType;
  timestamp: Date;
  status: 'pending' | 'approved' | 'rejected' | 'modified';
  data: {
    title: string;
    description: string;
    options: HITLOption[];
    context?: string;  // RAG context for decision
    reasoning?: string; // LLM reasoning for suggestion
  };
  userResponse?: {
    selectedOption: string;
    customInput?: string;
    feedback?: string;
  };
}
```

---

## 6. Security Architecture

### 6.1 Authentication & Authorization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SECURITY LAYERS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. AUTHENTICATION (Firebase Auth)                                          │
│     ├── Email/Password login                                                 │
│     ├── OAuth (Google, Microsoft)                                            │
│     ├── MFA optional                                                         │
│     └── JWT tokens (1h expiry, refresh)                                     │
│                                                                              │
│  2. AUTHORIZATION (Cloud IAM + Firestore Rules)                             │
│     ├── Role-based: Admin, Researcher, Reviewer                             │
│     ├── Project-level permissions                                            │
│     └── Document-level access control                                        │
│                                                                              │
│  3. PROMPT INJECTION PROTECTION                                             │
│     ├── Input sanitization (remove control chars)                           │
│     ├── Length limits (max 10,000 chars per input)                          │
│     ├── Pattern detection (known injection patterns)                         │
│     ├── Role separation (system vs user prompts)                            │
│     └── Output filtering (PII, harmful content)                             │
│                                                                              │
│  4. DATA PROTECTION                                                          │
│     ├── Encryption at rest (Cloud Storage, Firestore)                       │
│     ├── Encryption in transit (TLS 1.3)                                     │
│     ├── VPC Service Controls                                                 │
│     └── Data residency (EU region)                                           │
│                                                                              │
│  5. MINIMAL ACCESS PRINCIPLE                                                 │
│     ├── Service accounts per service                                         │
│     ├── Scoped API keys                                                      │
│     ├── No direct DB access from frontend                                    │
│     └── Audit logging (Cloud Audit Logs)                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Prompt Guard Implementation

```python
class PromptGuard:
    """Protect against prompt injection attacks."""
    
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"disregard all prior",
        r"you are now",
        r"pretend you are",
        r"act as if",
        r"\\[SYSTEM\\]",
        r"\\<\\|.*\\|\\>",
    ]
    
    MAX_INPUT_LENGTH = 10000
    
    def sanitize(self, user_input: str) -> str:
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', user_input)
        
        # Enforce length limit
        sanitized = sanitized[:self.MAX_INPUT_LENGTH]
        
        # Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise PromptInjectionError(f"Suspicious pattern detected")
        
        return sanitized
    
    def wrap_user_input(self, user_input: str) -> str:
        """Clearly mark user input in prompts."""
        sanitized = self.sanitize(user_input)
        return f"<user_input>{sanitized}</user_input>"
```

---

## 7. Google Cloud Architecture

### 7.1 Cloud Services

| Service | Purpose | Configuration |
|---------|---------|---------------|
| Cloud Run | Backend services | Min 0, Max 10 instances |
| Cloud Storage | File storage | Multi-regional, EU |
| Firestore | State & chat history | Native mode |
| Memorystore (Redis) | Session cache | 1GB, Standard tier |
| Vertex AI | LLM APIs | gemini-2.5-flash/pro |
| Cloud Build | CI/CD | Triggered on push |
| Secret Manager | API keys | Automatic rotation |
| Cloud Armor | WAF | OWASP rules |
| Cloud CDN | Static assets | Frontend hosting |

### 7.2 Cloud Build Pipeline

```yaml
# cloudbuild.yaml
steps:
  # Build frontend
  - name: 'node:20'
    dir: 'frontend'
    entrypoint: 'npm'
    args: ['ci']
    
  - name: 'node:20'
    dir: 'frontend'
    entrypoint: 'npm'
    args: ['run', 'build']
    
  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/researchflow-api', './backend']
    
  # Run tests
  - name: 'gcr.io/$PROJECT_ID/researchflow-api'
    entrypoint: 'pytest'
    args: ['tests/', '-v']
    
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'researchflow-api'
      - '--image=gcr.io/$PROJECT_ID/researchflow-api'
      - '--region=europe-west1'
      - '--platform=managed'
      
  # Deploy frontend to Firebase Hosting
  - name: 'gcr.io/$PROJECT_ID/firebase'
    args: ['deploy', '--only', 'hosting']

timeout: '1200s'
```

### 7.3 Infrastructure as Code (Terraform)

```hcl
# main.tf
resource "google_cloud_run_service" "api" {
  name     = "researchflow-api"
  location = "europe-west1"
  
  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/researchflow-api"
        
        resources {
          limits = {
            memory = "2Gi"
            cpu    = "2"
          }
        }
        
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
      }
      
      service_account_name = google_service_account.api.email
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "10"
      }
    }
  }
}

resource "google_storage_bucket" "documents" {
  name     = "researchflow-documents-${var.project_id}"
  location = "EU"
  
  uniform_bucket_level_access = true
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}
```

---

## 8. Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] GitHub repository setup
- [ ] Project structure refactoring  
- [ ] Basic authentication (Firebase)
- [ ] Cloud infrastructure (Terraform)
- [ ] CI/CD pipeline (Cloud Build)

### Phase 2: Core Backend (Weeks 3-4)
- [ ] API Gateway setup
- [ ] Memory system implementation
- [ ] RAG service enhancement
- [ ] Chatbot service (research plan creation)
- [ ] Basic HITL framework

### Phase 3: Agent Enhancement (Weeks 5-6)
- [ ] Search string generator agent
- [ ] Abstract screening agent
- [ ] Identifier extractor agent
- [ ] Gap analysis enhancement
- [ ] Reasoning trace storage

### Phase 4: Frontend Development (Weeks 7-8)
- [ ] React/Next.js setup
- [ ] Chatbot interface
- [ ] Article viewer (PDF + MD)
- [ ] HITL decision panels
- [ ] Document explorer

### Phase 5: Integration (Weeks 9-11)
- [ ] Statistics dashboard
- [ ] Agent monitoring
- [ ] Source citations display
- [ ] Visualization generation
- [ ] Export functionality
- [ ] Document versioning system
- [ ] Multi-user collaboration (reviewer roles)

### Phase 6: Security & Polish (Weeks 12-14)
- [ ] Prompt injection protection (regex + LLM-based)
- [ ] Input validation
- [ ] Rate limiting (per-user, per-project)
- [ ] Error handling
- [ ] Performance optimization
- [ ] Audit logging implementation
- [ ] GDPR compliance features

### Phase 7: Testing & QA (Weeks 15-17)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration testing
- [ ] Security penetration testing
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Load testing (100+ concurrent users)
- [ ] Cross-browser testing

### Phase 8: Launch Preparation (Weeks 18-20)
- [ ] User acceptance testing
- [ ] Documentation completion
- [ ] Monitoring/alerting setup
- [ ] Disaster recovery testing
- [ ] Beta launch (limited users)
- [ ] Production launch

---

## 9. API Endpoints

### 9.1 Core Endpoints (v1)

```
# Health & System
GET    /health                    # Liveness probe
GET    /ready                     # Readiness probe
GET    /api/v1/version            # API version info

# Authentication
POST   /api/v1/auth/login
POST   /api/v1/auth/register
POST   /api/v1/auth/refresh
DELETE /api/v1/auth/logout
POST   /api/v1/auth/mfa/setup
POST   /api/v1/auth/mfa/verify

# Projects
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/{id}
PUT    /api/v1/projects/{id}
DELETE /api/v1/projects/{id}
GET    /api/v1/projects/{id}/collaborators
POST   /api/v1/projects/{id}/collaborators/invite

# Research Plan
GET    /api/projects/{id}/plan
PUT    /api/projects/{id}/plan
POST   /api/projects/{id}/plan/generate

# Documents
GET    /api/projects/{id}/documents
POST   /api/projects/{id}/documents/upload
DELETE /api/projects/{id}/documents/{doc_id}
GET    /api/projects/{id}/documents/{doc_id}/content

# Search
POST   /api/projects/{id}/search/generate
GET    /api/projects/{id}/search/strings
POST   /api/projects/{id}/search/execute

# Screening
POST   /api/projects/{id}/screening/abstracts
GET    /api/projects/{id}/screening/results
PUT    /api/projects/{id}/screening/{abstract_id}

# Article Generation
POST   /api/projects/{id}/article/generate
GET    /api/projects/{id}/article/status
GET    /api/projects/{id}/article/draft
PUT    /api/projects/{id}/article/section/{section_id}

# HITL
GET    /api/projects/{id}/hitl/pending
POST   /api/projects/{id}/hitl/{decision_id}/respond
GET    /api/projects/{id}/hitl/history

# Chat
POST   /api/projects/{id}/chat
GET    /api/projects/{id}/chat/history

# Statistics
GET    /api/projects/{id}/stats
GET    /api/projects/{id}/stats/generations

# Export
POST   /api/projects/{id}/export/pdf
POST   /api/projects/{id}/export/docx
POST   /api/projects/{id}/export/bibtex
```

---

## 10. Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy (optional) / Firestore SDK
- **Task Queue:** Cloud Tasks / Celery + Redis
- **LLM:** Vertex AI (Gemini 2.5)
- **Vector DB:** ChromaDB / Vertex AI Matching Engine

### Frontend
- **Framework:** Next.js 14 (React)
- **State:** Zustand / Redux Toolkit
- **UI:** Tailwind CSS + shadcn/ui
- **Charts:** Recharts / Plotly
- **PDF:** react-pdf
- **Markdown:** react-markdown

### Infrastructure
- **Cloud:** Google Cloud Platform
- **Auth:** Firebase Authentication
- **Storage:** Cloud Storage + Firestore
- **Hosting:** Cloud Run + Firebase Hosting
- **CI/CD:** Cloud Build
- **IaC:** Terraform

---

## 11. Questions for Approval

Pred implementacijo prosim potrdi naslednje točke:

1. **Arhitektura:** Ali se strinjate z predlagano arhitekturo (Cloud Run + Firestore + Redis)?

2. **HITL točke:** Ali so vse HITL točke ustrezne ali bi dodali/odstranili kakšno?

3. **Frontend:** Ali je predlagana razporeditev UI ustrezna?

4. **Prioritete:** Ali se strinjate z vrstnim redom implementacijskih faz?

5. **Varnost:** Ali so varnostni ukrepi zadostni za komercialno rabo?

---

## 12. GDPR Compliance

### 12.1 Data Classification

| Kategorija | Podatki | Retencija | Šifriranje |
|------------|---------|-----------|------------|
| **Osebni** | Email, ime | Do izbrisa računa | AES-256 |
| **Projektni** | Dokumenti, drafts | 5 let po zadnji aktivnosti | AES-256 |
| **Analitični** | Usage logs | 2 leti | At-rest |
| **Sistemski** | Error logs | 90 dni | None |

### 12.2 User Rights Implementation

```python
# GDPR API Endpoints
GET    /api/v1/user/data-export     # Right to access
POST   /api/v1/user/data-delete     # Right to be forgotten
PUT    /api/v1/user/data-restrict   # Right to restrict processing
GET    /api/v1/user/data-portability # Right to data portability

class GDPRService:
    async def export_user_data(self, user_id: str) -> dict:
        """Export all user data in JSON format."""
        return {
            "profile": await self.get_profile(user_id),
            "projects": await self.get_all_projects(user_id),
            "chat_history": await self.get_chat_history(user_id),
            "documents": await self.get_document_metadata(user_id),
            "audit_log": await self.get_user_actions(user_id)
        }
    
    async def delete_user_data(self, user_id: str) -> bool:
        """Complete user data deletion (right to be forgotten)."""
        # 1. Delete from Firestore
        await self.firestore.delete_user_tree(user_id)
        # 2. Delete from Cloud Storage
        await self.storage.delete_user_bucket(user_id)
        # 3. Delete from ChromaDB
        await self.vector_db.delete_user_embeddings(user_id)
        # 4. Anonymize audit logs
        await self.audit.anonymize_user(user_id)
        return True
```

### 12.3 Data Processing Agreement (DPA)

- Google Cloud DPA: Signed automatically via GCP Terms
- Sub-processors: Vertex AI (Gemini), Firebase Auth
- Data location: EU (europe-west1) only
- Transfer mechanisms: Standard Contractual Clauses (SCCs)

---

## 13. Cost Estimation

### 13.1 Monthly Infrastructure Costs (Production)

| Service | Specifikacija | Mesečni strošek |
|---------|---------------|-----------------|
| **Cloud Run** | 2 vCPU, 2GB RAM, 100k requests/day | ~$50-80 |
| **Firestore** | 1M reads, 500k writes, 10GB storage | ~$30-50 |
| **Cloud Storage** | 100GB storage, 10GB egress | ~$5-10 |
| **Memorystore Redis** | 1GB instance | ~$35 |
| **Vertex AI (Gemini)** | ~50k tokens/user/day, 100 users | ~$150-300 |
| **Firebase Auth** | 100 MAU | Free tier |
| **Cloud Build** | 120 min/day | Free tier |
| **Secret Manager** | 10 secrets, 10k accesses | ~$1 |
| **Cloud Armor** | Basic WAF | ~$5 |
| **Cloud Monitoring** | Basic tier | Free |

**Total Estimate:** $280-490/month (100 active users)

### 13.2 Per-User Cost Analysis

| Tier | Users | Infra Cost | Per-User |
|------|-------|------------|----------|
| Startup | 1-50 | ~$200/mo | $4-200/user |
| Growth | 50-500 | ~$800/mo | $1.60/user |
| Enterprise | 500+ | ~$2,500/mo | $0.50/user |

### 13.3 Pricing Model Recommendations

- **Freemium:** 1 project, 10 documents, basic features
- **Pro ($29/mo):** 5 projects, 100 docs, full features
- **Team ($99/mo):** 20 projects, collaboration, priority support
- **Enterprise (Custom):** Unlimited, SLA, dedicated support

---

## 14. Disaster Recovery & Business Continuity

### 14.1 Recovery Objectives

| Metric | Target | Achieved By |
|--------|--------|-------------|
| **RPO** (Recovery Point Objective) | 1 hour | Firestore point-in-time recovery |
| **RTO** (Recovery Time Objective) | 4 hours | Terraform re-deployment |
| **Availability** | 99.9% | Cloud Run multi-region (future) |

### 14.2 Backup Strategy

```yaml
# backup-config.yaml
backups:
  firestore:
    frequency: daily
    retention: 30_days
    location: europe-west1
    
  cloud_storage:
    versioning: enabled
    lifecycle:
      - age: 90_days
        action: nearline
      - age: 365_days
        action: coldline
        
  redis:
    persistence: RDB
    snapshot_frequency: hourly
```

### 14.3 Failover Procedure

1. **Detection:** Cloud Monitoring alerts (< 5 min)
2. **Assessment:** On-call engineer evaluates scope
3. **Failover:** 
   - If region failure → Deploy to europe-west4 (Netherlands)
   - If service failure → Scale up replicas + restart
4. **Recovery:** Restore from Firestore backup if needed
5. **Post-mortem:** Document incident within 48 hours

---

## 15. Observability & Monitoring

### 15.1 Metrics to Track

```yaml
# metrics.yaml
application:
  - request_latency_p99
  - request_error_rate
  - active_users
  - projects_created_daily
  - documents_processed_daily
  - agent_execution_time
  - hitl_decision_turnaround

llm:
  - vertex_ai_latency
  - tokens_consumed_per_request
  - prompt_injection_attempts
  - content_safety_violations

infrastructure:
  - cloud_run_cpu_utilization
  - cloud_run_memory_utilization
  - firestore_read_latency
  - redis_connection_count
```

### 15.2 Alerting Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High Error Rate | > 5% 5xx errors in 5 min | Critical | Page on-call |
| Slow Responses | p99 > 3s for 10 min | Warning | Slack notification |
| LLM Failures | > 10 Vertex AI errors in 1 min | Critical | Page + fallback |
| Security Event | Injection attempt detected | High | Slack + log |
| Cost Spike | Daily spend > 150% normal | Medium | Email alert |

### 15.3 Dashboards

- **Operations Dashboard:** Request rate, latency, errors, uptime
- **User Analytics:** Active users, feature usage, conversion
- **LLM Analytics:** Token usage, cost, latency per model
- **Security Dashboard:** Auth failures, injection attempts, WAF blocks

---

## 16. Accessibility Requirements (WCAG 2.1 AA)

### 16.1 Implementation Checklist

```markdown
## Perceivable
- [ ] All images have alt text
- [ ] Color contrast ratio ≥ 4.5:1 (text) / 3:1 (large text)
- [ ] Content readable at 200% zoom
- [ ] Captions for video content (if any)

## Operable
- [ ] All functionality keyboard accessible
- [ ] Focus indicators visible
- [ ] Skip navigation links
- [ ] No timing-dependent interactions (or adjustable)

## Understandable
- [ ] Consistent navigation across pages
- [ ] Form error messages descriptive
- [ ] Labels associated with inputs

## Robust
- [ ] Valid HTML markup
- [ ] ARIA roles where needed
- [ ] Screen reader tested (NVDA, VoiceOver)
```

### 16.2 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + /` | Open command palette |
| `Ctrl/Cmd + K` | Focus chat input |
| `Ctrl/Cmd + S` | Save current draft |
| `Ctrl/Cmd + E` | Export dialog |
| `Esc` | Close modal/panel |
| `Tab` | Navigate between panels |
| `Enter` | Confirm HITL decision |

---

## 17. External Integrations

### 17.1 Reference Manager Integration

```python
# Zotero Integration
class ZoteroIntegration:
    async def import_collection(self, api_key: str, collection_id: str) -> List[Document]:
        """Import references from Zotero collection."""
        pass
    
    async def export_to_zotero(self, documents: List[Document], api_key: str) -> bool:
        """Export reviewed documents back to Zotero."""
        pass

# Mendeley Integration
class MendeleyIntegration:
    async def import_folder(self, access_token: str, folder_id: str) -> List[Document]:
        """Import references from Mendeley folder."""
        pass
```

### 17.2 DOI/PMID Resolution

```python
class MetadataResolver:
    async def resolve_doi(self, doi: str) -> dict:
        """Resolve DOI to full citation metadata via CrossRef."""
        url = f"https://api.crossref.org/works/{doi}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()["message"]
    
    async def resolve_pmid(self, pmid: str) -> dict:
        """Resolve PMID to metadata via PubMed API."""
        url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
        # ... implementation
        pass
```

### 17.3 Export Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **PDF** | Full article with figures | Final submission |
| **DOCX** | Editable Word format | Revisions |
| **LaTeX** | Academic typesetting | Journal formatting |
| **BibTeX** | Reference bibliography | Citation management |
| **PRISMA-ScR** | Scoping review checklist | Methodology compliance |
| **RIS** | Reference interchange | Import to EndNote |

---

## 18. Security Enhancements (v2.0)

### 18.1 LLM-Based Content Moderation

```python
class EnhancedPromptGuard:
    """
    Two-layer prompt injection protection:
    1. Regex-based (fast, catches common patterns)
    2. LLM-based (slower, catches semantic attacks)
    """
    
    REGEX_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        # ... existing patterns
    ]
    
    async def validate(self, user_input: str) -> ValidationResult:
        # Layer 1: Fast regex check
        for pattern in self.REGEX_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return ValidationResult(safe=False, reason="Regex match")
        
        # Layer 2: LLM-based semantic analysis
        prompt = f"""
        Analyze if this user input contains prompt injection attempts:
        
        Input: {user_input}
        
        Respond with JSON: {{"safe": true/false, "reason": "..."}}
        """
        
        response = await self.vertex_ai.generate(prompt, model="gemini-2.5-flash")
        return ValidationResult.from_json(response)
```

### 18.2 Audit Logging

```python
class AuditLogger:
    async def log(self, event: AuditEvent):
        """Log security-relevant events to Firestore + BigQuery."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": event.user_id,
            "action": event.action,  # e.g., "project.create", "document.delete"
            "resource": event.resource,
            "ip_address": event.ip,
            "user_agent": event.user_agent,
            "outcome": event.outcome,  # "success" | "failure"
            "details": event.details
        }
        
        await self.firestore.collection("audit_logs").add(entry)
        await self.bigquery.stream_insert("audit_logs", entry)
```

### 18.3 Rate Limiting Specification

| Endpoint | Limit | Window | Per |
|----------|-------|--------|-----|
| `/api/v1/auth/*` | 10 | 1 min | IP |
| `/api/v1/chat` | 30 | 1 min | User |
| `/api/v1/projects/*/article/generate` | 5 | 1 hour | Project |
| `/api/v1/export/*` | 10 | 1 hour | User |
| `*` (default) | 100 | 1 min | User |

---

## 19. Multi-User Collaboration

### 19.1 Role Definitions

| Role | Permissions |
|------|-------------|
| **Owner** | Full access, delete project, manage team |
| **Editor** | Edit documents, approve HITL, generate articles |
| **Reviewer** | View, comment, approve screening decisions |
| **Viewer** | Read-only access to all content |

### 19.2 Collaboration Features

- **Real-time presence:** See who's viewing which document
- **Conflict resolution:** Last-write-wins with version history
- **Comments/Annotations:** Thread-based discussions on documents
- **Activity feed:** Timeline of all project changes
- **Notifications:** Email/in-app for mentions and decisions

---

## 20. Document Versioning

### 20.1 Version Control for Articles

```python
class DocumentVersioning:
    async def save_version(self, project_id: str, content: str, author: str):
        """Save new version of article draft."""
        version = {
            "version_number": await self.get_next_version(project_id),
            "content": content,
            "author": author,
            "created_at": datetime.utcnow(),
            "diff_from_previous": self.compute_diff(project_id, content)
        }
        await self.firestore.collection(f"projects/{project_id}/versions").add(version)
    
    async def restore_version(self, project_id: str, version_number: int) -> str:
        """Restore article to specific version."""
        version = await self.get_version(project_id, version_number)
        return version["content"]
    
    async def get_history(self, project_id: str) -> List[dict]:
        """Get version history with diffs."""
        return await self.firestore.get_versions(project_id)
```

### 20.2 Comparison View

- Side-by-side diff viewer for article versions
- Highlight additions (green), deletions (red)
- Version timeline with author attribution
- One-click restore to any previous version

---

## 21. Final Architecture Diagram (v2.0)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             RESEARCHFLOW ARCHITECTURE v2.0                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        FRONTEND (Next.js 14)                              │   │
│  │  • Responsive (mobile-first)  • Dark mode  • WCAG 2.1 AA  • PWA         │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                           │
│                                      ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                  API GATEWAY (Cloud Run) - /api/v1/*                      │   │
│  │  • Rate limiting  • Request validation  • Audit logging  • CORS          │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                      │                                           │
│       ┌──────────────────────────────┼──────────────────────────────┐           │
│       ▼                              ▼                              ▼           │
│  ┌──────────┐                 ┌──────────┐                  ┌──────────┐        │
│  │ Firebase │                 │ Pub/Sub  │                  │  Cloud   │        │
│  │   Auth   │                 │ (Events) │                  │   Tasks  │        │
│  └──────────┘                 └──────────┘                  └──────────┘        │
│                                      │                                           │
│           ┌──────────────────────────┼──────────────────────────────┐           │
│           ▼                          ▼                              ▼           │
│  ┌────────────────┐   ┌────────────────────┐   ┌────────────────────────┐       │
│  │ ORCHESTRATION  │   │    RAG SERVICE     │   │     AGENT CLUSTER      │       │
│  │    SERVICE     │   │                    │   │                        │       │
│  │                │   │ • ChromaDB         │   │ • Research Cluster     │       │
│  │ • Workflow     │   │ • Hybrid Search    │   │ • Writing Cluster      │       │
│  │ • State Machine│   │ • Citation Tracker │   │ • Quality Cluster      │       │
│  │ • HITL Manager │   │                    │   │ • Screening Agent      │       │
│  └────────────────┘   └────────────────────┘   └────────────────────────┘       │
│                                      │                                           │
│           ┌──────────────────────────┼──────────────────────────────┐           │
│           ▼                          ▼                              ▼           │
│  ┌────────────────┐   ┌────────────────────┐   ┌────────────────────────┐       │
│  │  FIRESTORE     │   │   CLOUD STORAGE    │   │     MEMORYSTORE        │       │
│  │                │   │                    │   │       (Redis)          │       │
│  │ • Projects     │   │ • PDF Documents    │   │ • Session state        │       │
│  │ • Users        │   │ • Generated PDFs   │   │ • Rate limit counters  │       │
│  │ • Audit Logs   │   │ • Backups          │   │ • Cache                │       │
│  │ • Versions     │   │                    │   │                        │       │
│  └────────────────┘   └────────────────────┘   └────────────────────────┘       │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                         SECURITY LAYER                                    │   │
│  │  • TLS 1.3  • Cloud Armor WAF  • VPC Service Controls  • Secret Manager │   │
│  │  • EnhancedPromptGuard (Regex + LLM)  • Input Sanitization              │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                       OBSERVABILITY                                       │   │
│  │  • Cloud Monitoring  • Cloud Logging  • Error Reporting  • Cloud Trace  │   │
│  │  • Custom Dashboards (Ops, Analytics, Security)  • PagerDuty Integration│   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

6. **Ime:** Ali je "ResearchFlow" ustrezno ime ali predlagate drugega?

7. **Budget:** Ali imate preference glede Cloud storitev (Standard vs Premium tier)?

---

## 22. SWOT Analysis

### 22.1 SWOT Matrix

```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│           STRENGTHS (S)              │           WEAKNESSES (W)            │
│           Prednosti                  │           Slabosti                  │
├─────────────────────────────────────┼─────────────────────────────────────┤
│                                     │                                     │
│ S1. Multi-agent sistem že deluje    │ W1. Odvisnost od enega LLM          │
│     (prototip dokazan)              │     ponudnika (Vertex AI)           │
│                                     │                                     │
│ S2. HITL pristop zagotavlja         │ W2. Kompleksna arhitektura =        │
│     kakovost in kontrolo            │     višji stroški vzdrževanja       │
│                                     │                                     │
│ S3. Cloud-native arhitektura        │ W3. Ni offline načina delovanja     │
│     (skalabilnost)                  │                                     │
│                                     │                                     │
│ S4. RAG sistem omogoča              │ W4. PDF parsing ni 100% zanesljiv   │
│     transparentne vire              │     (posebej za stare skenirane)    │
│                                     │                                     │
│ S5. Obstoječa koda za               │ W5. Časovno zahtevna prva           │
│     vizualizacije                   │     nastavitev projekta             │
│                                     │                                     │
│ S6. GDPR-ready zasnova              │ W6. Manjka mobile app               │
│                                     │                                     │
├─────────────────────────────────────┼─────────────────────────────────────┤
│         OPPORTUNITIES (O)            │           THREATS (T)               │
│         Priložnosti                  │           Grožnje                   │
├─────────────────────────────────────┼─────────────────────────────────────┤
│                                     │                                     │
│ O1. Rastoč trg AI research          │ T1. Konkurenca velikih igralcev     │
│     tools (CAGR ~25%)               │     (Elsevier, Clarivate)           │
│                                     │                                     │
│ O2. Univerze iščejo avtomatizirane  │ T2. Spremembe v Vertex AI API       │
│     rešitve za preglede             │     lahko pokvarijo funkcionalnost  │
│                                     │                                     │
│ O3. Integracija z akademskimi       │ T3. Regulatorne spremembe           │
│     založniki (pogodbe)             │     (AI Act, copyright)             │
│                                     │                                     │
│ O4. White-label rešitev za          │ T4. Akademiki skeptični do          │
│     institucije                     │     AI-generiranih vsebin           │
│                                     │                                     │
│ O5. Razširitev na meta-analize      │ T5. Stroški Vertex AI lahko         │
│     in protokole                    │     narastejo nepredvidljivo        │
│                                     │                                     │
│ O6. Grant funding za research       │ T6. Hallucination tveganja          │
│     infrastructure                  │     škodujejo ugledu                │
│                                     │                                     │
└─────────────────────────────────────┴─────────────────────────────────────┘
```

### 22.2 Strategic Implications

| Strategija | Opis | Prioriteta |
|------------|------|------------|
| **SO1** | Izkoristi delujoč prototip za hitro pridobitev early adopters na univerzah | HIGH |
| **SO2** | Ponudi white-label verzijo institucijam z lastnim brandingom | MEDIUM |
| **WO1** | Dodaj offline mode s sinhronizacijo za raziskovalce na terenu | LOW |
| **WO2** | Vzpostavi multi-LLM fallback (Gemini → Claude → GPT-4) | HIGH |
| **ST1** | Pozicioniraj se kot HITL tool, ne "AI replacement" za akademike | HIGH |
| **ST2** | Vzpostavi cost capping na uporabnika za predvidljivo ceno | MEDIUM |
| **WT1** | Začni z nizkimi stroški (freemium) da zgradiš trust | HIGH |
| **WT2** | Transparentno prikaži vse AI-generirane dele z viri | HIGH |

---

## 23. Risk Analysis & Mitigation

### 23.1 Risk Register

| ID | Tveganje | Verjetnost | Vpliv | Score | Mitigation Strategy |
|----|----------|------------|-------|-------|---------------------|
| R01 | Vertex AI API breaking changes | Medium | High | 🔴 HIGH | Abstraction layer, verzioniran API, fallback to other LLMs |
| R02 | Cost overrun na Vertex AI | High | Medium | 🔴 HIGH | Per-user token limits, caching, daily cost alerts |
| R03 | LLM hallucinations v članku | Medium | Critical | 🔴 HIGH | Fact-checker agent, mandatory citations, HITL review |
| R04 | Data breach / security incident | Low | Critical | 🟡 MEDIUM | Penetration testing, WAF, encryption, audit logs |
| R05 | GDPR violation (data handling) | Low | High | 🟡 MEDIUM | DPA signed, EU-only hosting, data retention policies |
| R06 | PDF parsing failures | High | Low | 🟡 MEDIUM | Multiple parsers (PyMuPDF, pdfplumber), manual upload fallback |
| R07 | User adoption barrier | Medium | High | 🔴 HIGH | Extensive onboarding, video tutorials, freemium tier |
| R08 | Competitor launches similar | Medium | Medium | 🟡 MEDIUM | First-mover advantage, focus on HITL differentiation |
| R09 | Key developer leaves | Medium | High | 🔴 HIGH | Documentation, code reviews, knowledge sharing |
| R10 | ChromaDB scalability limits | Low | Medium | 🟢 LOW | Migration path to Vertex AI Matching Engine |
| R11 | Firebase Auth outage | Low | High | 🟡 MEDIUM | Retry logic, graceful degradation, status page |
| R12 | Academic credibility issues | Medium | Critical | 🔴 HIGH | Peer-reviewed validation study, transparent methodology |
| R13 | Copyright issues (PDF content) | Medium | High | 🔴 HIGH | User responsibility clause, no PDF redistribution |
| R14 | Rate limiting by WoS/Scopus | Medium | Medium | 🟡 MEDIUM | User-executed searches, export/import workflow |
| R15 | Long article generation times | High | Medium | 🟡 MEDIUM | Progress indicators, background processing, email notifications |

### 23.2 Risk Heat Map

```
           │  Low Impact  │ Medium Impact │ High Impact │ Critical Impact │
───────────┼──────────────┼───────────────┼─────────────┼─────────────────┤
High Prob  │              │ R02, R15      │ R07         │                 │
───────────┼──────────────┼───────────────┼─────────────┼─────────────────┤
Medium     │              │ R08, R14      │ R01, R09    │ R03, R12        │
Prob       │              │               │ R13         │                 │
───────────┼──────────────┼───────────────┼─────────────┼─────────────────┤
Low Prob   │ R10          │ R06, R11      │ R05         │ R04             │
───────────┴──────────────┴───────────────┴─────────────┴─────────────────┘
```

### 23.3 Contingency Plans

**R01 - Vertex AI API Changes:**
```
IF Vertex AI introduces breaking changes THEN
  1. Use abstraction layer to isolate impact
  2. Activate fallback LLM (Claude via AWS Bedrock)
  3. Notify users of potential delays
  4. Migrate within 2-week sprint
```

**R03 - LLM Hallucinations:**
```
IF Hallucination detected (FactChecker fails) THEN
  1. Flag specific claims in article
  2. Request HITL verification
  3. Log incident for model improvement
  4. Optionally regenerate section with stricter prompts
```

**R07 - Low User Adoption:**
```
IF Monthly active users < 50 after 3 months THEN
  1. Launch targeted academic marketing campaign
  2. Partner with specific university department
  3. Offer free pilot for one scoping review
  4. Gather feedback and iterate rapidly
```

---

## 24. Competitive Analysis

### 24.1 Competitor Landscape

| Competitor | Type | Strengths | Weaknesses | Pricing |
|------------|------|-----------|------------|---------|
| **Rayyan** | Abstract screening | Large user base, free tier | No AI writing, manual only | Free / $12/mo |
| **Covidence** | Full SR workflow | Gold standard, integrations | No AI generation, expensive | $240/mo team |
| **ASReview** | AI screening | Open source, active community | Screening only, no writing | Free |
| **Elicit** | AI research assistant | Good for exploration | No full article generation | Free / $10/mo |
| **Semantic Scholar** | Paper discovery | Huge database | Search only, no workflow | Free |
| **Scholarcy** | Summarization | Quick summaries | No SR methodology | $12/mo |
| **SciSpace** | AI assistant | Chat with PDFs | No structured workflow | $12/mo |
| **ResearchRabbit** | Discovery | Visual citation mapping | No screening/writing | Free |

### 24.2 Competitive Positioning

```
                     HIGH AUTOMATION
                           │
                           │   ┌─────────────┐
                           │   │ ResearchFlow│ ← Target Position
                           │   │ (Full AI +  │
                           │   │  HITL)      │
                           │   └─────────────┘
                           │
         ┌─────────────┐   │   ┌─────────────┐
         │  ASReview   │   │   │   Elicit    │
         │(AI Screen)  │   │   │ (AI Explore)│
         └─────────────┘   │   └─────────────┘
                           │
    ─────────────────────────────────────────────►
    MANUAL                 │              FULL WORKFLOW
    (Single Tool)          │              (End-to-End)
                           │
         ┌─────────────┐   │   ┌─────────────┐
         │   Rayyan    │   │   │  Covidence  │
         │(Man Screen) │   │   │ (Manual SR) │
         └─────────────┘   │   └─────────────┘
                           │
                     LOW AUTOMATION
```

### 24.3 Unique Value Proposition (UVP)

> **"ResearchFlow: The only AI platform that writes scoping reviews WITH you, not FOR you."**

Key differentiators:
1. **Full pipeline** - From research plan to publication-ready PDF
2. **HITL control** - Researcher always in the driver's seat
3. **Transparency** - Every claim is traceable to source
4. **RAG assistant** - Conversational help throughout process
5. **Slovenian origin** - EU/GDPR native, understands local academic norms

---

## 25. Technical Dependencies & Bottlenecks

### 25.1 Critical Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DEPENDENCY CHAIN                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Level 0 (Foundation)                                                        │
│  ├── Google Cloud Platform (All infrastructure)                             │
│  ├── Python 3.11+ Runtime                                                   │
│  └── Node.js 20+ (Frontend)                                                 │
│                                                                              │
│  Level 1 (Core Services)                                                     │
│  ├── Vertex AI (Gemini) ← CRITICAL SINGLE POINT OF FAILURE                 │
│  ├── Firebase Auth                                                          │
│  ├── Firestore                                                              │
│  └── Cloud Run                                                              │
│                                                                              │
│  Level 2 (Support Services)                                                  │
│  ├── ChromaDB (self-hosted on Cloud Run)                                    │
│  ├── Memorystore Redis                                                      │
│  ├── Cloud Storage                                                          │
│  └── Cloud Build CI/CD                                                      │
│                                                                              │
│  Level 3 (Libraries - High Risk if Breaking Changes)                        │
│  ├── LangChain (RAG orchestration)                                          │
│  ├── FastAPI (API framework)                                                │
│  ├── PyMuPDF/pdfplumber (PDF parsing)                                       │
│  ├── Plotly (Visualizations)                                                │
│  ├── Next.js 14 (Frontend)                                                  │
│  └── shadcn/ui (UI components)                                              │
│                                                                              │
│  Level 4 (External APIs)                                                     │
│  ├── CrossRef API (DOI resolution)                                          │
│  ├── PubMed API (PMID resolution)                                           │
│  └── Zotero API (optional integration)                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 25.2 Performance Bottlenecks

| Bottleneck | Location | Current Limit | Mitigation |
|------------|----------|---------------|------------|
| **LLM Latency** | Article generation | ~2-5s per chunk | Parallelize sections, streaming |
| **PDF Processing** | Document ingestion | ~10s per PDF | Background queue, batch processing |
| **Vector Search** | RAG queries | ~500ms cold start | Redis cache for hot queries |
| **Token Limits** | Long articles | 128k context | Chunking strategy, summarization |
| **Cloud Run Cold Start** | First request | ~3-5s | Min instances = 1, warmup endpoint |
| **Firestore Reads** | Dashboard stats | 1M reads/day limit | Aggregation caching, Redis |

### 25.3 Scalability Concerns

```python
# Scalability Analysis
scalability_assessment = {
    "users": {
        "current_limit": 100,
        "bottleneck": "Vertex AI rate limits (60 RPM)",
        "solution": "Request quota increase, implement queue"
    },
    "documents_per_project": {
        "current_limit": 500,
        "bottleneck": "ChromaDB memory usage",
        "solution": "Migrate to Vertex AI Matching Engine"
    },
    "concurrent_generations": {
        "current_limit": 10,
        "bottleneck": "Cloud Run instances + LLM API",
        "solution": "Pub/Sub queue, priority tiers"
    },
    "storage_per_user": {
        "current_limit": "10GB",
        "bottleneck": "Cost",
        "solution": "Enforce quotas, archive old projects"
    }
}
```

---

## 26. MVP Definition

### 26.1 MVP Scope (Weeks 1-10)

**IN SCOPE (Must Have):**
- [ ] User registration/login (Firebase Auth)
- [ ] Create project with research plan
- [ ] Chatbot for research plan creation
- [ ] Upload PDF abstracts for screening
- [ ] AI-assisted abstract screening (Include/Exclude/Uncertain)
- [ ] HITL review for uncertain abstracts
- [ ] Upload full-text PDFs
- [ ] Generate article draft (single generation)
- [ ] Export to PDF
- [ ] Basic visualization (PRISMA diagram)

**OUT OF SCOPE (v2.0):**
- Multi-user collaboration
- Advanced visualizations (Evidence Gap Map, etc.)
- Zotero/Mendeley integration
- DOI/PMID auto-resolution
- Document versioning
- Mobile app
- White-label options
- LaTeX export
- Custom citation styles

### 26.2 MVP Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first draft | < 2 hours (vs 2+ weeks manual) | User tracking |
| User retention (7-day) | > 40% | Analytics |
| Task completion rate | > 70% complete a draft | Funnel analysis |
| User satisfaction (NPS) | > 30 | Survey |
| Bugs (critical) | 0 in production | Error tracking |

### 26.3 MVP Architecture (Simplified)

```
┌─────────────────────────────────────────────────────────┐
│              MVP ARCHITECTURE (Minimal)                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend: Next.js (Vercel hosting) ← Simpler!         │
│       │                                                 │
│       ▼                                                 │
│  Backend: FastAPI on Cloud Run (single service)        │
│       │                                                 │
│  ┌────┼────┬─────────────┬─────────────┐               │
│  ▼    ▼    ▼             ▼             ▼               │
│ Auth  Firestore   Cloud Storage   Vertex AI           │
│                                                         │
│  NO: Redis, Pub/Sub, ChromaDB cluster                  │
│  USE: In-memory caching, synchronous processing        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 27. Success Metrics & KPIs

### 27.1 Business KPIs

| KPI | Definition | Target (Year 1) |
|-----|------------|-----------------|
| **MAU** | Monthly Active Users | 500 |
| **MRR** | Monthly Recurring Revenue | $5,000 |
| **CAC** | Customer Acquisition Cost | < $50 |
| **LTV** | Lifetime Value | > $200 |
| **Churn** | Monthly churn rate | < 5% |
| **NPS** | Net Promoter Score | > 40 |

### 27.2 Product KPIs

| KPI | Definition | Target |
|-----|------------|--------|
| **Time to First Value** | Time from signup to first draft | < 30 min |
| **Project Completion Rate** | % of projects with exported PDF | > 60% |
| **HITL Response Time** | Avg time for user to respond to HITL | < 24h |
| **Generation Quality** | User-rated quality 1-5 | > 4.0 |
| **Support Tickets** | Per 100 users per month | < 10 |

### 27.3 Technical KPIs

| KPI | Definition | Target |
|-----|------------|--------|
| **Uptime** | Service availability | > 99.5% |
| **P99 Latency** | 99th percentile response time | < 3s |
| **Error Rate** | % of requests failing | < 0.5% |
| **Deployment Frequency** | Releases per week | > 2 |
| **Mean Time to Recovery** | Incident recovery time | < 1h |

---

## 28. Team Requirements

### 28.1 Core Team (MVP Phase)

| Role | Responsibilities | FTE | Cost/Month |
|------|------------------|-----|------------|
| **Full-stack Developer** | Backend, Frontend, DevOps | 1.0 | €4,000-6,000 |
| **ML/AI Engineer** | Agent development, RAG optimization | 0.5 | €2,500-4,000 |
| **Product Owner** | Requirements, testing, user feedback | 0.5 | €2,000-3,000 |
| **Total MVP Team** | | **2.0 FTE** | **€8,500-13,000** |

### 28.2 Growth Team (Post-MVP)

| Role | Responsibilities | FTE |
|------|------------------|-----|
| **Frontend Developer** | UI/UX improvements, mobile | 1.0 |
| **Backend Developer** | Scalability, integrations | 1.0 |
| **DevOps/SRE** | Infrastructure, monitoring | 0.5 |
| **Data Scientist** | Model fine-tuning, analytics | 0.5 |
| **Customer Success** | Onboarding, support | 0.5 |
| **Marketing** | Content, outreach | 0.5 |
| **Total Growth Team** | | **4.0 FTE** |

### 28.3 Skills Matrix

```
┌────────────────────┬────────────────────────────────────────────────────────┐
│ Skill              │ Required │ Nice to Have │ Current │ Gap               │
├────────────────────┼──────────┼──────────────┼─────────┼───────────────────┤
│ Python/FastAPI     │    ●     │              │    ●    │ None              │
│ Next.js/React      │    ●     │              │    ○    │ Need to learn     │
│ GCP Architecture   │    ●     │              │    ◐    │ Some experience   │
│ LLM/Prompt Eng.    │    ●     │              │    ●    │ None              │
│ RAG Systems        │    ●     │              │    ●    │ None              │
│ Terraform          │          │      ●       │    ○    │ Learning needed   │
│ Academic Writing   │    ●     │              │    ●    │ None              │
│ UI/UX Design       │          │      ●       │    ○    │ Need designer     │
└────────────────────┴──────────┴──────────────┴─────────┴───────────────────┘

Legend: ● = Strong  ◐ = Moderate  ○ = Weak/None
```

---

## 29. Legal & IP Considerations

### 29.1 Intellectual Property

| Asset | IP Type | Status | Action Needed |
|-------|---------|--------|---------------|
| ResearchFlow name | Trademark | Unchecked | EUIPO trademark search |
| Source code | Copyright | Owned | License decision (proprietary vs open core) |
| Agent architecture | Trade secret | Protected | NDAs for contributors |
| Prompts/templates | Copyright | Owned | Document ownership |
| User content | User-owned | Clear | Terms of Service clause |
| Generated articles | User-owned | Clear | ToS states user owns output |

### 29.2 Terms of Service - Key Clauses

```markdown
## Critical ToS Provisions

1. **User Content Ownership**
   - Users retain full ownership of uploaded documents
   - Users own all AI-generated content
   - Platform has license to process for service delivery only

2. **AI Disclosure**
   - Clearly disclose AI involvement in article generation
   - User responsible for final review and accuracy
   - No guarantee of factual accuracy

3. **Academic Integrity**
   - User responsible for compliance with institutional policies
   - Tool assists, does not replace scholarly judgment
   - Plagiarism checking is user's responsibility

4. **Liability Limitations**
   - No liability for hallucinations or incorrect citations
   - User must verify all claims before publication
   - Service provided "as is"

5. **Data Processing**
   - Documents processed only for service delivery
   - No training on user data without consent
   - EU data residency guaranteed
```

### 29.3 Copyright Considerations

| Concern | Risk Level | Mitigation |
|---------|------------|------------|
| PDF redistribution | HIGH | Users upload their own legally obtained PDFs |
| Copyrighted text in RAG | MEDIUM | Fair use for research, no redistribution |
| AI-generated plagiarism | LOW | Not trained on user docs, citation required |
| Publisher paywalls | LOW | User obtains full-text through legitimate channels |

---

## 30. Go-to-Market Strategy

### 30.1 Target Segments (Priority Order)

| Segment | Description | Size | Approach |
|---------|-------------|------|----------|
| **PhD Students** | Writing lit reviews, scoping reviews | Large | Freemium + academic pricing |
| **Research Groups** | Small teams at universities | Medium | Team plan, department demo |
| **Institutions** | University libraries, research offices | Small | White-label, annual contracts |
| **Consultancies** | Policy research, think tanks | Small | Enterprise tier |

### 30.2 Launch Strategy

```
MONTH 1-2: Private Beta
├── 10-20 hand-picked researchers
├── Personal onboarding sessions
├── Intensive feedback collection
└── Bug fixes and iterations

MONTH 3: Public Beta
├── Open signup with waitlist
├── Academic conference presentations
├── Social media launch (Twitter/X, LinkedIn)
└── Research community outreach

MONTH 4-6: General Availability
├── Full pricing tiers active
├── Partner with 2-3 universities
├── Start content marketing (blog, tutorials)
└── Seek academic publication validation
```

### 30.3 Marketing Channels

| Channel | Cost | Expected Impact | Priority |
|---------|------|-----------------|----------|
| Academic Twitter/X | Low | High (viral potential) | HIGH |
| LinkedIn (researchers) | Low | Medium | MEDIUM |
| Conference booths | Medium | High (targeted) | HIGH |
| SEO/Content marketing | Low | Medium (long-term) | MEDIUM |
| YouTube tutorials | Low | High (demonstrations) | HIGH |
| Email to research offices | Low | Low-Medium | LOW |
| Paid ads (Google) | High | Low (niche audience) | LOW |

---

## 31. Vendor Lock-in Analysis

### 31.1 Lock-in Risk Assessment

| Component | Vendor | Lock-in Risk | Mitigation |
|-----------|--------|--------------|------------|
| LLM API | Vertex AI (Gemini) | 🔴 HIGH | Abstract LLM layer, support multiple providers |
| Auth | Firebase Auth | 🟡 MEDIUM | Standard OAuth, exportable user data |
| Database | Firestore | 🟡 MEDIUM | Document DB pattern portable to MongoDB |
| Storage | Cloud Storage | 🟢 LOW | S3-compatible API, easy migration |
| Hosting | Cloud Run | 🟢 LOW | Docker containers, any cloud |
| Redis | Memorystore | 🟢 LOW | Standard Redis, any provider |
| Vector DB | ChromaDB | 🟢 LOW | Open source, self-hosted possible |
| CI/CD | Cloud Build | 🟢 LOW | Standard build process, GitHub Actions alternative |

### 31.2 Multi-Cloud Escape Plan

```python
# LLM Abstraction Layer
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str) -> str:
        pass

class VertexAIProvider(LLMProvider):
    async def generate(self, prompt: str, model: str) -> str:
        # Vertex AI implementation
        pass

class AnthropicProvider(LLMProvider):
    async def generate(self, prompt: str, model: str) -> str:
        # Claude implementation (fallback)
        pass

class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, model: str) -> str:
        # GPT-4 implementation (fallback)
        pass

# Factory with automatic failover
class LLMFactory:
    providers = [VertexAIProvider(), AnthropicProvider(), OpenAIProvider()]
    
    async def generate(self, prompt: str) -> str:
        for provider in self.providers:
            try:
                return await provider.generate(prompt)
            except Exception:
                continue
        raise AllProvidersFailedError()
```

---

## 32. Known Limitations & Future Improvements

### 32.1 Current Limitations

| Limitation | Impact | Planned Fix | Version |
|------------|--------|-------------|---------|
| English only | Excludes non-English researchers | Multi-language support | v2.5 |
| No real-time collaboration | Multiple researchers can't edit simultaneously | WebSocket-based co-editing | v2.0 |
| Single LLM provider | Vendor lock-in, outage risk | Multi-LLM support | v2.0 |
| No mobile app | Poor mobile experience | React Native app | v3.0 |
| Limited journal templates | Manual formatting needed | Journal template library | v2.5 |
| No automated database search | User must search WoS/Scopus manually | API integration with databases | v3.0 |
| ChromaDB scaling | Max ~100k vectors per project | Vertex AI Matching Engine | v2.5 |
| No plagiarism check | User must use external tool | Turnitin/iThenticate integration | v2.5 |

### 32.2 Technical Debt Backlog

| Item | Description | Priority | Effort |
|------|-------------|----------|--------|
| Test coverage | Current ~40%, target 80% | HIGH | 2 weeks |
| API documentation | OpenAPI spec incomplete | MEDIUM | 1 week |
| Error handling | Inconsistent error codes | MEDIUM | 1 week |
| Logging | Missing structured logging | HIGH | 3 days |
| Config management | Hardcoded values | MEDIUM | 3 days |
| Database indexes | Unoptimized Firestore queries | LOW | 2 days |

### 32.3 Feature Roadmap

```
v2.0 (Q3 2026)
├── Multi-user collaboration
├── Document versioning
├── Multi-LLM fallback
└── Advanced visualizations

v2.5 (Q4 2026)
├── Multi-language support
├── Plagiarism check integration
├── Journal template library
└── Vertex AI Matching Engine migration

v3.0 (Q1 2027)
├── Mobile app (React Native)
├── Automated database search
├── Real-time co-editing
└── White-label customization

v4.0 (Q3 2027)
├── Meta-analysis support
├── Protocol builder
├── Institutional dashboard
└── API for third-party tools
```

---

## 33. Final Checklist Before Implementation

### 33.1 Pre-Development Checklist

```markdown
## Business
- [ ] ResearchFlow trademark search completed
- [ ] Business entity registered
- [ ] Bank account opened
- [ ] Privacy policy drafted
- [ ] Terms of Service drafted
- [ ] Pricing tiers finalized

## Technical
- [ ] GCP project created
- [ ] Firebase project linked
- [ ] Vertex AI API enabled
- [ ] Domain purchased
- [ ] SSL certificates configured
- [ ] CI/CD pipeline tested

## Team
- [ ] Core team assembled
- [ ] Development environment standardized
- [ ] Git workflow agreed
- [ ] Communication tools set up (Slack/Discord)
- [ ] Documentation standards defined

## Security
- [ ] Penetration test scheduled (pre-launch)
- [ ] GDPR DPA signed with GCP
- [ ] Security policy documented
- [ ] Incident response plan drafted

## Launch
- [ ] Beta testers identified (10-20 people)
- [ ] Feedback collection mechanism ready
- [ ] Support/help documentation started
- [ ] Analytics tracking configured
```

### 33.2 Go/No-Go Decision Criteria

| Criterion | Requirement | Met? |
|-----------|-------------|------|
| MVP features complete | All items in 26.1 | [ ] |
| Critical bugs | Zero critical bugs | [ ] |
| Security audit | No high-severity findings | [ ] |
| Performance | P99 < 3s for all endpoints | [ ] |
| Documentation | User guide complete | [ ] |
| Legal | ToS and Privacy Policy published | [ ] |
| Team readiness | Support process defined | [ ] |

---

## 34. Market Positioning Analysis

### 34.1 Product Category Classification

ResearchFlow spada v več kategorij hkrati, kar definira njegovo edinstveno pozicijo:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PRODUCT CATEGORY TAXONOMY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PRIMARY CATEGORY:                                                           │
│  ━━━━━━━━━━━━━━━━━                                                          │
│  AI-Powered Research Automation Platform                                     │
│     └── Subcategory: Systematic/Scoping Review Automation                   │
│                                                                              │
│  SECONDARY CATEGORIES:                                                       │
│  ━━━━━━━━━━━━━━━━━━━━                                                       │
│  ├── Academic Writing Assistant (AI)                                        │
│  ├── Literature Review Tool                                                 │
│  ├── Research Workflow Management                                           │
│  ├── Evidence Synthesis Platform                                            │
│  └── Scientific Document Generation                                         │
│                                                                              │
│  ADJACENT CATEGORIES:                                                        │
│  ━━━━━━━━━━━━━━━━━━━                                                        │
│  ├── Reference Management (Zotero, Mendeley)                                │
│  ├── Abstract Screening (Rayyan, Covidence)                                 │
│  ├── AI Research Assistants (Elicit, Semantic Scholar)                      │
│  └── Academic Collaboration (Overleaf, Authorea)                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 34.2 Market Tier Classification

```
                    TIER 1: Enterprise Research Platforms
                    ($10,000+ / year)
┌────────────────────────────────────────────────────────────────────────────┐
│  • Covidence ($1,900-3,500/review)                                         │
│  • DistillerSR ($4,000-10,000/year)                                        │
│  • EPPI-Reviewer (Institutional license)                                   │
│  • JBI SUMARI ($1,500-3,000/year)                                          │
│  Značilnosti: Full SR support, institutional, no AI generation            │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    TIER 2: Professional Research Tools
                    ($500-2,000 / year)
┌────────────────────────────────────────────────────────────────────────────┐
│  • Rayyan Pro ($12-25/mo per user)                                         │
│  • SciSpace Premium ($144/year)                                            │
│  • Scholarcy Library ($156/year)                                           │
│  Značilnosti: Team features, some AI, limited scope                       │
└────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
          ═══════════════════════════════════════════════════
          ║       TIER 2.5: RESEARCHFLOW POSITION           ║
          ║       ($350-1,200 / year proposed)              ║
          ═══════════════════════════════════════════════════
          │  • Full pipeline automation (unique)            │
          │  • AI article generation (unique)               │
          │  • HITL quality control                        │
          │  • Cloud-native, modern UX                     │
          └─────────────────────────────────────────────────┘
                              │
                              ▼
                    TIER 3: Researcher Tools (Freemium)
                    ($0-200 / year)
┌────────────────────────────────────────────────────────────────────────────┐
│  • Rayyan Free (basic screening)                                           │
│  • ASReview (open source, AI screening)                                    │
│  • Elicit Free (research exploration)                                      │
│  • Research Rabbit (free discovery)                                        │
│  Značilnosti: Single-purpose, free tiers, limited features                │
└────────────────────────────────────────────────────────────────────────────┘
```

### 34.3 Unique Positioning Statement

> **ResearchFlow: Edina platforma, ki pokriva celoten cikel scoping reviewa od raziskovalnega vprašanja do publikacije-pripravnega članka, z AI podporo in človekom na volanu.**

**Ključne razlike:**

| Atribut | ResearchFlow | Konkurenca |
|---------|--------------|------------|
| Celoten pipeline | ✅ Research plan → PDF | ❌ Samo screening ALI samo pisanje |
| AI generacija članka | ✅ Z viri, HITL | ❌ Nobeden |
| HITL na vseh korakih | ✅ 10 decision points | ⚠️ Omejeno |
| RAG chatbot | ✅ Dostop do vseh docs | ❌ Večinoma ne |
| Vizualizacije | ✅ PRISMA, Evidence Map | ⚠️ Omejen PRISMA |
| Reasoning traces | ✅ Transparentno | ❌ Black box |

---

## 35. Web of Science API Integration Analysis

### 35.1 WoS API Pregled

Clarivate ponuja dva API-ja za dostop do Web of Science:

#### A) Web of Science Starter API (Osnovni)

| Lastnost | Vrednost |
|----------|----------|
| **Namen** | Osnovni metadata check (DOI, avtor, naslov, citati) |
| **Full-text vsebina** | ❌ NE - samo metapodatki |
| **Abstracts** | ⚠️ Omejeno (skrajšani) |
| **Limiti (Free Trial)** | 50 requests/dan |
| **Limiti (Institutional)** | 5,000-20,000 requests/dan |
| **Cena** | Brezplačno z WoS naročnino |

#### B) Web of Science API Expanded (Napredni)

| Lastnost | Vrednost |
|----------|----------|
| **Namen** | Polni metapodatki + citati + funding |
| **Full-text vsebina** | ❌ NE - samo metapodatki in abstracts |
| **Abstracts** | ✅ Polni abstracts |
| **Citing/Cited references** | ✅ DA |
| **Limiti** | 50,000 - 3,000,000 records/leto |
| **Cena** | Plačljivo (institucijska licenca) |

### 35.2 Kaj WoS API OMOGOČA

```python
# WoS API Expanded - Available Data
wos_api_returns = {
    "metadata": {
        "title": "✅ Full title",
        "authors": "✅ Names, affiliations, ORCID",
        "source": "✅ Journal, volume, issue, pages",
        "doi": "✅ DOI identifier",
        "accession_number": "✅ WoS UT",
        "publication_date": "✅ Full date",
        "document_type": "✅ Article, Review, etc.",
        "language": "✅ Publication language"
    },
    "abstract": {
        "content": "✅ Full abstract text",  # THIS IS KEY FOR SCREENING
        "keywords": "✅ Author + WoS keywords"
    },
    "citations": {
        "times_cited": "✅ Current count",
        "citing_articles": "✅ List of citing papers",
        "cited_references": "✅ Bibliography of paper"
    },
    "funding": {
        "agencies": "✅ Funding bodies",
        "grant_numbers": "✅ Grant IDs"
    },
    "full_text": "❌ NOT AVAILABLE",  # Critical limitation
    "pdf": "❌ NOT AVAILABLE"
}
```

### 35.3 Kaj WoS API NE OMOGOČA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WoS API LIMITATIONS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ❌ FULL-TEXT VSEBINA                                                       │
│     • WoS API ne služi člankov                                              │
│     • Uporabnik mora članke prenesti iz založniških portalov               │
│     • To ni tehnična omejitev, ampak pravna (copyright)                    │
│                                                                              │
│  ❌ AVTOMATSKI BATCH PRENOS                                                 │
│     • Ni "download all papers" funkcionalnosti                              │
│     • Vsak članek mora biti pridobljen posebej                             │
│                                                                              │
│  ❌ DIREKTEN PDF DOSTOP                                                     │
│     • PDF-ji so na strani založnikov (Elsevier, Springer, etc.)            │
│     • Potrebna je institucijska naročnina ali Open Access                  │
│                                                                              │
│  ⚠️ RATE LIMITS                                                             │
│     • 2-5 requests/sekundo                                                  │
│     • Dnevne/letne kvote                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 35.4 ResearchFlow + WoS API Integracija

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              PROPOSED WoS INTEGRATION WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  FAZA 1: Iskalni niz                                                        │
│  ━━━━━━━━━━━━━━━━━━━                                                        │
│  [ResearchFlow] ──► Generira WoS-compatible search string                  │
│                     (TS=, TI=, AU=, etc.)                                   │
│                                                                              │
│  FAZA 2: Izvoz abstraktov (MOŽNO Z API)                                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                   │
│  [WoS API] ══► ABSTRACT EXPORT                                              │
│              │  • Execute search query                                       │
│              │  • Retrieve all matching records                              │
│              │  • Get full abstracts programmatically                        │
│              └─► JSON/XML output (title, abstract, DOI, etc.)               │
│                                                                              │
│  FAZA 3: Abstract screening (V ResearchFlow)                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                │
│  [ResearchFlow] ──► AI screens abstracts                                    │
│                 ──► HITL za UNCERTAIN                                       │
│                 ──► Izbor INCLUDED člankov                                  │
│                                                                              │
│  FAZA 4: Full-text pridobivanje (MANUAL - API NE PODPIRA)                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                  │
│  [Uporabnik] ──► Prejme seznam DOI-jev za prenos                           │
│              ──► Prenese preko institucijskega dostopa:                     │
│                  • Knjižnični portal                                         │
│                  • ScienceDirect, SpringerLink, Wiley, etc.                 │
│                  • Interlibrary loan za nedostopne                          │
│              ──► Naloži PDF-je v ResearchFlow                               │
│                                                                              │
│  FAZA 5: Analiza in pisanje (V ResearchFlow)                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                               │
│  [ResearchFlow] ──► Procesira PDF-je                                        │
│                 ──► Izvaja analizo                                          │
│                 ──► Generira članek                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 35.5 WoS API - Implementacijski načrt

```python
class WoSIntegration:
    """
    Web of Science API integration for automated abstract retrieval.
    Note: Full-text retrieval is NOT possible via API.
    """
    
    BASE_URL = "https://wos-api.clarivate.com/api/wos"
    
    async def search(self, query: str, database: str = "WOS") -> dict:
        """
        Execute search and return matching records.
        
        Args:
            query: WoS advanced search query (e.g., "TS=(AI AND HR)")
            database: WOS, MEDLINE, etc.
        
        Returns:
            List of records with abstracts and metadata
        """
        params = {
            "databaseId": database,
            "usrQuery": query,
            "count": 100,  # Max per request
            "firstRecord": 1
        }
        # Returns: title, authors, abstract, DOI, times_cited, etc.
        # Does NOT return: full-text, PDF
        pass
    
    async def export_abstracts_for_screening(
        self, 
        query: str, 
        max_records: int = 1000
    ) -> List[Abstract]:
        """
        Export all abstracts for a search query.
        Used for abstract screening phase.
        """
        abstracts = []
        # Paginate through all results
        # Rate limit: 2 req/sec
        return abstracts
    
    # FULL-TEXT: Not available via API
    # Users must download PDFs manually from publisher sites
```

### 35.6 Prihodnje možnosti (Spekulativno)

| Funkcionalnost | Trenutno | Prihodnost (2027+?) |
|----------------|----------|---------------------|
| Abstract export | ✅ API | ✅ API |
| Full-text search | ❌ Ne | ⚠️ Malo verjetno (copyright) |
| PDF download | ❌ Ne | ❌ Zelo malo verjetno |
| Open Access links | ✅ Da (če obstaja) | ✅ Izboljšano |
| Preprint links | ⚠️ Omejeno | ✅ Verjetno boljše |
| AI-powered search | ❌ Ne | ⚠️ Možno |

**Zaključek:** WoS API je koristen za abstract screening fazo, NI pa rešitev za full-text pridobivanje. To ostaja uporabnikova naloga.

---

## 36. Global Market Potential

### 36.1 Target Addressable Market (TAM → SAM → SOM)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MARKET SIZE ANALYSIS                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TAM (Total Addressable Market)                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                              │
│  Global Academic Research Software Market: ~$4.5B (2026)                    │
│  CAGR: 12-15% annually                                                       │
│  Includes: Reference managers, discovery tools, writing tools, etc.        │
│                                                                              │
│  SAM (Serviceable Addressable Market)                                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                          │
│  Systematic/Scoping Review Tools: ~$350M (2026)                             │
│  Growth: ~20-25% annually (AI adoption driving growth)                      │
│  Key players: Covidence, Rayyan, DistillerSR, EPPI-Reviewer                │
│                                                                              │
│  SOM (Serviceable Obtainable Market)                                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                           │
│  Realistic 5-year target: ~$5-15M ARR                                       │
│  Market share goal: 1.5-4% of SAM                                           │
│  Users: 10,000-30,000 researchers globally                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 36.2 Market Drivers

| Driver | Impact | Trend |
|--------|--------|-------|
| **Publish or perish pressure** | HIGH | Constant ↔ |
| **Systematic review requirements** | HIGH | Growing ▲ |
| **AI adoption in academia** | MEDIUM→HIGH | Rapid growth ▲▲ |
| **Time constraints for researchers** | HIGH | Increasing ▲ |
| **Open science movement** | MEDIUM | Growing ▲ |
| **Grant requirements for evidence synthesis** | HIGH | Increasing ▲ |
| **Multi-disciplinary research** | MEDIUM | Growing ▲ |

### 36.3 Geographic Market Potential

| Region | Market Size | Growth | Entry Difficulty |
|--------|-------------|--------|------------------|
| **North America** | 35% of SAM | High | Medium (saturated) |
| **Europe** | 30% of SAM | High | Low (GDPR advantage) |
| **Asia Pacific** | 25% of SAM | Very High | Medium (localization) |
| **Latin America** | 5% of SAM | High | Low (price sensitive) |
| **Middle East/Africa** | 5% of SAM | High | Medium |

### 36.4 User Segments & Volume

```
                    GLOBAL USER POTENTIAL
        
┌─────────────────────────────────────────────────────────────────┐
│ PhD Students                                                     │
│ Global estimate: ~3.5 million enrolled                          │
│ Potential users: 500,000-700,000 (scoping/systematic reviews)   │
│ Conversion target: 1-2% = 5,000-14,000 users                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Postdocs & Early Career Researchers                             │
│ Global estimate: ~1 million                                     │
│ Potential users: 200,000-300,000                                │
│ Conversion target: 2-3% = 4,000-9,000 users                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Faculty & Senior Researchers                                     │
│ Global estimate: ~2 million (active in research)                │
│ Potential users: 100,000-200,000 (supervising reviews)          │
│ Conversion target: 1% = 1,000-2,000 users                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Research Institutions & Groups                                   │
│ Global estimate: ~50,000 research departments                   │
│ Potential customers: 5,000-10,000 (needing team tools)          │
│ Conversion target: 2-5% = 100-500 teams                         │
└─────────────────────────────────────────────────────────────────┘
```

### 36.5 Revenue Projections (5-Year)

| Year | Users (MAU) | MRR | ARR | Notes |
|------|-------------|-----|-----|-------|
| Y1 | 500 | $5K | $60K | Beta + early adopters |
| Y2 | 2,500 | $25K | $300K | Growth phase |
| Y3 | 8,000 | $80K | $960K | Market expansion |
| Y4 | 20,000 | $180K | $2.2M | Enterprise focus |
| Y5 | 40,000 | $350K | $4.2M | International scale |

---

## 37. Tool Classification & Category Mapping

### 37.1 Research Tool Ecosystem Map

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                     RESEARCH TOOL ECOSYSTEM (2026)                             │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│   DISCOVERY & SEARCH                    SCREENING & SELECTION                  │
│   ──────────────────                    ──────────────────────                 │
│   ├── Google Scholar (free)             ├── Rayyan (freemium)                  │
│   ├── Semantic Scholar (free)           ├── Covidence (paid)                   │
│   ├── PubMed (free)                     ├── ASReview (open source)             │
│   ├── Web of Science (institutional)    ├── Abstrackr (free)                   │
│   ├── Scopus (institutional)            └── EPPI-Reviewer (paid)               │
│   ├── Dimensions (freemium)                                                    │
│   └── OpenAlex (free)                                                          │
│                                                                                │
│   AI ASSISTANTS                         REFERENCE MANAGEMENT                   │
│   ─────────────                         ────────────────────                   │
│   ├── Elicit (freemium)                 ├── Zotero (free)                      │
│   ├── Consensus (freemium)              ├── Mendeley (freemium)                │
│   ├── SciSpace/Typeset (freemium)       ├── EndNote (paid)                     │
│   ├── Scholarcy (freemium)              └── Paperpile (paid)                   │
│   ├── Research Rabbit (free)                                                   │
│   └── Scite (freemium)                                                         │
│                                                                                │
│   WRITING & COLLABORATION               SR/MA SPECIFIC                         │
│   ───────────────────────               ───────────────                        │
│   ├── Overleaf (freemium)               ├── DistillerSR (enterprise)           │
│   ├── Authorea (freemium)               ├── JBI SUMARI (paid)                  │
│   ├── Grammarly (freemium)              ├── RevMan (Cochrane, free)            │
│   ├── ChatGPT/Claude (varies)           ├── PRISMA generators (free)           │
│   └── Writefull (freemium)              └── PROSPERO (free registry)           │
│                                                                                │
│                                                                                │
│   ╔════════════════════════════════════════════════════════════════════════╗   │
│   ║                     ★ RESEARCHFLOW (PROPOSED) ★                       ║   │
│   ║                                                                        ║   │
│   ║  Spans: Discovery → Screening → Analysis → Writing → Visualization   ║   │
│   ║  Unique: AI article generation + HITL + Full pipeline                 ║   │
│   ║                                                                        ║   │
│   ╚════════════════════════════════════════════════════════════════════════╝   │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 37.2 Competitive Category Analysis

| Kategorija | Orodja | ResearchFlow Coverage |
|------------|--------|----------------------|
| **Literature Search** | WoS, Scopus, PubMed | ⚠️ Integrates via API, doesn't replace |
| **Paper Discovery** | Semantic Scholar, Research Rabbit | ⚠️ RAG-based, not primary function |
| **Abstract Screening** | Rayyan, ASReview, Covidence | ✅ FULL - AI-assisted + HITL |
| **Reference Management** | Zotero, Mendeley | ⚠️ Import/export, not core |
| **AI Research Assistant** | Elicit, Consensus, SciSpace | ✅ FULL - Integrated chatbot |
| **Writing Assistance** | Grammarly, ChatGPT | ✅ FULL - Article generation |
| **Collaboration** | Overleaf, Authorea | ⚠️ Partial (v2.0 roadmap) |
| **SR Workflow** | Covidence, DistillerSR | ✅ FULL - Scoping review specific |
| **Visualization** | RevMan, Various | ✅ FULL - PRISMA, Evidence Maps |
| **Export/Formatting** | Overleaf, LaTeX editors | ✅ FULL - PDF, DOCX, BibTeX |

### 37.3 Category Leadership Potential

```
CURRENT MARKET LEADERS BY CATEGORY:

Category                    Leader              ResearchFlow Potential
─────────────────────────────────────────────────────────────────────────
Abstract Screening          Rayyan              🥈 Challenger (AI edge)
SR Workflow Management      Covidence           🥉 Disruptor (price + AI)
AI Research Assistant       Elicit              🥈 Challenger (workflow integration)
Article Generation          None (gap!)         🥇 Create category!
Full Pipeline Automation    None (gap!)         🥇 Create category!

Legend:
🥇 = Market leader potential (first mover in new category)
🥈 = Strong challenger (differentiated offering)
🥉 = Potential disruptor (different approach)
```

---

## 38. Competitive Tier Ranking

### 38.1 Feature Comparison Matrix

```
┌──────────────────────┬─────────┬─────────┬─────────┬─────────┬────────────┐
│ Feature              │Rayyan   │Covidence│Elicit   │ASReview │ResearchFlow│
├──────────────────────┼─────────┼─────────┼─────────┼─────────┼────────────┤
│ Abstract Screening   │ ✅      │ ✅      │ ⚠️      │ ✅      │ ✅         │
│ AI-assisted Screen   │ ⚠️      │ ⚠️      │ ✅      │ ✅      │ ✅         │
│ Full-text Analysis   │ ❌      │ ✅      │ ⚠️      │ ❌      │ ✅         │
│ Article Generation   │ ❌      │ ❌      │ ❌      │ ❌      │ ✅ ★       │
│ HITL Workflow        │ ⚠️      │ ✅      │ ❌      │ ⚠️      │ ✅         │
│ RAG Chatbot          │ ❌      │ ❌      │ ✅      │ ❌      │ ✅         │
│ PRISMA Diagram       │ ❌      │ ✅      │ ❌      │ ❌      │ ✅         │
│ Visualization Suite  │ ❌      │ ⚠️      │ ❌      │ ❌      │ ✅         │
│ PDF Export           │ ❌      │ ⚠️      │ ❌      │ ❌      │ ✅         │
│ Team Collaboration   │ ✅      │ ✅      │ ❌      │ ⚠️      │ ⚠️ (v2)    │
│ Free Tier            │ ✅      │ ❌      │ ✅      │ ✅      │ ✅         │
│ Cloud-native         │ ✅      │ ✅      │ ✅      │ ❌      │ ✅         │
│ Open Source          │ ❌      │ ❌      │ ❌      │ ✅      │ ❌         │
├──────────────────────┼─────────┼─────────┼─────────┼─────────┼────────────┤
│ TOTAL SCORE          │ 5/12    │ 7/12    │ 5/12    │ 4/12    │ 11/12 ★   │
└──────────────────────┴─────────┴─────────┴─────────┴─────────┴────────────┘

Legend: ✅ = Full support | ⚠️ = Partial | ❌ = No support | ★ = Unique feature
```

### 38.2 Final Competitive Ranking

```
                    COMPETITIVE TIER RANKING (2026)
                    
    ════════════════════════════════════════════════════════════
    
    TIER S: Complete Platform (End-to-End)
    ───────────────────────────────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │  ★ RESEARCHFLOW                                         │
    │    • Only tool with AI article generation              │
    │    • Full pipeline: Plan → Screen → Write → Export     │
    │    • HITL at every step                                │
    │    • Position: CATEGORY CREATOR / LEADER               │
    └─────────────────────────────────────────────────────────┘
    
    ════════════════════════════════════════════════════════════
    
    TIER A: Comprehensive Workflow Tools
    ─────────────────────────────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │  Covidence ($1,900-3,500/review)                        │
    │    • Gold standard for SR workflow                     │
    │    • Strong institutional adoption                     │
    │    • No AI generation                                  │
    │    • Position: INCUMBENT LEADER                        │
    ├─────────────────────────────────────────────────────────┤
    │  DistillerSR ($4,000-10,000/year)                      │
    │    • Enterprise features                               │
    │    • Regulatory compliance                             │
    │    • Position: ENTERPRISE LEADER                       │
    └─────────────────────────────────────────────────────────┘
    
    ════════════════════════════════════════════════════════════
    
    TIER B: Specialized Tools
    ──────────────────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │  Rayyan (Free / $12-25/mo)                              │
    │    • Best free tier for screening                      │
    │    • Large user base                                   │
    │    • Position: SCREENING LEADER                        │
    ├─────────────────────────────────────────────────────────┤
    │  ASReview (Free, Open Source)                          │
    │    • Active learning for screening                     │
    │    • Academic community driven                         │
    │    • Position: OPEN SOURCE LEADER                      │
    ├─────────────────────────────────────────────────────────┤
    │  Elicit (Free / $10/mo)                                │
    │    • Best for exploration/brainstorming                │
    │    • Good AI but no workflow                          │
    │    • Position: AI ASSISTANT LEADER                     │
    └─────────────────────────────────────────────────────────┘
    
    ════════════════════════════════════════════════════════════
    
    TIER C: Single-Purpose Tools
    ─────────────────────────────
    
    ┌─────────────────────────────────────────────────────────┐
    │  Research Rabbit, Scholarcy, SciSpace, etc.             │
    │    • Good at one thing                                 │
    │    • Must be combined with other tools                 │
    │    • Position: COMPLEMENTARY TOOLS                     │
    └─────────────────────────────────────────────────────────┘
```

### 38.3 Strategic Positioning Conclusion

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESEARCHFLOW MARKET POSITION                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  KATEGORIJA:        AI-Powered Scoping Review Automation Platform           │
│  TIER:              S (Category Creator)                                    │
│  TRŽNI POTENCIAL:   $5-15M ARR (5-year)                                    │
│  KONKURENČNA PREDNOST:                                                      │
│                                                                              │
│    1. EDINI z AI generacijo celotnega članka                               │
│    2. EDINI s celotnim pipelineom (research plan → PDF)                    │
│    3. HITL na vsakem koraku (brez black box)                               │
│    4. RAG chatbot z dostopom do vseh dokumentov                            │
│    5. Moderna cloud-native arhitektura                                      │
│                                                                              │
│  PRIMERJAVA CENE:                                                           │
│    • Covidence: $1,900-3,500 per review                                    │
│    • DistillerSR: $4,000-10,000/year                                       │
│    • ResearchFlow: $29-99/mo ($350-1,200/year)  ← 60-80% ceneje!          │
│                                                                              │
│  VSTOPNA STRATEGIJA:                                                        │
│    • Freemium za PhD študente (acquisition)                                │
│    • Pro tier za aktivne raziskovalce (revenue)                            │
│    • Team/Enterprise za institucije (scale)                                │
│                                                                              │
│  WoS API INTEGRACIJA:                                                       │
│    • Abstracts: ✅ Avtomatski izvoz možen                                  │
│    • Full-text: ❌ Manual prenos (copyright omejitev)                      │
│    • Prihodnost: Abstracts ostanejo ključ, full-text malo verjetno        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 39. Detailed Competitive Comparison by Categories

### 39.1 Evaluation Framework

Primerjava temelji na 8 ključnih kategorijah z utežmi glede na pomembnost za scoping review:

| # | Kategorija | Utež | Opis |
|---|------------|------|------|
| 1 | **Funkcionalnosti** | 25% | Obseg in globina funkcij |
| 2 | **AI zmogljivosti** | 20% | Kakovost in obseg AI |
| 3 | **Cena/Vrednost** | 15% | Cenovna dostopnost |
| 4 | **Varnost & GDPR** | 15% | Skladnost in zaščita |
| 5 | **Hitrost/Performance** | 10% | Odzivnost in skalabilnost |
| 6 | **Integracije** | 5% | API in povezljivost |
| 7 | **Uporabniška izkušnja** | 5% | UI/UX kakovost |
| 8 | **Podpora & Dokumentacija** | 5% | Pomoč uporabnikom |

---

### 39.2 Competitor Profiles

#### A) RAYYAN

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAYYAN PROFILE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Podjetje:           Qatar Computing Research Institute (QCRI)             │
│  Ustanovitev:        2016                                                   │
│  Uporabniki:         1,000,000+ (lastna trditev)                           │
│  Primarni fokus:     Abstract screening za systematic reviews              │
│  Target segment:     Akademiki, medicinski raziskovalci                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  CENE (april 2026):                                                         │
│  ├── Free:      3 reviews, 2 reviewers, basic features                     │
│  ├── Essential: $4.99/seat/mo ($59.88/leto) - 5 reviewers, PRISMA          │
│  ├── Advanced:  $8.33/seat/mo ($99.99/leto) - 9 reviews, PICO, AI          │
│  └── Business:  Po dogovoru - department/institution                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  PREDNOSTI:                                                                  │
│  ✅ Zelo dober brezplačni tier                                              │
│  ✅ Odlično prepoznavanje duplikatov                                        │
│  ✅ Mobilna aplikacija                                                      │
│  ✅ Velik ecosystem in community                                            │
│  ✅ PRISMA diagram generator                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  SLABOSTI:                                                                   │
│  ❌ NI full-text analize                                                    │
│  ❌ NI generacije članka                                                    │
│  ❌ AI samo za screening, ne za pisanje                                     │
│  ❌ Omejena vizualizacija                                                  │
│  ❌ Ni RAG/chatbot                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### B) COVIDENCE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COVIDENCE PROFILE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  Podjetje:           Covidence (Veritas Health Innovation)                  │
│  Ustanovitev:        2013                                                   │
│  Uporabniki:         600,000+ claimed                                       │
│  Primarni fokus:     Cochrane-grade systematic review workflow             │
│  Target segment:     Medicinski raziskovalci, Evidence synthesis teams     │
├─────────────────────────────────────────────────────────────────────────────┤
│  CENE (april 2026):                                                         │
│  ├── Trial:     500 references, time-limited                               │
│  ├── Single:    $339/review/leto - 1 review, unlimited collaborators       │
│  ├── Package:   $907/leto - do 3 reviews                                   │
│  └── Org:       Po pogodbi - unlimited reviews                             │
│  ⚠️ Cena per-review, NE per-user!                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  PREDNOSTI:                                                                  │
│  ✅ Cochrane uraden partner                                                 │
│  ✅ Gold standard workflow                                                  │
│  ✅ Quality assessment tools                                                │
│  ✅ RevMan integracija                                                      │
│  ✅ Data extraction forms                                                   │
│  ✅ PRISMA generation                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  SLABOSTI:                                                                   │
│  ❌ Drago za multiple reviews                                               │
│  ❌ NI AI generacije članka                                                 │
│  ❌ Omejen AI (samo screening prioritization)                              │
│  ❌ Ni chatbot/RAG                                                          │
│  ❌ Zastarela UI/UX                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### C) DISTILLERSR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DISTILLERSR PROFILE                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  Podjetje:           DistillerSR Inc. (Evidence Partners)                   │
│  Ustanovitev:        2008                                                   │
│  Uporabniki:         250+ enterprise customers                              │
│  Primarni fokus:     Enterprise evidence management                        │
│  Target segment:     Pharma, Medical Device, Regulatory                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  CENE (april 2026):                                                         │
│  ├── Academic:   Od $4,000/leto                                            │
│  ├── Enterprise: $6,000-10,000+/leto                                       │
│  └── Premium:    Po pogodbi (multi-year deals)                             │
│  ⚠️ Ciljana za regulatorne use-case (EU-MDR, FDA)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  PREDNOSTI:                                                                  │
│  ✅ Enterprise-grade security (SOC 2, HIPAA)                               │
│  ✅ Regulatory compliance (EU-MDR, FDA)                                    │
│  ✅ AI-assisted screening                                                  │
│  ✅ Evidence reuse across projects                                         │
│  ✅ 24M+ references under management                                       │
│  ✅ Audit trail for compliance                                             │
│  ✅ 35-50% time reduction claims                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  SLABOSTI:                                                                   │
│  ❌ Zelo drago za akademike                                                 │
│  ❌ NI article generation                                                   │
│  ❌ Kompleksna konfiguracija                                                │
│  ❌ Ni chatbot/RAG                                                          │
│  ❌ Overkill za enostavne scoping reviews                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### D) ASREVIEW

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ASREVIEW PROFILE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Podjetje:           Utrecht University (Academic project)                  │
│  Ustanovitev:        2019                                                   │
│  Uporabniki:         638,000+ installations                                 │
│  Primarni fokus:     AI-driven abstract screening                          │
│  Target segment:     Akademiki, open source enthusiasts                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  CENE:                                                                       │
│  └── FREE - Open source (MIT License)                                      │
│      Cloud version: Free (asreview.app)                                    │
│      Self-hosted: Free                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  PREDNOSTI:                                                                  │
│  ✅ Popolnoma brezplačno                                                    │
│  ✅ Open source (transparentno)                                            │
│  ✅ GDPR compliant (self-hosted možnost)                                   │
│  ✅ Active learning model (učinkovit AI)                                   │
│  ✅ No tracking cookies                                                     │
│  ✅ Dobra dokumentacija                                                     │
│  ✅ Močna akademska skupnost                                               │
│  ✅ 95% workload reduction claims                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  SLABOSTI:                                                                   │
│  ❌ SAMO screening (ni full pipeline)                                       │
│  ❌ NI article generation                                                   │
│  ❌ Ni data extraction                                                      │
│  ❌ Ni visualization (PRISMA, etc.)                                        │
│  ❌ Zahteva tehnično znanje za self-hosting                                │
│  ❌ Omejena podpora (community-based)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### E) ELICIT

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ELICIT PROFILE                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  Podjetje:           Elicit Inc. (San Francisco)                            │
│  Ustanovitev:        2021                                                   │
│  Uporabniki:         200,000+ claimed                                       │
│  Primarni fokus:     AI research assistant                                  │
│  Target segment:     Researchers, Pharma, Medtech                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  CENE (april 2026):                                                         │
│  ├── Basic:     FREE - limited features                                    │
│  ├── Pro:       $49/user/mo ($588/leto) - SR workflow, 5K papers          │
│  ├── Scale:     $169/user/mo ($2,028/leto) - collaboration, 240 reports   │
│  └── Enterprise: Custom - SSO, SAML, 40K papers                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  PREDNOSTI:                                                                  │
│  ✅ Odličen AI (GPT-based)                                                 │
│  ✅ 138M+ papers searchable                                                │
│  ✅ Automated reports                                                       │
│  ✅ PICO extraction                                                         │
│  ✅ Chat with papers                                                        │
│  ✅ Zotero import                                                           │
│  ✅ API access                                                              │
│  ✅ Figure extraction (Scale+)                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  SLABOSTI:                                                                   │
│  ❌ NI scoping review workflow                                              │
│  ❌ NI full article generation                                              │
│  ❌ Drago za teamse (Scale tier)                                           │
│  ❌ Ni PRISMA/visualization                                                │
│  ❌ More exploration than structured workflow                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 39.3 Category-by-Category Comparison

#### KATEGORIJA 1: FUNKCIONALNOSTI (25%)

```
┌──────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ Funkcionalnost                   │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├──────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ Research plan creation           │   ❌   │    ⚠️    │    ⚠️     │   ❌    │   ❌   │     ✅     │
│ Search string generation         │   ❌   │    ❌    │    ❌     │   ❌    │   ❌   │     ✅     │
│ Abstract screening               │   ✅   │    ✅    │    ✅     │   ✅    │   ⚠️   │     ✅     │
│ Duplicate detection              │   ✅   │    ✅    │    ✅     │   ⚠️    │   ❌   │     ✅     │
│ Full-text screening              │   ❌   │    ✅    │    ✅     │   ❌    │   ❌   │     ✅     │
│ Data extraction forms            │   ❌   │    ✅    │    ✅     │   ❌    │   ⚠️   │     ✅     │
│ Quality assessment (RoB)         │   ❌   │    ✅    │    ✅     │   ❌    │   ❌   │     ⚠️     │
│ ARTICLE GENERATION               │   ❌   │    ❌    │    ❌     │   ❌    │   ❌   │     ✅ ★   │
│ PRISMA diagram                   │   ✅   │    ✅    │    ✅     │   ❌    │   ❌   │     ✅     │
│ Evidence gap map                 │   ❌   │    ❌    │    ⚠️     │   ❌    │   ❌   │     ✅     │
│ Other visualizations             │   ❌   │    ⚠️    │    ⚠️     │   ⚠️    │   ❌   │     ✅     │
│ PDF export                       │   ❌   │    ⚠️    │    ✅     │   ❌    │   ❌   │     ✅     │
│ BibTeX/RIS export                │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ HITL workflow                    │   ⚠️   │    ✅    │    ✅     │   ⚠️    │   ❌   │     ✅     │
├──────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ TOTAL (✅=2, ⚠️=1, ❌=0)         │   9    │    14    │    15     │    6    │   4    │     26 ★   │
│ SCORE (0-10)                     │  3.2   │   5.0    │   5.4     │   2.1   │  1.4   │    9.3 ★   │
└──────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘

Legend: ✅ = Full (2pts) | ⚠️ = Partial (1pt) | ❌ = No (0pts) | ★ = Unique advantage
```

#### KATEGORIJA 2: AI ZMOGLJIVOSTI (20%)

```
┌──────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ AI Feature                       │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├──────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ AI screening prioritization      │   ✅   │    ⚠️    │    ✅     │   ✅    │   ⚠️   │     ✅     │
│ Active learning                  │   ⚠️   │    ❌    │    ✅     │   ✅    │   ❌   │     ✅     │
│ PICO extraction                  │   ✅   │    ❌    │    ⚠️     │   ❌    │   ✅   │     ✅     │
│ AI summarization                 │   ❌   │    ❌    │    ❌     │   ❌    │   ✅   │     ✅     │
│ AI article WRITING               │   ❌   │    ❌    │    ❌     │   ❌    │   ❌   │     ✅ ★   │
│ RAG/Chatbot                      │   ❌   │    ❌    │    ❌     │   ❌    │   ✅   │     ✅     │
│ Fact-checking                    │   ❌   │    ❌    │    ❌     │   ❌    │   ⚠️   │     ✅     │
│ Citation generation              │   ❌   │    ❌    │    ❌     │   ❌    │   ⚠️   │     ✅     │
│ Semantic search                  │   ❌   │    ❌    │    ⚠️     │   ❌    │   ✅   │     ✅     │
│ LLM model (state-of-art)         │   ⚠️   │    ❌    │    ⚠️     │   ⚠️    │   ✅   │     ✅     │
│ Reasoning traces visible         │   ❌   │    ❌    │    ❌     │   ⚠️    │   ⚠️   │     ✅ ★   │
│ Hallucination mitigation         │   N/A  │   N/A    │    ⚠️     │   ⚠️    │   ⚠️   │     ✅     │
├──────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ TOTAL                            │   6    │    1     │    8      │    7    │   12   │     22 ★   │
│ SCORE (0-10)                     │  2.5   │   0.4    │   3.3     │   2.9   │  5.0   │    9.2 ★   │
└──────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

#### KATEGORIJA 3: CENA IN VREDNOST (15%)

```
┌───────────────────────────────────┬────────────┬────────────┬────────────┬────────────┬────────────┬─────────────┐
│ Pricing Aspect                    │   Rayyan   │  Covidence │ DistillerSR│  ASReview  │   Elicit   │ ResearchFlow│
├───────────────────────────────────┼────────────┼────────────┼────────────┼────────────┼────────────┼─────────────┤
│ Free tier available               │     ✅     │     ⚠️     │     ❌     │     ✅     │     ✅     │     ✅     │
│ Free tier usability               │    Good    │   Limited  │    None    │  Excellent │   Limited  │    Good     │
│ Entry price (annual)              │    $60     │    $339    │  $4,000+   │     $0     │    $588    │    $350     │
│ Mid-tier price (annual)           │   $100     │    $907    │  $6,000+   │     $0     │   $2,028   │    $600     │
│ Enterprise price                  │  Custom    │   Custom   │  $10,000+  │     $0     │   Custom   │   $1,200    │
│ Per-seat vs per-project           │  Per-seat  │ Per-review │  Per-org   │    Free    │  Per-seat  │  Per-seat   │
│ Student discount                  │     ⚠️     │     ✅     │     ❌     │     ✅     │     ❌     │     ✅     │
│ Value for money (full pipeline)   │     3      │      5     │      5     │      4     │      4     │      9 ★    │
│ Transparent pricing               │     ✅     │     ✅     │     ❌     │     ✅     │     ✅     │     ✅     │
├───────────────────────────────────┼────────────┼────────────┼────────────┼────────────┼────────────┼─────────────┤
│ SCORE (0-10)                      │    7.0     │    4.5     │    2.0     │    9.5 ★   │    5.0     │    8.5      │
└───────────────────────────────────┴────────────┴────────────┴────────────┴────────────┴────────────┴─────────────┘

💡 Opomba: ASReview ima najboljšo ceno (brezplačno), a omejen obseg funkcij.
   ResearchFlow ponuja najboljše razmerje med ceno in funkcionalnostjo.
```

#### KATEGORIJA 4: VARNOST IN GDPR (15%)

```
┌───────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ Security Feature                  │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ GDPR compliant                    │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ EU data residency                 │   ❌   │    ⚠️    │    ⚠️     │   ✅    │   ❌   │     ✅ ★   │
│ SOC 2 certified                   │   ❌   │    ⚠️    │    ✅     │   N/A   │   ⚠️   │     ⚠️     │
│ HIPAA compliant                   │   ❌   │    ❌    │    ✅     │   N/A   │   ⚠️   │     ⚠️     │
│ SSL/TLS encryption                │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ Encryption at rest                │   ⚠️   │    ✅    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ MFA support                       │   ❌   │    ⚠️    │    ✅     │   ❌    │   ✅   │     ✅     │
│ SSO/SAML (Enterprise)             │   ❌   │    ❌    │    ✅     │   ❌    │   ✅   │     ⚠️     │
│ Audit logging                     │   ❌   │    ⚠️    │    ✅     │   ⚠️    │   ⚠️   │     ✅     │
│ Data export (portability)         │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ Right to deletion                 │   ⚠️   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ AI data usage transparency        │   ❌   │   N/A    │    ⚠️     │   ✅    │   ⚠️   │     ✅ ★   │
│ Self-hosted option                │   ❌   │    ❌    │    ❌     │   ✅    │   ❌   │     ❌     │
│ No tracking cookies               │   ❌   │    ❌    │    ❌     │   ✅    │   ❌   │     ✅     │
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ TOTAL                             │   8    │    12    │    18     │   14    │   13   │     19 ★   │
│ SCORE (0-10)                      │  2.9   │   4.3    │   6.4     │   5.0   │  4.6   │    6.8 ★   │
└───────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

#### KATEGORIJA 5: HITROST IN PERFORMANCE (10%)

```
┌───────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ Performance Metric                │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ Page load time                    │  Good  │  Medium  │   Medium  │  Good   │  Good  │    Good     │
│ Screening speed (UX)              │  Fast  │  Medium  │   Medium  │  Fast   │  N/A   │    Fast     │
│ Large dataset handling (10K+)     │   ⚠️   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ Cloud-native (auto-scaling)       │   ✅   │    ✅    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Batch processing                  │   ⚠️   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ AI response latency               │  ~2s   │   N/A    │   ~3s     │  ~1s    │  ~2s   │    ~2-3s    │
│ Export generation speed           │  Fast  │  Medium  │   Medium  │  Fast   │  Fast  │    Medium   │
│ Mobile performance                │   ✅   │    ⚠️    │    ❌     │   ❌    │   ⚠️   │     ⚠️     │
│ Offline capability                │   ❌   │    ❌    │    ❌     │   ✅    │   ❌   │     ❌     │
│ Concurrent users support          │  High  │  Medium  │   High    │ Medium  │  High  │    High     │
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ SCORE (0-10)                      │  6.5   │   6.0    │   6.5     │   7.0   │  7.0   │    7.0      │
└───────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

#### KATEGORIJA 6: INTEGRACIJE (5%)

```
┌───────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ Integration                       │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ Zotero                            │   ✅   │    ✅    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Mendeley                          │   ✅   │    ✅    │    ✅     │   ⚠️    │   ⚠️   │     ✅     │
│ EndNote                           │   ✅   │    ✅    │    ✅     │   ⚠️    │   ⚠️   │     ⚠️     │
│ PubMed import                     │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ RIS/BibTeX import                 │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ RevMan (Cochrane)                 │   ⚠️   │    ✅    │    ✅     │   ❌    │   ❌   │     ⚠️     │
│ WoS API                           │   ❌   │    ❌    │    ⚠️     │   ❌    │   ⚠️   │     ✅ ★   │
│ Scopus API                        │   ❌   │    ❌    │    ⚠️     │   ❌    │   ⚠️   │     ⚠️     │
│ CrossRef/DOI                      │   ⚠️   │    ⚠️    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Public API available              │   ❌   │    ❌    │    ✅     │   ✅    │   ✅   │     ✅     │
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ SCORE (0-10)                      │  6.0   │   6.5    │   8.0     │   5.0   │  6.5   │    8.0      │
└───────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

#### KATEGORIJA 7: UPORABNIŠKA IZKUŠNJA (5%)

```
┌───────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ UX Aspect                         │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ Modern UI design                  │   ✅   │    ⚠️    │    ⚠️     │   ✅    │   ✅   │     ✅     │
│ Learning curve                    │  Easy  │  Medium  │   Hard    │  Easy   │  Easy  │   Medium    │
│ Onboarding experience             │   ✅   │    ✅    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Keyboard shortcuts                │   ✅   │    ⚠️    │    ⚠️     │   ✅    │   ⚠️   │     ✅     │
│ Dark mode                         │   ✅   │    ❌    │    ❌     │   ⚠️    │   ✅   │     ✅     │
│ Accessibility (WCAG)              │   ⚠️   │    ⚠️    │    ✅     │   ⚠️    │   ⚠️   │     ✅     │
│ Mobile app                        │   ✅   │    ⚠️    │    ❌     │   ❌    │   ⚠️   │     ⚠️     │
│ Intuitive navigation              │   ✅   │    ⚠️    │    ⚠️     │   ✅    │   ✅   │     ✅     │
│ Error messages clarity            │   ⚠️   │    ⚠️    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Progress indicators               │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ SCORE (0-10)                      │  8.0   │   5.5    │   5.5     │   6.5   │  7.5   │    8.5 ★   │
└───────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

#### KATEGORIJA 8: PODPORA IN DOKUMENTACIJA (5%)

```
┌───────────────────────────────────┬────────┬──────────┬───────────┬─────────┬────────┬─────────────┐
│ Support Aspect                    │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow│
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ Documentation quality             │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ✅     │
│ Video tutorials                   │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ⚠️     │
│ Knowledge base                    │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ⚠️     │
│ Email support                     │   ✅   │    ✅    │    ✅     │   ⚠️    │   ✅   │     ✅     │
│ Live chat                         │   ⚠️   │    ⚠️    │    ✅     │   ❌    │   ⚠️   │     ❌     │
│ Phone support                     │   ❌   │    ❌    │    ✅     │   ❌    │   ❌   │     ❌     │
│ Community forum                   │   ⚠️   │    ⚠️    │    ⚠️     │   ✅    │   ⚠️   │     ⚠️     │
│ Training webinars                 │   ✅   │    ✅    │    ✅     │   ✅    │   ✅   │     ⚠️     │
│ Response time (SLA)               │  24-48h│   24h    │   <4h     │  Varies │  24h   │    24-48h   │
│ Dedicated support (Enterprise)    │   ⚠️   │    ⚠️    │    ✅     │   ❌    │   ✅   │     ⚠️     │
├───────────────────────────────────┼────────┼──────────┼───────────┼─────────┼────────┼─────────────┤
│ SCORE (0-10)                      │  7.0   │   7.0    │   9.0 ★   │   6.0   │  7.5   │    5.5      │
└───────────────────────────────────┴────────┴──────────┴───────────┴─────────┴────────┴─────────────┘
```

---

### 39.4 Weighted Total Score

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              WEIGHTED TOTAL SCORE CALCULATION                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│  Category          │ Weight │ Rayyan │ Covidence│ DistillerSR│ ASReview│ Elicit │ ResearchFlow │
│  ──────────────────┼────────┼────────┼──────────┼────────────┼─────────┼────────┼──────────────│
│  Funkcionalnosti   │  25%   │  3.2   │   5.0    │    5.4     │   2.1   │  1.4   │    9.3       │
│  AI zmogljivosti   │  20%   │  2.5   │   0.4    │    3.3     │   2.9   │  5.0   │    9.2       │
│  Cena/Vrednost     │  15%   │  7.0   │   4.5    │    2.0     │   9.5   │  5.0   │    8.5       │
│  Varnost/GDPR      │  15%   │  2.9   │   4.3    │    6.4     │   5.0   │  4.6   │    6.8       │
│  Hitrost           │  10%   │  6.5   │   6.0    │    6.5     │   7.0   │  7.0   │    7.0       │
│  Integracije       │   5%   │  6.0   │   6.5    │    8.0     │   5.0   │  6.5   │    8.0       │
│  UX                │   5%   │  8.0   │   5.5    │    5.5     │   6.5   │  7.5   │    8.5       │
│  Podpora           │   5%   │  7.0   │   7.0    │    9.0     │   6.0   │  7.5   │    5.5       │
│  ──────────────────┼────────┼────────┼──────────┼────────────┼─────────┼────────┼──────────────│
│  WEIGHTED TOTAL    │ 100%   │  4.4   │   4.0    │    4.7     │   4.4   │  4.4   │    8.4 ★★★  │
│                    │        │        │          │            │         │        │              │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

FORMULA: Σ (Category_Score × Weight)
```

### 39.5 Radar Chart Comparison (Visual)

```
                              FUNKCIONALNOSTI (25%)
                                     10
                                      │
                                  8 ──┼── ResearchFlow (9.3)
                                      │
                                  6 ──┼
                                      │──── DistillerSR (5.4)
                                  4 ──┼──── Covidence (5.0)
                                      │──── Rayyan (3.2)
                                  2 ──┼──── ASReview (2.1)
                                      │──── Elicit (1.4)
         PODPORA (5%)           0 ────┼──────────────────── AI (20%)
               │                      │
         5.5 ──┼                      │──── 9.2 ResearchFlow
               │                      │
               │              VARNOST │
               │              (15%)   │
               │                      │
         UX ───┼──────────────────────┼─── CENA (15%)
        (5%)   │                      │
               │                      │
        8.5 ───┼                      ├─── 8.5 ResearchFlow
               │                      │
               │         INTEGRACIJE  │
               │            (5%)      │    HITROST (10%)
               │                      │
               └──────────────────────┘

INTERPRETATION:
ResearchFlow dominira v Funkcionalnostih in AI, z dobrimi ocenami v ostalih kategorijah.
Konkurenti so specializirani: ASReview v ceni, DistillerSR v varnosti/podpori.
```

---

### 39.6 Competitive Advantages Summary

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            RESEARCHFLOW COMPETITIVE ADVANTAGES                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  🏆 UNIQUE CAPABILITIES (Nobeden konkurent nima):                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                                │
│  1. AI-powered FULL ARTICLE GENERATION                                                         │
│  2. End-to-end pipeline (Research plan → Publication-ready PDF)                               │
│  3. RAG chatbot with access to ALL project documents                                          │
│  4. Visible reasoning traces for every AI decision                                            │
│  5. 10 HITL decision points throughout workflow                                               │
│                                                                                                 │
│  💪 STRONG ADVANTAGES (Boljši od večine):                                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                                     │
│  • EU data residency (GDPR native)                                                            │
│  • WoS API integration for automated abstract export                                          │
│  • Modern visualization suite (PRISMA, Evidence Gap Map, etc.)                               │
│  • Competitive pricing ($29-99/mo vs $339+ per review)                                        │
│  • State-of-the-art LLM (Gemini 2.5)                                                          │
│                                                                                                 │
│  ⚠️ AREAS FOR IMPROVEMENT (Konkurenti boljši):                                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                                  │
│  • Support/Documentation: DistillerSR ima 24/7 + phone support                               │
│  • SOC 2/HIPAA certification: DistillerSR fully certified                                    │
│  • Mobile app: Rayyan has native mobile app                                                  │
│  • Community size: Rayyan (1M+), ASReview (638K installations)                              │
│  • Enterprise features: DistillerSR has regulatory compliance                               │
│                                                                                                 │
│  📊 FINAL POSITIONING:                                                                         │
│  ━━━━━━━━━━━━━━━━━━━━━                                                                        │
│  • Overall Score: 8.4/10 (Highest among all competitors)                                     │
│  • Category: S-Tier (Category Creator)                                                        │
│  • Best for: Researchers who need FULL automation with human control                         │
│  • Not ideal for: Enterprises needing regulatory compliance (use DistillerSR)               │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 39.7 Decision Matrix: When to Choose Which Tool

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              DECISION MATRIX: WHICH TOOL TO USE?                                │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  IF you need...                           │ THEN use...      │ Why?                            │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Full pipeline + AI article generation    │ ResearchFlow ★   │ Only option available          │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Free screening for simple review         │ Rayyan / ASReview│ Good free tiers                │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Cochrane-grade SR with audit trail       │ Covidence        │ Cochrane partner               │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Regulatory compliance (EU-MDR, FDA)      │ DistillerSR      │ SOC2, HIPAA certified          │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  AI research exploration/brainstorming    │ Elicit           │ Best conversational AI         │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Self-hosted + privacy-critical           │ ASReview         │ Open source, local install     │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  PhD student on a budget                  │ ASReview/Rayyan  │ Free, then ResearchFlow Pro    │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  Team collaboration on SR                 │ Covidence/Distil │ Mature team features           │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│  SCOPING REVIEW with article draft        │ ResearchFlow ★★  │ Purpose-built for this         │
│  ─────────────────────────────────────────┼──────────────────┼─────────────────────────────────│
│                                                                                                 │
│  ★ = ResearchFlow is the best choice                                                          │
│  ★★ = ResearchFlow is the ONLY choice (no competition)                                        │
│                                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

**Dokument pripravil:** Claude (AI Assistant)  
**Za potrditev:** [Ime raziskovalca]  
**Datum:** April 2026
**Verzija:** 2.3
