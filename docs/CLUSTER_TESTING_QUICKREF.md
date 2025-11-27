# Cluster Testing Quick Reference

## One-Command Setup & Test

```bash
# Clone, setup, and run comprehensive test
git clone https://github.com/jyesselm/rna_map_nextflow && \
cd rna_map_nextflow && \
conda env create -f environment.yml && \
conda activate rna-map-nextflow && \
export PYTHONPATH="${PWD}/lib:${PYTHONPATH}" && \
./test/nextflow/test_cluster.sh
```

## Essential Commands

### Setup
```bash
conda env create -f environment.yml
conda activate rna-map-nextflow
export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"
```

### Verify Installation
```bash
which nextflow java bowtie2 fastqc trim_galore
python -c "from lib.bit_vectors import generate_bit_vectors; print('OK')"
```

### Quick Test (Interactive)
```bash
./test/nextflow/test_cluster.sh
```

### Quick Test (SLURM Job)
```bash
sbatch test/nextflow/test_cluster.sh
```

### Minimal Workflow Test
```bash
nextflow run main.nf \
    -profile slurm \
    --account YOUR_ACCOUNT \
    --partition normal \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results \
    --skip_fastqc \
    --skip_trim_galore
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| `Module not found: lib` | `export PYTHONPATH="${PWD}/lib:${PYTHONPATH}"` |
| Java version error | `conda install openjdk=11 -c conda-forge` |
| Nextflow not found | `conda install nextflow -c bioconda` |
| Tool not found | `conda install -c bioconda bowtie2 fastqc trim-galore` |
| SLURM account error | Check with `sacctmgr show user $USER` |

## Test Levels

1. **Syntax**: `./test/nextflow/test_local_simple.sh`
2. **Dry Run**: `nextflow run main.nf --help`
3. **Minimal**: Run with `--skip_fastqc --skip_trim_galore`
4. **Full**: Run with all steps enabled
5. **Parallel**: Run with `--split_fastq`

## Verify Results

```bash
# Check output structure
ls -lh test_results/<sample_id>/BitVector_Files/

# Check key files
head test_results/<sample_id>/BitVector_Files/summary.csv
ls test_results/<sample_id>/BitVector_Files/mutation_histos.*
```

## Full Documentation

See [CLUSTER_TESTING_GUIDE.md](CLUSTER_TESTING_GUIDE.md) for complete instructions.

