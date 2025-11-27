"""Nextflow wrapper for RNA MAP CLI commands."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from rna_map.logger import get_logger, setup_logging

log = get_logger("CLI.NEXTFLOW")


def get_nextflow_path() -> Path:
    """Get path to Nextflow workflow directory.
    
    Returns:
        Path to nextflow/ directory
    """
    # Try to find nextflow directory relative to this file
    current_file = Path(__file__).resolve()
    # Go up: cli/ -> rna_map/ -> repo root
    repo_root = current_file.parent.parent.parent
    nextflow_dir = repo_root / "nextflow"
    
    if not nextflow_dir.exists():
        # Try alternative location
        nextflow_dir = repo_root.parent / "nextflow"
        if not nextflow_dir.exists():
            raise FileNotFoundError(
                f"Nextflow directory not found. Expected: {repo_root / 'nextflow'}"
            )
    
    return nextflow_dir


def run_nextflow(
    main_nf: Path,
    args: list[str],
    profile: str = "local",
    check: bool = True,
) -> subprocess.CompletedProcess:
    """Run Nextflow workflow.
    
    Args:
        main_nf: Path to main.nf file
        args: Additional Nextflow arguments
        profile: Nextflow profile to use
        check: Whether to raise on non-zero exit
        
    Returns:
        Completed process
    """
    cmd = ["nextflow", "run", str(main_nf), "-profile", profile] + args
    
    log.info(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=False,  # Let output stream to console
        )
        return result
    except subprocess.CalledProcessError as e:
        log.error(f"Nextflow workflow failed with exit code {e.returncode}")
        raise
    except FileNotFoundError:
        log.error("Nextflow not found. Please install Nextflow or activate conda environment.")
        log.error("Install: conda install -c bioconda nextflow")
        raise


def run_single_sample(
    fasta: Path,
    fastq1: Path,
    fastq2: Optional[Path] = None,
    dot_bracket: Optional[Path] = None,
    output_dir: Path = Path("results"),
    skip_fastqc: bool = False,
    skip_trim_galore: bool = False,
    tg_q_cutoff: int = 20,
    bt2_alignment_args: str = "",
    qscore_cutoff: int = 25,
    map_score_cutoff: int = 15,
    summary_output_only: bool = False,
    overwrite: bool = False,
    profile: str = "local",
    split_fastq: bool = False,
    chunk_size: int = 1000000,
    **kwargs,
) -> None:
    """Run RNA MAP on a single sample using Nextflow.
    
    Args:
        fasta: Path to FASTA file
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file (optional)
        dot_bracket: Path to dot-bracket CSV file (optional)
        output_dir: Output directory
        skip_fastqc: Skip FastQC
        skip_trim_galore: Skip Trim Galore
        tg_q_cutoff: Trim Galore quality cutoff
        bt2_alignment_args: Bowtie2 alignment arguments (semicolon-separated)
        qscore_cutoff: Quality score cutoff for bit vectors
        map_score_cutoff: Mapping score cutoff for bit vectors
        summary_output_only: Only output summary files
        overwrite: Overwrite existing files
        profile: Nextflow profile (local, slurm, etc.)
        split_fastq: Split FASTQ files for parallel processing
        chunk_size: Number of reads per chunk
        **kwargs: Additional parameters (SLURM options)
    """
    nextflow_dir = get_nextflow_path()
    main_nf = nextflow_dir / "main.nf"
    
    if not main_nf.exists():
        raise FileNotFoundError(f"Nextflow workflow not found: {main_nf}")
    
    args = [
        "--fasta", str(fasta),
        "--fastq1", str(fastq1),
        "--output_dir", str(output_dir),
    ]
    
    if fastq2:
        args.extend(["--fastq2", str(fastq2)])
    
    if dot_bracket:
        args.extend(["--dot_bracket", str(dot_bracket)])
    
    if skip_fastqc:
        args.append("--skip_fastqc")
    
    if skip_trim_galore:
        args.append("--skip_trim_galore")
    
    if overwrite:
        args.append("--overwrite")
    
    if split_fastq:
        args.extend(["--split_fastq", "--chunk_size", str(chunk_size)])
    
    # Add mapping parameters
    # Always pass tg_q_cutoff if different from Nextflow default (20)
    if tg_q_cutoff != 20:
        args.extend(["--tg_q_cutoff", str(tg_q_cutoff)])
    
    # Always pass bt2_alignment_args if provided (Python default includes -p 16, Nextflow doesn't)
    if bt2_alignment_args:
        args.extend(["--bt2_alignment_args", bt2_alignment_args])
    
    # Add bit vector parameters
    # Python defaults (25, 15) differ from Nextflow defaults (20, 20), so always pass them
    if qscore_cutoff != 20:  # Nextflow default is 20, Python default is 25
        args.extend(["--qscore_cutoff", str(qscore_cutoff)])
    
    if map_score_cutoff != 20:  # Nextflow default is 20, Python default is 15
        args.extend(["--map_score_cutoff", str(map_score_cutoff)])
    
    if summary_output_only:
        args.append("--summary_output_only")
    
    # Add SLURM options if on cluster
    if profile == "slurm":
        if kwargs.get("account"):
            args.extend(["--account", kwargs["account"]])
        if kwargs.get("partition"):
            args.extend(["--partition", kwargs["partition"]])
        if kwargs.get("max_cpus"):
            args.extend(["--max_cpus", str(kwargs["max_cpus"])])
    
    run_nextflow(main_nf, args, profile=profile)


def run_batch(
    samples_csv: Path,
    output_dir: Path = Path("results"),
    overwrite: bool = False,
    profile: str = "local",
    account: Optional[str] = None,
    partition: str = "normal",
    max_cpus: int = 16,
    split_fastq: bool = False,
    chunk_size: int = 1000000,
    skip_fastqc: bool = False,
    skip_trim_galore: bool = False,
    tg_q_cutoff: int = 20,
    bt2_alignment_args: str = "",
    qscore_cutoff: int = 25,
    map_score_cutoff: int = 15,
    summary_output_only: bool = False,
) -> None:
    """Run RNA MAP on multiple samples using Nextflow.
    
    Args:
        samples_csv: Path to samples CSV file
        output_dir: Output directory
        overwrite: Overwrite existing files
        profile: Nextflow profile (local, slurm, etc.)
        account: SLURM account (for slurm profile)
        partition: SLURM partition (for slurm profile)
        max_cpus: Maximum CPUs per process
        split_fastq: Split FASTQ files for parallel processing
        chunk_size: Number of reads per chunk
        skip_fastqc: Skip FastQC
        skip_trim_galore: Skip Trim Galore
        tg_q_cutoff: Trim Galore quality cutoff
        bt2_alignment_args: Bowtie2 alignment arguments (semicolon-separated)
        qscore_cutoff: Quality score cutoff for bit vectors
        map_score_cutoff: Mapping score cutoff for bit vectors
        summary_output_only: Only output summary files
    """
    nextflow_dir = get_nextflow_path()
    main_nf = nextflow_dir / "main.nf"
    
    if not main_nf.exists():
        raise FileNotFoundError(f"Nextflow workflow not found: {main_nf}")
    
    args = [
        "--samples_csv", str(samples_csv),
        "--output_dir", str(output_dir),
        "--max_cpus", str(max_cpus),
    ]
    
    if overwrite:
        args.append("--overwrite")
    
    if split_fastq:
        args.extend(["--split_fastq", "--chunk_size", str(chunk_size)])
    
    if skip_fastqc:
        args.append("--skip_fastqc")
    
    if skip_trim_galore:
        args.append("--skip_trim_galore")
    
    # Add mapping parameters
    # Always pass tg_q_cutoff if different from Nextflow default (20)
    if tg_q_cutoff != 20:
        args.extend(["--tg_q_cutoff", str(tg_q_cutoff)])
    
    # Always pass bt2_alignment_args if provided (Python default includes -p 16, Nextflow doesn't)
    if bt2_alignment_args:
        args.extend(["--bt2_alignment_args", bt2_alignment_args])
    
    # Add bit vector parameters
    # Python defaults (25, 15) differ from Nextflow defaults (20, 20), so always pass them
    if qscore_cutoff != 20:  # Nextflow default is 20, Python default is 25
        args.extend(["--qscore_cutoff", str(qscore_cutoff)])
    
    if map_score_cutoff != 20:  # Nextflow default is 20, Python default is 15
        args.extend(["--map_score_cutoff", str(map_score_cutoff)])
    
    if summary_output_only:
        args.append("--summary_output_only")
    
    if profile == "slurm":
        if account:
            args.extend(["--account", account])
        args.extend(["--partition", partition])
    
    run_nextflow(main_nf, args, profile=profile)

