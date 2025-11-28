FROM mambaorg/micromamba:latest
SHELL ["/bin/bash", "-lc"]
USER root

# Create your data directories
RUN mkdir -p /data /data2 /data3 /data4

# Copy environment spec
COPY environment.yml /tmp/environment.yml

# Install everything into the *base* environment
# Using --yes (-y) and --strict-channel-priority ensures Bioconda/Conda-Forge order
RUN micromamba install -y -n base -f /tmp/environment.yml --strict-channel-priority \
 && micromamba clean -a -y

# Ensure base is first on PATH (usually already true, but explicit here)
ENV PATH=/opt/conda/bin:$PATH

# Copy your source code and install your package into base
WORKDIR /opt/rna_map
COPY . /opt/rna_map
RUN pip install -e . \
 && python -c "from lib.bit_vectors import generate_bit_vectors; print('✅ lib package installed')" || true

# Optional: simple sanity check (nonfatal)
RUN set -eux; \
  for exe in bowtie2 fastqc cutadapt trim_galore; do \
    command -v "$exe" || echo "MISS: $exe"; \
  done; \
  true

# Set working directory for Nextflow
WORKDIR /data