"""Validate SKILL.md YAML frontmatter across all agent skills.

Usage:
    python validate_skills.py
"""

import os
import yaml
import re
from pathlib import Path

def validate_yaml_frontmatter(filepath):
    """Extract and validate YAML frontmatter from a SKILL.md file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {"file": filepath, "valid": False, "error": "No YAML frontmatter found"}
        
        yaml_content = match.group(1)
        
        # Parse YAML
        data = yaml.safe_load(yaml_content)
        
        # Check required fields
        required = ['name', 'description']
        missing = [f for f in required if f not in data]
        
        if missing:
            return {"file": filepath, "valid": False, "error": f"Missing required fields: {missing}"}
        
        # Get relative path for display
        try:
            rel_path = str(Path(filepath).relative_to(Path(__file__).parent))
        except ValueError:
            rel_path = str(filepath)
        
        return {
            "file": rel_path,
            "valid": True,
            "name": data['name'],
            "user_invocable": data.get('user-invocable', 'not set'),
            "has_tools": 'tools' in data,
            "has_model": 'model' in data
        }
    
    except yaml.YAMLError as e:
        return {"file": filepath, "valid": False, "error": f"YAML error: {e}"}
    except Exception as e:
        return {"file": filepath, "valid": False, "error": str(e)}

def main():
    # Find all SKILL.md files
    skills_dir = Path(__file__).parent
    skill_files = list(skills_dir.rglob("SKILL.md"))
    
    print(f"Found {len(skill_files)} SKILL.md files\n")
    print("=" * 70)
    
    valid_count = 0
    errors = []
    
    for skill_file in sorted(skill_files):
        result = validate_yaml_frontmatter(skill_file)
        if result['valid']:
            valid_count += 1
            invocable = "✓ user" if result['user_invocable'] == True else "  agent"
            tools = "T" if result.get('has_tools') else " "
            model = "M" if result.get('has_model') else " "
            print(f"✓ {result['file']:<50} [{invocable}] [{tools}{model}]")
        else:
            errors.append(result)
            print(f"✗ {result['file']}: {result['error']}")
    
    print("=" * 70)
    print(f"\nSummary: {valid_count}/{len(skill_files)} valid")
    print(f"Legend: [T]=tools, [M]=model defined\n")
    
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e['file']}: {e['error']}")
    else:
        print("✓ All SKILL.md files have valid YAML frontmatter")

if __name__ == "__main__":
    main()
