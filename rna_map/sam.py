"""SAM file parsing (backward compatibility).

This module re-exports classes from the new io.sam module for backward compatibility.
"""

# Re-export from new io module for backward compatibility
from rna_map.io.sam import (
    AlignedRead,
    PairedSamIterator,
    SingleSamIterator,
    get_aligned_read_from_line,
)

__all__ = [
    "AlignedRead",
    "PairedSamIterator",
    "SingleSamIterator",
    "get_aligned_read_from_line",
]
