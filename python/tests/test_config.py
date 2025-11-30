"""Tests for configuration dataclasses."""


import pytest

from rna_map.core.config import (
    BitVectorConfig,
    MappingConfig,
    StricterConstraints,
)


def test_mapping_config_defaults():
    """Test MappingConfig with default values."""
    config = MappingConfig()
    assert config.skip_fastqc is False
    assert config.skip_trim_galore is False
    assert config.tg_q_cutoff == 20
    assert "--local" in config.bt2_alignment_args
    assert config.save_unaligned is False


def test_mapping_config_custom():
    """Test MappingConfig with custom values."""
    config = MappingConfig(
        skip_fastqc=True,
        skip_trim_galore=True,
        tg_q_cutoff=25,
        bt2_alignment_args="--local;-p 8",
        save_unaligned=True,
    )
    assert config.skip_fastqc is True
    assert config.skip_trim_galore is True
    assert config.tg_q_cutoff == 25
    assert config.bt2_alignment_args == "--local;-p 8"
    assert config.save_unaligned is True


def test_mapping_config_from_dict():
    """Test MappingConfig.from_dict() method."""
    data = {
        "skip_fastqc": True,
        "skip_trim_galore": False,
        "tg_q_cutoff": 30,
        "bt2_alignment_args": "--local",
        "save_unaligned": False,
    }
    config = MappingConfig.from_dict(data)
    assert config.skip_fastqc is True
    assert config.skip_trim_galore is False
    assert config.tg_q_cutoff == 30
    assert config.bt2_alignment_args == "--local"
    assert config.save_unaligned is False


def test_mapping_config_from_dict_partial():
    """Test MappingConfig.from_dict() with partial data."""
    data = {"skip_fastqc": True}
    config = MappingConfig.from_dict(data)
    assert config.skip_fastqc is True
    assert config.skip_trim_galore is False  # Default value
    assert config.tg_q_cutoff == 20  # Default value


def test_mapping_config_immutable():
    """Test that MappingConfig is immutable."""
    from dataclasses import FrozenInstanceError

    config = MappingConfig()
    with pytest.raises(FrozenInstanceError):
        config.skip_fastqc = True


def test_bit_vector_config_defaults():
    """Test BitVectorConfig with default values."""
    config = BitVectorConfig()
    assert config.qscore_cutoff == 25
    assert config.num_of_surbases == 10
    assert config.map_score_cutoff == 15
    assert config.plot_sequence is False
    assert config.summary_output_only is False
    assert config.stricter_constraints is None


def test_bit_vector_config_with_stricter():
    """Test BitVectorConfig with stricter constraints."""
    stricter = StricterConstraints(
        min_mut_distance=5,
        percent_length_cutoff=0.10,
        mutation_count_cutoff=5,
    )
    config = BitVectorConfig(
        qscore_cutoff=30,
        map_score_cutoff=20,
        stricter_constraints=stricter,
    )
    assert config.qscore_cutoff == 30
    assert config.map_score_cutoff == 20
    assert config.stricter_constraints is not None
    assert config.stricter_constraints.min_mut_distance == 5
    assert config.stricter_constraints.percent_length_cutoff == 0.10
    assert config.stricter_constraints.mutation_count_cutoff == 5


def test_bit_vector_config_from_dict():
    """Test BitVectorConfig.from_dict() method."""
    data = {
        "qscore_cutoff": 30,
        "num_of_surbases": 15,
        "map_score_cutoff": 20,
        "plot_sequence": True,
        "summary_output_only": True,
    }
    config = BitVectorConfig.from_dict(data)
    assert config.qscore_cutoff == 30
    assert config.num_of_surbases == 15
    assert config.map_score_cutoff == 20
    assert config.plot_sequence is True
    assert config.summary_output_only is True
    assert config.stricter_constraints is None


def test_bit_vector_config_from_dict_with_stricter():
    """Test BitVectorConfig.from_dict() with stricter constraints."""
    data = {
        "qscore_cutoff": 25,
        "stricter_constraints": {
            "min_mut_distance": 5,
            "percent_length_cutoff": 0.10,
            "mutation_count_cutoff": 5,
        },
    }
    config = BitVectorConfig.from_dict(data, use_stricter=True)
    assert config.stricter_constraints is not None
    assert config.stricter_constraints.min_mut_distance == 5
    assert config.stricter_constraints.percent_length_cutoff == 0.10
    assert config.stricter_constraints.mutation_count_cutoff == 5


def test_bit_vector_config_from_dict_stricter_disabled():
    """Test BitVectorConfig.from_dict() with use_stricter=False."""
    data = {
        "qscore_cutoff": 25,
        "stricter_constraints": {
            "min_mut_distance": 5,
            "percent_length_cutoff": 0.10,
            "mutation_count_cutoff": 5,
        },
    }
    config = BitVectorConfig.from_dict(data, use_stricter=False)
    assert config.stricter_constraints is None


def test_stricter_constraints_defaults():
    """Test StricterConstraints with default values."""
    constraints = StricterConstraints()
    assert constraints.min_mut_distance == 5
    assert constraints.percent_length_cutoff == 0.10
    assert constraints.mutation_count_cutoff == 5


def test_stricter_constraints_from_dict():
    """Test StricterConstraints.from_dict() method."""
    data = {
        "min_mut_distance": 10,
        "percent_length_cutoff": 0.20,
        "mutation_count_cutoff": 10,
    }
    constraints = StricterConstraints.from_dict(data)
    assert constraints.min_mut_distance == 10
    assert constraints.percent_length_cutoff == 0.20
    assert constraints.mutation_count_cutoff == 10


def test_stricter_constraints_from_dict_partial():
    """Test StricterConstraints.from_dict() with partial data."""
    data = {"min_mut_distance": 10}
    constraints = StricterConstraints.from_dict(data)
    assert constraints.min_mut_distance == 10
    assert constraints.percent_length_cutoff == 0.10  # Default
    assert constraints.mutation_count_cutoff == 5  # Default

