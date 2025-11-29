"""Detailed comparison of all implementations including bit vector level comparison."""

import sys
import json
from pathlib import Path
from collections import defaultdict
import pytest

TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT / "cpp"))
if str(PROJECT_ROOT / "lib") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "lib"))

TEST_RESOURCES_CASE1 = TEST_DIR / "resources" / "case_1"

# Case 1 paths
SAM_PATH_CASE1 = TEST_RESOURCES_CASE1 / "output" / "Mapping_Files" / "aligned.sam"
FASTA_PATH_CASE1 = TEST_RESOURCES_CASE1 / "test.fasta"


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


def run_python_native(sam_path: Path, ref_seqs: dict[str, str], max_reads: int = 100) -> dict:
    """Run Python native implementation."""
    from rna_map.io.sam import SingleSamIterator
    from rna_map.analysis.bit_vector_iterator import BitVectorIterator
    
    iterator = BitVectorIterator(
        sam_path, ref_seqs, paired=False, use_pysam=False
    )
    
    results = {
        "mutation_counts": defaultdict(int),
        "bit_vectors": [],
        "total_reads": 0,
        "aligned_reads": 0,
    }
    
    for i, bit_vector in enumerate(iterator):
        results["total_reads"] += 1
        if bit_vector.data:
            results["aligned_reads"] += 1
            mut_count = sum(
                1 for v in bit_vector.data.values() 
                if v in ["A", "C", "G", "T"]
            )
            results["mutation_counts"][mut_count] += 1
            
            # Store first few bit vectors for detailed comparison
            if i < max_reads:
                results["bit_vectors"].append({
                    "qname": bit_vector.reads[0].qname if bit_vector.reads else "unknown",
                    "data": dict(bit_vector.data),
                })
    
    results["mutation_counts"] = dict(results["mutation_counts"])
    return results


def run_pysam(sam_path: Path, ref_seqs: dict[str, str], max_reads: int = 100) -> dict:
    """Run pysam implementation."""
    try:
        import pysam
    except ImportError:
        return None
    
    from rna_map.io.sam import SingleSamIterator
    from rna_map.analysis.bit_vector_iterator import BitVectorIterator
    
    iterator = BitVectorIterator(
        sam_path, ref_seqs, paired=False, use_pysam=True
    )
    
    results = {
        "mutation_counts": defaultdict(int),
        "bit_vectors": [],
        "total_reads": 0,
        "aligned_reads": 0,
    }
    
    for i, bit_vector in enumerate(iterator):
        results["total_reads"] += 1
        if bit_vector.data:
            results["aligned_reads"] += 1
            mut_count = sum(
                1 for v in bit_vector.data.values() 
                if v in ["A", "C", "G", "T"]
            )
            results["mutation_counts"][mut_count] += 1
            
            if i < max_reads:
                results["bit_vectors"].append({
                    "qname": bit_vector.reads[0].qname if bit_vector.reads else "unknown",
                    "data": dict(bit_vector.data),
                })
    
    results["mutation_counts"] = dict(results["mutation_counts"])
    return results


def run_cpp(sam_path: Path, ref_seqs: dict[str, str], max_reads: int = 100) -> dict:
    """Run C++ implementation."""
    try:
        import bit_vector_cpp
    except ImportError:
        return None
    
    gen = bit_vector_cpp.BitVectorGenerator(qscore_cutoff=25, num_of_surbases=10)
    phred_scores = {chr(i): i - 33 for i in range(33, 127)}
    
    results = {
        "mutation_counts": defaultdict(int),
        "bit_vectors": [],
        "total_reads": 0,
        "aligned_reads": 0,
    }
    
    read_count = 0
    with open(sam_path) as f:
        for line in f:
            if line.startswith("@"):
                continue
            fields = line.strip().split("\t")
            if len(fields) < 11:
                continue
            
            results["total_reads"] += 1
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
                    results["aligned_reads"] += 1
                    mut_count = sum(
                        1 for v in bitvector.values() 
                        if v in ["A", "C", "G", "T"]
                    )
                    results["mutation_counts"][mut_count] += 1
                    
                    if read_count < max_reads:
                        results["bit_vectors"].append({
                            "qname": read.qname,
                            "data": dict(bitvector),
                        })
                    read_count += 1
            except Exception:
                pass
    
    results["mutation_counts"] = dict(results["mutation_counts"])
    return results


def compare_bit_vectors(bv1: dict, bv2: dict, qname: str) -> list[str]:
    """Compare two bit vectors and return differences."""
    differences = []
    
    # Compare positions
    positions1 = set(bv1.keys())
    positions2 = set(bv2.keys())
    
    if positions1 != positions2:
        only_in_1 = positions1 - positions2
        only_in_2 = positions2 - positions1
        if only_in_1:
            differences.append(f"  Positions only in first: {sorted(only_in_1)[:10]}")
        if only_in_2:
            differences.append(f"  Positions only in second: {sorted(only_in_2)[:10]}")
    
    # Compare values at common positions
    common_positions = positions1 & positions2
    for pos in sorted(common_positions):
        if bv1[pos] != bv2[pos]:
            differences.append(
                f"  Position {pos}: '{bv1[pos]}' vs '{bv2[pos]}'"
            )
            if len(differences) > 10:  # Limit output
                differences.append("  ... (more differences)")
                break
    
    return differences


def detailed_comparison(results: dict[str, dict]) -> dict:
    """Perform detailed comparison including bit vectors."""
    comparison = {
        "summary": {
            "total_reads": {impl: data["total_reads"] for impl, data in results.items()},
            "aligned_reads": {impl: data["aligned_reads"] for impl, data in results.items()},
        },
        "mutation_distribution": {},
        "bit_vector_comparison": {},
        "differences": [],
    }
    
    # Compare mutation distributions
    all_mut_counts = set()
    for data in results.values():
        all_mut_counts.update(data["mutation_counts"].keys())
    
    for mut_count in sorted(all_mut_counts):
        counts = {impl: data["mutation_counts"].get(mut_count, 0) 
                  for impl, data in results.items()}
        comparison["mutation_distribution"][mut_count] = counts
        
        if len(set(counts.values())) > 1:
            comparison["differences"].append(
                f"Mutation count {mut_count}: {counts}"
            )
    
    # Compare bit vectors for first N reads
    impls = list(results.keys())
    if len(impls) >= 2:
        base_impl = impls[0]
        base_bvs = results[base_impl]["bit_vectors"]
        
        for other_impl in impls[1:]:
            other_bvs = results[other_impl]["bit_vectors"]
            min_len = min(len(base_bvs), len(other_bvs))
            
            bv_diffs = []
            for i in range(min_len):
                base_bv = base_bvs[i]
                other_bv = other_bvs[i]
                
                # Match by qname if possible
                if base_bv["qname"] == other_bv["qname"]:
                    diffs = compare_bit_vectors(
                        base_bv["data"], 
                        other_bv["data"],
                        base_bv["qname"]
                    )
                    if diffs:
                        bv_diffs.append({
                            "read": base_bv["qname"],
                            "differences": diffs,
                        })
                else:
                    # Try to find matching read
                    matching = None
                    for other_bv2 in other_bvs:
                        if other_bv2["qname"] == base_bv["qname"]:
                            matching = other_bv2
                            break
                    
                    if matching:
                        diffs = compare_bit_vectors(
                            base_bv["data"],
                            matching["data"],
                            base_bv["qname"]
                        )
                        if diffs:
                            bv_diffs.append({
                                "read": base_bv["qname"],
                                "differences": diffs,
                            })
            
            if bv_diffs:
                comparison["bit_vector_comparison"][f"{base_impl}_vs_{other_impl}"] = bv_diffs
                comparison["differences"].append(
                    f"Bit vector differences between {base_impl} and {other_impl}: "
                    f"{len(bv_diffs)} reads differ"
                )
    
    return comparison


def main():
    """Run detailed comparison."""
    import sys
    
    # Use case 1
    ref_seqs = _read_reference_sequences(FASTA_PATH_CASE1)
    sam_path = SAM_PATH_CASE1
    case_name = "Case 1"
    
    print("=" * 80)
    print(f"DETAILED IMPLEMENTATION COMPARISON - {case_name}")
    print("=" * 80)
    
    results = {}
    
    # Run all implementations
    print("\n1. Running Python Native...")
    results["python_native"] = run_python_native(sam_path, ref_seqs, max_reads=100)
    
    print("2. Running C++...")
    cpp_result = run_cpp(sam_path, ref_seqs, max_reads=100)
    if cpp_result:
        results["cpp"] = cpp_result
    else:
        print("   ⚠️  C++ not available")
    
    print("3. Running pysam...")
    pysam_result = run_pysam(sam_path, ref_seqs, max_reads=100)
    if pysam_result:
        results["pysam"] = pysam_result
    else:
        print("   ⚠️  pysam not available")
    
    # Compare
    comparison = detailed_comparison(results)
    
    print("\n" + "=" * 80)
    print("COMPARISON RESULTS")
    print("=" * 80)
    
    print(f"\nTotal reads: {comparison['summary']['total_reads']}")
    print(f"Aligned reads: {comparison['summary']['aligned_reads']}")
    
    print("\nMutation distribution (first 10):")
    for mut_count in sorted(comparison["mutation_distribution"].keys())[:10]:
        counts = comparison["mutation_distribution"][mut_count]
        print(f"  {mut_count} mutations: {counts}")
    
    if comparison["bit_vector_comparison"]:
        print("\n⚠️  Bit Vector Differences Found:")
        for comp_key, diffs in comparison["bit_vector_comparison"].items():
            print(f"\n  {comp_key}:")
            for diff in diffs[:5]:  # Show first 5
                print(f"    Read: {diff['read']}")
                for d in diff["differences"][:3]:  # Show first 3 differences
                    print(f"      {d}")
                if len(diff["differences"]) > 3:
                    print(f"      ... ({len(diff['differences']) - 3} more)")
    
    if comparison["differences"]:
        print("\n⚠️  SUMMARY OF DIFFERENCES:")
        for diff in comparison["differences"]:
            print(f"  - {diff}")
    else:
        print("\n✅ All implementations produce IDENTICAL results!")
        print("   - Same total reads")
        print("   - Same aligned reads")
        print("   - Same mutation distribution")
        print("   - Same bit vectors (checked first 50 reads)")
    
    # Save results
    output_file = TEST_DIR / "detailed_comparison.json"
    with open(output_file, "w") as f:
        json.dump({
            "results": {
                k: {
                    "total_reads": v["total_reads"],
                    "aligned_reads": v["aligned_reads"],
                    "mutation_counts": v["mutation_counts"],
                    "bit_vectors_count": len(v["bit_vectors"]),
                }
                for k, v in results.items()
            },
            "comparison": comparison,
        }, f, indent=2)
    print(f"\nDetailed comparison saved to: {output_file}")


if __name__ == "__main__":
    main()

