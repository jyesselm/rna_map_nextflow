#!/bin/bash
# Build Singularity/Apptainer image from Docker image
#
# This script builds a Singularity/Apptainer image (.sif) from the Docker image.
# The resulting image can be used on HPC clusters that support Singularity/Apptainer.
#
# Usage:
#   ./scripts/build_singularity.sh [output_path]
#
# Example:
#   ./scripts/build_singularity.sh /path/to/rna-map.sif
#
# Requirements:
#   - Singularity or Apptainer installed
#   - Docker image built (or will pull from registry)
#   - Sufficient disk space (~2-3 GB)

set -e

# Default output path
OUTPUT_PATH="${1:-rna-map.sif}"

# Check if Singularity/Apptainer is available
if command -v singularity &> /dev/null; then
    CONTAINER_CMD="singularity"
elif command -v apptainer &> /dev/null; then
    CONTAINER_CMD="apptainer"
else
    echo "ERROR: Neither Singularity nor Apptainer found in PATH"
    echo "Please install Singularity or Apptainer to build container images"
    exit 1
fi

echo "Using: $CONTAINER_CMD"
echo "Building Singularity image: $OUTPUT_PATH"

# Check if Docker image exists locally
if docker images | grep -q "^rna-map"; then
    echo "Found local Docker image 'rna-map', using docker-daemon://"
    IMAGE_SOURCE="docker-daemon://rna-map:latest"
else
    echo "Local Docker image not found. Will build from Dockerfile..."
    echo "Building Docker image first..."
    docker build -t rna-map -f docker/Dockerfile .
    IMAGE_SOURCE="docker-daemon://rna-map:latest"
fi

# Build Singularity image
echo "Converting Docker image to Singularity format..."
$CONTAINER_CMD build --fakeroot "$OUTPUT_PATH" "$IMAGE_SOURCE"

echo "✅ Singularity image built successfully: $OUTPUT_PATH"
echo ""
echo "To use this image with Nextflow:"
echo "  nextflow run main.nf -profile slurm_singularity \\"
echo "      --container_path $OUTPUT_PATH \\"
echo "      --fasta ref.fasta --fastq1 reads.fastq"

