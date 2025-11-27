"""Improved CLI argument parsing and validation."""

from rna_map.cli.bowtie2 import (
    build_bowtie2_args,
    get_preset_names,
    load_bowtie2_presets,
    parse_bowtie2_cli_args,
)
from rna_map.cli.parser import parse_cli_args, normalize_bowtie2_args, validate_bowtie2_args_cli

__all__ = [
    "parse_cli_args",
    "normalize_bowtie2_args",
    "validate_bowtie2_args_cli",
    "build_bowtie2_args",
    "get_preset_names",
    "load_bowtie2_presets",
    "parse_bowtie2_cli_args",
]

