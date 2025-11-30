"""Tests for improved CLI parser."""

import pytest

# CLI module was removed - skip these tests
pytestmark = pytest.mark.skip(reason="rna_map.cli module was removed in Nextflow-first restructure")


def test_normalize_bowtie2_args_comma_separated():
    """Test normalizing comma-separated Bowtie2 arguments."""
    result = normalize_bowtie2_args("--local,--no-unal,-p 8")
    assert result == "--local;--no-unal;-p 8"


def test_normalize_bowtie2_args_semicolon_separated():
    """Test normalizing semicolon-separated Bowtie2 arguments."""
    result = normalize_bowtie2_args("--local;--no-unal;-p 8")
    assert result == "--local;--no-unal;-p 8"


def test_normalize_bowtie2_args_space_separated():
    """Test normalizing space-separated Bowtie2 arguments."""
    result = normalize_bowtie2_args("--local --no-unal -p 8")
    assert result == "--local;--no-unal;-p 8"


def test_normalize_bowtie2_args_none():
    """Test normalizing None or empty Bowtie2 arguments."""
    assert normalize_bowtie2_args(None) == ""
    assert normalize_bowtie2_args("") == ""
    assert normalize_bowtie2_args("   ") == ""


def test_normalize_bowtie2_args_with_values():
    """Test normalizing arguments with values."""
    result = normalize_bowtie2_args("-X 1000,-L 12,-p 16")
    assert result == "-X 1000;-L 12;-p 16"


def test_validate_bowtie2_args_cli_valid():
    """Test validating valid Bowtie2 arguments."""
    result = validate_bowtie2_args_cli("--local,--no-unal,-p 8")
    assert result == "--local;--no-unal;-p 8"


def test_validate_bowtie2_args_cli_invalid():
    """Test validating invalid Bowtie2 arguments raises error."""
    with pytest.raises(DREEMInputException):
        validate_bowtie2_args_cli("--invalid-arg")


def test_parse_cli_args_basic():
    """Test parsing basic CLI arguments."""
    params = get_default_params()
    args = {
        "skip_fastqc": True,
        "map_score_cutoff": 20,
        "overwrite": True,
    }
    parse_cli_args(params, args)
    assert params["map"]["skip_fastqc"] is True
    assert params["bit_vector"]["map_score_cutoff"] == 20
    assert params["overwrite"] is True


def test_parse_cli_args_bowtie2():
    """Test parsing Bowtie2 arguments."""
    params = get_default_params()
    args = {
        "bt2_alignment_args": "--local,--no-unal,-p 8",
    }
    parse_cli_args(params, args)
    assert params["map"]["bt2_alignment_args"] == "--local;--no-unal;-p 8"


def test_parse_cli_args_defaults_ignored():
    """Test that default values are not set."""
    params = get_default_params()
    original_tg_cutoff = params["map"]["tg_q_cutoff"]
    args = {
        "tg_q_cutoff": 20,  # Default value
    }
    parse_cli_args(params, args)
    # Should not change if it's the default
    assert params["map"]["tg_q_cutoff"] == original_tg_cutoff


def test_parse_cli_args_stricter_constraints():
    """Test parsing stricter constraint arguments."""
    params = get_default_params()
    args = {
        "stricter_bv_constraints": True,
        "mutation_count_cutoff": 10,
        "min_mut_distance": 8,
    }
    parse_cli_args(params, args)
    assert params["stricter_bv_constraints"] is True
    assert params["bit_vector"]["stricter_constraints"]["mutation_count_cutoff"] == 10
    assert params["bit_vector"]["stricter_constraints"]["min_mut_distance"] == 8

