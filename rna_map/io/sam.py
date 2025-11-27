"""SAM file parsing utilities."""

from dataclasses import dataclass

from rna_map.logger import get_logger

log = get_logger("IO.SAM")


@dataclass(frozen=True, order=True)
class AlignedRead:
    """Represents an aligned read from a SAM file."""

    qname: str
    flag: str
    rname: str
    pos: int
    mapq: int
    cigar: str
    rnext: str
    pnext: int
    tlen: int
    seq: str
    qual: str
    md_string: str


def get_aligned_read_from_line(line: str) -> AlignedRead:
    """Get an AlignedRead object from a line of a SAM file.

    Args:
        line: A line from a SAM file

    Returns:
        AlignedRead object

    Raises:
        ValueError: If line doesn't have enough fields
    """
    spl = line.split()
    if len(spl) < 11:
        raise ValueError("cannot setup AlignRead object from split, its too short")
    return AlignedRead(
        spl[0],
        spl[1],
        spl[2],
        int(spl[3]),
        int(spl[4]),
        spl[5],
        spl[6],
        int(spl[7]),
        int(spl[8]),
        spl[9],
        spl[10],
        spl[11].split(":")[2],
    )


class SamIterator:
    """Base iterator for SAM files."""

    def __init__(self, samfile_path: str):
        """Initialize SAM iterator.

        Args:
            samfile_path: Path to SAM file
        """
        self._f = open(samfile_path)
        self._good = True

    def get_next(self):
        """Get next read (not implemented in base class)."""
        pass

    def is_good(self) -> bool:
        """Check if iterator is still valid."""
        return self._good


class SingleSamIterator:
    """Iterator for single-end SAM files."""

    def __init__(self, samfile_path: str, ref_seqs: dict[str, str]):
        """Initialize single-end SAM iterator.

        Args:
            samfile_path: Path to SAM file
            ref_seqs: Dictionary of reference sequences
        """
        self._f = open(samfile_path)
        ignore_lines = len(ref_seqs.keys()) + 2
        for _ in range(ignore_lines):  # Ignore header lines
            self._f.readline()
        self._read_1_line = ""
        self._read_1: AlignedRead | None = None

    def __iter__(self):
        """Return iterator."""
        return self

    def __next__(self) -> list[AlignedRead]:
        """Get next single-end read.

        Returns:
            List containing one AlignedRead

        Raises:
            StopIteration: When end of file is reached
        """
        self._read_1_line = self._f.readline().strip()
        if len(self._read_1_line) == 0:
            raise StopIteration
        self._read_1 = get_aligned_read_from_line(self._read_1_line)
        return [self._read_1]


class PairedSamIterator:
    """Iterator for paired-end SAM files."""

    def __init__(self, samfile_path: str, ref_seqs: dict[str, str]):
        """Initialize paired-end SAM iterator.

        Args:
            samfile_path: Path to SAM file
            ref_seqs: Dictionary of reference sequences
        """
        self._f = open(samfile_path)
        ignore_lines = len(ref_seqs.keys()) + 2
        for _ in range(ignore_lines):  # Ignore header lines
            self._f.readline()
        self._read_1_line = ""
        self._read_2_line = ""
        self._read_1: AlignedRead | None = None
        self._read_2: AlignedRead | None = None

    def __iter__(self):
        """Return iterator."""
        return self

    def __next__(self) -> list[AlignedRead]:
        """Get next paired-end read pair.

        Returns:
            List containing two AlignedRead objects

        Raises:
            StopIteration: When end of file is reached
        """
        self._read_1_line = self._f.readline().strip()
        self._read_2_line = self._f.readline().strip()
        if len(self._read_1_line) == 0 or len(self._read_2_line) == 0:
            raise StopIteration
        self._read_1 = get_aligned_read_from_line(self._read_1_line)
        self._read_2 = get_aligned_read_from_line(self._read_2_line)

        # check if reads are paired
        if not (
            self._read_1.pnext == self._read_2.pos
            and self._read_1.rname == self._read_2.rname
            and self._read_1.rnext == "="
        ):
            log.warning(
                "mate_2 is inconsistent with mate_1 for read: "
                f"{self._read_1.qname} SKIPPING!"
            )
            self.__next__()
        if not (
            self._read_1.qname == self._read_2.qname
            and self._read_1.mapq == self._read_2.mapq
        ):
            log.warning(
                "mate_2 is inconsistent with mate_1 for read: "
                f"{self._read_1.qname} SKIPPING!"
            )
            self.__next__()
        return [self._read_1, self._read_2]
