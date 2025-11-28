# CIGAR Parsing Fixes - Impact Analysis

## Summary

Fixed CIGAR string parsing in the C++ implementation to correctly handle all valid SAM CIGAR operations according to the SAM specification.

## Changes Made

### 1. Fixed Regex Pattern
- **Before**: `R"((\d+)([A-Z]))"` - Accepted any uppercase letter
- **After**: `R"((\d+)([MIDNSHPX=]))"` - Only accepts valid CIGAR operations

### 2. Added Missing CIGAR Operations
- **Before**: Only handled `M`, `D`, `I`, `S`
- **After**: Now handles all valid operations:
  - `M` - Match or mismatch (consumes both reference and read)
  - `=` - Sequence match (consumes both)
  - `X` - Sequence mismatch (consumes both)
  - `D` - Deletion (consumes reference only)
  - `N` - Skipped region (consumes reference only, similar to deletion)
  - `I` - Insertion (consumes read only)
  - `S` - Soft clipping (consumes read only)
  - `H` - Hard clipping (consumes nothing, skipped)
  - `P` - Padding (consumes nothing, skipped)

### 3. Added Validation
- Empty CIGAR strings (`""` or `"*"`) are handled gracefully
- Operations with zero or negative lengths are filtered out
- Better error handling for malformed CIGAR strings

## Impact on Results

### Will Results Change?

**For existing test data: NO CHANGE expected**

The test data (`test/resources/case_1/`) only contains CIGAR strings with operations that were already handled:
- `134M12S` - Match and soft clip
- `80M1D53M12S` - Match, deletion, match, soft clip
- `43M1I91M12S` - Match, insertion, match, soft clip

All of these operations (`M`, `D`, `I`, `S`) were already correctly handled.

### When Results WILL Change

Results will change if your data contains:
1. **`N` (skipped region)**: Previously ignored, now processed as deletion
2. **`=` (sequence match)**: Previously ignored, now processed as match
3. **`X` (sequence mismatch)**: Previously ignored, now processed as match
4. **`H` (hard clipping)**: Previously ignored, now explicitly skipped (no change in behavior)
5. **`P` (padding)**: Previously ignored, now explicitly skipped (no change in behavior)

### Edge Cases

- **Invalid characters**: Previously might have been parsed incorrectly, now rejected
- **Malformed CIGAR strings**: Better handling, returns empty vector instead of crashing

## Verification

### 1. Run CIGAR Parsing Tests

```bash
pytest test/test_cigar_parsing.py -v
```

This will test:
- All valid CIGAR operations parse correctly
- Invalid operations are handled gracefully
- Real test data parses without errors

### 2. Compare C++ vs Python Implementation

```bash
pytest test/test_bit_vector_cpp.py::test_cpp_vs_python_comparison -v
```

This will:
- Run both C++ and Python implementations
- Compare results
- Generate comparison report at `test_output_cpp_comparison/cpp_python_comparison.json`

### 3. Compare Before/After Results

If you want to compare results before and after the fix:

```bash
# 1. Generate baseline (before fix - if you have old code)
# Save output to baseline_output/

# 2. Generate new results (after fix)
# Save output to new_output/

# 3. Compare
python test/compare_outputs.py baseline_output new_output
```

### 4. Test with Real Data

```python
from rna_map.core.config import BitVectorConfig
from rna_map.pipeline.functions import generate_bit_vectors
from pathlib import Path

config = BitVectorConfig(
    qscore_cutoff=25,
    num_of_surbases=10,
    map_score_cutoff=15,
    use_cpp=True,
)

result = generate_bit_vectors(
    sam_path=Path("your_data.sam"),
    fasta=Path("your_ref.fasta"),
    output_dir=Path("output"),
    config=config,
    compare_with_python=True,  # Compare with Python version
)
```

## SAM Specification Reference

According to the SAM specification, valid CIGAR operations are:

| Operation | Description | Consumes Reference | Consumes Read |
|-----------|-------------|-------------------|---------------|
| `M` | Match or mismatch | Yes | Yes |
| `=` | Sequence match | Yes | Yes |
| `X` | Sequence mismatch | Yes | Yes |
| `I` | Insertion | No | Yes |
| `D` | Deletion | Yes | No |
| `N` | Skipped region | Yes | No |
| `S` | Soft clipping | No | Yes |
| `H` | Hard clipping | No | No |
| `P` | Padding | No | No |

## Recommendations

1. **For existing pipelines**: No action needed if your data only uses `M`, `D`, `I`, `S`
2. **For new data**: The fix ensures all valid CIGAR operations are handled correctly
3. **For validation**: Run the comparison tests to verify results match Python implementation

## Testing Checklist

- [x] All valid CIGAR operations parse correctly
- [x] Invalid operations are handled gracefully
- [x] Empty CIGAR strings handled
- [x] Real test data parses without errors
- [ ] Compare C++ vs Python results (run test)
- [ ] Verify no regressions in existing test data

