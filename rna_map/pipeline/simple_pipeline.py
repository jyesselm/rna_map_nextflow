"""Simple pipeline for demultiplexing FASTQ files.

Note: Mapping and bit vector generation are now handled by Nextflow workflow.
This module only provides demultiplexing functionality.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from rna_map.logger import get_logger

log = get_logger("PIPELINE.SIMPLE")


@dataclass
class Sample:
    """Represents a single sample to process.

    Attributes:
        sample_id: Unique identifier for the sample
        fasta: Path to FASTA reference file
        fastq1: Path to R1 FASTQ file
        fastq2: Path to R2 FASTQ file (optional)
        dot_bracket: Path to dot-bracket CSV file (optional)
        barcode: Barcode sequence (optional)
        output_dir: Output directory (auto-generated if None)
    """

    sample_id: str
    fasta: Path
    fastq1: Path
    fastq2: Optional[Path] = None
    dot_bracket: Optional[Path] = None
    barcode: Optional[str] = None
    output_dir: Optional[Path] = None

    def __post_init__(self) -> None:
        """Set default output directory if not provided."""
        if self.output_dir is None:
            self.output_dir = Path("results") / self.sample_id


def demultiplex_fastq(
    fastq1: Path,
    fastq2: Path,
    barcodes_csv: Path,
    output_dir: Path,
) -> List[Sample]:
    """Demultiplex FASTQ files by barcode.

    Args:
        fastq1: Path to R1 FASTQ file
        fastq2: Path to R2 FASTQ file
        barcodes_csv: CSV with barcode sequences and metadata
        output_dir: Where to write demultiplexed files

    Returns:
        List of Sample objects, one per barcode

    Raises:
        FileNotFoundError: If input files don't exist
        ValueError: If demultiplexing fails
    """
    import pandas as pd

    log.info(f"Demultiplexing {fastq1} and {fastq2}")

    if not fastq1.exists():
        raise FileNotFoundError(f"FASTQ1 not found: {fastq1}")
    if not fastq2.exists():
        raise FileNotFoundError(f"FASTQ2 not found: {fastq2}")
    if not barcodes_csv.exists():
        raise FileNotFoundError(f"Barcodes CSV not found: {barcodes_csv}")

    try:
        from rna_map_slurm.demultiplex import SabreDemultiplexer
        from rna_map_slurm.fastq import PairedFastqFiles, FastqFile
    except ImportError:
        log.warning("rna_map_slurm not available, using placeholder")
        return _demultiplex_placeholder(fastq1, fastq2, barcodes_csv, output_dir)

    df = pd.read_csv(barcodes_csv)
    output_dir.mkdir(parents=True, exist_ok=True)

    paired_fastqs = PairedFastqFiles(FastqFile(fastq1), FastqFile(fastq2))
    demultiplexer = SabreDemultiplexer()
    demultiplexer.run(df, paired_fastqs, output_dir)

    return _create_samples_from_demultiplexed(df, output_dir)


def _create_samples_from_demultiplexed(df, output_dir: Path) -> List[Sample]:
    """Create Sample objects from demultiplexed files.

    Args:
        df: DataFrame with barcode information
        output_dir: Directory with demultiplexed files

    Returns:
        List of Sample objects
    """
    import pandas as pd

    samples = []
    for _, row in df.iterrows():
        barcode = row["barcode_seq"]
        barcode_dir = output_dir / barcode

        r1_files = list(barcode_dir.glob("*_R1*.fastq*"))
        r2_files = list(barcode_dir.glob("*_R2*.fastq*"))

        if not r1_files:
            log.warning(f"No R1 files found for barcode {barcode}")
            continue

        r1_path = r1_files[0]
        r2_path = r2_files[0] if r2_files else None

        dot_bracket = None
        if "dot_bracket" in row and pd.notna(row["dot_bracket"]):
            dot_bracket = Path(row["dot_bracket"])

        fasta = Path(row.get("fasta", "")) if "fasta" in row else None

        samples.append(
            Sample(
                sample_id=f"{barcode}_{row.get('construct', 'unknown')}",
                fasta=fasta or Path(""),  # Will be set later
                fastq1=r1_path,
                fastq2=r2_path,
                dot_bracket=dot_bracket,
                barcode=barcode,
                output_dir=Path("results") / barcode,
            )
        )

    log.info(f"Demultiplexed into {len(samples)} samples")
    return samples


def _demultiplex_placeholder(
    fastq1: Path, fastq2: Path, barcodes_csv: Path, output_dir: Path
) -> List[Sample]:
    """Placeholder for demultiplexing when rna_map_slurm not available.

    Args:
        fastq1: Path to R1 FASTQ file
        fastq2: Path to R2 FASTQ file
        barcodes_csv: CSV with barcode information
        output_dir: Output directory

    Returns:
        List of Sample objects (placeholder)
    """
    import pandas as pd

    df = pd.read_csv(barcodes_csv)
    samples = []
    for _, row in df.iterrows():
        samples.append(
            Sample(
                sample_id=f"{row['barcode_seq']}_placeholder",
                fasta=Path(row.get("fasta", "")),
                fastq1=fastq1,  # Placeholder: use original files
                fastq2=fastq2,
                barcode=row["barcode_seq"],
            )
        )
    return samples
