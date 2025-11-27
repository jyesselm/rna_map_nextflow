"""FastQC command execution."""

import os
from pathlib import Path

from rna_map.external.base import ProgOutput, run_named_command


def run_fastqc(
    fastq1: str | Path, fastq2: str | Path, out_dir: str | Path
) -> ProgOutput:
    """Run FastQC on FASTQ files.

    Args:
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file (empty string for single-end)
        out_dir: Path to output directory

    Returns:
        ProgOutput with command results
    """
    fastqc_dir = os.path.join(out_dir, "fastqc")
    os.makedirs(fastqc_dir, exist_ok=True)
    fastqc_cmd = f"fastqc {fastq1} {fastq2} -o {fastqc_dir}"
    return run_named_command("fastqc", fastqc_cmd)
