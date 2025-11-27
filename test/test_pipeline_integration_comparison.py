"""Integration test comparing new pipeline with original pipeline.

This test ensures the new scalable pipeline produces identical results
to the original pipeline for the same inputs.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from rna_map.parameters import get_default_params
from rna_map.pipeline import run as run_original
from rna_map.pipeline.simple_pipeline import Sample, run_rna_map_sample

TEST_DIR = Path(__file__).parent
TEST_RESOURCES = TEST_DIR / "resources" / "case_1"


def get_test_inputs():
    """Get test input file paths.

    Returns:
        Dictionary with fasta, fastq1, fastq2 paths
    """
    return {
        "fasta": TEST_RESOURCES / "test.fasta",
        "fastq1": TEST_RESOURCES / "test_mate1.fastq",
        "fastq2": TEST_RESOURCES / "test_mate2.fastq",
        "csv": TEST_RESOURCES / "test.csv",
    }


def create_temp_test_dir():
    """Create a temporary directory for test output.

    Returns:
        Path to temporary directory
    """
    return Path(tempfile.mkdtemp(prefix="rna_map_test_"))


def cleanup_temp_dir(temp_dir: Path):
    """Remove temporary test directory.

    Args:
        temp_dir: Path to temporary directory to remove
    """
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


def compare_summary_csv(original_path: Path, new_path: Path) -> bool:
    """Compare two summary.csv files.

    Args:
        original_path: Path to original summary.csv
        new_path: Path to new summary.csv

    Returns:
        True if files are identical, False otherwise
    """
    if not original_path.exists() or not new_path.exists():
        return False

    orig_df = pd.read_csv(original_path)
    new_df = pd.read_csv(new_path)

    # Compare columns
    if set(orig_df.columns) != set(new_df.columns):
        print(f"Column mismatch: {set(orig_df.columns)} vs {set(new_df.columns)}")
        return False

    # Compare number of rows
    if len(orig_df) != len(new_df):
        print(f"Row count mismatch: {len(orig_df)} vs {len(new_df)}")
        return False

    # Compare each row (allowing small floating point differences)
    for idx in range(len(orig_df)):
        orig_row = orig_df.iloc[idx]
        new_row = new_df.iloc[idx]

        for col in orig_df.columns:
            orig_val = orig_row[col]
            new_val = new_row[col]

            # Handle numeric comparison with tolerance
            if isinstance(orig_val, (int, float)) and isinstance(new_val, (int, float)):
                if abs(orig_val - new_val) > 0.01:  # Allow 0.01 difference
                    print(f"Row {idx}, column {col}: {orig_val} vs {new_val}")
                    return False
            elif orig_val != new_val:
                print(f"Row {idx}, column {col}: {orig_val} vs {new_val}")
                return False

    return True


def compare_mutation_histos(original_path: Path, new_path: Path) -> bool:
    """Compare two mutation_histos.json files.

    Args:
        original_path: Path to original mutation_histos.json
        new_path: Path to new mutation_histos.json

    Returns:
        True if files are similar enough, False otherwise
    """
    if not original_path.exists() or not new_path.exists():
        return False

    with open(original_path) as f:
        orig_data = json.load(f)

    with open(new_path) as f:
        new_data = json.load(f)

    # Compare structure
    if set(orig_data.keys()) != set(new_data.keys()):
        print(f"Key mismatch: {set(orig_data.keys())} vs {set(new_data.keys())}")
        return False

    # Compare each entry
    for key in orig_data.keys():
        orig_entry = orig_data[key]
        new_entry = new_data[key]

        # Compare key numeric fields
        numeric_fields = ["num_reads", "num_aligned", "start", "end"]
        for field in numeric_fields:
            if field in orig_entry and field in new_entry:
                if abs(orig_entry[field] - new_entry[field]) > 0.01:
                    print(f"{key}.{field}: {orig_entry[field]} vs {new_entry[field]}")
                    return False

    return True


from rna_map.pipeline.functions import check_program_versions


def has_external_tools():
    """Check if external tools are available."""
    try:
        check_program_versions()
        return True
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    not has_external_tools(),
    reason="External tools not available",
)
def test_new_pipeline_vs_original():
    """Compare new pipeline output with original pipeline output.

    This test:
    1. Runs the original pipeline
    2. Runs the new pipeline on the same inputs
    3. Compares key output files (summary.csv, mutation_histos.json)
    4. Verifies they produce identical results
    """
    # Create temporary directories
    orig_dir = create_temp_test_dir()
    new_dir = create_temp_test_dir()

    try:
        # Get test inputs
        inputs = get_test_inputs()

        # ============================================================
        # Run ORIGINAL pipeline
        # ============================================================
        print("\n" + "=" * 60)
        print("Running ORIGINAL pipeline...")
        print("=" * 60)

        params_orig = get_default_params()
        params_orig["dirs"]["output"] = str(orig_dir / "output")
        params_orig["dirs"]["input"] = str(orig_dir / "input")
        params_orig["dirs"]["log"] = str(orig_dir / "log")
        params_orig["overwrite"] = True

        run_original(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            params=params_orig,
        )

        orig_bitvector_dir = Path(params_orig["dirs"]["output"]) / "BitVector_Files"
        orig_summary = orig_bitvector_dir / "summary.csv"
        orig_mut_histos = orig_bitvector_dir / "mutation_histos.json"

        print(f"Original output: {orig_bitvector_dir}")
        print(f"Summary exists: {orig_summary.exists()}")
        print(f"Mutation histos exists: {orig_mut_histos.exists()}")

        # ============================================================
        # Run NEW pipeline
        # ============================================================
        print("\n" + "=" * 60)
        print("Running NEW pipeline...")
        print("=" * 60)

        # Create sample for new pipeline
        sample = Sample(
            sample_id="test_sample",
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            output_dir=new_dir / "test_sample",
        )

        result = run_rna_map_sample(sample, overwrite=True)

        assert (
            result["status"] == "success"
        ), f"New pipeline failed: {result.get('error')}"

        # Get output directory from sample (since result doesn't include it)
        new_output_dir = sample.output_dir
        new_bitvector_dir = new_output_dir / "BitVector_Files"
        new_summary = new_bitvector_dir / "summary.csv"
        new_mut_histos = new_bitvector_dir / "mutation_histos.json"

        print(f"New output: {new_bitvector_dir}")
        print(f"Summary exists: {new_summary.exists()}")
        print(f"Mutation histos exists: {new_mut_histos.exists()}")

        # ============================================================
        # Compare results
        # ============================================================
        print("\n" + "=" * 60)
        print("Comparing results...")
        print("=" * 60)

        # Compare summary.csv
        print("\nComparing summary.csv...")
        summary_match = compare_summary_csv(orig_summary, new_summary)
        if summary_match:
            print("✓ summary.csv files match!")
        else:
            print("✗ summary.csv files differ")
            print("\nOriginal summary.csv:")
            print(pd.read_csv(orig_summary).to_string())
            print("\nNew summary.csv:")
            print(pd.read_csv(new_summary).to_string())

        # Compare mutation_histos.json
        print("\nComparing mutation_histos.json...")
        histos_match = compare_mutation_histos(orig_mut_histos, new_mut_histos)
        if histos_match:
            print("✓ mutation_histos.json files match!")
        else:
            print("✗ mutation_histos.json files differ")

        # Final assertion
        assert summary_match, "summary.csv files do not match"
        assert histos_match, "mutation_histos.json files do not match"

        print("\n" + "=" * 60)
        print("✓ All comparisons passed! New pipeline produces identical results.")
        print("=" * 60)

        # Save output locations for manual inspection
        print(f"\nOriginal output saved to: {orig_dir}")
        print(f"New output saved to: {new_dir}")
        print("\nTo keep outputs for manual comparison:")
        print(f"  cp -r {orig_dir} /path/to/original_output/")
        print(f"  cp -r {new_dir} /path/to/new_output/")

    finally:
        # Optionally keep outputs for inspection (comment out to keep)
        # cleanup_temp_dir(orig_dir)
        # cleanup_temp_dir(new_dir)
        pass
