#!/bin/bash
# Run case_2 optimization with the same number of reads as case_1

conda activate rna-map-optuna

python scripts/optimize_bowtie2_params_optuna.py \
    --fasta test/resources/case_2/C009J.fasta \
    --fastq1 test/resources/case_2/test_R1.fastq.gz \
    --fastq2 test/resources/case_2/test_R2.fastq.gz \
    --n-trials 200 \
    --threads 8 \
    --output-dir case2_optimization \
    --study-name "case2_bowtie2_optimization"

