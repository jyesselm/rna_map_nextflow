# Implementation Performance Comparison

This document summarizes the runtime performance of the three implementations:
1. **Python Native** - Original Python implementation with native SAM parsing
2. **C++** - C++ implementation with pybind11 bindings
3. **pysam** - Python implementation using pysam library for SAM parsing

## Test Results

### Case 1 (Small Dataset: 2,357 reads)

| Implementation | Runtime (seconds) | Reads/sec | Speedup vs Python Native |
|----------------|-------------------|-----------|---------------------------|
| Python Native  | 0.07s             | 33,950    | 1.00x (baseline)          |
| C++            | 0.07s             | 31,632    | 0.93x                     |
| pysam          | 0.08s             | 31,272    | 0.92x                     |

### Case 2 (Larger Dataset: 25,318 reads)

| Implementation | Runtime (seconds) | Reads/sec | Speedup vs Python Native |
|----------------|-------------------|-----------|---------------------------|
| Python Native  | 0.72s             | 35,158    | 1.00x (baseline)          |
| C++            | 0.77s             | 32,994    | 0.94x                     |
| pysam          | 0.80s             | 31,735    | 0.90x                     |

## Key Observations

1. **All implementations produce identical results** - The correctness is verified across all three methods.

2. **Python Native is slightly faster** - The native Python implementation shows the best performance in these tests. This is likely due to:
   - Lower overhead (no pybind11 or pysam initialization costs)
   - Well-optimized Python code for this specific use case
   - Small dataset sizes where overhead dominates

3. **C++ performance** - The C++ implementation is slightly slower than Python native, likely due to:
   - pybind11 overhead when calling from Python
   - Data conversion costs between Python and C++
   - For larger datasets, C++ would likely show better performance

4. **pysam performance** - The pysam implementation is slightly slower, likely due to:
   - Library initialization overhead
   - Additional abstraction layers
   - However, pysam provides better robustness and BAM file support

## Performance Considerations

### When to Use Each Implementation

- **Python Native**: Best for small to medium datasets where simplicity and speed are priorities
- **C++**: Best for very large datasets where computational efficiency becomes critical
- **pysam**: Best when you need BAM file support, better error handling, or compatibility with other pysam-based tools

### Scaling Expectations

For very large datasets (millions of reads), we expect:
- **C++** to show the best performance due to compiled code efficiency
- **pysam** to maintain consistent performance with better memory management
- **Python Native** to remain competitive but may show memory pressure on very large files

## Running Performance Tests

To run the performance comparison yourself:

```bash
# Case 1 (small dataset)
python3 test/test_all_implementations_comparison.py case1

# Case 2 (larger dataset)
python3 test/test_all_implementations_comparison.py case2
```

The test will output:
- Total and aligned read counts
- Mutation distribution
- Runtime for each implementation
- Speedup comparisons
- Reads per second throughput

## Notes

- Performance results may vary based on:
  - System hardware (CPU, memory, I/O)
  - Python version and optimization flags
  - Dataset characteristics (read length, CIGAR complexity)
  - System load at time of testing

- All implementations are functionally equivalent and produce identical results.

