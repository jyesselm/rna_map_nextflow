"""Analysis module for RNA-MAP.

This module contains classes and functions for analyzing mutation data,
including mutation histograms, bit vector iteration, and statistical calculations.
"""

from .bit_vector_iterator import BitVectorIterator
from .mutation_histogram import MutationHistogram
from .statistics import (
    get_dataframe,
    merge_all_merge_mut_histo_dicts,
    merge_mut_histo_dicts,
)

__all__ = [
    "MutationHistogram",
    "BitVectorIterator",
    "get_dataframe",
    "merge_mut_histo_dicts",
    "merge_all_merge_mut_histo_dicts",
]
