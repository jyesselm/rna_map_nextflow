#!/usr/bin/env python3
"""Test best parameters on case_2 data with same number of reads as case_1.

This script:
1. Reads the optimal parameters from best_parameters.txt
2. Tests them on case_2 data
3. Uses the same number of reads as case_1 (2500 reads)
4. Generates bit vectors and calculates metrics
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict

# Add lib to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from rna_map.io.fasta import fasta_to_dict
from rna_map.logger import get_logger
from rna_map.analysis.bit_vector_iterator import BitVectorIterator
from rna_map.analysis.mutation_histogram import MutationHistogram

log = get_logger("TEST_BEST_PARAMS_CASE2")


def subsample_fastq(input_fastq: Path, output_fastq: Path, num_reads: int) -> None:
    """Subsample FASTQ file to specified number of reads.

    Args:
        input_fastq: Input FASTQ file (can be gzipped)
        output_fastq: Output FASTQ file
        num_reads: Number of reads to extract
    """
    import gzip

    open_func = gzip.open if input_fastq.suffix == ".gz" else open
    mode = "rt" if input_fastq.suffix == ".gz" else "r"

    read_count = 0
    lines_per_read = 4

    with open_func(input_fastq, mode) as f_in, open(output_fastq, "w") as f_out:
        while read_count < num_reads:
            lines = []
            for _ in range(lines_per_read):
                line = f_in.readline()
                if not line:
                    break
                lines.append(line)

            if len(lines) < lines_per_read:
                break

            f_out.writelines(lines)
            read_count += 1

    log.info(f"Extracted {read_count} reads from {input_fastq.name}")


def build_bowtie2_index(fasta: Path, index_dir: Path) -> Path:
    """Build Bowtie2 index from FASTA file.

    Args:
        fasta: Path to FASTA file
        index_dir: Directory to store index

    Returns:
        Path to index basename
    """
    index_dir.mkdir(parents=True, exist_ok=True)
    index_name = index_dir / fasta.stem

    if (index_name.with_suffix(".1.bt2")).exists():
        log.info(f"Index already exists: {index_name}")
        return index_name

    log.info(f"Building Bowtie2 index: {index_name}")
    cmd = ["bowtie2-build", str(fasta), str(index_name)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"Failed to build index: {result.stderr}")

    return index_name


def run_bowtie2_alignment(
    index: Path,
    fastq1: Path,
    fastq2: Path | None,
    output_sam: Path,
    bt2_args: list[str],
    threads: int = 4,
) -> Path:
    """Run Bowtie2 alignment with given parameters.

    Args:
        index: Path to Bowtie2 index
        fastq1: Path to first FASTQ file
        fastq2: Path to second FASTQ file (optional)
        output_sam: Path to output SAM file
        bt2_args: List of Bowtie2 arguments
        threads: Number of threads

    Returns:
        Path to stderr file
    """
    stderr_file = output_sam.parent / "bowtie2_stderr.txt"

    # Build command
    cmd = ["bowtie2"] + bt2_args + ["-x", str(index), "-S", str(output_sam)]

    if fastq2 and fastq2.exists():
        cmd.extend(["-1", str(fastq1), "-2", str(fastq2)])
    else:
        cmd.extend(["-U", str(fastq1)])

    # Add threads
    cmd.extend(["-p", str(threads)])

    log.info(f"Running: {' '.join(cmd[:10])}...")
    with open(stderr_file, "w") as stderr:
        result = subprocess.run(cmd, stderr=stderr, stdout=subprocess.PIPE, text=True)

    if result.returncode != 0:
        log.warning(f"Bowtie2 returned non-zero exit code: {result.returncode}")

    return stderr_file


def parse_bowtie2_stats(stderr_file: Path) -> Dict:
    """Parse Bowtie2 alignment statistics.

    Args:
        stderr_file: Path to Bowtie2 stderr output

    Returns:
        Dictionary with alignment statistics
    """
    stats = {
        "total_reads": 0,
        "aligned_0_times": 0,
        "aligned_exactly_1_time": 0,
        "aligned_more_than_1_time": 0,
        "overall_alignment_rate": 0.0,
    }

    if not stderr_file.exists():
        return stats

    with open(stderr_file) as f:
        for line in f:
            line = line.strip()
            if "reads; of these:" in line:
                stats["total_reads"] = int(line.split()[0])
            elif "aligned 0 times" in line:
                stats["aligned_0_times"] = int(line.split()[0])
            elif "aligned exactly 1 time" in line:
                stats["aligned_exactly_1_time"] = int(line.split()[0])
            elif "aligned >1 times" in line:
                stats["aligned_more_than_1_time"] = int(line.split()[0])
            elif "overall alignment rate" in line:
                rate_str = line.split("%")[0].split()[-1]
                stats["overall_alignment_rate"] = float(rate_str)

    return stats


def generate_bit_vectors_and_analyze(
    sam_file: Path,
    ref_seqs: dict[str, str],
    paired: bool,
    qscore_cutoff: int = 25,
    mapq_cutoff: int = 20,
) -> Dict:
    """Generate bit vectors and extract quality metrics.

    Args:
        sam_file: Path to SAM file
        ref_seqs: Dictionary of reference sequences
        paired: Whether reads are paired-end
        qscore_cutoff: Quality score cutoff
        mapq_cutoff: MAPQ cutoff

    Returns:
        Dictionary with metrics including signal-to-noise ratio
    """
    from collections import defaultdict

    metrics = {
        "total_bit_vectors": 0,
        "accepted_bit_vectors": 0,
        "rejected_low_mapq": 0,
        "signal_to_noise": 0.0,
    }

    if not sam_file.exists():
        return metrics

    try:
        # Create mutation histograms
        mut_histos = {}
        for ref_name, ref_seq in ref_seqs.items():
            mut_histos[ref_name] = MutationHistogram(
                ref_name, ref_seq, "DMS", 1, len(ref_seq)
            )

        iterator = BitVectorIterator(
            sam_file,
            ref_seqs,
            paired=paired,
            use_pysam=False,
            qscore_cutoff=qscore_cutoff,
        )

        for bit_vector in iterator:
            metrics["total_bit_vectors"] += 1

            if not bit_vector.reads:
                continue

            if any(read.mapq < mapq_cutoff for read in bit_vector.reads):
                metrics["rejected_low_mapq"] += 1
                continue

            if not bit_vector.data:
                continue

            metrics["accepted_bit_vectors"] += 1

            # Update mutation histogram
            ref_name = bit_vector.reads[0].rname
            if ref_name in mut_histos:
                mh = mut_histos[ref_name]
                mh.num_reads += 1
                mh.num_aligned += 1

                for pos in mh.get_nuc_coords():
                    if pos not in bit_vector.data:
                        continue
                    read_bit = bit_vector.data[pos]
                    mh.cov_bases[pos] += 1

                    if read_bit in ["A", "C", "G", "T"]:
                        mh.mut_bases[pos] += 1
                        mh.mod_bases[read_bit][pos] += 1

        # Calculate signal-to-noise
        total_snr = 0.0
        total_weight = 0
        for ref_name, mh in mut_histos.items():
            if mh.num_aligned > 0:
                snr = mh.get_signal_to_noise()
                total_snr += snr * mh.num_aligned
                total_weight += mh.num_aligned

        if total_weight > 0:
            metrics["signal_to_noise"] = total_snr / total_weight

    except Exception as e:
        log.warning(f"Error generating bit vectors: {e}")

    return metrics


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Test best parameters on case_2 data")
    parser.add_argument(
        "--fasta",
        type=Path,
        default=Path("test/resources/case_2/C009J.fasta"),
        help="Path to reference FASTA file",
    )
    parser.add_argument(
        "--fastq1",
        type=Path,
        default=Path("test/resources/case_2/test_R1.fastq.gz"),
        help="Path to first FASTQ file",
    )
    parser.add_argument(
        "--fastq2",
        type=Path,
        default=Path("test/resources/case_2/test_R2.fastq.gz"),
        help="Path to second FASTQ file",
    )
    parser.add_argument(
        "--num-reads",
        type=int,
        default=2500,
        help="Number of reads to use (default: 2500, same as case_1)",
    )
    parser.add_argument(
        "--params-file",
        type=Path,
        default=Path("best_parameters.txt"),
        help="File with best parameters (default: best_parameters.txt)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("case2_test_results"),
        help="Output directory",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=4,
        help="Number of threads",
    )

    args = parser.parse_args()

    # Read best parameters
    if not args.params_file.exists():
        print(f"ERROR: Parameters file not found: {args.params_file}")
        return 1

    with open(args.params_file) as f:
        params_line = f.read().strip()
        # Extract parameters (skip comments)
        params_line = [
            line for line in params_line.split("\n") if not line.strip().startswith("#")
        ][0]

    bt2_args = params_line.split()

    print("=" * 80)
    print("Testing Best Parameters on Case 2")
    print("=" * 80)
    print(f"FASTA: {args.fasta}")
    print(f"FASTQ1: {args.fastq1}")
    print(f"FASTQ2: {args.fastq2}")
    print(f"Number of reads: {args.num_reads}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Setup output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Subsample reads
    print(f"Subsampling {args.num_reads} reads from case_2...")
    subsampled_fq1 = args.output_dir / "subsampled_R1.fastq"
    subsampled_fq2 = args.output_dir / "subsampled_R2.fastq"

    subsample_fastq(args.fastq1, subsampled_fq1, args.num_reads)
    if args.fastq2.exists():
        subsample_fastq(args.fastq2, subsampled_fq2, args.num_reads)
    else:
        subsampled_fq2 = None

    # Build index
    index_dir = args.output_dir / "index"
    print("Building Bowtie2 index...")
    index = build_bowtie2_index(args.fasta, index_dir)

    # Run alignment
    output_sam = args.output_dir / "aligned.sam"
    print("Running Bowtie2 alignment...")
    stderr_file = run_bowtie2_alignment(
        index, subsampled_fq1, subsampled_fq2, output_sam, bt2_args, args.threads
    )

    # Parse statistics
    alignment_stats = parse_bowtie2_stats(stderr_file)

    # Read reference sequences
    ref_seqs = fasta_to_dict(args.fasta)

    # Generate bit vectors and analyze
    print("Generating bit vectors and calculating metrics...")
    bit_vector_metrics = generate_bit_vectors_and_analyze(
        output_sam,
        ref_seqs,
        paired=subsampled_fq2 is not None,
        qscore_cutoff=25,
        mapq_cutoff=20,
    )

    # Print results
    print()
    print("=" * 80)
    print("Results")
    print("=" * 80)
    print(f"Total reads: {alignment_stats['total_reads']}")
    print(f"Alignment rate: {alignment_stats['overall_alignment_rate']:.2f}%")
    print(f"Aligned exactly 1 time: {alignment_stats['aligned_exactly_1_time']}")
    print(f"Aligned >1 times: {alignment_stats['aligned_more_than_1_time']}")
    print()
    print(f"Total bit vectors: {bit_vector_metrics['total_bit_vectors']}")
    print(f"Accepted bit vectors: {bit_vector_metrics['accepted_bit_vectors']}")
    print(f"Rejected (low MAPQ): {bit_vector_metrics['rejected_low_mapq']}")
    print(f"Signal-to-Noise (AC/GU): {bit_vector_metrics['signal_to_noise']:.2f}")
    print()
    print(f"Results saved to: {args.output_dir}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
