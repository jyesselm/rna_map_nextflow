"""CLI commands for Nextflow-based RNA MAP pipeline."""

from pathlib import Path

import cloup

from rna_map.logger import get_logger, setup_logging
from rna_map.cli.nextflow_wrapper import run_batch
from rna_map.pipeline.simple_pipeline import (
    Sample,
    demultiplex_fastq,
)
import pandas as pd

log = get_logger("CLI.PIPELINE")


@cloup.group()
def pipeline():
    """RNA MAP pipeline with Nextflow orchestration."""
    pass


@pipeline.command()
@cloup.argument("fastq1", type=cloup.Path(exists=True))
@cloup.argument("fastq2", type=cloup.Path(exists=True))
@cloup.argument("barcodes_csv", type=cloup.Path(exists=True))
@cloup.option(
    "--output-dir",
    default="demultiplexed",
    type=cloup.Path(),
    help="Output directory for demultiplexed files",
)
def demultiplex(fastq1, fastq2, barcodes_csv, output_dir):
    """Demultiplex FASTQ files by barcode.
    
    Creates a samples.csv file that can be used with 'rna-map-pipeline run'.
    
    Args:
        fastq1: Path to R1 FASTQ file
        fastq2: Path to R2 FASTQ file
        barcodes_csv: CSV file with barcode sequences and metadata
        output_dir: Output directory for demultiplexed files
    """
    setup_logging()
    log.info(f"Demultiplexing {fastq1} and {fastq2}")

    samples = demultiplex_fastq(
        fastq1=Path(fastq1),
        fastq2=Path(fastq2),
        barcodes_csv=Path(barcodes_csv),
        output_dir=Path(output_dir),
    )

    samples_df = pd.DataFrame([
        {
            "sample_id": s.sample_id,
            "fasta": str(s.fasta) if s.fasta else "",
            "fastq1": str(s.fastq1),
            "fastq2": str(s.fastq2) if s.fastq2 else "",
            "dot_bracket": str(s.dot_bracket) if s.dot_bracket else "",
            "barcode": s.barcode if s.barcode else "",
        }
        for s in samples
    ])
    samples_df.to_csv("samples.csv", index=False)
    log.info(f"Saved {len(samples)} samples to samples.csv")


@pipeline.command()
@cloup.argument("samples_csv", type=cloup.Path(exists=True))
@cloup.option("--output-dir", default="results", type=cloup.Path(), help="Output directory")
@cloup.option("--account", help="SLURM account (for slurm profile)")
@cloup.option("--partition", default="normal", help="SLURM partition (for slurm profile)")
@cloup.option("--max-cpus", default=16, type=int, help="Maximum CPUs per process")
@cloup.option("--overwrite", is_flag=True, help="Overwrite existing files")
@cloup.option("--split-fastq", is_flag=True, help="Split FASTQ files and process chunks in parallel")
@cloup.option("--chunk-size", default=1000000, type=int, help="Number of reads per chunk (when --split-fastq)")
@cloup.option(
    "--profile",
    default="local",
    type=cloup.Choice(["local", "slurm"]),
    help="Nextflow profile (local or slurm)",
)
def run(samples_csv, output_dir, account, partition, max_cpus, overwrite, split_fastq, chunk_size, profile):
    """Run RNA MAP on multiple samples using Nextflow.
    
    Automatically parallelizes independent samples. Works on both local and cluster.
    
    Args:
        samples_csv: CSV file with sample information
        output_dir: Output directory for results
        account: SLURM account (for slurm profile)
        partition: SLURM partition (for slurm profile)
        max_cpus: Maximum CPUs per process
        overwrite: Whether to overwrite existing files
        profile: Nextflow profile (local or slurm)
    """
    import os
    
    setup_logging()
    log.info(f"Running RNA MAP pipeline with Nextflow")
    log.info(f"Loading samples from {samples_csv}")
    
    # Auto-detect profile if not specified
    if profile == "local" and os.environ.get("SLURM_JOB_ID"):
        profile = "slurm"
        log.info("Detected SLURM environment, using slurm profile")
    
    run_batch(
        samples_csv=Path(samples_csv),
        output_dir=Path(output_dir),
        overwrite=overwrite,
        profile=profile,
        account=account,
        partition=partition,
        max_cpus=max_cpus,
        split_fastq=split_fastq,
        chunk_size=chunk_size,
    )
    
    log.info(f"Pipeline completed! Results in: {output_dir}")


@pipeline.command()
@cloup.argument("fastq1", type=cloup.Path(exists=True))
@cloup.argument("fastq2", type=cloup.Path(exists=True))
@cloup.argument("barcodes_csv", type=cloup.Path(exists=True))
@cloup.option(
    "--num-workers",
    default=100,
    type=int,
    help="Number of Dask workers",
)
@cloup.option("--account", help="SLURM account (HPC only)")
@cloup.option(
    "--partition",
    default="normal",
    help="SLURM partition (HPC only)",
)
@cloup.option(
    "--environment",
    type=cloup.Choice(["local", "hpc"]),
    help="Force environment (auto-detect if not specified)",
)
@cloup.option("--overwrite", is_flag=True, help="Overwrite existing files")
@cloup.option("--output-dir", default="results", type=cloup.Path(), help="Output directory")
@cloup.option("--max-cpus", default=16, type=int, help="Maximum CPUs per process")
@cloup.option(
    "--profile",
    default="local",
    type=cloup.Choice(["local", "slurm"]),
    help="Nextflow profile (local or slurm)",
)
def full(
    fastq1,
    fastq2,
    barcodes_csv,
    num_workers,
    account,
    partition,
    environment,
    overwrite,
    output_dir,
    max_cpus,
    profile,
):
    """Run full pipeline: demultiplex → RNA MAP (parallel).

    This is a convenience command that runs demultiplexing and then
    processes all samples in parallel with worker reuse.

    Args:
        fastq1: Path to R1 FASTQ file
        fastq2: Path to R2 FASTQ file
        barcodes_csv: CSV file with barcode information
        num_workers: Number of Dask workers (deprecated, kept for compatibility)
        account: SLURM account (HPC only)
        partition: SLURM partition (HPC only)
        environment: Force environment (auto-detect if not specified)
        overwrite: Whether to overwrite existing files
        output_dir: Output directory for results
        max_cpus: Maximum CPUs per process
        profile: Nextflow profile (local or slurm)
    """
    setup_logging()
    log.info("Starting full pipeline: demultiplex → RNA MAP")

    # Step 1: Demultiplex
    log.info("Step 1: Demultiplexing...")
    samples = demultiplex_fastq(
        fastq1=Path(fastq1),
        fastq2=Path(fastq2),
        barcodes_csv=Path(barcodes_csv),
        output_dir=Path("demultiplexed"),
    )

    # Step 2: Run RNA MAP using Nextflow
    log.info(f"Step 2: Running RNA MAP on {len(samples)} samples with Nextflow...")
    
    # Create samples.csv
    samples_df = pd.DataFrame([
        {
            "sample_id": s.sample_id,
            "fasta": str(s.fasta) if s.fasta else "",
            "fastq1": str(s.fastq1),
            "fastq2": str(s.fastq2) if s.fastq2 else "",
            "dot_bracket": str(s.dot_bracket) if s.dot_bracket else "",
            "barcode": s.barcode if s.barcode else "",
        }
        for s in samples
    ])
    samples_csv = Path("samples.csv")
    samples_df.to_csv(samples_csv, index=False)
    
    # Run Nextflow
    import os
    # Auto-detect profile if not specified
    if profile == "local" and os.environ.get("SLURM_JOB_ID"):
        profile = "slurm"
        log.info("Detected SLURM environment, using slurm profile")
    
    run_batch(
        samples_csv=samples_csv,
        output_dir=Path(output_dir),
        overwrite=overwrite,
        profile=profile,
        account=account,
        partition=partition,
        max_cpus=max_cpus,
    )
    
    log.info("Pipeline complete!")

