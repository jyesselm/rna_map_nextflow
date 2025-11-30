"""Core data structures and algorithms for RNA MAP.

This module contains core data structures including:
- Input dataclasses
- Bit vector data structures
- Aligned read data structures
- Configuration dataclasses
- Result dataclasses
"""

from rna_map.core.aligned_read import AlignedRead
from rna_map.core.bit_vector import BitVector, BitVectorSymbols
from rna_map.core.config import BitVectorConfig, MappingConfig, StricterConstraints
# from rna_map.core.inputs import Inputs  # Not needed for bit vector generation
from rna_map.core.results import BitVectorResult

__all__ = [
    "AlignedRead",
    "BitVector",
    "BitVectorSymbols",
    "Inputs",
    "MappingConfig",  # Used by CLI for parsing arguments
    "BitVectorConfig",  # Used by Nextflow
    "StricterConstraints",
    "BitVectorResult",  # Used by Nextflow
]
