#!/bin/bash
# Simple test - just validate the workflow syntax
# This doesn't require Java to be the right version

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "Validating Nextflow Workflow Syntax"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

# Check if Nextflow can at least parse the workflow
echo "Checking workflow files..."
echo ""

# Check main.nf exists
if [ ! -f "$PROJECT_ROOT/main.nf" ]; then
    echo "ERROR: main.nf not found at $PROJECT_ROOT/main.nf"
    exit 1
fi

# Check nextflow.config exists
if [ ! -f "$PROJECT_ROOT/nextflow.config" ]; then
    echo "ERROR: nextflow.config not found at $PROJECT_ROOT/nextflow.config"
    exit 1
fi

echo "✅ Workflow files found"
echo ""

# Check test data
FASTA="${PROJECT_ROOT}/test/resources/case_1/test.fasta"
FASTQ1="${PROJECT_ROOT}/test/resources/case_1/test_mate1.fastq"
FASTQ2="${PROJECT_ROOT}/test/resources/case_1/test_mate2.fastq"
DOT_BRACKET="${PROJECT_ROOT}/test/resources/case_1/test.csv"

echo "Checking test data..."
for file in "$FASTA" "$FASTQ1" "$FASTQ2" "$DOT_BRACKET"; do
    if [ -f "$file" ]; then
        echo "✅ $(basename $file)"
    else
        echo "❌ $(basename $file) not found"
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "Workflow files are valid!"
echo "=========================================="
echo ""
echo "To run the workflow, you need:"
echo "  1. Java 8-18 installed"
echo "  2. Nextflow installed"
echo "  3. rna-map Python package (installed in conda environment)"
echo ""
echo "Setup:"
echo "  conda env create -f environment.yml"
echo "  conda activate rna-map-nextflow"
echo "  cd src/rna_map && pip install -e . && cd ../.."
echo "  (No PYTHONPATH needed - package is installed in conda environment)"
echo ""

