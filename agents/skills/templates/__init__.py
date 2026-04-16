"""
ResearchFlow Templates Package

Provides standardized templates for scoping review workflow.

Templates:
    - data-charting-form: Data extraction form (PCC framework)
    - search-documentation: Search strategy documentation
    - screening-form: Title/abstract and full-text screening
    - prisma-scr-checklist: 22-item PRISMA-ScR compliance
    - study-characteristics-summary: Summary tables
    - conflict-resolution-form: Disagreement resolution

Usage:
    from agents.skills.templates import load_template, list_templates
    
    # List available templates
    for name in list_templates():
        print(name)
    
    # Load a template
    form = load_template("data-charting-form")
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent


def load_template(template_name: str) -> str:
    """
    Load a template file content.
    
    Args:
        template_name: Template name without .md extension
        
    Returns:
        Template content as string
    """
    path = TEMPLATES_DIR / f"{template_name}.md"
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


def get_template_path(template_name: str) -> Path:
    """Get the full path to a template."""
    return TEMPLATES_DIR / f"{template_name}.md"


__all__ = [
    "TEMPLATES_DIR",
    "load_template",
    "list_templates",
    "get_template_path",
]
