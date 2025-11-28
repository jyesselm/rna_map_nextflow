# Cluster Testing Guide - RNA MAP Nextflow

This guide provides comprehensive instructions for testing the RNA MAP Nextflow workflow on a cluster environment (SLURM).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Testing Levels](#testing-levels)
4. [Step-by-Step Testing](#step-by-step-testing)
5. [Verifying Results](#verifying-results)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Testing](#advanced-testing)

## Prerequisites

### Required Software

- **Conda/Mamba** - For environment management (or use containers)
- **Java 8-18** - Required by Nextflow
- **Nextflow 23.0+** - Workflow engine
- **Bioinformatics tools** (if not using containers):
  - Bowtie2 2.2.9+
  - FastQC 0.11.9+
  - Trim Galore 0.6.6+
  - Cutadapt 1.18+

### Optional: Container Support

- **Singularity/Apptainer** - For containerized execution (recommended)
  - Provides consistent environment
  - Eliminates need for package installation on compute nodes
  - See [CONTAINER_USAGE.md](CONTAINER_USAGE.md) for details

### Cluster Requirements

- SLURM job scheduler
- Access to compute nodes
- Sufficient storage for test data and results
- Network access (if using shared storage)

## Initial Setup

### 1. Clone Repository

```bash
# On login node or compute node with git access
cd /path/to/your/workspace
git clone https://github.com/jyesselm/rna_map_nextflow
cd rna_map_nextflow
```

### 2. Create Conda Environment

```bash
# Create environment from environment.yml
conda env create -f environment.yml

# Activate environment
conda activate rna-map-nextflow

# Verify installation
which nextflow
which java
which bowtie2
which fastqc
which trim_galore
```

### 3. Install Python Package

**CRITICAL**: You must install the Python package for the workflow to work!

```bash
# Install the package in editable mode (ensures lib/ is available)
pip install -e .

# Verify installation
python -c "from lib.bit_vectors import generate_bit_vectors; print('✅ lib imports work')"
python -c "from lib.core.config import BitVectorConfig; print('✅ lib.core imports work')"
```

**Note**: The package is automatically installed by Nextflow processes via `beforeScript`, but installing it manually ensures it's available for testing and debugging.

### 4. Verify Test Data

```bash
# Check test data exists
ls -lh test/resources/case_1/

# Should see:
# - test.fasta
# - test_mate1.fastq
# - test_mate2.fastq
# - test.csv
```

## Testing Levels

We recommend testing in this order:

1. **Level 1: Syntax Validation** - Quick check that workflow files are valid
2. **Level 2: Dry Run** - Test workflow without executing
3. **Level 3: Single Sample Test** - Run one sample with minimal resources
4. **Level 4: Full Test** - Complete workflow with all steps
5. **Level 5: Parallel Test** - Test FASTQ splitting and parallel processing

### Using Containers (Recommended)

If your cluster supports Singularity/Apptainer, we recommend using containers:

```bash
# Build container (one time)
./scripts/build_singularity.sh /path/to/rna-map.sif

# Run with container
nextflow run main.nf \
    -profile slurm_singularity \
    --container_path /path/to/rna-map.sif \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --output_dir test_results_container
```

See [CONTAINER_USAGE.md](CONTAINER_USAGE.md) for detailed container usage guide.

## Step-by-Step Testing

### Level 1: Syntax Validation

**Purpose**: Verify Nextflow can parse all workflow files

```bash
# Activate environment
conda activate rna-map-nextflow
pip install -e .

# Run syntax validation script
chmod +x test/nextflow/test_local_simple.sh
./test/nextflow/test_local_simple.sh
```

**Expected Output**:
```
==========================================
Validating Nextflow Workflow Syntax
==========================================

Checking workflow files...
✅ Workflow files found

Checking test data...
✅ test.fasta
✅ test_mate1.fastq
✅ test_mate2.fastq
✅ test.csv

==========================================
Workflow files are valid!
==========================================
```

**If this fails**: Check that all files are in the correct locations and Nextflow is installed.

### Level 2: Dry Run

**Purpose**: Test workflow configuration without executing

```bash
# Test with --help to see parameters
nextflow run main.nf --help

# Dry run (validates configuration)
nextflow run main.nf \
    -profile slurm \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_dry \
    -with-dag test_dag_dry.html \
    -resume
```

**Expected Output**: Nextflow should show the workflow DAG and exit without errors.

### Level 3: Single Sample Test (Minimal)

**Purpose**: Run one sample with minimal resources to verify basic functionality

```bash
# Create test script
cat > test_cluster_minimal.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=rna_map_test
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --partition=normal
#SBATCH --output=test_%j.out
#SBATCH --error=test_%j.err

# Load modules if needed (customize for your cluster)
# module load conda
# module load java

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Change to submission directory
cd ${SLURM_SUBMIT_DIR}

# Install Python package (ensures lib/ is available without PYTHONPATH)
pip install -e . --quiet

# Run Nextflow
nextflow run main.nf \
    -profile slurm \
    --account $(groups | cut -d' ' -f1) \
    --partition normal \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_minimal \
    --skip_fastqc \
    --skip_trim_galore \
    --max_cpus 4 \
    -with-report test_report_minimal.html \
    -with-trace test_trace_minimal.txt \
    -with-dag test_dag_minimal.html

echo "Test completed. Check test_results_minimal/ for outputs."
EOF

chmod +x test_cluster_minimal.sh

# Submit job
sbatch test_cluster_minimal.sh

# Monitor job
squeue -u $USER

# Check output when job completes
cat test_*.out
```

**Expected Output**:
- Job completes successfully
- `test_results_minimal/` directory created
- Output files present in results directory

### Level 4: Full Test

**Purpose**: Run complete workflow with all steps (FastQC, Trim Galore, alignment, bit vectors)

```bash
# Create full test script
cat > test_cluster_full.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=rna_map_full
#SBATCH --time=4:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=32G
#SBATCH --partition=normal
#SBATCH --output=test_full_%j.out
#SBATCH --error=test_full_%j.err

# Load modules if needed
# module load conda
# module load java

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Change to submission directory
cd ${SLURM_SUBMIT_DIR}

# Install Python package (ensures lib/ is available without PYTHONPATH)
pip install -e . --quiet

# Run Nextflow with all steps
nextflow run main.nf \
    -profile slurm \
    --account $(groups | cut -d' ' -f1) \
    --partition normal \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_full \
    --max_cpus 8 \
    -with-report test_report_full.html \
    -with-trace test_trace_full.txt \
    -with-dag test_dag_full.html

echo "Full test completed. Check test_results_full/ for outputs."
EOF

chmod +x test_cluster_full.sh
sbatch test_cluster_full.sh
```

### Level 5: Parallel Processing Test

**Purpose**: Test FASTQ splitting and parallel processing

```bash
# Use the provided parallel test script
chmod +x test/nextflow/test_parallel.sh

# Modify for cluster use
cat > test_cluster_parallel.sh << 'EOF'
#!/bin/bash
#SBATCH --job-name=rna_map_parallel
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=64G
#SBATCH --partition=normal
#SBATCH --output=test_parallel_%j.out
#SBATCH --error=test_parallel_%j.err

source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow
cd ${SLURM_SUBMIT_DIR}
pip install -e . --quiet

nextflow run main.nf \
    -profile slurm \
    --account $(groups | cut -d' ' -f1) \
    --partition normal \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_parallel \
    --split_fastq \
    --chunk_size 1000 \
    --max_cpus 16 \
    -with-report test_report_parallel.html \
    -with-trace test_trace_parallel.txt \
    -with-dag test_dag_parallel.html
EOF

chmod +x test_cluster_parallel.sh
sbatch test_cluster_parallel.sh
```

## Verifying Results

### 1. Check Job Status

```bash
# Check if job completed
squeue -u $USER

# Check job exit status
sacct -j <JOB_ID> --format=JobID,JobName,State,ExitCode

# View job output
cat test_*.out
cat test_*.err
```

### 2. Verify Output Structure

```bash
# Check output directory structure
tree test_results_full/ -L 3

# Should see:
# test_results_full/
# └── <sample_id>/
#     ├── BitVector_Files/
#     │   ├── summary.csv
#     │   ├── mutation_histos.p
#     │   ├── mutation_histos.json
#     │   └── <sequence>_bitvectors.txt
#     └── Mapping_Files/
#         └── aligned.sam
```

### 3. Check Key Output Files

```bash
RESULTS_DIR="test_results_full/<sample_id>"

# Check summary CSV exists and has data
head -5 ${RESULTS_DIR}/BitVector_Files/summary.csv

# Check mutation histograms exist
ls -lh ${RESULTS_DIR}/BitVector_Files/mutation_histos.*

# Check SAM file exists and has alignments
head -20 ${RESULTS_DIR}/Mapping_Files/aligned.sam

# Check bit vector files
ls -lh ${RESULTS_DIR}/BitVector_Files/*_bitvectors.txt
```

### 4. Verify Nextflow Reports

```bash
# Open HTML reports (download to local machine if needed)
# - test_report_full.html - Execution report
# - test_dag_full.html - Workflow DAG visualization
# - test_trace_full.txt - Detailed execution trace

# Check trace file
head -20 test_trace_full.txt
```

### 5. Validate Python Output

```bash
# Test that Python can read the output
python << 'PYTHON'
import pickle
import json
from pathlib import Path

results_dir = Path("test_results_full/<sample_id>/BitVector_Files")

# Check pickle file
with open(results_dir / "mutation_histos.p", "rb") as f:
    histos = pickle.load(f)
    print(f"✅ Pickle file loaded: {len(histos)} sequences")

# Check JSON file
with open(results_dir / "mutation_histos.json", "r") as f:
    histos_json = json.load(f)
    print(f"✅ JSON file loaded: {len(histos_json)} sequences")

# Check summary CSV
import pandas as pd
df = pd.read_csv(results_dir / "summary.csv")
print(f"✅ Summary CSV loaded: {len(df)} rows")
print(df.head())
PYTHON
```

## Troubleshooting

### Issue: "Module not found: lib"

**Solution**:
```bash
# Install the Python package
pip install -e .

# Verify installation
python -c "from lib.bit_vectors import generate_bit_vectors; print('OK')"

# If still failing, check that you're in the project root directory
pwd
# Should be: /path/to/rna_map_nextflow
```

### Issue: "Java version error"

**Solution**:
```bash
# Check Java version
java -version

# Should be Java 8-18
# If not, install in conda environment:
conda install openjdk=11 -c conda-forge
```

### Issue: "Nextflow not found"

**Solution**:
```bash
# Check if Nextflow is in environment
which nextflow

# If not, install:
conda install nextflow -c bioconda

# Or verify environment is activated
conda activate rna-map-nextflow
```

### Issue: "Tool not found" (bowtie2, fastqc, etc.)

**Solution**:
```bash
# Check if tools are in environment
which bowtie2
which fastqc
which trim_galore

# If not, install:
conda install -c bioconda bowtie2 fastqc trim-galore cutadapt
```

### Issue: "SLURM account/partition error"

**Solution**:
```bash
# Check your account
sacctmgr show user $USER

# Check available partitions
sinfo

# Update job script with correct account/partition
# --account your_account
# --partition your_partition
```

### Issue: "Permission denied" on scripts

**Solution**:
```bash
# Make scripts executable
chmod +x test/nextflow/*.sh
chmod +x lint.sh fmt.sh
```

### Issue: "Workflow fails with Python error"

**Solution**:
```bash
# Check Nextflow logs
cat .nextflow.log

# Check process logs in work directory
ls -la work/*/

# Verify package is installed in conda environment
# The package should be automatically installed via beforeScript in configs
# If issues persist, manually install: pip install -e .
```

### Issue: "Out of memory" or "Time limit exceeded"

**Solution**:
```bash
# Increase resources in job script:
#SBATCH --mem=64G
#SBATCH --time=8:00:00
#SBATCH --ntasks-per-node=16

# Or adjust Nextflow params:
--max_cpus 16
--max_memory "64 GB"
```

## Advanced Testing

### Test Multiple Samples

```bash
# Create samples CSV
cat > test_samples.csv << 'EOF'
sample_id,fasta,fastq1,fastq2,dot_bracket
test1,test/resources/case_1/test.fasta,test/resources/case_1/test_mate1.fastq,test/resources/case_1/test_mate2.fastq,test/resources/case_1/test.csv
test2,test/resources/case_1/test.fasta,test/resources/case_1/test_mate1.fastq,test/resources/case_1/test_mate2.fastq,test/resources/case_1/test.csv
EOF

# Run with samples CSV
nextflow run main.nf \
    -profile slurm \
    --samples_csv test_samples.csv \
    --output_dir test_results_multi \
    --max_cpus 16
```

### Test with Custom Configuration

```bash
# Create custom config
cat > my_config.config << 'EOF'
params {
    max_cpus = 32
    max_memory = "128 GB"
    bt2_alignment_args = "--very-sensitive-local;--no-unal"
}
EOF

# Run with custom config
nextflow run main.nf \
    -c my_config.config \
    -profile slurm \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --output_dir test_results_custom
```

### Test Resume Functionality

```bash
# Run workflow
nextflow run main.nf -profile slurm --fasta ... --output_dir results

# If it fails, resume from checkpoint
nextflow run main.nf -profile slurm --fasta ... --output_dir results -resume
```

## Testing Checklist

Use this checklist to verify your installation:

- [ ] Repository cloned successfully
- [ ] Conda environment created and activated
- [ ] All tools installed (nextflow, java, bowtie2, fastqc, trim_galore)
- [ ] Python package installed (`pip install -e .`)
- [ ] Python imports work (`from lib.bit_vectors import ...`)
- [ ] Syntax validation passes (`test_local_simple.sh`)
- [ ] Dry run completes without errors
- [ ] Minimal test job completes successfully
- [ ] Output files created in results directory
- [ ] Summary CSV has data
- [ ] Mutation histograms generated
- [ ] SAM file contains alignments
- [ ] Nextflow reports generated
- [ ] Full test completes successfully
- [ ] Parallel test completes successfully

## Getting Help

If you encounter issues:

1. **Check logs**: `cat test_*.out` and `cat test_*.err`
2. **Check Nextflow logs**: `cat .nextflow.log`
3. **Check process logs**: `ls -la work/*/`
4. **Verify environment**: Run `conda list` to see installed packages
5. **Test imports**: Run Python import tests manually
6. **Check SLURM**: Verify account, partition, and resource limits

## Next Steps

Once testing is complete:

1. **Production Setup**: Configure for your production data
2. **Resource Tuning**: Adjust CPU/memory based on your data size
3. **Storage**: Set up appropriate storage for results
4. **Monitoring**: Set up job monitoring and notifications
5. **Documentation**: Document cluster-specific configurations

---

**Last Updated**: 2025-11-27
**Version**: 1.0.0
