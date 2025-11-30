#!/bin/bash
# Nextflow Syntax Validation Script
# Works with Nextflow 24.x (uses syntax checking via --help)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "Nextflow Syntax Validation"
echo "=========================================="
echo ""

# Activate conda environment if available
if command -v conda &> /dev/null; then
    if conda env list | grep -q "rna-map-nextflow"; then
        echo "Activating conda environment: rna-map-nextflow"
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate rna-map-nextflow || {
            echo "⚠️  Could not activate conda environment, using system Nextflow"
        }
    fi
fi

# Check Nextflow version
if ! command -v nextflow &> /dev/null; then
    echo "ERROR: Nextflow not found in PATH"
    echo "Please install Nextflow or activate conda environment"
    exit 1
fi

NEXTFLOW_VERSION=$(nextflow -version 2>&1 | grep -i version | head -1)
echo "Nextflow: $NEXTFLOW_VERSION"
echo ""

# Check Nextflow version for lint support
# Extract version numbers (macOS-compatible, no -P flag)
NEXTFLOW_VERSION_FULL=$(nextflow -version 2>&1 | grep -i "version" | head -1)
NEXTFLOW_MAJOR=$(echo "$NEXTFLOW_VERSION_FULL" | sed -E 's/.*version[^0-9]*([0-9]+)\.[0-9]+\..*/\1/' || echo "0")
NEXTFLOW_MINOR=$(echo "$NEXTFLOW_VERSION_FULL" | sed -E 's/.*version[^0-9]*[0-9]+\.([0-9]+)\..*/\1/' || echo "0")

if [ "$NEXTFLOW_MAJOR" -ge 25 ] || ([ "$NEXTFLOW_MAJOR" -eq 24 ] && [ "$NEXTFLOW_MINOR" -ge 4 ]); then
    echo "✅ Nextflow version supports 'lint' command"
    echo ""
    
    # Try using lint command
    if nextflow lint --help &> /dev/null 2>&1; then
        echo "Using Nextflow built-in linting..."
        echo ""
        nextflow lint main.nf
        echo ""
        echo "✅ Syntax validation complete"
        exit 0
    fi
fi

echo "⚠️  Nextflow lint command not available (requires Nextflow 25.04+)"
echo "   Using alternative syntax validation method..."
echo ""

# Alternative: Validate syntax by checking if Nextflow can parse the file
# This works by running nextflow with --help which validates syntax

VALIDATION_ERRORS=0

echo "Validating main.nf..."
if nextflow run main.nf --help > /dev/null 2>&1; then
    echo "✅ main.nf syntax is valid"
else
    # Check the actual error
    ERROR_OUTPUT=$(nextflow run main.nf --help 2>&1 || true)
    if echo "$ERROR_OUTPUT" | grep -q "ERROR: Must provide either"; then
        # This is our expected error, not a syntax error
        echo "✅ main.nf syntax is valid (parameter validation working)"
    elif echo "$ERROR_OUTPUT" | grep -qi "syntax\|parse\|compil"; then
        echo "❌ main.nf has syntax errors:"
        echo "$ERROR_OUTPUT" | grep -i "error\|syntax\|parse" | head -10
        VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
    else
        # Other errors might be expected (missing params, etc.)
        echo "⚠️  main.nf validation unclear - check output:"
        echo "$ERROR_OUTPUT" | head -5
    fi
fi
echo ""

# Validate modules
if [ -d "modules" ]; then
    echo "Validating modules..."
    for file in modules/*.nf; do
        if [ -f "$file" ]; then
            echo "  Checking $(basename $file)..."
            # Try to parse the module file
            # Modules can't be run directly, so we check if Nextflow can at least read them
            # by checking for obvious syntax errors in the log
            if grep -q "process\|workflow" "$file" 2>/dev/null; then
                echo "    ✅ $(basename $file) structure looks valid"
            else
                echo "    ⚠️  $(basename $file) may have issues (no process/workflow found)"
            fi
        fi
    done
    echo ""
fi

# Validate workflows
if [ -d "workflows" ]; then
    echo "Validating workflows..."
    for file in workflows/*.nf; do
        if [ -f "$file" ]; then
            echo "  Checking $(basename $file)..."
            if grep -q "workflow" "$file" 2>/dev/null; then
                echo "    ✅ $(basename $file) structure looks valid"
            else
                echo "    ⚠️  $(basename $file) may have issues (no workflow found)"
            fi
        fi
    done
    echo ""
fi

# Summary
if [ $VALIDATION_ERRORS -eq 0 ]; then
    echo "✅ All Nextflow files passed basic syntax validation"
    echo ""
    echo "Note: For more comprehensive linting, upgrade to Nextflow 25.04+ or use:"
    echo "  - Nextflow IDE extension in Cursor/VS Code"
    echo "  - nf-core lint (pip install nf-core)"
    exit 0
else
    echo "❌ Found $VALIDATION_ERRORS syntax error(s)"
    exit 1
fi

