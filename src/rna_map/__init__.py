"""RNA MAP: Rapid analysis of RNA mutational profiling (MaP) experiments.

RNA MAP is a Python package for analyzing DMS-MaPseq sequencing data to identify
RNA structural information through mutation analysis. The tool performs quality
control, read alignment, bit vector generation, and visualization of mutation patterns.

Package Structure:
    - io: Input/output operations (FASTA, FASTQ, SAM, CSV parsing)
    - core: Core data structures (Inputs, AlignedRead, BitVector)
    - external: External command wrappers (Bowtie2, FastQC, Trim Galore)
    - pipeline: Pipeline orchestration (Mapper, BitVectorGenerator)
    - analysis: Mutation analysis (MutationHistogram, statistics)
    - visualization: Plotting and visualization (Plotly-based plots)

For detailed documentation, see CODE_DOCUMENTATION.md
"""

__version__ = "1.0.0"

from rna_map import settings

__all__ = ["settings"]
