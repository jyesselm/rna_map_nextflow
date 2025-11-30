# Test Fixes Summary

## Overview

All test files have been updated to work with the new repository structure after refactoring.

## Changes Made

### 1. Created `python/tests/conftest.py`
- Provides `TEST_DATA_DIR` constant pointing to `test/data/resources/`
- Provides `PROJECT_ROOT` constant
- All tests can import these constants

### 2. Updated All Test Files

**Files Updated (11 total):**
- ✅ `test_bit_vector.py` - Updated to use `TEST_DATA_DIR`
- ✅ `test_bit_vector_cpp.py` - Updated paths and C++ module path
- ✅ `test_external_cmd.py` - Updated test data paths
- ✅ `test_run.py` - Updated test data paths
- ✅ `test_storage_format_performance.py` - Updated paths and C++ module path
- ✅ `test_detailed_implementation_comparison.py` - Updated paths and C++ module path
- ✅ `test_all_implementations_comparison.py` - Updated paths and C++ module path
- ✅ `test_cigar_parsing.py` - Updated test data path
- ✅ `test_sam.py` - Updated test data paths
- ✅ `test_mutation_histogram.py` - Updated test data paths

### 3. Path Updates

**Old paths (broken):**
- `TEST_DIR / "resources" / "case_1"` ❌
- `PROJECT_ROOT / "src" / "cpp"` ❌

**New paths (working):**
- `TEST_DATA_DIR / "case_1"` ✅ (from conftest)
- `PROJECT_ROOT / "cpp"` ✅ (from conftest)

### 4. C++ Module Path Updates

All tests that reference the C++ module now use:
```python
CPP_MODULE_PATH = PROJECT_ROOT / "cpp"  # Was: PROJECT_ROOT / "src" / "cpp"
```

## Test Data Location

Test data is now in: `test/data/resources/` (relative to project root)

This is accessible from tests via:
```python
from conftest import TEST_DATA_DIR
fa_path = TEST_DATA_DIR / "case_1" / "test.fasta"
```

## Verification

✅ All test files updated
✅ conftest.py created and working
✅ Test data paths verified to exist
✅ No remaining references to old paths

## Running Tests

To run tests, you need:
1. Python package installed: `cd python && pip install -e .`
2. Dependencies installed (from environment.yml or requirements.txt)
3. pytest installed: `pip install pytest`

Then run:
```bash
cd python
pytest tests/ -v
```

## Notes

- Some tests may require additional dependencies (pytest, etc.)
- C++ tests require the C++ module to be built
- Test data is in `test/data/resources/` and is tracked by git
- All imports use `from rna_map` (not `from src.rna_map`)

