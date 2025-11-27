# Bit Vector Storage System

## Overview

The bit vector storage system supports multiple formats for saving bit vector data. This allows flexibility in how mutation data is stored and enables conversion between formats.

## Supported Formats

### TEXT Format (Default)
- **File**: `{ref_name}_bitvectors.txt`
- **Format**: Tab-separated text file with header
- **Structure**:
  ```
  @ref    {name}    {sequence}    {data_type}
  @coordinates:    {start},{end}:{length}
  Query_name    Bit_vector    N_Mutations
  {qname}    {bit_string}    {count}
  ```
- **Storage**: Stores **every position** in the sequence (including 0s for non-mutated positions)
  - Example: `"000000A000000G000..."` (1000+ characters for a 1000bp read)
- **Pros**: Human-readable, easy to parse, one file per reference
- **Cons**: **Much larger file size** (stores all positions), slower to parse

### JSON Format
- **File**: `muts.json` (single file for all references)
- **Format**: JSON array of bit vector records
- **Structure**:
  ```json
  [
    [rname, mapq1, mapq2, read1_len, read2_len, muts, dels, ambigs],
    ...
  ]
  ```
  Where `muts`, `dels`, and `ambigs` are dictionaries mapping position → value
  - Example: `{7: "A", 15: "G"}` (only stores mutation positions)
- **Storage**: Stores **only positions with mutations/deletions/ambiguities**
  - For a 1000bp read with 2 mutations: stores ~20 bytes vs 1000+ characters
- **Pros**: **Much smaller file size** (sparse storage), fast to parse, structured data, single file
- **Cons**: Not human-readable, requires parsing

## Configuration

### Using BitVectorConfig

```python
from rna_map.core.config import BitVectorConfig
from rna_map.io.bit_vector_storage import StorageFormat

# Use TEXT format (default)
config = BitVectorConfig(storage_format=StorageFormat.TEXT)

# Use JSON format
config = BitVectorConfig(storage_format=StorageFormat.JSON)
```

### Using Parameter Files

Add to your YAML parameter file:

```yaml
bit_vector:
  storage_format: "json"  # or "text"
  # ... other options
```

## Usage Examples

### Functional API

```python
from pathlib import Path
from rna_map.core.config import BitVectorConfig
from rna_map.io.bit_vector_storage import StorageFormat
from rna_map.pipeline.functions import generate_bit_vectors

config = BitVectorConfig(
    storage_format=StorageFormat.JSON,
    map_score_cutoff=20
)

result = generate_bit_vectors(
    sam_path=Path("aligned.sam"),
    fasta=Path("ref.fa"),
    output_dir=Path("output"),
    config=config
)
```

### Class-based API

```python
from rna_map.pipeline.bit_vector_generator import BitVectorGenerator

generator = BitVectorGenerator()
params = {
    "dirs": {"output": "output"},
    "bit_vector": {
        "storage_format": "json",  # or "text"
        # ... other options
    }
}
generator.setup(params)
generator.run(sam_path, fasta, paired=True, csv_file=None)
```

## Conversion Tool

Convert between storage formats using the conversion tool:

### Command Line

```bash
# Convert TEXT to JSON
python -m rna_map.tools.convert_bitvector_storage \
    input_dir output_dir \
    --from-format text \
    --to-format json

# Convert JSON to TEXT (requires reference info)
python -m rna_map.tools.convert_bitvector_storage \
    input_dir output_dir \
    --from-format json \
    --to-format text \
    --ref-name "reference1" \
    --sequence "ATCGATCGATCG"
```

### Python API

```python
from pathlib import Path
from rna_map.io.bit_vector_storage import StorageFormat
from rna_map.tools import convert_storage_format

convert_storage_format(
    input_dir=Path("input"),
    output_dir=Path("output"),
    from_format=StorageFormat.TEXT,
    to_format=StorageFormat.JSON,
)
```

## Implementation Details

### Storage Writers

- `TextStorageWriter`: Writes per-reference text files
- `JsonStorageWriter`: Writes single JSON file for all references

### Storage Abstraction

The `BitVectorStorageWriter` abstract base class provides a consistent interface:

```python
class BitVectorStorageWriter(ABC):
    @abstractmethod
    def write_bit_vector(
        self, q_name: str, bit_vector: dict[int, str], reads: list[Any]
    ) -> None:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
```

### Factory Function

```python
from rna_map.io.bit_vector_storage import create_storage_writer, StorageFormat

writer = create_storage_writer(
    StorageFormat.JSON,
    output_dir=Path("output")
)
```

## Migration from better_mut_storage Branch

The JSON format matches the format used in the `jdy/better_mut_storage` branch:

- Single `muts.json` file
- Array of records with metadata
- Mutations, deletions, and ambiguities stored separately

To use the JSON format from that branch:

1. Set `storage_format: "json"` in your config
2. Or use `BitVectorConfig(storage_format=StorageFormat.JSON)`
3. Generated files will be compatible with tools expecting that format

## Size Comparison

The JSON format is **significantly smaller** than TEXT format because it uses sparse storage:

- **TEXT format**: Stores every position in the sequence
  - For a 1000bp read: ~1000 characters per read
  - Example: `"000000A000000G000..."` (all positions, including zeros)
  
- **JSON format**: Only stores positions with mutations/deletions/ambiguities
  - For a 1000bp read with 2 mutations: ~20-30 bytes per read
  - Example: `{7: "A", 15: "G"}` (only mutation positions)
  
**Size reduction**: Typically 10-100x smaller for typical datasets where most positions are non-mutated.

## Notes

- TEXT format creates one file per reference sequence
- JSON format creates a single file for all references
- Both formats preserve all mutation data
- JSON format is **much more compact** (sparse storage) but less human-readable
- Conversion preserves all data but may lose some metadata (e.g., query names in JSON->TEXT)

