"""External command wrappers for RNA MAP.

This module provides wrappers for external bioinformatics tools:
- Bowtie2 alignment
- FastQC quality control
- Trim Galore adapter trimming
- Version checking utilities
"""

from rna_map.external.base import (
    ProgOutput,
    does_program_exist,
    run_command,
    run_named_command,
)
from rna_map.external.bowtie2 import (
    run_bowtie_alignment,
    run_bowtie_build,
    validate_bowtie2_args,
)
from rna_map.external.fastqc import run_fastqc
from rna_map.external.trim_galore import run_trim_galore
from rna_map.external.version import (
    get_bowtie2_version,
    get_cutadapt_version,
    get_fastqc_version,
    get_trim_galore_version,
)

__all__ = [
    "ProgOutput",
    "does_program_exist",
    "run_command",
    "run_named_command",
    "get_bowtie2_version",
    "get_fastqc_version",
    "get_trim_galore_version",
    "get_cutadapt_version",
    "run_fastqc",
    "run_trim_galore",
    "run_bowtie_build",
    "run_bowtie_alignment",
    "validate_bowtie2_args",
]
