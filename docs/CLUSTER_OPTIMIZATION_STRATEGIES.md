# Cluster Optimization Strategies

This guide covers advanced strategies to speed up Nextflow workflows and reduce unnecessary job usage on SLURM clusters.

## Table of Contents

1. [Process Caching](#process-caching)
2. [Resume Functionality](#resume-functionality)
3. [Resource Right-Sizing](#resource-right-sizing)
4. [Work Directory Optimization](#work-directory-optimization)
5. [Process Consolidation](#process-consolidation)
6. [Parallel Processing](#parallel-processing)
7. [Local Executor for Fast Tasks](#local-executor-for-fast-tasks)
8. [Container Caching](#container-caching)
9. [Input/Output Optimization](#inputoutput-optimization)
10. [Monitoring and Profiling](#monitoring-and-profiling)

---

## 1. Process Caching

### What It Does

Nextflow caches completed processes based on input files and parameters. If you rerun a workflow, completed processes are skipped.

### Benefits

- **Zero job submissions** for cached processes
- **Instant results** for cached steps
- **Automatic** - no configuration needed

### How It Works

```bash
# First run - all processes execute
nextflow run main.nf -profile slurm --fasta ref.fasta --fastq1 reads.fastq

# Second run - cached processes skipped (no jobs submitted!)
nextflow run main.nf -profile slurm --fasta ref.fasta --fastq1 reads.fastq
```

### Cache Location

By default, Nextflow stores cache in the `work/` directory. You can optimize this:

```groovy
// In nextflow.config
workDir = System.getenv('SCRATCH') ? "${System.getenv('SCRATCH')}/nextflow-work" : "${System.getenv('HOME')}/nextflow-work"
```

**Benefits of using scratch space**:
- Faster I/O (scratch is typically faster storage)
- Doesn't fill up home directory
- Often has better performance

### Cache Invalidation

Cache is invalidated when:
- Input files change
- Process parameters change
- Process code changes

### Best Practices

1. **Use scratch space for work directory**:
   ```groovy
   workDir = "${System.getenv('SCRATCH')}/nextflow-work"
   ```

2. **Keep cache between runs** - don't delete `work/` directory unnecessarily

3. **Use `-resume` flag** explicitly:
   ```bash
   nextflow run main.nf -profile slurm -resume ...
   ```

---

## 2. Resume Functionality

### What It Does

The `-resume` flag tells Nextflow to skip completed processes and continue from where it left off.

### When to Use

- **Workflow interrupted**: Job killed, cluster maintenance, etc.
- **Adding new samples**: Only new samples processed
- **Parameter tuning**: Only affected processes rerun

### Example

```bash
# Workflow fails partway through
nextflow run main.nf -profile slurm --fasta ref.fasta --fastq1 reads.fastq

# Resume from last checkpoint (no duplicate jobs!)
nextflow run main.nf -profile slurm --fasta ref.fasta --fastq1 reads.fastq -resume
```

### Benefits

- **No duplicate work**: Completed processes not rerun
- **Faster recovery**: Continue from failure point
- **Resource savings**: Only necessary jobs submitted

### Best Practices

1. **Always use `-resume`** for production runs:
   ```bash
   nextflow run main.nf -profile slurm -resume ...
   ```

2. **Checkpoint frequently**: Nextflow automatically creates checkpoints

3. **Monitor progress**: Use `-with-trace` to see what's running

---

## 3. Resource Right-Sizing

### The Problem

Requesting too many resources wastes cluster capacity and can delay job scheduling. Requesting too few causes failures.

### Strategy: Match Resources to Task Needs

```groovy
// In conf/slurm.config or custom config
process {
    // FastQC: Low resources needed
    withName: 'FASTQC' {
        cpus = 2
        memory = '4 GB'
        time = '1h'
    }
    
    // Bowtie2: Medium resources
    withName: 'BOWTIE2_ALIGN' {
        cpus = 8
        memory = '16 GB'
        time = '4h'
    }
    
    // Bit vectors: High resources
    withName: 'RNA_MAP_BIT_VECTORS' {
        cpus = 16
        memory = '32 GB'
        time = '24h'
    }
}
```

### Benefits

- **Faster scheduling**: Smaller jobs schedule faster
- **Better utilization**: Resources match actual needs
- **Fewer failures**: Adequate resources prevent OOM/timeout

### How to Determine Resource Needs

1. **Run test workflow** with `-with-trace`:
   ```bash
   nextflow run main.nf -profile slurm -with-trace trace.txt ...
   ```

2. **Check resource usage**:
   ```bash
   grep -E "process|memory|%mem" trace.txt | head -20
   ```

3. **Adjust based on actual usage**:
   - If memory usage is 50% of requested → reduce memory
   - If jobs timeout → increase time limit
   - If jobs wait long → reduce CPU/memory requests

### Best Practices

1. **Start conservative**: Request more than needed initially
2. **Profile and optimize**: Reduce based on actual usage
3. **Use process labels**: Group similar tasks
4. **Monitor over time**: Resource needs may change

---

## 4. Work Directory Optimization

### The Problem

Work directories on shared filesystems can be slow, causing I/O bottlenecks.

### Strategy: Use Scratch Space

```groovy
// In nextflow.config
workDir = System.getenv('SCRATCH') ? "${System.getenv('SCRATCH')}/nextflow-work" : "${System.getenv('HOME')}/nextflow-work"
```

### Benefits

- **Faster I/O**: Scratch space is typically faster
- **Less network traffic**: Local to compute nodes
- **Better for large files**: Scratch handles large I/O better

### Alternative: Use Local Storage

For very fast workflows, use local node storage:

```groovy
workDir = "/tmp/nextflow-work-${System.getenv('SLURM_JOB_ID')}"
```

**Warning**: Local storage is temporary - ensure results are published!

### Best Practices

1. **Use scratch space** when available
2. **Clean up old work directories** periodically:
   ```bash
   # Remove work directories older than 30 days
   find $SCRATCH/nextflow-work -type d -mtime +30 -exec rm -rf {} +
   ```
3. **Monitor disk usage**: Scratch space may have quotas

---

## 5. Process Consolidation

### The Problem

Multiple small processes create many job submissions, each with overhead.

### Strategy: Combine Related Steps

Instead of:
```
Step 1 → Step 2 → Step 3 (3 jobs)
```

Do:
```
Combined Step (1 job)
```

### Example: Combine QC Steps

```groovy
// Instead of separate FastQC and Trim Galore processes
process COMBINED_QC {
    input:
    path fastq
    
    output:
    path "trimmed.fastq"
    
    script:
    """
    fastqc ${fastq}
    trim_galore --quality 20 ${fastq}
    """
}
```

### Benefits

- **Fewer job submissions**: 1 job instead of 2
- **Less overhead**: Single submission overhead
- **Faster execution**: No intermediate file I/O

### Trade-offs

- **Less flexibility**: Harder to rerun individual steps
- **More complex**: Combined processes harder to debug
- **Resource allocation**: Need resources for all steps

### Best Practices

1. **Combine only related steps**: Don't combine unrelated processes
2. **Keep steps separate if they fail often**: Easier to debug
3. **Consider workflow structure**: Some steps must be separate

---

## 6. Parallel Processing

### The Problem

Large files processed sequentially take a long time.

### Strategy: Split and Process in Parallel

Your workflow already supports this with `--split_fastq`:

```bash
nextflow run main.nf \
    -profile slurm \
    --split_fastq \
    --chunk_size 1000000 \
    --fasta ref.fasta \
    --fastq1 reads.fastq
```

### How It Works

```
Large FASTQ (100M reads)
    ↓
Split into chunks (10 chunks × 10M reads)
    ↓
Process chunks in parallel (10 jobs)
    ↓
Merge results
```

### Benefits

- **Faster processing**: Parallel execution
- **Better resource utilization**: Multiple nodes
- **Scalable**: Add more chunks for larger files

### Optimization Tips

1. **Tune chunk size**: Balance between overhead and parallelism
   - Too small: High overhead, many jobs
   - Too large: Limited parallelism, long jobs

2. **Match chunk size to resources**:
   ```bash
   # For 16 CPUs, use chunks that take ~15-30 min
   --chunk_size 2000000  # 2M reads per chunk
   ```

3. **Monitor chunk processing time**:
   ```bash
   # Check trace to see chunk processing times
   grep "SPLIT" trace.txt
   ```

---

## 7. Local Executor for Fast Tasks

### The Problem

Very fast tasks (< 1 minute) have overhead exceeding runtime when submitted to SLURM.

### Strategy: Use Local Executor

Use `slurm_local` profile for workflows with many fast tasks:

```bash
sbatch --time=2:00:00 --mem=32G --cpus-per-task=16 test_cluster_job_local.sh
```

### How It Works

```
Submit ONE SLURM job
    ↓
All tasks run locally within that job
    ↓
No additional SLURM submissions
```

### Benefits

- **Zero submission overhead**: Single job submission
- **Fast task switching**: No queue wait
- **Better for many small tasks**: Ideal for QC steps

### When to Use

- **Many fast tasks** (< 5 minutes each)
- **Total workflow time** < SLURM job time limit
- **Single node sufficient**: Don't need multiple nodes

### Best Practices

1. **Use for QC-heavy workflows**: FastQC, file operations
2. **Monitor resource usage**: Ensure single job has enough resources
3. **Fallback to SLURM**: For tasks that exceed job limits

---

## 8. Container Caching

### The Problem

Container images must be loaded for each job, adding overhead.

### Strategy: Use Container Cache

Singularity/Apptainer caches container layers automatically.

### How to Optimize

1. **Pre-pull container** to shared location:
   ```bash
   # Pull once to shared storage
   singularity pull /shared/containers/rna-map.sif docker://rna-map:latest
   ```

2. **Use shared container path**:
   ```bash
   --container_path /shared/containers/rna-map.sif
   ```

3. **Enable Singularity cache**:
   ```bash
   export SINGULARITY_CACHEDIR=/shared/singularity-cache
   ```

### Benefits

- **Faster container loading**: Cached layers load faster
- **Reduced network traffic**: Don't pull from registry each time
- **Better reliability**: Local copy more reliable

### Best Practices

1. **Store containers on shared storage**: Accessible to all nodes
2. **Version containers**: Tag with version numbers
3. **Update periodically**: Rebuild when dependencies change

---

## 9. Input/Output Optimization

### The Problem

Excessive file I/O slows down workflows and wastes resources.

### Strategies

#### A. Minimize Intermediate Files

```groovy
// Instead of saving intermediate files
process STEP {
    output:
    path "intermediate.txt"  // Don't publish this
    
    // Only publish final results
    publishDir "${params.output_dir}", pattern: "final_results.*"
}
```

#### B. Use Compression

```groovy
// Compress large intermediate files
process COMPRESS {
    output:
    path "data.gz"  // Compressed output
}
```

#### C. Stream Processing

For very large files, process in streams rather than loading entirely:

```groovy
process STREAM_PROCESS {
    script:
    """
    # Process file in chunks, don't load entire file
    cat ${input} | process_stream.py > ${output}
    """
}
```

#### D. Clean Up Work Directory

```groovy
// In nextflow.config
process {
    cleanup = true  // Remove intermediate files after success
}
```

### Benefits

- **Faster I/O**: Less data to read/write
- **Less storage**: Reduced disk usage
- **Faster transfers**: Smaller files transfer faster

---

## 10. Monitoring and Profiling

### The Problem

You can't optimize what you don't measure.

### Strategy: Profile Your Workflow

#### A. Use Nextflow Trace

```bash
nextflow run main.nf -profile slurm -with-trace trace.txt ...
```

Analyze trace:
```bash
# Find slowest processes
sort -k11 -n trace.txt | tail -20

# Find processes with most overhead
grep -E "submit|start" trace.txt | awk '{print $11-$10}'

# Find resource usage
grep -E "memory|%mem" trace.txt
```

#### B. Use Nextflow Reports

```bash
nextflow run main.nf -profile slurm -with-report report.html ...
```

Check:
- Process execution times
- Resource usage
- Bottlenecks

#### C. Monitor SLURM Queue

```bash
# Watch job submissions
watch -n 5 'squeue -u $USER | wc -l'

# Check job wait times
squeue -u $USER -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"
```

### Use Profiling to Optimize

1. **Identify bottlenecks**: Which processes take longest?
2. **Find overhead**: How much time in submission vs execution?
3. **Resource usage**: Are you requesting too much/little?
4. **Optimize iteratively**: Make changes, measure, repeat

---

## Summary: Optimization Checklist

### Quick Wins (High Impact, Low Effort)

- [ ] Use `-resume` flag for all runs
- [ ] Set work directory to scratch space
- [ ] Use `slurm_local` for fast task workflows
- [ ] Enable process cleanup
- [ ] Right-size resources based on profiling

### Medium Effort (High Impact)

- [ ] Optimize queueSize based on task duration
- [ ] Use parallel processing (`--split_fastq`)
- [ ] Consolidate related processes
- [ ] Use container caching
- [ ] Profile and optimize resource requests

### Advanced (Medium Impact, Higher Effort)

- [ ] Implement custom process consolidation
- [ ] Optimize I/O patterns
- [ ] Use streaming for large files
- [ ] Implement custom caching strategies
- [ ] Fine-tune based on cluster characteristics

---

## Example: Optimized Workflow

```bash
# Optimized command with all strategies
nextflow run main.nf \
    -profile slurm_optimized \
    -resume \
    --container_path /shared/containers/rna-map.sif \
    --split_fastq \
    --chunk_size 2000000 \
    --fasta ref.fasta \
    --fastq1 reads.fastq \
    --output_dir results \
    -with-trace trace.txt \
    -with-report report.html

# With work directory on scratch (set in nextflow.config)
# With optimized queueSize (set in profile)
# With right-sized resources (set in profile)
```

This single command uses:
- ✅ Process caching (`-resume`)
- ✅ Container optimization (shared container)
- ✅ Parallel processing (`--split_fastq`)
- ✅ Queue batching (via profile)
- ✅ Resource optimization (via profile)
- ✅ Monitoring (`-with-trace`, `-with-report`)

---

## Additional Resources

- [Nextflow Best Practices](https://www.nextflow.io/docs/latest/best-practices.html)
- [SLURM Optimization Guide](https://slurm.schedmd.com/optimization.html)
- [Container Performance](https://docs.sylabs.io/guides/latest/user-guide/performance.html)

