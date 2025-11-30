"""Mutation histogram class for tracking mutations across reads."""

import numpy as np
import pandas as pd

from rna_map.logger import get_logger

log = get_logger("MUT_HISTOGRAM")


class MutationHistogram:
    """Tracks and analyzes mutation patterns across reads.

    Attributes:
        name: Name of the construct/sequence
        sequence: Reference sequence
        structure: Secondary structure (dot-bracket notation)
        data_type: Type of data (e.g., "DMS")
        num_reads: Total number of reads processed
        num_aligned: Number of reads that passed filtering
        skips: Dictionary tracking reasons for rejected reads
        num_of_mutations: List counting reads by mutation count
        mut_bases: Array counting mutations per position
        info_bases: Array counting informative bases per position
        del_bases: Array counting deletions per position
        ins_bases: Array counting insertions per position
        cov_bases: Array counting coverage per position
        mod_bases: Dictionary (A/C/G/T) of arrays counting specific mutations
        start: Start position (1-based)
        end: End position (1-based)
    """

    def __init__(
        self,
        name: str,
        sequence: str,
        data_type: str,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        """Initialize a MutationHistogram.

        Args:
            name: Name of the construct
            sequence: Reference sequence
            data_type: Type of data (e.g., "DMS")
            start: Start position (1-based), defaults to 1
            end: End position (1-based), defaults to len(sequence)
        """
        self.name = name
        self.sequence = sequence
        self.structure = None
        self.data_type = data_type
        self.num_reads = 0
        self.num_aligned = 0
        self.skips = {
            "low_mapq": 0,
            "short_read": 0,
            "too_many_muts": 0,
            "muts_too_close": 0,
        }
        self.num_of_mutations = [0] * (len(sequence) + 1)
        self.mut_bases = np.zeros(len(sequence) + 1)
        self.info_bases = np.zeros(len(sequence) + 1)
        self.del_bases = np.zeros(len(sequence) + 1)
        self.ins_bases = np.zeros(len(sequence) + 1)
        self.cov_bases = np.zeros(len(sequence) + 1)
        self.mod_bases = {
            "A": np.zeros(len(sequence) + 1),
            "C": np.zeros(len(sequence) + 1),
            "G": np.zeros(len(sequence) + 1),
            "T": np.zeros(len(sequence) + 1),
        }
        self.start = start
        self.end = end
        if self.start is None:
            self.start = 1
        if self.end is None:
            self.end = len(self.sequence)

    @classmethod
    def from_dict(cls, d: dict) -> "MutationHistogram":
        """Create MutationHistogram from dictionary.

        Args:
            d: Dictionary with histogram data

        Returns:
            MutationHistogram instance
        """
        mh = cls(d["name"], d["sequence"], d["data_type"])
        mh.structure = d["structure"]
        mh.start = d["start"]
        mh.end = d["end"]
        mh.num_reads = d["num_reads"]
        mh.num_aligned = d["num_aligned"]
        mh.skips = d["skips"]
        mh.num_of_mutations = d["num_of_mutations"]
        mh.mut_bases = np.array(d["mut_bases"])
        mh.info_bases = np.array(d["info_bases"])
        mh.del_bases = np.array(d["del_bases"])
        mh.ins_bases = np.array(d["ins_bases"])
        mh.cov_bases = np.array(d["cov_bases"])
        mh.mod_bases["A"] = np.array(d["mod_bases"]["A"])
        mh.mod_bases["C"] = np.array(d["mod_bases"]["C"])
        mh.mod_bases["G"] = np.array(d["mod_bases"]["G"])
        mh.mod_bases["T"] = np.array(d["mod_bases"]["T"])
        return mh

    def get_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "sequence": self.sequence,
            "structure": self.structure,
            "data_type": self.data_type,
            "start": self.start,
            "end": self.end,
            "num_reads": self.num_reads,
            "num_aligned": self.num_aligned,
            "skips": self.skips,
            "num_of_mutations": self.num_of_mutations,
            "mut_bases": self.mut_bases.tolist(),
            "info_bases": self.info_bases.tolist(),
            "del_bases": self.del_bases.tolist(),
            "ins_bases": self.ins_bases.tolist(),
            "cov_bases": self.cov_bases.tolist(),
            "mod_bases": {
                "A": self.mod_bases["A"].tolist(),
                "C": self.mod_bases["C"].tolist(),
                "G": self.mod_bases["G"].tolist(),
                "T": self.mod_bases["T"].tolist(),
            },
        }

    def merge(self, other: "MutationHistogram") -> None:
        """Merge values from another histogram.

        Args:
            other: Another MutationHistogram to merge

        Raises:
            ValueError: If histograms cannot be merged (mismatched attributes)
        """
        if self.name != other.name:
            raise ValueError("MutationalHistogram names do not match cannot merge")
        if self.sequence != other.sequence:
            raise ValueError("MutationalHistogram sequences do not match cannot merge")
        if self.data_type != other.data_type:
            raise ValueError("MutationalHistogram data_types do not match cannot merge")
        if self.start != other.start:
            raise ValueError("MutationalHistogram starts do not match cannot merge")
        if self.end != other.end:
            raise ValueError("MutationalHistogram ends do not match cannot merge")
        if self.structure != other.structure:
            raise ValueError("MutationalHistogram structures do not match cannot merge")
        self.num_reads += other.num_reads
        self.num_aligned += other.num_aligned
        for key in self.skips:
            self.skips[key] += other.skips[key]
        for ii in range(len(other.num_of_mutations)):
            self.num_of_mutations[ii] += other.num_of_mutations[ii]
        self.mut_bases += other.mut_bases
        self.ins_bases += other.ins_bases
        self.cov_bases += other.cov_bases
        self.info_bases += other.info_bases
        for key in self.mod_bases:
            self.mod_bases[key] += other.mod_bases[key]

    def record_skip(self, t: str) -> None:
        """Record a skipped read.

        Args:
            t: Skip type (e.g., "low_mapq", "short_read")
        """
        self.num_reads += 1
        self.skips[t] += 1

    def get_read_coverage(self) -> list[float]:
        """Get normalized read coverage.

        Returns:
            List of coverage fractions per position
        """
        read_cov = []
        for pos in self.get_nuc_coords():
            try:
                cov_frac = self.cov_bases[pos] / self.num_reads
            except ZeroDivisionError:
                cov_frac = 0.0
            read_cov.append(cov_frac)
        return read_cov

    def get_nuc_coords(self) -> list[int]:
        """Get nucleotide coordinates.

        Returns:
            List of positions from start to end
        """
        start = self.start if self.start is not None else 1
        end = self.end if self.end is not None else len(self.sequence)
        return list(range(start, end + 1))

    def get_pop_avg(self, inc_del: bool = False) -> list[float]:
        """Get population average mutation rate.

        Args:
            inc_del: If True, include deletions in the average

        Returns:
            List of mutation fractions per position
        """
        pop_avg = []
        for pos in self.get_nuc_coords():
            try:
                if inc_del:
                    mut_frac = (
                        self.del_bases[pos] + self.mut_bases[pos]
                    ) / self.info_bases[pos]
                else:
                    mut_frac = self.mut_bases[pos] / self.info_bases[pos]
            except Exception:
                mut_frac = 0.0
            pop_avg.append(round(mut_frac, 5))
        return pop_avg

    def get_pop_avg_dataframe(self) -> pd.DataFrame:
        """Get population average as DataFrame.

        Returns:
            DataFrame with position, mismatches, and nucleotides
        """
        pop_avg = self.get_pop_avg(inc_del=False)
        pop_avg_del = self.get_pop_avg(inc_del=True)
        df = pd.DataFrame(
            {
                "position": self.get_nuc_coords(),
                "mismatches": pop_avg,
                "mismatch_del": pop_avg_del,
                "nuc": list(self.sequence),
            }
        )
        if self.structure is not None:
            df["structure"] = list(self.structure)
        return df

    def get_percent_mutations(self) -> list[float]:
        """Get percentage of reads by mutation count.

        Returns:
            List of percentages: [0_mut, 1_mut, 2_mut, 3_mut, 3+_mut]
        """
        data_array = np.array(
            self.num_of_mutations[0:4] + [sum(self.num_of_mutations[5:])]
        )
        if self.num_aligned != 0:
            data = [round(x, 2) for x in list((data_array / self.num_aligned) * 100)]
        else:
            data = [0.0] * 5
        return data

    def get_signal_to_noise(self) -> float:
        """Calculate signal-to-noise ratio (AC/GU ratio).

        Returns:
            Signal-to-noise ratio as float
        """
        seq = self.sequence
        AC: float = 0.0
        GU: float = 0.0
        AC_count = seq.count("A") + seq.count("C")
        GU_count = seq.count("G") + seq.count("U") + seq.count("T")
        for pos in self.get_nuc_coords():
            if seq[pos - 1] == "A" or seq[pos - 1] == "C":
                AC += float(self.mut_bases[pos])
            else:
                GU += float(self.mut_bases[pos])
        AC /= float(AC_count)
        GU /= float(GU_count)
        if GU == 0:
            return 0.0
        return round(float(AC / GU), 2)
