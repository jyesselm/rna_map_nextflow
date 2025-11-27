# Cluster Testing Guide for Nextflow Workflow

## Prerequisites

### 1. Cluster Access
- SSH access to cluster
- SLURM account and partition access
- Sufficient quota for test runs

### 2. Software on Cluster
- Nextflow installed (or use conda environment)
- Java 8-18 (included in conda environment)
- Access to shared storage (for input/output files)

### 3. Local Setup
- Nextflow workflow tested locally
- Conda environment created and validated
- Test data prepared

## Pre-Cluster Checklist

### ✅ Local Validation Complete
```bash
cd nextflow/
./test_local_conda.sh
# Verify: All processes complete successfully
# Verify: Output files match baseline
```

### ✅ Environment Ready
```bash
# Create conda environment (if not done)
./setup_conda.sh

# Verify Nextflow works
conda activate rna_map_nextflow
nextflow -version
```

### ✅ Test Data Prepared
- Small test dataset ready
- Sample CSV file created
- Input files accessible from cluster

## Cluster Setup

### Step 1: Transfer Files to Cluster

```bash
# From local machine
rsync -avz nextflow/ user@cluster:/path/to/rna_map/nextflow/
rsync -avz test/resources/ user@cluster:/path/to/rna_map/test/resources/
```

### Step 2: Create Conda Environment on Cluster

```bash
# SSH to cluster
ssh user@cluster

# Navigate to project
cd /path/to/rna_map/nextflow/

# Create environment (if conda available)
./setup_conda.sh

# OR use module system (if available)
module load nextflow
module load java/11
```

### Step 3: Configure for Your Cluster

Edit `nextflow.config`:

```groovy
profiles {
    slurm {
        process.executor = 'slurm'
        process.clusterOptions = { 
            def opts = []
            if (params.account) {
                opts << "--account=${params.account}"
            }
            opts << "--partition=${params.partition}"
            opts << "--time=${params.max_time}"
            opts << "--mem=${params.max_memory}"
            return opts.join(' ')
        }
        
        // Module loading (if needed)
        process.beforeScript = '''
            module load bowtie2
            module load fastqc
            module load trim_galore
        '''
    }
}
```

### Step 4: Set Resource Requirements

Update process labels in `main.nf`:

```groovy
process RNA_MAP_MAPPING {
    label 'process_high'  // Uses: cpus=16, memory=32GB, time=4h
    // ...
}

process RNA_MAP_BIT_VECTORS {
    label 'process_high'  // Uses: cpus=4, memory=16GB, time=2h
    // ...
}
```

Configure in `nextflow.config`:

```groovy
process {
    withLabel: 'process_high' {
        cpus = 16
        memory = '32 GB'
        time = '4h'
    }
}
```

## Testing on Cluster

### Test 1: Single Sample (Dry Run)

```bash
# Activate environment
conda activate rna_map_nextflow

# Dry run (validates workflow without executing)
nextflow run main.nf \
    -profile slurm \
    --fasta /path/to/test.fasta \
    --fastq1 /path/to/test_mate1.fastq \
    --fastq2 /path/to/test_mate2.fastq \
    --dot_bracket /path/to/test.csv \
    --output_dir /path/to/results \
    --account your_account \
    --partition normal \
    -with-dag dag.html \
    -with-report report.html \
    -with-trace trace.txt
```

### Test 2: Single Sample (Actual Run)

```bash
# Submit to cluster
nextflow run main.nf \
    -profile slurm \
    --fasta /path/to/test.fasta \
    --fastq1 /path/to/test_mate1.fastq \
    --fastq2 /path/to/test_mate2.fastq \
    --dot_bracket /path/to/test.csv \
    --output_dir /path/to/results \
    --account your_account \
    --partition normal \
    --max_cpus 16
```

### Test 3: Multiple Samples

Create `samples.csv`:

```csv
sample_id,fasta,fastq1,fastq2,dot_bracket
sample1,/path/to/ref1.fasta,/path/to/r1_1.fastq,/path/to/r1_2.fastq,/path/to/struct1.csv
sample2,/path/to/ref2.fasta,/path/to/r2_1.fastq,/path/to/r2_2.fastq,/path/to/struct2.csv
```

Run:

```bash
nextflow run main.nf \
    -profile slurm \
    --samples_csv samples.csv \
    --output_dir /path/to/results \
    --account your_account \
    --partition normal
```

## Monitoring

### Check Job Status

```bash
# Nextflow status
nextflow log

# SLURM jobs
squeue -u $USER

# Nextflow work directory
ls -lh $SCRATCH/nextflow-work/
```

### View Logs

```bash
# Nextflow execution log
cat .nextflow.log

# Process logs
find work -name ".command.err" -exec tail -20 {} \;
find work -name ".command.out" -exec tail -20 {} \;
```

### Check Output

```bash
# Verify results
ls -lh results/*/BitVector_Files/summary.csv
head results/*/BitVector_Files/summary.csv
```

## Troubleshooting

### Issue: Jobs Not Starting

**Check:**
- SLURM account and partition correct
- Resource requirements not too high
- Module loading working
- File paths accessible

**Solution:**
```bash
# Test SLURM access
sbatch --account=your_account --partition=normal --time=1:00:00 --wrap="echo test"

# Check module availability
module avail bowtie2
module load bowtie2
which bowtie2
```

### Issue: File Not Found Errors

**Check:**
- Input files accessible from compute nodes
- Paths are absolute (not relative)
- Files in shared storage (not local disk)

**Solution:**
```bash
# Use absolute paths
--fasta /shared/data/ref.fasta

# Not relative paths
--fasta ./ref.fasta  # ❌ May not work on compute nodes
```

### Issue: Out of Memory

**Solution:**
```groovy
// Increase memory in nextflow.config
process {
    withLabel: 'process_high' {
        memory = '64 GB'  // Increase from 32 GB
    }
}
```

### Issue: Timeout Errors

**Solution:**
```groovy
// Increase time limit
process {
    withLabel: 'process_high' {
        time = '8h'  // Increase from 4h
    }
}
```

### Issue: Too Many Files (5M Limit)

**Check file count:**
```bash
find $SCRATCH/nextflow-work -type f | wc -l
```

**Solution:**
- Use scratch space for work directory
- Clean up old work directories: `nextflow clean -f`
- Archive results regularly
- Use `--resume` to avoid recomputation

## Performance Optimization

### 1. Use Scratch Space

```groovy
// In nextflow.config
workDir = System.getenv('SCRATCH') ? "${System.getenv('SCRATCH')}/nextflow-work" : "${System.getenv('HOME')}/nextflow-work"
```

### 2. Parallel Execution

Nextflow automatically parallelizes independent samples. No configuration needed!

### 3. Resume Failed Runs

```bash
# If workflow fails, resume from last successful step
nextflow run main.nf -resume [previous run name]
```

### 4. Resource Tuning

Adjust based on your cluster's resources:

```groovy
process {
    withLabel: 'process_high' {
        cpus = { Math.min(task.cpus ?: 16, 32) }  // Use up to 32 CPUs
        memory = { task.attempt == 1 ? '32 GB' : '64 GB' }  // Retry with more memory
    }
}
```

## Validation

### Compare Cluster Results to Local

```bash
# On cluster
head results/sample1/BitVector_Files/summary.csv

# On local (if you have same test data)
head test_results/sample_test.fasta/BitVector_Files/summary.csv

# Should match!
```

### Check File Counts

```bash
# Monitor file creation
find results -type f | wc -l
find $SCRATCH/nextflow-work -type f | wc -l

# Should stay well under 5M limit
```

## Production Checklist

Before running production jobs:

- [ ] Tested with small dataset
- [ ] Validated output matches local results
- [ ] Resource requirements tuned
- [ ] File paths verified (absolute paths)
- [ ] Module loading configured
- [ ] Scratch space configured
- [ ] Output directory has sufficient space
- [ ] SLURM account/partition correct
- [ ] Monitoring setup (logs, reports)

## Quick Reference

```bash
# Single sample
nextflow run main.nf -profile slurm --fasta X --fastq1 Y --output_dir Z

# Multiple samples
nextflow run main.nf -profile slurm --samples_csv samples.csv --output_dir results

# Resume failed run
nextflow run main.nf -resume [run_name]

# Clean work directory
nextflow clean -f

# View reports
open report.html
open dag.html
```

## Support

- Nextflow docs: https://www.nextflow.io/docs/latest/
- SLURM docs: Check your cluster's documentation
- Workflow logs: `.nextflow.log`
- Process logs: `work/*/.command.err` and `.command.out`

