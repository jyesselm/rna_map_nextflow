import cloup
from cloup import option, option_group

from rna_map.logger import get_logger

log = get_logger("CLI_OPTS")


def main_options():
    return option_group(
        "Main arguments",
        "These are the main arguments for the command line interface",
        option(
            "-fa",
            "--fasta",
            type=cloup.Path(exists=True),
            required=True,
            help="The fasta file containing the reference sequences",
        ),
        option(
            "-fq1",
            "--fastq1",
            type=cloup.Path(exists=True),
            required=True,
            help=(
                "The fastq file containing the single end reads or the first pair of"
                " paired end reads"
            ),
        ),
        option(
            "-fq2",
            "--fastq2",
            type=str,
            default="",
            help="The fastq file containing the second pair of paired end reads",
        ),
        option(
            "--dot-bracket",
            type=str,
            default="",
            help="The directory containing the input files",
        ),
        option(
            "-pf",
            "--param-file",
            type=str,
            default=None,
            help=(
                "A yml formatted file to specify parameters, see"
                " rna_map/resources/default.yml for an example"
            ),
        ),
        option(
            "-pp",
            "--param-preset",
            type=str,
            default=None,
            help="run a set of parameters for specific uses like 'barcoded-libraries'",
        ),
    )


def docker_options():
    return option_group(
        "Docker options",
        "These are the options for running the command line interface in a docker"
        " container",
        option(
            "--docker",
            is_flag=True,
            help="Run the program in a docker container",
        ),
        option(
            "--docker-image",
            type=str,
            default="rna-map",
            help="The docker image to use",
        ),
        option(
            "--docker-platform",
            type=str,
            default="",
            help="The platform to use for the docker image",
        ),
    )


def mapping_options():
    """Mapping options including improved Bowtie2 argument handling."""
    from rna_map.cli.bowtie2 import get_preset_names

    preset_names = get_preset_names()
    preset_help = f"Available presets: {', '.join(preset_names)}" if preset_names else ""

    return option_group(
        "Mapping options",
        "These are the options for pre processing of fastq files and alignment to"
        " reference sequences",
        option(
            "--skip-fastqc",
            is_flag=True,
            help="do not run fastqc for quality control of sequence data",
        ),
        option(
            "--skip-trim-galore",
            is_flag=True,
            help="do not run trim galore for quality control of sequence data",
        ),
        option(
            "--tg-q-cutoff",
            type=int,
            default=20,
            help="the quality cutoff for trim galore",
        ),
        # Bowtie2 preset option
        option(
            "--bt2-preset",
            type=str,
            default=None,
            help=f"Bowtie2 alignment preset to use. {preset_help}",
        ),
        # Individual Bowtie2 flags
        option(
            "--bt2-local",
            is_flag=True,
            help="use local alignment mode (default for most presets)",
        ),
        option(
            "--bt2-end-to-end",
            is_flag=True,
            help="use end-to-end alignment mode",
        ),
        option(
            "--bt2-threads",
            type=int,
            default=None,
            help="number of threads for alignment (e.g., 8, 16)",
        ),
        option(
            "--bt2-maxins",
            type=int,
            default=None,
            help="maximum insert size for paired-end reads (e.g., 1000)",
        ),
        option(
            "--bt2-seed-length",
            type=int,
            default=None,
            help="seed length for alignment (e.g., 12, 20). Shorter (10-12) better for mutation detection",
        ),
        option(
            "--bt2-seed-mismatches",
            type=int,
            default=None,
            help="max mismatches in seed (0-1). Use 1 for mutation tracking to allow mutations in seed",
        ),
        option(
            "--bt2-max-alignments",
            type=int,
            default=None,
            help="report up to N alignments per read (e.g., 10). Useful for similar sequences",
        ),
        option(
            "--bt2-no-unal",
            is_flag=True,
            help="suppress SAM records for unaligned reads",
        ),
        option(
            "--bt2-no-discordant",
            is_flag=True,
            help="suppress discordant alignments",
        ),
        option(
            "--bt2-no-mixed",
            is_flag=True,
            help="suppress unpaired alignments for paired reads",
        ),
        # Advanced options
        option(
            "--bt2-mismatch-penalty",
            type=str,
            default=None,
            help="mismatch penalty (e.g., '50,30')",
        ),
        option(
            "--bt2-gap-penalty-read",
            type=str,
            default=None,
            help="read gap penalty (e.g., '50,30')",
        ),
        option(
            "--bt2-gap-penalty-ref",
            type=str,
            default=None,
            help="reference gap penalty (e.g., '50,30')",
        ),
        option(
            "--bt2-score-min",
            type=str,
            default=None,
            help="minimum score function (e.g., 'G,20,15')",
        ),
        # Raw args fallback (for advanced users)
        option(
            "--bt2-alignment-args",
            help=(
                "raw Bowtie2 arguments (advanced). "
                "Can be separated by commas, semicolons, or spaces. "
                "Example: '--local,--no-unal,-p 8'. "
                "Note: This overrides preset and individual flags."
            ),
        ),
        option(
            "--save-unaligned",
            is_flag=True,
            help="the path to save unaligned reads to",
        ),
    )


def bit_vector_options():
    return option_group(
        "Bit vector options",
        "These are the options for the bit vector step",
        option(
            "--skip-bit-vector",
            is_flag=True,
            help="do not run the bit vector step",
        ),
        option(
            "--summary-output-only",
            is_flag=True,
            help=(
                "do not generate bit vector files or plots recommended when there are"
                " thousands of reference sequences"
            ),
        ),
        option(
            "--plot-sequence",
            is_flag=True,
            help=(
                "plot sequence and structure is supplied under the population average"
                " plots"
            ),
        ),
        option(
            "--map-score-cutoff",
            type=int,
            default=15,
            help=(
                "reject any bit vector where the mapping score for bowtie2 alignment is"
                " less than this value"
            ),
        ),
        option(
            "--qscore-cutoff",
            type=int,
            default=25,
            help=(
                "quality score of read nucleotide, sets to ambigious if under this val"
            ),
        ),
        option(
            "--mutation-count-cutoff",
            type=int,
            default=5,
            help=(
                "maximum number of mutations allowed in a bit vector will be discarded"
                " if higher"
            ),
        ),
        option(
            "--percent-length-cutoff",
            type=float,
            default=0.1,
            help=(
                "minium percent of the length of the reference sequence allowed in a"
                " bit vector will be discarded if lower"
            ),
        ),
        option(
            "--min-mut-distance",
            type=int,
            default=5,
            help=(
                "minimum distance between mutations in a bit vector will be discarded"
                " if lower"
            ),
        ),
    )


def misc_options():
    return option_group(
        "Misc options",
        "These are the options for the misc stage",
        option(
            "--overwrite",
            is_flag=True,
            help="overwrite the output directory if it exists",
        ),
        option(
            "--restore-org-behavior",
            is_flag=True,
            help="restore the original behavior of the rna_map",
        ),
        option(
            "--stricter-bv-constraints",
            is_flag=True,
            help=(
                "use stricter constraints for bit vector generation, use at your own"
                " risk!"
            ),
        ),
        option(
            "--debug",
            is_flag=True,
            help="enable debug mode",
        ),
    )


def parse_cli_args(params, args):
    """Parse CLI arguments and update parameters dictionary.

    This function now uses the improved parser from rna_map.cli.parser
    for better maintainability and validation.

    Args:
        params: Parameters dictionary to update
        args: CLI arguments dictionary
    """
    from rna_map.cli.parser import parse_cli_args as parse_cli_args_improved

    parse_cli_args_improved(params, args)
