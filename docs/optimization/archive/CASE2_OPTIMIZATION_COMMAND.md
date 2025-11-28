# Case 2 Optimization Command

## Quick Start Command

```bash
conda activate rna-map-optuna

python scripts/optimize_bowtie2_params_optuna.py \
    --fasta test/resources/case_2/C009J.fasta \
    --fastq1 test/resources/case_2/test_R1.fastq.gz \
    --fastq2 test/resources/case_2/test_R2.fastq.gz \
    --n-trials 200 \
    --threads 8 \
    --output-dir case2_optimization \
    --study-name "case2_bowtie2_optimization"
```

## Or Use the Script

```bash
./RUN_CASE2_OPTIMIZATION.sh
```

## Command Breakdown

- `--fasta test/resources/case_2/C009J.fasta` - Case 2 reference sequence
- `--fastq1 test/resources/case_2/test_R1.fastq.gz` - Case 2 R1 reads (gzipped)
- `--fastq2 test/resources/case_2/test_R2.fastq.gz` - Case 2 R2 reads (gzipped)
- `--n-trials 200` - Number of optimization trials (same as case_1)
- `--threads 8` - Number of threads for alignment
- `--output-dir case2_optimization` - Output directory
- `--study-name "case2_bowtie2_optimization"` - Unique study name

## Notes

- Bowtie2 can read gzipped FASTQ files directly (no need to decompress)
- Uses the same number of trials (200) as case_1 for fair comparison
- Will explore all 17 parameters we added
- Expected runtime: 1-3 hours depending on system

## After Optimization

1. Analyze top parameters:
   ```bash
   python analyze_top_parameters.py case2_optimization/optuna_summary.csv --top-n 100
   ```

2. Compare with case_1:
   - Check which parameters differ
   - See if any constants are different

3. Use optimal parameters for case_2 data

