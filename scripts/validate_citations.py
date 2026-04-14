"""Citation Validator: Verifies citation consistency and completeness."""

import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class CitationIssue:
    """A citation-related issue."""
    issue_type: str  # format, missing_reference, orphan_reference
    citation: str
    context: str
    severity: str  # error, warning


class CitationValidator:
    """Validates citations in academic articles."""
    
    def __init__(self):
        # Track citations and references
        self.in_text_citations: Set[str] = set()
        self.references: Dict[str, str] = {}  # normalized_key -> full_reference
        
    def validate_article(self, content: str) -> Dict:
        """Validate all citations in an article."""
        
        issues: List[CitationIssue] = []
        
        # Split into main content and references
        if "## References" in content:
            main_content, references_section = content.split("## References", 1)
        else:
            main_content = content
            references_section = ""
        
        # Extract in-text citations
        self.in_text_citations = self._extract_in_text_citations(main_content)
        
        # Extract references
        self.references = self._extract_references(references_section)
        
        # Check format consistency
        format_issues = self._check_format_consistency(main_content)
        issues.extend(format_issues)
        
        # Check for missing references
        missing_issues = self._check_missing_references()
        issues.extend(missing_issues)
        
        # Check for orphan references (no in-text citation)
        orphan_issues = self._check_orphan_references()
        issues.extend(orphan_issues)
        
        # Summary
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        return {
            "valid": len(errors) == 0,
            "total_citations": len(self.in_text_citations),
            "total_references": len(self.references),
            "issues": [self._issue_to_dict(i) for i in issues],
            "errors": len(errors),
            "warnings": len(warnings),
            "citation_list": sorted(list(self.in_text_citations)),
            "reference_keys": sorted(list(self.references.keys()))
        }
    
    def _extract_in_text_citations(self, content: str) -> Set[str]:
        """Extract all in-text citations."""
        citations = set()
        
        # Pattern 1: [Author, Year] or [Author & Author, Year]
        bracket_pattern = r'\[([A-Z][a-zA-Z\'\-]+(?:\s*(?:&|and)\s*[A-Z][a-zA-Z\'\-]+)?(?:\s*et\s*al\.)?),?\s*(\d{4})\]'
        
        # Pattern 2: (Author, Year) or (Author et al., Year)
        paren_pattern = r'\(([A-Z][a-zA-Z\'\-]+(?:\s*(?:&|and)\s*[A-Z][a-zA-Z\'\-]+)?(?:\s*et\s*al\.)?),?\s*(\d{4})\)'
        
        # Pattern 3: Author et al. (Year) - narrative citation
        narrative_pattern = r'([A-Z][a-zA-Z\'\-]+(?:\s*(?:&|and)\s*[A-Z][a-zA-Z\'\-]+)?)\s+et\s+al\.\s*\((\d{4})\)'
        
        # Pattern 4: Multiple citations [A, 2020; B, 2021]
        multi_bracket = r'\[([^\]]+)\]'
        multi_paren = r'\(([^)]+(?:;\s*[^)]+)+)\)'
        
        for match in re.finditer(bracket_pattern, content):
            author = match.group(1).strip()
            year = match.group(2)
            citations.add(self._normalize_citation(author, year))
        
        for match in re.finditer(paren_pattern, content):
            author = match.group(1).strip()
            year = match.group(2)
            citations.add(self._normalize_citation(author, year))
        
        # Handle narrative citations: Author et al. (Year)
        for match in re.finditer(narrative_pattern, content):
            author = match.group(1).strip()
            year = match.group(2)
            citations.add(self._normalize_citation(author, year))
        
        # Handle multiple citations in one bracket/paren
        for match in re.finditer(multi_bracket, content):
            inner = match.group(1)
            if ';' in inner:
                for part in inner.split(';'):
                    part = part.strip()
                    if re.match(r'[A-Z].*\d{4}', part):
                        # Extract author and year
                        year_match = re.search(r'(\d{4})', part)
                        if year_match:
                            year = year_match.group(1)
                            author = part[:year_match.start()].strip(' ,')
                            citations.add(self._normalize_citation(author, year))
        
        for match in re.finditer(multi_paren, content):
            inner = match.group(1)
            if ';' in inner:
                for part in inner.split(';'):
                    part = part.strip()
                    if re.match(r'[A-Z].*\d{4}', part):
                        year_match = re.search(r'(\d{4})', part)
                        if year_match:
                            year = year_match.group(1)
                            author = part[:year_match.start()].strip(' ,')
                            citations.add(self._normalize_citation(author, year))
        
        return citations
    
    def _normalize_citation(self, author: str, year: str) -> str:
        """Normalize citation to standard format."""
        # Remove "et al." for matching
        author = re.sub(r'\s*et\s*al\.?', '', author).strip()
        # Standardize ampersand
        author = re.sub(r'\s+and\s+', ' & ', author)
        return f"{author}, {year}"
    
    def _extract_references(self, ref_section: str) -> Dict[str, str]:
        """Extract references from reference section."""
        references = {}
        
        # Each reference typically starts with author names and year
        # Pattern: Author, A. B., & Author, C. D. (Year).
        lines = ref_section.split('\n')
        
        current_ref = ""
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('*') or line.startswith('---'):
                continue
            
            # Check if this looks like the start of a new reference
            if re.match(r'^[A-Z][a-zA-Z\'\-]+,?\s+[A-Z]\.', line):
                if current_ref:
                    # Save previous reference
                    key = self._extract_ref_key(current_ref)
                    if key:
                        references[key] = current_ref
                current_ref = line
            else:
                current_ref += " " + line
        
        # Don't forget the last one
        if current_ref:
            key = self._extract_ref_key(current_ref)
            if key:
                references[key] = current_ref
        
        return references
    
    def _extract_ref_key(self, reference: str) -> str:
        """Extract normalized key from a full reference."""
        # Look for (Year) pattern
        year_match = re.search(r'\((\d{4})\)', reference)
        if not year_match:
            return ""
        
        year = year_match.group(1)
        
        # Get first author's last name
        author_match = re.match(r'^([A-Z][a-zA-Z\'\-]+)', reference)
        if not author_match:
            return ""
        
        first_author = author_match.group(1)
        
        # Check for "et al." citations - these match first author only
        # Return just first author for matching
        return f"{first_author}, {year}"
    
    def _check_format_consistency(self, content: str) -> List[CitationIssue]:
        """Check for consistent citation format."""
        issues = []
        
        # Count bracket vs parenthesis citations
        bracket_count = len(re.findall(r'\[[A-Z][^\]]*\d{4}\]', content))
        paren_count = len(re.findall(r'\([A-Z][^)]*\d{4}\)', content))
        
        if bracket_count > 0 and paren_count > 0:
            dominant = "brackets []" if bracket_count > paren_count else "parentheses ()"
            minority = "parentheses ()" if bracket_count > paren_count else "brackets []"
            issues.append(CitationIssue(
                issue_type="format",
                citation="mixed",
                context=f"Found {bracket_count} bracket citations and {paren_count} parenthesis citations",
                severity="warning"
            ))
        
        return issues
    
    def _check_missing_references(self) -> List[CitationIssue]:
        """Check for in-text citations without matching reference."""
        issues = []
        
        for citation in self.in_text_citations:
            # Extract first author and year from citation
            cit_match = re.match(r'^([A-Za-z\'\-]+)', citation)
            year_match = re.search(r'(\d{4})', citation)
            
            if not cit_match or not year_match:
                continue
            
            cit_author = cit_match.group(1).lower()
            cit_year = year_match.group(1)
            
            # Try to find matching reference
            found = False
            for ref_key in self.references.keys():
                ref_match = re.match(r'^([A-Za-z\'\-]+)', ref_key)
                ref_year_match = re.search(r'(\d{4})', ref_key)
                
                if ref_match and ref_year_match:
                    ref_author = ref_match.group(1).lower()
                    ref_year = ref_year_match.group(1)
                    
                    if cit_author == ref_author and cit_year == ref_year:
                        found = True
                        break
            
            if not found:
                issues.append(CitationIssue(
                    issue_type="missing_reference",
                    citation=citation,
                    context=f"No matching reference found for: {citation}",
                    severity="error"
                ))
        
        return issues
    
    def _check_orphan_references(self) -> List[CitationIssue]:
        """Check for references without in-text citations."""
        issues = []
        
        for ref_key in self.references.keys():
            # Extract first author and year from reference
            ref_match = re.match(r'^([A-Za-z\'\-]+)', ref_key)
            ref_year_match = re.search(r'(\d{4})', ref_key)
            
            if not ref_match or not ref_year_match:
                continue
                
            ref_author = ref_match.group(1).lower()
            ref_year = ref_year_match.group(1)
            
            found = False
            for citation in self.in_text_citations:
                cit_match = re.match(r'^([A-Za-z\'\-]+)', citation)
                cit_year_match = re.search(r'(\d{4})', citation)
                
                if cit_match and cit_year_match:
                    cit_author = cit_match.group(1).lower()
                    cit_year = cit_year_match.group(1)
                    
                    if cit_author == ref_author and cit_year == ref_year:
                        found = True
                        break
            
            if not found:
                issues.append(CitationIssue(
                    issue_type="orphan_reference",
                    citation=ref_key,
                    context=f"Reference not cited in text: {ref_key}",
                    severity="warning"
                ))
        
        return issues
    
    def _issue_to_dict(self, issue: CitationIssue) -> Dict:
        return {
            "type": issue.issue_type,
            "citation": issue.citation,
            "context": issue.context,
            "severity": issue.severity
        }


def main():
    """Test citation validation."""
    print("=" * 60)
    print("CITATION VALIDATION")
    print("=" * 60)
    
    # Read article
    article_path = Path("output/article_scoping_review.md")
    if not article_path.exists():
        print(f"Article not found: {article_path}")
        return
    
    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    validator = CitationValidator()
    result = validator.validate_article(content)
    
    print(f"\nTotal in-text citations: {result['total_citations']}")
    print(f"Total references: {result['total_references']}")
    print(f"Errors: {result['errors']}")
    print(f"Warnings: {result['warnings']}")
    print(f"Valid: {'✓' if result['valid'] else '✗'}")
    
    if result['issues']:
        print("\n" + "-" * 40)
        print("ISSUES FOUND:")
        print("-" * 40)
        for issue in result['issues']:
            icon = "❌" if issue['severity'] == "error" else "⚠"
            print(f"{icon} [{issue['type']}] {issue['citation']}")
            print(f"   {issue['context']}")
    
    print("\n" + "-" * 40)
    print("IN-TEXT CITATIONS FOUND:")
    print("-" * 40)
    for cit in sorted(result['citation_list']):
        print(f"  - {cit}")
    
    print("\n" + "-" * 40)
    print("REFERENCES FOUND:")
    print("-" * 40)
    for ref in sorted(result['reference_keys']):
        print(f"  - {ref}")


if __name__ == "__main__":
    main()
