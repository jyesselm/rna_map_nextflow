#!/bin/bash
#SBATCH --job-name=rna_map_test_singularity
#SBATCH --time=2:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=16G
#SBATCH --output=test_job_singularity_%j.out
#SBATCH --error=test_job_singularity_%j.err

# Activate conda environment (for Nextflow only, tools run in container)
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rna-map-nextflow

# Change to project directory
cd ${SLURM_SUBMIT_DIR:-/work/yesselmanlab/jyesselm/installs/rna_map_nextflow}

# Set container path (adjust to your cluster's location)
# Common locations: /path/to/containers/, $HOME/containers/, or shared storage
CONTAINER_PATH="${CONTAINER_PATH:-${PWD}/rna-map.sif}"

# Check if container exists
if [ ! -f "$CONTAINER_PATH" ]; then
    echo "WARNING: Container not found at $CONTAINER_PATH"
    echo "Please build the container first:"
    echo "  ./scripts/build_singularity.sh $CONTAINER_PATH"
    echo ""
    echo "Or set CONTAINER_PATH environment variable to point to your container"
    exit 1
fi

# Run Nextflow with Singularity/Apptainer container
# This uses containers for all processes - no need to install packages!
nextflow run main.nf \
    -profile slurm_singularity \
    --container_path "$CONTAINER_PATH" \
    --fasta test/resources/case_1/test.fasta \
    --fastq1 test/resources/case_1/test_mate1.fastq \
    --fastq2 test/resources/case_1/test_mate2.fastq \
    --dot_bracket test/resources/case_1/test.csv \
    --output_dir test_results_job_singularity \
    --skip_fastqc \
    --skip_trim_galore \
    --max_cpus 4 \
    -with-report test_report_job_singularity.html \
    -with-trace test_trace_job_singularity.txt \
    -with-dag test_dag_job_singularity.html

echo "Test completed. Check test_results_job_singularity/ for outputs."

