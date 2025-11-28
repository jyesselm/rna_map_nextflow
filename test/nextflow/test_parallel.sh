#!/bin/bash
# Test Nextflow workflow with parallel FASTQ splitting

set -e

echo "=========================================="
echo "Testing RNA MAP Nextflow Parallel Processing"
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
OUTPUT_DIR="${PROJECT_ROOT}/test_results_parallel"

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

echo "Checking prerequisites..."
echo ""

# Check if conda environment is activated
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "WARNING: Conda environment not activated. Please activate 'rna_map_nextflow' for best results."
else
    echo "✅ Conda environment: $CONDA_DEFAULT_ENV"
fi

# Check Java - prefer conda environment Java if available
# Check both possible locations (lib/jvm/bin is common for openjdk)
if [ -n "$CONDA_PREFIX" ]; then
    if [ -f "${CONDA_PREFIX}/lib/jvm/bin/java" ]; then
        export JAVA_HOME="${CONDA_PREFIX}/lib/jvm"
        export PATH="${CONDA_PREFIX}/lib/jvm/bin:${CONDA_PREFIX}/bin:$PATH"
        export JAVA_CMD="${CONDA_PREFIX}/lib/jvm/bin/java"
        echo "Using Java from conda environment: ${CONDA_PREFIX}/lib/jvm"
    elif [ -f "${CONDA_PREFIX}/bin/java" ]; then
        export JAVA_HOME="${CONDA_PREFIX}"
        export PATH="${CONDA_PREFIX}/bin:$PATH"
        export JAVA_CMD="${CONDA_PREFIX}/bin/java"
        echo "Using Java from conda environment: ${CONDA_PREFIX}"
    fi
fi

if ! command -v java &> /dev/null; then
    echo "ERROR: Java is required for Nextflow"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -1)
JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -1 | sed -E 's/.*version "([0-9]+).*/\1/' 2>/dev/null || echo "0")

echo "Java: $JAVA_VERSION"

# Check Java version (Nextflow requires Java 8-18)
if [ "$JAVA_MAJOR_VERSION" -gt 18 ] || [ "$JAVA_MAJOR_VERSION" -lt 8 ]; then
    echo ""
    echo "WARNING: Java $JAVA_MAJOR_VERSION detected, but Nextflow requires Java 8-18"
    echo ""
    
    # Try to use Java from conda environment if available
    if [ -n "$CONDA_PREFIX" ]; then
        # Check both possible locations (lib/jvm/bin is common for openjdk)
        CONDA_JAVA="${CONDA_PREFIX}/lib/jvm/bin/java"
        if [ ! -f "$CONDA_JAVA" ]; then
            CONDA_JAVA="${CONDA_PREFIX}/bin/java"
        fi
        if [ -f "$CONDA_JAVA" ]; then
            CONDA_JAVA_VER=$("$CONDA_JAVA" -version 2>&1 | head -1 | sed -E 's/.*version "([0-9]+).*/\1/' 2>/dev/null || echo "0")
            if [ "$CONDA_JAVA_VER" -ge 8 ] && [ "$CONDA_JAVA_VER" -le 18 ]; then
                # Set JAVA_HOME and PATH to use conda Java
                if [ -f "${CONDA_PREFIX}/lib/jvm/bin/java" ]; then
                    export JAVA_HOME="${CONDA_PREFIX}/lib/jvm"
                    export PATH="${CONDA_PREFIX}/lib/jvm/bin:${CONDA_PREFIX}/bin:$PATH"
                    # Also set for Nextflow
                    export JAVA_CMD="${CONDA_PREFIX}/lib/jvm/bin/java"
                else
                    export JAVA_HOME="${CONDA_PREFIX}"
                    export PATH="${CONDA_PREFIX}/bin:$PATH"
                    export JAVA_CMD="${CONDA_PREFIX}/bin/java"
                fi
                echo "✅ Found Java $CONDA_JAVA_VER in conda environment: ${CONDA_PREFIX}"
                echo "   Using conda Java instead of system Java"
                # Re-check version after switching
                JAVA_VERSION=$(java -version 2>&1 | head -1)
                JAVA_MAJOR_VERSION=$(java -version 2>&1 | head -1 | sed -E 's/.*version "([0-9]+).*/\1/' 2>/dev/null || echo "0")
                echo "   Java: $JAVA_VERSION"
                echo "   JAVA_HOME: $JAVA_HOME"
            else
                echo "❌ Conda environment has Java $CONDA_JAVA_VER (also incompatible)"
                echo ""
                # Detect if mamba is available
                if command -v mamba &> /dev/null; then
                    INSTALL_CMD="mamba install openjdk=11 -c conda-forge"
                    ENV_CMD="mamba env create -f environment.yml"
                else
                    INSTALL_CMD="conda install openjdk=11 -c conda-forge"
                    ENV_CMD="conda env create -f environment.yml"
                fi
                echo "To fix: Install Java 11 in your conda environment:"
                echo "  ${INSTALL_CMD}"
                echo ""
                echo "Or create/update the rna_map_nextflow environment:"
                echo "  ${ENV_CMD}"
                exit 1
            fi
        else
            echo "❌ No Java found in conda environment: ${CONDA_PREFIX}"
            echo ""
            # Detect if mamba is available
            if command -v mamba &> /dev/null; then
                INSTALL_CMD="mamba install openjdk=11 -c conda-forge"
                ENV_CMD="mamba env create -f environment.yml"
            else
                INSTALL_CMD="conda install openjdk=11 -c conda-forge"
                ENV_CMD="conda env create -f environment.yml"
            fi
            echo "To fix: Install Java 11 in your conda environment:"
            echo "  ${INSTALL_CMD}"
            echo ""
            echo "Or create/update the rna_map_nextflow environment:"
            echo "  ${ENV_CMD}"
            exit 1
        fi
    else
        echo "❌ No conda environment detected"
        echo ""
        # Detect if mamba is available
        if command -v mamba &> /dev/null; then
            INSTALL_CMD="mamba install openjdk=11 -c conda-forge"
        else
            INSTALL_CMD="conda install openjdk=11 -c conda-forge"
        fi
        echo "To fix: Activate rna_map_nextflow environment or install Java 8-18"
        echo "  conda activate rna_map_nextflow"
        echo "  ${INSTALL_CMD}"
        exit 1
    fi
fi

# Check Nextflow
if ! command -v nextflow &> /dev/null; then
    echo "ERROR: Nextflow not found in PATH"
    exit 1
fi

# Verify Nextflow can see the correct Java
if [ -n "$JAVA_HOME" ]; then
    echo "Nextflow Java check:"
    JAVA_CHECK=$(nextflow -version 2>&1 | grep -i "java\|error" | head -3 || echo "OK")
    echo "  $JAVA_CHECK"
fi

echo "Nextflow: $(nextflow -version 2>&1 | head -1)"
echo ""

# Count reads in FASTQ file to determine chunk size
echo "Analyzing FASTQ file..."
READ_COUNT=$(grep -c "^@" "$FASTQ1" 2>/dev/null || echo "0")
echo "  Reads in FASTQ1: ${READ_COUNT}"

# Use small chunk size for testing (split into 2-3 chunks)
CHUNK_SIZE=$((READ_COUNT / 3))
if [ $CHUNK_SIZE -lt 100 ]; then
    CHUNK_SIZE=100  # Minimum chunk size
fi
echo "  Chunk size: ${CHUNK_SIZE} reads (will create ~3 chunks)"
echo ""

echo "Running Nextflow workflow with parallel splitting..."
echo ""

# Run Nextflow with local profile and split_fastq enabled
cd "$PROJECT_ROOT"

# No PYTHONPATH needed - packages are installed in conda environment via .pth file

# Note: This requires Java 8-18. If you get a Java version error, please:
# 1. Activate the rna_map_nextflow conda environment: conda activate rna_map_nextflow
# 2. Or install Java 11: conda install openjdk=11 -c conda-forge

nextflow run main.nf \
    -profile local \
    --fasta "$FASTA" \
    --fastq1 "$FASTQ1" \
    --fastq2 "$FASTQ2" \
    --dot_bracket "$DOT_BRACKET" \
    --output_dir "$OUTPUT_DIR" \
    --split_fastq \
    --chunk_size "$CHUNK_SIZE" \
    --skip_fastqc \
    --skip_trim_galore \
    -with-report test_report_parallel.html \
    -with-trace test_trace_parallel.txt \
    -with-dag test_dag_parallel.html

echo ""
echo "=========================================="
echo "Test completed!"
echo "=========================================="
echo ""
echo "Results:"
echo "  Output directory: ${OUTPUT_DIR}"
echo "  Report: ${PROJECT_ROOT}/test_report_parallel.html"
echo "  Trace: ${PROJECT_ROOT}/test_trace_parallel.txt"
echo "  DAG: ${PROJECT_ROOT}/test_dag_parallel.html"
echo ""
echo "Checking outputs..."
echo ""

# Check for key output files
SAM_FILE=$(find "${OUTPUT_DIR}" -name "aligned.sam" -path "*/Mapping_Files/*" | head -1)
if [ -n "${SAM_FILE}" ] && [ -f "${SAM_FILE}" ]; then
    echo "✅ SAM file found: ${SAM_FILE}"
    SAM_LINES=$(wc -l < "${SAM_FILE}")
    echo "   SAM file has ${SAM_LINES} lines"
else
    echo "❌ SAM file not found"
fi

SUMMARY_FILE=$(find "${OUTPUT_DIR}" -name "summary.csv" -path "*/BitVector_Files/*" | head -1)
if [ -n "${SUMMARY_FILE}" ] && [ -f "${SUMMARY_FILE}" ]; then
    echo "✅ Summary CSV found: ${SUMMARY_FILE}"
else
    echo "⚠️  Summary CSV not found (may be optional if summary_output_only=false)"
fi

PICKLE_FILE=$(find "${OUTPUT_DIR}" -name "mutation_histos.p" -path "*/BitVector_Files/*" | head -1)
if [ -n "${PICKLE_FILE}" ] && [ -f "${PICKLE_FILE}" ]; then
    echo "✅ Mutation histograms pickle found: ${PICKLE_FILE}"
else
    echo "❌ Mutation histograms pickle not found"
fi

JSON_FILE=$(find "${OUTPUT_DIR}" -name "mutation_histos.json" -path "*/BitVector_Files/*" | head -1)
if [ -n "${JSON_FILE}" ] && [ -f "${JSON_FILE}" ]; then
    echo "✅ Mutation histograms JSON found: ${JSON_FILE}"
else
    echo "❌ Mutation histograms JSON not found"
fi

echo ""
echo "To view results:"
echo "  ls -lh ${OUTPUT_DIR}/*/"
echo ""

