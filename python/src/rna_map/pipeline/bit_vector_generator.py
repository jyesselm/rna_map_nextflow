"""Bit vector generator for mutation analysis."""

import os
from pathlib import Path
import pickle

import pandas as pd
from tabulate import tabulate

from rna_map.analysis.mutation_histogram import MutationHistogram
from rna_map.analysis.statistics import get_dataframe
from rna_map.core.bit_vector import BitVectorSymbols
from rna_map.io.bit_vector_storage import (
    StorageFormat,
    create_storage_writer,
    BitVectorStorageWriter,
)
from rna_map.io.fasta import fasta_to_dict
from rna_map.logger import get_logger
from rna_map.mutation_histogram import (
    write_mut_histos_to_json_file,
    write_mut_histos_to_pickle_file,
)
from rna_map.visualization import (
    plot_modified_bases,
    plot_mutation_histogram,
    plot_population_avg,
    plot_read_coverage,
)

# Import BitVectorIterator from analysis module
# Lazy import to avoid circular dependency - import inside run() method

log = get_logger("PIPELINE.BIT_VECTOR_GENERATOR")


class BitVectorGenerator:
    """Generates bit vectors from aligned reads and performs mutation analysis."""

    def __init__(self):
        """Initialize BitVectorGenerator."""
        self.__bases = ["A", "C", "G", "T"]
        self.__bts = BitVectorSymbols()

    def setup(self, params: dict) -> None:
        """Setup generator with parameters.

        Args:
            params: Parameter dictionary
        """
        self.__params = params
        self.__out_dir = Path(params["dirs"]["output"]) / "BitVector_Files"
        os.makedirs(params["dirs"]["output"], exist_ok=True)
        os.makedirs(self.__out_dir, exist_ok=True)

    def run(
        self, sam_path: Path, fasta: str | Path, paired: bool, csv_file: str | Path
    ) -> None:
        """Run bit vector generation and analysis.

        Args:
            sam_path: Path to aligned SAM file
            fasta: Path to FASTA file
            paired: Whether reads are paired-end
            csv_file: Path to CSV file with structure info (optional)
        """
        log.info("starting bitvector generation")
        self.__ref_seqs = fasta_to_dict(fasta)
        # Lazy import to avoid circular dependency
        from rna_map.analysis.bit_vector_iterator import BitVectorIterator

        use_pysam = self.__params.get("bit_vector", {}).get("use_pysam", False)
        self.__bit_vec_iterator = BitVectorIterator(
            sam_path, self.__ref_seqs, paired, use_pysam=use_pysam
        )
        self.__mut_histos: dict[str, MutationHistogram] = {}
        self.__map_score_cutoff = self.__params["bit_vector"]["map_score_cutoff"]
        self.__csv_file = csv_file
        self.__summary_only = self.__params["bit_vector"]["summary_output_only"]
        self.__rejected_out = open(self.__out_dir / "rejected_bvs.csv", "w")
        self.__rejected_out.write("qname,rname,reason,read1,read2,bitvector\n")
        self.__generate_all_bit_vectors()
        self.__generate_plots()
        self.__get_skip_summary()
        self.__write_summary_csv()

    def __write_summary_csv(self) -> None:
        """Write summary CSV file."""
        cols = [
            "name",
            "reads",
            "aligned",
            "no_mut",
            "1_mut",
            "2_mut",
            "3_mut",
            "3plus_mut",
            "sn",
        ]
        df = get_dataframe(self.__mut_histos, cols)
        log.info(
            "MUTATION SUMMARY:\n"
            + tabulate(df, df.columns, tablefmt="github", showindex=False)
        )
        sum_path = os.path.join(self.__out_dir, "summary.csv")
        df.to_csv(sum_path, index=False)

    def __get_skip_summary(self) -> None:
        """Generate summary of rejected reads."""
        data = []
        cols = ["low_mapq"]
        if self.__params["stricter_bv_constraints"]:
            cols += ["short_read", "too_many_muts", "muts_too_close"]
        for mut_histo in self.__mut_histos.values():
            row: list[str | float] = [mut_histo.name]
            for col in cols:
                try:
                    row.append(mut_histo.skips[col] / mut_histo.num_reads * 100)
                except ZeroDivisionError:
                    row.append(0.0)
            data.append(row)
        df = pd.DataFrame(data, columns=["name"] + cols)
        log.info(
            "REMOVED READS:\n"
            + tabulate(df, df.columns, tablefmt="github", showindex=False)
            + "\n"
        )

    def __generate_plots(self) -> None:
        """Generate plots for each mutation histogram."""
        for _, mh in self.__mut_histos.items():
            fname = f"{self.__out_dir}/{mh.name}_{mh.start}_{mh.end}_"
            if not self.__summary_only:
                df = mh.get_pop_avg_dataframe()
                plot_population_avg(
                    df,
                    mh.name,
                    f"{fname}pop_avg.html",
                    plot_sequence=self.__params["bit_vector"]["plot_sequence"],
                )
            if self.__params["restore_org_behavior"]:
                mod_bases_list = {k: v.tolist() for k, v in mh.mod_bases.items()}
                plot_modified_bases(
                    mh.get_nuc_coords(), mod_bases_list, f"{fname}mutations.html"
                )
                plot_mutation_histogram(
                    mh.get_nuc_coords(),
                    mh.num_of_mutations,
                    f"{fname}mutation_histogram.html",
                )
                plot_read_coverage(
                    mh.get_nuc_coords(),
                    mh.get_read_coverage(),
                    f"{fname}read_coverage.html",
                )

    def __generate_all_bit_vectors(self) -> None:
        """Generate all bit vectors from SAM file."""
        pickle_file = self.__out_dir / "mutation_histos.p"
        if self._should_skip_generation(pickle_file):
            return
        self._initialize_mutation_histograms()
        self._load_structure_from_csv()
        self._process_all_bit_vectors()
        self._close_writers()
        self._save_mutation_histograms(pickle_file)

    def _close_writers(self) -> None:
        """Close all bit vector storage writers."""
        for writer in self._bit_vector_writers.values():
            if writer:
                writer.close()

    def _should_skip_generation(self, pickle_file: Path) -> bool:
        """Check if bit vector generation should be skipped.

        Args:
            pickle_file: Path to pickle file

        Returns:
            True if should skip, False otherwise
        """
        if os.path.isfile(pickle_file) and not self.__params["overwrite"]:
            log.info(
                "SKIPPING bit vector generation, it has run already! specify"
                " -overwrite to rerun"
            )
            with open(pickle_file, "rb") as handle:
                self.__mut_histos = pickle.load(handle)
            return True
        return False

    def _initialize_mutation_histograms(self) -> None:
        """Initialize mutation histograms and bit vector writers."""
        self._bit_vector_writers: dict[str, BitVectorStorageWriter] = {}
        storage_format_str = self.__params["bit_vector"].get(
            "storage_format", "text"
        ).lower()
        storage_format = (
            StorageFormat.JSON
            if storage_format_str == "json"
            else StorageFormat.TEXT
        )

        for ref_name, seq in self.__ref_seqs.items():
            self.__mut_histos[ref_name] = MutationHistogram(
                ref_name, seq, "DMS", 1, len(seq)
            )
            if not self.__summary_only:
                if storage_format == StorageFormat.TEXT:
                    self._bit_vector_writers[ref_name] = create_storage_writer(
                        storage_format,
                        self.__out_dir,
                        name=ref_name,
                        sequence=seq,
                        data_type="DMS",
                        start=1,
                        end=len(seq),
                    )
                else:
                    # JSON format uses a single writer for all references
                    if "json_writer" not in self._bit_vector_writers:
                        self._bit_vector_writers["json_writer"] = create_storage_writer(
                            storage_format, self.__out_dir
                        )

    def _load_structure_from_csv(self) -> None:
        """Load structure information from CSV file."""
        if str(self.__csv_file) != "." and str(self.__csv_file) != "":
            df = pd.read_csv(self.__csv_file)
            for _, row in df.iterrows():
                if row["name"] in self.__mut_histos:
                    self.__mut_histos[row["name"]].structure = row["structure"]

    def _process_all_bit_vectors(self) -> None:
        """Process all bit vectors from iterator."""
        for bit_vector in self.__bit_vec_iterator:
            self.__record_bit_vector(bit_vector)

    def _save_mutation_histograms(self, pickle_file: Path) -> None:
        """Save mutation histograms to files.

        Args:
            pickle_file: Path to pickle file
        """
        json_file = os.path.join(self.__out_dir, "mutation_histos.json")
        write_mut_histos_to_pickle_file(self.__mut_histos, str(pickle_file))
        write_mut_histos_to_json_file(self.__mut_histos, json_file)

    def __record_bit_vector(self, bit_vector) -> None:
        """Record a bit vector in mutation histogram.

        Args:
            bit_vector: BitVector object to record
        """
        mh = self.__mut_histos[bit_vector.reads[0].rname]
        for read in bit_vector.reads:
            if read.mapq < self.__map_score_cutoff:
                self.__write_rejected_bit_vector(mh, bit_vector, "low_mapq")
                mh.record_skip("low_mapq")
                return
        if self.__are_reads_to_short(mh, bit_vector):
            return
        if self.__too_many_mutations(mh, bit_vector):
            return
        if self.__muts_too_close(mh, bit_vector):
            return
        self.__update_mut_histo(mh, bit_vector.data)
        if not self.__params["bit_vector"]["summary_output_only"]:
            storage_format_str = self.__params["bit_vector"].get(
                "storage_format", "text"
            ).lower()
            if storage_format_str == "json":
                writer = self._bit_vector_writers.get("json_writer")
            else:
                writer = self._bit_vector_writers.get(bit_vector.reads[0].rname)
            if writer:
                writer.write_bit_vector(
                    bit_vector.reads[0].qname, bit_vector.data, bit_vector.reads
                )

    def __update_mut_histo(
        self, mh: MutationHistogram, bit_vector: dict[int, str]
    ) -> None:
        """Update mutation histogram with bit vector data.

        Args:
            mh: MutationHistogram to update
            bit_vector: Bit vector dictionary
        """
        mh.num_reads += 1
        mh.num_aligned += 1
        total_muts = 0
        for pos in mh.get_nuc_coords():
            if pos not in bit_vector:
                continue
            read_bit = bit_vector[pos]
            if read_bit != self.__bts.ambig_info:
                mh.cov_bases[pos] += 1
            if read_bit in self.__bases:
                total_muts += 1
                mh.mod_bases[read_bit][pos] += 1
                mh.mut_bases[pos] += 1
            elif read_bit == self.__bts.del_bit:
                mh.del_bases[pos] += 1
            mh.info_bases[pos] += 1
        mh.num_of_mutations[total_muts] += 1

    def __are_reads_to_short(self, mh: MutationHistogram, bit_vector) -> bool:
        """Check if reads are too short.

        Args:
            mh: MutationHistogram
            bit_vector: BitVector object

        Returns:
            True if reads are too short
        """
        if not self.__params["stricter_bv_constraints"]:
            return False
        cutoff = self.__params["bit_vector"]["stricter_constraints"][
            "percent_length_cutoff"
        ]
        ref_seq = self.__ref_seqs[bit_vector.reads[0].rname]
        for read in bit_vector.reads:
            per = len(read.seq) / len(ref_seq)
            if per < cutoff:
                self.__write_rejected_bit_vector(mh, bit_vector, "short_read")
                mh.record_skip("short_read")
                return True
        return False

    def __too_many_mutations(self, mh: MutationHistogram, bit_vector) -> bool:
        """Check if bit vector has too many mutations.

        Args:
            mh: MutationHistogram
            bit_vector: BitVector object

        Returns:
            True if too many mutations
        """
        if not self.__params["stricter_bv_constraints"]:
            return False
        cutoff = self.__params["bit_vector"]["stricter_constraints"][
            "mutation_count_cutoff"
        ]
        muts = 0
        for pos in mh.get_nuc_coords():
            if pos not in bit_vector.data:
                continue
            read_bit = bit_vector.data[pos]
            if read_bit in self.__bases:
                muts += 1
        if muts > cutoff:
            self.__write_rejected_bit_vector(mh, bit_vector, "too_many_muts")
            mh.record_skip("too_many_muts")
            return True
        return False

    def __muts_too_close(self, mh: MutationHistogram, bit_vector) -> bool:
        """Check if mutations are too close together.

        Args:
            mh: MutationHistogram
            bit_vector: BitVector object

        Returns:
            True if mutations are too close
        """
        if not self.__params["stricter_bv_constraints"]:
            return False
        cutoff = self.__params["bit_vector"]["stricter_constraints"]["min_mut_distance"]
        start = mh.start if mh.start is not None else 1
        end = mh.end if mh.end is not None else len(mh.sequence)
        for pos in range(start, end + 1):
            if pos not in bit_vector.data:
                continue
            read_bit = bit_vector.data[pos]
            if read_bit in self.__bases:
                for pos2 in range(pos - cutoff, pos + cutoff):
                    if pos2 == pos:
                        continue
                    if pos2 not in bit_vector.data:
                        continue
                    if bit_vector.data[pos2] in self.__bases:
                        self.__write_rejected_bit_vector(
                            mh, bit_vector, "muts_too_close"
                        )
                        mh.record_skip("muts_too_close")
                        return True
        return False

    def __write_rejected_bit_vector(
        self, mh: MutationHistogram, bit_vector, reason: str
    ) -> None:
        """Write rejected bit vector to log file.

        Args:
            mh: MutationHistogram
            bit_vector: BitVector object
            reason: Reason for rejection
        """
        read1 = bit_vector.reads[0]
        if len(bit_vector.reads) == 2:
            read2_seq = bit_vector.reads[1].seq
        else:
            read2_seq = ""
        bv_vec = []
        for nuc in mh.get_nuc_coords():
            if nuc in bit_vector.data:
                bv_vec.append(bit_vector.data[nuc])
            else:
                bv_vec.append(".")
        self.__rejected_out.write(
            f"{read1.qname},{read1.rname},{reason},{read1.seq},{read2_seq},"
            f"{''.join(bv_vec)}\n"
        )
