"""CSV and dot-bracket file handling."""

from pathlib import Path

import pandas as pd

from rna_map.exception import DREEMInputException
from rna_map.io.fasta import fasta_to_dict


def validate_csv_file(fa: str | Path, csv: str | Path) -> None:
    """Ensure that the CSV file matches the FASTA file.

    Args:
        fa: Path to the FASTA file
        csv: Path to the CSV file

    Raises:
        DREEMInputException: If CSV file format is invalid or doesn't match FASTA
    """
    ref_seqs = fasta_to_dict(fa)
    df = pd.read_csv(csv)
    if "name" not in df.columns:
        raise DREEMInputException("csv file does not contain a column named 'name'.")
    if "sequence" not in df.columns:
        raise DREEMInputException("csv file does not contain a column named 'sequence'")
    if "structure" not in df.columns:
        raise DREEMInputException(
            "csv file does not contain a column named 'structure'"
        )
    if len(ref_seqs) != len(df):
        raise DREEMInputException(
            f"number of reference sequences in fasta ({len(ref_seqs)}) does not match"
            f" number of reference sequences in dot-bracket file ({len(df)})"
        )
    for _, row in df.iterrows():
        if row["name"] not in ref_seqs:
            raise DREEMInputException(
                f"reference sequence name {row['name']} in csv file does not match"
                " any reference sequence names in fasta file"
            )
