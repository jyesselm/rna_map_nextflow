"""Bowtie2 argument handling with presets and individual flags."""


import yaml

from rna_map.exception import DREEMInputException
from rna_map.logger import get_logger
from rna_map.settings import get_py_path

log = get_logger("CLI.BOWTIE2")


def load_bowtie2_presets() -> dict:
    """Load Bowtie2 presets from YAML file.

    Returns:
        Dictionary of presets and argument mappings
    """
    preset_file = get_py_path() / "resources" / "bowtie2_presets.yml"
    if not preset_file.exists():
        log.warning(f"Bowtie2 presets file not found: {preset_file}")
        return {"presets": {}, "arg_mapping": {}}

    with open(preset_file) as f:
        return yaml.safe_load(f)


def get_preset_names() -> list[str]:
    """Get list of available preset names.

    Returns:
        List of preset names
    """
    presets_data = load_bowtie2_presets()
    return list(presets_data.get("presets", {}).keys())


def build_bowtie2_args(
    preset: str | None = None,
    overrides: dict | None = None,
    raw_args: str | None = None,
) -> str:
    """Build Bowtie2 argument string from preset and overrides.

    Args:
        preset: Name of preset to use
        overrides: Dictionary of argument overrides
        raw_args: Raw argument string (takes precedence if provided)

    Returns:
        Semicolon-separated argument string

    Raises:
        DREEMInputException: If preset not found
    """
    # If raw args provided, use them directly (for backward compatibility)
    if raw_args:
        from rna_map.cli.parser import normalize_bowtie2_args

        return normalize_bowtie2_args(raw_args)

    presets_data = load_bowtie2_presets()
    presets = presets_data.get("presets", {})
    arg_mapping = presets_data.get("arg_mapping", {})

    # Start with preset args if provided
    args_dict: dict[str, str | int | bool] = {}
    if preset:
        if preset not in presets:
            available = ", ".join(presets.keys())
            raise DREEMInputException(
                f"Unknown Bowtie2 preset: '{preset}'. "
                f"Available presets: {available}"
            )
        preset_data = presets[preset]
        args_dict = preset_data.get("args", {}).copy()
        log.info(f"Using Bowtie2 preset: {preset} - {preset_data.get('description', '')}")

    # Apply overrides
    if overrides:
        args_dict.update(overrides)

    # Convert to argument string
    arg_list = []
    for key, value in args_dict.items():
        if key not in arg_mapping:
            log.warning(f"Unknown Bowtie2 argument key: {key}, skipping")
            continue

        flag = arg_mapping[key]

        # Handle boolean flags
        if isinstance(value, bool):
            if value:
                arg_list.append(flag)
        # Handle arguments with values
        elif value is not None:
            arg_list.append(f"{flag} {value}")

    return ";".join(arg_list)


def _extract_bowtie2_overrides(args: dict) -> dict[str, str | int | bool]:
    """Extract Bowtie2 argument overrides from CLI args.

    Args:
        args: CLI arguments dictionary

    Returns:
        Dictionary of overrides
    """
    overrides: dict[str, str | int | bool] = {}

    # Boolean flags
    flag_mapping = {
        "bt2_local": "local",
        "bt2_end_to_end": "end_to_end",
        "bt2_no_unal": "no_unal",
        "bt2_no_discordant": "no_discordant",
        "bt2_no_mixed": "no_mixed",
    }

    for cli_key, override_key in flag_mapping.items():
        if args.get(cli_key):
            overrides[override_key] = True
            if cli_key == "bt2_end_to_end":
                overrides["local"] = False  # Mutually exclusive

    # Value flags
    value_mapping = {
        "bt2_threads": "threads",
        "bt2_maxins": "maxins",
        "bt2_seed_length": "seed_length",
        "bt2_seed_mismatches": "seed_mismatches",
        "bt2_max_alignments": "max_alignments",
        "bt2_mismatch_penalty": "mismatch_penalty",
        "bt2_gap_penalty_read": "gap_penalty_read",
        "bt2_gap_penalty_ref": "gap_penalty_ref",
        "bt2_score_min": "score_min",
    }

    for cli_key, override_key in value_mapping.items():
        value = args.get(cli_key)
        if value is not None:
            overrides[override_key] = value

    return overrides


def parse_bowtie2_cli_args(args: dict) -> str:
    """Parse Bowtie2 arguments from CLI args dictionary.

    Handles:
    - --bt2-preset: Select a preset
    - Individual flags: --bt2-local, --bt2-threads, etc.
    - --bt2-alignment-args: Raw string (fallback)

    Args:
        args: CLI arguments dictionary

    Returns:
        Semicolon-separated argument string
    """
    # Check for raw args first (highest priority)
    if args.get("bt2_alignment_args"):
        from rna_map.cli.parser import validate_bowtie2_args_cli

        return validate_bowtie2_args_cli(args["bt2_alignment_args"])

    # Build overrides from individual flags
    overrides = _extract_bowtie2_overrides(args)

    # Get preset
    preset = args.get("bt2_preset")

    # Build final args
    try:
        return build_bowtie2_args(
            preset=preset, overrides=overrides if overrides else None
        )
    except DREEMInputException as e:
        log.error(str(e))
        raise

