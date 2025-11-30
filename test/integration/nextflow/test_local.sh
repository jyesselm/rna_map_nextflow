#!/bin/bash
# Test Nextflow workflow locally with example data

set -e

echo "=========================================="
echo "Testing RNA MAP Nextflow Workflow Locally"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Test data paths
FASTA="${PROJECT_ROOT}/test/resources/case_1/test.fasta"
FASTQ1="${PROJECT_ROOT}/test/resources/case_1/test_mate1.fastq"
FASTQ2="${PROJECT_ROOT}/test/resources/case_1/test_mate2.fastq"
DOT_BRACKET="${PROJECT_ROOT}/test/resources/case_1/test.csv"
OUTPUT_DIR="${PROJECT_ROOT}/test_results"

echo "Test Data:"
echo "  FASTA: ${FASTA}"
echo "  FASTQ1: ${FASTQ1}"
echo "  FASTQ2: ${FASTQ2}"
echo "  Dot-bracket: ${DOT_BRACKET}"
echo "  Output: ${OUTPUT_DIR}"
echo ""

# Check if test data exists
if [ ! -f "$FASTA" ]; then
    echo "ERROR: FASTA file not found: $FASTA"
    exit 1
fi

if [ ! -f "$FASTQ1" ]; then
    echo "ERROR: FASTQ1 file not found: $FASTQ1"
    exit 1
fi

if [ ! -f "$FASTQ2" ]; then
    echo "ERROR: FASTQ2 file not found: $FASTQ2"
    exit 1
fi

echo "Checking prerequisites..."
echo ""

# Check if conda environment is activated
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "WARNING: Conda environment not activated"
    echo ""
    echo "Recommended: Use conda environment"
    echo "  conda activate rna_map_nextflow"
    echo ""
    echo "Continuing with system Java/Nextflow..."
    echo ""
else
    echo "✅ Conda environment: $CONDA_DEFAULT_ENV"
fi

# Check Java
if ! command -v java &> /dev/null; then
    echo "ERROR: Java is required for Nextflow"
    echo ""
    echo "Solution: Use conda environment"
    echo "  conda activate rna_map_nextflow"
    echo "  # Or install manually:"
    echo "  conda install openjdk=11 -c conda-forge"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -1)
JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -1 | sed -E 's/.*version "([0-9]+).*/\1/')

echo "Java: $JAVA_VERSION"

# Check Java version (Nextflow requires Java 8-18)
if [ "$JAVA_MAJOR_VERSION" -gt 18 ]; then
    echo ""
    echo "WARNING: Java $JAVA_MAJOR_VERSION detected, but Nextflow requires Java 8-18"
    echo ""
    echo "Solution: Use conda environment with Java 11"
    echo "  conda activate rna_map_nextflow"
    echo ""
    echo "Continuing anyway (may fail)..."
    echo ""
fi

# Check Nextflow
if ! command -v nextflow &> /dev/null; then
    echo "ERROR: Nextflow not found in PATH"
    echo ""
    echo "Solution: Use conda environment"
    echo "  conda activate rna_map_nextflow"
    echo "  # Or install: conda install nextflow -c bioconda"
    exit 1
fi

echo "Nextflow: $(nextflow -version 2>&1 | head -1)"
echo ""

echo "Running Nextflow workflow..."
echo ""

# Run Nextflow with local profile
cd "$PROJECT_ROOT"

nextflow run main.nf \
    -profile local \
    --fasta "$FASTA" \
    --fastq1 "$FASTQ1" \
    --fastq2 "$FASTQ2" \
    --dot_bracket "$DOT_BRACKET" \
    --output_dir "$OUTPUT_DIR" \
    --skip_fastqc \
    --skip_trim_galore \
    -with-report test_report.html \
    -with-trace test_trace.txt \
    -with-dag test_dag.html

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="
echo ""
echo "Results:"
echo "  Output directory: ${OUTPUT_DIR}"
echo "  Report: ${PROJECT_ROOT}/test_report.html"
echo "  Trace: ${PROJECT_ROOT}/test_trace.txt"
echo "  DAG: ${PROJECT_ROOT}/test_dag.html"
echo ""
echo "To view results:"
echo "  ls -lh ${OUTPUT_DIR}/*/"
echo ""

