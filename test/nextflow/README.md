# Nextflow Test Scripts

This directory contains test scripts for the RNA MAP Nextflow workflow.

## Test Scripts

### `test_cluster.sh` ⭐ **START HERE FOR CLUSTER TESTING**
Comprehensive test suite for cluster environments. Tests:
- Environment setup
- Tool availability
- PYTHONPATH configuration
- File structure
- Test data availability
- Nextflow syntax validation
- Configuration files
- Dry run execution

**Usage:**
```bash
# Interactive (on compute node)
./test/nextflow/test_cluster.sh

# As SLURM job
sbatch test/nextflow/test_cluster.sh
```

### `test_local_simple.sh`
Quick syntax validation - checks that workflow files are valid.
Does not require Java or full execution.

**Usage:**
```bash
./test/nextflow/test_local_simple.sh
```

### `test_local.sh`
Full workflow test on local machine. Requires:
- Java 8-18
- Nextflow installed
- Test data available
- All tools installed

**Usage:**
```bash
./test/nextflow/test_local.sh
```

### `test_local_conda.sh`
Test using conda environment. Automatically uses conda environment.

**Usage:**
```bash
./test/nextflow/test_local_conda.sh
```

### `test_parallel.sh`
Test parallel FASTQ splitting and processing.

**Usage:**
```bash
./test/nextflow/test_parallel.sh
```

## Testing Order (Recommended)

1. **First**: Run `test_cluster.sh` to verify environment
2. **Second**: Run `test_local_simple.sh` for syntax check
3. **Third**: Run `test_local.sh` for full workflow test
4. **Fourth**: Run `test_parallel.sh` for parallel processing test

## Documentation

- **Cluster Testing**: See [../../docs/CLUSTER_TESTING_GUIDE.md](../../docs/CLUSTER_TESTING_GUIDE.md)
- **Quick Reference**: See [../../docs/CLUSTER_TESTING_QUICKREF.md](../../docs/CLUSTER_TESTING_QUICKREF.md)
- **Main README**: See [../../README.md](../../README.md)

## Test Data

Test data is located in `../../test/resources/case_1/`:
- `test.fasta` - Reference sequence
- `test_mate1.fastq` - Forward reads
- `test_mate2.fastq` - Reverse reads
- `test.csv` - Dot-bracket structure

## Troubleshooting

If tests fail:
1. Check PYTHONPATH is set: `echo $PYTHONPATH`
2. Verify environment: `conda activate rna-map-nextflow`
3. Check tools: `which nextflow java bowtie2`
4. See [CLUSTER_TESTING_GUIDE.md](../../docs/CLUSTER_TESTING_GUIDE.md) for detailed troubleshooting
