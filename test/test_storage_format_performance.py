"""Compare performance of TEXT vs JSON storage formats for bit vectors."""

import sys
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from collections import defaultdict

import pytest

TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent

# Add paths
sys.path.insert(0, str(PROJECT_ROOT / "cpp"))
if str(PROJECT_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "lib"))

from rna_map.io.bit_vector_storage import (
    StorageFormat,
    create_storage_writer,
    TextStorageWriter,
    JsonStorageWriter,
)

# Test data paths
TEST_RESOURCES = TEST_DIR / "resources"
FASTA_PATH_CASE1 = TEST_RESOURCES / "case_1" / "test.fasta"
SAM_PATH_CASE1 = TEST_RESOURCES / "case_1" / "output" / "Mapping_Files" / "aligned.sam"
FASTA_PATH_CASE2 = TEST_RESOURCES / "case_2" / "C009J.fasta"
SAM_PATH_CASE2 = TEST_RESOURCES / "case_2" / "output" / "Mapping_Files" / "aligned.sam"


def _read_reference_sequences(fasta_path: Path) -> dict[str, str]:
    """Read reference sequences from FASTA file."""
    ref_seqs = {}
    with open(fasta_path) as f:
        current_name = None
        current_seq = []
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                if current_name:
                    ref_seqs[current_name] = "".join(current_seq)
                current_name = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line)
        if current_name:
            ref_seqs[current_name] = "".join(current_seq)
    return ref_seqs


def _generate_test_bit_vectors(sam_path: Path, ref_seqs: dict[str, str]) -> list[tuple]:
    """Generate test bit vectors from SAM file.
    
    Returns:
        List of tuples: (qname, bit_vector_dict, reads_list)
    """
    from rna_map.analysis.bit_vector_iterator import BitVectorIterator
    
    iterator = BitVectorIterator(
        sam_path, ref_seqs, paired=False, use_pysam=False
    )
    
    bit_vectors = []
    for bit_vector in iterator:
        if bit_vector.data:
            # Get qname from first read
            qname = bit_vector.reads[0].qname if bit_vector.reads else "unknown"
            bit_vectors.append((qname, bit_vector.data, bit_vector.reads))
    
    return bit_vectors


def _write_text_format(
    bit_vectors: list[tuple],
    ref_name: str,
    ref_seq: str,
    output_dir: Path,
) -> float:
    """Write bit vectors in TEXT format and return elapsed time."""
    start_time = time.time()
    
    writer = TextStorageWriter(
        output_dir, ref_name, ref_seq, "DMS", 1, len(ref_seq)
    )
    
    for qname, bit_vector, reads in bit_vectors:
        writer.write_bit_vector(qname, bit_vector, reads)
    
    writer.close()
    
    elapsed_time = time.time() - start_time
    return elapsed_time


def _write_json_format(
    bit_vectors: list[tuple],
    output_dir: Path,
) -> float:
    """Write bit vectors in JSON format and return elapsed time."""
    start_time = time.time()
    
    writer = JsonStorageWriter(output_dir)
    
    for qname, bit_vector, reads in bit_vectors:
        writer.write_bit_vector(qname, bit_vector, reads)
    
    writer.close()
    
    elapsed_time = time.time() - start_time
    return elapsed_time


def _get_file_sizes(output_dir: Path, ref_name: str) -> dict[str, int]:
    """Get file sizes for both formats."""
    text_file = output_dir / f"{ref_name}_bitvectors.txt"
    json_file = output_dir / "muts.json"
    
    sizes = {}
    if text_file.exists():
        sizes["text"] = text_file.stat().st_size
    if json_file.exists():
        sizes["json"] = json_file.stat().st_size
    
    return sizes


@pytest.mark.skipif(
    not SAM_PATH_CASE1.exists() or not FASTA_PATH_CASE1.exists(),
    reason="Case 1 test data not found"
)
def test_storage_format_performance_case1():
    """Test and compare TEXT vs JSON storage format performance - Case 1."""
    _run_storage_performance_test(SAM_PATH_CASE1, FASTA_PATH_CASE1, "Case 1")


@pytest.mark.skipif(
    not SAM_PATH_CASE2.exists() or not FASTA_PATH_CASE2.exists(),
    reason="Case 2 test data not found"
)
def test_storage_format_performance_case2():
    """Test and compare TEXT vs JSON storage format performance - Case 2."""
    _run_storage_performance_test(SAM_PATH_CASE2, FASTA_PATH_CASE2, "Case 2")


def _run_storage_performance_test(sam_path: Path, fasta_path: Path, case_name: str):
    """Run storage format performance test.
    
    Args:
        sam_path: Path to SAM file
        fasta_path: Path to FASTA file
        case_name: Name of test case
    """
    ref_seqs = _read_reference_sequences(fasta_path)
    ref_name = list(ref_seqs.keys())[0]
    ref_seq = ref_seqs[ref_name]
    
    # Generate test bit vectors
    print("\n" + "=" * 80)
    print(f"STORAGE FORMAT PERFORMANCE TEST - {case_name}")
    print("=" * 80)
    print(f"\nGenerating bit vectors from: {sam_path}")
    bit_vectors = _generate_test_bit_vectors(sam_path, ref_seqs)
    print(f"Generated {len(bit_vectors)} bit vectors")
    
    if not bit_vectors:
        pytest.skip("No bit vectors generated")
    
    # Test TEXT format
    with TemporaryDirectory() as tmpdir:
        text_dir = Path(tmpdir) / "text"
        text_dir.mkdir()
        
        print("\n" + "=" * 80)
        print("Testing TEXT Format")
        print("=" * 80)
        text_time = _write_text_format(bit_vectors, ref_name, ref_seq, text_dir)
        text_sizes = _get_file_sizes(text_dir, ref_name)
        
        print(f"Write time: {text_time:.4f}s")
        print(f"File size: {text_sizes.get('text', 0):,} bytes")
        if text_sizes.get('text', 0) > 0:
            print(f"Throughput: {len(bit_vectors) / text_time:.0f} bit vectors/sec")
            print(f"Size per bit vector: {text_sizes['text'] / len(bit_vectors):.1f} bytes")
    
    # Test JSON format
    with TemporaryDirectory() as tmpdir:
        json_dir = Path(tmpdir) / "json"
        json_dir.mkdir()
        
        print("\n" + "=" * 80)
        print("Testing JSON Format")
        print("=" * 80)
        json_time = _write_json_format(bit_vectors, json_dir)
        json_sizes = _get_file_sizes(json_dir, ref_name)
        
        print(f"Write time: {json_time:.4f}s")
        print(f"File size: {json_sizes.get('json', 0):,} bytes")
        if json_sizes.get('json', 0) > 0:
            print(f"Throughput: {len(bit_vectors) / json_time:.0f} bit vectors/sec")
            print(f"Size per bit vector: {json_sizes['json'] / len(bit_vectors):.1f} bytes")
    
    # Comparison
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    
    if text_time > 0 and json_time > 0:
        speedup = text_time / json_time
        print(f"\nWrite Speed:")
        print(f"  TEXT: {text_time:.4f}s")
        print(f"  JSON: {json_time:.4f}s")
        if speedup > 1:
            print(f"  JSON is {speedup:.2f}x faster")
        else:
            print(f"  TEXT is {1/speedup:.2f}x faster")
    
    if text_sizes.get('text', 0) > 0 and json_sizes.get('json', 0) > 0:
        size_ratio = text_sizes['text'] / json_sizes['json']
        print(f"\nFile Size:")
        print(f"  TEXT: {text_sizes['text']:,} bytes")
        print(f"  JSON: {json_sizes['json']:,} bytes")
        print(f"  JSON is {size_ratio:.2f}x smaller")
        print(f"  Size reduction: {(1 - 1/size_ratio)*100:.1f}%")
    
    # Save results
    results = {
        "num_bit_vectors": len(bit_vectors),
        "text": {
            "write_time_seconds": text_time,
            "file_size_bytes": text_sizes.get('text', 0),
            "throughput_bv_per_sec": len(bit_vectors) / text_time if text_time > 0 else 0,
        },
        "json": {
            "write_time_seconds": json_time,
            "file_size_bytes": json_sizes.get('json', 0),
            "throughput_bv_per_sec": len(bit_vectors) / json_time if json_time > 0 else 0,
        },
    }
    
    if text_time > 0 and json_time > 0:
        results["speedup"] = {
            "json_vs_text": text_time / json_time,
        }
    
    if text_sizes.get('text', 0) > 0 and json_sizes.get('json', 0) > 0:
        results["size_ratio"] = {
            "text_vs_json": text_sizes['text'] / json_sizes['json'],
        }
    
    output_file = TEST_DIR / f"storage_format_performance_{case_name.lower().replace(' ', '_')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

