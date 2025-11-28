# Queue Optimization Guide for Cluster Execution

This guide explains how Nextflow's queue system works and how to optimize it for faster cluster execution.

## The Problem: Job Submission Overhead

When running workflows on SLURM clusters, each Nextflow process becomes a separate SLURM job. This creates overhead:

### Without Queue Batching

```
Task 1 → Submit to SLURM → Wait in queue → Run (30 seconds)
Task 2 → Submit to SLURM → Wait in queue → Run (30 seconds)
Task 3 → Submit to SLURM → Wait in queue → Run (30 seconds)
...
Task 100 → Submit to SLURM → Wait in queue → Run (30 seconds)

Total: 100 submissions × (5 sec overhead + 30 sec runtime) = ~58 minutes
```

**Problems**:
- Each job submission takes 2-10 seconds (scheduler overhead)
- Queue wait time for each job
- Scheduler load from many small jobs
- For fast tasks (< 5 min), overhead can exceed runtime!

### With Queue Batching

```
Tasks 1-10 → Batch together → Submit once → Run in parallel
Tasks 11-20 → Batch together → Submit once → Run in parallel
...

Total: 10 batches × (5 sec overhead + 30 sec runtime) = ~6 minutes
```

**Benefits**:
- Fewer job submissions (10x reduction)
- Less scheduler overhead
- Faster overall execution
- Better resource utilization

## How QueueSize Works

The `queueSize` parameter controls how many tasks Nextflow batches together before submitting to SLURM.

### Example: queueSize = 10

```groovy
process {
    queueSize = 10  // Batch 10 tasks before submitting
}
```

**What happens**:
1. Nextflow collects up to 10 tasks
2. When queue reaches 10 tasks, submits them all at once
3. SLURM schedules them (often in parallel if resources available)
4. Nextflow collects next batch of 10 tasks
5. Repeat until all tasks complete

### Visual Example

```
Time →
Without batching (queueSize = 1):
Task1 [submit][wait][run] Task2 [submit][wait][run] Task3 [submit][wait][run]
     ↑overhead↑              ↑overhead↑              ↑overhead↑

With batching (queueSize = 10):
Tasks1-10 [submit once][wait][run in parallel]
Tasks11-20 [submit once][wait][run in parallel]
     ↑one overhead↑              ↑one overhead↑
```

## Choosing the Right QueueSize

### Fast Tasks (< 5 minutes)

**Recommended**: `queueSize = 20-50`

```groovy
withLabel: 'process_low' {
    queueSize = 20  // Batch many fast tasks
}
```

**Why**: Fast tasks have high overhead-to-runtime ratio. Batching many together maximizes efficiency.

**Example**:
- Task runtime: 1 minute
- Submission overhead: 5 seconds
- Without batching: 100 tasks × 65 seconds = 108 minutes
- With batching (20): 5 batches × 65 seconds = 5.4 minutes
- **Speedup: 20x faster!**

### Medium Tasks (5-30 minutes)

**Recommended**: `queueSize = 10-20`

```groovy
withLabel: 'process_medium' {
    queueSize = 10  // Moderate batching
}
```

**Why**: Overhead is smaller relative to runtime, but batching still helps.

**Example**:
- Task runtime: 15 minutes
- Submission overhead: 5 seconds
- Without batching: 100 tasks × 15.08 minutes = 25.1 hours
- With batching (10): 10 batches × 15.08 minutes = 2.5 hours
- **Speedup: 10x faster!**

### Slow Tasks (> 30 minutes)

**Recommended**: `queueSize = 1-5`

```groovy
withLabel: 'process_high' {
    queueSize = 5  // Less batching for slower tasks
}
```

**Why**: Overhead is negligible compared to runtime. Don't delay long tasks waiting for batch to fill.

**Example**:
- Task runtime: 2 hours
- Submission overhead: 5 seconds
- Without batching: 10 tasks × 2 hours = 20 hours
- With batching (5): 2 batches × 2 hours = 4 hours
- **Speedup: 5x faster, but also starts earlier!**

### Very Slow Tasks (> 2 hours)

**Recommended**: `queueSize = 1`

```groovy
withLabel: 'process_slow' {
    queueSize = 1  // Submit immediately - no batching
}
```

**Why**: These tasks should start immediately. Don't wait for batch to fill.

## Real-World Example: RNA MAP Workflow

### Typical Workflow Tasks

```groovy
// Fast tasks: FastQC, file operations
FASTQC {
    label 'process_low'      // queueSize = 20
    // Runtime: 1-2 minutes
}

// Medium tasks: Trim Galore, Bowtie2 alignment
TRIM_GALORE {
    label 'process_medium'  // queueSize = 10
    // Runtime: 5-15 minutes
}

BOWTIE2_ALIGN {
    label 'process_medium'  // queueSize = 10
    // Runtime: 10-30 minutes
}

// Slow tasks: Bit vector generation
RNA_MAP_BIT_VECTORS {
    label 'process_high'    // queueSize = 5
    // Runtime: 30 minutes - 2 hours
}
```

### Performance Impact

**Scenario**: Processing 10 samples with parallel FASTQ splitting (40 chunks total)

**Without optimization** (queueSize = 1):
- 40 FastQC tasks: 40 submissions × 5 sec = 200 sec overhead
- 40 Trim Galore tasks: 40 submissions × 5 sec = 200 sec overhead
- 40 Bowtie2 tasks: 40 submissions × 5 sec = 200 sec overhead
- 10 Bit vector tasks: 10 submissions × 5 sec = 50 sec overhead
- **Total overhead: 650 seconds (~11 minutes)**

**With optimization** (queueSize = 20 for fast, 10 for medium, 5 for slow):
- 40 FastQC tasks: 2 batches × 5 sec = 10 sec overhead
- 40 Trim Galore tasks: 4 batches × 5 sec = 20 sec overhead
- 40 Bowtie2 tasks: 4 batches × 5 sec = 20 sec overhead
- 10 Bit vector tasks: 2 batches × 5 sec = 10 sec overhead
- **Total overhead: 60 seconds (1 minute)**
- **Speedup: 10.8x faster!**

## Configuration Examples

### Profile: slurm_optimized

```groovy
process {
    queueSize = 10  // Default for all processes
    
    withLabel: 'process_low' {
        queueSize = 20  // Fast tasks: batch more
    }
    
    withLabel: 'process_medium' {
        queueSize = 10  // Medium tasks: moderate batching
    }
    
    withLabel: 'process_high' {
        queueSize = 5   // Slow tasks: less batching
    }
    
    withLabel: 'process_slow' {
        queueSize = 1  // Very slow: submit immediately
    }
}
```

### Custom Configuration

Create `conf/my_workflow.config`:

```groovy
process {
    // Global setting
    queueSize = 15
    
    // Override for specific process
    withName: 'RNA_MAP_BIT_VECTORS' {
        queueSize = 1  // This is slow, submit immediately
    }
    
    // Override for label
    withLabel: 'process_low' {
        queueSize = 50  // Very fast tasks, batch many
    }
}
```

Use it:
```bash
nextflow run main.nf -profile slurm -c conf/my_workflow.config ...
```

## Advanced: Dynamic Queue Sizing

### Based on Task Count

For workflows with varying numbers of tasks:

```groovy
process {
    // Small workflow: batch less
    queueSize = params.task_count < 50 ? 5 : 20
}
```

### Based on Resource Availability

```groovy
process {
    // If cluster has many nodes, batch more
    queueSize = params.max_cpus > 32 ? 20 : 10
}
```

## Monitoring Queue Performance

### Check Nextflow Trace

```bash
# Run with trace
nextflow run main.nf -profile slurm -with-trace trace.txt ...

# Check submission times
grep "submit" trace.txt | head -20
```

Look for:
- **Many submissions close together**: Good batching
- **Submissions spread out**: May need higher queueSize
- **Long gaps between submissions**: Batch may be too large

### Check SLURM Queue

```bash
# Monitor job submissions
watch -n 5 'squeue -u $USER | wc -l'

# Check job start times
squeue -u $USER -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
```

## Common Issues and Solutions

### Issue: "Tasks completing instantly but workflow is slow"

**Problem**: Overhead exceeds runtime

**Solution**: Use `slurm_local` profile or increase queueSize

```bash
# Option 1: Use local executor (no SLURM overhead)
nextflow run main.nf -profile slurm_local ...

# Option 2: Increase queueSize
# In config: queueSize = 50
```

### Issue: "Long tasks waiting for batch to fill"

**Problem**: queueSize too high for slow tasks

**Solution**: Use process labels or lower queueSize for slow tasks

```groovy
withLabel: 'process_slow' {
    queueSize = 1  // Submit immediately
}
```

### Issue: "Too many pending jobs" error

**Problem**: Cluster limits concurrent jobs

**Solution**: Increase queueSize to batch more tasks

```groovy
process {
    queueSize = 50  // Batch more, fewer submissions
    maxForks = 10   // Limit concurrent jobs
}
```

## Best Practices

1. **Use Process Labels**: Assign labels based on task duration
   ```groovy
   process MY_FAST_PROCESS {
       label 'process_low'  // Automatically uses queueSize = 20
   }
   ```

2. **Profile Your Workflow**: Measure actual overhead vs runtime
   ```bash
   nextflow run main.nf -with-trace trace.txt ...
   # Analyze trace.txt to see submission overhead
   ```

3. **Start Conservative**: Begin with default queueSize, then optimize
   - Default: `queueSize = 10`
   - Fast tasks: Increase to 20-50
   - Slow tasks: Decrease to 1-5

4. **Monitor Cluster Load**: Check if batching helps or hurts
   ```bash
   # If cluster is busy, batching may help
   # If cluster is idle, lower queueSize may be better
   ```

5. **Use slurm_local for Very Fast Tasks**: If tasks are < 1 minute, consider local executor
   ```bash
   nextflow run main.nf -profile slurm_local ...
   ```

## Summary

| Task Duration | Recommended queueSize | Why |
|--------------|----------------------|-----|
| < 5 minutes | 20-50 | High overhead-to-runtime ratio |
| 5-30 minutes | 10-20 | Moderate overhead |
| 30 min - 2 hours | 5-10 | Low overhead, but batching still helps |
| > 2 hours | 1-5 | Overhead negligible, start quickly |

**Key Takeaway**: The queue system batches tasks to reduce SLURM job submission overhead. For fast tasks, this can provide 10-20x speedup. For slow tasks, it still helps but less dramatically.

