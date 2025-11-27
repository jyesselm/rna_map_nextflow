"""Input file validation utilities."""

import os
from pathlib import Path

from rna_map.core.inputs import Inputs
from rna_map.exception import DREEMInputException
from rna_map.io.csv import validate_csv_file
from rna_map.io.fasta import validate_fasta_file
from rna_map.io.fastq import validate_fastq_file
from rna_map.logger import get_logger

log = get_logger("IO.VALIDATION")


def validate_inputs(fa: Path, fq1: Path, fq2: Path, csv: Path) -> Inputs:
    """Validate all input files.

    Args:
        fa: Path to the FASTA file
        fq1: Path to the first FASTQ file
        fq2: Path to the second FASTQ file (optional, use Path(".") for single-end)
        csv: Path to the dot-bracket CSV file (optional, use Path(".") to skip)

    Returns:
        Inputs dataclass with validated file paths

    Raises:
        DREEMInputException: If any input file is invalid
    """
    if not fa.is_file():
        raise DREEMInputException(f"fasta file: does not exist {fa}!")
    log.info(f"fasta file: {fa} exists")
    if validate_fasta_file(fa):
        log.info("fasta file is valid")

    if not fq1.is_file():
        raise DREEMInputException(f"fastq1 file: does not exist {fq1}!")
    if not validate_fastq_file(fq1):
        raise DREEMInputException(f"fastq1 file: is not a valid fastq file {fq1}!")
    log.info(f"fastq1 file: {fq1} exists")

    if str(fq2) != "." and str(fq2) != "":
        if not os.path.isfile(fq2):
            raise DREEMInputException(f"fastq2 file: does not exist {fq2}!")
        log.info(f"fastq2 file: {fq2} exists")
        log.info("two fastq files supplied, thus assuming paired reads")
        if not validate_fastq_file(Path(fq2)):
            raise DREEMInputException(f"fastq2 file: is not a valid fastq file {fq2}!")

    if str(csv) != "." and str(csv) != "":
        if not os.path.isfile(csv):
            raise DREEMInputException(f"csv file: does not exist {csv}!")
        log.info(f"csv file: {csv} exists")
        validate_csv_file(fa, csv)

    return Inputs(fa, fq1, fq2, csv)
