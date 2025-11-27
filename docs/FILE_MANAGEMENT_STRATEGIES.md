# File Management Strategies for Cluster File Limits

## Quick Reference

If your cluster has a **5 million file limit**, here are strategies to minimize file creation.

## File Count Estimation

### Per Sample File Count

**Current Pipeline:**
- Mapping_Files: ~5-10 files (SAM, FastQC, trimmed FASTQ)
- BitVector_Files: ~5-10 files (bitvectors, histograms, plots, CSVs)
- Log: 1 file
- **Total: ~10-20 files per sample**

**With Nextflow/Snakemake (default):**
- Additional work directories: ~5-10 files per process
- **Total: ~25-35 files per sample**

**With Cleanup Enabled:**
- Only final outputs kept
- **Total: ~10-15 files per sample**

### Scale Estimation

| Samples | Current | Nextflow (default) | Nextflow (cleanup) |
|---------|---------|-------------------|-------------------|
| 1,000 | ~15,000 | ~30,000 | ~12,000 |
| 10,000 | ~150,000 | ~300,000 | ~120,000 |
| 100,000 | ~1,500,000 | ~3,000,000 | ~1,200,000 |

**All are well under 5M limit**, but cleanup is recommended for long-term use.

## Strategy 1: Aggressive Cleanup (Recommended)

### Nextflow Configuration

```nextflow
// nextflow.config
process {
    // Delete work directories after successful completion
    cleanup = true
    
    // Only publish final outputs
    publishDir = [
        path: 'results',
        mode: 'copy',
        pattern: '*.csv,*.html,*.json',  // Only keep these file types
        saveAs: { it.name }  // Flatten structure
    ]
}

// Use scratch space (often has separate/higher limits)
workDir = '/scratch/$USER/nextflow-work'

// Clean up old runs
cleanup = true
```

**Benefits:**
- Reduces file count by 50-70%
- Automatic cleanup
- No code changes needed

### Snakemake Configuration

```python
# Snakefile
# Only define final outputs in rule all
rule all:
    input:
        expand("results/{sample}/summary.csv", sample=SAMPLES)

# Clean up intermediate files in each rule
rule bit_vector_gen:
    input:
        sam="results/{sample}/aligned.sam"
    output:
        summary="results/{sample}/summary.csv"
    shell:
        """
        # Generate intermediate files
        python generate.py {input.sam} > temp.txt
        
        # Process to final output
        python process.py temp.txt > {output.summary}
        
        # Clean up immediately
        rm temp.txt
        """
```

**Benefits:**
- Full control over what's kept
- Can clean up per-rule
- Explicit and clear

## Strategy 2: Archive Outputs

Store multiple outputs in single archive files.

### Nextflow Example

```nextflow
process ARCHIVE_RESULTS {
    input:
    path summary
    path bitvectors
    path plots
    
    output:
    path "*.tar.gz"
    
    script:
    """
    tar -czf ${sample_id}.tar.gz summary.csv bitvectors.txt plots.html
    """
}
```

### Snakemake Example

```python
rule archive_results:
    input:
        summary="results/{sample}/summary.csv",
        bitvectors="results/{sample}/bitvectors.txt",
        plots="results/{sample}/plots.html"
    output:
        archive="results/{sample}.tar.gz"
    shell:
        "tar -czf {output.archive} -C results {wildcards.sample}"
```

**Benefits:**
- Reduces 10 files → 1 file per sample
- 90% file count reduction
- Easy to extract when needed

## Strategy 3: Database/Storage Format

Use single-file storage formats (HDF5, SQLite, Parquet).

### HDF5 Example

```python
import h5py
import pandas as pd

# Store all results in one HDF5 file
with h5py.File(f'results/{sample}.h5', 'w') as f:
    # Store bit vectors
    f.create_dataset('bitvectors', data=bitvectors_array)
    
    # Store summary as structured array
    summary_df.to_hdf(f'results/{sample}.h5', 'summary', mode='a')
    
    # Store metadata
    f.attrs['sample_id'] = sample_id
    f.attrs['timestamp'] = timestamp
```

**Benefits:**
- 1 file per sample (minimal file count)
- Efficient storage and access
- Can store complex data structures

**Drawbacks:**
- More complex code
- Requires HDF5 library
- Less human-readable

### SQLite Example

```python
import sqlite3

# Store all results in SQLite database
conn = sqlite3.connect(f'results/{sample}.db')
summary_df.to_sql('summary', conn, if_exists='replace')
bitvectors_df.to_sql('bitvectors', conn, if_exists='replace')
conn.close()
```

**Benefits:**
- 1 file per sample
- SQL queries for analysis
- Standard format

## Strategy 4: Batch/Combine Outputs

Combine outputs from multiple samples into single files.

### Combine Summaries

```python
# Combine all sample summaries into one file
rule combine_summaries:
    input:
        expand("results/{sample}/summary.csv", sample=SAMPLES)
    output:
        "results/all_summaries.csv"
    run:
        import pandas as pd
        dfs = [pd.read_csv(f) for f in input]
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv(output[0], index=False)
        
        # Optionally clean up individual files
        for f in input:
            f.unlink()  # Delete individual summaries
```

**Benefits:**
- Reduces N files → 1 file
- Easier to analyze all samples
- Can still keep individual files if needed

## Strategy 5: Use Scratch Space

Many clusters have separate scratch space with different limits.

### Nextflow

```nextflow
// Use scratch space for work directories
workDir = '/scratch/$USER/nextflow-work'

// Keep final results in home directory
publishDir = '/home/$USER/results'
```

### Snakemake

```python
# Use scratch for temporary files
config['scratch_dir'] = '/scratch/$USER/snakemake-work'

# Keep final results in home
config['results_dir'] = '/home/$USER/results'
```

**Benefits:**
- Scratch often has separate/higher limits
- Home directory stays clean
- Automatic cleanup on scratch

## Strategy 6: Monitor File Count

Add monitoring to track file usage.

### Nextflow

```nextflow
// Add to nextflow.config
process {
    afterScript = '''
        # Count files in output directory
        FILE_COUNT=$(find results -type f | wc -l)
        echo "Total files: $FILE_COUNT"
        
        # Alert if approaching limit
        if [ $FILE_COUNT -gt 4000000 ]; then
            echo "WARNING: Approaching file limit!"
        fi
    '''
}
```

### Snakemake

```python
# Add to Snakefile
def count_files():
    import subprocess
    result = subprocess.run(['find', 'results', '-type', 'f'], 
                          capture_output=True, text=True)
    count = len(result.stdout.strip().split('\n'))
    print(f"Total files: {count}")
    if count > 4000000:
        print("WARNING: Approaching file limit!")
    return count

# Call at end of workflow
rule monitor:
    input:
        expand("results/{sample}/summary.csv", sample=SAMPLES)
    run:
        count_files()
```

## Recommended Approach

**For 5M file limit with typical usage (<10k samples):**

1. ✅ **Use Nextflow/Snakemake with cleanup enabled**
   - Automatic cleanup of intermediate files
   - Only keep final outputs
   - Minimal configuration needed

2. ✅ **Use scratch space for work directories**
   - Separate quota
   - Automatic cleanup
   - Keeps home directory clean

3. ✅ **Monitor file count**
   - Add alerts when approaching limit
   - Track file usage over time
   - Clean up old results periodically

4. ⚠️ **Consider archive approach if processing >50k samples**
   - Archive per-sample outputs
   - Extract when needed
   - Significant file count reduction

5. ⚠️ **Database format only if file count becomes critical**
   - More complex
   - Requires code changes
   - Only if other strategies insufficient

## Quick Checklist

- [ ] Enable cleanup in workflow manager config
- [ ] Use scratch space for work directories
- [ ] Only publish final outputs (not intermediates)
- [ ] Monitor file count regularly
- [ ] Clean up old pipeline runs periodically
- [ ] Consider archiving if processing >50k samples
- [ ] Document file management strategy for team

## Example: Complete Nextflow Config with File Management

```nextflow
// nextflow.config
process {
    // Cleanup intermediate files
    cleanup = true
    
    // Use scratch space
    workDir = '/scratch/$USER/nextflow-work'
    
    // Only publish final outputs
    publishDir = [
        [
            path: 'results',
            mode: 'copy',
            pattern: '*.csv,*.html,*.json',  // Only these file types
            saveAs: { it.name }  // Flatten structure
        ]
    ]
    
    // Monitor file count
    afterScript = '''
        FILE_COUNT=$(find results -type f 2>/dev/null | wc -l)
        echo "Files in results: $FILE_COUNT"
        if [ $FILE_COUNT -gt 4000000 ]; then
            echo "WARNING: Approaching 5M file limit!"
        fi
    '''
}

// Global cleanup
cleanup = true
```

## Example: Complete Snakemake Config with File Management

```python
# Snakefile
configfile: "config.yaml"

# Use scratch space
import os
SCRATCH_DIR = os.environ.get('SCRATCH', '/scratch/$USER')
WORK_DIR = f'{SCRATCH_DIR}/snakemake-work'

# Only final outputs
rule all:
    input:
        expand("results/{sample}/summary.csv", sample=config["samples"])

# Clean up in each rule
rule bit_vector_gen:
    input:
        sam="results/{sample}/aligned.sam"
    output:
        summary="results/{sample}/summary.csv"
    shell:
        """
        # Generate (creates temp files)
        python generate.py {input.sam} > temp.txt
        
        # Process to final output
        python process.py temp.txt > {output.summary}
        
        # Clean up immediately
        rm -f temp.txt
        """

# Monitor at end
rule monitor:
    input:
        expand("results/{sample}/summary.csv", sample=config["samples"])
    run:
        import subprocess
        result = subprocess.run(['find', 'results', '-type', 'f'], 
                              capture_output=True, text=True)
        count = len([x for x in result.stdout.strip().split('\n') if x])
        print(f"Total files: {count}")
        if count > 4000000:
            print("WARNING: Approaching 5M file limit!")
```

## Summary

**File limits are NOT a blocker** for using workflow managers. With proper configuration:

- ✅ Cleanup reduces file count by 50-70%
- ✅ Scratch space provides separate quota
- ✅ Archive approach reduces by 90% if needed
- ✅ All strategies keep you well under 5M limit

**Recommendation**: Use Nextflow/Snakemake with cleanup enabled. This is sufficient for typical usage and requires minimal configuration.

