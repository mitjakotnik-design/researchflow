# ResearchFlow: AI-Powered Scoping Review Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Ready-4285F4.svg)](https://cloud.google.com/)

AI-powered multi-agent system for automated scientific literature review article generation with human-in-the-loop decision making.

## 🎯 Overview

ResearchFlow is a commercial platform that assists researchers in writing scoping review and systematic review articles. The platform uses a multi-agent AI system with integrated Human-in-the-Loop (HITL) approach where **the researcher guides the tool, not the other way around**.

### Key Features

- **Chatbot-guided Research Planning** - Create research plans through conversation
- **Automated Search String Generation** - WoS, Scopus, PubMed formats
- **HITL Decision Points** - Human confirmation at critical stages
- **Transparent Operation** - Full visibility into agent work, statistics, sources
- **RAG-powered Assistant** - Chatbot with access to all documents and reasoning traces
- **Cloud-native Architecture** - Google Cloud with authentication and security

## 📁 Project Structure

```
researchflow/
├── agents/                     # AI Agent implementations
│   ├── research_cluster/       # Research-focused agents
│   │   ├── researcher.py       # Main research coordinator
│   │   ├── literature_scout.py # Document discovery
│   │   ├── data_extractor.py   # Data extraction from papers
│   │   ├── meta_analyst.py     # Meta-analysis
│   │   └── gap_identifier.py   # Research gap analysis
│   │
│   ├── writing_cluster/        # Writing-focused agents
│   │   ├── writer.py           # Article section writer
│   │   ├── synthesizer.py      # Literature synthesis
│   │   ├── academic_editor.py  # Academic style editing
│   │   ├── citation_manager.py # Citation formatting
│   │   └── visualizer.py       # Visualization generation
│   │
│   └── quality_cluster/        # Quality assurance agents
│       ├── multi_evaluator.py  # Multi-dimensional evaluation
│       ├── fact_checker.py     # Claim verification
│       ├── consistency_checker.py # Internal consistency
│       ├── bias_auditor.py     # Bias detection
│       └── critic.py           # Constructive criticism
│
├── config/                     # Configuration
│   ├── models_config.py        # LLM model settings
│   ├── quality_thresholds.py   # Quality score thresholds
│   ├── sections_config.py      # Article section definitions
│   └── state_manager.py        # State persistence
│
├── core/                       # Core infrastructure
│   ├── container.py            # Dependency injection
│   ├── interfaces.py           # Abstract interfaces
│   ├── rate_limiter.py         # API rate limiting
│   └── retry.py                # Retry mechanisms
│
├── orchestration/              # Workflow orchestration
│   ├── meta_orchestrator.py    # Main workflow coordinator
│   └── saturation_loop.py      # Iterative improvement loop
│
├── rag/                        # Retrieval Augmented Generation
│   ├── hybrid_search.py        # Hybrid search (semantic + BM25)
│   ├── query_decomposer.py     # Query decomposition
│   └── reranker.py             # Result reranking
│
├── scripts/                    # Utility scripts
│   ├── ingest_documents.py     # Document ingestion
│   ├── create_modern_visualizations.py  # Chart generation
│   ├── export_article_with_figures.py   # PDF export
│   └── generate_full_article.py         # Article generation
│
├── data/                       # Data storage
│   ├── raw_literature/         # Original PDFs
│   ├── processed_literature/   # Processed documents
│   ├── chroma/                 # Vector database
│   ├── states/                 # Workflow states
│   └── checkpoints/            # Processing checkpoints
│
├── output/                     # Generated outputs
│   ├── drafts/                 # Article drafts
│   ├── figures/                # Basic visualizations
│   ├── figures_modern/         # Modern Plotly visualizations
│   ├── final/                  # Final articles
│   └── logs/                   # Execution logs
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE_PLAN.md    # System architecture
│   └── API.md                  # API documentation
│
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Cloud account with Vertex AI enabled
- ChromaDB for vector storage

### Installation

```bash
# Clone the repository
git clone https://github.com/[your-org]/researchflow.git
cd researchflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Create a `.env` file:

```env
# Google Cloud
USE_VERTEX_AI=true
GCP_PROJECT=your-project-id
GCP_REGION=europe-west1

# Or use API key
# GOOGLE_API_KEY=your-api-key

# ChromaDB (optional, defaults to local)
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### Usage

#### 1. Ingest Documents

```bash
# Ingest PDF documents into vector database
python main.py ingest --documents /path/to/pdfs
```

#### 2. Generate Article

```bash
# Generate scoping review article
python main.py generate --topic "HR and AI Workplace Transformation"
```

#### 3. Create Visualizations

```bash
# Generate modern visualizations
python scripts/create_modern_visualizations.py
```

#### 4. Export to PDF

```bash
# Export article with figures
python scripts/export_article_with_figures.py
```

## 📊 Current Capabilities

### Implemented Features

| Feature | Status | Description |
|---------|--------|-------------|
| Document Ingestion | ✅ | PDF to vector DB ingestion |
| Hybrid RAG Search | ✅ | Semantic + BM25 search |
| Multi-Agent Generation | ✅ | 17 specialized agents |
| Quality Evaluation | ✅ | Multi-dimensional scoring |
| Saturation Loop | ✅ | Iterative improvement |
| Modern Visualizations | ✅ | Plotly-based charts |
| PDF Export | ✅ | Publication-ready PDFs |
| Citation Management | ✅ | APA 7th edition |

### Generated Visualizations

1. **PRISMA Flow Diagram** - Study selection process (Sankey)
2. **Conceptual Model** - HR as mediator network diagram
3. **Technostress Dimensions** - Lollipop chart
4. **HR Interventions** - Dumbbell chart
5. **Study Characteristics** - Sunburst chart
6. **Geographic Distribution** - Choropleth map
7. **Publication Timeline** - Trend analysis
8. **Keywords Cloud** - Word cloud
9. **Evidence Gap Map** - Heatmap matrix

## 🏗️ Architecture

### Agent Clusters

```
┌─────────────────────────────────────────────────────────────┐
│                    META ORCHESTRATOR                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RESEARCH CLUSTER     WRITING CLUSTER     QUALITY CLUSTER   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │ Researcher  │     │   Writer    │     │ Evaluator   │    │
│  │ Scout       │     │ Synthesizer │     │ FactChecker │    │
│  │ Extractor   │     │   Editor    │     │ Consistency │    │
│  │ Analyst     │     │  Citation   │     │ BiasAuditor │    │
│  │ GapFinder   │     │ Visualizer  │     │   Critic    │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                      RAG SYSTEM                              │
│   Hybrid Search │ Query Decomposer │ Reranker               │
├─────────────────────────────────────────────────────────────┤
│                     VECTOR DB (ChromaDB)                     │
└─────────────────────────────────────────────────────────────┘
```

### Saturation Loop

The system uses an iterative improvement loop:

```
Write Section → Evaluate → Check Facts → Check Consistency
       ↑                                        │
       │         < Quality Threshold?           │
       └────────────── Yes ←───────────────────┘
                        │
                       No
                        ↓
                 Section Complete
```

## 📈 Sample Output

### Generated Article Statistics

- **Word Count:** ~7,500 words
- **Sections:** 5 main sections
- **Figures:** 8 visualizations
- **References:** 26 citations (APA 7th)
- **Quality Score:** 87%+

### Sample PRISMA Flow

```
Database Records (n=2,847) ─┐
                           ├─► Total (n=3,003) ─► After Duplicates (n=2,156)
Other Sources (n=156) ─────┘                            │
                                                        ▼
                                         Title/Abstract Screening
                                                        │
                                    ┌───────────────────┴───────────────────┐
                                    ▼                                       ▼
                            Excluded (n=1,842)                    Full-text (n=314)
                                                                           │
                                                        ┌──────────────────┴──────────────────┐
                                                        ▼                                      ▼
                                                Excluded (n=247)                    Included (n=67)
```

## 🔒 Security

- Vertex AI with service account authentication
- No API keys stored in code
- Input sanitization for all user inputs
- Rate limiting on API calls
- Audit logging enabled

## 🗺️ Roadmap

See [ARCHITECTURE_PLAN.md](docs/ARCHITECTURE_PLAN.md) for the complete implementation plan.

### Phase 1: Foundation ✅
- [x] Multi-agent system
- [x] RAG implementation
- [x] Quality evaluation
- [x] Visualization generation

### Phase 2: Cloud Migration (In Progress)
- [ ] Google Cloud deployment
- [ ] Authentication system
- [ ] API Gateway

### Phase 3: Frontend (Planned)
- [ ] Chatbot interface
- [ ] HITL decision panels
- [ ] Real-time monitoring

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 👥 Authors

- **Rania Ayache** - Alma Mater Europaea University

## 🙏 Acknowledgments

- Google Vertex AI for LLM capabilities
- ChromaDB for vector search
- Plotly for visualizations
