"""FASTQ file validation and quality score parsing."""

from pathlib import Path


def validate_fastq_file(fastq_file: Path) -> bool:
    """Validate a FASTQ file.

    Args:
        fastq_file: Path to FASTQ file

    Returns:
        True if valid FASTQ format

    Note:
        TODO: add validation for gz files
    """
    if not fastq_file.exists() or not fastq_file.is_file():
        return False
    if fastq_file.suffix == ".gz":
        return True
    with open(fastq_file) as f:
        lines = [f.readline().strip() for _ in range(4)]
    if len(lines) < 4:
        return False
    if not lines[0].startswith("@"):
        return False
    if not lines[2].startswith("+"):
        return False
    if len(lines[1]) != len(lines[3]):
        return False
    return True


def parse_phred_qscore_file(qscore_filename: str | Path) -> dict[str, int]:
    """Parse PHRED quality score ASCII mapping file.

    Args:
        qscore_filename: Path to PHRED quality score file

    Returns:
        Dictionary mapping ASCII characters to quality scores
    """
    phred_qscore: dict[str, int] = {}
    with open(qscore_filename) as qscore_file:
        qscore_file.readline()  # Ignore header line
        for line in qscore_file:
            parts = line.strip().split()
            score, symbol = int(parts[0]), parts[1]
            phred_qscore[symbol] = score
    return phred_qscore
