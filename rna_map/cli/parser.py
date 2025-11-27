"""Improved CLI argument parser with better structure and validation."""


from rna_map.core.config import BitVectorConfig, MappingConfig
from rna_map.exception import DREEMInputException
from rna_map.external.bowtie2 import validate_bowtie2_args
from rna_map.logger import get_logger

log = get_logger("CLI.PARSER")


def normalize_bowtie2_args(args: str | None) -> str:
    """Normalize Bowtie2 arguments to semicolon-separated format.

    Accepts arguments separated by commas, semicolons, or spaces.
    Converts to semicolon-separated format used internally.

    Args:
        args: Bowtie2 arguments in any format (comma, semicolon, or space separated)

    Returns:
        Normalized semicolon-separated argument string

    Example:
        >>> normalize_bowtie2_args("--local,--no-unal,-p 8")
        "--local;--no-unal;-p 8"
        >>> normalize_bowtie2_args("--local;--no-unal;-p 8")
        "--local;--no-unal;-p 8"
        >>> normalize_bowtie2_args("--local --no-unal -p 8")
        "--local;--no-unal;-p 8"
    """
    if args is None or args.strip() == "":
        return ""

    # Try comma-separated first (most common user input)
    if "," in args:
        normalized = ";".join(arg.strip() for arg in args.split(",") if arg.strip())
    # Try semicolon-separated (current format)
    elif ";" in args:
        normalized = ";".join(arg.strip() for arg in args.split(";") if arg.strip())
    # Try space-separated (natural format)
    else:
        # Split by spaces but keep arguments with values together
        parts = args.split()
        normalized_parts = []
        i = 0
        while i < len(parts):
            part = parts[i]
            # If it's a flag (starts with -), check if next part is a value
            if part.startswith("-") and not part.startswith("--"):
                # Short flag, might have value attached or separate
                if i + 1 < len(parts) and not parts[i + 1].startswith("-"):
                    normalized_parts.append(f"{part} {parts[i + 1]}")
                    i += 2
                else:
                    normalized_parts.append(part)
                    i += 1
            else:
                normalized_parts.append(part)
                i += 1
        normalized = ";".join(normalized_parts)

    return normalized


def validate_bowtie2_args_cli(args: str | None) -> str:
    """Validate and normalize Bowtie2 arguments from CLI.

    Args:
        args: Bowtie2 arguments from command line

    Returns:
        Normalized and validated argument string

    Raises:
        DREEMInputException: If arguments are invalid
    """
    if args is None:
        return ""

    normalized = normalize_bowtie2_args(args)
    if normalized:
        try:
            validate_bowtie2_args(normalized)
        except DREEMInputException as e:
            raise DREEMInputException(
                f"Invalid Bowtie2 arguments: {e.args[0]}\n"
                f"Provided: {args}\n"
                f"Normalized: {normalized}\n"
                "Tip: Use comma, semicolon, or space-separated arguments like: "
                "'--local,--no-unal,-p 8' or '--local;--no-unal;-p 8'"
            ) from e
    return normalized


# Mapping of CLI argument names to parameter paths
# Format: "cli_arg_name": ("param_path", "log_message_template", default_value)
CLI_ARG_MAPPING = {
    # Mapping options
    "skip_fastqc": (
        ("map", "skip_fastqc"),
        "skipping fastqc for quality control (only do this if you are confident in the quality of your data)",
        False,
    ),
    "skip_trim_galore": (
        ("map", "skip_trim_galore"),
        "skipping trim galore for quality control (not recommended)",
        False,
    ),
    "tg_q_cutoff": (
        ("map", "tg_q_cutoff"),
        "trim galore quality cutoff set to {value}",
        20,
    ),
    "bt2_alignment_args": (
        ("map", "bt2_alignment_args"),
        "bowtie2 alignment arguments set",
        None,
    ),
    "save_unaligned": (
        ("map", "save_unaligned"),
        "saving unaligned reads",
        False,
    ),
    # Bit vector options
    "skip_bit_vector": (
        ("bit_vector", "skip"),
        "skipping bit vector step",
        False,
    ),
    "summary_output_only": (
        ("bit_vector", "summary_output_only"),
        "only outputting summary files",
        False,
    ),
    "plot_sequence": (
        ("bit_vector", "plot_sequence"),
        "plotting sequence/structure on bit vector plots",
        False,
    ),
    "map_score_cutoff": (
        ("bit_vector", "map_score_cutoff"),
        "mapping score cutoff set to {value}",
        15,
    ),
    "qscore_cutoff": (
        ("bit_vector", "qscore_cutoff"),
        "qscore cutoff set to {value}",
        25,
    ),
    "mutation_count_cutoff": (
        ("bit_vector", "stricter_constraints", "mutation_count_cutoff"),
        "mutation count cutoff set to {value} (only active if --stricter-bv-constraints is set)",
        5,
    ),
    "percent_length_cutoff": (
        ("bit_vector", "stricter_constraints", "percent_length_cutoff"),
        "percent length cutoff set to {value} (only active if --stricter-bv-constraints is set)",
        0.1,
    ),
    "min_mut_distance": (
        ("bit_vector", "stricter_constraints", "min_mut_distance"),
        "minimum mutation distance set to {value} (only active if --stricter-bv-constraints is set)",
        5,
    ),
    # Misc options
    "overwrite": (
        ("overwrite",),
        "will overwrite all existing files",
        False,
    ),
    "restore_org_behavior": (
        ("restore_org_behavior",),
        "restoring original behavior of rna_map publications",
        False,
    ),
    "stricter_bv_constraints": (
        ("stricter_bv_constraints",),
        "stricter bit vector constraints are active (please use at your own risk)",
        False,
    ),
}


def _set_nested_param(params: dict, path: tuple[str, ...], value) -> None:
    """Set a nested parameter value.

    Args:
        params: Parameters dictionary
        path: Tuple of keys to navigate to the parameter
        value: Value to set
    """
    current = params
    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[path[-1]] = value


def _handle_bowtie2_args(params: dict, args: dict) -> None:
    """Handle Bowtie2 alignment arguments with presets and individual flags.

    Args:
        params: Parameters dictionary to update
        args: CLI arguments dictionary
    """
    from rna_map.cli.bowtie2 import parse_bowtie2_cli_args

    try:
        bt2_args = parse_bowtie2_cli_args(args)
        if bt2_args:
            _set_nested_param(params, ("map", "bt2_alignment_args"), bt2_args)
            log.info("bowtie2 alignment arguments configured")
    except DREEMInputException as e:
        log.error(str(e))
        raise


def _handle_regular_arg(
    params: dict,
    arg_name: str,
    arg_value,
    param_path: tuple[str, ...],
    log_msg_template: str,
    default_value,
) -> None:
    """Handle a regular CLI argument.

    Args:
        params: Parameters dictionary to update
        arg_name: Name of the CLI argument
        arg_value: Value from CLI
        param_path: Path to parameter in params dict
        log_msg_template: Template for log message
        default_value: Default value to compare against
    """
    if arg_value is None:
        return

    # For flags, check if they're True
    if isinstance(default_value, bool):
        if not arg_value:
            return
        _set_nested_param(params, param_path, True)
        log.info(log_msg_template)
    # For values, check if they differ from default
    else:
        if arg_value == default_value:
            return
        _set_nested_param(params, param_path, arg_value)
        if "{value}" in log_msg_template:
            log.info(log_msg_template.format(value=arg_value))
        else:
            log.info(log_msg_template)


def parse_cli_args(params: dict, args: dict) -> None:
    """Parse CLI arguments and update parameters dictionary.

    This is a cleaner, more maintainable version that uses a mapping
    to handle argument parsing instead of repetitive if statements.

    Args:
        params: Parameters dictionary to update
        args: CLI arguments dictionary
    """
    # Handle Bowtie2 arguments specially (needs normalization and validation)
    _handle_bowtie2_args(params, args)

    # Handle all other arguments using the mapping
    for arg_name, (param_path, log_msg_template, default_value) in CLI_ARG_MAPPING.items():
        if arg_name == "bt2_alignment_args":
            continue  # Already handled above

        _handle_regular_arg(
            params,
            arg_name,
            args.get(arg_name),
            param_path,
            log_msg_template,
            default_value,
        )


def parse_cli_args_to_configs(args: dict, params: dict | None = None) -> tuple[MappingConfig, BitVectorConfig, dict]:
    """Parse CLI arguments into configuration dataclasses.

    This is a newer approach that converts CLI args directly to typed configs,
    which is cleaner and provides better type safety.

    Args:
        args: CLI arguments dictionary
        params: Optional base parameters dictionary (uses defaults if None)

    Returns:
        Tuple of (MappingConfig, BitVectorConfig, misc_params_dict)
    """
    from rna_map.parameters import get_default_params

    if params is None:
        params = get_default_params()

    # Parse CLI args into params dict first
    parse_cli_args(params, args)

    # Convert to configs
    mapping_config = MappingConfig.from_dict(params.get("map", {}))
    bv_config = BitVectorConfig.from_dict(
        params.get("bit_vector", {}),
        use_stricter=params.get("stricter_bv_constraints", False),
    )

    # Extract misc params
    misc_params = {
        "overwrite": params.get("overwrite", False),
        "restore_org_behavior": params.get("restore_org_behavior", False),
        "stricter_bv_constraints": params.get("stricter_bv_constraints", False),
    }

    return mapping_config, bv_config, misc_params

