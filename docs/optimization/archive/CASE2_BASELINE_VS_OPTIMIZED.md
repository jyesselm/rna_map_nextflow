# Case 2: Baseline vs Optimized Parameters Comparison

## Summary

**Key Finding**: Case_2 had a **very low alignment rate (0.92%) even with the original baseline parameters**. The optimized parameters from case_1 (0.96%) did not significantly improve or worsen the alignment rate.

## Results Comparison

### Baseline Parameters
- **Parameters**: `--local --no-unal --no-discordant --no-mixed -X 1000 -L 12`
- **Alignment Rate**: **0.92%**
- **Aligned Reads**: 23 pairs
- **Accepted Bit Vectors**: 23 (all passed MAPQ filter)
- **Signal-to-Noise (AC/GU)**: 2.35

### Optimized Parameters (from case_1)
- **Parameters**: See `best_parameters.txt`
- **Alignment Rate**: **0.96%**
- **Aligned Reads**: 24 pairs
- **Accepted Bit Vectors**: 0 (all rejected due to low MAPQ)
- **Signal-to-Noise (AC/GU)**: 0.00

## Key Insights

1. **Alignment rates are nearly identical**: 0.92% (baseline) vs 0.96% (optimized)
   - Difference is only 0.04%, which is essentially negligible
   - Both are extremely low compared to case_1 (~86-99%)

2. **Baseline parameters actually performed better**:
   - More accepted bit vectors (23 vs 0)
   - Signal-to-noize ratio of 2.35 vs 0.00
   - All aligned reads passed the MAPQ filter

3. **The problem is not parameter-dependent**:
   - Case_2 data has fundamental alignment challenges
   - Parameter optimization cannot fix underlying data issues
   - Low alignment rate persists regardless of parameter settings

## Implications

### What This Means

1. **Case_2 requires dataset-specific optimization**:
   - Parameters optimized for case_1 do not generalize to case_2
   - Need to run optimization directly on case_2 data
   - May need different parameter ranges

2. **Data quality may be the issue**:
   - Low alignment rate suggests reference-read mismatch
   - Possible adapter contamination (observed in reads)
   - Library characteristics may be incompatible

3. **Baseline parameters were actually reasonable**:
   - For case_2, the simple baseline performed as well as complex optimized parameters
   - Less restrictive parameters might actually be better for case_2

### Recommendations

1. **Run case_2-specific optimization**:
   ```bash
   python scripts/optimize_bowtie2_params_optuna.py \
       --fasta test/resources/case_2/C009J.fasta \
       --fastq1 test/resources/case_2/test_R1.fastq.gz \
       --fastq2 test/resources/case_2/test_R2.fastq.gz \
       --n-trials 100 \
       --output-dir case2_optimization
   ```

2. **Investigate data quality**:
   - Check if reference sequence matches reads
   - Verify read quality scores
   - Look for adapter contamination (already observed)
   - Consider adapter trimming before alignment

3. **Try less restrictive parameters**:
   - Increase max insert size (`-X`)
   - Use more sensitive alignment modes
   - Reduce seed length requirements
   - Lower score thresholds

## Test Details

### Baseline Test
- **Script**: `test_baseline_params_case2.py`
- **Reads**: 2,500 (same as case_1)
- **Output**: `case2_baseline_test_results/`

### Optimized Test
- **Script**: `test_best_params_case2.py`
- **Reads**: 2,500 (same as case_1)
- **Output**: `case2_test_results/`

## Conclusion

**Case_2 had a low alignment rate from the beginning.** The optimized parameters from case_1 did not significantly change this. This suggests that:

- Case_2 data has fundamental characteristics that make alignment challenging
- Parameter optimization alone may not be sufficient
- Dataset-specific optimization and data quality investigation are needed

The baseline parameters actually performed slightly better for case_2, producing usable bit vectors with a reasonable signal-to-noise ratio, while the optimized parameters rejected all aligned reads due to MAPQ filtering.

