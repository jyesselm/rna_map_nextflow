# RNA MAP Pipeline Guide

## Quick Start

### Basic Usage

```bash
# Install with Dask support
pip install rna-map[dask]

# Process samples in parallel
rna-map-pipeline run samples.csv --num-workers 50
```

### Sample CSV Format

```csv
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,ref1.fasta,sample1_R1.fastq,sample1_R2.fastq,ref1.csv
sample2,ref2.fasta,sample2_R1.fastq,sample2_R2.fastq,ref2.csv
```

## CLI Commands

### Demultiplex FASTQ Files

```bash
rna-map-pipeline demultiplex \
    multiplexed_R1.fastq \
    multiplexed_R2.fastq \
    barcodes.csv \
    --output-dir demultiplexed
```

### Run RNA MAP (Parallel)

```bash
rna-map-pipeline run samples.csv \
    --num-workers 100 \
    --account myaccount \
    --partition normal
```

### Run RNA MAP (Sequential)

```bash
rna-map-pipeline run samples.csv --sequential
```

### Full Pipeline

```bash
rna-map-pipeline full \
    R1.fastq R2.fastq barcodes.csv \
    --num-workers 50
```

## Python API

### Simple: Single Sample

```python
from pathlib import Path
from rna_map.pipeline.simple_pipeline import Sample, run_rna_map_sample

sample = Sample(
    sample_id="test",
    fasta=Path("ref.fasta"),
    fastq1=Path("R1.fastq"),
    fastq2=Path("R2.fastq"),
    dot_bracket=Path("ref.csv"),
)

result = run_rna_map_sample(sample, overwrite=True)
print(result["status"])  # "success" or "error"
```

### Parallel: Multiple Samples

```python
from rna_map.pipeline.simple_pipeline import demultiplex_fastq
from rna_map.pipeline.dask_pipeline import run_samples_parallel

# Demultiplex
samples = demultiplex_fastq(
    fastq1=Path("R1.fastq"),
    fastq2=Path("R2.fastq"),
    barcodes_csv=Path("barcodes.csv"),
    output_dir=Path("demultiplexed"),
)

# Process in parallel
results = run_samples_parallel(
    samples,
    num_workers=100,
    account="myaccount",
    partition="normal",
)
```

## Environment Detection

The pipeline automatically detects local vs HPC:

- **Local**: Uses `LocalCluster` (local CPU cores)
- **HPC**: Uses `SLURMCluster` (submits SLURM jobs)

Same code works everywhere - no changes needed!

## Worker Reuse

**Key benefit**: Workers stay alive and process multiple samples, saving hours of queue time on HPC.

```python
# Without worker reuse: 100 samples × 5 min queue = 500 min queue time
# With worker reuse: 100 workers × 5 min queue = 5 min queue time
# Time saved: 495 minutes (8+ hours)!
```

## Testing

### Run Integration Test

```bash
# Compare new pipeline with original
pytest test/test_pipeline_integration_comparison.py::test_new_pipeline_vs_original -v -s
```

### Run All Tests

```bash
# Unit tests
pytest test/test_simple_pipeline.py -v

# Dask tests
pytest test/test_dask_pipeline.py -v

# CLI tests
pytest test/test_cli_pipeline.py -v
```

## Architecture

```
rna_map/                    (Core pipeline)
├── pipeline/
│   ├── simple_pipeline.py  (Sample processing)
│   └── dask_pipeline.py    (Parallel execution)
└── external/               (FastQC, Trim Galore, Bowtie2)

rna_map_slurm/             (Orchestration - optional)
└── tasks.py                (Split, Demultiplex, Join)
```

**Dependency**: `rna_map_slurm` → `rna_map` (not vice versa)

## Integration with rna_map_slurm

See `docs/RNA_MAP_SLURM_INTEGRATION.md` for details on integrating additional tasks (splitting, internal demultiplexing, combining results).

