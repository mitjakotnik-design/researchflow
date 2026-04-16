#!/usr/bin/env python3
"""
ResearchFlow Skills Integration Demo

Demonstrates how to use the skills, templates, and tools integration.

Usage:
    python demo_integration.py
"""

import sys
from pathlib import Path

# Ensure the agents module is importable
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def demo_skill_loader():
    """Demonstrate skill loading functionality."""
    print("\n" + "=" * 60)
    print("1. SKILL LOADER DEMO")
    print("=" * 60)
    
    from agents import get_skill, list_all_skills, get_system_prompt
    
    # List all skills
    skills = list_all_skills()
    print(f"\n📚 Total skills available: {len(skills)}")
    
    # Group by cluster
    clusters = {}
    for skill in skills:
        parts = skill.split('/')
        cluster = parts[0]
        if cluster not in clusters:
            clusters[cluster] = []
        clusters[cluster].append(skill)
    
    for cluster, cluster_skills in clusters.items():
        print(f"\n  📁 {cluster}:")
        for s in cluster_skills:
            name = s.split('/')[-1] if '/' in s else '(cluster entry)'
            print(f"      - {name}")
    
    # Load a specific skill
    print("\n\n🔍 Loading 'research-cluster/researcher' skill...")
    skill = get_skill("research-cluster/researcher")
    print(f"   Name: {skill.name}")
    print(f"   Description: {skill.description[:100]}..." if len(skill.description) > 100 else f"   Description: {skill.description}")
    print(f"   Tools: {skill.tools}")
    print(f"   Model: {skill.model}")
    
    # Get system prompt
    print("\n\n💬 System prompt for 'researcher' agent:")
    prompt = get_system_prompt("researcher")
    if prompt:
        print(f"   {prompt[:200]}...")
    else:
        print("   (Not found)")


def demo_templates():
    """Demonstrate template loading functionality."""
    print("\n\n" + "=" * 60)
    print("2. TEMPLATES DEMO")
    print("=" * 60)
    
    from agents.skills import list_templates, load_template
    
    templates = list_templates()
    print(f"\n📄 Available templates ({len(templates)}):")
    for t in templates:
        print(f"   - {t}")
    
    # Load a template preview
    print("\n\n📝 Preview of 'data-charting-form' template:")
    content = load_template("data-charting-form")
    lines = content.split('\n')[:20]
    for line in lines:
        print(f"   {line}")
    print("   ...")


def demo_schemas():
    """Demonstrate schema validation functionality."""
    print("\n\n" + "=" * 60)
    print("3. SCHEMAS DEMO")
    print("=" * 60)
    
    from agents.skills.templates.schemas import (
        list_schemas, 
        create_empty_data_charting,
        validate_data_charting
    )
    
    schemas = list_schemas()
    print(f"\n📋 Available schemas: {schemas}")
    
    # Create empty form
    print("\n\n📝 Creating empty data charting form...")
    form = create_empty_data_charting()
    print(f"   Top-level fields: {list(form.keys())}")
    
    # Show validation (will fail on empty form)
    print("\n\n✅ Validating empty form (should have errors):")
    try:
        errors = validate_data_charting(form)
        if errors:
            for err in errors[:5]:
                print(f"   ❌ {err}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        else:
            print("   ✓ Valid (no errors)")
    except ImportError as e:
        print(f"   ⚠️ {e}")


def demo_scripts():
    """Demonstrate script tools."""
    print("\n\n" + "=" * 60)
    print("4. SCRIPTS DEMO")
    print("=" * 60)
    
    try:
        from agents.skills.templates.scripts import (
            calculate_kappa,
            generate_prisma_diagram
        )
        
        # IRR Demo
        print("\n\n📊 IRR Calculation Demo:")
        rater1 = ["include", "include", "exclude", "include", "exclude", 
                  "include", "exclude", "include", "include", "exclude"]
        rater2 = ["include", "exclude", "exclude", "include", "exclude",
                  "include", "include", "include", "include", "exclude"]
        
        result = calculate_kappa(rater1, rater2)
        print(f"   Rater 1: {rater1}")
        print(f"   Rater 2: {rater2}")
        print(f"   Cohen's Kappa: {result['kappa']:.3f}")
        print(f"   Agreement: {result['percent_agreement']:.1f}%")
        print(f"   Interpretation: {result['interpretation']}")
        
        # PRISMA Demo
        print("\n\n📈 PRISMA Diagram Demo:")
        counts = {
            "identified": 500,
            "duplicates_removed": 100,
            "screened": 400,
            "excluded_screening": 300,
            "sought_retrieval": 100,
            "not_retrieved": 10,
            "assessed_eligibility": 90,
            "excluded_eligibility": 50,
            "included": 40
        }
        
        diagram = generate_prisma_diagram(counts, format="ascii")
        print(diagram)
        
    except ImportError as e:
        print(f"\n   ⚠️ Scripts not available: {e}")
    except Exception as e:
        print(f"\n   ❌ Error: {e}")


def demo_integration():
    """Show full integration example."""
    print("\n\n" + "=" * 60)
    print("5. FULL INTEGRATION EXAMPLE")
    print("=" * 60)
    
    print("""
    
    # Example: Using skills to configure an agent
    
    from agents import get_skill, get_system_prompt, ResearcherAgent
    from agents.skills import load_template
    from agents.skills.templates.schemas import create_empty_data_charting
    from agents.skills.templates.scripts import calculate_kappa
    
    # 1. Get the skill for researcher agent
    skill = get_skill("research-cluster/researcher")
    
    # 2. Get system prompt (could use with LLM)
    system_prompt = get_system_prompt("researcher")
    
    # 3. Load template for data extraction
    template = load_template("data-charting-form")
    
    # 4. Create empty form for filling
    form = create_empty_data_charting()
    
    # 5. After two reviewers complete extraction, calculate IRR
    kappa = calculate_kappa(reviewer1_ratings, reviewer2_ratings)
    
    print(f"Inter-rater Kappa: {kappa['kappa']:.3f}")
    
    """)


def main():
    """Run all demos."""
    print("=" * 60)
    print("   RESEARCHFLOW SKILLS INTEGRATION DEMO")
    print("=" * 60)
    
    demo_skill_loader()
    demo_templates()
    demo_schemas()
    demo_scripts()
    demo_integration()
    
    print("\n" + "=" * 60)
    print("   DEMO COMPLETE")
    print("=" * 60)
    print("""
    
    📂 Integration structure:
    
    agents/
    ├── __init__.py          # Main exports (includes skill_loader)
    ├── skill_loader.py      # Core skill loading functionality
    └── skills/
        ├── __init__.py      # Skills package
        ├── templates/
        │   ├── __init__.py  # Templates package
        │   ├── schemas/
        │   │   └── __init__.py  # Schema validation
        │   └── scripts/
        │       └── __init__.py  # IRR & PRISMA tools
        ├── research-cluster/
        ├── writing-cluster/
        └── quality-cluster/
    
    """)


if __name__ == "__main__":
    main()
