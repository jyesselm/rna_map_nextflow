# Workflow Review and Recommendations

## Executive Summary

This document provides a comprehensive review of the RNA MAP Nextflow workflow, focusing on:
- Workflow architecture and design
- Data structures and algorithms
- Performance optimizations
- Tool recommendations
- Code quality improvements

## 1. Workflow Architecture

### Current Strengths

1. **Modular Design**: Well-structured Nextflow modules with clear separation of concerns
2. **Parallel Processing**: Good support for chunking and parallel processing
3. **C++ Integration**: Efficient C++ implementation for bit vector generation
4. **Flexible I/O**: Support for both TEXT and JSON storage formats

### Recommendations

#### 1.1 Stream Processing for Large Files

**Current Issue**: SAM files are read entirely into memory before processing.

**Recommendation**: Implement streaming SAM parsing for very large files.

```python
# Instead of loading entire SAM file
# Use streaming iterator that processes reads one at a time
class StreamingSamProcessor:
    def __init__(self, sam_path: Path, batch_size: int = 10000):
        self.sam_path = sam_path
        self.batch_size = batch_size
    
    def process_in_batches(self):
        """Process SAM file in batches to reduce memory usage."""
        batch = []
        for read in self.sam_iterator:
            batch.append(read)
            if len(batch) >= self.batch_size:
                yield self.process_batch(batch)
                batch = []
        if batch:
            yield self.process_batch(batch)
```

**Benefits**:
- Lower memory footprint
- Better for very large datasets
- Can process files larger than available RAM

#### 1.2 Incremental Bit Vector Merging

**Current Issue**: In parallel mode, all bit vectors are generated separately then merged at the end.

**Recommendation**: Use incremental merging with a merge tree or heap-based approach.

```python
# Instead of merging all at once
# Use a priority queue for incremental merging
import heapq

class IncrementalBitVectorMerger:
    def __init__(self):
        self.merge_queue = []
    
    def add_chunk(self, chunk_id: int, bit_vectors: dict):
        """Add a chunk to the merge queue."""
        heapq.heappush(self.merge_queue, (chunk_id, bit_vectors))
    
    def merge_all(self) -> dict:
        """Merge all chunks incrementally."""
        if not self.merge_queue:
            return {}
        
        # Merge pairs iteratively
        while len(self.merge_queue) > 1:
            chunk1 = heapq.heappop(self.merge_queue)
            chunk2 = heapq.heappop(self.merge_queue)
            merged = self._merge_pair(chunk1[1], chunk2[1])
            heapq.heappush(self.merge_queue, (chunk1[0], merged))
        
        return self.merge_queue[0][1]
```

**Benefits**:
- Lower peak memory usage
- Can start outputting results before all chunks complete
- More efficient for many chunks

#### 1.3 Better Error Handling and Recovery

**Current Issue**: If one chunk fails, entire workflow may fail.

**Recommendation**: Implement checkpointing and partial result recovery.

```nextflow
process RNA_MAP_BIT_VECTORS {
    // Add error handling
    errorStrategy { task.attempt <= 3 ? 'retry' : 'ignore' }
    
    // Save intermediate results
    publishDir "${params.output_dir}/${sample_id}/checkpoints",
        mode: 'copy',
        pattern: '*.checkpoint',
        saveAs: { filename -> filename }
}
```

## 2. Data Structures and Algorithms

### Current Implementation

#### Bit Vector Storage
- **TEXT format**: Stores every position (sparse in memory, dense on disk)
- **JSON format**: Sparse storage (only mutations)
- **In-memory**: `dict[int, char]` (sparse dictionary)

### Recommendations

#### 2.1 Use Compressed Sparse Data Structures

**Current**: `dict[int, char]` is good for sparse data, but could be optimized.

**Recommendation**: Consider using specialized sparse array libraries for very large sequences.

```python
# For extremely large sequences (>100kbp)
from scipy.sparse import csr_matrix
import numpy as np

class SparseBitVector:
    """Memory-efficient sparse bit vector for large sequences."""
    
    def __init__(self, length: int):
        self.length = length
        self.indices = []  # List of positions with mutations
        self.values = []  # List of mutation values
    
    def set(self, pos: int, value: str):
        """Set a position to a value."""
        if pos < 0 or pos >= self.length:
            raise IndexError(f"Position {pos} out of range")
        # Use binary search for insertion
        idx = bisect.bisect_left(self.indices, pos)
        if idx < len(self.indices) and self.indices[idx] == pos:
            self.values[idx] = value
        else:
            self.indices.insert(idx, pos)
            self.values.insert(idx, value)
    
    def get(self, pos: int) -> str:
        """Get value at position."""
        idx = bisect.bisect_left(self.indices, pos)
        if idx < len(self.indices) and self.indices[idx] == pos:
            return self.values[idx]
        return '0'  # Default: no mutation
```

**Benefits**:
- More memory efficient for very sparse data
- Faster lookups with binary search
- Better cache locality

#### 2.2 Optimize CIGAR Parsing

**Current**: Regex-based parsing is good, but could be faster for high-throughput.

**Recommendation**: Use a state machine parser for CIGAR strings.

```cpp
// Instead of regex, use a simple state machine
std::vector<CigarOp> parse_cigar_fast(const std::string& cigar) {
    std::vector<CigarOp> ops;
    int length = 0;
    
    for (char c : cigar) {
        if (std::isdigit(c)) {
            length = length * 10 + (c - '0');
        } else if (std::isalpha(c)) {
            if (length > 0) {
                ops.push_back({length, c});
                length = 0;
            }
        }
    }
    return ops;
}
```

**Benefits**:
- 2-3x faster than regex
- Lower memory allocation
- Simpler code

#### 2.3 Use Bloom Filters for Read Filtering

**Current**: Reads are filtered by iterating through all criteria.

**Recommendation**: Use probabilistic data structures for pre-filtering.

```python
from pybloom_live import BloomFilter

class ReadFilter:
    def __init__(self, expected_reads: int, error_rate: float = 0.001):
        # Bloom filter for quick rejection
        self.bloom = BloomFilter(capacity=expected_reads, error_rate=error_rate)
        self.rejected_reads = set()  # For exact tracking
    
    def should_process(self, read: AlignedRead) -> bool:
        """Quick check if read should be processed."""
        read_id = f"{read.qname}:{read.pos}"
        if read_id in self.bloom:
            return read_id not in self.rejected_reads
        return True
```

**Benefits**:
- Faster rejection of low-quality reads
- Lower memory for tracking rejected reads
- Good for very large datasets

#### 2.4 Optimize Mutation Histogram Merging

**Current**: `MutationHistogram.merge()` does element-wise addition.

**Recommendation**: Use NumPy vectorized operations more effectively.

```python
def merge(self, other: "MutationHistogram") -> None:
    """Optimized merge using vectorized operations."""
    # Validate (existing code)
    if self.name != other.name:
        raise ValueError("Names do not match")
    
    # Vectorized operations (faster than loops)
    self.num_reads += other.num_reads
    self.num_aligned += other.num_aligned
    
    # Use NumPy for array operations
    self.mut_bases = np.add(self.mut_bases, other.mut_bases)
    self.info_bases = np.add(self.info_bases, other.info_bases)
    self.del_bases = np.add(self.del_bases, other.del_bases)
    self.cov_bases = np.add(self.cov_bases, other.cov_bases)
    
    # Dictionary merge for skips
    for key in self.skips:
        self.skips[key] += other.skips[key]
    
    # Vectorized mutation count merge
    self.num_of_mutations = [
        a + b for a, b in zip(self.num_of_mutations, other.num_of_mutations)
    ]
```

**Benefits**:
- Faster merging (NumPy is optimized C code)
- Better cache utilization
- Cleaner code

## 3. Tools and Technologies

### Recommended Additions

#### 3.1 Use pysam for SAM/BAM Processing

**Current**: Custom SAM parsing.

**Recommendation**: Use `pysam` library for better performance and SAM/BAM support.

```python
import pysam

def process_sam_pysam(sam_path: Path):
    """Process SAM file using pysam (faster, supports BAM)."""
    with pysam.AlignmentFile(str(sam_path), "r") as samfile:
        for read in samfile:
            # pysam handles all parsing, indexing, etc.
            if read.is_paired:
                process_paired_read(read)
            else:
                process_single_read(read)
```

**Benefits**:
- Faster than custom parsing
- Supports BAM files (compressed)
- Better handling of SAM format edge cases
- Built-in indexing support

#### 3.2 Use HDF5 for Large Data Storage

**Current**: Pickle files for mutation histograms.

**Recommendation**: Use HDF5 for large, structured data.

```python
import h5py
import numpy as np

def save_mutation_histos_hdf5(histos: dict, output_path: Path):
    """Save mutation histograms to HDF5."""
    with h5py.File(output_path, 'w') as f:
        for name, histo in histos.items():
            group = f.create_group(name)
            group.attrs['sequence'] = histo.sequence
            group.attrs['data_type'] = histo.data_type
            group.create_dataset('mut_bases', data=histo.mut_bases)
            group.create_dataset('info_bases', data=histo.info_bases)
            # ... etc
```

**Benefits**:
- Faster I/O than pickle
- Compressed storage
- Partial reading (read only what you need)
- Cross-language compatibility

#### 3.3 Use Dask for Distributed Processing

**Current**: Nextflow handles distribution, but Python processing is single-threaded.

**Recommendation**: Use Dask for parallel Python processing within Nextflow processes.

```python
import dask.array as da
from dask import delayed

@delayed
def process_read_chunk(chunk: list[AlignedRead]) -> dict:
    """Process a chunk of reads."""
    # ... processing logic
    return result

def process_sam_dask(sam_path: Path, n_workers: int = 4):
    """Process SAM file using Dask for parallelization."""
    chunks = split_sam_into_chunks(sam_path, chunk_size=10000)
    
    # Process chunks in parallel
    results = [process_read_chunk(chunk) for chunk in chunks]
    
    # Compute all results
    from dask import compute
    all_results = compute(*results)
    
    return merge_results(all_results)
```

**Benefits**:
- Parallel processing within Python
- Better CPU utilization
- Can use multiple cores per Nextflow process
- Scales to clusters

#### 3.4 Use Apache Arrow/Parquet for Intermediate Data

**Current**: CSV and JSON for intermediate data.

**Recommendation**: Use Parquet format for columnar data.

```python
import pyarrow.parquet as pq
import pandas as pd

def save_bit_vectors_parquet(bit_vectors: dict, output_path: Path):
    """Save bit vectors in Parquet format."""
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'qname': qname,
            'position': pos,
            'value': value
        }
        for qname, bv in bit_vectors.items()
        for pos, value in bv.items()
    ])
    
    # Save as Parquet (compressed, columnar)
    df.to_parquet(output_path, compression='snappy')
```

**Benefits**:
- Much faster I/O than CSV/JSON
- Columnar storage (better for analytics)
- Built-in compression
- Schema evolution support

#### 3.5 Use Redis/Celery for Job Queue (Optional)

**Current**: Nextflow handles job scheduling.

**Recommendation**: For very large-scale processing, consider Redis + Celery.

```python
from celery import Celery

app = Celery('rna_map', broker='redis://localhost:6379')

@app.task
def process_chunk(chunk_id: str, sam_chunk_path: Path):
    """Process a chunk as a Celery task."""
    # ... processing logic
    return result
```

**Benefits**:
- Better job queue management
- Retry logic
- Progress tracking
- Distributed task execution

## 4. Performance Optimizations

### 4.1 Memory-Mapped Files for Large References

**Current**: FASTA files are loaded entirely into memory.

**Recommendation**: Use memory-mapped files for large reference sequences.

```python
import mmap

class MemoryMappedFasta:
    def __init__(self, fasta_path: Path):
        self.fasta_path = fasta_path
        self.file = open(fasta_path, 'rb')
        self.mmap = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
    
    def get_sequence(self, name: str) -> str:
        """Get sequence by name (lazy loading)."""
        # Parse FASTA on-demand
        # Only load sequence when needed
        pass
```

**Benefits**:
- Lower memory usage
- OS handles paging
- Faster for large files

### 4.2 Use NumPy Structured Arrays

**Current**: Mutation histograms use separate NumPy arrays.

**Recommendation**: Use structured arrays for better cache locality.

```python
# Instead of separate arrays
mut_bases = np.zeros(length)
info_bases = np.zeros(length)

# Use structured array
dtype = np.dtype([
    ('mut_bases', np.float64),
    ('info_bases', np.float64),
    ('del_bases', np.float64),
    ('cov_bases', np.float64),
])
histogram_data = np.zeros(length, dtype=dtype)
```

**Benefits**:
- Better cache locality
- Single memory allocation
- Faster iteration

### 4.3 Profile and Optimize Hot Paths

**Recommendation**: Use profiling tools to identify bottlenecks.

```python
# Use cProfile or line_profiler
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run your code
result = generate_bit_vectors(...)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Tools**:
- `cProfile`: Built-in Python profiler
- `line_profiler`: Line-by-line profiling
- `py-spy`: Sampling profiler (no code changes)
- `memory_profiler`: Memory usage profiling

## 5. Code Quality Improvements

### 5.1 Add Type Hints Everywhere

**Current**: Some functions lack type hints.

**Recommendation**: Add comprehensive type hints.

```python
from typing import Iterator, Optional
from pathlib import Path

def process_sam_file(
    sam_path: Path,
    fasta_path: Path,
    config: BitVectorConfig,
) -> Iterator[BitVector]:
    """Process SAM file and yield bit vectors."""
    # ...
```

### 5.2 Use Dataclasses for Configuration

**Current**: Mix of dict and dataclass configs.

**Recommendation**: Standardize on dataclasses.

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class ProcessingConfig:
    """Immutable processing configuration."""
    qscore_cutoff: int = 20
    map_score_cutoff: int = 20
    chunk_size: int = 1000000
    num_workers: int = 4
    storage_format: StorageFormat = StorageFormat.JSON
```

### 5.3 Add Comprehensive Logging

**Recommendation**: Add structured logging with context.

```python
import structlog

logger = structlog.get_logger()

def process_read(read: AlignedRead):
    logger.info(
        "processing_read",
        qname=read.qname,
        pos=read.pos,
        mapq=read.mapq,
    )
```

### 5.4 Add Metrics and Monitoring

**Recommendation**: Add metrics collection for monitoring.

```python
from prometheus_client import Counter, Histogram

reads_processed = Counter('reads_processed_total', 'Total reads processed')
processing_time = Histogram('processing_time_seconds', 'Processing time')

@processing_time.time()
def process_read(read: AlignedRead):
    reads_processed.inc()
    # ... processing
```

## 6. Nextflow-Specific Improvements

### 6.1 Use Nextflow Channels More Effectively

**Recommendation**: Use operators for better data flow.

```nextflow
// Instead of complex map operations
// Use more Nextflow operators
samples_ch
    .map { sample_id, fasta, fq1, fq2, db ->
        [sample_id, fasta, fq1, fq2, db]
    }
    .filter { sample_id, fasta, fq1, fq2, db ->
        fasta.exists()
    }
    .groupTuple(by: 0)
    .set { grouped_samples }
```

### 6.2 Add Workflow Caching

**Recommendation**: Use Nextflow's resume feature more effectively.

```nextflow
process RNA_MAP_BIT_VECTORS {
    // Add cache directive
    cache 'lenient'
    
    // Use unique output names for better caching
    output:
    path("${sample_id}_*.csv"), emit: summary
}
```

### 6.3 Use Nextflow Tower for Monitoring

**Recommendation**: Set up Nextflow Tower for workflow monitoring.

**Benefits**:
- Real-time monitoring
- Resource usage tracking
- Cost analysis
- Workflow visualization

## 7. Testing and Validation

### 7.1 Add Property-Based Testing

**Recommendation**: Use Hypothesis for property-based testing.

```python
from hypothesis import given, strategies as st

@given(
    cigar=st.text(alphabet='0123456789MIDNSHPX=', min_size=1, max_size=100),
    seq=st.text(alphabet='ACGT', min_size=1, max_size=1000),
)
def test_cigar_parsing_properties(cigar: str, seq: str):
    """Test CIGAR parsing with random inputs."""
    try:
        result = parse_cigar(cigar)
        # Properties that should always hold
        assert all(op.length > 0 for op in result)
        assert all(op.operation in 'MIDNSHPX=' for op in result)
    except ValueError:
        # Invalid CIGAR is OK
        pass
```

### 7.2 Add Performance Benchmarks

**Recommendation**: Add benchmark tests to track performance regressions.

```python
import pytest
import time

@pytest.mark.benchmark
def test_bit_vector_generation_benchmark(benchmark):
    """Benchmark bit vector generation."""
    result = benchmark(
        generate_bit_vectors,
        sam_path=test_sam,
        fasta=test_fasta,
        output_dir=tmpdir,
        config=config,
    )
    assert result is not None
```

## 8. Summary of Priority Recommendations

### High Priority (Immediate Impact)

1. **Use pysam for SAM parsing** - Faster, more robust
2. **Optimize CIGAR parsing** - State machine instead of regex
3. **Add streaming SAM processing** - Lower memory usage
4. **Use Parquet for intermediate data** - Faster I/O

### Medium Priority (Significant Improvement)

1. **Implement incremental merging** - Lower peak memory
2. **Use HDF5 for mutation histograms** - Better storage
3. **Add Dask for parallel Python processing** - Better CPU utilization
4. **Profile and optimize hot paths** - Identify bottlenecks

### Low Priority (Nice to Have)

1. **Use Bloom filters for pre-filtering** - Faster rejection
2. **Add Redis/Celery for job queue** - Better job management
3. **Use Nextflow Tower** - Better monitoring
4. **Add property-based testing** - Better test coverage

## 9. Implementation Roadmap

### Phase 1: Quick Wins (1-2 weeks)
- Switch to pysam
- Optimize CIGAR parsing
- Add Parquet support

### Phase 2: Performance (2-4 weeks)
- Implement streaming processing
- Add incremental merging
- Profile and optimize

### Phase 3: Scalability (1-2 months)
- Add Dask integration
- Implement HDF5 storage
- Add monitoring

### Phase 4: Polish (Ongoing)
- Improve testing
- Add documentation
- Refactor code quality

## 10. Conclusion

The current workflow is well-designed and functional. The recommendations above focus on:
- **Performance**: Faster processing, lower memory usage
- **Scalability**: Handle larger datasets more efficiently
- **Maintainability**: Better code quality and testing
- **Robustness**: Better error handling and recovery

Priority should be given to high-impact, low-effort improvements first (pysam, CIGAR optimization), then move to more complex optimizations as needed.

