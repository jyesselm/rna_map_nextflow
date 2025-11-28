# C++ Bit Vector Generation

This directory contains a C++ implementation of bit vector generation with pybind11 bindings for Python integration.

## Building

### Prerequisites
- C++17 compatible compiler (g++, clang++)
- CMake >= 3.12
- pybind11 >= 2.10
- Python 3.10+

### Build Instructions

1. Install pybind11:
```bash
pip install pybind11
```

2. Build the module:
```bash
cd cpp
python setup.py build_ext --inplace
```

Or use the build script:
```bash
./cpp/build.sh
```

The compiled module will be placed in `lib/rna_map/bit_vector_cpp.*` (`.so` on Linux, `.dylib` on macOS, `.pyd` on Windows).

## Usage

The C++ implementation can be enabled by setting `use_cpp=True` in `BitVectorConfig`:

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
    compare_with_python=True,  # Compare results with Python version
)
```

## Comparison

When `compare_with_python=True`, the function will:
1. Run the C++ implementation
2. Run the Python implementation
3. Compare the results
4. Generate a comparison report at `output/cpp_python_comparison.json`

## Implementation Details

The C++ implementation:
- Parses CIGAR strings to process alignments
- Handles match/mismatch, deletions, insertions, and soft clips
- Applies quality score filtering
- Merges paired-end reads
- Checks for ambiguous deletions

The Python SAM parsing is reused, so the C++ code focuses on the computationally intensive bit vector generation.

## Performance

The C++ implementation is expected to be 2-5x faster than the Python version for large SAM files, especially when processing many reads.

