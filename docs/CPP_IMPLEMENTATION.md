# C++ Bit Vector Generation Implementation

This document describes the C++ implementation of bit vector generation with Python bindings.

## Overview

The C++ implementation provides a faster alternative to the Python bit vector generation code. It uses pybind11 to create Python bindings, allowing seamless integration with the existing Python codebase.

## Architecture

- **C++ Core** (`cpp/src/bit_vector_generator.cpp`): Implements the bit vector generation algorithm
- **Python Bindings** (`cpp/src/bindings.cpp`): pybind11 bindings to expose C++ to Python
- **Python Wrapper** (`lib/rna_map/pipeline/bit_vector_cpp.py`): Integration layer that uses C++ for bit vector generation but Python for SAM parsing and histogram generation

## Key Features

1. **Hybrid Approach**: Uses Python for SAM file parsing (reusing existing code) and C++ for computationally intensive bit vector generation
2. **Automatic Fallback**: Falls back to Python implementation if C++ module is not available
3. **Comparison Mode**: Can compare C++ and Python results to verify correctness
4. **Same Interface**: Uses the same `generate_bit_vectors()` function with `use_cpp=True` config option

## Building

### Prerequisites

```bash
pip install pybind11
```

### Build

```bash
cd cpp
python setup.py build_ext --inplace
```

Or use the build script:
```bash
./cpp/build.sh
```

The compiled module will be placed in `lib/rna_map/bit_vector_cpp.*`.

## Usage

### Enable C++ Implementation

```python
from rna_map.core.config import BitVectorConfig
from rna_map.pipeline.functions import generate_bit_vectors

config = BitVectorConfig(
    qscore_cutoff=25,
    num_of_surbases=10,
    map_score_cutoff=15,
    use_cpp=True,  # Enable C++ implementation
)

result = generate_bit_vectors(
    sam_path=Path("aligned.sam"),
    fasta=Path("ref.fasta"),
    output_dir=Path("output"),
    config=config,
)
```

### Compare with Python Implementation

```python
result = generate_bit_vectors(
    sam_path=Path("aligned.sam"),
    fasta=Path("ref.fasta"),
    output_dir=Path("output"),
    config=config,
    compare_with_python=True,  # Run both and compare
)
```

This will:
1. Run C++ implementation
2. Run Python implementation
3. Compare results
4. Generate comparison report at `output/cpp_python_comparison.json`

## Implementation Details

### C++ Algorithm

The C++ implementation mirrors the Python algorithm:

1. **CIGAR Parsing**: Parses CIGAR strings using regex
2. **Match Operations**: Compares read sequence to reference, applies quality filtering
3. **Deletion Operations**: Handles deletions with ambiguity checking
4. **Insertion Operations**: Skips insertions (advances read position only)
5. **Soft Clips**: Marks as missing information if at end
6. **Paired-End Merging**: Merges bit vectors from paired reads with conflict resolution

### Integration Points

- **SAM Parsing**: Uses existing Python `SingleSamIterator` / `PairedSamIterator`
- **Histogram Generation**: Uses existing Python `BitVectorGenerator` for mutation histogram creation
- **Output**: Uses existing Python code for CSV/JSON/pickle output

## Performance

Expected performance improvements:
- **2-5x faster** for large SAM files
- **Lower memory usage** due to C++ efficiency
- **Better CPU cache utilization**

## Testing

Run comparison tests:

```bash
pytest test/test_bit_vector_cpp.py -v
```

## Troubleshooting

### Module Not Found

If you get `ImportError: No module named 'bit_vector_cpp'`:

1. Ensure pybind11 is installed: `pip install pybind11`
2. Build the module: `cd cpp && python setup.py build_ext --inplace`
3. Check that `lib/rna_map/bit_vector_cpp.*` exists

### Build Errors

- **Compiler not found**: Install C++ compiler (g++, clang++)
- **pybind11 not found**: `pip install pybind11`
- **CMake errors**: Ensure CMake >= 3.12 is installed

### Results Don't Match

If C++ and Python results differ:
1. Check `output/cpp_python_comparison.json` for details
2. Verify C++ code matches Python algorithm (see `lib/rna_map/analysis/bit_vector_iterator.py`)
3. Check for off-by-one errors in position indexing (C++ uses 1-based like Python)

## Future Improvements

- [ ] Add stricter constraints support in C++
- [ ] Optimize CIGAR parsing
- [ ] Add SIMD optimizations for match operations
- [ ] Parallel processing support
- [ ] Memory-mapped file I/O for large SAM files

