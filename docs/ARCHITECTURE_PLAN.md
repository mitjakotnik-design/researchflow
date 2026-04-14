# ResearchFlow: AI-Powered Scoping Review Platform

## Architecture & Implementation Plan

**Version:** 1.0  
**Date:** April 2026  
**Status:** PENDING APPROVAL

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

### Phase 5: Integration (Weeks 9-10)
- [ ] Statistics dashboard
- [ ] Agent monitoring
- [ ] Source citations display
- [ ] Visualization generation
- [ ] Export functionality

### Phase 6: Security & Polish (Weeks 11-12)
- [ ] Prompt injection protection
- [ ] Input validation
- [ ] Rate limiting
- [ ] Error handling
- [ ] Performance optimization

### Phase 7: Testing & Launch (Weeks 13-14)
- [ ] Integration testing
- [ ] User acceptance testing
- [ ] Documentation completion
- [ ] Beta launch
- [ ] Monitoring setup

---

## 9. API Endpoints

### 9.1 Core Endpoints

```
# Authentication
POST   /api/auth/login
POST   /api/auth/register
POST   /api/auth/refresh
DELETE /api/auth/logout

# Projects
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PUT    /api/projects/{id}
DELETE /api/projects/{id}

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

6. **Ime:** Ali je "ResearchFlow" ustrezno ime ali predlagate drugega?

7. **Budget:** Ali imate preference glede Cloud storitev (Standard vs Premium tier)?

---

**Dokument pripravil:** Claude (AI Assistant)  
**Za potrditev:** [Ime raziskovalca]  
**Datum:** April 2026
