# Container Usage on Cluster

This guide explains how to use Singularity/Apptainer containers with the RNA MAP Nextflow workflow on HPC clusters.

## Why Use Containers?

Containers provide several advantages for cluster execution:

1. **Consistent Environment**: Same environment on all compute nodes
2. **No Package Installation**: All dependencies are pre-installed in the container
3. **Faster Execution**: No need to install packages on each node
4. **Reproducibility**: Same results across different clusters
5. **Easier Setup**: No need to manage conda environments on compute nodes

## Quick Start

### 1. Build the Container Image

First, build a Singularity/Apptainer image from the Docker image:

```bash
# Build Singularity image
./bin/build_singularity.sh /path/to/rna-map.sif

# Or specify a custom location
./bin/build_singularity.sh $HOME/containers/rna-map.sif
```

The script will:
- Check for Singularity or Apptainer
- Build the Docker image if needed
- Convert Docker image to Singularity format (.sif)

### 2. Run with Container

```bash
# Using slurm_singularity profile
nextflow run main.nf \
    -profile slurm_singularity \
    --container_path /path/to/rna-map.sif \
    --fasta ref.fasta \
    --fastq1 reads.fastq \
    --fastq2 reads2.fastq \
    --output_dir results
```

### 3. Using Test Script

```bash
# Set container path (or edit test_cluster_job_singularity.sh)
export CONTAINER_PATH=/path/to/rna-map.sif

# Submit job
sbatch test_cluster_job_singularity.sh
```

## Available Profiles

### `slurm_singularity`

Uses SLURM executor with Singularity/Apptainer containers. Each process runs in a container.

**Best for**: Standard cluster execution with containers

```bash
nextflow run main.nf \
    -profile slurm_singularity \
    --container_path /path/to/rna-map.sif \
    --fasta ref.fasta --fastq1 reads.fastq
```

### `slurm_local_singularity`

Uses local executor within a SLURM job, with all processes running in containers.

**Best for**: Fast tasks (< 5 minutes) where job submission overhead is a concern

```bash
sbatch --time=2:00:00 --mem=32G --cpus-per-task=16 test_cluster_job_local.sh
# Use slurm_local_singularity profile in your job script
```

## Container Image Location

### Option 1: Shared Storage (Recommended)

Store the container on shared storage accessible to all compute nodes:

```bash
# Build to shared location
./bin/build_singularity.sh /shared/containers/rna-map.sif

# Use in workflow
--container_path /shared/containers/rna-map.sif
```

**Benefits**:
- Single copy for all nodes
- Easy to update
- No need to copy to each node

### Option 2: User Home Directory

Store in your home directory:

```bash
# Build to home directory
./bin/build_singularity.sh $HOME/containers/rna-map.sif

# Use in workflow
--container_path $HOME/containers/rna-map.sif
```

### Option 3: Scratch Space

For temporary or test runs:

```bash
# Build to scratch
./bin/build_singularity.sh $SCRATCH/rna-map.sif

# Use in workflow
--container_path $SCRATCH/rna-map.sif
```

## Building the Container

### Prerequisites

- Singularity or Apptainer installed
- Docker (for building the base image)
- Sufficient disk space (~2-3 GB)

### Build Process

The `scripts/build_singularity.sh` script handles the build process:

```bash
# Basic usage
./bin/build_singularity.sh rna-map.sif

# Custom location
./bin/build_singularity.sh /path/to/containers/rna-map.sif
```

**What it does**:
1. Checks for Singularity/Apptainer
2. Builds Docker image if not present
3. Converts Docker image to Singularity format
4. Creates .sif file ready for use

### Manual Build

If you prefer to build manually:

```bash
# 1. Build Docker image
docker build -t rna-map -f containers/Dockerfile .

# 2. Convert to Singularity
singularity build rna-map.sif docker-daemon://rna-map:latest

# Or with Apptainer
apptainer build rna-map.sif docker-daemon://rna-map:latest
```

## Configuration

### Setting Container Path

You can set the container path in several ways:

#### 1. Command Line

```bash
nextflow run main.nf -profile slurm_singularity \
    --container_path /path/to/rna-map.sif ...
```

#### 2. Config File

Create `conf/my_singularity.config`:

```groovy
params {
    container_path = "/path/to/rna-map.sif"
}
```

Then use:
```bash
nextflow run main.nf -profile slurm_singularity -c conf/my_singularity.config ...
```

#### 3. Environment Variable

```bash
export CONTAINER_PATH=/path/to/rna-map.sif
# Use in test script or Nextflow command
```

## Performance Considerations

### Container Caching

Singularity/Apptainer caches container layers, so:
- First run: May be slower (cache population)
- Subsequent runs: Faster (uses cached layers)

### Storage Location

- **Shared storage**: Best for multi-node jobs (single copy)
- **Local storage**: Faster access but needs copying to each node
- **Scratch space**: Fast but temporary

### Overhead

Container overhead is minimal:
- **Startup**: ~1-2 seconds per process
- **Runtime**: Negligible (< 1% overhead)
- **Benefits**: Outweigh overhead (no package installation, consistent environment)

## Troubleshooting

### Issue: "Container not found"

**Solution**:
```bash
# Check container path
ls -lh /path/to/rna-map.sif

# Verify path in Nextflow command
--container_path /absolute/path/to/rna-map.sif
```

### Issue: "Permission denied" on container

**Solution**:
```bash
# Make sure container is readable
chmod 644 rna-map.sif

# Check filesystem permissions
ls -l /path/to/rna-map.sif
```

### Issue: "Singularity/Apptainer not found"

**Solution**:
```bash
# Check if available
which singularity
which apptainer

# Load module if needed
module load singularity
# or
module load apptainer
```

### Issue: Container build fails

**Solution**:
```bash
# Check Docker is running
docker ps

# Check disk space
df -h

# Try building Docker image first
docker build -t rna-map -f containers/Dockerfile .
```

## Comparison: Containers vs. Native

| Aspect | Containers | Native (Conda) |
|--------|-----------|----------------|
| Setup | Build once | Install on each node |
| Consistency | High | Variable |
| Performance | Minimal overhead | No overhead |
| Reproducibility | Excellent | Good |
| Portability | Excellent | Limited |
| Storage | ~2-3 GB image | Variable |

## Best Practices

1. **Use Shared Storage**: Store container on shared filesystem accessible to all nodes
2. **Version Control**: Tag containers with version numbers
3. **Test First**: Test container on login node before submitting jobs
4. **Monitor Resources**: Containers use similar resources to native execution
5. **Update Regularly**: Rebuild containers when dependencies change

## Example Job Script

```bash
#!/bin/bash
#SBATCH --job-name=rna_map
#SBATCH --time=4:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --mem=32G

# Activate conda (for Nextflow only)
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

cd ${SLURM_SUBMIT_DIR}

# Set container path
CONTAINER_PATH="/shared/containers/rna-map.sif"

# Run with container
nextflow run main.nf \
    -profile slurm_singularity \
    --container_path "$CONTAINER_PATH" \
    --fasta ref.fasta \
    --fastq1 reads1.fastq \
    --fastq2 reads2.fastq \
    --output_dir results
```

## Additional Resources

- [Singularity Documentation](https://docs.sylabs.io/)
- [Apptainer Documentation](https://apptainer.org/docs/)
- [Nextflow Container Support](https://www.nextflow.io/docs/latest/container.html)

