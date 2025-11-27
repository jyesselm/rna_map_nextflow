"""External command wrappers (backward compatibility).

This module re-exports functions from the new external module for backward compatibility.
"""

# Re-export from new external module for backward compatibility
from rna_map.external import (
    ProgOutput,
    does_program_exist,
    get_bowtie2_version,
    get_cutadapt_version,
    get_fastqc_version,
    get_trim_galore_version,
    run_bowtie_alignment,
    run_bowtie_build,
    run_command,
    run_fastqc,
    run_named_command,
    run_trim_galore,
    validate_bowtie2_args,
)

__all__ = [
    "ProgOutput",
    "does_program_exist",
    "get_bowtie2_version",
    "get_fastqc_version",
    "get_trim_galore_version",
    "get_cutadapt_version",
    "run_command",
    "run_named_command",
    "run_fastqc",
    "run_trim_glore",
    "run_bowtie_build",
    "validate_bowtie2_args",
    "run_bowtie_alignment",
]

# Alias for backward compatibility (note: original had typo "trim_glore")
run_trim_glore = run_trim_galore
