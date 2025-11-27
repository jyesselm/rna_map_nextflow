# RNA MAP Nextflow - Quick Start Guide

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow

# 2. Create conda environment
conda env create -f environment.yml
conda activate rna-map-nextflow

# 3. Set PYTHONPATH (required!)
export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"
```

## Basic Usage

### Single Sample

```bash
nextflow run main.nf \
    -profile local \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --dot_bracket structure.csv \
    --output_dir results
```

### Multiple Samples

Create `samples.csv`:
```csv
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,ref1.fasta,s1_R1.fastq,s1_R2.fastq,struct1.csv
sample2,ref2.fasta,s2_R1.fastq,s2_R2.fastq,struct2.csv
```

Run:
```bash
nextflow run main.nf \
    -profile slurm \
    --samples_csv samples.csv \
    --output_dir results
```

## Configuration Profiles

- **`local`**: For local execution
  ```bash
  nextflow run main.nf -profile local --fasta ref.fasta --fastq1 reads.fastq
  ```

- **`slurm`**: For SLURM cluster execution
  ```bash
  nextflow run main.nf -profile slurm --account myaccount --partition normal --fasta ref.fasta --fastq1 reads.fastq
  ```

## Testing

### Local Testing

```bash
# Quick syntax validation
./test/nextflow/test_local_simple.sh

# Full workflow test (requires test data)
./test/nextflow/test_local.sh
```

### Cluster Testing

**For comprehensive cluster testing, see [docs/CLUSTER_TESTING_GUIDE.md](docs/CLUSTER_TESTING_GUIDE.md)**

Quick cluster test:
```bash
# Run comprehensive test suite
./test/nextflow/test_cluster.sh

# Or submit as SLURM job
sbatch test/nextflow/test_cluster.sh
```

The cluster testing guide includes:
- Step-by-step testing procedures (5 levels)
- SLURM job script templates
- Troubleshooting guide
- Result verification procedures
- Advanced testing scenarios

## Troubleshooting

### PYTHONPATH not set
```bash
export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"
```

### Java version error
```bash
conda install openjdk=11 -c conda-forge
```

### Nextflow not found
```bash
conda install nextflow -c bioconda
```

## Key Files

- `main.nf` - Main workflow
- `nextflow.config` - Configuration
- `conf/` - Configuration profiles
- `modules/` - Nextflow modules
- `workflows/` - Subworkflows
- `lib/` - Python library (minimal)

## More Information

See `README.md` for detailed documentation.

