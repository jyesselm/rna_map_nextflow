"""Bit vector file I/O operations."""

from pathlib import Path


class BitVectorFileWriter:
    """Writer for bit vector text files."""

    def __init__(
        self, path: Path, name: str, sequence: str, data_type: str, start: int, end: int
    ):
        """Initialize bit vector file writer.

        Args:
            path: Output directory path
            name: Reference sequence name
            sequence: Reference sequence
            data_type: Type of data (e.g., "DMS")
            start: Start position
            end: End position
        """
        self.start = start
        self.end = end
        self.sequence = sequence
        self.f = open(path / Path(name + "_bitvectors.txt"), "w")
        self.f.write(f"@ref\t{name}\t{sequence}\t{data_type}\n")
        self.f.write(f"@coordinates:\t{start},{end}:{len(sequence)}\n")
        self.f.write("Query_name\tBit_vector\tN_Mutations\n")

    def write_bit_vector(self, q_name: str, bit_vector: dict[int, str]) -> None:
        """Write a bit vector to the file.

        Args:
            q_name: Query name (read ID)
            bit_vector: Dictionary mapping positions to bit values
        """
        n_mutations = 0
        bit_string = ""
        for pos in range(self.start, self.end + 1):
            if pos not in bit_vector:
                bit_string += "."
            else:
                read_bit = bit_vector[pos]
                if read_bit.isalpha():
                    n_mutations += 1
                bit_string += read_bit
        self.f.write(f"{q_name}\t{bit_string}\t{n_mutations}\n")


class BitVectorFileReader:
    """Reader for bit vector text files (placeholder for future implementation)."""

    def __init__(self):
        """Initialize bit vector file reader."""
        pass
