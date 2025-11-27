"""Result dataclasses for RNA MAP pipeline components."""

from dataclasses import dataclass
from pathlib import Path

from rna_map.analysis.mutation_histogram import MutationHistogram


@dataclass(frozen=True)
class MappingResult:
    """Result from mapping pipeline.

    Attributes:
        sam_path: Path to aligned SAM file
        fasta_path: Path to FASTA file used
        is_paired: Whether reads were paired-end
        output_dir: Output directory for mapping files
    """

    sam_path: Path
    fasta_path: Path
    is_paired: bool
    output_dir: Path


@dataclass(frozen=True)
class BitVectorResult:
    """Result from bit vector generation.

    Attributes:
        mutation_histos: Dictionary of mutation histograms by sequence name
        summary_path: Path to summary CSV file
        output_dir: Output directory for bit vector files
    """

    mutation_histos: dict[str, MutationHistogram]
    summary_path: Path
    output_dir: Path


# PipelineResult removed - no longer needed after migration to Nextflow

