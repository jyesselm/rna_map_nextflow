#!/bin/bash
# Build script for C++ bit vector module

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Building C++ bit vector module..."

cd "$PROJECT_ROOT"

# Check if pybind11 is available
python3 -c "import pybind11" 2>/dev/null || {
    echo "ERROR: pybind11 not found. Install with: pip install pybind11"
    exit 1
}

# Build using setuptools
python3 cpp/setup.py build_ext --inplace

echo "✅ C++ module built successfully!"
echo "Module location: lib/rna_map/bit_vector_cpp.*"

