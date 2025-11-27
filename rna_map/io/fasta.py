"""FASTA file parsing and validation."""

from pathlib import Path
import re

from rna_map.exception import DREEMInputException
from rna_map.logger import get_logger

log = get_logger("IO.FASTA")


def fasta_to_dict(fasta_file: str | Path) -> dict[str, str]:
    """Parse a FASTA file into a dictionary.

    Args:
        fasta_file: Path to FASTA file

    Returns:
        Dictionary mapping sequence names to sequences
    """
    refs_seq: dict[str, str] = {}
    with open(fasta_file) as handle:
        for line in handle.readlines():
            if line[0] == ">":
                ref_name = line[1:].strip()
                refs_seq[ref_name] = ""
            else:
                refs_seq[ref_name] += line.strip()
    return refs_seq


def validate_fasta_file(fa: str | Path) -> bool:
    """Ensure that the FASTA file is in the correct format.

    Args:
        fa: Path to the FASTA file

    Returns:
        True if valid

    Raises:
        DREEMInputException: If FASTA file format is invalid
    """
    with open(fa, encoding="utf8") as f:
        lines = f.readlines()
    if len(lines) > 2000:
        log.warning(
            "fasta file contains more than 1000 sequences, this may lead"
            " to file generation issues. Its recommended to use --summary-output-only "
        )
    num = 0
    for i, line in enumerate(lines):
        line = line.rstrip()
        if len(line) == 0:
            raise DREEMInputException(
                f"blank line found on ln: {i}. These are not allowed in fastas."
            )
        # should be a reference sequence declaration
        if i % 2 == 0:
            num += 1
            if not line.startswith(">"):
                raise DREEMInputException(
                    "reference sequence names are on line zero and even numbers."
                    f" line {i} has value which is not correct format in the fasta"
                )
            if line.startswith("> "):
                raise DREEMInputException(
                    "there should be no spaces between > and reference name."
                    f"this occured on ln: {i} in the fasta file"
                )
        elif i % 2 == 1:
            if line.startswith(">"):
                raise DREEMInputException(
                    "sequences should be on are on odd line numbers."
                    f" line {i} has value which is not correct format in fasta file"
                )
            if re.search(r"[^AGCT]", line):
                raise DREEMInputException(
                    "reference sequences must contain only AGCT characters."
                    f" line {i} is not consistent with this in fasta"
                )
    log.info(f"found {num} valid reference sequences in {fa}")
    return True
