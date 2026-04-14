"""Generate a complete scoping review article using existing vector database."""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import vertexai
from agents.agent_factory import AgentFactory
from config import ModelsConfig, StateManager, QualityThresholds
from agents.base_agent import AgentContext
from rag.hybrid_search import HybridSearch
from agents.consistency_validator import ConsistencyValidatorAgent


# Canonical values from research plan (SINGLE SOURCE OF TRUTH)
CANONICAL_VALUES = {
    "timeframe_start": "2015",
    "timeframe_end": "2025",
    "timeframe_full": "2015-2025",
    "timeframe_text": "January 2015 and December 2025",
    "methodology": "scoping review",
    "guidelines": "PRISMA-ScR",
    "databases": "Web of Science, Scopus, PubMed, PsycINFO, Business Source Complete",
    "languages": "English, Slovenian, German",
}


# Article configuration
ARTICLE_CONFIG = {
    "title": "From Technostress to Organizational Resilience: The Critical Role of HR in AI-Driven Workplace Transformation",
    "article_id": "scoping_review_hr_ai_2026",
    "target_journal": "Journal of Occupational Health Psychology",
    "language": "en",
    "sections": [
        {
            "id": "abstract",
            "name": "Abstract",
            "min_words": 250,
            "max_words": 350,
            "guidelines": f"""Write a structured abstract with: Background (context and importance), 
            Objective (main research question), Methods (scoping review methodology, databases, inclusion criteria),
            Results (key findings on psychosocial risks, HR role, organizational culture), 
            Conclusions (implications for practice and research). Follow PRISMA-ScR guidelines.
            
            IMPORTANT: The timeframe for this review is {CANONICAL_VALUES['timeframe_full']} 
            (published between {CANONICAL_VALUES['timeframe_text']}). Use this EXACT timeframe.""",
            "avoid": "Do not include citations. Avoid vague statements. Do NOT use any other timeframe than 2015-2025."
        },
        {
            "id": "introduction",
            "name": "Introduction",
            "min_words": 800,
            "max_words": 1200,
            "guidelines": """Structure the introduction:
            1. Opening: The rapid adoption of AI in workplaces and its dual nature (opportunities and risks)
            2. Technostress concept: Define and explain techno-overload, techno-complexity, techno-insecurity
            3. HR's critical role: Why HR is central to managing AI implementation
            4. Organizational culture: How culture moderates AI's impact on employees
            5. Knowledge gap: The lack of integrated understanding
            6. Research objectives: State the main research question and sub-questions
            Use theoretical frameworks: JD-R Model, Conservation of Resources Theory, Self-Determination Theory.""",
            "avoid": "Avoid being too broad. Do not oversimplify the relationship between AI and stress."
        },
        {
            "id": "methods",
            "name": "Methods",
            "min_words": 600,
            "max_words": 900,
            "guidelines": f"""Follow PRISMA-ScR guidelines strictly:
            1. Protocol and Registration
            2. Eligibility Criteria (PCC framework: Population, Concept, Context)
            3. Information Sources (databases: {CANONICAL_VALUES['databases']})
            4. Search Strategy (describe search terms, Boolean operators)
            5. Selection of Sources (two independent reviewers, pilot testing)
            6. Data Charting Process (extraction variables)
            7. Data Items (author, year, methodology, sample, key findings)
            8. Critical Appraisal (quality assessment approach)
            9. Synthesis of Results (thematic analysis)
            
            CRITICAL: Timeframe is EXACTLY {CANONICAL_VALUES['timeframe_full']} 
            (published between {CANONICAL_VALUES['timeframe_text']}). 
            Languages: {CANONICAL_VALUES['languages']}.""",
            "avoid": "Do not skip any PRISMA-ScR elements. Do not use vague methodology descriptions. Do NOT use any other timeframe than 2015-2025."
        },
        {
            "id": "results",
            "name": "Results",
            "min_words": 1500,
            "max_words": 2500,
            "guidelines": """Present results thematically:
            1. Study Selection: PRISMA flow diagram description (records identified, screened, included)
            2. Study Characteristics: Geographic distribution, methodologies, sectors
            3. Theme 1 - Technostress Manifestations: 
               - Techno-overload, techno-complexity, techno-insecurity
               - Prevalence and severity findings
            4. Theme 2 - HR's Role in AI Implementation:
               - Training and upskilling programs
               - Change management strategies
               - Communication approaches
            5. Theme 3 - Organizational Culture as Moderator:
               - Digital climate and leadership
               - Trust and transparency
               - Supportive vs. performance-focused cultures
            6. Theme 4 - Psychosocial Risk Factors:
               - Job autonomy loss
               - Role ambiguity
               - Surveillance and algorithmic management
            7. Theme 5 - Interventions and Mitigation:
               - Organizational-level interventions
               - Team-level interventions
               - Individual coping strategies
            Include specific findings with citations.""",
            "avoid": "Do not interpret results here. Do not mix discussion with results."
        },
        {
            "id": "discussion",
            "name": "Discussion",
            "min_words": 1200,
            "max_words": 1800,
            "guidelines": """Structure the discussion:
            1. Summary of Main Findings: Synthesize key results
            2. Theoretical Implications:
               - How findings relate to JD-R Model
               - Conservation of Resources perspective
               - Self-Determination Theory implications
               - Socio-Technical Systems insights
            3. Comparison with Existing Literature:
               - Where our findings align with previous research
               - Where they diverge and why
            4. The Critical Role of HR:
               - HR as bridge between technology and people
               - Strategic vs. operational HR functions
               - HR competencies needed for AI era
            5. Organizational Culture:
               - Culture as protective or risk factor
               - Digital culture maturity
            6. Limitations:
               - Heterogeneity of studies
               - Geographic and sector bias
               - Publication bias
            7. Future Research Directions:
               - Longitudinal studies needed
               - Intervention effectiveness research
               - Context-specific studies""",
            "avoid": "Do not introduce new data. Do not overstate conclusions."
        },
        {
            "id": "conclusion",
            "name": "Conclusion",
            "min_words": 300,
            "max_words": 500,
            "guidelines": """Provide a concise conclusion:
            1. Restate the main research question
            2. Summarize key findings (3-4 bullet points)
            3. Practical implications for HR professionals
            4. Policy implications (EU AI Act, OSH regulations)
            5. Final statement on organizational resilience through HR leadership""",
            "avoid": "Do not introduce new information. Do not be vague."
        }
    ]
}


async def generate_article():
    """Generate complete scoping review article."""
    
    project = os.getenv("GCP_PROJECT")
    location = os.getenv("GCP_LOCATION", "us-central1")
    
    print("=" * 70)
    print(f"GENERATING SCOPING REVIEW ARTICLE")
    print(f"Title: {ARTICLE_CONFIG['title']}")
    print("=" * 70)
    
    # Initialize Vertex AI
    print("\n[1/5] Initializing Vertex AI...")
    vertexai.init(project=project, location=location)
    
    # Initialize components
    print("[2/5] Loading existing vector database...")
    state_manager = StateManager()
    
    # Create article state
    state_manager.create_new_article(
        article_id=ARTICLE_CONFIG["article_id"],
        title=ARTICLE_CONFIG["title"],
        target_journal=ARTICLE_CONFIG["target_journal"],
        language=ARTICLE_CONFIG["language"]
    )
    
    models_config = ModelsConfig()
    quality_thresholds = QualityThresholds()
    
    # Load existing RAG (using existing database!)
    rag = HybridSearch(
        collection_name="scoping_review_articles",
        persist_directory="data/chroma",
        embedding_model="textembedding-gecko@003"
    )
    rag.initialize()
    print(f"    Loaded {rag._collection.count()} document chunks from existing database")
    
    async def rag_query(query: str, top_k: int = 15, filters: dict = None) -> list[dict]:
        results = await rag.search(query, top_k=top_k, filters=filters)
        return [r.to_dict() for r in results]
    
    context = AgentContext(
        state_manager=state_manager,
        models_config=models_config,
        quality_thresholds=quality_thresholds,
        rag_query=rag_query,
        verbose=True
    )
    
    factory = AgentFactory()
    
    # Generate each section
    print("[3/5] Generating article sections...")
    article_content = {}
    
    for section in ARTICLE_CONFIG["sections"]:
        print(f"\n  Writing {section['name']}...")
        
        # Research phase
        researcher = factory.create_v1("researcher")
        researcher.initialize(context)
        
        # Generate research queries based on section
        research_queries = _get_research_queries(section["id"])
        
        research_result = await researcher.execute(
            action="research",
            section=section["id"],
            research_questions=research_queries,
            depth="deep" if section["id"] in ["results", "discussion"] else "normal"
        )
        
        research_context = ""
        if research_result.success and research_result.output:
            synthesis = research_result.output.get("synthesis", {})
            if isinstance(synthesis, dict):
                research_context = synthesis.get("summary", "")
                if synthesis.get("key_themes"):
                    research_context += "\n\nKey themes: " + ", ".join(synthesis.get("key_themes", []))
        
        # Writing phase
        writer = factory.create_v1("writer")
        writer.initialize(context)
        
        write_result = await writer.execute(
            action="write_section",
            section_id=section["id"],
            section_name=section["name"],
            min_words=section["min_words"],
            max_words=section["max_words"],
            guidelines=section["guidelines"],
            avoid=section["avoid"],
            research_context=research_context
        )
        
        if write_result.success:
            content = write_result.output
            word_count = len(str(content).split())
            article_content[section["id"]] = content
            print(f"    ✓ {section['name']}: {word_count} words")
        else:
            print(f"    ✗ {section['name']}: FAILED - {write_result.error}")
            article_content[section["id"]] = f"[Section generation failed: {write_result.error}]"
    
    # Compile full article
    print("\n[4/5] Compiling article...")
    full_article = _compile_article(article_content, ARTICLE_CONFIG)
    
    # Validate consistency
    print("\n[4.5/5] Validating consistency...")
    validator = ConsistencyValidatorAgent()
    validator.set_canonical_values(CANONICAL_VALUES)
    validator.on_initialize()
    
    validation_result = await validator._validate_article(full_article)
    
    if validation_result["errors"] > 0:
        print(f"    ⚠ Found {validation_result['errors']} consistency errors")
        for issue in validation_result["issues"]:
            if issue["severity"] == "error":
                print(f"      - {issue['issue_type']}: found '{issue['found']}', expected '{issue['expected']}'")
        
        # Auto-fix issues
        print("    → Auto-fixing issues...")
        full_article = await validator._fix_issues(full_article, validation_result["issues"])
        
        # Re-validate
        revalidation = await validator._validate_article(full_article)
        if revalidation["errors"] == 0:
            print("    ✓ All consistency issues fixed")
        else:
            print(f"    ⚠ {revalidation['errors']} issues remain (manual review needed)")
    else:
        print("    ✓ No consistency issues found")
    
    if validation_result["warnings"] > 0:
        print(f"    ℹ {validation_result['warnings']} warnings (review recommended)")
    
    # Save outputs
    print("[5/5] Saving outputs...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Save Markdown
    md_path = output_dir / "article_scoping_review.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_article)
    print(f"    Saved: {md_path}")
    
    # Generate statistics
    total_words = sum(len(str(c).split()) for c in article_content.values())
    print(f"\n{'=' * 70}")
    print(f"ARTICLE GENERATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total words: {total_words}")
    print(f"Sections: {len(article_content)}")
    print(f"Output: {md_path}")
    
    return str(md_path)


def _get_research_queries(section_id: str) -> list[str]:
    """Get research queries for each section."""
    queries = {
        "abstract": [
            "technostress psychosocial risks AI workplace scoping review"
        ],
        "introduction": [
            "technostress definition techno-overload techno-complexity",
            "artificial intelligence workplace transformation HR",
            "organizational culture digital transformation employee wellbeing",
            "Job Demands Resources model AI implementation"
        ],
        "methods": [
            "scoping review methodology PRISMA-ScR",
            "systematic review psychosocial risks workplace"
        ],
        "results": [
            "technostress prevalence employees AI adoption",
            "HR role AI implementation change management",
            "organizational culture digital climate leadership",
            "algorithmic management employee autonomy surveillance",
            "psychosocial interventions technostress mitigation",
            "burnout job insecurity digital transformation"
        ],
        "discussion": [
            "technostress theoretical implications JD-R model",
            "Conservation of Resources theory workplace technology",
            "Self-Determination Theory algorithmic management autonomy",
            "HR digital transformation strategic role",
            "organizational resilience AI workplace"
        ],
        "conclusion": [
            "HR AI implementation recommendations policy",
            "organizational resilience technostress prevention"
        ]
    }
    return queries.get(section_id, ["AI workplace psychosocial risks"])


def _compile_article(content: dict, config: dict) -> str:
    """Compile full article in academic format."""
    
    lines = []
    
    # Title
    lines.append(f"# {config['title']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Authors placeholder
    lines.append("**Authors:** [Author Names]")
    lines.append("")
    lines.append("**Affiliations:** [Institutional Affiliations]")
    lines.append("")
    lines.append(f"**Target Journal:** {config['target_journal']}")
    lines.append("")
    lines.append(f"**Date:** {datetime.now().strftime('%B %Y')}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Abstract
    if "abstract" in content:
        lines.append("## Abstract")
        lines.append("")
        lines.append(content["abstract"])
        lines.append("")
        lines.append("**Keywords:** technostress, artificial intelligence, human resources, organizational culture, psychosocial risks, workplace transformation, scoping review")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Main sections
    section_order = ["introduction", "methods", "results", "discussion", "conclusion"]
    section_numbers = {"introduction": "1", "methods": "2", "results": "3", "discussion": "4", "conclusion": "5"}
    
    for sec_id in section_order:
        if sec_id in content:
            sec_name = sec_id.replace("_", " ").title()
            lines.append(f"## {section_numbers[sec_id]}. {sec_name}")
            lines.append("")
            lines.append(content[sec_id])
            lines.append("")
    
    # References placeholder
    lines.append("---")
    lines.append("")
    lines.append("## References")
    lines.append("")
    lines.append("*[References will be compiled from in-text citations]*")
    lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    output_path = asyncio.run(generate_article())
    print(f"\nArticle saved to: {output_path}")
