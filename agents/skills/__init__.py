"""
ResearchFlow Skills Package

This package contains SKILL.md documentation for all agents.

Structure:
    skills/
    ├── research-cluster/    # Research agents
    │   ├── researcher/
    │   ├── literature-scout/
    │   ├── data-extractor/
    │   ├── meta-analyst/
    │   └── gap-identifier/
    ├── writing-cluster/     # Writing agents
    │   ├── writer/
    │   ├── synthesizer/
    │   ├── academic-editor/
    │   ├── terminology-guardian/
    │   ├── citation-manager/
    │   └── visualizer/
    └── quality-cluster/     # Quality agents
        ├── multi-evaluator/
        ├── fact-checker/
        ├── consistency-checker/
        ├── bias-auditor/
        ├── critic/
        └── methodology-validator/

Usage:
    from agents.skills import templates, schemas
    
    # Load a template
    template = templates.load_template("data-charting-form")
    
    # Validate data
    schemas.validate_data_charting(data)
"""

from pathlib import Path

SKILLS_DIR = Path(__file__).parent
TEMPLATES_DIR = SKILLS_DIR / "templates"
SCHEMAS_DIR = TEMPLATES_DIR / "schemas"
SCRIPTS_DIR = TEMPLATES_DIR / "scripts"


def get_template_path(template_name: str) -> Path:
    """
    Get the full path to a template.
    
    Args:
        template_name: Template name without .md extension
        
    Returns:
        Path to the template file
    """
    return TEMPLATES_DIR / f"{template_name}.md"


def load_template(template_name: str) -> str:
    """
    Load a template file content.
    
    Args:
        template_name: Template name without .md extension
        
    Returns:
        Template content as string
    """
    path = get_template_path(template_name)
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def list_templates() -> list[str]:
    """List all available templates."""
    templates = []
    for file in TEMPLATES_DIR.iterdir():
        if file.is_file() and file.suffix == '.md' and file.name != 'README.md':
            templates.append(file.stem)
    return sorted(templates)


__all__ = [
    "SKILLS_DIR",
    "TEMPLATES_DIR",
    "SCHEMAS_DIR",
    "SCRIPTS_DIR",
    "get_template_path",
    "load_template",
    "list_templates",
]
