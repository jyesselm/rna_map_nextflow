"""Input data structures for RNA MAP."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, order=True)
class Inputs:
    """Input parameters for RNA MAP pipeline.

    Attributes:
        fasta: Path to FASTA file
        fastq1: Path to first FASTQ file (required)
        fastq2: Path to second FASTQ file (optional, use Path("") for single-end)
        csv: Path to dot-bracket CSV file (optional, use Path("") to skip)
    """

    fasta: str | Path
    fastq1: str | Path
    fastq2: str | Path = Path("")
    csv: str | Path = Path("")

    def is_paired(self) -> bool:
        """Check if the input is paired (has both R1 and R2).

        Returns:
            True if paired-end, False if single-end
        """
        if self.fastq2 != Path(""):
            return True
        return False

    def supplied_csv(self) -> bool:
        """Check if the user supplied a CSV file.

        Returns:
            True if CSV file was supplied
        """
        if self.csv != Path(""):
            return True
        return False

    def fastq1_name(self) -> str:
        """Get the name of the fastq1 file.

        Returns:
            Filename without extension
        """
        return Path(self.fastq1).stem

    def fastq2_name(self) -> str:
        """Get the name of the fastq2 file.

        Returns:
            Filename without extension
        """
        return Path(self.fastq2).stem
