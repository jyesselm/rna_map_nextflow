# Cluster-Based Bowtie2 Optimization

This directory contains scripts for running large-scale Bowtie2 parameter optimization on a cluster.

## Setup

### 1. Setup Conda Environment

First, create the conda environment with all dependencies:

```bash
bash scripts/optimization/setup_optimization_env.sh
```

This will:
- Create a conda environment named `rna-map-optimization`
- Install Bowtie2, Python dependencies, and Optuna
- Install the `rna_map` package in editable mode

### 2. Prepare Test Cases

Create a `data/` directory in the project root and organize test cases:

```
data/
├── case_1/
│   ├── reference.fasta
│   ├── reads_R1.fastq.gz
│   └── reads_R2.fastq.gz
├── case_2/
│   ├── reference.fasta
│   ├── reads_R1.fastq.gz
│   └── reads_R2.fastq.gz
└── ...
```

**Required files per case:**
- `*.fasta` or `*.fa` - Reference sequence(s)
- `*_R1*.fastq*` or `*_1.fastq*` - Read 1 (required)
- `*_R2*.fastq*` or `*_2.fastq*` - Read 2 (optional, for paired-end)

### 3. Configure Optimization Settings

Edit `scripts/optimization/cluster_optimization_config.yml` to set:

- **Optimization parameters**: Number of combinations, threads, cutoffs
- **Cluster settings**: Partition, time limits, memory, CPUs
- **Output settings**: Base directory, whether to keep intermediates

Example configuration:

```yaml
optimization:
  max_combinations: 200
  read_length: 150
  threads: 8
  mapq_cutoff: 20

cluster:
  partition: "normal"
  time: "24:00:00"
  memory: "32G"
  cpus: 8
  account: "your_account"  # Set if required
```

### 4. Submit Jobs

Run the submission script:

```bash
bash scripts/optimization/submit_optimization_jobs.sh
```

This will:
- Scan `data/` for all test cases
- Create SLURM job scripts for each case
- Submit jobs to the cluster
- Create output directories for results

## Output Structure

Results will be organized as:

```
optimization_results/
├── case_1/
│   ├── <job_id>.out          # Job stdout
│   ├── <job_id>.err          # Job stderr
│   ├── index/                 # Bowtie2 index
│   ├── results/               # Alignment results
│   │   ├── baseline/          # Baseline results
│   │   └── combo_XXX/         # Parameter combination results
│   ├── best_parameters.json   # Best parameters found
│   ├── optimization_results.json  # All results
│   └── optimization_summary.csv   # Summary CSV
├── case_2/
│   └── ...
└── job_scripts/               # Submitted job scripts
    ├── case_1_optimization.sh
    └── case_2_optimization.sh
```

## Monitoring Jobs

Check job status:

```bash
squeue -u $USER
```

View job output:

```bash
tail -f optimization_results/case_1/<job_id>.out
```

Cancel a job:

```bash
scancel <job_id>
```

## Per-Case Overrides

You can override settings for specific cases in the config file:

```yaml
case_overrides:
  case_1:
    max_combinations: 500
    time: "48:00:00"
    memory: "64G"
  case_2:
    max_combinations: 100
    time: "12:00:00"
```

## Single vs Multiple Sequences

The optimization script automatically detects the number of sequences:

- **Single sequence**: Uses permissive parameters for mutation detection
- **Multiple sequences**: Uses stricter parameters for better discrimination

The script will:
- Use `-k 1` to only report best alignments
- Adjust seed length, scoring thresholds, and effort parameters
- Track multi-mapping statistics

## Troubleshooting

### Environment not found
```bash
# Recreate environment
bash scripts/optimization/setup_optimization_env.sh
```

### Jobs failing
- Check `.err` files for error messages
- Verify all input files exist and are readable
- Check that Bowtie2 is available in the environment
- Ensure sufficient time/memory allocated

### No test cases found
- Verify `data/` directory exists
- Check that subdirectories contain `.fasta` and `.fastq` files
- Ensure file naming matches expected patterns

## Example Workflow

```bash
# 1. Setup environment (once)
bash scripts/optimization/setup_optimization_env.sh

# 2. Prepare data
mkdir -p data/case_1
cp reference.fasta data/case_1/
cp reads_R1.fastq.gz data/case_1/
cp reads_R2.fastq.gz data/case_1/

# 3. Configure (edit config file)
vim scripts/optimization/cluster_optimization_config.yml

# 4. Submit jobs
bash scripts/optimization/submit_optimization_jobs.sh

# 5. Monitor
squeue -u $USER

# 6. Check results
ls optimization_results/case_1/
cat optimization_results/case_1/best_parameters.json
```

