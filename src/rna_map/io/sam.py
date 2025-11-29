"""SAM file parsing utilities.

Supports two parsing backends:
1. Native Python parsing (default) - Simple line-by-line parsing
2. pysam (optional) - Faster, more robust SAM/BAM parsing using pysam library
"""

from dataclasses import dataclass
from typing import Optional

from rna_map.logger import get_logger

log = get_logger("IO.SAM")

# Try to import pysam, but make it optional
try:
    import pysam
    PYSAM_AVAILABLE = True
except ImportError:
    PYSAM_AVAILABLE = False
    pysam = None


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
    """Iterator for single-end SAM files.
    
    Supports both native Python parsing and pysam backend.
    """

    def __init__(
        self, 
        samfile_path: str, 
        ref_seqs: dict[str, str],
        use_pysam: bool = False
    ):
        """Initialize single-end SAM iterator.

        Args:
            samfile_path: Path to SAM file
            ref_seqs: Dictionary of reference sequences
            use_pysam: If True, use pysam for parsing (faster, more robust)
        """
        self._samfile_path = samfile_path
        self._ref_seqs = ref_seqs
        self._use_pysam = use_pysam and PYSAM_AVAILABLE
        
        if self._use_pysam:
            self._samfile = pysam.AlignmentFile(samfile_path, "r")
            self._iter = iter(self._samfile)
        else:
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
        if self._use_pysam:
            try:
                pysam_read = next(self._iter)
                # Skip unmapped reads
                if pysam_read.is_unmapped:
                    return self.__next__()
                
                # Extract MD tag if available
                md_string = ""
                if pysam_read.has_tag("MD"):
                    md_string = pysam_read.get_tag("MD")
                else:
                    md_string = ""
                
                aligned_read = AlignedRead(
                    qname=pysam_read.query_name,
                    flag=str(pysam_read.flag),
                    rname=pysam_read.reference_name or "*",
                    pos=pysam_read.reference_start + 1,  # pysam is 0-based, SAM is 1-based
                    mapq=pysam_read.mapping_quality,
                    cigar=pysam_read.cigarstring or "*",
                    rnext=pysam_read.next_reference_name or "*",
                    pnext=pysam_read.next_reference_start + 1 if pysam_read.next_reference_start >= 0 else 0,
                    tlen=pysam_read.template_length,
                    seq=pysam_read.query_sequence or "",
                    qual=pysam_read.qual if pysam_read.qual else "",
                    md_string=md_string,
                )
                return [aligned_read]
            except StopIteration:
                self._samfile.close()
                raise
        else:
            self._read_1_line = self._f.readline().strip()
            if len(self._read_1_line) == 0:
                self._f.close()
                raise StopIteration
            self._read_1 = get_aligned_read_from_line(self._read_1_line)
            return [self._read_1]
    
    def __del__(self):
        """Clean up resources."""
        if self._use_pysam and hasattr(self, '_samfile'):
            try:
                self._samfile.close()
            except:
                pass
        elif hasattr(self, '_f'):
            try:
                self._f.close()
            except:
                pass


class PairedSamIterator:
    """Iterator for paired-end SAM files.
    
    Supports both native Python parsing and pysam backend.
    """

    def __init__(
        self, 
        samfile_path: str, 
        ref_seqs: dict[str, str],
        use_pysam: bool = False
    ):
        """Initialize paired-end SAM iterator.

        Args:
            samfile_path: Path to SAM file
            ref_seqs: Dictionary of reference sequences
            use_pysam: If True, use pysam for parsing (faster, more robust)
        """
        self._samfile_path = samfile_path
        self._ref_seqs = ref_seqs
        self._use_pysam = use_pysam and PYSAM_AVAILABLE
        
        if self._use_pysam:
            self._samfile = pysam.AlignmentFile(samfile_path, "r")
            self._iter = iter(self._samfile)
            self._pending_read: Optional[AlignedRead] = None
        else:
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
        if self._use_pysam:
            reads = []
            try:
                # If we have a pending read, use it
                if self._pending_read:
                    reads.append(self._pending_read)
                    self._pending_read = None
                
                # Collect reads until we have a proper pair
                while len(reads) < 2:
                    pysam_read = next(self._iter)
                    
                    # Skip unmapped reads
                    if pysam_read.is_unmapped:
                        continue
                    
                    # Extract MD tag if available
                    md_string = ""
                    if pysam_read.has_tag("MD"):
                        md_string = pysam_read.get_tag("MD")
                    
                    aligned_read = AlignedRead(
                        qname=pysam_read.query_name,
                        flag=str(pysam_read.flag),
                        rname=pysam_read.reference_name or "*",
                        pos=pysam_read.reference_start + 1,  # pysam is 0-based, SAM is 1-based
                        mapq=pysam_read.mapping_quality,
                        cigar=pysam_read.cigarstring or "*",
                        rnext=pysam_read.next_reference_name or "*",
                        pnext=pysam_read.next_reference_start + 1 if pysam_read.next_reference_start >= 0 else 0,
                        tlen=pysam_read.template_length,
                        seq=pysam_read.query_sequence or "",
                        qual=pysam_read.qual if pysam_read.qual else "",
                        md_string=md_string,
                    )
                    
                    # Check if this is the first or second read of a pair
                    if pysam_read.is_read1:
                        if len(reads) == 0:
                            reads.append(aligned_read)
                        else:
                            # We have read1 but were expecting read2, save for next iteration
                            self._pending_read = aligned_read
                            break
                    elif pysam_read.is_read2:
                        if len(reads) == 1 and reads[0].qname == aligned_read.qname:
                            reads.append(aligned_read)
                        else:
                            # Mismatched pair, skip read2
                            log.warning(
                                f"Mismatched pair for {aligned_read.qname}, skipping"
                            )
                            continue
                    else:
                        # Single-end read, treat as read1
                        if len(reads) == 0:
                            reads.append(aligned_read)
                        else:
                            self._pending_read = aligned_read
                            break
                
                if len(reads) == 2:
                    return reads
                elif len(reads) == 1:
                    # Only one read, return it as single-end
                    return reads
                else:
                    raise StopIteration
                    
            except StopIteration:
                self._samfile.close()
                if len(reads) > 0:
                    return reads
                raise
        else:
            self._read_1_line = self._f.readline().strip()
            self._read_2_line = self._f.readline().strip()
            if len(self._read_1_line) == 0 or len(self._read_2_line) == 0:
                self._f.close()
                raise StopIteration
            self._read_1 = get_aligned_read_from_line(self._read_1_line)
            self._read_2 = get_aligned_read_from_line(self._read_2_line)

            # check if reads are paired - use a loop to avoid infinite recursion
            max_retries = 100  # Prevent infinite loops
            retries = 0
            while retries < max_retries:
                retries += 1
                # Check if reads are properly paired
                if (
                    self._read_1.pnext == self._read_2.pos
                    and self._read_1.rname == self._read_2.rname
                    and self._read_1.rnext == "="
                    and self._read_1.qname == self._read_2.qname
                    and self._read_1.mapq == self._read_2.mapq
                ):
                    # Reads are properly paired, break out of loop
                    break
                
                # Reads are inconsistent, skip and try next pair
                log.warning(
                    "mate_2 is inconsistent with mate_1 for read: "
                    f"{self._read_1.qname} SKIPPING!"
                )
                # Read next pair
                self._read_1_line = self._f.readline().strip()
                self._read_2_line = self._f.readline().strip()
                if len(self._read_1_line) == 0 or len(self._read_2_line) == 0:
                    raise StopIteration
                self._read_1 = get_aligned_read_from_line(self._read_1_line)
                self._read_2 = get_aligned_read_from_line(self._read_2_line)
            
            if retries >= max_retries:
                log.warning(f"Too many inconsistent read pairs, stopping iteration")
                raise StopIteration
            return [self._read_1, self._read_2]
    
    def __del__(self):
        """Clean up resources."""
        if self._use_pysam and hasattr(self, '_samfile'):
            try:
                self._samfile.close()
            except:
                pass
        elif hasattr(self, '_f'):
            try:
                self._f.close()
            except:
                pass
