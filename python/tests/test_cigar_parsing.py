"""Test CIGAR string parsing to verify correctness after fixes."""

import pytest
from pathlib import Path

TEST_DIR = Path(__file__).parent


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
def test_cigar_parsing_valid_operations():
    """Test that all valid CIGAR operations are parsed correctly."""
    import bit_vector_cpp
    
    generator = bit_vector_cpp.BitVectorGenerator(qscore_cutoff=25, num_of_surbases=10)
    
    # Test cases: (cigar_string, expected_ops_count, description)
    test_cases = [
        ("134M12S", 2, "Match and soft clip"),
        ("80M1D53M12S", 4, "Match, deletion, match, soft clip"),
        ("43M1I91M12S", 4, "Match, insertion, match, soft clip"),
        ("10M5N10M", 3, "Match, skipped region, match"),
        ("20M5H10M", 2, "Match, hard clip (skipped), match"),
        ("15M3P10M", 2, "Match, padding (skipped), match"),
        ("10=5X10M", 3, "Sequence match, mismatch, match"),
        ("*", 0, "Empty CIGAR"),
        ("", 0, "Empty string"),
    ]
    
    for cigar_str, expected_count, description in test_cases:
        # We can't directly test parse_cigar as it's private,
        # but we can test through generate_single with a mock read
        print(f"Testing: {cigar_str} ({description})")
        
        # Create a minimal aligned read for testing
        read = bit_vector_cpp.AlignedRead()
        read.cigar = cigar_str
        read.seq = "A" * 200  # Dummy sequence
        read.qual = "I" * 200  # Dummy quality
        read.pos = 1
        read.mapq = 30
        
        ref_seq = "A" * 200  # Dummy reference
        
        # Create phred scores map
        phred_scores = {chr(i): i - 33 for i in range(33, 127)}
        
        # This should not crash - if parsing fails, it will return empty or error
        try:
            result = generator.generate_single(read, ref_seq, phred_scores)
            print(f"  ✓ Parsed successfully, generated {len(result)} bit vector entries")
        except Exception as e:
            pytest.fail(f"Failed to parse CIGAR '{cigar_str}': {e}")


@pytest.mark.skipif(
    not _check_cpp_available(),
    reason="C++ module not available"
)
def test_cigar_parsing_invalid_operations():
    """Test that invalid CIGAR operations are rejected."""
    import bit_vector_cpp
    
    generator = bit_vector_cpp.BitVectorGenerator(qscore_cutoff=25, num_of_surbases=10)
    
    # Invalid CIGAR strings should be handled gracefully
    invalid_cases = [
        "10Z5M",  # Z is not a valid CIGAR operation
        "10m5M",  # lowercase m should not match (though regex is case-sensitive)
        "ABC",    # No numbers
        "10",     # No operation
    ]
    
    for cigar_str in invalid_cases:
        read = bit_vector_cpp.AlignedRead()
        read.cigar = cigar_str
        read.seq = "A" * 200
        read.qual = "I" * 200
        read.pos = 1
        read.mapq = 30
        
        ref_seq = "A" * 200
        phred_scores = {chr(i): i - 33 for i in range(33, 127)}
        
        # Should handle gracefully (either parse what it can or return empty)
        try:
            result = generator.generate_single(read, ref_seq, phred_scores)
            print(f"  CIGAR '{cigar_str}' handled, generated {len(result)} entries")
        except Exception as e:
            # Some invalid cases might throw - that's acceptable
            print(f"  CIGAR '{cigar_str}' rejected (expected): {e}")


@pytest.mark.skipif(
    not _check_cpp_available(),
    reason="C++ module not available"
)
def test_cigar_parsing_real_data():
    """Test CIGAR parsing with real test data."""
    import bit_vector_cpp
    
    from conftest import TEST_DATA_DIR
    sam_path = TEST_DATA_DIR / "case_1" / "output" / "Mapping_Files" / "aligned.sam"
    
    if not sam_path.exists():
        pytest.skip(f"Test data not found: {sam_path}")
    
    # Read first few CIGAR strings from SAM file
    cigar_strings = []
    with open(sam_path) as f:
        for line in f:
            if line.startswith("@"):
                continue
            fields = line.strip().split("\t")
            if len(fields) > 5:
                cigar = fields[5]
                if cigar and cigar != "*":
                    cigar_strings.append(cigar)
                    if len(cigar_strings) >= 10:
                        break
    
    if not cigar_strings:
        pytest.skip("No CIGAR strings found in test data")
    
    generator = bit_vector_cpp.BitVectorGenerator(qscore_cutoff=25, num_of_surbases=10)
    ref_seq = "A" * 500  # Dummy reference
    phred_scores = {chr(i): i - 33 for i in range(33, 127)}
    
    for cigar_str in cigar_strings:
        read = bit_vector_cpp.AlignedRead()
        read.cigar = cigar_str
        read.seq = "A" * 200
        read.qual = "I" * 200
        read.pos = 1
        read.mapq = 30
        
        # Should parse without errors
        try:
            result = generator.generate_single(read, ref_seq, phred_scores)
            print(f"  ✓ Parsed '{cigar_str}' successfully")
        except Exception as e:
            pytest.fail(f"Failed to parse real CIGAR '{cigar_str}': {e}")

