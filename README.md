


# RNA MAP

[![CI](https://github.com/YesselmanLab/rna_map/actions/workflows/ci.yml/badge.svg)](https://github.com/YesselmanLab/rna_map/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: flake8](https://img.shields.io/badge/linting-flake8-greenyellow)](https://github.com/PyCQA/flake8)
[![PYPI package](https://badge.fury.io/py/rna-map.png)](http://badge.fury.io/py/rna-map)

## Table of Contents

- [Overview](#overview)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
  - [Using Conda (Recommended)](#using-conda-recommended)
- [Quick Start](#quick-start)
- [Testing](#testing)
  - [Local Testing](#local-testing)
  - [Cluster Testing](#cluster-testing)
- [Usage Examples](#usage-examples)
  - [Basic Usage](#basic-usage)
  - [Advanced Usage](#advanced-usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Citation](#citation)

## Overview

**RNA MAP** is an open-source tool for rapid analysis of RNA mutational profiling (MaP) experiments. This tool was inspired by the DREEM algorithm developed by the Rouskin Lab and provides a comprehensive platform for analyzing DMS-reactivity of RNA molecules.

### What is RNA MaP?

RNA mutational profiling (MaP) is a powerful technique that uses dimethyl sulfate (DMS) to probe RNA structure by introducing mutations during reverse transcription. The resulting sequencing data reveals the structural state of RNA molecules at single-nucleotide resolution.

### Key Features

- **Fast and accurate analysis** of DMS-MaPseq experiments
- **Nextflow-based orchestration** for scalable, reproducible workflows
- **Support for both single-end and paired-end** sequencing data
- **Quality control integration** with FastQC and Trim Galore
- **Flexible alignment options** using Bowtie2
- **Interactive visualizations** with Plotly
- **Batch processing** capabilities for large datasets (local and HPC clusters)
- **Docker support** for reproducible environments

### Input Requirements

- **FASTA file**: Reference RNA sequence(s) of interest
- **FASTQ file(s)**: Raw sequencing data from DMS-MaPseq experiment
- **Optional**: Dot-bracket structure file for enhanced visualization

## Software Requirements

### Core Dependencies
- **Python**: 3.8 or greater
- **Nextflow**: 22.10+ (for workflow orchestration)
- **Bowtie2**: 2.2.9+ (for sequence alignment)
- **FastQC**: 0.11.9+ (for quality control)
- **Trim Galore**: 0.6.6+ (for adapter trimming)
- **Cutadapt**: 1.18+ (for quality trimming)

### Optional Dependencies
- **Conda/Mamba**: For environment management
- **Docker**: For containerized deployment
- **SLURM**: For HPC cluster execution (optional)

> **💡 Recommendation**: If you're trying the software for the first time, we highly recommend using the Docker image for a hassle-free experience.

## Installation

### Using Conda (Recommended)

The easiest way to set up RNA MAP Nextflow is using the provided `environment.yml` file:

```bash
# Clone the repository
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow

# Create environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate rna-map-nextflow

# Install Python package (makes it available in conda environment)
cd src/rna_map && python -m pip install -e . && cd ../..
```

The `src/rna_map/` directory contains the Python package. Install it with `pip install -e src/rna_map` to make it available in your conda environment without needing PYTHONPATH.

### Using Docker

Docker provides the most reliable installation method with all dependencies pre-configured:

```bash
# Clone the repository
git clone https://github.com/YesselmanLab/rna_map
cd rna_map

# Build the Docker image
# For Linux and Intel Mac:
docker build -t rna-map -f docker/Dockerfile .

# For Apple Silicon Mac (ARM64):
docker build -t rna-map --platform linux/amd64 -f docker/Dockerfile .

# Run RNA MAP with Docker
rna-map -fa <fasta_file> -fq1 <fastq_file> --docker
```

### From Source

For development or if you need the latest features:

```bash
# Clone the repository
git clone https://github.com/YesselmanLab/rna_map
cd rna_map

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a quick reference guide.

### Basic Analysis

```bash
# Single sample (after installing package with pip install -e src/rna_map)
nextflow run main.nf \
    -profile local \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --dot_bracket structures.csv \
    --output_dir results
```

## Testing

### 🧪 Comprehensive Testing Documentation

**For cluster testing, see the complete testing documentation:**

- **[📘 Testing Index](docs/TESTING_INDEX.md)** - Navigate all testing docs
- **[📗 Cluster Testing Guide](docs/CLUSTER_TESTING_GUIDE.md)** - Complete step-by-step guide (625 lines)
- **[📕 Quick Reference](docs/CLUSTER_TESTING_QUICKREF.md)** - Essential commands and fixes
- **[📋 Testing Checklist](docs/TESTING_CHECKLIST.md)** - Systematic testing checklist

### Quick Start Testing

**On Cluster (Recommended):**
```bash
# 1. Run automated comprehensive test
./test/nextflow/test_cluster.sh

# 2. Or submit as SLURM job
sbatch test/nextflow/test_cluster.sh
```

**Local Testing:**
```bash
# Quick syntax validation
./test/nextflow/test_local_simple.sh

# Full workflow test
./test/nextflow/test_local.sh
```

### Testing Documentation Overview

The testing documentation package includes:

1. **CLUSTER_TESTING_GUIDE.md** (625 lines)
   - 5 testing levels (syntax → parallel)
   - SLURM job script templates
   - Troubleshooting guide (10+ common issues)
   - Result verification procedures

2. **CLUSTER_TESTING_QUICKREF.md** (87 lines)
   - One-command setup
   - Essential commands
   - Common issues & fixes table

3. **TESTING_CHECKLIST.md** (166 lines)
   - Pre-testing setup checklist
   - Installation verification
   - Test execution steps
   - Output verification

4. **test_cluster.sh** - Automated test suite
   - Tests environment, tools, configuration
   - Can run interactively or as SLURM job
   - Comprehensive validation

**See [docs/TESTING_INDEX.md](docs/TESTING_INDEX.md) for complete navigation guide.**

## Usage Examples

### Basic Usage

#### Single-End Analysis
```bash
rna-map -fa my_rna.fasta -fq1 my_reads.fastq
```

#### Paired-End Analysis
```bash
rna-map -fa my_rna.fasta -fq1 reads_R1.fastq -fq2 reads_R2.fastq
```

#### With Secondary Structure
```bash
rna-map -fa my_rna.fasta -fq1 my_reads.fastq --dot-bracket structures.csv
```

### Advanced Usage

#### Using Parameter Files
```bash
# Create a custom parameter file
rna-map -fa my_rna.fasta -fq1 my_reads.fastq -pf custom_params.yml

# Use preset parameters for barcoded libraries
rna-map -fa my_rna.fasta -fq1 my_reads.fastq -pp barcoded-library
```

#### Quality Control Options
```bash
# Skip quality control steps for faster processing
rna-map -fa my_rna.fasta -fq1 my_reads.fastq --skip-fastqc --skip-trim-galore

# Custom quality cutoff
rna-map -fa my_rna.fasta -fq1 my_reads.fastq --tg-q-cutoff 20
```

#### Bit Vector Filtering
```bash
# Apply strict filtering criteria
rna-map -fa my_rna.fasta -fq1 my_reads.fastq \
  --map-score-cutoff 20 \
  --qscore-cutoff 20 \
  --mutation-count-cutoff 2 \
  --percent-length-cutoff 0.8
```

### Working with Large Datasets

For large datasets with thousands of reference sequences:

```bash
# Generate summary only (no individual plots)
rna-map -fa large_dataset.fasta -fq1 reads.fastq --summary-output-only

# Skip bit vector generation for very large datasets
rna-map -fa large_dataset.fasta -fq1 reads.fastq --skip-bit-vector
```

### Nextflow Workflow (Recommended)

This repository is structured as a **Nextflow-first** package. The Nextflow workflow provides scalable, reproducible processing of RNA MAP analyses.

#### Quick Start

```bash
# 1. Setup environment
conda env create -f environment.yml
conda activate rna-map-nextflow

# 2. Install Python package
cd src/rna_map && pip install -e . && cd ../..

# 3. Run single sample
nextflow run main.nf \
    -profile local \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --dot_bracket structure.csv \
    --output_dir results

# 4. Run multiple samples
# Create samples.csv:
# sample_id,fasta,fastq1,fastq2,dot_bracket
# sample1,ref1.fasta,s1_R1.fastq,s1_R2.fastq,struct1.csv
# sample2,ref2.fasta,s2_R1.fastq,s2_R2.fastq,struct2.csv

nextflow run main.nf \
    -profile slurm \
    --samples_csv samples.csv \
    --output_dir results
```

#### Configuration Profiles

- **`local`**: For local execution (uses all available CPUs)
- **`slurm`**: For SLURM cluster execution (default)

```bash
# Local execution
nextflow run main.nf -profile local --fasta ref.fasta --fastq1 reads.fastq

# SLURM cluster execution
nextflow run main.nf -profile slurm --account myaccount --partition normal --fasta ref.fasta --fastq1 reads.fastq
```

#### Key Features

- **Standard Nextflow Structure**: Follows Nextflow best practices
- **Minimal Python Library**: Only Python code needed by the workflow (in `src/rna_map/`)
- **Scalable**: Automatic parallelization on local machines or HPC clusters
- **Reproducible**: Conda environment with all dependencies
- **Cluster-Ready**: Pre-configured for SLURM with resource management

#### Detailed Usage Examples

**Example 1: Demultiplex Multiplexed FASTQ Files**

If you have a single FASTQ file pair with multiple barcoded samples:

```bash
# Create a barcodes CSV file
cat > barcodes.csv << EOF
barcode,sample_id,fasta,dot_bracket
AAAA,sample1,ref1.fasta,ref1.csv
TTTT,sample2,ref2.fasta,ref2.csv
GGGG,sample3,ref3.fasta,
EOF

# Demultiplex the FASTQ files
rna-map-pipeline demultiplex \
    multiplexed_R1.fastq \
    multiplexed_R2.fastq \
    barcodes.csv \
    --output-dir demultiplexed

# This creates:
# - demultiplexed/sample1_R1.fastq, sample1_R2.fastq
# - demultiplexed/sample2_R1.fastq, sample2_R2.fastq
# - demultiplexed/sample3_R1.fastq, sample3_R2.fastq
# - samples.csv (ready for processing)
```

**Example 2: Process Multiple Samples Locally**

For local processing with a small number of samples:

```bash
# Create samples.csv manually or from demultiplexing
cat > samples.csv << EOF
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,ref1.fasta,sample1_R1.fastq,sample1_R2.fastq,ref1.csv
sample2,ref2.fasta,sample2_R1.fastq,sample2_R2.fastq,ref2.csv
sample3,ref3.fasta,sample3_R1.fastq,sample3_R2.fastq,
EOF

# Process sequentially (no Dask, good for <10 samples)
rna-map-pipeline run samples.csv --sequential

# Or process in parallel with 4 local workers
rna-map-pipeline run samples.csv --num-workers 4 --environment local
```

**Example 3: Process Many Samples on HPC**

For processing hundreds of samples on an HPC cluster:

```bash
# Process 200 samples with 100 workers
# Automatically detects HPC environment and uses SLURM
rna-map-pipeline run samples.csv \
    --num-workers 100 \
    --account myaccount \
    --partition normal

# Workers stay alive and process multiple samples each
# This saves hours of queue time compared to submitting individual jobs!
```

**Example 4: Full Pipeline Workflow**

Complete workflow from multiplexed FASTQ to results:

```bash
# Step 1: Demultiplex
rna-map-pipeline demultiplex \
    multiplexed_R1.fastq \
    multiplexed_R2.fastq \
    barcodes.csv \
    --output-dir demultiplexed

# Step 2: Process all samples in parallel
rna-map-pipeline run samples.csv --num-workers 100

# Or do it all in one command:
rna-map-pipeline full \
    multiplexed_R1.fastq \
    multiplexed_R2.fastq \
    barcodes.csv \
    --num-workers 100
```

**Example 5: Single-End Sequencing**

For single-end sequencing data:

```bash
cat > samples.csv << EOF
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,ref1.fasta,sample1.fastq,,ref1.csv
sample2,ref2.fasta,sample2.fastq,,
EOF

rna-map-pipeline run samples.csv --output-dir results
```

**Example 6: Python API Usage**

You can also use the pipeline programmatically:

```python
from pathlib import Path
from rna_map.pipeline.simple_pipeline import Sample, process_samples, run_rna_map_sample
from rna_map.cli.nextflow_wrapper import run_batch

# Single sample
sample = Sample(
    sample_id="my_sample",
    fasta=Path("ref.fasta"),
    fastq1=Path("reads_R1.fastq"),
    fastq2=Path("reads_R2.fastq"),
    dot_bracket=Path("structure.csv"),
)

result = run_rna_map_sample(sample, overwrite=True)
print(f"Status: {result['status']}")

# Multiple samples sequentially
samples = [sample1, sample2, sample3]
results = process_samples(samples, overwrite=True)

# Multiple samples in parallel (with Nextflow)
# First create a samples.csv file, then:
run_batch(
    samples_csv=Path("samples.csv"),
    output_dir=Path("results"),
    overwrite=True,
    profile="slurm",  # or "local"
    account="myaccount",
    partition="normal",
    max_cpus=16,
)
```

**Example 7: Checking Results**

After processing, check the results:

```bash
# Results are saved to results_summary.csv
cat results_summary.csv

# Each sample's output is in its own directory
# Structure: results/{sample_id}/
#   - BitVector_Files/
#   - Mapping_Files/
#   - log/
```

**Example 8: Error Handling**

The pipeline handles errors gracefully:

```bash
# If some samples fail, check results_summary.csv
# Failed samples will have status="error" and error details

# Re-run only failed samples
# (filter samples.csv to only include failed ones, then re-run)
```

### Docker Usage

```bash
# Run with Docker (Linux/Intel Mac)
rna-map -fa my_rna.fasta -fq1 my_reads.fastq --docker

# Run with Docker (Apple Silicon Mac)
rna-map -fa my_rna.fasta -fq1 my_reads.fastq --docker --docker-platform linux/amd64
```



## Command Line Reference

For a complete list of available options, run:

```bash
rna-map --help
```

### Main Arguments
- `-fa, --fasta PATH`: Reference sequences in FASTA format (required)
- `-fq1, --fastq1 PATH`: Single-end reads or first pair of paired-end reads (required)
- `-fq2, --fastq2 PATH`: Second pair of paired-end reads (optional)
- `--dot-bracket PATH`: CSV file with secondary structure information
- `-pf, --param-file PATH`: Custom parameter file (YAML format)
- `-pp, --param-preset TEXT`: Use preset parameters (e.g., 'barcoded-library')

### Quality Control Options
- `--skip-fastqc`: Skip FastQC quality control
- `--skip-trim-galore`: Skip Trim Galore adapter trimming
- `--tg-q-cutoff INTEGER`: Quality cutoff for Trim Galore (default: 20)

### Alignment Options
- `--bt2-alignment-args TEXT`: Custom Bowtie2 arguments (comma-separated)
- `--save-unaligned PATH`: Save unaligned reads to specified path

### Bit Vector Options
- `--skip-bit-vector`: Skip bit vector generation
- `--summary-output-only`: Generate summary only (no individual plots)
- `--map-score-cutoff INTEGER`: Minimum mapping score threshold
- `--qscore-cutoff INTEGER`: Quality score threshold for nucleotides
- `--mutation-count-cutoff INTEGER`: Maximum mutations per read
- `--percent-length-cutoff FLOAT`: Minimum read length percentage
- `--min-mut-distance INTEGER`: Minimum distance between mutations

### Docker Options
- `--docker`: Run in Docker container
- `--docker-image TEXT`: Specify Docker image
- `--docker-platform TEXT`: Specify platform (e.g., linux/amd64)

### Other Options
- `--overwrite`: Overwrite existing output directory
- `--debug`: Enable debug mode
- `--help`: Show help message

## Troubleshooting

### Common Issues

#### Installation Problems

**Problem**: `rna-map` command not found after installation
```bash
# Solution: Ensure the conda environment is activated
conda activate rna-map
which rna-map
```

**Problem**: Missing dependencies (bowtie2, fastqc, etc.)
```bash
# Solution: Install using conda
conda install -c bioconda bowtie2 fastqc cutadapt trim-galore
```

#### Runtime Errors

**Problem**: Low alignment rates
- Check that your FASTQ files are properly formatted
- Verify that the reference sequence matches your experimental setup
- Try adjusting Bowtie2 parameters: `--bt2-alignment-args "very-sensitive-local"`

**Problem**: Memory issues with large datasets
```bash
# Solution: Use summary-only mode for large datasets
rna-map -fa large_dataset.fasta -fq1 reads.fastq --summary-output-only
```

**Problem**: Docker permission errors
```bash
# Solution: Add user to docker group (Linux) or use sudo
sudo usermod -aG docker $USER
# Then log out and back in
```

#### Quality Control Issues

**Problem**: Poor quality scores
- Check your sequencing quality
- Adjust quality cutoff: `--tg-q-cutoff 15` (lower threshold)
- Skip quality control if data is known to be good: `--skip-fastqc --skip-trim-galore`

**Problem**: No mutations detected
- Verify DMS treatment was performed correctly
- Check that reference sequence is correct
- Lower mutation count cutoff: `--mutation-count-cutoff 1`

### Getting Help

1. **Check the logs**: RNA MAP provides detailed logging information
2. **Use debug mode**: Add `--debug` flag for verbose output
3. **Test with sample data**: Use the provided test files in `test/resources/`
4. **GitHub Issues**: Report bugs and ask questions on the [GitHub repository](https://github.com/YesselmanLab/rna_map/issues)

### Example Output

A successful run will show:
```
rna_map.CLI - INFO - Starting RNA MAP analysis...
rna_map.RUN - INFO - Found 1 valid reference sequences
rna_map.MAPPING - INFO - Bowtie2 2.4.5 detected!
rna_map.MAPPING - INFO - FastQC v0.11.9 detected!
rna_map.MAPPING - INFO - Trim Galore 0.6.6 detected!
rna_map.EXTERNAL_CMD - INFO - Running FastQC...
rna_map.EXTERNAL_CMD - INFO - FastQC completed successfully
rna_map.EXTERNAL_CMD - INFO - Running Trim Galore...
rna_map.EXTERNAL_CMD - INFO - Trim Galore completed successfully
rna_map.EXTERNAL_CMD - INFO - Running Bowtie2 alignment...
rna_map.EXTERNAL_CMD - INFO - Bowtie2 alignment completed successfully
rna_map.BIT_VECTOR - INFO - Starting bit vector generation...
rna_map.BIT_VECTOR - INFO - Analysis completed successfully!
```

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/YesselmanLab/rna_map
cd rna_map

# Create development environment
conda env create -f environment.yml
conda activate rna-map

# Install in development mode
pip install -e ".[dev]"

# Install Python package (if not already done)
cd src/rna_map && python -m pip install -e . && cd ../..

# Run Python tests (if you have pytest installed)
# pytest test/  # Optional - test src/rna_map/ modules

# Run Nextflow tests
./test/nextflow/test_local_simple.sh  # Quick syntax validation
./test/nextflow/test_local.sh         # Full workflow test

# Run Nextflow linting
./lint.sh

# Format Nextflow code
./fmt.sh
```

### Continuous Integration

The CI pipeline automatically runs:
- Python library import tests (verifies src/rna_map/ modules work)
- Nextflow workflow validation and syntax checks
- Bioinformatics tool verification

All tests must pass before merging pull requests.


### Code Style

This project uses:
- **Nextflow lint/fmt** for Nextflow code (Nextflow 25.04+)
- **Ruff** for Python code formatting and linting (in src/rna_map/)
- **MyPy** for type checking (optional, for src/rna_map/)
- **Pytest** for testing (optional, for src/rna_map/)

## Citation

If you use RNA MAP in your research, please cite:

```
Yesselman, J.D., et al. (2022). RNA mutational profiling (MaP) with DREEM reveals 
structural and functional insights into RNA structure. Nucleic Acids Research, 
50(12), e70. https://doi.org/10.1093/nar/gkac435
```
