#!/bin/bash
#SBATCH --job-name=rna_map_test
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --output=test_job_local_%j.out
#SBATCH --error=test_job_local_%j.err

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Change to project directory
cd ${SLURM_SUBMIT_DIR:-/work/yesselmanlab/jyesselm/installs/rna_map_nextflow}

# Run Nextflow with slurm_local profile
# This uses local executor within the SLURM job to reduce overhead
nextflow run main.nf \
    -profile slurm_local \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_job_local \
    --skip_fastqc \
    --skip_trim_galore \
    --max_cpus 4 \
    -with-report test_report_job_local.html \
    -with-trace test_trace_job_local.txt \
    -with-dag test_dag_job_local.html

echo "Test completed. Check test_results_job_local/ for outputs."

