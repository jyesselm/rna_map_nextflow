"""Core bit vector data structures."""

from dataclasses import dataclass

from rna_map.io.sam import AlignedRead


@dataclass(frozen=True, order=True)
class BitVector:
    """Represents a bit vector with associated reads and mutation data.

    Attributes:
        reads: List of aligned reads used to generate this bit vector
        data: Dictionary mapping positions to bit values
    """

    reads: list[AlignedRead]
    data: dict[int, str]


@dataclass(frozen=True, order=True)
class BitVectorSymbols:
    """Symbol definitions for bit vector encoding.

    Attributes:
        miss_info: Symbol for missing information
        ambig_info: Symbol for ambiguous information
        nomut_bit: Symbol for no mutation
        del_bit: Symbol for deletion
    """

    miss_info: str = "*"
    ambig_info: str = "?"
    nomut_bit: str = "0"
    del_bit: str = "1"
