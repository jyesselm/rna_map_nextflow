"""Trim Galore command execution."""

from pathlib import Path

from rna_map.external.base import ProgOutput, run_named_command


def run_trim_galore(
    fastq1: str | Path, fastq2: str | Path, out_dir: str | Path
) -> ProgOutput:
    """Run Trim Galore on FASTQ files.

    Args:
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file (empty string for single-end)
        out_dir: Path to output directory

    Returns:
        ProgOutput with command results
    """
    if fastq2 != "":
        cmd = f"trim_galore --fastqc --paired {fastq1} {fastq2} -o {out_dir}"
    else:
        cmd = f"trim_galore --fastqc {fastq1} -o {out_dir}"
    return run_named_command("trim_galore", cmd)
