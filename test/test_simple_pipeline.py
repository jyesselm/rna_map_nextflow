"""Tests for simple pipeline components."""

from pathlib import Path
import tempfile

import pytest

from rna_map.pipeline.simple_pipeline import (
    Sample,
    demultiplex_fastq,
    process_samples,
    run_rna_map_sample,
)


def test_sample_creation():
    """Test Sample dataclass creation."""
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("test.fasta"),
        fastq1=Path("test_R1.fastq"),
        fastq2=Path("test_R2.fastq"),
    )
    assert sample.sample_id == "test_sample"
    assert sample.fasta == Path("test.fasta")
    assert sample.fastq1 == Path("test_R1.fastq")
    assert sample.fastq2 == Path("test_R2.fastq")


def test_sample_default_output_dir():
    """Test Sample creates default output directory."""
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("test.fasta"),
        fastq1=Path("test_R1.fastq"),
    )
    assert sample.output_dir == Path("results") / "test_sample"


def test_sample_custom_output_dir():
    """Test Sample with custom output directory."""
    custom_dir = Path("custom") / "output"
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("test.fasta"),
        fastq1=Path("test_R1.fastq"),
        output_dir=custom_dir,
    )
    assert sample.output_dir == custom_dir


def test_sample_optional_fields():
    """Test Sample with optional fields."""
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("test.fasta"),
        fastq1=Path("test_R1.fastq"),
        dot_bracket=Path("test.csv"),
        barcode="ATCG",
    )
    assert sample.dot_bracket == Path("test.csv")
    assert sample.barcode == "ATCG"


def test_sample_single_end():
    """Test Sample for single-end reads."""
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("test.fasta"),
        fastq1=Path("test_R1.fastq"),
        fastq2=None,
    )
    assert sample.fastq2 is None


@pytest.mark.integration
def test_run_rna_map_sample_success():
    """Test run_rna_map_sample with valid inputs."""
    from rna_map.core.config import MappingConfig, BitVectorConfig
    from rna_map.external import does_program_exist

    # Skip if external tools not available
    if not all(does_program_exist(p) for p in ["bowtie2", "fastqc"]):
        pytest.skip("External tools not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        fasta = test_dir / "test.fasta"
        fastq1 = test_dir / "test_R1.fastq"
        fastq2 = test_dir / "test_R2.fastq"

        # Create minimal test files
        fasta.write_text(">test\nATCG\n")
        fastq1.write_text("@read1\nATCG\n+\nIIII\n")
        fastq2.write_text("@read1\nCGAT\n+\nIIII\n")

        sample = Sample(
            sample_id="test_sample",
            fasta=fasta,
            fastq1=fastq1,
            fastq2=fastq2,
            output_dir=test_dir / "output",
        )

        config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)
        bv_config = BitVectorConfig(summary_output_only=True)

        result = run_rna_map_sample(sample, config, bv_config, overwrite=True)

        assert result["status"] == "success"
        assert result["sample_id"] == "test_sample"
        assert "sam_path" in result


def test_run_rna_map_sample_missing_file():
    """Test run_rna_map_sample with missing file."""
    sample = Sample(
        sample_id="test_sample",
        fasta=Path("nonexistent.fasta"),
        fastq1=Path("nonexistent_R1.fastq"),
    )

    result = run_rna_map_sample(sample)

    assert result["status"] == "error"
    assert "error" in result


@pytest.mark.integration
def test_process_samples():
    """Test process_samples with multiple samples."""
    from rna_map.core.config import MappingConfig
    from rna_map.external import does_program_exist

    # Skip if external tools not available
    if not all(does_program_exist(p) for p in ["bowtie2", "fastqc"]):
        pytest.skip("External tools not available")

    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir)
        fasta = test_dir / "test.fasta"
        fastq1 = test_dir / "test_R1.fastq"

        fasta.write_text(">test\nATCG\n")
        fastq1.write_text("@read1\nATCG\n+\nIIII\n")

        samples = [
            Sample(
                sample_id=f"sample_{i}",
                fasta=fasta,
                fastq1=fastq1,
                output_dir=test_dir / f"output_{i}",
            )
            for i in range(2)
        ]

        config = MappingConfig(skip_fastqc=True, skip_trim_galore=True)
        results = process_samples(samples, mapping_config=config, overwrite=True)

        assert len(results) == 2
        assert all("status" in r for r in results)
