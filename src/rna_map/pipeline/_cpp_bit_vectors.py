"""C++ implementation wrapper for bit vector generation."""

import sys
from pathlib import Path
from typing import Optional

# Try to import C++ module
# The .so file is in the same directory, so we import it directly
try:
    import importlib.util
    
    # Find the .so file in the same directory as this Python file
    pipeline_dir = Path(__file__).parent
    
    # Try multiple possible names
    possible_names = [
        "bit_vector_cpp.cpython-311-darwin.so",
        "_bit_vector_cpp_impl.so",
        "bit_vector_cpp*.so",  # Will use glob for this
    ]
    
    so_file = None
    for name in possible_names:
        if "*" in name:
            # Use glob
            so_files = list(pipeline_dir.glob(name))
            if so_files:
                so_file = so_files[0]
                break
        else:
            candidate = pipeline_dir / name
            if candidate.exists():
                so_file = candidate
                break
    
    # Also check cpp directory
    if not so_file or not so_file.exists():
        cpp_dir = pipeline_dir.parent.parent.parent / "cpp"
        for name in possible_names:
            if "*" in name:
                so_files = list(cpp_dir.glob(name))
                if so_files:
                    so_file = so_files[0]
                    break
            else:
                candidate = cpp_dir / name
                if candidate.exists():
                    so_file = candidate
                    break
    
    if so_file.exists():
        spec = importlib.util.spec_from_file_location("bit_vector_cpp", so_file)
        bit_vector_cpp = importlib.util.module_from_spec(spec)
        if spec.loader:
            spec.loader.exec_module(bit_vector_cpp)
            CPP_AVAILABLE = True
        else:
            CPP_AVAILABLE = False
    else:
        # Try normal import (might work if in path)
        import bit_vector_cpp
        CPP_AVAILABLE = True
except Exception as e:
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
    
    # Initialize rejected output file if needed
    if not hasattr(generator_py, '_BitVectorGenerator__rejected_out'):
        rejected_file = bv_dir / "rejected_bvs.csv"
        generator_py._BitVectorGenerator__rejected_out = open(rejected_file, "w")
        generator_py._BitVectorGenerator__rejected_out.write("qname,rname,reason,read1,read2,bitvector\n")
    
    # Process bit vectors to generate histograms
    # Note: Single underscore methods don't get name-mangled, double underscore attributes do
    generator_py._BitVectorGenerator__mut_histos = {}
    generator_py._initialize_mutation_histograms()  # Single underscore, no mangling
    generator_py._load_structure_from_csv()  # Single underscore, no mangling
    generator_py._process_all_bit_vectors()  # Single underscore, no mangling
    generator_py._close_writers()  # Single underscore, no mangling
    pickle_file = bv_dir / "mutation_histos.p"
    generator_py._save_mutation_histograms(pickle_file)  # Single underscore, no mangling
    generator_py._BitVectorGenerator__generate_plots()  # Double underscore, needs mangling
    generator_py._BitVectorGenerator__get_skip_summary()  # Double underscore, needs mangling
    generator_py._BitVectorGenerator__write_summary_csv()  # Double underscore, needs mangling
    
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

