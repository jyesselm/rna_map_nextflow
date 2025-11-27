"""Input/output operations for RNA MAP.

This module handles file I/O operations including:
- FASTA file parsing and validation
- FASTQ file validation
- SAM file parsing
- CSV/dot-bracket file handling
- Bit vector file I/O
"""

from rna_map.io.bit_vector import BitVectorFileReader, BitVectorFileWriter
from rna_map.io.csv import validate_csv_file
from rna_map.io.fasta import fasta_to_dict, validate_fasta_file
from rna_map.io.fastq import parse_phred_qscore_file, validate_fastq_file
from rna_map.io.sam import (
    AlignedRead,
    PairedSamIterator,
    SingleSamIterator,
    get_aligned_read_from_line,
)
from rna_map.io.validation import validate_inputs

__all__ = [
    "AlignedRead",
    "BitVectorFileReader",
    "BitVectorFileWriter",
    "PairedSamIterator",
    "SingleSamIterator",
    "fasta_to_dict",
    "get_aligned_read_from_line",
    "parse_phred_qscore_file",
    "validate_csv_file",
    "validate_fasta_file",
    "validate_fastq_file",
    "validate_inputs",
]
