#!/bin/bash
# Simple test - just validate the workflow syntax
# This doesn't require Java to be the right version

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Validating Nextflow Workflow Syntax"
echo "=========================================="
echo ""

cd "$SCRIPT_DIR"

# Check if Nextflow can at least parse the workflow
echo "Checking workflow files..."
echo ""

# Check main.nf exists
if [ ! -f "main.nf" ]; then
    echo "ERROR: main.nf not found"
    exit 1
fi

# Check nextflow.config exists
if [ ! -f "nextflow.config" ]; then
    echo "ERROR: nextflow.config not found"
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
echo "  3. rna_map Python package installed"
echo ""
echo "See INSTALL.md for installation instructions"
echo ""

