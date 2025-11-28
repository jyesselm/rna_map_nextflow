# Storage Format Performance Comparison

This document compares the performance of TEXT vs JSON storage formats for bit vector output.

## Test Results

### Case 1 (Small Dataset: 2,357 bit vectors)

| Format | Write Time | File Size | Throughput | Size per BV |
|--------|------------|-----------|------------|-------------|
| TEXT   | 0.0925s    | 430,173 bytes | 25,468 BV/sec | 182.5 bytes |
| JSON   | 0.1773s    | 273,222 bytes | 13,292 BV/sec | 115.9 bytes |

**Comparison:**
- **Write Speed**: TEXT is **1.92x faster** than JSON
- **File Size**: JSON is **1.57x smaller** than TEXT (36.5% reduction)

### Case 2 (Larger Dataset: 25,318 bit vectors)

| Format | Write Time | File Size | Throughput | Size per BV |
|--------|------------|-----------|------------|-------------|
| TEXT   | 1.1674s    | 4,426,769 bytes | 21,688 BV/sec | 174.8 bytes |
| JSON   | 2.1380s    | 3,725,885 bytes | 11,842 BV/sec | 147.2 bytes |

**Comparison:**
- **Write Speed**: TEXT is **1.83x faster** than JSON
- **File Size**: JSON is **1.19x smaller** than TEXT (15.8% reduction)

## Key Findings

### Write Performance

1. **TEXT format is consistently faster** (~1.8-1.9x) for writing bit vectors
   - Direct string concatenation and file I/O
   - No serialization overhead
   - Simpler format = faster writes

2. **JSON format is slower** due to:
   - Dictionary serialization overhead
   - JSON formatting and escaping
   - More complex data structure handling

### File Size

1. **JSON format produces smaller files** (15-36% reduction)
   - Sparse storage: only stores positions with mutations/deletions/ambiguities
   - More efficient encoding for typical datasets
   - Size advantage is more pronounced for datasets with fewer mutations

2. **TEXT format stores all positions**
   - Includes every position in the sequence (even non-mutated)
   - Uses "." for missing/non-mutated positions
   - Larger files but simpler structure

### Trade-offs

| Aspect | TEXT Format | JSON Format |
|--------|-------------|-------------|
| **Write Speed** | ✅ Faster (1.8-1.9x) | ❌ Slower |
| **File Size** | ❌ Larger | ✅ Smaller (15-36%) |
| **Readability** | ✅ Human-readable | ❌ Requires parsing |
| **Parsing Speed** | ⚠️ Slower (must parse all positions) | ✅ Faster (sparse) |
| **Compatibility** | ✅ Simple text format | ✅ Standard JSON format |
| **Storage Efficiency** | ❌ Stores all positions | ✅ Sparse storage |

## Recommendations

### Use TEXT Format When:
- **Write performance is critical** (e.g., real-time processing)
- **Human readability is important** (debugging, inspection)
- **Simple parsing is sufficient** (one file per reference)
- **File size is not a concern** (small datasets, sufficient storage)

### Use JSON Format When:
- **File size matters** (large datasets, limited storage)
- **Downstream tools expect JSON** (better integration)
- **Sparse storage is beneficial** (few mutations per read)
- **Read/parse performance is more important** than write performance
- **Single file for all references** is preferred

## Performance Scaling

The performance characteristics scale consistently:

- **Write speed ratio** remains ~1.8-1.9x (TEXT faster) across dataset sizes
- **Size reduction** varies with mutation density:
  - High mutation density: ~15-20% reduction
  - Low mutation density: ~30-40% reduction
- **Throughput** decreases slightly with larger datasets (I/O overhead)

## Running Performance Tests

To run the performance comparison yourself:

```bash
# Case 1 (small dataset)
python3 -m pytest test/test_storage_format_performance.py::test_storage_format_performance_case1 -v -s

# Case 2 (larger dataset)
python3 -m pytest test/test_storage_format_performance.py::test_storage_format_performance_case2 -v -s
```

Results are saved to:
- `test/storage_format_performance_case_1.json`
- `test/storage_format_performance_case_2.json`

## Implementation Details

### TEXT Format
- Writes one file per reference: `{ref_name}_bitvectors.txt`
- Format: Tab-separated with header
- Stores every position in sequence (sparse with "." for non-mutated)
- Simple string concatenation for bit vector representation

### JSON Format
- Writes single file: `muts.json`
- Format: JSON array of records
- Stores only positions with mutations/deletions/ambiguities
- Uses `json.dump()` for serialization

## Notes

- Performance results may vary based on:
  - System I/O performance (SSD vs HDD)
  - Python version and optimization
  - Dataset characteristics (read length, mutation density)
  - System load at time of testing

- Both formats preserve all mutation data identically
- Conversion between formats is possible but may lose some metadata

