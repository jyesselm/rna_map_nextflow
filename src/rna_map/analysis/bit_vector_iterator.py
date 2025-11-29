"""Bit vector iterator for generating bit vectors from SAM files."""

from pathlib import Path
import re

from rna_map import settings
from rna_map.core.bit_vector import BitVector, BitVectorSymbols
from rna_map.io.fastq import parse_phred_qscore_file
from rna_map.io.sam import (
    AlignedRead,
    PairedSamIterator,
    SingleSamIterator,
)
from rna_map.logger import get_logger

log = get_logger("BIT_VECTOR")


class BitVectorIterator:
    """Generate bit vectors from SAM files.

    Does minimal checking to ensure the bitvector is acceptable.
    """

    def __init__(
        self,
        sam_path: Path | str,
        ref_seqs: dict[str, str],
        paired: bool,
        qscore_cutoff: int = 25,
        num_of_surbases: int = 10,
        use_pysam: bool = False,
    ) -> None:
        """Initialize BitVectorIterator.

        Args:
            sam_path: Path to SAM file
            ref_seqs: Dictionary of reference sequences
            paired: Whether reads are paired-end
            qscore_cutoff: Quality score cutoff (default: 25)
            num_of_surbases: Number of surrounding bases for ambiguity check
            use_pysam: If True, use pysam for SAM parsing (faster, more robust)
        """
        sam_path_str = str(sam_path)
        if paired:
            self.__sam_iterator: PairedSamIterator | SingleSamIterator = (
                PairedSamIterator(sam_path_str, ref_seqs, use_pysam=use_pysam)
            )
        else:
            self.__sam_iterator = SingleSamIterator(sam_path_str, ref_seqs, use_pysam=use_pysam)
        self.count = 0
        self.rejected = 0
        self.__ref_seqs = ref_seqs
        self.__paired = paired
        self.__cigar_pattern = re.compile(r"(\d+)([A-Z]{1})")
        self.__phred_qscores = parse_phred_qscore_file(
            settings.get_py_path() / "resources" / "phred_ascii.txt"
        )
        self.__bases = ["A", "C", "G", "T"]
        self.__qscore_cutoff = qscore_cutoff
        self.__num_of_surbases = num_of_surbases
        self.__bts = BitVectorSymbols()

    def __iter__(self):
        """Return iterator."""
        return self

    def __next__(self):
        """Get next bit vector.

        Returns:
            BitVector object

        Raises:
            StopIteration: When no more reads
            ValueError: If read aligned to unknown reference
        """
        self.count += 1
        reads = next(self.__sam_iterator)
        for read in reads:
            if read.rname not in self.__ref_seqs:
                raise ValueError(
                    f"read {read.qname} aligned to {read.rname} which is not in "
                    "the reference fasta"
                )
        if self.__paired:
            data = self.__get_bit_vector_paired(reads[0], reads[1])
        else:
            data = self.__get_bit_vector_single(reads[0])
        return BitVector(reads, data)

    def __get_bit_vector_single(self, read: AlignedRead) -> dict[int, str]:
        """Generate bit vector for single-end read.

        Args:
            read: AlignedRead object

        Returns:
            Dictionary mapping position to bit value
        """
        ref_seq = self.__ref_seqs[read.rname]
        bit_vector = self.__convert_read_to_bit_vector(read, ref_seq)
        return bit_vector

    def __convert_read_to_bit_vector(
        self, read: AlignedRead, ref_seq: str
    ) -> dict[int, str]:
        """Convert read to bit vector.

        Args:
            read: AlignedRead object
            ref_seq: Reference sequence

        Returns:
            Dictionary mapping position to bit value
        """
        bitvector: dict[int, str] = {}
        read_seq = read.seq
        q_scores = read.qual
        i = read.pos
        j = 0
        cigar_ops = self._parse_cigar(read.cigar)
        op_index = 0
        while op_index < len(cigar_ops):
            op = cigar_ops[op_index]
            desc, length = op[1], int(op[0])
            if desc == "M":
                i, j = self._process_match_operation(
                    bitvector, read_seq, q_scores, ref_seq, i, j, length
                )
            elif desc == "D":
                i = self._process_deletion_operation(bitvector, ref_seq, i, length)
            elif desc == "I":
                j += length
            elif desc == "S":
                i, j = self._process_soft_clip_operation(
                    bitvector, i, j, length, op_index, len(cigar_ops)
                )
            else:
                log.warn(f"unknown cigar op encounters: {desc}")
                return {}
            op_index += 1
        return bitvector

    def _process_match_operation(
        self,
        bitvector: dict[int, str],
        read_seq: str,
        q_scores: str,
        ref_seq: str,
        i: int,
        j: int,
        length: int,
    ) -> tuple[int, int]:
        """Process match/mismatch CIGAR operation.

        Args:
            bitvector: Bit vector dictionary to update
            read_seq: Read sequence
            q_scores: Quality scores
            ref_seq: Reference sequence
            i: Reference position
            j: Read position
            length: Operation length

        Returns:
            Tuple of (new_i, new_j) positions
        """
        for _ in range(length):
            if self.__phred_qscores[q_scores[j]] > self.__qscore_cutoff:
                if read_seq[j] != ref_seq[i - 1]:
                    bitvector[i] = read_seq[j]
                else:
                    bitvector[i] = self.__bts.nomut_bit
            else:
                bitvector[i] = self.__bts.ambig_info
            i += 1
            j += 1
        return i, j

    def _process_deletion_operation(
        self, bitvector: dict[int, str], ref_seq: str, i: int, length: int
    ) -> int:
        """Process deletion CIGAR operation.

        Args:
            bitvector: Bit vector dictionary to update
            ref_seq: Reference sequence
            i: Reference position
            length: Deletion length

        Returns:
            New reference position
        """
        for _ in range(length - 1):
            bitvector[i] = self.__bts.ambig_info
            i += 1
        is_ambig = self.__calc_ambig_reads(ref_seq, i, length)
        if is_ambig:
            bitvector[i] = self.__bts.ambig_info
        else:
            bitvector[i] = self.__bts.del_bit
        i += 1
        return i

    def _process_soft_clip_operation(
        self,
        bitvector: dict[int, str],
        i: int,
        j: int,
        length: int,
        op_index: int,
        total_ops: int,
    ) -> tuple[int, int]:
        """Process soft clip CIGAR operation.

        Args:
            bitvector: Bit vector dictionary to update
            i: Reference position
            j: Read position
            length: Clip length
            op_index: Current operation index
            total_ops: Total number of operations

        Returns:
            Tuple of (new_i, new_j) positions
        """
        j += length
        if op_index == total_ops - 1:
            for _ in range(length):
                bitvector[i] = self.__bts.miss_info
                i += 1
        return i, j

    def __get_bit_vector_paired(
        self, read_1: AlignedRead, read_2: AlignedRead
    ) -> dict[int, str]:
        """Generate bit vector for paired-end reads.

        Args:
            read_1: First AlignedRead
            read_2: Second AlignedRead

        Returns:
            Dictionary mapping position to bit value
        """
        ref_seq = self.__ref_seqs[read_1.rname]
        bit_vector_1 = self.__convert_read_to_bit_vector(read_1, ref_seq)
        bit_vector_2 = self.__convert_read_to_bit_vector(read_2, ref_seq)
        bit_vector = self.__merge_paired_bit_vectors(bit_vector_1, bit_vector_2)
        return bit_vector

    def _parse_cigar(self, cigar_string: str) -> list[tuple[str, ...]]:
        """Parse CIGAR string.

        Args:
            cigar_string: CIGAR string

        Returns:
            List of (length, operation) tuples
        """
        return re.findall(self.__cigar_pattern, cigar_string)

    def __calc_ambig_reads(self, ref_seq: str, i: int, length: int) -> bool:
        """Calculate if deletion is ambiguous.

        Args:
            ref_seq: Reference sequence
            i: Position
            length: Deletion length

        Returns:
            True if ambiguous, False otherwise
        """
        orig_del_start = i - length + 1
        orig_sur_start = orig_del_start - self.__num_of_surbases
        orig_sur_end = i + self.__num_of_surbases
        orig_sur_seq = (
            ref_seq[orig_sur_start - 1 : orig_del_start - 1] + ref_seq[i:orig_sur_end]
        )
        for new_del_end in range(i - length, i + length + 1):
            if new_del_end == i:
                continue
            new_del_start = new_del_end - length + 1
            sur_seq = (
                ref_seq[orig_sur_start - 1 : new_del_start - 1]
                + ref_seq[new_del_end:orig_sur_end]
            )
            if sur_seq == orig_sur_seq:
                return True
        return False

    def __merge_paired_bit_vectors(
        self, bit_vector_1: dict[int, str], bit_vector_2: dict[int, str]
    ) -> dict[int, str]:
        """Merge two bit vectors from paired reads.

        Args:
            bit_vector_1: First bit vector
            bit_vector_2: Second bit vector

        Returns:
            Merged bit vector
        """
        bit_vector = dict(bit_vector_1)
        for pos, bit in bit_vector_2.items():
            if pos not in bit_vector:
                bit_vector[pos] = bit
            elif bit != bit_vector[pos]:
                bit_vector[pos] = self._resolve_bit_conflict(bit_vector_1[pos], bit)
        return bit_vector

    def _resolve_bit_conflict(self, bit1: str, bit2: str) -> str:
        """Resolve conflict between two different bit values.

        Args:
            bit1: First bit value
            bit2: Second bit value

        Returns:
            Resolved bit value
        """
        bits = {bit1, bit2}
        if self.__bts.nomut_bit in bits:
            return self.__bts.nomut_bit
        if self.__bts.ambig_info in bits:
            return list(bits - set(self.__bts.ambig_info))[0]
        if self.__bts.miss_info in bits:
            return list(bits - set(self.__bts.miss_info))[0]
        if bit1 in self.__bases and bit2 in self.__bases:
            return self.__bts.ambig_info
        if self._is_mutation_vs_deletion(bit1, bit2):
            return self.__bts.ambig_info
        log.warn(f"unable to merge bit_vectors with bits: {bit1} {bit2}")
        return bit1

    def _is_mutation_vs_deletion(self, bit1: str, bit2: str) -> bool:
        """Check if one bit is mutation and other is deletion.

        Args:
            bit1: First bit value
            bit2: Second bit value

        Returns:
            True if one is mutation and other is deletion
        """
        return (
            bit1 == self.__bts.del_bit
            and bit2 in self.__bases
            or bit1 in self.__bases
            and bit2 == self.__bts.del_bit
        )
