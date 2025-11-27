# Bowtie2 Arguments - Usage Guide

## Overview

Bowtie2 arguments can now be specified in **three flexible ways**:
1. **Presets** (easiest) - Use predefined configurations
2. **Individual flags** (flexible) - Override specific settings
3. **Raw string** (advanced) - Full control for power users

## Option 1: Using Presets (Recommended)

### Available Presets

- `default` - Standard RNA-MAP settings
- `sensitive` - More sensitive alignment
- `fast` - Faster alignment with less sensitivity
- `barcoded` - Optimized for barcoded libraries
- `barcoded_large` - For large barcoded libraries

### Basic Usage

```bash
# Use default preset
rna-map --bt2-preset default -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq

# Use sensitive preset
rna-map --bt2-preset sensitive -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq

# Use barcoded preset
rna-map --bt2-preset barcoded -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Override Preset Settings

```bash
# Use default preset but change threads
rna-map --bt2-preset default --bt2-threads 8 -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq

# Use sensitive preset but change max insert size
rna-map --bt2-preset sensitive --bt2-maxins 2000 -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

## Option 2: Individual Flags (No Preset)

Build your own configuration using individual flags:

```bash
rna-map \
  --bt2-local \
  --bt2-no-unal \
  --bt2-no-discordant \
  --bt2-no-mixed \
  --bt2-threads 16 \
  --bt2-maxins 1000 \
  --bt2-seed-length 12 \
  -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Available Individual Flags

**Alignment Mode:**
- `--bt2-local` - Use local alignment (default)
- `--bt2-end-to-end` - Use end-to-end alignment

**Common Options:**
- `--bt2-threads` / `--bt2-p` - Number of threads (e.g., 8, 16)
- `--bt2-maxins` / `--bt2-X` - Maximum insert size (e.g., 1000)
- `--bt2-seed-length` / `--bt2-L` - Seed length (e.g., 12, 20)

**Read Filtering:**
- `--bt2-no-unal` - Suppress unaligned reads
- `--bt2-no-discordant` - Suppress discordant alignments
- `--bt2-no-mixed` - Suppress unpaired alignments

**Advanced Options:**
- `--bt2-mismatch-penalty` - Mismatch penalty (e.g., "50,30")
- `--bt2-gap-penalty-read` - Read gap penalty (e.g., "50,30")
- `--bt2-gap-penalty-ref` - Reference gap penalty (e.g., "50,30")
- `--bt2-score-min` - Minimum score function (e.g., "G,20,15")

## Option 3: Raw String (Advanced)

For maximum control, use raw arguments (backward compatible):

```bash
# Comma-separated
rna-map --bt2-alignment-args "--local,--no-unal,-p 8" -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq

# Semicolon-separated
rna-map --bt2-alignment-args "--local;--no-unal;-p 8" -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq

# Space-separated
rna-map --bt2-alignment-args "--local --no-unal -p 8" -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Note**: Raw string arguments override presets and individual flags.

## Priority Order

Arguments are processed in this order (highest to lowest priority):

1. `--bt2-alignment-args` (raw string) - **Highest priority**
2. Individual flags (`--bt2-threads`, `--bt2-local`, etc.)
3. Preset (`--bt2-preset`) - **Lowest priority**

## Examples

### Example 1: Quick Start
```bash
# Simplest - just use default preset
rna-map --bt2-preset default -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Example 2: Custom Threads
```bash
# Use default preset but with 8 threads instead of 16
rna-map --bt2-preset default --bt2-threads 8 -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Example 3: Barcoded Library
```bash
# Use barcoded preset (optimized for barcoded libraries)
rna-map --bt2-preset barcoded -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Example 4: Fully Custom
```bash
# Build your own configuration
rna-map \
  --bt2-local \
  --bt2-no-unal \
  --bt2-threads 8 \
  --bt2-maxins 2000 \
  --bt2-seed-length 20 \
  -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Example 5: Advanced Override
```bash
# Use sensitive preset but override with advanced options
rna-map \
  --bt2-preset sensitive \
  --bt2-mismatch-penalty "60,40" \
  --bt2-gap-penalty-read "60,40" \
  -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

## Preset Definitions

### `default`
Standard settings for most RNA-MAP analyses:
- Local alignment
- No unaligned/discordant/mixed reads
- Max insert size: 1000
- Seed length: 12
- Threads: 16

### `sensitive`
More sensitive alignment:
- Same as default but:
- Seed length: 20 (longer = more sensitive)
- Score minimum: G,20,15

### `fast`
Faster alignment:
- Same as default but:
- Seed length: 10 (shorter = faster)
- Very fast local mode

### `barcoded`
Optimized for barcoded libraries:
- Same as default but:
- Mismatch penalty: 50,30
- Gap penalties: 50,30
- Score minimum: G,20,15

### `barcoded_large`
For large barcoded libraries:
- Similar to barcoded but optimized for scale

## Configuration File

You can also define Bowtie2 arguments in your parameter YAML file:

```yaml
map:
  bt2_alignment_args: "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16"
```

Or use presets in the future (when implemented in config files).

## Migration from Old Format

### Old Way
```bash
rna-map --bt2-alignment-args "--local;--no-unal;--no-discordant;--no-mixed;-X 1000;-L 12;-p 16" ...
```

### New Way (Easiest)
```bash
rna-map --bt2-preset default ...
```

### New Way (With Override)
```bash
rna-map --bt2-preset default --bt2-threads 8 ...
```

## Benefits

✅ **Easier**: Just use `--bt2-preset default` instead of remembering long strings
✅ **Flexible**: Override individual settings as needed
✅ **Type-safe**: Individual flags are validated
✅ **Discoverable**: `--help` shows all available options
✅ **Backward compatible**: Raw string format still works
✅ **Maintainable**: Presets defined in YAML, easy to add new ones

