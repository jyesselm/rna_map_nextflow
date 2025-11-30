# Bowtie2 Parameter Optimization

This directory contains everything needed for optimizing Bowtie2 alignment parameters for RNA-MAP workflows. This is a self-contained module that can be extracted to a separate repository.

## Overview

This optimization toolkit provides:
- **Automated parameter optimization** using Optuna (Bayesian optimization)
- **Grid search** for systematic parameter exploration
- **Cluster-based optimization** for large-scale runs
- **Analysis tools** for interpreting results
- **Recommended parameters** based on extensive analysis

## Quick Start

### Use Recommended Parameters

Recommended parameters from optimization are available in:
- **[docs/recommended_params/best_parameters.txt](./docs/recommended_params/best_parameters.txt)** - Full parameter string
- **[docs/BEST_PARAMETERS.md](./docs/BEST_PARAMETERS.md)** - Detailed breakdown

### Run Your Own Optimization

#### Local Optimization

1. **Setup environment**:
   ```bash
   conda env create -f environment.yml
   conda activate rna-map-optimization
   ```

2. **Run optimization**:
   ```bash
   python scripts/optimize_bowtie2_params_optuna.py \
       --fasta reference.fasta \
       --fastq1 reads_R1.fastq \
       --fastq2 reads_R2.fastq \
       --n-trials 100 \
       --output-dir optimization_results
   ```

#### Cluster-Based Optimization

For large-scale optimization on a cluster:

1. **Setup** (see [scripts/README.md](./scripts/README.md) for details):
   - Build container OR setup conda environment
   - Configure optimization settings
   - Prepare test cases

2. **Submit jobs**:
   ```bash
   bash scripts/submit_optimization_jobs.sh
   ```

3. **Collect results**:
   ```bash
   bash scripts/collect_all_results.sh
   ```

## Directory Structure

```
optimization/
├── README.md                 # This file
├── environment.yml           # Conda environment for optimization
├── scripts/                  # All optimization scripts
│   ├── optimize_bowtie2_params.py        # Grid search
│   ├── optimize_bowtie2_params_optuna.py # Bayesian optimization (recommended)
│   ├── run_baseline_test.py              # Baseline comparison
│   ├── collect_top_results.py            # Result aggregation
│   └── [cluster scripts]                 # Cluster-specific scripts
├── docs/                     # Documentation
│   ├── README.md            # Documentation index
│   ├── BEST_PARAMETERS.md   # Recommended parameters
│   ├── TOP_100_PARAMETER_ANALYSIS.md  # Analysis results
│   ├── recommended_params/  # Parameter files
│   ├── examples/            # Example scripts
│   └── archive/             # Historical documentation
├── config/                   # Optimization-specific configs
│   └── slurm_optimized.config
└── test/                     # Optimization test cases and results
```

## Documentation

### Essential Guides
- **[docs/BEST_PARAMETERS.md](./docs/BEST_PARAMETERS.md)** - Recommended parameters and usage
- **[docs/TOP_100_PARAMETER_ANALYSIS.md](./docs/TOP_100_PARAMETER_ANALYSIS.md)** - Detailed analysis results
- **[scripts/README.md](./scripts/README.md)** - Cluster-based optimization guide

### Key Results

**Optimal Parameters Summary:**

From analysis of top 100 parameter combinations:

**Constants (use these always):**
- Seed length: 18
- Mismatch penalty: 6,2
- Gap penalties: read=8,4, ref=5,3
- Sensitivity: fast-local
- Min insert size: 50

**Recommended defaults:**
- Max insert size: 200
- Seed mismatches: 1
- Score minimum: L,10,0.2
- Repetitive effort: 4

See **[docs/TOP_100_PARAMETER_ANALYSIS.md](./docs/TOP_100_PARAMETER_ANALYSIS.md)** for complete analysis.

## Scripts

### Main Optimization Scripts

- **`scripts/optimize_bowtie2_params_optuna.py`** - Bayesian optimization using Optuna (recommended)
- **`scripts/optimize_bowtie2_params.py`** - Grid search optimization
- **`scripts/run_baseline_test.py`** - Run baseline with original parameters for comparison

### Analysis Scripts

- **`scripts/collect_top_results.py`** - Aggregate and analyze optimization results

### Cluster Scripts

- **`scripts/submit_optimization_jobs.sh`** - Submit optimization jobs to cluster
- **`scripts/collect_all_results.sh`** - Collect and aggregate all results
- **`scripts/build_optimization_container.sh`** - Build container for cluster use
- See [scripts/README.md](./scripts/README.md) for complete cluster guide

## Configuration

- **`environment.yml`** - Conda environment with all dependencies
- **`config/slurm_optimized.config`** - Optimized SLURM configuration
- **`scripts/cluster_optimization_config.yml`** - Cluster optimization settings

## Test Cases

Optimization test cases and results are in `test/` directory:
- Contains optimization results from various test cases
- Includes baseline comparisons
- Historical optimization runs

## Usage Examples

### Quick Optimization (Local)

```bash
conda activate rna-map-optimization
python scripts/optimize_bowtie2_params_optuna.py \
    --fasta test.fasta \
    --fastq1 test_R1.fastq \
    --fastq2 test_R2.fastq \
    --n-trials 50
```

### Baseline Comparison

```bash
python scripts/run_baseline_test.py \
    --fasta test.fasta \
    --fastq1 test_R1.fastq \
    --fastq2 test_R2.fastq \
    --output-dir baseline_results
```

### Cluster Optimization

See [scripts/README.md](./scripts/README.md) for detailed cluster workflow.

## Results and Analysis

Optimization results include:
- Best parameter combinations
- Quality scores and statistics
- Comparison with baseline
- Visualization of optimization history (Optuna)

See **[docs/TOP_100_PARAMETER_ANALYSIS.md](./docs/TOP_100_PARAMETER_ANALYSIS.md)** for comprehensive analysis of optimization results.

## Notes

- This directory is self-contained and can be extracted to a separate repository
- All optimization-related code, docs, configs, and tests are here
- Main workflow code remains in the parent repository
- See parent repository README for main workflow documentation

