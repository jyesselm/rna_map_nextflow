"""Tests for mutation tracking presets."""

import pytest

from rna_map.cli.bowtie2 import build_bowtie2_args


def test_mutation_single_preset():
    """Test mutation_single preset has correct parameters."""
    args = build_bowtie2_args(preset="mutation_single")
    
    # Critical parameters
    assert "-N 1" in args  # Seed mismatches = 1 (CRITICAL)
    assert "-L 10" in args  # Short seed length
    assert "-X 300" in args  # Optimized insert size
    assert "--mp 6,2" in args  # Lower mismatch penalty
    assert "--score-min L,0,-0.6" in args  # Lower score threshold
    assert "--local" in args  # Local alignment


def test_mutation_similar_preset():
    """Test mutation_similar preset has correct parameters."""
    args = build_bowtie2_args(preset="mutation_similar")
    
    # Should have same mutation-optimized params
    assert "-N 1" in args
    assert "-L 10" in args
    assert "-X 300" in args
    
    # Plus multiple alignments
    assert "-k 10" in args  # Report multiple alignments
    
    # Should NOT suppress unaligned (for analysis)
    assert "--no-unal" not in args


def test_mutation_large_preset():
    """Test mutation_large preset balances speed and sensitivity."""
    args = build_bowtie2_args(preset="mutation_large")
    
    # Still has critical mutation params
    assert "-N 1" in args  # Still allows seed mismatches
    assert "-X 300" in args  # Still optimized insert size
    
    # But optimized for speed
    assert "-L 12" in args  # Slightly longer seed (faster)
    assert "--fast-local" in args  # Faster alignment mode
    assert "--score-min L,0,-0.4" in args  # Slightly higher threshold


def test_mutation_presets_vs_default():
    """Test that mutation presets differ from default in key ways."""
    default_args = build_bowtie2_args(preset="default")
    mutation_args = build_bowtie2_args(preset="mutation_single")
    
    # Default should NOT have seed mismatches
    assert "-N 1" not in default_args or "-N 0" in default_args
    
    # Mutation preset MUST have seed mismatches
    assert "-N 1" in mutation_args
    
    # Default has larger insert size
    assert "-X 1000" in default_args
    
    # Mutation preset has optimized insert size
    assert "-X 300" in mutation_args


def test_mutation_preset_overrides():
    """Test that mutation preset can be overridden."""
    overrides = {"maxins": 250, "threads": 8}
    args = build_bowtie2_args(preset="mutation_single", overrides=overrides)
    
    # Override should take effect
    assert "-X 250" in args
    assert "-p 8" in args
    
    # But critical mutation params should remain
    assert "-N 1" in args
    assert "-L 10" in args

