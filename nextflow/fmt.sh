#!/bin/bash
# Nextflow Formatting Script
# Formats all Nextflow workflow files

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Nextflow Formatting"
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

# Check if fmt command is available (Nextflow 25.04+)
if nextflow fmt --help &> /dev/null; then
    echo "Formatting Nextflow files..."
    echo ""
    
    # Format main workflow
    echo "Formatting main.nf..."
    nextflow fmt main.nf
    
    # Format modules
    if [ -d "modules" ]; then
        echo "Formatting modules..."
        nextflow fmt modules/
    fi
    
    # Format workflows
    if [ -d "workflows" ]; then
        echo "Formatting workflows..."
        nextflow fmt workflows/
    fi
    
    echo ""
    echo "✅ Formatting complete"
else
    echo "⚠️  Nextflow fmt command not available (requires Nextflow 25.04+)"
    echo "   Current version may not support 'nextflow fmt'"
    exit 0
fi

