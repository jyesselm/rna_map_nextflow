"""Helper script to compare summary.csv and mutation_histos.json between branches.

Usage:
    python test/compare_outputs.py <baseline_dir> <current_dir>

Example:
    # Generate baseline on main branch
    git checkout main
    rna-map -fa test/resources/case_1/test.fasta -fq1 test/resources/case_1/test_mate1.fastq -fq2 test/resources/case_1/test_mate2.fastq
    cp -r output/BitVector_Files baseline_output/

    # Generate current output on refactored branch
    git checkout jdy/ai_improvements
    pytest test/test_integration.py::test_full_pipeline_integration -v -s

    # Compare
    python test/compare_outputs.py baseline_output output/BitVector_Files
"""

import json
import sys
from pathlib import Path

import pandas as pd


def compare_summary_csv(baseline_file: Path, current_file: Path) -> bool:
    """Compare two summary.csv files.

    Args:
        baseline_file: Path to baseline summary.csv
        current_file: Path to current summary.csv

    Returns:
        True if files match, False otherwise
    """
    print(f"\n{'='*60}")
    print("COMPARING SUMMARY.CSV")
    print(f"{'='*60}")

    if not baseline_file.exists():
        print(f"ERROR: Baseline file not found: {baseline_file}")
        return False

    if not current_file.exists():
        print(f"ERROR: Current file not found: {current_file}")
        return False

    baseline_df = pd.read_csv(baseline_file)
    current_df = pd.read_csv(current_file)

    # Compare structure
    if list(baseline_df.columns) != list(current_df.columns):
        print(f"ERROR: Column mismatch")
        print(f"  Baseline columns: {list(baseline_df.columns)}")
        print(f"  Current columns: {list(current_df.columns)}")
        return False

    # Compare number of rows
    if len(baseline_df) != len(current_df):
        print(f"ERROR: Row count mismatch")
        print(f"  Baseline rows: {len(baseline_df)}")
        print(f"  Current rows: {len(current_df)}")
        return False

    # Compare data (with tolerance for floating point)
    matches = True
    for idx in range(len(baseline_df)):
        baseline_row = baseline_df.iloc[idx]
        current_row = current_df.iloc[idx]
        
        for col in baseline_df.columns:
            baseline_val = baseline_row[col]
            current_val = current_row[col]

            # For numeric columns, allow small floating point differences
            if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                if abs(baseline_val - current_val) > 0.01:  # 0.01% tolerance
                    print(f"ERROR: Value mismatch in row {idx}, column '{col}'")
                    print(f"  Baseline: {baseline_val}")
                    print(f"  Current: {current_val}")
                    print(f"  Difference: {abs(baseline_val - current_val)}")
                    matches = False
            elif baseline_val != current_val:
                print(f"ERROR: Value mismatch in row {idx}, column '{col}'")
                print(f"  Baseline: {baseline_val}")
                print(f"  Current: {current_val}")
                matches = False

    if matches:
        print("✓ SUMMARY.CSV MATCHES")
        print(f"\nBaseline summary.csv:")
        print(baseline_df.to_string(index=False))
        print(f"\nCurrent summary.csv:")
        print(current_df.to_string(index=False))
    else:
        print("✗ SUMMARY.CSV DOES NOT MATCH")

    return matches


def compare_mutation_histos_json(baseline_file: Path, current_file: Path) -> bool:
    """Compare two mutation_histos.json files.

    Args:
        baseline_file: Path to baseline mutation_histos.json
        current_file: Path to current mutation_histos.json

    Returns:
        True if files match, False otherwise
    """
    print(f"\n{'='*60}")
    print("COMPARING MUTATION_HISTOS.JSON")
    print(f"{'='*60}")

    if not baseline_file.exists():
        print(f"ERROR: Baseline file not found: {baseline_file}")
        return False

    if not current_file.exists():
        print(f"ERROR: Current file not found: {current_file}")
        return False

    with open(baseline_file, "r") as f:
        baseline_data = json.load(f)

    with open(current_file, "r") as f:
        current_data = json.load(f)

    # Compare structure
    if set(baseline_data.keys()) != set(current_data.keys()):
        print(f"ERROR: Key mismatch")
        print(f"  Baseline keys: {set(baseline_data.keys())}")
        print(f"  Current keys: {set(current_data.keys())}")
        return False

    matches = True
    for key in baseline_data.keys():
        baseline_histo = baseline_data[key]
        current_histo = current_data[key]

        # Compare key numeric fields with tolerance
        numeric_fields = [
            "num_reads",
            "num_aligned",
            "start",
            "end",
        ]

        for field in numeric_fields:
            if field in baseline_histo and field in current_histo:
                baseline_val = baseline_histo[field]
                current_val = current_histo[field]
                if isinstance(baseline_val, (int, float)) and isinstance(current_val, (int, float)):
                    if abs(baseline_val - current_val) > 0.01:
                        print(f"ERROR: Value mismatch in '{key}', field '{field}'")
                        print(f"  Baseline: {baseline_val}")
                        print(f"  Current: {current_val}")
                        matches = False

        # Compare mutation counts dictionaries
        if "num_of_mutations" in baseline_histo and "num_of_mutations" in current_histo:
            baseline_muts = baseline_histo["num_of_mutations"]
            current_muts = current_histo["num_of_mutations"]
            if baseline_muts != current_muts:
                print(f"ERROR: Mutation counts mismatch in '{key}'")
                print(f"  Baseline: {baseline_muts}")
                print(f"  Current: {current_muts}")
                matches = False

    if matches:
        print("✓ MUTATION_HISTOS.JSON MATCHES")
    else:
        print("✗ MUTATION_HISTOS.JSON DOES NOT MATCH")

    return matches


def main():
    """Main comparison function."""
    if len(sys.argv) != 3:
        print("Usage: python test/compare_outputs.py <baseline_dir> <current_dir>")
        print("\nExample:")
        print("  python test/compare_outputs.py baseline_output output/BitVector_Files")
        sys.exit(1)

    baseline_dir = Path(sys.argv[1])
    current_dir = Path(sys.argv[2])

    baseline_summary = baseline_dir / "summary.csv"
    current_summary = current_dir / "summary.csv"
    baseline_mut_histos = baseline_dir / "mutation_histos.json"
    current_mut_histos = current_dir / "mutation_histos.json"

    print(f"Comparing outputs:")
    print(f"  Baseline directory: {baseline_dir}")
    print(f"  Current directory: {current_dir}")

    summary_match = compare_summary_csv(baseline_summary, current_summary)
    mut_histos_match = compare_mutation_histos_json(baseline_mut_histos, current_mut_histos)

    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"  summary.csv: {'✓ MATCH' if summary_match else '✗ MISMATCH'}")
    print(f"  mutation_histos.json: {'✓ MATCH' if mut_histos_match else '✗ MISMATCH'}")

    if summary_match and mut_histos_match:
        print("\n✓ ALL FILES MATCH!")
        sys.exit(0)
    else:
        print("\n✗ FILES DO NOT MATCH")
        sys.exit(1)


if __name__ == "__main__":
    main()

