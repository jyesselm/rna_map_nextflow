# RNA MAP Nextflow

[![CI](https://github.com/YesselmanLab/rna_map/actions/workflows/ci.yml/badge.svg)](https://github.com/YesselmanLab/rna_map/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: flake8](https://img.shields.io/badge/linting-flake8-greenyellow)](https://github.com/PyCQA/flake8)

**RNA MAP** is an open-source tool for rapid analysis of RNA mutational profiling (MaP) experiments. This repository provides a scalable Nextflow-based workflow for processing DMS-MaPseq data.

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow
conda env create -f environment.yml
conda activate rna-map-nextflow
cd python && pip install -e . && cd ..

# 2. Run workflow
nextflow run main.nf \
    -profile local \
    --fasta reference.fasta \
    --fastq1 reads_R1.fastq \
    --fastq2 reads_R2.fastq \
    --output_dir results
```

### Example: Run with Test Data

To test the pipeline with included test data:

```bash
nextflow run main.nf \
    -profile local \
    --fasta test/data/resources/case_1/test.fasta \
    --fastq1 test/data/resources/case_1/test_mate1.fastq \
    --fastq2 test/data/resources/case_1/test_mate2.fastq \
    --output_dir test_output
```

For detailed instructions, see **[docs/QUICKSTART.md](docs/QUICKSTART.md)** or **[docs/SETUP.md](docs/SETUP.md)**.

## Documentation

### Getting Started
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Quick start guide
- **[SETUP.md](docs/SETUP.md)** - Complete setup guide (environment, IDE, linting)

### Usage & Configuration
- **[PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md)** - Workflow usage and configuration
- **[docs/README.md](docs/README.md)** - Complete documentation index

### Testing & Deployment
- **[CLUSTER_TESTING_GUIDE.md](docs/CLUSTER_TESTING_GUIDE.md)** - Cluster testing guide
- **[CONTAINER_USAGE.md](docs/CONTAINER_USAGE.md)** - Docker/Singularity usage

### Optimization (Separate Module)
- **[optimization/README.md](optimization/README.md)** - Bowtie2 parameter optimization

All documentation is in the **[docs/](docs/)** directory. See **[docs/README.md](docs/README.md)** for a complete index.

## Features

- ✅ **Nextflow-based workflow** - Scalable, reproducible processing
- ✅ **Quality control** - Integrated FastQC and Trim Galore
- ✅ **Flexible alignment** - Bowtie2 with customizable parameters
- ✅ **Batch processing** - Process multiple samples efficiently
- ✅ **Cluster-ready** - Pre-configured for SLURM HPC clusters
- ✅ **Container support** - Docker and Singularity compatibility

## Requirements

### Core Dependencies
- **Python**: 3.10+
- **Nextflow**: 25.04+ (25.10.2 recommended)
- **Java**: 17-24 (required for Nextflow 25.x)
- **Bowtie2**: 2.2.9+
- **FastQC**: 0.11.9+
- **Trim Galore**: 0.6.6+

All dependencies are included in `environment.yml`.

## Installation

### Using Conda (Recommended)

```bash
# Clone repository
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow

# Create environment
conda env create -f environment.yml
conda activate rna-map-nextflow

# Install Python package
cd python && pip install -e . && cd ..
```

### Verify Installation

```bash
nextflow -version  # Should show 25.10.2+
java -version      # Should show Java 17+
```

See **[docs/SETUP.md](docs/SETUP.md)** for detailed setup instructions.

## Usage Examples

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

- **`local`** - Local execution (uses all available CPUs)
- **`slurm`** - SLURM cluster execution (default)

See **[PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md)** for detailed configuration options.

## Project Structure

```
.
├── main.nf              # Main workflow
├── nextflow.config      # Workflow configuration
├── modules/             # Nextflow process modules
├── workflows/           # Subworkflows
├── conf/                # Configuration profiles
├── python/src/rna_map/  # Python library
├── docs/                # Documentation
├── optimization/        # Optimization toolkit (self-contained)
└── test/                # Test files and resources
```

## Testing

### Local Testing

```bash
# Quick syntax validation
./test/nextflow/test_local_simple.sh

# Full workflow test
./test/nextflow/test_local.sh
```

### Cluster Testing

See **[docs/CLUSTER_TESTING_GUIDE.md](docs/CLUSTER_TESTING_GUIDE.md)** for comprehensive cluster testing guide.

## Code Quality

This project uses:
- **Nextflow lint** (25.04+) - Built-in linting and formatting
- **Ruff & Black** - Python code formatting
- **MyPy** - Type checking

```bash
# Lint Nextflow files
nextflow lint .

# Validate syntax
./bin/validate_nextflow.sh
```

See **[docs/SETUP.md](docs/SETUP.md)** for IDE setup and **[docs/NEXTFLOW_LINTING.md](docs/NEXTFLOW_LINTING.md)** for linting details.

## Optimization

Bowtie2 parameter optimization tools are in the **[optimization/](optimization/)** directory. This is a self-contained module that can be used independently or extracted to a separate repository.

See **[optimization/README.md](optimization/README.md)** for details.

## Citation

If you use RNA MAP in your research, please cite:

```
Yesselman, J.D., et al. (2022). RNA mutational profiling (MaP) with DREEM reveals 
structural and functional insights into RNA structure. Nucleic Acids Research, 
50(12), e70. https://doi.org/10.1093/nar/gkac435
```

## License

See [LICENSE](LICENSE) file for details.

## Links

- **Documentation**: [docs/README.md](docs/README.md)
- **Quick Start**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **Setup Guide**: [docs/SETUP.md](docs/SETUP.md)
- **Optimization**: [optimization/README.md](optimization/README.md)
