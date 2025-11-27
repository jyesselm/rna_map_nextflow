"""Tests for functional orchestrator."""

from pathlib import Path
import tempfile

import pytest

from rna_map.core.config import BitVectorConfig, MappingConfig
from rna_map.core.results import PipelineResult
from rna_map.pipeline.orchestrator_functional import run_functional

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


@pytest.mark.integration
def test_run_functional_basic():
    """Test run_functional with basic configuration."""
    inputs = get_test_inputs()

    mapping_config = MappingConfig(
        skip_fastqc=True,
        skip_trim_galore=True,
    )

    bv_config = BitVectorConfig(
        summary_output_only=True,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_functional(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            output_dir=output_dir,
            mapping_config=mapping_config,
            bv_config=bv_config,
            overwrite=True,
            check_versions=False,
        )

        # Verify result structure
        assert isinstance(result, PipelineResult)
        assert result.mapping.sam_path.exists()
        assert result.bit_vectors.summary_path.exists()
        assert result.mapping.is_paired is True


@pytest.mark.integration
def test_run_functional_with_params():
    """Test run_functional with params dict (backward compatibility)."""
    inputs = get_test_inputs()

    from rna_map.parameters import get_default_params

    params = get_default_params()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        params["dirs"]["output"] = str(output_dir)
        params["dirs"]["input"] = str(output_dir / "input")
        params["dirs"]["log"] = str(output_dir / "log")
        params["overwrite"] = True

        result = run_functional(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            params=params,
            check_versions=False,
        )

        assert isinstance(result, PipelineResult)
        assert result.mapping.sam_path.exists()


@pytest.mark.integration
def test_run_functional_skip_mapping():
    """Test run_functional with skip_mapping option."""
    inputs = get_test_inputs()

    # First, create a SAM file
    mapping_config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)
    bv_config = BitVectorConfig(summary_output_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"

        # Run mapping first
        from rna_map.core.inputs import Inputs
        from rna_map.pipeline.functions import run_mapping

        ins = Inputs(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
        )

        mapping_result = run_mapping(
            inputs=ins,
            output_dir=output_dir,
            config=mapping_config,
            overwrite=True,
            check_versions=False,
        )

        # Now test skip_mapping
        result = run_functional(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2=inputs["fastq2"],
            dot_bracket=inputs["csv"],
            output_dir=output_dir,
            mapping_config=mapping_config,
            bv_config=bv_config,
            skip_mapping=True,
            sam_path=mapping_result.sam_path,
            overwrite=True,
            check_versions=False,
        )

        assert isinstance(result, PipelineResult)
        assert result.mapping.sam_path == mapping_result.sam_path
        assert result.bit_vectors.summary_path.exists()


def test_run_functional_skip_mapping_no_sam():
    """Test run_functional raises error when skip_mapping=True but no sam_path."""
    inputs = get_test_inputs()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        with pytest.raises(ValueError, match="sam_path is required"):
            run_functional(
                fasta=inputs["fasta"],
                fastq1=inputs["fastq1"],
                fastq2=inputs["fastq2"],
                dot_bracket=inputs["csv"],
                output_dir=output_dir,
                skip_mapping=True,
                sam_path=None,
                check_versions=False,
            )


@pytest.mark.integration
def test_run_functional_single_end():
    """Test run_functional with single-end reads."""
    inputs = get_test_inputs()

    mapping_config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)
    bv_config = BitVectorConfig(summary_output_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_functional(
            fasta=inputs["fasta"],
            fastq1=inputs["fastq1"],
            fastq2="",  # Single-end
            dot_bracket=inputs["csv"],
            output_dir=output_dir,
            mapping_config=mapping_config,
            bv_config=bv_config,
            overwrite=True,
            check_versions=False,
        )

        assert isinstance(result, PipelineResult)
        assert result.mapping.is_paired is False
        assert result.mapping.sam_path.exists()

