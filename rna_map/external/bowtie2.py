"""Bowtie2 command execution and validation."""

from pathlib import Path

import pandas as pd

from rna_map.exception import DREEMInputException
from rna_map.external.base import ProgOutput, run_named_command
from rna_map.logger import get_logger
from rna_map.settings import get_py_path

log = get_logger("EXTERNAL.BOWTIE2")


def _check_type(arg: str) -> str:
    """Check the type of an argument value.

    Args:
        arg: Argument value to check

    Returns:
        Type string: "int", "float", or "str"
    """
    if arg.isdigit():
        return "int"
    try:
        float(arg)
        return "float"
    except ValueError:
        return "str"


def validate_bowtie2_args(args: str) -> bool:
    """Validate Bowtie2 arguments against reference table.

    Args:
        args: Arguments to validate, separated by ";"

    Returns:
        True if all arguments are valid

    Raises:
        DREEMInputException: If any argument is invalid
    """
    df = pd.read_csv(get_py_path() / "resources" / "bowtie2_args.csv")
    valid_bt2_args = {}
    for _, row in df.iterrows():
        valid_bt2_args[row["param"]] = row["vtype"]
    if len(args) == 0:
        log.warning("no bowtie2 arguments supplied thats probably wrong")
    supplied_args = args.strip().split(";")
    for full_arg in supplied_args:
        if len(full_arg) == 0:
            continue
        if full_arg in valid_bt2_args:
            log.debug(f"{full_arg} is a valid bt2 argument")
            continue
        spl = full_arg.split()
        if len(spl) == 1:
            raise DREEMInputException(
                f"{full_arg} is not a valid bowtie2 argument. "
                "Please check the documentation for valid arguments"
            )
        arg, arg_val = spl[0], spl[1]
        if arg in valid_bt2_args:
            log.debug(f"{arg} is a valid bt2 argument")
        else:
            raise DREEMInputException(f"{full_arg} is an invalid bt2 argument")
        if _check_type(arg_val) != valid_bt2_args[arg]:
            raise DREEMInputException(f"{arg} must be of type {valid_bt2_args[arg]}")
    log.debug("all bt2 arguments are valid")
    return True


def run_bowtie_build(fasta: str | Path, input_dir: str | Path) -> ProgOutput:
    """Run bowtie2-build on a FASTA file.

    Args:
        fasta: Path to FASTA file
        input_dir: Path to input directory for index files

    Returns:
        ProgOutput with command results
    """
    fasta_name = Path(fasta).stem
    cmd = f'bowtie2-build "{fasta}" {input_dir}/{fasta_name}'
    return run_named_command("bowtie2-build", cmd)


def run_bowtie_alignment(
    fasta: str | Path,
    fastq1: str | Path,
    fastq2: str | Path,
    in_dir: str | Path,
    out_dir: str | Path,
    args: str,
    **kwargs,
) -> ProgOutput:
    """Run Bowtie2 alignment.

    Args:
        fasta: Path to FASTA file
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file (empty string for single-end)
        in_dir: Path to Bowtie2 index directory
        out_dir: Path to output directory
        args: Bowtie2 arguments separated by ";"
        **kwargs: Additional options (e.g., save_unaligned)

    Returns:
        ProgOutput with command results
    """
    validate_bowtie2_args(args)
    cmd = _build_bowtie2_command(fasta, fastq1, fastq2, in_dir, out_dir, args, **kwargs)
    out = run_named_command("bowtie2 alignment", cmd)
    _log_bowtie2_results(out)
    return out


def _build_bowtie2_command(fasta, fastq1, fastq2, in_dir, out_dir, args, **kwargs):
    """Build Bowtie2 command string.

    Args:
        fasta: Path to FASTA file
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file
        in_dir: Path to Bowtie2 index directory
        out_dir: Path to output directory
        args: Bowtie2 arguments
        **kwargs: Additional options

    Returns:
        Complete Bowtie2 command string
    """
    bt2_index = Path(in_dir) / Path(fasta).stem
    bt2_args = " ".join(args.split(";"))
    sam_file = Path(out_dir) / "aligned.sam"
    cmd = f"bowtie2 {bt2_args} -x {bt2_index} -S {sam_file} "
    cmd += _add_fastq_inputs(fastq1, fastq2)
    if "save_unaligned" in kwargs:
        cmd += " --un-conc unaligned.fastq"
    return cmd


def _add_fastq_inputs(fastq1, fastq2):
    """Add FASTQ input files to command.

    Args:
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file

    Returns:
        Command string fragment for FASTQ inputs
    """
    if fastq2 != "":
        return f"-1 {fastq1} -2 {fastq2} "
    return f"-U {fastq1}"


def _log_bowtie2_results(out):
    """Log Bowtie2 alignment results.

    Args:
        out: ProgOutput with command results
    """
    output_lines = out.output.split("\n")
    keep = [line for line in output_lines if len(line) > 0 and line[0] != "U"]
    log.info("results for bowtie alignment: \n" + "\n".join(keep))
