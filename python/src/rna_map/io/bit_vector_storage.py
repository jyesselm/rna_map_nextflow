"""Bit vector storage abstraction supporting multiple formats."""

import json
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

from rna_map.logger import get_logger

log = get_logger("IO.BIT_VECTOR_STORAGE")


class StorageFormat(str, Enum):
    """Bit vector storage format options."""

    TEXT = "text"  # Original text format (_bitvectors.txt)
    JSON = "json"  # JSON format (muts.json)


class BitVectorStorageWriter(ABC):
    """Abstract base class for bit vector storage writers."""

    @abstractmethod
    def write_bit_vector(
        self, q_name: str, bit_vector: dict[int, str], reads: list[Any]
    ) -> None:
        """Write a bit vector to storage.

        Args:
            q_name: Query name (read ID)
            bit_vector: Dictionary mapping positions to bit values
            reads: List of aligned reads (for metadata)
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the storage writer."""
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class TextStorageWriter(BitVectorStorageWriter):
    """Text format storage writer (original format)."""

    def __init__(
        self,
        path: Path,
        name: str,
        sequence: str,
        data_type: str,
        start: int,
        end: int,
    ) -> None:
        """Initialize text storage writer.

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
        self.file_path = path / Path(name + "_bitvectors.txt")
        self.f = open(self.file_path, "w")
        self.f.write(f"@ref\t{name}\t{sequence}\t{data_type}\n")
        self.f.write(f"@coordinates:\t{start},{end}:{len(sequence)}\n")
        self.f.write("Query_name\tBit_vector\tN_Mutations\n")

    def write_bit_vector(
        self, q_name: str, bit_vector: dict[int, str], reads: list[Any]
    ) -> None:
        """Write bit vector in text format.

        Args:
            q_name: Query name
            bit_vector: Bit vector dictionary
            reads: List of reads (unused in text format)
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

    def close(self) -> None:
        """Close the file."""
        if self.f:
            self.f.close()


class JsonStorageWriter(BitVectorStorageWriter):
    """JSON format storage writer (better_mut_storage format)."""

    def __init__(self, path: Path) -> None:
        """Initialize JSON storage writer.

        Args:
            path: Output directory path
        """
        self.file_path = path / "muts.json"
        self.f = open(self.file_path, "w")
        self.f.write("[")
        self._first = True
        self._bases = ["A", "C", "G", "T"]
        self._del_bit = "1"
        self._ambig_info = "?"

    def write_bit_vector(
        self, q_name: str, bit_vector: dict[int, str], reads: list[Any]
    ) -> None:
        """Write bit vector in JSON format.

        Args:
            q_name: Query name
            bit_vector: Bit vector dictionary
            reads: List of aligned reads (for metadata)
        """
        if not self._first:
            self.f.write(",")
        self._first = False

        muts: dict[int, str] = {}
        dels: dict[int, str] = {}
        ambigs: dict[int, str] = {}

        for pos, bit in bit_vector.items():
            if bit in self._bases:
                muts[int(pos)] = bit
            elif bit == self._del_bit:
                dels[int(pos)] = bit
            elif bit == self._ambig_info:
                ambigs[int(pos)] = bit

        read1 = reads[0] if reads else None
        read2 = reads[1] if len(reads) > 1 else None

        data = [
            read1.rname if read1 else "",
            read1.mapq if read1 else 0,
            read2.mapq if read2 else 0,
            len(read1.seq) if read1 else 0,
            len(read2.seq) if read2 else 0,
            muts,
            dels,
            ambigs,
        ]
        json.dump(data, self.f)

    def close(self) -> None:
        """Close the file."""
        if self.f:
            self.f.write("]")
            self.f.close()


def create_storage_writer(
    format_type: StorageFormat,
    path: Path,
    name: str = "",
    sequence: str = "",
    data_type: str = "DMS",
    start: int = 1,
    end: int = 1,
) -> BitVectorStorageWriter:
    """Create a storage writer for the specified format.

    Args:
        format_type: Storage format to use
        path: Output directory path
        name: Reference sequence name (required for TEXT format)
        sequence: Reference sequence (required for TEXT format)
        data_type: Type of data (required for TEXT format)
        start: Start position (required for TEXT format)
        end: End position (required for TEXT format)

    Returns:
        BitVectorStorageWriter instance
    """
    if format_type == StorageFormat.TEXT:
        return TextStorageWriter(path, name, sequence, data_type, start, end)
    elif format_type == StorageFormat.JSON:
        return JsonStorageWriter(path)
    else:
        raise ValueError(f"Unknown storage format: {format_type}")

