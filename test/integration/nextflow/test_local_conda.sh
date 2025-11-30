#!/bin/bash
# Test Nextflow workflow locally using conda environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "Testing RNA MAP Nextflow Workflow (Conda)"
echo "=========================================="
echo ""

# Check if conda/mamba environment exists
if command -v mamba &> /dev/null; then
    CONDA_CMD="mamba"
elif command -v conda &> /dev/null; then
    CONDA_CMD="conda"
else
    echo "ERROR: Neither mamba nor conda found"
    exit 1
fi

if ! $CONDA_CMD env list | grep -q "rna_map_nextflow"; then
    echo "ERROR: Conda environment 'rna_map_nextflow' not found"
    echo ""
    echo "Create it with:"
    echo "  conda env create -f environment.yml"
    exit 1
fi

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

echo "Using conda environment: rna_map_nextflow"
echo ""

# Verify tools in environment
echo "Checking tools..."
$CONDA_CMD run -n rna_map_nextflow nextflow -version 2>&1 | head -1
$CONDA_CMD run -n rna_map_nextflow python -c "import sys; sys.path.insert(0, '${PROJECT_ROOT}/lib'); from lib import __version__; print(f'lib: {__version__}')" 2>&1
echo ""

echo "Running Nextflow workflow..."
echo ""

# Run Nextflow with local profile using conda environment
cd "$PROJECT_ROOT"

# No PYTHONPATH needed - packages are installed in conda environment via .pth file

$CONDA_CMD run -n rna_map_nextflow bash -c "nextflow run main.nf \
    -profile local \
    --fasta "$FASTA" \
    --fastq1 "$FASTQ1" \
    --fastq2 "$FASTQ2" \
    --dot_bracket "$DOT_BRACKET" \
    --output_dir "$OUTPUT_DIR" \
    --max_cpus 4 \
    --skip_fastqc \
    --skip_trim_galore \
    -with-report test_report.html \
    -with-trace test_trace.txt \
    -with-dag test_dag.html"

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

