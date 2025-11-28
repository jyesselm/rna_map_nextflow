# Nextflow Executor Optimization Guide

This guide explains how to optimize Nextflow job submission for different task workloads.

## Problem: Job Submission Overhead

When tasks are very fast (< 1 minute), the overhead of submitting individual SLURM jobs can exceed the task runtime. When tasks are slow (> 1 hour), you want to maximize resource utilization and reuse workers.

## Available Profiles

### 1. `slurm_local` - Fast Tasks (Default for Fast Workflows)

**Best for**: Workflows with mostly fast tasks (< 5 minutes)

**How it works**: Submits one SLURM job that runs all tasks locally within that job.

**Pros**:
- Minimal overhead - all tasks run in a single job
- Fast task switching
- Good for workflows with many short tasks

**Cons**:
- Limited to resources of single SLURM job
- Not suitable for very long tasks (> job time limit)

**Usage**:
```bash
sbatch --time=2:00:00 --mem=32G --cpus-per-task=16 test_cluster_job_local.sh
```

**Configuration**: `conf/slurm_local.config`

---

### 2. `slurm_optimized` - Slow Tasks with Batching

**Best for**: Workflows with slow tasks that can be batched

**How it works**: Uses SLURM executor with queue batching to reduce submission overhead.

**Pros**:
- Can handle long-running tasks
- Queues multiple tasks to reduce submission overhead
- Scalable to multiple nodes

**Cons**:
- Still has per-task submission overhead
- May wait for queue if batch isn't full

**Usage**:
```bash
nextflow run main.nf -profile slurm_optimized \
    --fasta ref.fasta \
    --fastq1 reads.fastq \
    --max_cpus 16
```

**Configuration**: `conf/slurm_optimized.config`

**Customization**: Adjust `queueSize` parameter:
- `queueSize = 1`: Submit immediately (no batching)
- `queueSize = 5-10`: Moderate batching (default)
- `queueSize = 20-50`: Heavy batching for many fast tasks

---

### 3. `slurm_hybrid` - Mixed Fast and Slow Tasks

**Best for**: Workflows with both fast and slow tasks

**How it works**: Uses local executor for fast tasks, SLURM for slow tasks (based on process labels).

**Pros**:
- Optimized for both task types
- Flexible resource allocation

**Cons**:
- Requires proper process labeling
- More complex configuration

**Usage**:
```bash
sbatch --time=4:00:00 --mem=32G --cpus-per-task=16 test_cluster_job.sh
# Use slurm_hybrid profile in your job script
```

**Configuration**: `conf/slurm_hybrid.config`

---

### 4. `slurm` - Standard SLURM (Default)

**Best for**: Standard workflows with moderate task durations

**How it works**: Standard SLURM executor with individual job submission.

**Usage**:
```bash
nextflow run main.nf -profile slurm \
    --fasta ref.fasta \
    --fastq1 reads.fastq
```

**Configuration**: `conf/slurm.config`

---

## Customizing Task Execution

### Method 1: Process Labels

Add labels to processes to control executor behavior:

```groovy
process MY_PROCESS {
    label 'process_low'    // Fast task - uses local executor in hybrid mode
    label 'process_high'   // Slow task - uses SLURM executor
    label 'process_slow'   // Very slow task - no batching, immediate submission
    
    // ... rest of process
}
```

**Available Labels**:
- `process_low`: Fast tasks (< 5 min) - use local executor
- `process_medium`: Medium tasks (5-30 min) - use local or SLURM with batching
- `process_high`: Slow tasks (> 30 min) - use SLURM with moderate batching
- `process_slow`: Very slow tasks (> 2 hours) - use SLURM with no batching

### Method 2: Custom Queue Size

Override `queueSize` in your config file:

```groovy
process {
    withLabel: 'my_custom_label' {
        queueSize = 1      // No batching
        executor = 'slurm'
        cpus = 16
        memory = '32 GB'
        time = '24h'
    }
}
```

### Method 3: Per-Process Configuration

Create a custom config file (`conf/custom.config`):

```groovy
process {
    // Specific process configuration
    withName: 'RNA_MAP_BIT_VECTORS' {
        queueSize = 1
        executor = 'slurm'
        cpus = 16
        memory = '32 GB'
        time = '48h'
    }
    
    // Or use labels
    withLabel: 'process_slow' {
        queueSize = 1
        executor = 'slurm'
    }
}
```

Then use it:
```bash
nextflow run main.nf -profile slurm -c conf/custom.config ...
```

---

## Parameter Reference

### `queueSize`
- **Purpose**: Number of tasks to queue before submitting to SLURM
- **Range**: 1 (immediate) to 100+ (heavy batching)
- **Recommendation**: 
  - Fast tasks: 20-50
  - Slow tasks: 1-5

### `maxForks`
- **Purpose**: Maximum concurrent tasks/processes
- **Default**: Based on `params.max_cpus`
- **Recommendation**: Set to number of CPUs available

### `pollInterval`
- **Purpose**: How often Nextflow checks for new tasks
- **Default**: 5-10 seconds
- **Recommendation**: Lower (1-5s) for fast tasks, higher (10-30s) for slow tasks

---

## Examples

### Example 1: Many Fast Tasks

```bash
# Use slurm_local profile
sbatch --time=2:00:00 --mem=16G --cpus-per-task=8 test_cluster_job_local.sh
```

### Example 2: Few Slow Tasks

```bash
# Use slurm_optimized with low queueSize
nextflow run main.nf -profile slurm_optimized \
    -c conf/custom_slow.config \
    --fasta ref.fasta --fastq1 reads.fastq
```

Where `conf/custom_slow.config`:
```groovy
process {
    queueSize = 1  // Submit immediately
    withLabel: 'process_high' {
        time = '24h'
        memory = '64 GB'
    }
}
```

### Example 3: Mixed Workload

```bash
# Use slurm_hybrid profile
# Fast tasks (process_low) run locally
# Slow tasks (process_high) run on SLURM
sbatch --time=4:00:00 --mem=32G --cpus-per-task=16 test_cluster_job.sh
```

---

## Choosing the Right Profile

| Scenario | Recommended Profile | queueSize | Notes |
|----------|---------------------|-----------|-------|
| All tasks < 5 min | `slurm_local` | N/A | Single SLURM job |
| All tasks > 30 min | `slurm_optimized` | 1-5 | Individual jobs |
| Mixed workloads | `slurm_hybrid` | Auto | Based on labels |
| Many fast, few slow | `slurm_local` + custom | N/A | Override slow tasks |
| Few fast, many slow | `slurm_optimized` | 10-20 | Batch slow tasks |

---

## Troubleshooting

### "Too many pending jobs" error
- **Solution**: Increase `queueSize` to batch more tasks together

### Tasks completing instantly but workflow is slow
- **Solution**: Use `slurm_local` profile instead

### Out of memory errors
- **Solution**: Increase memory in SLURM job or process labels
- Check `conf/slurm_local.config` memory settings match your job allocation

### Tasks timing out
- **Solution**: Increase `time` parameter in process labels or custom config

