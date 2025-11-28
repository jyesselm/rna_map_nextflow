# Quick Executor Guide

## The Problem

- **Fast tasks** (< 5 min): Job submission overhead can be longer than task runtime
- **Slow tasks** (> 1 hour): Want immediate submission, not waiting in batches

## Solution: Choose the Right Profile

### Fast Tasks (Most tasks < 5 minutes)

```bash
# Use slurm_local - all tasks run in one SLURM job
sbatch --time=2:00:00 --mem=32G --cpus-per-task=16 test_cluster_job_local.sh
```

**Profile**: `slurm_local`  
**What it does**: Submits ONE SLURM job, all tasks run locally within it

---

### Slow Tasks (Tasks take hours)

```bash
# Use slurm_optimized with low queue size
nextflow run main.nf -profile slurm_optimized \
    --fasta ref.fasta --fastq1 reads.fastq \
    --max_cpus 16
```

**Profile**: `slurm_optimized`  
**What it does**: Uses SLURM with optimized batching (queueSize=5-10)

---

### Customize for Mixed Workloads

#### Option 1: Set queueSize per process via labels

Add label to your process:
```groovy
process MY_SLOW_PROCESS {
    label 'process_slow'  // This will use queueSize=1
    // ... rest of process
}
```

#### Option 2: Create custom config file

Create `conf/my_workflow.config`:
```groovy
process {
    withName: 'RNA_MAP_BIT_VECTORS' {
        queueSize = 1  // Submit immediately - no batching
        time = '48h'   // Long time limit
    }
    
    withLabel: 'process_low' {
        queueSize = 50  // Batch many fast tasks
    }
}
```

Use it:
```bash
nextflow run main.nf -profile slurm -c conf/my_workflow.config ...
```

#### Option 3: Override via command line

```bash
# Set global queue size
nextflow run main.nf -profile slurm \
    --fasta ref.fasta \
    -process.queueSize=1  # Submit immediately
```

---

## Quick Reference Table

| Scenario | Profile | queueSize | Notes |
|----------|---------|-----------|-------|
| All fast tasks | `slurm_local` | N/A | Single job |
| All slow tasks | `slurm_optimized` | 1-5 | Immediate submission |
| Mixed workload | `slurm_optimized` + custom labels | 1-50 | Per-task config |
| Very slow tasks | `slurm` + custom config | 1 | No batching |

---

## Process Labels

| Label | Default queueSize | Use Case |
|-------|-------------------|----------|
| `process_low` | 20 | Fast tasks (< 5 min) |
| `process_medium` | 10 | Medium tasks (5-30 min) |
| `process_high` | 5 | Slow tasks (30 min - 2h) |
| `process_slow` | 1 | Very slow tasks (> 2h) |

---

## Common Use Cases

### Case 1: Bit vector generation takes hours

```groovy
// In conf/custom.config
process {
    withName: 'RNA_MAP_BIT_VECTORS' {
        queueSize = 1      // Submit immediately
        time = '48h'       // Long time limit
        memory = '64 GB'   // More memory
    }
}
```

### Case 2: Many fast QC tasks

```groovy
// In conf/custom.config
process {
    withLabel: 'process_low' {
        queueSize = 50  // Batch 50 tasks together
    }
}
```

### Case 3: Everything is slow

```bash
# Just use slurm_optimized with low queueSize globally
nextflow run main.nf -profile slurm_optimized \
    -process.queueSize=1 \
    --fasta ref.fasta
```

---

## Need More Details?

See `docs/EXECUTOR_OPTIMIZATION.md` for comprehensive documentation.

