"""
ResearchFlow Scripts Package

Provides Python tools for scoping review workflow.

Tools:
    - IRR Calculator: Inter-rater reliability calculation (Cohen's Kappa)
    - PRISMA Generator: PRISMA flow diagram generation

Usage:
    from agents.skills.templates.scripts import calculate_kappa, generate_prisma_ascii
    
    # Calculate IRR
    result = calculate_kappa([1,1,0,1], [1,0,0,1])
    print(f"Kappa: {result.kappa:.3f}")
    
    # Generate PRISMA diagram
    from agents.skills.templates.scripts import PRISMAFlowData, generate_ascii
    data = PRISMAFlowData(
        identified=1500,
        duplicates_removed=300,
        screened=1200,
        excluded_screening=800,
        sought_retrieval=400,
        not_retrieved=20,
        assessed_eligibility=380,
        excluded_eligibility=180,
        included=200
    )
    print(generate_ascii(data))
"""

import sys
from pathlib import Path

# Add scripts directory to path for direct imports
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import IRR Calculator functions
try:
    from irr_calculator import (
        calculate_kappa,
        IRRResult,
        print_report as print_irr_report,
        get_disagreements,
        get_recommendations,
        load_from_csv as load_irr_from_csv,
    )
    IRR_AVAILABLE = True
except ImportError as e:
    IRR_AVAILABLE = False
    calculate_kappa = None
    IRRResult = None
    print_irr_report = None
    get_disagreements = None
    get_recommendations = None
    load_irr_from_csv = None

# Import PRISMA Generator functions
try:
    from prisma_generator import (
        PRISMAFlowData,
        generate_ascii as generate_prisma_ascii,
        generate_mermaid as generate_prisma_mermaid,
        generate_json as generate_prisma_json,
        example_data as prisma_example_data,
    )
    PRISMA_AVAILABLE = True
except ImportError as e:
    PRISMA_AVAILABLE = False
    PRISMAFlowData = None
    generate_prisma_ascii = None
    generate_prisma_mermaid = None
    generate_prisma_json = None
    prisma_example_data = None


# Legacy compatibility - wrap functions to match old interface
class IRRCalculator:
    """Wrapper for IRR functions to provide class-based interface."""
    
    def __init__(self):
        if not IRR_AVAILABLE:
            raise ImportError("IRRCalculator requires numpy")
        self._ratings = []
    
    def add_rating(self, item_id: str, rater1: str, rater2: str):
        """Add a rating pair."""
        r1 = 1 if rater1.lower() in ('include', 'yes', '1', 'true') else 0
        r2 = 1 if rater2.lower() in ('include', 'yes', '1', 'true') else 0
        self._ratings.append((item_id, r1, r2))
    
    def calculate(self) -> dict:
        """Calculate Kappa and return results."""
        if not self._ratings:
            raise ValueError("No ratings added")
        
        r1_list = [r[1] for r in self._ratings]
        r2_list = [r[2] for r in self._ratings]
        
        result = calculate_kappa(r1_list, r2_list)
        
        disagreements = [
            {"item_id": item_id, "rater1": "include" if r1 else "exclude", "rater2": "include" if r2 else "exclude"}
            for item_id, r1, r2 in self._ratings if r1 != r2
        ]
        
        return {
            "kappa": result.kappa,
            "percent_agreement": result.percent_agreement,
            "interpretation": result.interpretation,
            "n_items": result.n_items,
            "n_agreements": result.n_agree,
            "n_disagreements": result.n_disagree,
            "disagreements": disagreements
        }
    
    def get_confusion_matrix(self):
        """Get confusion matrix as formatted string."""
        if not self._ratings:
            return "No ratings"
        
        r1_list = [r[1] for r in self._ratings]
        r2_list = [r[2] for r in self._ratings]
        result = calculate_kappa(r1_list, r2_list)
        
        cm = result.confusion_matrix
        return f"""
              R2:Include  R2:Exclude
R1:Include      {cm.get('both_include', 0):^8}  {cm.get('r1_include', 0):^8}
R1:Exclude      {cm.get('r2_include', 0):^8}  {cm.get('both_exclude', 0):^8}
"""


class PRISMAGenerator:
    """Wrapper for PRISMA functions to provide class-based interface."""
    
    def __init__(self):
        if not PRISMA_AVAILABLE:
            raise ImportError("PRISMAGenerator not available")
        self._data = None
    
    def set_counts(self, identified: int, duplicates_removed: int, screened: int,
                   excluded_screening: int, sought_retrieval: int, not_retrieved: int,
                   assessed_eligibility: int, excluded_eligibility: int, included: int):
        """Set PRISMA flow counts (maps to PRISMA 2020 terminology)."""
        self._data = PRISMAFlowData(
            databases_records=identified,
            duplicates_removed=duplicates_removed,
            records_screened=screened,
            records_excluded=excluded_screening,
            reports_sought=sought_retrieval,
            reports_not_retrieved=not_retrieved,
            reports_assessed=assessed_eligibility,
            exclusion_reasons={"Not meeting criteria": excluded_eligibility},
            studies_included=included,
            reports_included=included
        )
    
    def generate_ascii(self) -> str:
        """Generate ASCII diagram."""
        if not self._data:
            raise ValueError("No counts set")
        return generate_prisma_ascii(self._data)
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram."""
        if not self._data:
            raise ValueError("No counts set")
        return generate_prisma_mermaid(self._data)
    
    def generate_json(self) -> dict:
        """Generate JSON structure."""
        if not self._data:
            raise ValueError("No counts set")
        return generate_prisma_json(self._data)


def get_irr_calculator():
    """Get an IRRCalculator instance."""
    return IRRCalculator()


def get_prisma_generator():
    """Get a PRISMAGenerator instance."""
    return PRISMAGenerator()


# Quick convenience functions
def quick_kappa(ratings_rater1: list, ratings_rater2: list) -> dict:
    """
    Quick Cohen's Kappa calculation.
    
    Args:
        ratings_rater1: List of ratings (strings like "include"/"exclude" or ints 0/1)
        ratings_rater2: List of ratings
    
    Returns:
        dict with kappa, percent_agreement, interpretation
    """
    calc = IRRCalculator()
    for i, (r1, r2) in enumerate(zip(ratings_rater1, ratings_rater2)):
        r1_str = str(r1) if isinstance(r1, int) else r1
        r2_str = str(r2) if isinstance(r2, int) else r2
        calc.add_rating(f"item_{i}", r1_str, r2_str)
    return calc.calculate()


def generate_prisma_diagram(counts: dict, format: str = "ascii") -> str:
    """
    Quick PRISMA diagram generation.
    
    Args:
        counts: Dict with required keys
        format: "ascii", "mermaid", or "json"
    
    Returns:
        Diagram as string
    """
    gen = PRISMAGenerator()
    gen.set_counts(**counts)
    
    if format == "ascii":
        return gen.generate_ascii()
    elif format == "mermaid":
        return gen.generate_mermaid()
    elif format == "json":
        import json
        return json.dumps(gen.generate_json(), indent=2)
    else:
        raise ValueError(f"Unknown format: {format}")


__all__ = [
    # Status flags
    "SCRIPTS_DIR",
    "IRR_AVAILABLE",
    "PRISMA_AVAILABLE",
    # IRR direct imports
    "calculate_kappa",
    "IRRResult", 
    "print_irr_report",
    "get_disagreements",
    "get_recommendations",
    "load_irr_from_csv",
    # PRISMA direct imports
    "PRISMAFlowData",
    "generate_prisma_ascii",
    "generate_prisma_mermaid", 
    "generate_prisma_json",
    "prisma_example_data",
    # Wrapper classes (legacy)
    "IRRCalculator",
    "PRISMAGenerator",
    "get_irr_calculator",
    "get_prisma_generator",
    # Convenience functions
    "quick_kappa",
    "generate_prisma_diagram",
]
