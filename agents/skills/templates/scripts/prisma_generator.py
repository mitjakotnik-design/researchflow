"""
PRISMA 2020 Flow Diagram Generator

Generates PRISMA 2020 flow diagrams in multiple formats:
- Mermaid (for GitHub/GitLab/VS Code preview)
- DOT (for Graphviz)
- ASCII (for terminal/plain text)
- JSON (for programmatic use)

Usage:
    python prisma_generator.py --output diagram.md
    python prisma_generator.py --format dot --output diagram.dot
"""

import argparse
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PRISMAFlowData:
    """PRISMA 2020 flow diagram data structure."""
    
    # Identification
    databases_records: int = 0
    registers_records: int = 0
    other_sources_records: int = 0
    
    # Before screening
    duplicates_removed: int = 0
    automation_removed: int = 0
    
    # Screening
    records_screened: int = 0
    records_excluded: int = 0
    
    # Retrieval
    reports_sought: int = 0
    reports_not_retrieved: int = 0
    
    # Eligibility
    reports_assessed: int = 0
    exclusion_reasons: Dict[str, int] = field(default_factory=dict)
    
    # Included
    studies_included: int = 0
    reports_included: int = 0
    
    # Optional: Previous studies (for updates)
    previous_studies: int = 0
    previous_reports: int = 0
    
    def total_excluded_fulltext(self) -> int:
        return sum(self.exclusion_reasons.values())
    
    def validate(self) -> List[str]:
        """Validate flow numbers are consistent."""
        errors = []
        
        total_identified = self.databases_records + self.registers_records + self.other_sources_records
        after_duplicates = total_identified - self.duplicates_removed - self.automation_removed
        
        if self.records_screened != after_duplicates:
            errors.append(f"Records screened ({self.records_screened}) != identified - removed ({after_duplicates})")
        
        after_screening = self.records_screened - self.records_excluded
        if self.reports_sought != after_screening:
            errors.append(f"Reports sought ({self.reports_sought}) != screened - excluded ({after_screening})")
        
        after_retrieval = self.reports_sought - self.reports_not_retrieved
        if self.reports_assessed != after_retrieval:
            errors.append(f"Reports assessed ({self.reports_assessed}) != sought - not retrieved ({after_retrieval})")
        
        after_eligibility = self.reports_assessed - self.total_excluded_fulltext()
        if self.studies_included != after_eligibility:
            errors.append(f"Studies included ({self.studies_included}) != assessed - excluded ({after_eligibility})")
        
        return errors


def generate_mermaid(data: PRISMAFlowData) -> str:
    """Generate Mermaid flowchart syntax."""
    
    exclusion_text = "\\n".join([f"• {reason}: n={count}" for reason, count in data.exclusion_reasons.items()])
    if not exclusion_text:
        exclusion_text = "Reasons documented"
    
    mermaid = f"""```mermaid
flowchart TD
    subgraph identification["Identification"]
        A1["Records identified from databases\\n(n = {data.databases_records})"]
        A2["Records identified from registers\\n(n = {data.registers_records})"]
        A3["Records from other sources\\n(n = {data.other_sources_records})"]
    end

    subgraph screening["Screening"]
        B1["Records after duplicates removed\\n(n = {data.records_screened})"]
        B2["Records screened\\n(n = {data.records_screened})"]
        B3["Records excluded\\n(n = {data.records_excluded})"]
    end

    subgraph eligibility["Eligibility"]
        C1["Reports sought for retrieval\\n(n = {data.reports_sought})"]
        C2["Reports not retrieved\\n(n = {data.reports_not_retrieved})"]
        C3["Reports assessed for eligibility\\n(n = {data.reports_assessed})"]
        C4["Reports excluded:\\n{exclusion_text}\\n(n = {data.total_excluded_fulltext()})"]
    end

    subgraph included["Included"]
        D1["Studies included in review\\n(n = {data.studies_included})"]
        D2["Reports of included studies\\n(n = {data.reports_included})"]
    end

    A1 & A2 & A3 --> B1
    B1 --> B2
    B2 --> B3
    B2 --> C1
    C1 --> C2
    C1 --> C3
    C3 --> C4
    C3 --> D1
    D1 --> D2

    style A1 fill:#e1f5fe
    style A2 fill:#e1f5fe
    style A3 fill:#e1f5fe
    style B3 fill:#ffebee
    style C2 fill:#ffebee
    style C4 fill:#ffebee
    style D1 fill:#e8f5e9
    style D2 fill:#e8f5e9
```"""
    
    return mermaid


def generate_ascii(data: PRISMAFlowData) -> str:
    """Generate ASCII diagram."""
    
    total_identified = data.databases_records + data.registers_records + data.other_sources_records
    duplicates = data.duplicates_removed + data.automation_removed
    
    exclusion_lines = [f"    {reason}: n={count}" for reason, count in data.exclusion_reasons.items()]
    exclusion_text = "\n".join(exclusion_lines) if exclusion_lines else "    [No reasons specified]"
    
    ascii_diagram = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PRISMA 2020 FLOW DIAGRAM                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  IDENTIFICATION                                                              ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │ Records identified from:                                               │ ║
║  │   • Databases (n = {data.databases_records:,})                                              │ ║
║  │   • Registers (n = {data.registers_records:,})                                              │ ║
║  │   • Other sources (n = {data.other_sources_records:,})                                        │ ║
║  │ Total: (n = {total_identified:,})                                                   │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
║                                      │                                       ║
║                                      ▼                                       ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │ Duplicates removed (n = {duplicates:,})                                          │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SCREENING                                                                   ║
║  ┌────────────────────────────────┐   ┌────────────────────────────────────┐ ║
║  │ Records screened               │   │ Records excluded                   │ ║
║  │ (n = {data.records_screened:,})                     │ → │ (n = {data.records_excluded:,})                          │ ║
║  └────────────────────────────────┘   └────────────────────────────────────┘ ║
║                  │                                                           ║
║                  ▼                                                           ║
║  ┌────────────────────────────────┐   ┌────────────────────────────────────┐ ║
║  │ Reports sought for retrieval   │   │ Reports not retrieved              │ ║
║  │ (n = {data.reports_sought:,})                        │ → │ (n = {data.reports_not_retrieved:,})                              │ ║
║  └────────────────────────────────┘   └────────────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ELIGIBILITY                                                                 ║
║  ┌────────────────────────────────┐   ┌────────────────────────────────────┐ ║
║  │ Reports assessed for           │   │ Reports excluded:                  │ ║
║  │ eligibility                    │   │ (n = {data.total_excluded_fulltext():,})                             │ ║
║  │ (n = {data.reports_assessed:,})                      │ → │ Reasons:                           │ ║
║  └────────────────────────────────┘   │{exclusion_text[:36]:<36}│ ║
║                  │                     └────────────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  INCLUDED                                                                    ║
║  ┌────────────────────────────────────────────────────────────────────────┐ ║
║  │ Studies included in review (n = {data.studies_included:,})                                │ ║
║  │ Reports of included studies (n = {data.reports_included:,})                              │ ║
║  └────────────────────────────────────────────────────────────────────────┘ ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return ascii_diagram


def generate_json(data: PRISMAFlowData) -> str:
    """Export as JSON."""
    return json.dumps({
        "identification": {
            "databases": data.databases_records,
            "registers": data.registers_records,
            "other_sources": data.other_sources_records
        },
        "duplicates_removed": data.duplicates_removed + data.automation_removed,
        "screening": {
            "records_screened": data.records_screened,
            "records_excluded": data.records_excluded
        },
        "retrieval": {
            "reports_sought": data.reports_sought,
            "reports_not_retrieved": data.reports_not_retrieved
        },
        "eligibility": {
            "reports_assessed": data.reports_assessed,
            "reports_excluded": data.total_excluded_fulltext(),
            "exclusion_reasons": data.exclusion_reasons
        },
        "included": {
            "studies": data.studies_included,
            "reports": data.reports_included
        }
    }, indent=2)


def example_data() -> PRISMAFlowData:
    """Generate example scoping review data."""
    return PRISMAFlowData(
        databases_records=1847,
        registers_records=0,
        other_sources_records=23,
        duplicates_removed=412,
        automation_removed=0,
        records_screened=1458,
        records_excluded=1102,
        reports_sought=356,
        reports_not_retrieved=12,
        reports_assessed=344,
        exclusion_reasons={
            "Wrong population": 45,
            "Wrong concept": 89,
            "Wrong study type": 67,
            "No full text": 8,
            "Not English": 5,
            "Other": 13
        },
        studies_included=117,
        reports_included=117
    )


def main():
    parser = argparse.ArgumentParser(description="Generate PRISMA 2020 Flow Diagram")
    parser.add_argument("--format", "-f", choices=["mermaid", "ascii", "json"], 
                        default="mermaid", help="Output format")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--input", "-i", help="Input JSON file with flow data")
    parser.add_argument("--validate", "-v", action="store_true", 
                        help="Validate flow numbers")
    
    args = parser.parse_args()
    
    # Load or use example data
    if args.input:
        with open(args.input, 'r') as f:
            data_dict = json.load(f)
        data = PRISMAFlowData(**data_dict)
    else:
        data = example_data()
    
    # Validate
    if args.validate:
        errors = data.validate()
        if errors:
            print("Validation errors:")
            for e in errors:
                print(f"  ✗ {e}")
        else:
            print("✓ All flow numbers are consistent")
    
    # Generate output
    if args.format == "mermaid":
        output = generate_mermaid(data)
    elif args.format == "ascii":
        output = generate_ascii(data)
    else:
        output = generate_json(data)
    
    # Write or print
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Diagram saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
