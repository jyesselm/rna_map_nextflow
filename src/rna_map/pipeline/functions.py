"""Functional APIs for RNA MAP pipeline components.

These functions provide stateless, composable interfaces to pipeline components.
They can be used independently or in any order, unlike the class-based APIs.
"""

import os
from pathlib import Path
import pickle

from rna_map.analysis.mutation_histogram import MutationHistogram
from rna_map.core.config import BitVectorConfig
from rna_map.core.results import BitVectorResult
from rna_map.logger import get_logger
from rna_map.pipeline.bit_vector_generator import BitVectorGenerator

log = get_logger("PIPELINE.FUNCTIONS")


def generate_bit_vectors(
    sam_path: Path,
    fasta: Path,
    output_dir: Path,
    config: BitVectorConfig,
    csv_file: Path | None = None,
    paired: bool | None = None,
    use_stricter_constraints: bool = False,
    compare_with_python: bool = False,
) -> BitVectorResult:
    """Generate bit vectors from SAM file and return result.

    This is a functional, stateless API that can be used independently.
    This function is used by the Nextflow workflow to generate bit vectors from SAM files.

    Args:
        sam_path: Path to SAM file (can be from anywhere)
        fasta: Path to FASTA file
        output_dir: Output directory for bit vector files
        config: Bit vector configuration
        csv_file: Optional CSV file with structure info
        paired: Whether reads are paired-end (auto-detected if None)
        use_stricter_constraints: Whether to apply stricter constraints
        compare_with_python: If using C++, also run Python version and compare

    Returns:
        BitVectorResult with mutation histograms and output paths

    Example:
        >>> from rna_map.core.config import BitVectorConfig
        >>> config = BitVectorConfig(map_score_cutoff=20)
        >>> result = generate_bit_vectors(
        ...     sam_path=Path("aligned.sam"),
        ...     fasta=Path("ref.fa"),
        ...     output_dir=Path("output"),
        ...     config=config
        ... )
        >>> print(result.summary_path)
    """
    # Try C++ implementation if requested and available
    if config.use_cpp:
        try:
            # Import the wrapper module, not the C++ module directly
            # The wrapper handles the C++ module import and avoids double registration
            from rna_map.pipeline import _cpp_bit_vectors as cpp_wrapper
            
            if not cpp_wrapper.CPP_AVAILABLE:
                raise ImportError("C++ bit vector module not available")
            
            log.info("Attempting to use C++ implementation...")
            result_cpp = cpp_wrapper.generate_bit_vectors_cpp(
                sam_path=sam_path,
                fasta=fasta,
                output_dir=output_dir,
                config=config,
                csv_file=csv_file,
                paired=paired,
                use_stricter_constraints=use_stricter_constraints,
            )
            
            log.info("C++ implementation completed successfully")
            
            # Compare with Python if requested
            if compare_with_python:
                result_py = _generate_bit_vectors_python(
                    sam_path, fasta, output_dir, config,
                    csv_file, paired, use_stricter_constraints
                )
                _compare_results(result_cpp, result_py, output_dir)
            
            return result_cpp
        except ImportError as e:
            log.warning(f"C++ implementation requested but not available: {e}, falling back to Python")
        except Exception as e:
            log.warning(f"C++ implementation failed: {e}, falling back to Python")
    
    # Use Python implementation
    return _generate_bit_vectors_python(
        sam_path, fasta, output_dir, config,
        csv_file, paired, use_stricter_constraints
    )


def _generate_bit_vectors_python(
    sam_path: Path,
    fasta: Path,
    output_dir: Path,
    config: BitVectorConfig,
    csv_file: Path | None = None,
    paired: bool | None = None,
    use_stricter_constraints: bool = False,
) -> BitVectorResult:
    """Generate bit vectors using Python implementation (internal)."""
    # Auto-detect paired-end if not specified
    if paired is None:
        # Simple heuristic: check if SAM has paired reads
        # This is a basic check - could be improved
        try:
            with open(sam_path) as f:
                first_line = f.readline()
                while first_line.startswith("@"):
                    first_line = f.readline()
                # Paired-end SAM files have flags indicating pairing
                if "\t" in first_line:
                    parts = first_line.split("\t")
                    if len(parts) > 1:
                        flag = int(parts[1]) if parts[1].isdigit() else 0
                        # Check if flag indicates paired (bit 0x1)
                        paired = (flag & 0x1) != 0
                    else:
                        paired = False
                else:
                    paired = False
        except Exception:
            # Fallback: assume single-end if detection fails
            paired = False

    # Build directory structure
    bv_dir = output_dir / "BitVector_Files"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(bv_dir, exist_ok=True)

    # Create temporary params dict for BitVectorGenerator class
    params = {
        "overwrite": True,  # Always overwrite in functional API
        "restore_org_behavior": False,
        "stricter_bv_constraints": use_stricter_constraints,
        "dirs": {"output": str(output_dir)},
        "bit_vector": {
            "qscore_cutoff": config.qscore_cutoff,
            "num_of_surbases": config.num_of_surbases,
            "map_score_cutoff": config.map_score_cutoff,
            "plot_sequence": config.plot_sequence,
            "summary_output_only": config.summary_output_only,
            "storage_format": config.storage_format.value,
        },
        "restore_org_behavior": False,
        "stricter_bv_constraints": use_stricter_constraints,
    }

    if config.stricter_constraints:
        params["bit_vector"]["stricter_constraints"] = {
            "min_mut_distance": config.stricter_constraints.min_mut_distance,
            "percent_length_cutoff": config.stricter_constraints.percent_length_cutoff,
            "mutation_count_cutoff": config.stricter_constraints.mutation_count_cutoff,
        }

    # Use existing BitVectorGenerator class (maintains backward compatibility)
    generator = BitVectorGenerator()
    generator.setup(params)
    generator.run(
        sam_path=sam_path,
        fasta=fasta,
        paired=paired,
        csv_file=csv_file if csv_file else Path(""),
    )

    # Load mutation histograms from pickle file (generated by BitVectorGenerator)
    pickle_file = bv_dir / "mutation_histos.p"
    mut_histos: dict[str, MutationHistogram] = {}
    if pickle_file.exists():
        with open(pickle_file, "rb") as f:
            mut_histos = pickle.load(f)

    summary_path = bv_dir / "summary.csv"
    return BitVectorResult(
        mutation_histos=mut_histos,
        summary_path=summary_path,
        output_dir=bv_dir,
    )


def _compare_results(
    result_cpp: BitVectorResult,
    result_py: BitVectorResult,
    output_dir: Path,
) -> None:
    """Compare C++ and Python results and log differences.
    
    Args:
        result_cpp: Result from C++ implementation
        result_py: Result from Python implementation
        output_dir: Output directory for comparison report
    """
    import json
    from pathlib import Path
    
    comparison = {
        "summary_match": False,
        "histogram_match": False,
        "differences": [],
    }
    
    # Compare summary files
    if result_cpp.summary_path.exists() and result_py.summary_path.exists():
        import pandas as pd
        df_cpp = pd.read_csv(result_cpp.summary_path)
        df_py = pd.read_csv(result_py.summary_path)
        
        if df_cpp.equals(df_py):
            comparison["summary_match"] = True
        else:
            comparison["differences"].append("Summary CSV files differ")
            # Save diff
            diff_file = output_dir / "comparison_summary_diff.csv"
            df_diff = df_cpp.compare(df_py)
            df_diff.to_csv(diff_file)
            log.warning(f"Summary files differ, diff saved to {diff_file}")
    
    # Compare mutation histograms
    if result_cpp.mutation_histos and result_py.mutation_histos:
        cpp_keys = set(result_cpp.mutation_histos.keys())
        py_keys = set(result_py.mutation_histos.keys())
        
        if cpp_keys != py_keys:
            comparison["differences"].append(
                f"Histogram keys differ: C++={cpp_keys}, Python={py_keys}"
            )
        else:
            all_match = True
            for key in cpp_keys:
                mh_cpp = result_cpp.mutation_histos[key]
                mh_py = result_py.mutation_histos[key]
                
                if mh_cpp.num_reads != mh_py.num_reads:
                    comparison["differences"].append(
                        f"{key}: num_reads differs (C++={mh_cpp.num_reads}, Python={mh_py.num_reads})"
                    )
                    all_match = False
                if mh_cpp.num_aligned != mh_py.num_aligned:
                    comparison["differences"].append(
                        f"{key}: num_aligned differs (C++={mh_cpp.num_aligned}, Python={mh_py.num_aligned})"
                    )
                    all_match = False
                if mh_cpp.num_of_mutations != mh_py.num_of_mutations:
                    comparison["differences"].append(
                        f"{key}: num_of_mutations differs (C++={mh_cpp.num_of_mutations}, Python={mh_py.num_of_mutations})"
                    )
                    all_match = False
            
            comparison["histogram_match"] = all_match
    
    # Save comparison report
    comparison_file = output_dir / "cpp_python_comparison.json"
    with open(comparison_file, "w") as f:
        json.dump(comparison, f, indent=2)
    
    if comparison["summary_match"] and comparison["histogram_match"]:
        log.info("✅ C++ and Python implementations produce identical results")
    else:
        log.warning(f"⚠️  C++ and Python implementations differ. See {comparison_file}")
        for diff in comparison["differences"]:
            log.warning(f"  - {diff}")

