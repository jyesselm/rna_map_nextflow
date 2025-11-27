#!/bin/bash
# Nextflow Linting Script
# Lints all Nextflow workflow files

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Nextflow Linting"
echo "=========================================="
echo ""

# Check Nextflow version
if ! command -v nextflow &> /dev/null; then
    echo "ERROR: Nextflow not found in PATH"
    echo "Please install Nextflow or activate conda environment"
    exit 1
fi

NEXTFLOW_VERSION=$(nextflow -version 2>&1 | head -1)
echo "Nextflow: $NEXTFLOW_VERSION"
echo ""

# Check if lint command is available (Nextflow 25.04+)
if nextflow lint --help &> /dev/null; then
    echo "Using Nextflow built-in linting..."
    echo ""
    
    # Lint main workflow
    echo "Linting main.nf..."
    nextflow lint main.nf || exit 1
    
    # Lint modules
    if [ -d "modules" ]; then
        echo "Linting modules..."
        for file in modules/*.nf; do
            if [ -f "$file" ]; then
                echo "  - $(basename $file)"
                nextflow lint "$file" || exit 1
            fi
        done
    fi
    
    # Lint workflows
    if [ -d "workflows" ]; then
        echo "Linting workflows..."
        for file in workflows/*.nf; do
            if [ -f "$file" ]; then
                echo "  - $(basename $file)"
                nextflow lint "$file" || exit 1
            fi
        done
    fi
    
    echo ""
    echo "✅ All Nextflow files passed linting"
else
    echo "⚠️  Nextflow lint command not available (requires Nextflow 25.04+)"
    echo "   Current version may not support 'nextflow lint'"
    echo ""
    echo "Alternative: Use 'nextflow run' with --dry-run to validate syntax"
    echo "   nextflow run main.nf --help"
    exit 0
fi

