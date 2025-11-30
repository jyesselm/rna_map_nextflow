# Test Status

## Test Organization

Tests are organized by what they test:
- **Core functionality tests**: Test core modules that are still used
- **Skipped tests**: Test modules that were removed during Nextflow migration

## Intentionally Skipped Tests

These tests are skipped because the modules they test were removed during the Nextflow-first restructure:

### 1. CLI Module Tests (Skipped)
- `test_bowtie2_presets.py` - Tests `rna_map.cli` module (removed)
- `test_cli_parser.py` - Tests `rna_map.cli` module (removed)

**Reason**: CLI functionality moved to Nextflow. These tests are kept for reference but skipped.

### 2. External Commands Module Tests (Skipped)
- `test_external_cmd.py` - Tests `rna_map.external` module (removed)

**Reason**: External command execution moved to Nextflow modules. These tests are kept for reference but skipped.

### 3. Visualization Module Tests (Partially Skipped)
- `test_mutation_histogram.py` - Some tests for `rna_map.visualization` (removed)

**Reason**: Visualization functionality removed. Core mutation histogram tests still run.

## Active Tests

These tests should work and are actively maintained:

- ✅ `test_bit_vector.py` - Core bit vector functionality
- ✅ `test_bit_vector_cpp.py` - C++ bit vector implementation (requires C++ module)
- ✅ `test_cigar_parsing.py` - CIGAR string parsing (requires C++ module)
- ✅ `test_config.py` - Configuration dataclasses
- ✅ `test_logging.py` - Logging functionality
- ✅ `test_mutation_histogram.py` - Mutation histogram core functionality (some visualization tests skipped)
- ✅ `test_results.py` - Result dataclasses
- ✅ `test_run.py` - Input validation
- ✅ `test_sam.py` - SAM file parsing
- ✅ `test_storage_format_performance.py` - Storage format performance (requires C++ module)
- ✅ `test_all_implementations_comparison.py` - Implementation comparison (requires C++ module)
- ✅ `test_detailed_implementation_comparison.py` - Detailed comparison (requires C++ module)

## Running Tests

### All Tests (including skipped)
```bash
cd python
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

## Test Dependencies

Some tests require:
- **C++ module**: `test_bit_vector_cpp.py`, `test_cigar_parsing.py`, etc.
  - Build with: `cd ../../cpp && ./build.sh`
- **Test data**: All tests use `test/data/resources/` (via `conftest.py`)

## Notes

- Skipped tests are kept for historical reference
- If you need CLI/external/visualization functionality, consider:
  - CLI: Use Nextflow directly or create wrapper scripts
  - External commands: Use Nextflow modules
  - Visualization: Use external tools or create new visualization module

