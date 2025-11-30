"""Pipeline components for RNA MAP.

This module contains components used by the Nextflow workflow:
- BitVectorGenerator for mutation analysis (class-based API)
- Functional APIs for stateless, composable pipeline execution (used by Nextflow)
- Simple pipeline for demultiplexing FASTQ files
"""

from rna_map.pipeline.bit_vector_generator import BitVectorGenerator
from rna_map.pipeline.functions import generate_bit_vectors

try:
    from rna_map.pipeline.simple_pipeline import (
        Sample,
        demultiplex_fastq,
    )
    _simple_pipeline_available = True
except ImportError:
    _simple_pipeline_available = False

# Dask pipeline removed - use Nextflow workflow instead
_dask_pipeline_available = False

__all__ = [
    "BitVectorGenerator",
    "generate_bit_vectors",  # Used by Nextflow
]

if _simple_pipeline_available:
    __all__.extend([
        "Sample",
        "demultiplex_fastq",
    ])

# Dask pipeline exports removed - use Nextflow workflow instead
