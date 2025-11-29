FROM continuumio/miniconda3:latest

# Install system dependencies
RUN apt-get update && apt-get install -y \
        build-essential \
        wget \
        curl \
        git \
        && rm -rf /var/lib/apt/lists/*

# Copy environment file and package source
COPY environment_optuna.yml /opt/environment_optuna.yml
COPY src/rna_map /opt/src/rna_map

# Create conda environment from environment_optuna.yml
RUN /opt/conda/bin/conda env create -f /opt/environment_optuna.yml -n rna-map-optimization

# Activate environment and install rna_map package
RUN . /opt/conda/etc/profile.d/conda.sh && \
        conda activate rna-map-optimization && \
        cd /opt/src/rna_map && \
        pip install -e .

# Clean up conda cache
RUN /opt/conda/bin/conda clean -afy

# Create directories for data and results
RUN mkdir -p /data /results /work

# Set working directory
WORKDIR /work

# Default command
CMD ["/opt/conda/envs/rna-map-optimization/bin/python"]

