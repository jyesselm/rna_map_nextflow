# Resource Optimization Guide

This guide explains how right-sizing resources (CPU and memory) can dramatically speed up job scheduling and reduce cluster waste.

## The Problem: Over-Requesting Resources

When you request more resources than you need:
- **Slower scheduling**: Jobs wait longer for available resources
- **Waste**: Resources sit idle while other jobs wait
- **Lower throughput**: Fewer jobs can run simultaneously

### Example: The Impact

**Scenario**: 100 tasks, each needs 1 CPU and 2 GB

**Over-requesting** (requesting 4 CPUs, 8 GB each):
- Cluster has 100 CPUs available
- Can only run 25 jobs simultaneously (100 CPUs ÷ 4 CPUs/job)
- Other 75 CPUs sit idle
- **Result**: 4x slower than necessary

**Right-sized** (requesting 1 CPU, 2 GB each):
- Cluster has 100 CPUs available
- Can run 100 jobs simultaneously
- All CPUs utilized
- **Result**: 4x faster!

## Your Current Configuration

Based on your workflow analysis, most tasks only need:
- **1 CPU**
- **2 GB memory**

All config files have been updated to reflect this:

```groovy
// Default for all processes
cpus = { task.cpus ?: 1 }
memory = { task.memory ?: '2 GB' }

// Fast/medium tasks
withLabel: 'process_low' {
    cpus = 1
    memory = '2 GB'
}

withLabel: 'process_medium' {
    cpus = 1
    memory = '2 GB'
}

// High tasks (e.g., bit vector generation) may need more
withLabel: 'process_high' {
    cpus = { params.max_cpus ?: 4 }
    memory = { params.max_memory ?: '8 GB' }
}
```

## Benefits of Right-Sizing

### 1. Faster Job Scheduling

**Before** (requesting 4 CPUs, 8 GB):
```
Job 1: Waiting for 4 CPUs... (queue time: 5 min)
Job 2: Waiting for 4 CPUs... (queue time: 5 min)
Job 3: Waiting for 4 CPUs... (queue time: 5 min)
```

**After** (requesting 1 CPU, 2 GB):
```
Job 1: Scheduled immediately (queue time: 30 sec)
Job 2: Scheduled immediately (queue time: 30 sec)
Job 3: Scheduled immediately (queue time: 30 sec)
```

**Result**: 10x faster scheduling!

### 2. Better Cluster Utilization

**Before**: 25 jobs running, 75 CPUs idle
**After**: 100 jobs running, 0 CPUs idle

**Result**: 4x better utilization!

### 3. Higher Throughput

With right-sized resources, you can:
- Run more jobs simultaneously
- Process more samples in parallel
- Complete workflows faster

## How to Verify Resource Needs

### Method 1: Profile Your Workflow

```bash
# Run with trace
nextflow run main.nf -profile slurm -with-trace trace.txt ...

# Check actual CPU usage
grep "%cpu" trace.txt | awk '{sum+=$NF; count++} END {print "Avg CPU:", sum/count}'

# Check actual memory usage
grep "%mem" trace.txt | awk '{sum+=$NF; count++} END {print "Avg Memory:", sum/count}'
```

### Method 2: Check SLURM Job Stats

```bash
# After job completes, check resource usage
sacct -j <JOB_ID> --format=JobID,JobName,MaxRSS,MaxVMSize,TotalCPU,ReqCPUS,ReqMem

# Compare requested vs actual
# If MaxRSS << ReqMem, you're over-requesting!
```

### Method 3: Monitor During Execution

```bash
# Watch resource usage in real-time
watch -n 5 'squeue -u $USER -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"'
```

## Customizing for Specific Processes

If some processes need more resources, override them:

### Example: Bit Vector Generation Needs More

```groovy
// In conf/custom.config or process definition
process {
    // Most tasks: 1 CPU, 2 GB
    cpus = { task.cpus ?: 1 }
    memory = { task.memory ?: '2 GB' }
    
    // Bit vector generation: needs more
    withName: 'RNA_MAP_BIT_VECTORS' {
        cpus = 4
        memory = '8 GB'
    }
}
```

### Example: Bowtie2 Alignment Needs More CPUs

```groovy
withName: 'BOWTIE2_ALIGN' {
    cpus = 8  // Bowtie2 can use multiple threads
    memory = '4 GB'
}
```

## Best Practices

### 1. Start Conservative, Then Optimize

```groovy
// Start with slightly more than needed
cpus = { task.cpus ?: 1 }
memory = { task.memory ?: '2 GB' }

// Profile and reduce if possible
// Better to have a little extra than to fail
```

### 2. Use Process Labels

Group similar tasks with labels:

```groovy
process FASTQC {
    label 'process_low'  // Automatically gets 1 CPU, 2 GB
    // ...
}
```

### 3. Monitor and Adjust

Regularly check:
- Actual vs requested resources
- Job wait times
- Cluster utilization

Adjust based on findings.

### 4. Document Resource Needs

Keep notes on which processes need more:
- FastQC: 1 CPU, 2 GB ✓
- Trim Galore: 1 CPU, 2 GB ✓
- Bowtie2: 8 CPUs, 4 GB (uses threading)
- Bit vectors: 4 CPUs, 8 GB (memory intensive)

## Expected Performance Improvements

With right-sized resources (1 CPU, 2 GB for most tasks):

| Metric | Before (4 CPU, 8 GB) | After (1 CPU, 2 GB) | Improvement |
|--------|---------------------|---------------------|-------------|
| Jobs per 100 CPUs | 25 | 100 | 4x |
| Queue wait time | 5-10 min | 30 sec - 2 min | 3-5x faster |
| Cluster utilization | 25% | 100% | 4x |
| Workflow completion | 4 hours | 1 hour | 4x faster |

## Troubleshooting

### Issue: Jobs failing with "Out of memory"

**Solution**: Increase memory for that specific process:

```groovy
withName: 'PROBLEM_PROCESS' {
    memory = '4 GB'  // Increase from 2 GB
}
```

### Issue: Jobs taking too long

**Solution**: Check if process can use more CPUs:

```groovy
withName: 'SLOW_PROCESS' {
    cpus = 4  // Increase from 1 if tool supports threading
}
```

### Issue: Jobs waiting too long in queue

**Solution**: Check if you're over-requesting:

```bash
# Check queue status
squeue -u $USER

# If many jobs pending, reduce resource requests
```

## Summary

**Key Takeaway**: Right-sizing resources from 4 CPU/8 GB to 1 CPU/2 GB for most tasks can provide:
- **4x faster scheduling**
- **4x better cluster utilization**
- **4x higher throughput**

Your configuration has been updated to use 1 CPU and 2 GB as defaults, with higher resources only for processes that actually need them (via `process_high` label).

