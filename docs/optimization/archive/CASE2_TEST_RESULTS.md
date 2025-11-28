# Case 2 Test Results with Best Parameters

## Test Configuration

- **Parameters**: Best parameters from case_1 optimization
- **Reads**: 2,500 reads (same as case_1)
- **Reference**: `test/resources/case_2/C009J.fasta`
- **Input**: `test/resources/case_2/test_R1.fastq.gz` and `test_R2.fastq.gz`

## Results Summary

### Alignment Statistics
- **Total reads**: 2,500
- **Overall alignment rate**: 0.96% ⚠️
- **Aligned exactly 1 time**: 2 pairs
- **Aligned >1 times**: 0 pairs
- **Unaligned**: 2,477 pairs (99.08%)

### Bit Vector Metrics
- **Total bit vectors**: 5
- **Accepted bit vectors**: 0
- **Rejected (low MAPQ)**: 5
- **Signal-to-Noise (AC/GU)**: 0.00

## Analysis

### Key Finding: Very Low Alignment Rate

The parameters optimized for case_1 **do not work well** for case_2 data:

1. **Alignment rate is extremely low** (0.96% vs ~86-99% for case_1)
2. **All aligned reads were rejected** due to low MAPQ scores
3. **No signal-to-noise data** could be calculated (no accepted reads)

### Baseline Parameters Comparison

**Important discovery**: Case_2 had a **very low alignment rate even with the original baseline parameters**!

| Parameters | Alignment Rate | Aligned Reads | Accepted Bit Vectors | Signal-to-Noise |
|------------|----------------|---------------|----------------------|-----------------|
| **Baseline** (`--local --no-unal --no-discordant --no-mixed -X 1000 -L 12`) | **0.92%** | 23 | 23 | 2.35 |
| **Optimized (case_1)** | **0.96%** | 24 | 0 | 0.00 |

**Key insights**:
- Both baseline and optimized parameters show nearly identical alignment rates (~0.92-0.96%)
- The optimized parameters **did not make case_2 worse** - it was already problematic
- Baseline parameters actually produced **more accepted bit vectors** (23 vs 0) with a signal-to-noise ratio of 2.35
- The optimized parameters rejected all aligned reads due to low MAPQ scores

**Conclusion**: Case_2 data has fundamental alignment challenges that are **not parameter-dependent**. The low alignment rate suggests:
- Reference sequence may not match the read sequences well
- Data may have quality issues
- Library characteristics may be incompatible with the reference

### Possible Reasons

1. **Different sequence characteristics**: Case_2 reference sequence may be very different
2. **Different library preparation**: Read characteristics may differ
3. **Read quality**: Case_2 reads may have different quality profiles
4. **Parameter mismatch**: Optimal parameters for case_1 may not suit case_2

### Observations

Looking at the reads:
- Reads start with `GTTGTTGTTGTTGTTTCTTT...` - specific pattern
- Reference is `ade_riboswitch` sequence
- Reads appear to have adapter sequences (`ATCGGAAGAGC...`)

The very low alignment rate suggests:
- Parameters may be too restrictive for this data
- Reference sequence may not match read sequences well
- Data may need different optimization

## Recommendations

### 1. Case_2 Needs Its Own Optimization

Case_2 data appears to be fundamentally different from case_1. You should:
- Run full optimization on case_2 data
- Compare optimal parameters between case_1 and case_2
- Identify which parameters differ and why

### 2. Try Less Restrictive Parameters

As a quick test, try:
- Increase `-X` (max insert size) from 200 to 500-1000
- Reduce seed length `-L` from 18 to 12-16
- Use more sensitive mode (try `--sensitive-local` instead of `--fast-local`)
- Reduce `--score-min` threshold

### 3. Check Data Quality

Before re-optimizing, verify:
- Reference sequence matches the reads
- Read quality is acceptable
- No adapter contamination (already see adapters in reads)
- Library type matches expected configuration

## Next Steps

1. **Run optimization on case_2**: Use the optimization script on case_2 data
2. **Compare parameters**: Identify differences between case_1 and case_2 optimal parameters
3. **Check data**: Verify reference sequence and read compatibility
4. **Consider data preprocessing**: May need adapter trimming or quality filtering

## Command to Test Less Restrictive Parameters

```bash
# Try with less restrictive settings
bowtie2 \
    --local --no-unal --no-discordant --no-mixed \
    -L 12 -X 500 -N 1 \
    --score-min L,0,0.2 \
    --mp 6,2 \
    --rdg 8,4 --rfg 5,3 \
    --sensitive-local \
    -i S,1,1.15 \
    --np 2 --n-ceil L,0,0.3 \
    --gbar 6 --ma 0 \
    -D 15 -R 4 -I 50 \
    -x index \
    -1 test_R1.fastq -2 test_R2.fastq \
    -S output.sam
```

## Conclusion

**The best parameters from case_1 do not work for case_2.** Case_2 requires its own parameter optimization. The extremely low alignment rate (0.96%) indicates the data characteristics are significantly different.

