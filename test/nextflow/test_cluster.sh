#!/bin/bash
# Cluster Testing Script for RNA MAP Nextflow
# 
# This script provides a comprehensive test suite for cluster environments.
# It can be run as a SLURM job or interactively on a compute node.
#
# Usage:
#   Interactive: ./test_cluster.sh
#   As SLURM job: sbatch test_cluster.sh

set -e

echo "=========================================="
echo "RNA MAP Nextflow - Cluster Testing Suite"
echo "=========================================="
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project root
cd "$PROJECT_ROOT"

echo "Project root: $PROJECT_ROOT"
echo ""

# Check if running as SLURM job
if [ -n "$SLURM_JOB_ID" ]; then
    echo "Running as SLURM job: $SLURM_JOB_ID"
    echo "Node: $SLURM_NODELIST"
    echo ""
fi

# Test 1: Environment Check
echo "=========================================="
echo "Test 1: Environment Check"
echo "=========================================="
echo ""

# Check conda
if command -v conda &> /dev/null; then
    echo "✅ Conda found: $(which conda)"
    conda --version
else
    echo "❌ Conda not found"
    exit 1
fi

# Check if environment exists
if conda env list | grep -q "rna-map-nextflow"; then
    echo "✅ Conda environment 'rna-map-nextflow' exists"
else
    echo "❌ Conda environment 'rna-map-nextflow' not found"
    echo "   Create it with: conda env create -f environment.yml"
    exit 1
fi

# Activate environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Check Java
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -1)
    echo "✅ Java found: $JAVA_VERSION"
    JAVA_MAJOR=$(java -version 2>&1 | head -1 | sed -E 's/.*version "([0-9]+).*/\1/')
    if [ "$JAVA_MAJOR" -lt 8 ] || [ "$JAVA_MAJOR" -gt 18 ]; then
        echo "⚠️  Warning: Java $JAVA_MAJOR detected. Nextflow requires Java 8-18"
    fi
else
    echo "❌ Java not found"
    exit 1
fi

# Check Nextflow
if command -v nextflow &> /dev/null; then
    echo "✅ Nextflow found: $(which nextflow)"
    nextflow -version | head -1
else
    echo "❌ Nextflow not found"
    exit 1
fi

# Check bioinformatics tools
for tool in bowtie2 fastqc trim_galore cutadapt; do
    if command -v $tool &> /dev/null; then
        echo "✅ $tool found: $(which $tool)"
    else
        echo "❌ $tool not found"
        exit 1
    fi
done

echo ""

# Test 2: PYTHONPATH Check
echo "=========================================="
echo "Test 2: PYTHONPATH Check"
echo "=========================================="
echo ""

export PYTHONPATH="${PROJECT_ROOT}/lib:${PYTHONPATH}"
echo "PYTHONPATH: $PYTHONPATH"

if [ -d "${PROJECT_ROOT}/lib" ]; then
    echo "✅ lib/ directory exists"
else
    echo "❌ lib/ directory not found"
    exit 1
fi

# Test Python imports
echo ""
echo "Testing Python imports..."
python -c "from lib.bit_vectors import generate_bit_vectors; print('✅ lib.bit_vectors')" || exit 1
python -c "from lib.core.config import BitVectorConfig; print('✅ lib.core.config')" || exit 1
python -c "from lib.analysis.statistics import merge_all_merge_mut_histo_dicts; print('✅ lib.analysis.statistics')" || exit 1
python -c "from lib.mutation_histogram import write_mut_histos_to_json_file; print('✅ lib.mutation_histogram')" || exit 1

echo ""

# Test 3: File Structure Check
echo "=========================================="
echo "Test 3: File Structure Check"
echo "=========================================="
echo ""

for file in main.nf nextflow.config environment.yml; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file not found"
        exit 1
    fi
done

for dir in modules workflows conf lib; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/ directory exists"
    else
        echo "❌ $dir/ directory not found"
        exit 1
    fi
done

echo ""

# Test 4: Test Data Check
echo "=========================================="
echo "Test 4: Test Data Check"
echo "=========================================="
echo ""

TEST_DATA_DIR="${PROJECT_ROOT}/test/resources/case_1"
if [ -d "$TEST_DATA_DIR" ]; then
    echo "✅ Test data directory exists"
    
    for file in test.fasta test_mate1.fastq test_mate2.fastq test.csv; do
        if [ -f "${TEST_DATA_DIR}/${file}" ]; then
            SIZE=$(ls -lh "${TEST_DATA_DIR}/${file}" | awk '{print $5}')
            echo "✅ $file exists ($SIZE)"
        else
            echo "❌ $file not found"
            exit 1
        fi
    done
else
    echo "❌ Test data directory not found: $TEST_DATA_DIR"
    exit 1
fi

echo ""

# Test 5: Nextflow Syntax Validation
echo "=========================================="
echo "Test 5: Nextflow Syntax Validation"
echo "=========================================="
echo ""

echo "Validating main.nf..."
nextflow run main.nf --help > /dev/null 2>&1 || {
    echo "❌ main.nf syntax error"
    exit 1
}
echo "✅ main.nf syntax valid"

echo "Validating modules..."
for module in modules/*.nf; do
    if [ -f "$module" ]; then
        echo "  Checking $(basename $module)..."
        # Basic syntax check - try to parse
        nextflow run "$module" --help > /dev/null 2>&1 || echo "  ⚠️  Warning: $(basename $module) may have issues"
    fi
done

echo "✅ Module validation complete"

echo ""

# Test 6: Configuration Check
echo "=========================================="
echo "Test 6: Configuration Check"
echo "=========================================="
echo ""

if [ -f "conf/base.config" ]; then
    echo "✅ conf/base.config exists"
else
    echo "❌ conf/base.config not found"
    exit 1
fi

if [ -f "conf/local.config" ]; then
    echo "✅ conf/local.config exists"
fi

if [ -f "conf/slurm.config" ]; then
    echo "✅ conf/slurm.config exists"
fi

echo ""

# Test 7: Dry Run Test
echo "=========================================="
echo "Test 7: Dry Run Test"
echo "=========================================="
echo ""

echo "Running Nextflow dry run (this may take a minute)..."
nextflow run main.nf \
    -profile slurm \
    --fasta "${TEST_DATA_DIR}/test.fasta" \
    --fastq1 "${TEST_DATA_DIR}/test_mate1.fastq" \
    --fastq2 "${TEST_DATA_DIR}/test_mate2.fastq" \
    --dot_bracket "${TEST_DATA_DIR}/test.csv" \
    --output_dir "${PROJECT_ROOT}/test_results_dry" \
    --skip_fastqc \
    --skip_trim_galore \
    -with-dag "${PROJECT_ROOT}/test_dag_dry.html" \
    -resume > /dev/null 2>&1 || {
    echo "❌ Dry run failed"
    echo "Check .nextflow.log for details"
    exit 1
}

echo "✅ Dry run completed successfully"

# Clean up dry run results
rm -rf "${PROJECT_ROOT}/test_results_dry" "${PROJECT_ROOT}/test_dag_dry.html" 2>/dev/null || true

echo ""

# Summary
echo "=========================================="
echo "✅ All Tests Passed!"
echo "=========================================="
echo ""
echo "Your cluster environment is ready for RNA MAP Nextflow."
echo ""
echo "Next steps:"
echo "  1. Review CLUSTER_TESTING_GUIDE.md for detailed testing instructions"
echo "  2. Run a minimal test: sbatch test_cluster_minimal.sh"
echo "  3. Run a full test: sbatch test_cluster_full.sh"
echo ""
echo "For help, see docs/CLUSTER_TESTING_GUIDE.md"
echo ""

