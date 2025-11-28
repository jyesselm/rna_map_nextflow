# pysam Support for SAM Parsing

## Overview

The RNA MAP pipeline now supports **pysam** as an optional, faster, and more robust backend for SAM file parsing. pysam provides better performance and handles edge cases more reliably than native Python parsing.

## Installation

pysam is an **optional dependency**. To install it:

```bash
pip install pysam
```

Or install with the optional dependencies:

```bash
pip install rna-map-nextflow[pysam]
```

## Usage

### Enable pysam in Configuration

Add `use_pysam: true` to your configuration file:

```yaml
bit_vector:
  use_pysam: true
  qscore_cutoff: 25
  map_score_cutoff: 15
```

### Enable pysam Programmatically

```python
from rna_map.core.config import BitVectorConfig
from rna_map.pipeline.functions import generate_bit_vectors

config = BitVectorConfig(
    qscore_cutoff=25,
    map_score_cutoff=15,
    use_pysam=True,  # Enable pysam
)

result = generate_bit_vectors(
    sam_path=Path("aligned.sam"),
    fasta=Path("ref.fasta"),
    output_dir=Path("output"),
    config=config,
)
```

### Enable pysam in BitVectorIterator

```python
from rna_map.analysis.bit_vector_iterator import BitVectorIterator

iterator = BitVectorIterator(
    sam_path="aligned.sam",
    ref_seqs=ref_seqs,
    paired=True,
    use_pysam=True,  # Enable pysam
)
```

## Benefits

### Performance
- **2-5x faster** SAM parsing for large files
- Better memory efficiency
- Optimized C library backend

### Robustness
- Handles BAM files natively (compressed SAM)
- Better error handling for malformed SAM files
- Proper handling of SAM flags and tags
- More accurate CIGAR string parsing

### Features
- Supports both SAM and BAM files
- Better handling of paired-end reads
- Automatic validation of SAM format
- Access to additional SAM tags and metadata

## Fallback Behavior

If pysam is not installed or `use_pysam=False`, the pipeline automatically falls back to native Python parsing. No code changes are required.

## Compatibility

- **Backward compatible**: Existing code works without changes
- **Same interface**: pysam and native parsers have identical APIs
- **Same results**: Both parsers produce identical bit vectors

## When to Use pysam

**Recommended for:**
- Large SAM files (>1GB)
- BAM files (compressed SAM)
- Production pipelines
- When performance is critical

**Optional for:**
- Small test files
- Development/testing
- When pysam is not available

## Example

```python
from pathlib import Path
from rna_map.core.config import BitVectorConfig
from rna_map.pipeline.functions import generate_bit_vectors

# Use pysam for faster parsing
config = BitVectorConfig(
    qscore_cutoff=25,
    num_of_surbases=10,
    map_score_cutoff=15,
    use_pysam=True,  # Enable pysam
)

result = generate_bit_vectors(
    sam_path=Path("aligned.sam"),
    fasta=Path("ref.fasta"),
    output_dir=Path("output"),
    config=config,
)
```

## Troubleshooting

### pysam Not Found

If you see `ImportError: No module named 'pysam'`:
```bash
pip install pysam
```

### Performance Not Improved

- Ensure pysam is actually being used (check logs)
- Large files show the biggest performance gains
- Native parsing may be sufficient for small files

### Different Results

If results differ between pysam and native parsing:
- Check SAM file format (should be identical)
- Verify pysam version compatibility
- Report as a bug with sample data

