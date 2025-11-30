# Test Status Report

## Summary

- **Total test files**: 15
- **Intentionally skipped**: 3 files (test removed modules)
- **Active test files**: 12 files
- **Broken tests**: 0 (all active tests should work)

## Intentionally Skipped Tests

These tests are **intentionally skipped** because they test modules that were removed during the Nextflow-first restructure. This is expected and correct behavior.

### 1. CLI Module Tests
- **File**: `test_bowtie2_presets.py`
- **File**: `test_cli_parser.py`
- **Reason**: `rna_map.cli` module was removed - CLI functionality moved to Nextflow
- **Status**: ✅ Correctly skipped

### 2. External Commands Module Tests
- **File**: `test_external_cmd.py`
- **Reason**: `rna_map.external` module was removed - external commands moved to Nextflow modules
- **Status**: ✅ Correctly skipped

### 3. Visualization Module Tests (Partial)
- **File**: `test_mutation_histogram.py` (4 tests skipped)
- **Reason**: `rna_map.visualization` module was removed
- **Status**: ✅ Correctly skipped (core mutation histogram tests still run)

## Active Tests (Should Work)

All of these tests should work correctly:

1. ✅ `test_bit_vector.py` - Core bit vector functionality
2. ✅ `test_bit_vector_cpp.py` - C++ implementation (requires C++ module)
3. ✅ `test_bowtie2_presets.py` - Skipped (CLI removed)
4. ✅ `test_cigar_parsing.py` - CIGAR parsing (requires C++ module)
5. ✅ `test_cli_parser.py` - Skipped (CLI removed)
6. ✅ `test_config.py` - Configuration dataclasses
7. ✅ `test_detailed_implementation_comparison.py` - Implementation comparison
8. ✅ `test_external_cmd.py` - Skipped (external module removed)
9. ✅ `test_logging.py` - Logging functionality
10. ✅ `test_mutation_histogram.py` - Mutation histogram (some visualization tests skipped)
11. ✅ `test_results.py` - Result dataclasses
12. ✅ `test_run.py` - Input validation
13. ✅ `test_sam.py` - SAM file parsing
14. ✅ `test_storage_format_performance.py` - Storage format performance
15. ✅ `test_all_implementations_comparison.py` - All implementations comparison

## Test Dependencies

### Required for All Tests
- Python package installed: `cd python && pip install -e .`
- Test data available: `test/data/resources/` (via `conftest.py`)

### Required for Some Tests
- **C++ module**: Required for tests with `_cpp` in name
  - Build: `cd cpp && ./build.sh`
  - Tests will skip if C++ module not available (using `@pytest.mark.skipif`)

## Running Tests

### All Tests (including skipped)
```bash
cd python
pip install -e .
pytest tests/ -v
```

### Only Active Tests (exclude skipped)
```bash
cd python
pytest tests/ -v -m "not skip"
```

### Quick Tests Only
```bash
cd python
pytest tests/ -v -m quick
```

### Specific Test File
```bash
cd python
pytest tests/test_bit_vector.py -v
```

## Expected Test Results

When running `pytest tests/ -v`:
- **Skipped tests**: Will show as "SKIPPED" (expected)
- **Active tests**: Should pass (if dependencies installed)
- **C++ tests**: Will skip if C++ module not built (expected)

## Notes

- Skipped tests are kept for historical reference
- All active tests have been updated for the new repository structure
- Test data paths fixed to use `test/data/resources/` via `conftest.py`
- C++ module paths updated from `src/cpp/` to `cpp/`

## If Tests Fail

1. **Import errors**: Make sure package is installed: `cd python && pip install -e .`
2. **Missing dependencies**: Install from `environment.yml` or `requirements.txt`
3. **C++ tests skip**: Build C++ module: `cd cpp && ./build.sh`
4. **Test data not found**: Verify `test/data/resources/` exists

