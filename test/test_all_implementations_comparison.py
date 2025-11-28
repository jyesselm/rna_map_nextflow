"""Compare results from all three implementations: Python native, C++, and pysam."""

import sys
import json
from pathlib import Path
from collections import defaultdict
import pytest

TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent

# Add paths
sys.path.insert(0, str(PROJECT_ROOT / "cpp"))
if str(PROJECT_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "lib"))

TEST_RESOURCES = TEST_DIR / "resources" / "case_1"
SAM_PATH = TEST_RESOURCES / "output" / "Mapping_Files" / "aligned.sam"
FASTA_PATH = TEST_RESOURCES / "test.fasta"


def _check_cpp_available():
    """Check if C++ module is available."""
    try:
        import bit_vector_cpp
        return True
    except ImportError:
        return False


def _check_pysam_available():
    """Check if pysam is available."""
    try:
        import pysam
        return True
    except ImportError:
        return False


def _read_reference_sequences(fasta_path: Path) -> dict[str, str]:
    """Read reference sequences from FASTA file."""
    ref_seqs = {}
    with open(fasta_path) as f:
        current_name = None
        current_seq = []
        for line in f:
            if line.startswith(">"):
                if current_name:
                    ref_seqs[current_name] = "".join(current_seq)
                current_name = line[1:].strip().split()[0]
                current_seq = []
            else:
                current_seq.append(line.strip())
        if current_name:
            ref_seqs[current_name] = "".join(current_seq)
    return ref_seqs


def _parse_phred_scores() -> dict[str, int]:
    """Parse PHRED quality scores."""
    phred_scores = {}
    for i in range(33, 127):
        phred_scores[chr(i)] = i - 33
    return phred_scores


def run_python_native(sam_path: Path, ref_seqs: dict[str, str]) -> dict:
    """Run Python native implementation."""
    from rna_map.io.sam import SingleSamIterator
    from rna_map.analysis.bit_vector_iterator import BitVectorIterator
    
    iterator = BitVectorIterator(
        sam_path, ref_seqs, paired=False, use_pysam=False
    )
    
    mutation_counts = defaultdict(int)
    total_reads = 0
    aligned_reads = 0
    
    for bit_vector in iterator:
        total_reads += 1
        if bit_vector.data:
            aligned_reads += 1
            mut_count = sum(
                1 for v in bit_vector.data.values() 
                if v in ["A", "C", "G", "T"]
            )
            mutation_counts[mut_count] += 1
    
    return {
        "total_reads": total_reads,
        "aligned_reads": aligned_reads,
        "mutation_counts": dict(mutation_counts),
    }


def run_pysam(sam_path: Path, ref_seqs: dict[str, str]) -> dict:
    """Run pysam implementation."""
    if not _check_pysam_available():
        return None
    
    from rna_map.io.sam import SingleSamIterator
    from rna_map.analysis.bit_vector_iterator import BitVectorIterator
    
    iterator = BitVectorIterator(
        sam_path, ref_seqs, paired=False, use_pysam=True
    )
    
    mutation_counts = defaultdict(int)
    total_reads = 0
    aligned_reads = 0
    
    for bit_vector in iterator:
        total_reads += 1
        if bit_vector.data:
            aligned_reads += 1
            mut_count = sum(
                1 for v in bit_vector.data.values() 
                if v in ["A", "C", "G", "T"]
            )
            mutation_counts[mut_count] += 1
    
    return {
        "total_reads": total_reads,
        "aligned_reads": aligned_reads,
        "mutation_counts": dict(mutation_counts),
    }


def run_cpp(sam_path: Path, ref_seqs: dict[str, str]) -> dict:
    """Run C++ implementation."""
    if not _check_cpp_available():
        return None
    
    import bit_vector_cpp
    
    gen = bit_vector_cpp.BitVectorGenerator(qscore_cutoff=25, num_of_surbases=10)
    phred_scores = _parse_phred_scores()
    
    mutation_counts = defaultdict(int)
    total_reads = 0
    aligned_reads = 0
    
    with open(sam_path) as f:
        for line in f:
            if line.startswith("@"):
                continue
            fields = line.strip().split("\t")
            if len(fields) < 11:
                continue
            
            total_reads += 1
            cigar = fields[5]
            if cigar == "*" or not cigar:
                continue
            
            read = bit_vector_cpp.AlignedRead()
            read.qname = fields[0]
            read.flag = fields[1]
            read.rname = fields[2]
            read.pos = int(fields[3])
            read.mapq = int(fields[4])
            read.cigar = cigar
            read.seq = fields[9]
            read.qual = fields[10]
            
            if read.rname not in ref_seqs:
                continue
            
            try:
                ref_seq = ref_seqs[read.rname]
                bitvector = gen.generate_single(read, ref_seq, phred_scores)
                
                if bitvector:
                    aligned_reads += 1
                    mut_count = sum(
                        1 for v in bitvector.values() 
                        if v in ["A", "C", "G", "T"]
                    )
                    mutation_counts[mut_count] += 1
            except Exception:
                pass
    
    return {
        "total_reads": total_reads,
        "aligned_reads": aligned_reads,
        "mutation_counts": dict(mutation_counts),
    }


def compare_results(results: dict[str, dict]) -> dict:
    """Compare results from different implementations."""
    comparison = {
        "implementations": list(results.keys()),
        "total_reads": {},
        "aligned_reads": {},
        "mutation_distribution": {},
        "differences": [],
    }
    
    # Compare total reads
    for impl, data in results.items():
        comparison["total_reads"][impl] = data["total_reads"]
        comparison["aligned_reads"][impl] = data["aligned_reads"]
    
    # Check if totals match
    total_reads_values = list(comparison["total_reads"].values())
    if len(set(total_reads_values)) > 1:
        comparison["differences"].append(
            f"Total reads differ: {comparison['total_reads']}"
        )
    
    aligned_reads_values = list(comparison["aligned_reads"].values())
    if len(set(aligned_reads_values)) > 1:
        comparison["differences"].append(
            f"Aligned reads differ: {comparison['aligned_reads']}"
        )
    
    # Compare mutation distributions
    all_mut_counts = set()
    for data in results.values():
        all_mut_counts.update(data["mutation_counts"].keys())
    
    for mut_count in sorted(all_mut_counts):
        counts = {}
        for impl, data in results.items():
            counts[impl] = data["mutation_counts"].get(mut_count, 0)
        comparison["mutation_distribution"][mut_count] = counts
        
        # Check for differences
        if len(set(counts.values())) > 1:
            comparison["differences"].append(
                f"Mutation count {mut_count}: {counts}"
            )
    
    return comparison


@pytest.mark.skipif(
    not SAM_PATH.exists() or not FASTA_PATH.exists(),
    reason="Test data not found"
)
def test_all_implementations_comparison():
    """Test and compare all three implementations."""
    ref_seqs = _read_reference_sequences(FASTA_PATH)
    
    results = {}
    
    # Run Python native
    print("\n" + "=" * 80)
    print("Running Python Native Implementation")
    print("=" * 80)
    results["python_native"] = run_python_native(SAM_PATH, ref_seqs)
    print(f"Total reads: {results['python_native']['total_reads']}")
    print(f"Aligned reads: {results['python_native']['aligned_reads']}")
    
    # Run C++
    if _check_cpp_available():
        print("\n" + "=" * 80)
        print("Running C++ Implementation")
        print("=" * 80)
        results["cpp"] = run_cpp(SAM_PATH, ref_seqs)
        if results["cpp"]:
            print(f"Total reads: {results['cpp']['total_reads']}")
            print(f"Aligned reads: {results['cpp']['aligned_reads']}")
    else:
        print("\n⚠️  C++ implementation not available")
    
    # Run pysam
    if _check_pysam_available():
        print("\n" + "=" * 80)
        print("Running pysam Implementation")
        print("=" * 80)
        results["pysam"] = run_pysam(SAM_PATH, ref_seqs)
        if results["pysam"]:
            print(f"Total reads: {results['pysam']['total_reads']}")
            print(f"Aligned reads: {results['pysam']['aligned_reads']}")
    else:
        print("\n⚠️  pysam not available (install with: pip install pysam)")
    
    # Compare results
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    comparison = compare_results(results)
    
    print(f"\nTotal reads: {comparison['total_reads']}")
    print(f"Aligned reads: {comparison['aligned_reads']}")
    
    print("\nMutation distribution:")
    for mut_count in sorted(comparison["mutation_distribution"].keys()):
        counts = comparison["mutation_distribution"][mut_count]
        print(f"  {mut_count} mutations: {counts}")
    
    if comparison["differences"]:
        print("\n⚠️  DIFFERENCES FOUND:")
        for diff in comparison["differences"]:
            print(f"  - {diff}")
    else:
        print("\n✅ All implementations produce identical results!")
    
    # Save comparison to file
    output_file = TEST_DIR / "implementation_comparison.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": results,
            "comparison": comparison,
        }, f, indent=2)
    print(f"\nComparison saved to: {output_file}")
    
    # Assertions
    assert len(results) >= 1, "At least one implementation should run"
    
    if len(results) > 1:
        # Check that all implementations produce same results
        if comparison["differences"]:
            pytest.fail(
                f"Implementations produce different results: "
                f"{comparison['differences']}"
            )


if __name__ == "__main__":
    # Run as script
    ref_seqs = _read_reference_sequences(FASTA_PATH)
    
    results = {}
    
    print("=" * 80)
    print("IMPLEMENTATION COMPARISON TEST")
    print("=" * 80)
    
    # Run Python native
    print("\n1. Running Python Native Implementation...")
    results["python_native"] = run_python_native(SAM_PATH, ref_seqs)
    
    # Run C++
    if _check_cpp_available():
        print("\n2. Running C++ Implementation...")
        results["cpp"] = run_cpp(SAM_PATH, ref_seqs)
    else:
        print("\n2. C++ implementation not available")
    
    # Run pysam
    if _check_pysam_available():
        print("\n3. Running pysam Implementation...")
        results["pysam"] = run_pysam(SAM_PATH, ref_seqs)
    else:
        print("\n3. pysam not available (install with: pip install pysam)")
    
    # Compare
    comparison = compare_results(results)
    
    print("\n" + "=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print(f"\nTotal reads: {comparison['total_reads']}")
    print(f"Aligned reads: {comparison['aligned_reads']}")
    
    print("\nMutation distribution:")
    for mut_count in sorted(comparison["mutation_distribution"].keys())[:10]:
        counts = comparison["mutation_distribution"][mut_count]
        print(f"  {mut_count} mutations: {counts}")
    
    if comparison["differences"]:
        print("\n⚠️  DIFFERENCES:")
        for diff in comparison["differences"]:
            print(f"  - {diff}")
    else:
        print("\n✅ All implementations produce identical results!")

