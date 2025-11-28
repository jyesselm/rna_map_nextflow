#!/bin/bash
#SBATCH --job-name=rna_map_test
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --output=test_job_%j.out
#SBATCH --error=test_job_%j.err

# Activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Change to project directory
cd ${SLURM_SUBMIT_DIR:-/work/yesselmanlab/jyesselm/installs/rna_map_nextflow}

# Install Python package (ensures lib/ is available without PYTHONPATH)
pip install -e . --quiet

# Optional: Use container if available
# CONTAINER_PATH="/path/to/rna-map.sif"
# if [ -f "$CONTAINER_PATH" ]; then
#     PROFILE="slurm_singularity"
#     CONTAINER_ARG="--container_path $CONTAINER_PATH"
# else
#     PROFILE="slurm"
#     CONTAINER_ARG=""
# fi

# Run Nextflow with minimal test (skip QC steps for speed)
nextflow run main.nf \
    -profile slurm \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_job \
    --skip_fastqc \
    --skip_trim_galore \
    --max_cpus 4 \
    -with-report test_report_job.html \
    -with-trace test_trace_job.txt \
    -with-dag test_dag_job.html

echo "Test completed. Check test_results_job/ for outputs."

