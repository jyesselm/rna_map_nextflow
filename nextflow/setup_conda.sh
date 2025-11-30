#!/bin/bash
# Setup conda environment for RNA MAP Nextflow workflow

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Setting up Conda Environment for Nextflow"
echo "=========================================="
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null && ! command -v mamba &> /dev/null; then
    echo "ERROR: Conda or Mamba not found"
    echo "Please install Miniconda or Mambaforge:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Use mamba if available (faster), otherwise conda
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
    echo "Using mamba (faster)"
else
    CONDA_CMD="conda"
    echo "Using conda"
fi

echo ""
echo "Creating conda environment: rna_map_nextflow"
echo "This will install:"
echo "  - Python 3.10+"
echo "  - Java 11 (for Nextflow)"
echo "  - Nextflow"
echo "  - Bowtie2, FastQC, Trim Galore, Cutadapt"
echo ""

# Create environment
cd "$SCRIPT_DIR"
$CONDA_CMD env create -f environment.yml

echo ""
echo "Installing rna_map package in editable mode..."
echo ""

# Activate environment and install rna_map from src/rna_map
cd "$PROJECT_ROOT/src/rna_map"
$CONDA_CMD run -n rna_map_nextflow python -m pip install -e .

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Setup complete!"
    echo "=========================================="
    echo ""
    echo "To use:"
    echo "  conda activate rna_map_nextflow"
    echo "  cd $SCRIPT_DIR"
    echo "  ./test_local.sh"
    echo ""
else
    echo ""
    echo "⚠️  rna_map installation had issues"
    echo "You can install it manually:"
    echo "  conda activate rna_map_nextflow"
    echo "  cd $PROJECT_ROOT/src/rna_map"
    echo "  python -m pip install -e ."
    echo ""
fi

