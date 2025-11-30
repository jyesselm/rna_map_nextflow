"""Tests for result dataclasses."""

from pathlib import Path

import pytest

from rna_map.analysis.mutation_histogram import MutationHistogram
from rna_map.core.results import BitVectorResult, MappingResult


def test_mapping_result():
    """Test MappingResult dataclass."""
    result = MappingResult(
        sam_path=Path("aligned.sam"),
        fasta_path=Path("ref.fasta"),
        is_paired=True,
        output_dir=Path("output/Mapping_Files"),
    )

    assert result.sam_path == Path("aligned.sam")
    assert result.fasta_path == Path("ref.fasta")
    assert result.is_paired is True
    assert result.output_dir == Path("output/Mapping_Files")


def test_mapping_result_immutable():
    """Test that MappingResult is immutable."""
    from dataclasses import FrozenInstanceError

    result = MappingResult(
        sam_path=Path("aligned.sam"),
        fasta_path=Path("ref.fasta"),
        is_paired=True,
        output_dir=Path("output/Mapping_Files"),
    )

    with pytest.raises(FrozenInstanceError):
        result.is_paired = False


def test_bit_vector_result():
    """Test BitVectorResult dataclass."""
    mut_histos = {
        "seq1": MutationHistogram("seq1", "ATCG", "DMS", 1, 4),
        "seq2": MutationHistogram("seq2", "GCTA", "DMS", 1, 4),
    }

    result = BitVectorResult(
        mutation_histos=mut_histos,
        summary_path=Path("summary.csv"),
        output_dir=Path("output/BitVector_Files"),
    )

    assert len(result.mutation_histos) == 2
    assert "seq1" in result.mutation_histos
    assert "seq2" in result.mutation_histos
    assert result.summary_path == Path("summary.csv")
    assert result.output_dir == Path("output/BitVector_Files")


def test_bit_vector_result_empty_histos():
    """Test BitVectorResult with empty mutation histograms."""
    result = BitVectorResult(
        mutation_histos={},
        summary_path=Path("summary.csv"),
        output_dir=Path("output/BitVector_Files"),
    )

    assert len(result.mutation_histos) == 0
    assert result.summary_path == Path("summary.csv")


# PipelineResult removed - no longer needed after migration to Nextflow
# Tests for PipelineResult removed

