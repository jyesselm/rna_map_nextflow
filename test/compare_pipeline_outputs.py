#!/usr/bin/env python3
"""Script to compare outputs from original and new pipeline.

Usage:
    python test/compare_pipeline_outputs.py original_output/ new_output/
"""

import json
import sys
from pathlib import Path

import pandas as pd


def compare_summary_csv(original_path: Path, new_path: Path) -> bool:
    """Compare two summary.csv files."""
    if not original_path.exists():
        print(f"ERROR: Original summary.csv not found: {original_path}")
        return False
    if not new_path.exists():
        print(f"ERROR: New summary.csv not found: {new_path}")
        return False

    orig_df = pd.read_csv(original_path)
    new_df = pd.read_csv(new_path)

    print("\n" + "=" * 60)
    print("COMPARING summary.csv")
    print("=" * 60)

    # Compare columns
    if set(orig_df.columns) != set(new_df.columns):
        print(f"✗ Column mismatch!")
        print(f"  Original: {set(orig_df.columns)}")
        print(f"  New:      {set(new_df.columns)}")
        return False
    print("✓ Columns match")

    # Compare number of rows
    if len(orig_df) != len(new_df):
        print(f"✗ Row count mismatch: {len(orig_df)} vs {len(new_df)}")
        return False
    print(f"✓ Row count matches: {len(orig_df)}")

    # Compare values
    all_match = True
    for idx, (orig_row, new_row) in enumerate(zip(orig_df.itertuples(), new_df.itertuples())):
        for col in orig_df.columns:
            orig_val = getattr(orig_row, col)
            new_val = getattr(new_row, col)

            if isinstance(orig_val, (int, float)) and isinstance(new_val, (int, float)):
                diff = abs(orig_val - new_val)
                if diff > 0.01:
                    print(f"✗ Row {idx}, {col}: {orig_val} vs {new_val} (diff: {diff})")
                    all_match = False
            elif orig_val != new_val:
                print(f"✗ Row {idx}, {col}: {orig_val} vs {new_val}")
                all_match = False

    if all_match:
        print("✓ All values match!")
        print("\nOriginal summary.csv:")
        print(orig_df.to_string(index=False))
    else:
        print("\nOriginal summary.csv:")
        print(orig_df.to_string(index=False))
        print("\nNew summary.csv:")
        print(new_df.to_string(index=False))

    return all_match


def compare_mutation_histos(original_path: Path, new_path: Path) -> bool:
    """Compare two mutation_histos.json files."""
    if not original_path.exists():
        print(f"ERROR: Original mutation_histos.json not found: {original_path}")
        return False
    if not new_path.exists():
        print(f"ERROR: New mutation_histos.json not found: {new_path}")
        return False

    with open(original_path) as f:
        orig_data = json.load(f)

    with open(new_path) as f:
        new_data = json.load(f)

    print("\n" + "=" * 60)
    print("COMPARING mutation_histos.json")
    print("=" * 60)

    # Compare keys
    if set(orig_data.keys()) != set(new_data.keys()):
        print(f"✗ Key mismatch!")
        print(f"  Original: {set(orig_data.keys())}")
        print(f"  New:      {set(new_data.keys())}")
        return False
    print(f"✓ Keys match: {list(orig_data.keys())}")

    # Compare values
    all_match = True
    for key in orig_data.keys():
        orig_entry = orig_data[key]
        new_entry = new_data[key]

        numeric_fields = ["num_reads", "num_aligned", "start", "end"]
        for field in numeric_fields:
            if field in orig_entry and field in new_entry:
                diff = abs(orig_entry[field] - new_entry[field])
                if diff > 0.01:
                    print(f"✗ {key}.{field}: {orig_entry[field]} vs {new_entry[field]} (diff: {diff})")
                    all_match = False

    if all_match:
        print("✓ All values match!")

    return all_match


def main():
    """Main comparison function."""
    if len(sys.argv) != 3:
        print("Usage: python compare_pipeline_outputs.py original_output/ new_output/")
        print("\nExample:")
        print("  python test/compare_pipeline_outputs.py \\")
        print("    /tmp/rna_map_test_xxx/output/BitVector_Files \\")
        print("    /tmp/rna_map_test_yyy/test_sample/BitVector_Files")
        sys.exit(1)

    orig_dir = Path(sys.argv[1])
    new_dir = Path(sys.argv[2])

    print("=" * 60)
    print("PIPELINE OUTPUT COMPARISON")
    print("=" * 60)
    print(f"Original: {orig_dir}")
    print(f"New:      {new_dir}")

    # Compare summary.csv
    orig_summary = orig_dir / "summary.csv"
    new_summary = new_dir / "summary.csv"
    summary_match = compare_summary_csv(orig_summary, new_summary)

    # Compare mutation_histos.json
    orig_histos = orig_dir / "mutation_histos.json"
    new_histos = new_dir / "mutation_histos.json"
    histos_match = compare_mutation_histos(orig_histos, new_histos)

    # Final result
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    if summary_match and histos_match:
        print("✓ ALL COMPARISONS PASSED!")
        print("  The new pipeline produces identical results to the original.")
        sys.exit(0)
    else:
        print("✗ COMPARISONS FAILED")
        if not summary_match:
            print("  - summary.csv does not match")
        if not histos_match:
            print("  - mutation_histos.json does not match")
        sys.exit(1)


if __name__ == "__main__":
    main()

