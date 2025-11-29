#!/usr/bin/env python3
"""Quick test script to verify Optuna environment is set up correctly.

This script checks that all required packages are installed and can be imported.
"""

import sys
from pathlib import Path

# Package should be installed via pip install -e src/rna_map
PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_imports() -> bool:
    """Test that all required packages can be imported.
    
    Returns:
        True if all imports succeed, False otherwise.
    """
    print("Testing imports...")
    errors = []
    
    # Test standard library imports
    try:
        import json
        import subprocess
        import time
        from pathlib import Path as PathLib
        print("  ✓ Standard library imports")
    except ImportError as e:
        errors.append(f"Standard library import failed: {e}")
    
    # Test third-party imports
    try:
        import pandas as pd
        print("  ✓ pandas")
    except ImportError as e:
        errors.append(f"pandas import failed: {e}")
    
    try:
        import numpy as np
        print("  ✓ numpy")
    except ImportError as e:
        errors.append(f"numpy import failed: {e}")
    
    try:
        import optuna
        print(f"  ✓ optuna (version {optuna.__version__})")
    except ImportError as e:
        errors.append(f"optuna import failed: {e}")
    
    try:
        import plotly
        print(f"  ✓ plotly (version {plotly.__version__})")
    except ImportError as e:
        errors.append(f"plotly import failed: {e}")
    
    # Test rna_map imports
    try:
        from rna_map.io.fasta import fasta_to_dict
        print("  ✓ rna_map.io.fasta")
    except ImportError as e:
        errors.append(f"rna_map.io.fasta import failed: {e}")
    
    try:
        from rna_map.logger import get_logger
        print("  ✓ rna_map.logger")
    except ImportError as e:
        errors.append(f"rna_map.logger import failed: {e}")
    
    try:
        from rna_map.analysis.bit_vector_iterator import BitVectorIterator
        print("  ✓ rna_map.analysis.bit_vector_iterator")
    except ImportError as e:
        errors.append(f"rna_map.analysis.bit_vector_iterator import failed: {e}")
    
    try:
        from rna_map.analysis.mutation_histogram import MutationHistogram
        print("  ✓ rna_map.analysis.mutation_histogram")
    except ImportError as e:
        errors.append(f"rna_map.analysis.mutation_histogram import failed: {e}")
    
    # Test Optuna visualization imports
    try:
        from optuna.visualization import (
            plot_optimization_history,
            plot_param_importances,
            plot_parallel_coordinate,
        )
        print("  ✓ optuna.visualization")
    except ImportError as e:
        errors.append(f"optuna.visualization import failed: {e}")
    
    if errors:
        print("\nErrors encountered:")
        for error in errors:
            print(f"  ✗ {error}")
        return False
    
    return True


def test_bowtie2() -> bool:
    """Test that bowtie2 is available.
    
    Returns:
        True if bowtie2 is available, False otherwise.
    """
    print("\nTesting bowtie2 availability...")
    try:
        import subprocess
        result = subprocess.run(
            ["bowtie2", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            print(f"  ✓ {version_line}")
            return True
        else:
            print(f"  ✗ bowtie2 returned non-zero exit code")
            return False
    except FileNotFoundError:
        print("  ✗ bowtie2 not found in PATH")
        return False
    except Exception as e:
        print(f"  ✗ Error testing bowtie2: {e}")
        return False


def test_optimization_script() -> bool:
    """Test that the optimization script exists and is executable.
    
    Returns:
        True if script exists, False otherwise.
    """
    print("\nTesting optimization script...")
    script_path = Path(__file__).parent / "scripts" / "optimize_bowtie2_params_optuna.py"
    if script_path.exists():
        print(f"  ✓ Script exists: {script_path}")
        return True
    else:
        print(f"  ✗ Script not found: {script_path}")
        return False


def test_test_resources() -> bool:
    """Test that test resources exist.
    
    Returns:
        True if resources exist, False otherwise.
    """
    print("\nTesting test resources...")
    base_path = Path(__file__).parent / "test" / "resources" / "case_1"
    required_files = [
        "test.fasta",
        "test_mate1.fastq",
        "test_mate2.fastq",
    ]
    
    all_exist = True
    for filename in required_files:
        file_path = base_path / filename
        if file_path.exists():
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} not found")
            all_exist = False
    
    return all_exist


def main() -> int:
    """Run all tests.
    
    Returns:
        0 if all tests pass, 1 otherwise.
    """
    print("=" * 60)
    print("Optuna Environment Test")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test bowtie2
    if not test_bowtie2():
        all_passed = False
    
    # Test optimization script
    if not test_optimization_script():
        all_passed = False
    
    # Test resources
    if not test_test_resources():
        all_passed = False
    
    print()
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! Environment is ready.")
        print("=" * 60)
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())

