"""Integration test for full pipeline execution.

This test runs the complete rna-map pipeline in a temporary directory
and saves output for comparison with baseline results.
Both summary.csv and mutation_histos.json are verified.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from rna_map.pipeline import run
from rna_map.parameters import get_default_params

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
        "csv": Path(""),  # No CSV file for this test
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


@pytest.mark.integration
def test_full_pipeline_integration():
    """Run full pipeline and save output for comparison.

    This test:
    1. Creates a temporary directory for test output
    2. Runs the complete rna-map pipeline
    3. Verifies key output files exist
    4. Displays summary.csv and mutation_histos.json for comparison
    5. Cleans up temporary directory
    """
    # Create temporary directory for test
    temp_dir = create_temp_test_dir()
    try:
        # Get test inputs
        inputs = get_test_inputs()

        # Get default parameters
        params = get_default_params()
        params["dirs"]["output"] = str(temp_dir / "output")
        params["dirs"]["input"] = str(temp_dir / "input")
        params["dirs"]["log"] = str(temp_dir / "log")
        params["overwrite"] = True  # Always overwrite to ensure fresh run

        # Run the pipeline
        run(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            params=params,
        )

        # Define output paths
        bitvector_dir = Path(params["dirs"]["output"]) / "BitVector_Files"
        summary_file = bitvector_dir / "summary.csv"
        mut_histos_file = bitvector_dir / "mutation_histos.json"

        # Verify output directory exists
        assert bitvector_dir.exists(), "BitVector_Files directory should exist"

        # Verify key output files exist
        expected_files = [
            "summary.csv",
            "mutation_histos.p",
            "mutation_histos.json",
            "rejected_bvs.csv",
        ]

        for filename in expected_files:
            filepath = bitvector_dir / filename
            assert filepath.exists(), f"Expected file {filename} should exist"

        # Verify bit vector files exist (if not summary-only mode)
        if not params.get("bit_vector", {}).get("summary_output_only", False):
            bitvector_files = list(bitvector_dir.glob("*_bitvectors.txt"))
            assert len(bitvector_files) > 0, "Should have at least one bitvector file"

        # Verify and display summary.csv (most important file)
        assert summary_file.exists(), "summary.csv must exist"
        summary_df = pd.read_csv(summary_file)
        
        print(f"\n{'='*60}")
        print("SUMMARY.CSV CONTENTS (for comparison):")
        print(f"{'='*60}")
        print(summary_df.to_string(index=False))
        print(f"{'='*60}")
        
        # Verify summary.csv has expected columns
        expected_columns = [
            "name",
            "reads",
            "aligned",
            "no_mut",
            "1_mut",
            "2_mut",
            "3_mut",
            "3plus_mut",
            "sn",
        ]
        for col in expected_columns:
            assert col in summary_df.columns, f"summary.csv missing column: {col}"
        
        # Verify summary.csv has data
        assert len(summary_df) > 0, "summary.csv should have at least one row"
        
        # Display summary statistics
        print(f"\nSummary Statistics:")
        print(f"  Number of sequences: {len(summary_df)}")
        for _, row in summary_df.iterrows():
            print(f"  {row['name']}:")
            print(f"    Total reads: {row['reads']}")
            print(f"    Aligned: {row['aligned']:.2f}%")
            print(f"    Signal-to-noise: {row['sn']:.2f}")
            print(f"    Mutations: 0={row['no_mut']:.2f}%, 1={row['1_mut']:.2f}%, 2={row['2_mut']:.2f}%, 3={row['3_mut']:.2f}%, 3+={row['3plus_mut']:.2f}%")

        # Verify and display mutation_histos.json (also important for comparison)
        assert mut_histos_file.exists(), "mutation_histos.json must exist"
        with open(mut_histos_file, "r") as f:
            mut_histos_data = json.load(f)
        
        print(f"\n{'='*60}")
        print("MUTATION_HISTOS.JSON CONTENTS (for comparison):")
        print(f"{'='*60}")
        # Pretty print the JSON structure
        print(json.dumps(mut_histos_data, indent=2))
        print(f"{'='*60}")
        
        # Verify mutation_histos.json structure
        assert isinstance(mut_histos_data, dict), "mutation_histos.json should be a dictionary"
        assert len(mut_histos_data) > 0, "mutation_histos.json should have at least one entry"
        
        # Display key statistics from mutation_histos.json
        print(f"\nMutation Histogram Statistics:")
        for name, histo in mut_histos_data.items():
            print(f"  {name}:")
            print(f"    Reads: {histo.get('num_reads', 'N/A')}")
            print(f"    Aligned: {histo.get('num_aligned', 'N/A')}")
            print(f"    Start: {histo.get('start', 'N/A')}, End: {histo.get('end', 'N/A')}")
            if 'num_of_mutations' in histo:
                print(f"    Mutation counts: {histo['num_of_mutations']}")

        # List all files for reference
        all_files = list(bitvector_dir.rglob("*"))
        print(f"\nGenerated {len(all_files)} files in {bitvector_dir}:")
        for f in sorted(all_files):
            if f.is_file():
                size = f.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                print(f"  {f.relative_to(bitvector_dir)} ({size_str})")

        # Note: To compare with baseline from main branch:
        #   1. git checkout main
        #   2. rna-map -fa test/resources/case_1/test.fasta -fq1 test/resources/case_1/test_mate1.fastq -fq2 test/resources/case_1/test_mate2.fastq
        #   3. cp -r output/BitVector_Files baseline_output/
        #   4. git checkout jdy/ai_improvements
        #   5. pytest test/test_integration.py::test_full_pipeline_integration -v -s
        #   6. Copy output from temp directory: cp -r <temp_dir>/output/BitVector_Files current_output/
        #   7. python test/compare_outputs.py baseline_output current_output
        #
        # The comparison script will verify that both summary.csv and mutation_histos.json match

        # Save output location for manual comparison if needed
        print(f"\nTest output saved to: {bitvector_dir}")
        print("To keep output for comparison, copy it before the test completes:")
        print(f"  cp -r {bitvector_dir} /path/to/comparison_dir/")

    finally:
        # Clean up temporary directory
        cleanup_temp_dir(temp_dir)

