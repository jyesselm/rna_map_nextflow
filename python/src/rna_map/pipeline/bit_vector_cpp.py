"""C++ implementation wrapper for bit vector generation."""

import sys
from pathlib import Path
from typing import Optional

# Try to import C++ module
# The .so file might be in the same directory, so we need to import it carefully
_module_paths = [
    Path(__file__).parent,  # Same directory as this file
    Path(__file__).parent.parent.parent.parent / "cpp",  # Project root / cpp
]
for path in _module_paths:
    if path.exists() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Try importing the C++ module directly
# If there's a .so file in the same directory, Python will import that instead
# So we need to import it as a compiled extension
try:
    # Try importing from the current directory first (where .so might be)
    import importlib.util
    so_file = Path(__file__).parent / "bit_vector_cpp.cpython-311-darwin.so"
    if not so_file.exists():
        # Try other possible names
        import glob
        so_files = list(Path(__file__).parent.glob("bit_vector_cpp*.so"))
        if so_files:
            so_file = so_files[0]
    
    if so_file.exists():
        spec = importlib.util.spec_from_file_location("_bit_vector_cpp_impl", so_file)
        bit_vector_cpp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bit_vector_cpp)
        CPP_AVAILABLE = True
    else:
        # Try normal import
        import bit_vector_cpp
        CPP_AVAILABLE = True
except (ImportError, FileNotFoundError, AttributeError):
    CPP_AVAILABLE = False

from rna_map.io.sam import AlignedRead
from rna_map.io.fasta import fasta_to_dict
from rna_map.io.fastq import parse_phred_qscore_file
from rna_map import settings
from rna_map.logger import get_logger

log = get_logger("PIPELINE.BIT_VECTOR_CPP")


def generate_bit_vectors_cpp(
    sam_path: Path,
    fasta: Path,
    output_dir: Path,
    config,
    csv_file: Optional[Path] = None,
    paired: Optional[bool] = None,
    use_stricter_constraints: bool = False,
):
    """Generate bit vectors using C++ implementation.
    
    Args:
        sam_path: Path to SAM file
        fasta: Path to FASTA file
        output_dir: Output directory
        config: BitVectorConfig object
        csv_file: Optional CSV file (not used in C++ version yet)
        paired: Whether reads are paired-end
        use_stricter_constraints: Whether to use stricter constraints (not used in C++ yet)
    
    Returns:
        BitVectorResult object
    """
    if not CPP_AVAILABLE:
        raise ImportError("C++ bit vector module not available. Install with: pip install -e .")
    
    # Load reference sequences
    ref_seqs = fasta_to_dict(fasta)
    
    # Load PHRED quality scores
    phred_qscores = parse_phred_qscore_file(
        settings.get_py_path() / "resources" / "phred_ascii.txt"
    )
    
    # Convert to C++ format
    ref_seqs_cpp = {str(k): str(v) for k, v in ref_seqs.items()}
    phred_qscores_cpp = {k: v for k, v in phred_qscores.items()}
    
    # Auto-detect paired-end if not specified
    if paired is None:
        try:
            with open(sam_path) as f:
                first_line = f.readline()
                while first_line.startswith("@"):
                    first_line = f.readline()
                if "\t" in first_line:
                    parts = first_line.split("\t")
                    if len(parts) > 1:
                        flag = int(parts[1]) if parts[1].isdigit() else 0
                        paired = (flag & 0x1) != 0
                    else:
                        paired = False
                else:
                    paired = False
        except Exception:
            paired = False
    
    # Create C++ generator
    generator = bit_vector_cpp.BitVectorGenerator(
        qscore_cutoff=config.qscore_cutoff,
        num_of_surbases=config.num_of_surbases
    )
    
    # Use Python SAM iterator directly (avoid BitVectorIterator which has recursion bug)
    from rna_map.io.sam import SingleSamIterator, PairedSamIterator
    from rna_map.core.bit_vector import BitVector
    from rna_map.core.results import BitVectorResult
    from rna_map.analysis.mutation_histogram import MutationHistogram
    import pickle
    import os
    
    log.info("Using C++ implementation for bit vector generation")
    
    bv_dir = output_dir / "BitVector_Files"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(bv_dir, exist_ok=True)
    
    # Use Python SAM iterator directly
    if paired:
        sam_iterator = PairedSamIterator(str(sam_path), ref_seqs)
    else:
        sam_iterator = SingleSamIterator(str(sam_path), ref_seqs)
    
    # Generate bit vectors using C++
    bit_vectors = []
    try:
        for reads in sam_iterator:
            if not reads:
                continue
            
            # Convert Python AlignedRead to C++ AlignedRead
            read1_cpp = bit_vector_cpp.AlignedRead()
            read1_cpp.qname = reads[0].qname
            read1_cpp.flag = reads[0].flag
            read1_cpp.rname = reads[0].rname
            read1_cpp.pos = reads[0].pos
            read1_cpp.mapq = reads[0].mapq
            read1_cpp.cigar = reads[0].cigar
            read1_cpp.rnext = reads[0].rnext
            read1_cpp.pnext = reads[0].pnext
            read1_cpp.tlen = reads[0].tlen
            read1_cpp.seq = reads[0].seq
            read1_cpp.qual = reads[0].qual
            read1_cpp.md_string = reads[0].md_string
            
            ref_seq = ref_seqs[reads[0].rname]
            
            if paired and len(reads) > 1:
                read2_cpp = bit_vector_cpp.AlignedRead()
                read2_cpp.qname = reads[1].qname
                read2_cpp.flag = reads[1].flag
                read2_cpp.rname = reads[1].rname
                read2_cpp.pos = reads[1].pos
                read2_cpp.mapq = reads[1].mapq
                read2_cpp.cigar = reads[1].cigar
                read2_cpp.rnext = reads[1].rnext
                read2_cpp.pnext = reads[1].pnext
                read2_cpp.tlen = reads[1].tlen
                read2_cpp.seq = reads[1].seq
                read2_cpp.qual = reads[1].qual
                read2_cpp.md_string = reads[1].md_string
                
                # Generate bit vector using C++
                data_cpp = generator.generate_paired(read1_cpp, read2_cpp, ref_seq, phred_qscores_cpp)
            else:
                # Generate bit vector using C++
                data_cpp = generator.generate_single(read1_cpp, ref_seq, phred_qscores_cpp)
            
            # Convert back to Python format
            data_py = {int(k): str(v) for k, v in data_cpp.items()}
            bv = BitVector(reads=reads, data=data_py)
            bit_vectors.append(bv)
    except StopIteration:
        pass
    
    # Now process bit vectors through Python pipeline for histograms
    
    # Generate mutation histograms (reuse Python code for this)
    from rna_map.pipeline.bit_vector_generator import BitVectorGenerator
    mut_histos: dict[str, MutationHistogram] = {}
    
    # Create temporary params for BitVectorGenerator to process histograms
    params = {
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
    
    # Use Python BitVectorGenerator for histogram generation and output
    # Create a custom iterator that yields our C++-generated bit vectors
    class CppBitVectorIterator:
        def __init__(self, bit_vectors):
            self.bit_vectors = bit_vectors
            self.index = 0
        
        def __iter__(self):
            return self
        
        def __next__(self):
            if self.index >= len(self.bit_vectors):
                raise StopIteration
            bv = self.bit_vectors[self.index]
            self.index += 1
            return bv
    
    generator_py = BitVectorGenerator()
    generator_py.setup(params)
    
    # Replace the iterator with our C++-generated bit vectors
    generator_py._BitVectorGenerator__bit_vec_iterator = CppBitVectorIterator(bit_vectors)
    generator_py._BitVectorGenerator__ref_seqs = ref_seqs
    generator_py._BitVectorGenerator__map_score_cutoff = config.map_score_cutoff
    generator_py._BitVectorGenerator__csv_file = csv_file if csv_file else Path("")
    generator_py._BitVectorGenerator__summary_only = config.summary_output_only
    
    # Process bit vectors to generate histograms
    generator_py._BitVectorGenerator__mut_histos = {}
    generator_py._BitVectorGenerator__initialize_mutation_histograms()
    generator_py._BitVectorGenerator__load_structure_from_csv()
    generator_py._BitVectorGenerator__process_all_bit_vectors()
    generator_py._BitVectorGenerator__close_writers()
    pickle_file = bv_dir / "mutation_histos.p"
    generator_py._BitVectorGenerator__save_mutation_histograms(pickle_file)
    generator_py._BitVectorGenerator__generate_plots()
    generator_py._BitVectorGenerator__get_skip_summary()
    generator_py._BitVectorGenerator__write_summary_csv()
    
    # Load mutation histograms
    pickle_file = bv_dir / "mutation_histos.p"
    if pickle_file.exists():
        with open(pickle_file, "rb") as f:
            mut_histos = pickle.load(f)
    
    summary_path = bv_dir / "summary.csv"
    return BitVectorResult(
        mutation_histos=mut_histos,
        summary_path=summary_path,
        output_dir=bv_dir,
    )

