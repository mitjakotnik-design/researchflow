"""Fix citation issues in the article."""

import re
from pathlib import Path


def fix_citations(content: str) -> str:
    """Fix all citation issues in the article."""
    
    # 1. Remove numbered citations like [9, 11] or [3, 5, 7]
    # These are placeholders that shouldn't be in final article
    content = re.sub(r'\s*\[\d+(?:,\s*\d+)*\]', '', content)
    
    # 2. Standardize bracket citations to parentheses (APA style)
    # Convert [Author, Year] to (Author, Year)
    bracket_citations = re.finditer(r'\[([A-Z][^\]]+?\d{4}[^\]]*)\]', content)
    replacements = []
    for match in bracket_citations:
        inner = match.group(1)
        # Skip if it's a URL or other non-citation bracket
        if 'http' in inner or 'www' in inner:
            continue
        replacements.append((match.group(0), f'({inner})'))
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    # 3. Fix "et al" format - ensure comma before year
    content = re.sub(r'(\w+)\s+et\s+al\.\s*,?\s*(\d{4})', r'\1 et al., \2', content)
    
    # 4. Add proper citations for theoretical frameworks in Introduction
    # Self-Determination Theory should cite Ryan & Deci
    if 'Self-Determination Theory (SDT)' in content and '(Ryan & Deci' not in content:
        content = content.replace(
            'Self-Determination Theory (SDT)',
            'Self-Determination Theory (SDT; Ryan & Deci, 2000)'
        )
    
    # Job Demands-Resources model should cite Bakker & Demerouti
    if 'Job Demands-Resources' in content and '(Bakker & Demerouti' not in content:
        content = content.replace(
            'The Job Demands-Resources (JD-R) model',
            'The Job Demands-Resources (JD-R) model (Bakker & Demerouti, 2007)'
        )
        content = content.replace(
            'Job Demands-Resources model',
            'Job Demands-Resources model (Bakker & Demerouti, 2007)'
        )
    
    # Conservation of Resources theory should cite Hobfoll
    if 'Conservation of Resources' in content and '(Hobfoll' not in content:
        content = content.replace(
            'Conservation of Resources (COR) theory',
            'Conservation of Resources (COR) theory (Hobfoll, 1989)'
        )
    
    # Socio-Technical Systems should cite Trist & Bamforth
    if 'Socio-Technical Systems' in content and '(Trist' not in content:
        content = content.replace(
            'Socio-Technical Systems (STS) theory',
            'Socio-Technical Systems (STS) theory (Trist & Bamforth, 1951)'
        )
    
    # Technostress original concept should cite Tarafdar
    if 'technostress' in content.lower() and '(Tarafdar' not in content:
        # Find first definition of technostress and add citation
        content = re.sub(
            r'(phenomenon of technostress,?\s*(?:broadly\s+)?defined as)',
            r'\1 by Tarafdar et al. (2007) as',
            content,
            count=1
        )
    
    return content


def main():
    """Fix citations in the article."""
    print("=" * 60)
    print("FIXING CITATIONS")
    print("=" * 60)
    
    article_path = Path("output/article_scoping_review.md")
    
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Count issues before
    numbered_before = len(re.findall(r'\[\d+(?:,\s*\d+)*\]', content))
    bracket_before = len(re.findall(r'\[[A-Z][^\]]*\d{4}[^\]]*\]', content))
    
    print(f"Before:")
    print(f"  - Numbered citations: {numbered_before}")
    print(f"  - Bracket citations: {bracket_before}")
    
    # Fix
    fixed_content = fix_citations(content)
    
    # Count after
    numbered_after = len(re.findall(r'\[\d+(?:,\s*\d+)*\]', fixed_content))
    bracket_after = len(re.findall(r'\[[A-Z][^\]]*\d{4}[^\]]*\]', fixed_content))
    paren_after = len(re.findall(r'\([A-Z][^)]*\d{4}[^)]*\)', fixed_content))
    
    print(f"\nAfter:")
    print(f"  - Numbered citations: {numbered_after}")
    print(f"  - Bracket citations: {bracket_after}")
    print(f"  - Parenthesis citations: {paren_after}")
    
    # Save
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(fixed_content)
    
    print(f"\n✓ Fixed article saved to: {article_path}")


if __name__ == "__main__":
    main()
