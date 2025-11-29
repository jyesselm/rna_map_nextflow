"""Input validation functions for RNA MAP."""

from pathlib import Path
from dataclasses import dataclass

from rna_map.exception import DREEMInputException
from rna_map.io.fasta import validate_fasta_file
from rna_map.io.fastq import validate_fastq_file


@dataclass
class ValidatedInputs:
    """Validated input file paths.
    
    Attributes:
        fasta: Path to FASTA file
        fastq1: Path to first FASTQ file (or empty if single-end)
        fastq2: Path to second FASTQ file (or empty if single-end)
        csv: Path to CSV/dot-bracket file (or empty)
    """
    fasta: Path
    fastq1: Path
    fastq2: Path
    csv: Path
    
    def is_paired(self) -> bool:
        """Check if paired-end reads.
        
        Returns:
            True if fastq2 is provided and is a valid file
        """
        return self.fastq2.exists() and self.fastq2.is_file() if self.fastq2 else False
    
    def supplied_csv(self) -> bool:
        """Check if CSV file was supplied.
        
        Returns:
            True if csv is provided and is a valid file
        """
        return self.csv.exists() and self.csv.is_file() if self.csv else False


def validate_inputs(
    fasta: Path,
    fastq1: Path,
    fastq2: Path,
    csv: Path,
) -> ValidatedInputs:
    """Validate input files for RNA MAP pipeline.
    
    Args:
        fasta: Path to FASTA reference file
        fastq1: Path to first FASTQ file (or empty Path for single-end)
        fastq2: Path to second FASTQ file (or empty Path for single-end)
        csv: Path to CSV/dot-bracket file (or empty Path)
    
    Returns:
        ValidatedInputs object with validated paths
    
    Raises:
        DREEMInputException: If any input file is invalid or missing
    """
    # Validate FASTA
    if not fasta.exists():
        raise DREEMInputException(f"FASTA file not found: {fasta}")
    validate_fasta_file(fasta)
    
    # Validate FASTQ1
    if not fastq1.exists() or not fastq1.is_file():
        raise DREEMInputException(f"FASTQ file not found: {fastq1}")
    if not validate_fastq_file(fastq1):
        raise DREEMInputException(f"Invalid FASTQ file: {fastq1}")
    
    # Validate FASTQ2 if provided
    if fastq2 and str(fastq2):
        if not fastq2.exists() or not fastq2.is_file():
            raise DREEMInputException(f"FASTQ file not found: {fastq2}")
        if not validate_fastq_file(fastq2):
            raise DREEMInputException(f"Invalid FASTQ file: {fastq2}")
    
    # Validate CSV if provided
    if csv and str(csv):
        if not csv.exists():
            raise DREEMInputException(f"CSV file not found: {csv}")
    
    return ValidatedInputs(
        fasta=fasta,
        fastq1=fastq1,
        fastq2=fastq2 if fastq2 else Path(""),
        csv=csv if csv else Path(""),
    )

