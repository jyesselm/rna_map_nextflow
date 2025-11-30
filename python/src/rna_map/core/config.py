"""Configuration dataclasses for RNA MAP pipeline components."""

from dataclasses import dataclass

from rna_map.io.bit_vector_storage import StorageFormat


@dataclass(frozen=True)
class StricterConstraints:
    """Stricter bit vector constraints configuration.

    Attributes:
        min_mut_distance: Minimum distance between mutations
        percent_length_cutoff: Minimum percent of reference length required
        mutation_count_cutoff: Maximum number of mutations allowed
    """

    min_mut_distance: int = 5
    percent_length_cutoff: float = 0.10
    mutation_count_cutoff: int = 5

    @classmethod
    def from_dict(cls, data: dict) -> "StricterConstraints":
        """Create from dictionary.

        Args:
            data: Dictionary with constraint values

        Returns:
            StricterConstraints instance
        """
        return cls(
            min_mut_distance=data.get("min_mut_distance", 5),
            percent_length_cutoff=data.get("percent_length_cutoff", 0.10),
            mutation_count_cutoff=data.get("mutation_count_cutoff", 5),
        )


@dataclass(frozen=True)
class MappingConfig:
    """Configuration for read mapping pipeline.

    Attributes:
        skip_fastqc: Skip FastQC quality control step
        skip_trim_galore: Skip Trim Galore adapter trimming step
        tg_q_cutoff: Trim Galore quality score cutoff
        bt2_alignment_args: Bowtie2 alignment arguments (semicolon-separated)
        save_unaligned: Save unaligned reads to file
    """

    skip_fastqc: bool = False
    skip_trim_galore: bool = False
    tg_q_cutoff: int = 20
    bt2_alignment_args: str = "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16"
    save_unaligned: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> "MappingConfig":
        """Create from dictionary.

        Args:
            data: Dictionary with mapping configuration

        Returns:
            MappingConfig instance
        """
        return cls(
            skip_fastqc=data.get("skip_fastqc", False),
            skip_trim_galore=data.get("skip_trim_galore", False),
            tg_q_cutoff=data.get("tg_q_cutoff", 20),
            bt2_alignment_args=data.get(
                "bt2_alignment_args",
                "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16",
            ),
            save_unaligned=data.get("save_unaligned", False),
        )


@dataclass(frozen=True)
class BitVectorConfig:
    """Configuration for bit vector generation.

    Attributes:
        qscore_cutoff: Quality score cutoff for read nucleotides
        num_of_surbases: Number of surrounding bases for ambiguity check
        map_score_cutoff: Minimum mapping score cutoff
        plot_sequence: Whether to plot sequence/structure on plots
        summary_output_only: Only generate summary files (skip bit vector files)
        storage_format: Storage format for bit vectors (TEXT or JSON)
        stricter_constraints: Optional stricter constraints
        use_cpp: Whether to use C++ implementation (if available)
    """

    qscore_cutoff: int = 25
    num_of_surbases: int = 10
    map_score_cutoff: int = 15
    plot_sequence: bool = False
    summary_output_only: bool = False
    storage_format: StorageFormat = StorageFormat.TEXT
    stricter_constraints: StricterConstraints | None = None
    use_cpp: bool = False
    use_pysam: bool = False

    @classmethod
    def from_dict(cls, data: dict, use_stricter: bool = False) -> "BitVectorConfig":
        """Create from dictionary.

        Args:
            data: Dictionary with bit vector configuration
            use_stricter: Whether to use stricter constraints

        Returns:
            BitVectorConfig instance
        """
        stricter = None
        if use_stricter and "stricter_constraints" in data:
            stricter = StricterConstraints.from_dict(data["stricter_constraints"])

        storage_format_str = data.get("storage_format", "text").lower()
        storage_format = (
            StorageFormat.JSON
            if storage_format_str == "json"
            else StorageFormat.TEXT
        )

        return cls(
            qscore_cutoff=data.get("qscore_cutoff", 25),
            num_of_surbases=data.get("num_of_surbases", 10),
            map_score_cutoff=data.get("map_score_cutoff", 15),
            plot_sequence=data.get("plot_sequence", False),
            summary_output_only=data.get("summary_output_only", False),
            storage_format=storage_format,
            stricter_constraints=stricter,
            use_cpp=data.get("use_cpp", False),
            use_pysam=data.get("use_pysam", False),
        )

