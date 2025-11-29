"""Tests for Bowtie2 preset system."""

import pytest

# CLI module was removed - skip these tests
pytestmark = pytest.mark.skip(reason="rna_map.cli module was removed in Nextflow-first restructure")


def test_load_bowtie2_presets():
    """Test loading Bowtie2 presets."""
    presets_data = load_bowtie2_presets()
    assert "presets" in presets_data
    assert "arg_mapping" in presets_data
    assert len(presets_data["presets"]) > 0


def test_get_preset_names():
    """Test getting preset names."""
    names = get_preset_names()
    assert len(names) > 0
    assert "default" in names
    assert isinstance(names, list)


def test_build_bowtie2_args_default_preset():
    """Test building args from default preset."""
    args = build_bowtie2_args(preset="default")
    assert "--local" in args
    assert "--no-unal" in args
    assert "--no-discordant" in args
    assert "--no-mixed" in args
    assert "-X 1000" in args
    assert "-L 12" in args
    assert "-p 16" in args


def test_build_bowtie2_args_with_overrides():
    """Test building args with preset and overrides."""
    overrides = {"threads": 8, "maxins": 2000}
    args = build_bowtie2_args(preset="default", overrides=overrides)
    assert "-p 8" in args  # Override
    assert "-X 2000" in args  # Override
    assert "--local" in args  # From preset
    assert "-L 12" in args  # From preset


def test_build_bowtie2_args_invalid_preset():
    """Test building args with invalid preset raises error."""
    with pytest.raises(DREEMInputException, match="Unknown Bowtie2 preset"):
        build_bowtie2_args(preset="invalid_preset")


def test_build_bowtie2_args_raw_string():
    """Test building args from raw string (backward compatibility)."""
    raw = "--local,--no-unal,-p 8"
    args = build_bowtie2_args(raw_args=raw)
    assert "--local" in args
    assert "--no-unal" in args
    assert "-p 8" in args


def test_build_bowtie2_args_individual_flags():
    """Test building args from individual flags without preset."""
    overrides = {
        "local": True,
        "no_unal": True,
        "threads": 8,
        "maxins": 1000,
    }
    args = build_bowtie2_args(overrides=overrides)
    assert "--local" in args
    assert "--no-unal" in args
    assert "-p 8" in args
    assert "-X 1000" in args


def test_parse_bowtie2_cli_args_preset():
    """Test parsing CLI args with preset."""
    args = {"bt2_preset": "default"}
    result = parse_bowtie2_cli_args(args)
    assert "--local" in result
    assert "--no-unal" in result


def test_parse_bowtie2_cli_args_preset_with_overrides():
    """Test parsing CLI args with preset and individual flags."""
    args = {
        "bt2_preset": "default",
        "bt2_threads": 8,
        "bt2_maxins": 2000,
    }
    result = parse_bowtie2_cli_args(args)
    assert "-p 8" in result
    assert "-X 2000" in result
    assert "--local" in result  # From preset


def test_parse_bowtie2_cli_args_individual_flags():
    """Test parsing CLI args with individual flags only."""
    args = {
        "bt2_local": True,
        "bt2_no_unal": True,
        "bt2_threads": 8,
        "bt2_maxins": 1000,
    }
    result = parse_bowtie2_cli_args(args)
    assert "--local" in result
    assert "--no-unal" in result
    assert "-p 8" in result
    assert "-X 1000" in result


def test_parse_bowtie2_cli_args_raw_string():
    """Test parsing CLI args with raw string (highest priority)."""
    args = {
        "bt2_preset": "default",
        "bt2_alignment_args": "--local,--no-unal,-p 8",
    }
    result = parse_bowtie2_cli_args(args)
    # Raw args should override preset
    assert "--local" in result
    assert "--no-unal" in result
    assert "-p 8" in result
    # Should not have preset-specific args
    assert "-X 1000" not in result


def test_parse_bowtie2_cli_args_sensitive_preset():
    """Test parsing with sensitive preset."""
    args = {"bt2_preset": "sensitive"}
    result = parse_bowtie2_cli_args(args)
    assert "--local" in result
    assert "-L 20" in result  # Longer seed length
    assert "--score-min G,20,15" in result


def test_parse_bowtie2_cli_args_barcoded_preset():
    """Test parsing with barcoded preset."""
    args = {"bt2_preset": "barcoded"}
    result = parse_bowtie2_cli_args(args)
    assert "--local" in result
    assert "--mp 50,30" in result
    assert "--rdg 50,30" in result
    assert "--rfg 50,30" in result

