"""
Inter-Rater Reliability Calculator for Screening

Calculates Cohen's Kappa and percent agreement for screening decisions.
Supports both Title/Abstract and Full-text screening phases.

Usage:
    python irr_calculator.py --file screening_data.csv
    python irr_calculator.py --r1 "1,1,0,1,0" --r2 "1,0,0,1,0"
"""

import argparse
import json
import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class IRRResult:
    """Inter-rater reliability result."""
    kappa: float
    percent_agreement: float
    n_items: int
    n_agree: int
    n_disagree: int
    confusion_matrix: Dict[str, int]
    interpretation: str
    
    def to_dict(self) -> dict:
        return {
            "kappa": round(self.kappa, 3),
            "percent_agreement": round(self.percent_agreement, 1),
            "n_items": self.n_items,
            "n_agree": self.n_agree,
            "n_disagree": self.n_disagree,
            "confusion_matrix": self.confusion_matrix,
            "interpretation": self.interpretation
        }


def calculate_kappa(reviewer1: List[int], reviewer2: List[int]) -> IRRResult:
    """
    Calculate Cohen's Kappa coefficient.
    
    Args:
        reviewer1: List of binary decisions (0=exclude, 1=include)
        reviewer2: List of binary decisions (0=exclude, 1=include)
    
    Returns:
        IRRResult with kappa, agreement, and interpretation
    """
    if len(reviewer1) != len(reviewer2):
        raise ValueError("Reviewer lists must have equal length")
    
    n = len(reviewer1)
    
    # Confusion matrix
    a = sum(1 for r1, r2 in zip(reviewer1, reviewer2) if r1 == 1 and r2 == 1)  # Both include
    b = sum(1 for r1, r2 in zip(reviewer1, reviewer2) if r1 == 1 and r2 == 0)  # R1 include, R2 exclude
    c = sum(1 for r1, r2 in zip(reviewer1, reviewer2) if r1 == 0 and r2 == 1)  # R1 exclude, R2 include
    d = sum(1 for r1, r2 in zip(reviewer1, reviewer2) if r1 == 0 and r2 == 0)  # Both exclude
    
    # Observed agreement
    po = (a + d) / n
    
    # Expected agreement (by chance)
    p_yes = ((a + b) / n) * ((a + c) / n)
    p_no = ((c + d) / n) * ((b + d) / n)
    pe = p_yes + p_no
    
    # Cohen's Kappa
    if pe == 1:
        kappa = 1.0  # Perfect agreement by chance
    else:
        kappa = (po - pe) / (1 - pe)
    
    # Interpretation (Landis & Koch, 1977)
    if kappa < 0:
        interpretation = "Poor (less than chance)"
    elif kappa < 0.21:
        interpretation = "Slight"
    elif kappa < 0.41:
        interpretation = "Fair"
    elif kappa < 0.61:
        interpretation = "Moderate"
    elif kappa < 0.81:
        interpretation = "Substantial"
    else:
        interpretation = "Almost perfect"
    
    return IRRResult(
        kappa=kappa,
        percent_agreement=po * 100,
        n_items=n,
        n_agree=a + d,
        n_disagree=b + c,
        confusion_matrix={
            "both_include": a,
            "r1_include_r2_exclude": b,
            "r1_exclude_r2_include": c,
            "both_exclude": d
        },
        interpretation=interpretation
    )


def print_report(result: IRRResult, phase: str = "Screening") -> None:
    """Print formatted IRR report."""
    print("\n" + "=" * 60)
    print(f"INTER-RATER RELIABILITY REPORT: {phase}")
    print("=" * 60)
    
    print(f"\nCohen's Kappa: κ = {result.kappa:.3f}")
    print(f"Interpretation: {result.interpretation}")
    print(f"\nPercent Agreement: {result.percent_agreement:.1f}%")
    print(f"Items Reviewed: {result.n_items}")
    print(f"  - Agreements: {result.n_agree}")
    print(f"  - Disagreements: {result.n_disagree}")
    
    print("\nConfusion Matrix:")
    print("                 Reviewer 2")
    print("                 Include   Exclude")
    print(f"Reviewer 1 Include  {result.confusion_matrix['both_include']:5d}     {result.confusion_matrix['r1_include_r2_exclude']:5d}")
    print(f"           Exclude  {result.confusion_matrix['r1_exclude_r2_include']:5d}     {result.confusion_matrix['both_exclude']:5d}")
    
    # Recommendations
    print("\nRecommendation:")
    if result.kappa >= 0.8:
        print("  ✓ Excellent agreement. Proceed with independent screening.")
    elif result.kappa >= 0.6:
        print("  ⚠ Substantial agreement. Review disagreements before proceeding.")
    else:
        print("  ✗ Agreement below threshold. Conduct calibration meeting.")
        print("    Review eligibility criteria and resolve conflicts.")
    
    print("=" * 60)


def load_from_csv(filepath: str) -> Tuple[List[int], List[int], List[str]]:
    """
    Load screening decisions from CSV file.
    
    Expected format:
    study_id,reviewer1,reviewer2
    Study001,1,1
    Study002,0,1
    ...
    
    Returns:
        Tuple of (reviewer1_decisions, reviewer2_decisions, study_ids)
    """
    r1, r2, ids = [], [], []
    
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.append(row.get('study_id', ''))
            r1.append(int(row['reviewer1']))
            r2.append(int(row['reviewer2']))
    
    return r1, r2, ids


def get_disagreements(r1: List[int], r2: List[int], ids: List[str]) -> List[Dict]:
    """Get list of disagreements for resolution."""
    disagreements = []
    for i, (v1, v2) in enumerate(zip(r1, r2)):
        if v1 != v2:
            disagreements.append({
                "study_id": ids[i] if ids else f"Item_{i+1}",
                "reviewer1": "Include" if v1 == 1 else "Exclude",
                "reviewer2": "Include" if v2 == 1 else "Exclude"
            })
    return disagreements


def export_report(result: IRRResult, disagreements: List[Dict], 
                  output_path: str) -> None:
    """Export IRR report to JSON."""
    report = {
        "irr_statistics": result.to_dict(),
        "disagreements": disagreements,
        "recommendations": get_recommendations(result)
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport exported to: {output_path}")


def get_recommendations(result: IRRResult) -> List[str]:
    """Get actionable recommendations based on IRR."""
    recs = []
    
    if result.kappa < 0.6:
        recs.append("Schedule calibration meeting to review criteria")
        recs.append("Discuss all disagreements together")
        recs.append("Consider revising eligibility criteria for clarity")
    
    if result.kappa >= 0.6 and result.kappa < 0.8:
        recs.append("Review disagreements and document resolution")
        recs.append("May proceed with screening but monitor agreement")
    
    if result.kappa >= 0.8:
        recs.append("Agreement excellent - proceed with independent screening")
        recs.append("Resolve any disagreements through discussion")
    
    # Specific patterns
    cm = result.confusion_matrix
    if cm['r1_include_r2_exclude'] > cm['r1_exclude_r2_include'] * 2:
        recs.append("Reviewer 1 appears more inclusive - align on thresholds")
    elif cm['r1_exclude_r2_include'] > cm['r1_include_r2_exclude'] * 2:
        recs.append("Reviewer 2 appears more inclusive - align on thresholds")
    
    return recs


def main():
    parser = argparse.ArgumentParser(
        description="Calculate Inter-Rater Reliability for Screening"
    )
    parser.add_argument(
        "--file", "-f", 
        help="CSV file with screening decisions"
    )
    parser.add_argument(
        "--r1", 
        help="Reviewer 1 decisions (comma-separated: 1,0,1,1,0)"
    )
    parser.add_argument(
        "--r2", 
        help="Reviewer 2 decisions (comma-separated: 1,0,1,1,0)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file for report"
    )
    parser.add_argument(
        "--phase",
        default="Title/Abstract Screening",
        help="Screening phase name"
    )
    
    args = parser.parse_args()
    
    # Load data
    if args.file:
        r1, r2, ids = load_from_csv(args.file)
    elif args.r1 and args.r2:
        r1 = [int(x.strip()) for x in args.r1.split(",")]
        r2 = [int(x.strip()) for x in args.r2.split(",")]
        ids = [f"Item_{i+1}" for i in range(len(r1))]
    else:
        # Demo data
        print("No data provided. Running demo...")
        r1 = [1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1]
        r2 = [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1]
        ids = [f"Study{i+1:03d}" for i in range(len(r1))]
    
    # Calculate IRR
    result = calculate_kappa(r1, r2)
    
    # Print report
    print_report(result, args.phase)
    
    # Get disagreements
    disagreements = get_disagreements(r1, r2, ids)
    if disagreements:
        print(f"\nDisagreements ({len(disagreements)}):")
        for d in disagreements:
            print(f"  - {d['study_id']}: R1={d['reviewer1']}, R2={d['reviewer2']}")
    
    # Export if requested
    if args.output:
        export_report(result, disagreements, args.output)


if __name__ == "__main__":
    main()
