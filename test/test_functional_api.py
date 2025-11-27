"""Tests for functional APIs."""

from pathlib import Path
import tempfile

import pytest

from rna_map.core.config import BitVectorConfig, MappingConfig
from rna_map.core.inputs import Inputs
from rna_map.core.results import BitVectorResult, MappingResult
from rna_map.pipeline.functions import (
    check_program_versions,
    generate_bit_vectors,
    run_mapping,
)

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


def test_check_program_versions():
    """Test check_program_versions function."""
    try:
        check_program_versions()
    except Exception as e:
        pytest.fail(f"check_program_versions() raised {e}")


def test_run_mapping_basic():
    """Test run_mapping with basic configuration."""
    inputs_dict = get_test_inputs()
    inputs = Inputs(
        fasta=inputs_dict["fasta"],
        fastq1=inputs_dict["fastq1"],
        fastq2=inputs_dict["fastq2"],
    )

    config = MappingConfig(
        skip_fastqc=True,  # Skip to speed up test
        skip_trim_galore=True,  # Skip to speed up test
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_mapping(
            inputs=inputs,
            output_dir=output_dir,
            config=config,
            overwrite=True,
            check_versions=False,  # Skip version check for faster test
        )

        # Verify result structure
        assert isinstance(result, MappingResult)
        assert result.sam_path.exists()
        assert result.fasta_path == Path(inputs.fasta)
        assert result.is_paired is True
        assert result.output_dir.exists()

        # Verify SAM file was created
        assert result.sam_path.name == "aligned.sam"
        assert result.sam_path.stat().st_size > 0


def test_run_mapping_single_end():
    """Test run_mapping with single-end reads."""
    inputs_dict = get_test_inputs()
    inputs = Inputs(
        fasta=inputs_dict["fasta"],
        fastq1=inputs_dict["fastq1"],
        fastq2=Path(""),  # Single-end
    )

    config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_mapping(
            inputs=inputs,
            output_dir=output_dir,
            config=config,
            overwrite=True,
            check_versions=False,
        )

        assert isinstance(result, MappingResult)
        assert result.is_paired is False
        assert result.sam_path.exists()


def test_run_mapping_with_custom_config():
    """Test run_mapping with custom configuration."""
    inputs_dict = get_test_inputs()
    inputs = Inputs(
        fasta=inputs_dict["fasta"],
        fastq1=inputs_dict["fastq1"],
        fastq2=inputs_dict["fastq2"],
    )

    config = MappingConfig(
        skip_fastqc=True,
        skip_trim_galore=True,
        tg_q_cutoff=25,
        bt2_alignment_args="--local;--no-unal;-p 4",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_mapping(
            inputs=inputs,
            output_dir=output_dir,
            config=config,
            overwrite=True,
            check_versions=False,
        )

        assert isinstance(result, MappingResult)
        assert result.sam_path.exists()


@pytest.mark.integration
def test_generate_bit_vectors_basic():
    """Test generate_bit_vectors with basic configuration."""
    inputs_dict = get_test_inputs()

    # First, we need a SAM file - use existing one if available
    existing_sam = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    if not existing_sam.exists():
        pytest.skip("No existing SAM file found, skipping test")

    config = BitVectorConfig(
        qscore_cutoff=25,
        map_score_cutoff=15,
        summary_output_only=True,  # Faster test
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = generate_bit_vectors(
            sam_path=existing_sam,
            fasta=inputs_dict["fasta"],
            output_dir=output_dir,
            config=config,
            csv_file=inputs_dict["csv"],
            paired=True,
        )

        # Verify result structure
        assert isinstance(result, BitVectorResult)
        assert result.summary_path.exists()
        assert result.output_dir.exists()

        # Verify summary file was created
        assert result.summary_path.name == "summary.csv"
        assert result.summary_path.stat().st_size > 0


@pytest.mark.integration
def test_generate_bit_vectors_with_stricter():
    """Test generate_bit_vectors with stricter constraints."""
    inputs_dict = get_test_inputs()

    existing_sam = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    if not existing_sam.exists():
        pytest.skip("No existing SAM file found, skipping test")

    from rna_map.core.config import StricterConstraints

    stricter = StricterConstraints(
        min_mut_distance=5,
        percent_length_cutoff=0.10,
        mutation_count_cutoff=5,
    )

    config = BitVectorConfig(
        qscore_cutoff=25,
        map_score_cutoff=15,
        stricter_constraints=stricter,
        summary_output_only=True,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = generate_bit_vectors(
            sam_path=existing_sam,
            fasta=inputs_dict["fasta"],
            output_dir=output_dir,
            config=config,
            csv_file=inputs_dict["csv"],
            paired=True,
            use_stricter_constraints=True,
        )

        assert isinstance(result, BitVectorResult)
        assert result.summary_path.exists()


def test_generate_bit_vectors_auto_detect_paired():
    """Test generate_bit_vectors with auto-detection of paired-end."""
    inputs_dict = get_test_inputs()

    existing_sam = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    if not existing_sam.exists():
        pytest.skip("No existing SAM file found, skipping test")

    config = BitVectorConfig(summary_output_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = generate_bit_vectors(
            sam_path=existing_sam,
            fasta=inputs_dict["fasta"],
            output_dir=output_dir,
            config=config,
            paired=None,  # Auto-detect
        )

        assert isinstance(result, BitVectorResult)
        assert result.summary_path.exists()


@pytest.mark.integration
def test_full_pipeline_functional():
    """Test full pipeline using functional APIs."""
    inputs_dict = get_test_inputs()
    inputs = Inputs(
        fasta=inputs_dict["fasta"],
        fastq1=inputs_dict["fastq1"],
        fastq2=inputs_dict["fastq2"],
    )

    mapping_config = MappingConfig(
        skip_fastqc=True,
        skip_trim_galore=True,
    )

    bv_config = BitVectorConfig(
        summary_output_only=True,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"

        # Step 1: Run mapping
        mapping_result = run_mapping(
            inputs=inputs,
            output_dir=output_dir,
            config=mapping_config,
            overwrite=True,
            check_versions=False,
        )

        assert mapping_result.sam_path.exists()

        # Step 2: Generate bit vectors
        bv_result = generate_bit_vectors(
            sam_path=mapping_result.sam_path,
            fasta=mapping_result.fasta_path,
            output_dir=output_dir,
            config=bv_config,
            csv_file=inputs_dict["csv"],
            paired=mapping_result.is_paired,
        )

        assert bv_result.summary_path.exists()

        # Verify both results are accessible
        assert isinstance(mapping_result, MappingResult)
        assert isinstance(bv_result, BitVectorResult)


def test_run_mapping_output_structure():
    """Test that run_mapping creates correct output structure."""
    inputs_dict = get_test_inputs()
    inputs = Inputs(
        fasta=inputs_dict["fasta"],
        fastq1=inputs_dict["fastq1"],
        fastq2=inputs_dict["fastq2"],
    )

    config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = run_mapping(
            inputs=inputs,
            output_dir=output_dir,
            config=config,
            overwrite=True,
            check_versions=False,
        )

        # Verify directory structure
        assert result.output_dir.exists()
        assert (result.output_dir / "aligned.sam").exists()
        assert result.output_dir.name == "Mapping_Files"


def test_generate_bit_vectors_output_structure():
    """Test that generate_bit_vectors creates correct output structure."""
    inputs_dict = get_test_inputs()

    existing_sam = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    if not existing_sam.exists():
        pytest.skip("No existing SAM file found, skipping test")

    config = BitVectorConfig(summary_output_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = generate_bit_vectors(
            sam_path=existing_sam,
            fasta=inputs_dict["fasta"],
            output_dir=output_dir,
            config=config,
            paired=True,
        )

        # Verify directory structure
        assert result.output_dir.exists()
        assert result.output_dir.name == "BitVector_Files"
        assert result.summary_path.exists()
        assert (result.output_dir / "mutation_histos.p").exists()
        assert (result.output_dir / "mutation_histos.json").exists()

