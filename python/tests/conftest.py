"""
Pytest configuration and fixtures for rna_map tests.

This file sets up the test environment and provides fixtures for test data paths.
"""
import os
from pathlib import Path

# Get the project root (2 levels up from this file: python/tests/ -> python/ -> project root)
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test" / "data" / "resources"

# Make TEST_DATA_DIR available as a constant
__all__ = ["TEST_DATA_DIR", "PROJECT_ROOT"]

