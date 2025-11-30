"""Tests for C++ bit vector generation and comparison with Python."""

import sys
import pytest
from pathlib import Path
from rna_map.core.config import BitVectorConfig
from rna_map.pipeline.functions import generate_bit_vectors

from conftest import TEST_DATA_DIR, PROJECT_ROOT

# C++ module path for testing
CPP_MODULE_PATH = PROJECT_ROOT / "cpp"
TEST_RESOURCES = TEST_DATA_DIR / "case_1"


def _check_cpp_available():
    """Check if C++ module is available."""
    try:
        import bit_vector_cpp
        return True
    except ImportError:
        return False


@pytest.mark.skipif(
    not _check_cpp_available(),
    reason="C++ module not available"
)
def test_cpp_implementation_available():
    """Test that C++ implementation can be imported."""
    import bit_vector_cpp
    assert bit_vector_cpp is not None


@pytest.mark.skipif(
    not _check_cpp_available(),
    reason="C++ module not available"
)
def test_cpp_vs_python_comparison():
    """Test that C++ and Python implementations produce same results."""
    import bit_vector_cpp
    
    sam_path = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    fasta_path = TEST_RESOURCES / "test.fasta"
    output_dir = TEST_DIR / "test_output_cpp_comparison"
    output_dir.mkdir(exist_ok=True)
    
    config = BitVectorConfig(
        qscore_cutoff=25,
        num_of_surbases=10,
        map_score_cutoff=15,
        use_cpp=True,
    )
    
    # Generate with C++ and compare with Python
    result = generate_bit_vectors(
        sam_path=sam_path,
        fasta=fasta_path,
        output_dir=output_dir,
        config=config,
        compare_with_python=True,
    )
    
    # Check that comparison file was created
    comparison_file = output_dir / "cpp_python_comparison.json"
    assert comparison_file.exists(), "Comparison file should be created"
    
    import json
    with open(comparison_file) as f:
        comparison = json.load(f)
    
    # Results should match
    assert comparison["summary_match"], "Summary files should match"
    assert comparison["histogram_match"], "Histogram files should match"
    assert len(comparison["differences"]) == 0, f"Differences found: {comparison['differences']}"


@pytest.mark.skipif(
    not _check_cpp_available(),
    reason="C++ module not available"
)
def test_cpp_implementation_basic():
    """Test basic C++ implementation functionality."""
    import bit_vector_cpp
    
    sam_path = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
    fasta_path = TEST_RESOURCES / "test.fasta"
    output_dir = TEST_DIR / "test_output_cpp"
    output_dir.mkdir(exist_ok=True)
    
    config = BitVectorConfig(
        qscore_cutoff=25,
        num_of_surbases=10,
        map_score_cutoff=15,
        use_cpp=True,
    )
    
    result = generate_bit_vectors(
        sam_path=sam_path,
        fasta=fasta_path,
        output_dir=output_dir,
        config=config,
    )
    
    # Check that results were generated
    assert result.summary_path.exists(), "Summary file should be created"
    assert len(result.mutation_histos) > 0, "Mutation histograms should be generated"

