"""
test bit_vector module
"""
import os
import shutil
import pytest
from pathlib import Path
from rna_map.io.fasta import fasta_to_dict
from rna_map.core.config import BitVectorConfig
from rna_map.analysis.bit_vector_iterator import BitVectorIterator
from rna_map.pipeline.bit_vector_generator import BitVectorGenerator
from conftest import TEST_DATA_DIR
# Test data is in test/data/resources/ (relative to project root)
PROJECT_ROOT = Path(TEST_DIR).parent.parent
TEST_DATA_DIR = PROJECT_ROOT / "test" / "data" / "resources"


@pytest.mark.quick
def test_bit_vector_iterator():
    """
    test bit vector iterator
    """
    fa_path = TEST_DATA_DIR / "case_1" / "test.fasta"
    ref_seqs = fasta_to_dict(fa_path)
    sam_path = TEST_DATA_DIR / "case_1" / "output" / "Mapping_Files" / "aligned.sam"
    bit_vector_iter = BitVectorIterator(sam_path, ref_seqs, False)
    bit_vector = next(bit_vector_iter)
    assert len(bit_vector.data) == 146
    count = 0
    for _ in bit_vector_iter:
        count += 1
    assert count == 2356


@pytest.mark.quick
def test_bit_vector_generator():
    """
    test bit vector generation
    """
    # setup_applevel_logger()
    fa_path = TEST_DATA_DIR / "case_1" / "test.fasta"
    sam_path = TEST_DATA_DIR / "case_1" / "output" / "Mapping_Files" / "aligned.sam"
    # Create default config
    config = BitVectorConfig()
    # Use the functional API instead of the class-based one
    from rna_map.pipeline.functions import generate_bit_vectors
    result = generate_bit_vectors(
        sam_path=sam_path,
        fasta=fa_path,
        output_dir=Path("output"),
        config=config,
        paired=False
    )
    assert result.summary_path.exists()
    shutil.rmtree("output")
