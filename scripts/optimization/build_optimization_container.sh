#!/bin/bash
# Build Apptainer/Singularity container for optimization workflow
#
# This script builds a container image with all dependencies for running
# Bowtie2 parameter optimization, including Optuna and the rna_map package.
#
# Usage:
#   ./scripts/optimization/build_optimization_container.sh [output_path]
#
# Example:
#   ./scripts/optimization/build_optimization_container.sh rna-map-optimization.sif
#   ./scripts/optimization/build_optimization_container.sh /shared/containers/rna-map-optimization.sif

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Default output path
OUTPUT_PATH="${1:-${PROJECT_ROOT}/rna-map-optimization.sif}"

# Check if Apptainer/Singularity is available
if command -v apptainer &> /dev/null; then
    CONTAINER_CMD="apptainer"
elif command -v singularity &> /dev/null; then
    CONTAINER_CMD="singularity"
else
    echo "ERROR: Neither Apptainer nor Singularity found in PATH"
    echo "Please install Apptainer or Singularity to build container images"
    echo ""
    echo "On HPC clusters, Apptainer is usually available as a module:"
    echo "  module load apptainer"
    exit 1
fi

echo "=========================================="
echo "Building Optimization Container"
echo "=========================================="
echo ""
echo "Using: $CONTAINER_CMD"
echo "Output: $OUTPUT_PATH"
echo "Project root: $PROJECT_ROOT"
echo ""

# Check if definition file exists
DEF_FILE="${SCRIPT_DIR}/rna-map-optimization.def"
if [ ! -f "$DEF_FILE" ]; then
    echo "ERROR: Definition file not found: $DEF_FILE"
    exit 1
fi

# Check if environment file exists
ENV_FILE="${PROJECT_ROOT}/environment_optuna.yml"
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file not found: $ENV_FILE"
    exit 1
fi

# Check if src/rna_map exists
RNA_MAP_DIR="${PROJECT_ROOT}/src/rna_map"
if [ ! -d "$RNA_MAP_DIR" ]; then
    echo "ERROR: rna_map package directory not found: $RNA_MAP_DIR"
    exit 1
fi

echo "Building container from definition file..."
echo "This may take 10-20 minutes depending on network speed..."
echo ""

# Build the container
cd "$PROJECT_ROOT"

# Determine build method based on available capabilities
USE_FAKEROOT=false
USE_REMOTE=false
USE_SUDO=false

if $CONTAINER_CMD --version | grep -q "apptainer"; then
    # Apptainer supports --fakeroot and remote builds
    if $CONTAINER_CMD capability list 2>/dev/null | grep -q "fakeroot"; then
        USE_FAKEROOT=true
        echo "✓ Fakeroot capability available - will build without sudo"
    elif command -v apptainer &> /dev/null; then
        # Try remote build (no root required)
        USE_REMOTE=true
        echo "✓ Using remote build (no sudo required)"
    else
        USE_SUDO=true
        echo "⚠️  Fakeroot not available - will try sudo (may fail)"
    fi
else
    # Singularity - older versions need sudo, newer support remote
    if $CONTAINER_CMD remote list 2>/dev/null | grep -q "DefaultRemote"; then
        USE_REMOTE=true
        echo "✓ Using remote build (no sudo required)"
    else
        USE_SUDO=true
        echo "⚠️  Will try sudo (may not work without root)"
    fi
fi

# Attempt build with selected method
BUILD_SUCCESS=false

if [ "$USE_FAKEROOT" = true ]; then
    echo "Building with fakeroot..."
    if $CONTAINER_CMD build --fakeroot "$OUTPUT_PATH" "$DEF_FILE" 2>&1; then
        BUILD_SUCCESS=true
    else
        echo "Fakeroot build failed, trying remote build..."
        USE_REMOTE=true
        USE_FAKEROOT=false
    fi
fi

if [ "$USE_REMOTE" = true ] && [ "$BUILD_SUCCESS" = false ]; then
    echo "Building with remote builder (no sudo required)..."
    echo "This will use Sylabs Cloud or configured remote endpoint"
    
    # Check if remote is configured
    if $CONTAINER_CMD remote list 2>/dev/null | grep -q "DefaultRemote"; then
        echo "Using configured remote endpoint..."
        if $CONTAINER_CMD build --remote "$OUTPUT_PATH" "$DEF_FILE" 2>&1; then
            BUILD_SUCCESS=true
        else
            echo "Remote build failed. You may need to configure a remote:"
            echo "  apptainer remote add --no-login SylabsCloud cloud.sycloud.io"
            echo "  # Or use a different remote endpoint"
        fi
    else
        echo "No remote configured. Setting up Sylabs Cloud (free, no login required)..."
        if $CONTAINER_CMD remote add --no-login SylabsCloud cloud.sycloud.io 2>/dev/null; then
            echo "Remote added. Building..."
            if $CONTAINER_CMD build --remote "$OUTPUT_PATH" "$DEF_FILE" 2>&1; then
                BUILD_SUCCESS=true
            fi
        else
            echo "Failed to configure remote. Trying local build with sudo..."
            USE_SUDO=true
        fi
    fi
fi

if [ "$USE_SUDO" = true ] && [ "$BUILD_SUCCESS" = false ]; then
    echo "Attempting build with sudo (may require password)..."
    if sudo $CONTAINER_CMD build "$OUTPUT_PATH" "$DEF_FILE" 2>&1; then
        BUILD_SUCCESS=true
    else
        echo ""
        echo "❌ All build methods failed!"
        echo ""
        echo "Options for building without sudo:"
        echo "  1. Use fakeroot: apptainer capability add --user $USER fakeroot"
        echo "  2. Use remote build: apptainer remote add SylabsCloud cloud.sycloud.io"
        echo "  3. Build on a system with sudo access, then transfer the .sif file"
        exit 1
    fi
fi

if [ "$BUILD_SUCCESS" = false ]; then
    echo ""
    echo "❌ Container build failed"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Container built successfully!"
    echo "=========================================="
    echo ""
    echo "Container location: $OUTPUT_PATH"
    echo ""
    echo "To test the container:"
    echo "  $CONTAINER_CMD exec $OUTPUT_PATH python -c 'import rna_map; print(\"rna_map installed successfully\")'"
    echo ""
    echo "To use with optimization scripts:"
    echo "  export CONTAINER_PATH=$OUTPUT_PATH"
    echo "  bash scripts/optimization/submit_optimization_jobs.sh"
    echo ""
    echo "Or run directly:"
    echo "  $CONTAINER_CMD exec -B /path/to/data:/data -B /path/to/results:/results \\"
    echo "      $OUTPUT_PATH python scripts/optimization/optimize_bowtie2_params.py"
    echo ""
else
    echo ""
    echo "❌ Container build failed"
    exit 1
fi

