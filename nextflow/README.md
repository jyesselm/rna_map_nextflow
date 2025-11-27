# RNA MAP Nextflow Workflow

A production-ready Nextflow workflow for running the RNA MAP pipeline on single samples or batch processing multiple samples.

## ✅ Status

- **Setup**: Complete
- **Testing**: Passed
- **Validation**: Results match original pipeline
- **Ready**: For production use

## Quick Start

### 1. Setup Environment

```bash
cd nextflow/
./setup_conda.sh
conda activate rna_map_nextflow
```

### 2. Run Single Sample

```bash
nextflow run main.nf \
    -profile local \
    --fasta /path/to/reference.fasta \
    --fastq1 /path/to/reads_1.fastq \
    --fastq2 /path/to/reads_2.fastq \
    --dot_bracket /path/to/structure.csv \
    --output_dir results
```

### 3. Run Multiple Samples

Create `samples.csv`:
```csv
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,ref1.fasta,r1_1.fastq,r1_2.fastq,struct1.csv
```

Then:
```bash
nextflow run main.nf --samples_csv samples.csv --output_dir results
```

## Documentation

- **[NEXT_STEPS.md](NEXT_STEPS.md)** - Detailed usage guide and next steps
- **[VALIDATION_RESULTS.md](VALIDATION_RESULTS.md)** - Validation against original pipeline
- **[SETUP.md](SETUP.md)** - Environment setup instructions
- **[TEST_LOCAL.md](TEST_LOCAL.md)** - Local testing guide

## Features

- ✅ **Validated**: Produces identical results to original pipeline
- ✅ **Scalable**: Handles single samples or batch processing
- ✅ **Cluster-ready**: Configured for SLURM
- ✅ **File-efficient**: Optimized for 5M file limit
- ✅ **Reproducible**: Conda environment with all dependencies

## Requirements

- Java 11+ (included in conda environment)
- Nextflow (included in conda environment)
- Conda/Mamba

## Configuration

### Tool Arguments (FastQC, Trim Galore, Bowtie2)

Customize tool arguments using `params.config`:

```bash
# Use the provided template
nextflow run main.nf -c params.config --fasta ref.fasta --fastq1 reads.fastq

# Or create your own config file
cp params.config my_config.config
# Edit my_config.config with your preferred arguments
nextflow run main.nf -c my_config.config --fasta ref.fasta --fastq1 reads.fastq
```

The `params.config` file allows you to set:
- **FastQC arguments**: `params.fastqc_args = "--threads 4"`
- **Trim Galore arguments**: `params.tg_args = "--length 20 --adapter AGATCGGAAGAGC"`
- **Bowtie2 arguments**: `params.bt2_alignment_args = "--local;--no-unal;-X 1000"`

### Nextflow Configuration

Edit `nextflow.config` for:
- SLURM cluster settings
- Resource allocation
- File paths
- Module loading

See [NEXT_STEPS.md](NEXT_STEPS.md) for detailed configuration options.

## Support

- Nextflow docs: https://www.nextflow.io/docs/latest/
- RNA MAP docs: See `../docs/` directory
- Workflow logs: Check `.nextflow.log`
