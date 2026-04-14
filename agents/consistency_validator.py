"""Consistency Validator Agent: Ensures data consistency across article sections."""

import re
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

import structlog

from agents.base_agent import BaseAgent, AgentRole, AgentResult


logger = structlog.get_logger()


@dataclass
class ConsistencyIssue:
    """Represents a consistency issue found in the article."""
    issue_type: str  # date, number, terminology
    section: str
    line_or_context: str
    expected_value: str
    found_value: str
    severity: str  # error, warning


class ConsistencyValidatorAgent(BaseAgent):
    """
    Agent responsible for validating consistency across article sections.
    
    Checks for:
    - Date/timeframe consistency (e.g., 2015-2025 everywhere)
    - Study count consistency (n=67 everywhere)
    - Terminology consistency
    - Citation format consistency
    """
    
    def __init__(self):
        super().__init__(
            name="consistency_validator",
            role=AgentRole.QUALITY,
            description="Validates data consistency across article sections",
            version="1.0.0"
        )
        
        # Canonical values from research plan
        self._canonical_values = {
            "timeframe_start": "2015",
            "timeframe_end": "2025",
            "timeframe_full": "2015-2025",
            "timeframe_text": "January 2015 and December 2025",
            "methodology": "scoping review",
            "guidelines": "PRISMA-ScR",
        }
    
    def set_canonical_values(self, values: Dict[str, str]) -> None:
        """Set canonical values from research plan."""
        self._canonical_values.update(values)
    
    def on_initialize(self) -> None:
        """Initialize validator."""
        pass
    
    async def _execute_action(self, action: str, **kwargs) -> Any:
        """Execute validation actions."""
        if action == "validate_article":
            return await self._validate_article(**kwargs)
        elif action == "validate_section":
            return await self._validate_section(**kwargs)
        elif action == "fix_issues":
            return await self._fix_issues(**kwargs)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _validate_article(
        self,
        article_content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate entire article for consistency."""
        
        issues: List[ConsistencyIssue] = []
        
        # Check date consistency
        date_issues = self._check_date_consistency(article_content)
        issues.extend(date_issues)
        
        # Check number consistency  
        number_issues = self._check_number_consistency(article_content)
        issues.extend(number_issues)
        
        # Check terminology consistency
        term_issues = self._check_terminology_consistency(article_content)
        issues.extend(term_issues)
        
        # Categorize issues
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        self.log.info(
            "validation_complete",
            total_issues=len(issues),
            errors=len(errors),
            warnings=len(warnings)
        )
        
        return {
            "valid": len(errors) == 0,
            "issues": [self._issue_to_dict(i) for i in issues],
            "errors": len(errors),
            "warnings": len(warnings),
            "summary": self._generate_summary(issues)
        }
    
    def _check_date_consistency(self, content: str) -> List[ConsistencyIssue]:
        """Check for date/timeframe consistency."""
        issues = []
        
        # Patterns for date ranges (more specific to avoid DOI matches)
        date_patterns = [
            # "between YYYY and YYYY" - most reliable
            (r'between\s+(19\d{2}|20\d{2})\s+and\s+(19\d{2}|20\d{2})', True),
            # "from YYYY to YYYY"
            (r'from\s+(19\d{2}|20\d{2})\s+to\s+(19\d{2}|20\d{2})', True),
            # "January YYYY and December YYYY"
            (r'January\s+(19\d{2}|20\d{2})\s+and\s+December\s+(19\d{2}|20\d{2})', True),
            # "YYYY-YYYY" or "YYYY–YYYY" but only in specific contexts (timeframe/period)
            (r'(?:timeframe|period|years?|published|between)\s*(?::|of|is|was|from)?\s*(19\d{2}|20\d{2})[-–](19\d{2}|20\d{2})', False),
        ]
        
        canonical_start = self._canonical_values.get("timeframe_start", "2015")
        canonical_end = self._canonical_values.get("timeframe_end", "2025")
        
        for pattern, is_direct_match in date_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                start_year = match.group(1)
                end_year = match.group(2)
                
                # Skip if this looks like it's inside a DOI or URL
                full_match_text = match.group(0)
                context_start = max(0, match.start() - 30)
                context_end = min(len(content), match.end() + 30)
                context = content[context_start:context_end]
                
                # Skip DOI patterns
                if 'doi.org' in context.lower() or '/10.' in context or 'https://' in context:
                    continue
                
                # Skip if within parentheses that look like journal references
                if re.search(r'\d{4}\.\d+', context):  # Looks like DOI
                    continue
                
                # Get display context
                display_context = content[max(0, match.start() - 50):min(len(content), match.end() + 50)].replace('\n', ' ')
                
                # Check if dates match canonical
                if start_year != canonical_start or end_year != canonical_end:
                    issues.append(ConsistencyIssue(
                        issue_type="date",
                        section="unknown",
                        line_or_context=f"...{display_context}...",
                        expected_value=f"{canonical_start}-{canonical_end}",
                        found_value=f"{start_year}-{end_year}",
                        severity="error"
                    ))
        
        return issues
    
    def _check_number_consistency(self, content: str) -> List[ConsistencyIssue]:
        """Check for number consistency (study counts, etc.)."""
        issues = []
        
        # Find all "n = X" or "(n=X)" patterns
        study_counts = {}
        patterns = [
            r'\(n\s*=\s*(\d+)\)',
            r'n\s*=\s*(\d+)',
            r'(\d+)\s+(?:studies|articles|papers)\s+(?:were\s+)?included',
            r'included\s+(\d+)\s+(?:studies|articles|papers)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                count = match.group(1)
                study_counts[count] = study_counts.get(count, 0) + 1
        
        # If there are multiple different study counts, flag inconsistency
        if len(study_counts) > 1:
            most_common = max(study_counts.items(), key=lambda x: x[1])
            for count, freq in study_counts.items():
                if count != most_common[0]:
                    issues.append(ConsistencyIssue(
                        issue_type="number",
                        section="multiple",
                        line_or_context=f"Study count '{count}' appears {freq} times",
                        expected_value=f"n={most_common[0]} (most common)",
                        found_value=f"n={count}",
                        severity="warning"
                    ))
        
        return issues
    
    def _check_terminology_consistency(self, content: str) -> List[ConsistencyIssue]:
        """Check for terminology consistency."""
        issues = []
        
        # Check for mixed American/British spelling
        spelling_pairs = [
            ("behaviour", "behavior"),
            ("organisation", "organization"),
            ("organise", "organize"),
            ("analyse", "analyze"),
            ("labour", "labor"),
        ]
        
        for british, american in spelling_pairs:
            british_count = len(re.findall(british, content, re.IGNORECASE))
            american_count = len(re.findall(american, content, re.IGNORECASE))
            
            if british_count > 0 and american_count > 0:
                dominant = british if british_count > american_count else american
                minority = american if british_count > american_count else british
                issues.append(ConsistencyIssue(
                    issue_type="terminology",
                    section="multiple",
                    line_or_context=f"Mixed spelling: '{british}' ({british_count}x) vs '{american}' ({american_count}x)",
                    expected_value=f"Use '{dominant}' consistently",
                    found_value=f"'{minority}' also used",
                    severity="warning"
                ))
        
        return issues
    
    def _fix_issues(
        self,
        content: str,
        issues: List[Dict[str, Any]],
        **kwargs
    ) -> str:
        """Automatically fix consistency issues."""
        
        fixed_content = content
        
        for issue in issues:
            if issue["issue_type"] == "date" and issue["severity"] == "error":
                # Fix date issues
                wrong_date = issue["found_value"]
                correct_date = issue["expected_value"]
                
                # Handle different formats
                if "-" in wrong_date or "–" in wrong_date:
                    start, end = re.split(r'[-–]', wrong_date)
                    correct_start, correct_end = correct_date.split("-")
                    
                    # Replace various formats
                    patterns = [
                        (f"between {start} and {end}", f"between {correct_start} and {correct_end}"),
                        (f"from {start} to {end}", f"from {correct_start} to {correct_end}"),
                        (f"{start}-{end}", f"{correct_start}-{correct_end}"),
                        (f"{start}–{end}", f"{correct_start}–{correct_end}"),
                    ]
                    
                    for old, new in patterns:
                        fixed_content = re.sub(
                            re.escape(old), 
                            new, 
                            fixed_content, 
                            flags=re.IGNORECASE
                        )
        
        return fixed_content
    
    async def _validate_section(
        self,
        section_content: str,
        section_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Validate a single section."""
        # Delegate to full article validation with section context
        result = await self._validate_article(section_content)
        
        # Update section info in issues
        for issue in result.get("issues", []):
            issue["section"] = section_name
        
        return result
    
    def _issue_to_dict(self, issue: ConsistencyIssue) -> Dict[str, Any]:
        """Convert ConsistencyIssue to dictionary."""
        return {
            "issue_type": issue.issue_type,
            "section": issue.section,
            "context": issue.line_or_context,
            "expected": issue.expected_value,
            "found": issue.found_value,
            "severity": issue.severity
        }
    
    def _generate_summary(self, issues: List[ConsistencyIssue]) -> str:
        """Generate human-readable summary of issues."""
        if not issues:
            return "No consistency issues found."
        
        summary_parts = []
        
        date_issues = [i for i in issues if i.issue_type == "date"]
        if date_issues:
            summary_parts.append(f"- {len(date_issues)} date/timeframe inconsistencies")
        
        number_issues = [i for i in issues if i.issue_type == "number"]
        if number_issues:
            summary_parts.append(f"- {len(number_issues)} number inconsistencies")
        
        term_issues = [i for i in issues if i.issue_type == "terminology"]
        if term_issues:
            summary_parts.append(f"- {len(term_issues)} terminology inconsistencies")
        
        return "Found issues:\n" + "\n".join(summary_parts)
    
    def _enrich_result(self, result: Any, action: str, **kwargs) -> AgentResult:
        """Enrich validation result."""
        if isinstance(result, dict):
            return AgentResult(
                success=result.get("valid", True),
                data=result,
                confidence=1.0 if result.get("valid", True) else 0.7,
                metadata={
                    "action": action,
                    "errors": result.get("errors", 0),
                    "warnings": result.get("warnings", 0)
                }
            )
        return AgentResult(success=True, data=result, confidence=1.0)
