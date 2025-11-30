#!/usr/bin/env python3
"""Analyze top parameter combinations to find constants.

This script analyzes the top N parameter combinations from optimization results
to identify which parameters are constant or most common.
"""

import argparse
import pandas as pd
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any


def analyze_top_parameters(
    csv_file: Path, top_n: int = 100, min_frequency: float = 0.5
) -> Dict[str, Any]:
    """Analyze top N parameter combinations.
    
    Args:
        csv_file: Path to optuna_summary.csv
        top_n: Number of top combinations to analyze
        min_frequency: Minimum frequency to report (0.5 = 50%)
        
    Returns:
        Dictionary with analysis results
    """
    # Read CSV
    df = pd.read_csv(csv_file)
    
    # Filter out failed trials (quality_score = 0)
    df = df[df["quality_score"] > 0].copy()
    
    if len(df) == 0:
        return {"error": "No successful trials found"}
    
    # Sort by quality_score descending
    df_sorted = df.sort_values("quality_score", ascending=False)
    
    # Take top N
    top_df = df_sorted.head(top_n).copy()
    
    print(f"Analyzing top {len(top_df)} parameter combinations")
    print(f"(from {len(df)} total successful trials)")
    print()
    
    # Parameter columns (exclude metrics)
    metric_columns = {
        "trial", "quality_score", "signal_to_noise", "alignment_rate",
        "avg_mapq", "bv_accepted"
    }
    param_columns = [col for col in df.columns if col not in metric_columns]
    
    # Analyze each parameter
    analysis = {
        "top_n": len(top_df),
        "total_trials": len(df),
        "quality_score_range": {
            "min": float(top_df["quality_score"].min()),
            "max": float(top_df["quality_score"].max()),
            "mean": float(top_df["quality_score"].mean()),
            "median": float(top_df["quality_score"].median()),
        },
        "parameters": {},
    }
    
    print("=" * 80)
    print("Parameter Analysis (Top {} Combinations)".format(len(top_df)))
    print("=" * 80)
    print()
    
    # Analyze each parameter
    for param in param_columns:
        if param not in top_df.columns:
            continue
            
        values = top_df[param].dropna()
        if len(values) == 0:
            continue
            
        # Count occurrences
        value_counts = Counter(values)
        total = len(values)
        
        # Calculate frequencies
        frequencies = {str(k): v / total for k, v in value_counts.items()}
        
        # Find most common
        most_common = value_counts.most_common(1)[0]
        most_common_value = most_common[0]
        most_common_freq = most_common[1] / total
        
        # Check if constant
        is_constant = most_common_freq == 1.0
        
        # Store analysis
        analysis["parameters"][param] = {
            "constant": is_constant,
            "most_common_value": str(most_common_value),
            "most_common_frequency": float(most_common_freq),
            "unique_values": len(value_counts),
            "frequencies": frequencies,
        }
        
        # Print results
        if is_constant:
            print(f"✓ {param}: CONSTANT = {most_common_value}")
        elif most_common_freq >= min_frequency:
            print(f"• {param}: {most_common_freq:.1%} = {most_common_value} "
                  f"(out of {len(value_counts)} unique values)")
        else:
            print(f"  {param}: VARIABLE (most common: {most_common_freq:.1%} = {most_common_value})")
    
    print()
    print("=" * 80)
    print("Summary Statistics")
    print("=" * 80)
    print(f"Quality Score Range: {analysis['quality_score_range']['min']:.4f} - "
          f"{analysis['quality_score_range']['max']:.4f}")
    print(f"Average Quality Score: {analysis['quality_score_range']['mean']:.4f}")
    print(f"Median Quality Score: {analysis['quality_score_range']['median']:.4f}")
    print()
    
    # Count constants vs variables
    constants = [p for p, data in analysis["parameters"].items() if data["constant"]]
    high_frequency = [
        p for p, data in analysis["parameters"].items()
        if not data["constant"] and data["most_common_frequency"] >= min_frequency
    ]
    variables = [
        p for p, data in analysis["parameters"].items()
        if not data["constant"] and data["most_common_frequency"] < min_frequency
    ]
    
    print(f"Constants: {len(constants)} parameters")
    for param in constants:
        print(f"  - {param} = {analysis['parameters'][param]['most_common_value']}")
    
    print()
    print(f"High Frequency (≥{min_frequency:.0%}): {len(high_frequency)} parameters")
    for param in high_frequency:
        freq = analysis["parameters"][param]["most_common_frequency"]
        val = analysis["parameters"][param]["most_common_value"]
        print(f"  - {param} = {val} ({freq:.1%})")
    
    print()
    print(f"Variable: {len(variables)} parameters")
    for param in variables:
        freq = analysis["parameters"][param]["most_common_frequency"]
        val = analysis["parameters"][param]["most_common_value"]
        unique = analysis["parameters"][param]["unique_values"]
        print(f"  - {param}: {unique} unique values (most common: {val} at {freq:.1%})")
    
    return analysis


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Analyze top parameter combinations from optimization results"
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="Path to optuna_summary.csv file",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="Number of top combinations to analyze (default: 100)",
    )
    parser.add_argument(
        "--min-frequency",
        type=float,
        default=0.5,
        help="Minimum frequency to report (default: 0.5 = 50%%)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file for detailed analysis (JSON format)",
    )
    
    args = parser.parse_args()
    
    if not args.csv_file.exists():
        print(f"ERROR: File not found: {args.csv_file}")
        return 1
    
    # Analyze
    analysis = analyze_top_parameters(
        args.csv_file, top_n=args.top_n, min_frequency=args.min_frequency
    )
    
    if "error" in analysis:
        print(f"ERROR: {analysis['error']}")
        return 1
    
    # Save output if requested
    if args.output:
        import json
        with open(args.output, "w") as f:
            json.dump(analysis, f, indent=2)
        print()
        print(f"Detailed analysis saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

