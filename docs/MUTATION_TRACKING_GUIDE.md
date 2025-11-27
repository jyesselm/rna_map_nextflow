# Mutation Tracking Optimization Guide

## Your Use Case

- **Mutation tracking**: 3-4 mutations maximum per read
- **Sequence length**: ~150 bp
- **Read length**: 300 cycle kits (150 bp each direction, paired-end)
- **Common adapters**: 5' and 3' sequences (handled by Trim Galore)
- **Use cases**:
  1. Single sequence matching
  2. Few similar sequences
  3. Huge libraries

## Recommended Presets

### 1. Single Sequence (`mutation_single`)

**Best for**: One reference sequence, maximum mutation sensitivity

```bash
rna-map --bt2-preset mutation_single -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Key parameters**:
- `-L 10` (seed length): Short seed allows mutations anywhere
- `-N 1` (seed mismatches): Allows mutations in seed region
- `-X 300` (max insert): Optimized for 150bp sequences
- `--mp 6,2` (mismatch penalty): Lower penalty helps detect mutations
- `--score-min L,0,-0.6` (score minimum): Lower threshold for mutation detection

### 2. Few Similar Sequences (`mutation_similar`)

**Best for**: Multiple similar sequences, need to report all alignments

```bash
rna-map --bt2-preset mutation_similar -fa refs.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Key parameters**:
- Same as `mutation_single` but:
- `-k 10` (max alignments): Reports up to 10 alignments per read
- `--no-unal` disabled: Keeps unaligned reads for analysis

### 3. Huge Libraries (`mutation_large`)

**Best for**: Large libraries, need speed but still detect mutations

```bash
rna-map --bt2-preset mutation_large -fa huge_lib.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Key parameters**:
- `-L 12` (seed length): Slightly longer for speed
- `--fast-local`: Faster alignment mode
- `--score-min L,0,-0.4`: Slightly higher threshold for speed
- Otherwise similar to `mutation_single`

## Key Parameters for Mutation Tracking

### Most Important Parameters (Priority Order)

#### 1. **Seed Mismatches (`-N` / `--bt2-seed-mismatches`)** ⭐ CRITICAL
   - **Recommendation**: **1** (not 0!)
   - **Why**: This is THE most important parameter for mutation tracking
     - Default (0) requires perfect seed match - mutations in seed = no alignment
     - With N=1, mutations can occur in seed region and still align
     - Your mutations (3-4 max) can occur anywhere, including seed
   - **Impact**: Without this, you'll miss many mutations
   - **Trade-off**: Slightly slower, but essential for mutation detection

#### 2. **Seed Length (`-L` / `--bt2-seed-length`)** ⭐ VERY IMPORTANT
   - **Recommendation**: **10** for maximum sensitivity, **12** for speed
   - **Why**: 
     - Shorter seeds = more positions where mutations can occur
     - For 150bp sequences, seed of 10-12 covers ~7-8% of sequence
     - Longer seeds (20+) are too restrictive for mutation detection
   - **Trade-off**: 
     - L=10: More sensitive, slightly slower
     - L=12: Balanced (used in mutation_large preset)
     - L=20: Too long, will miss mutations

#### 3. **Max Insert Size (`-X` / `--bt2-maxins`)** ⭐ IMPORTANT
   - **Recommendation**: **200-300** for your 150bp sequences
   - **Why**: 
     - Your sequences: ~150bp
     - Your reads: 150bp each direction
     - Insert size = distance between read pairs
     - For 150bp sequence: insert should be ~200-300bp (allows overlap)
   - **Current default**: 1000 (way too large, wastes computation)
   - **Calculation**: Sequence length + buffer = 150 + 50-150 = 200-300bp

#### 4. **Mismatch Penalty (`--mp` / `--bt2-mismatch-penalty`)** ⭐ IMPORTANT
   - **Recommendation**: **"6,2"** (lower than default ~6,4)
   - **Why**: 
     - Mutations are EXPECTED in your data (that's what you're tracking!)
     - Lower penalty = mutations don't penalize alignment as much
     - Format: "open,extend" (e.g., "6,2" = 6 to open, 2 per base)
   - **Default**: Higher penalties (e.g., "6,4") penalize mutations too much
   - **Impact**: Affects whether reads with mutations align or get rejected

#### 5. **Score Minimum (`--score-min` / `--bt2-score-min`)** ⭐ IMPORTANT
   - **Recommendation**: **"L,0,-0.6"** for single sequence, **"L,0,-0.4"** for large libs
   - **Why**: 
     - Lower threshold = allows reads with mutations to align
     - Format: "L,min,max" where L=linear function
     - -0.6 is quite permissive (good for mutations)
     - -0.4 is slightly stricter (faster for large libs)
   - **Default**: Higher thresholds reject mutated reads
   - **Impact**: Directly affects how many mutated reads align

### Secondary Parameters

6. **Gap Penalties (`--rdg` / `--rfg`)** 
   - **Recommendation**: "5,3" (moderate)
   - **Why**: 
     - Mutations are usually substitutions, not indels
     - DMS modifications cause substitutions (A→G, C→U)
     - Moderate penalties allow some indels but not too many
   - **Default**: Higher penalties (usually fine, but moderate is safer)

7. **Max Alignments (`-k` / `--bt2-max-alignments`)**
   - **Recommendation**: 10 for similar sequences, not needed for single sequence
   - **Why**: 
     - When sequences are similar, a read might align to multiple references
     - Reports up to N best alignments
     - Useful for distinguishing between similar sequences
   - **Only needed**: When you have similar sequences (use `mutation_similar` preset)

8. **Local Alignment (`--local`)**
   - **Recommendation**: **Always use** for mutation tracking
   - **Why**: 
     - Allows soft clipping of adapters (your common 5'/3' sequences)
     - Handles mutations at read ends better
     - More flexible for mutation detection
   - **Essential**: For reads with common adapter sequences
   - **Alternative**: `--end-to-end` is too strict for mutation tracking

### Parameters You Can Usually Ignore

- **Threads (`-p`)**: Set based on your CPU (16-32 typical)
- **No unaligned/discordant/mixed**: Keep defaults (filters low-quality)
- **Gap penalties**: Defaults usually fine, moderate (5,3) is safer

## Parameter Priority

### High Priority (Must Optimize)
1. ✅ **Seed length** (`-L`): 10-12
2. ✅ **Seed mismatches** (`-N`): 1
3. ✅ **Max insert size** (`-X`): 200-300
4. ✅ **Mismatch penalty** (`--mp`): Lower (6,2)

### Medium Priority (Should Optimize)
5. ✅ **Score minimum** (`--score-min`): Lower threshold
6. ✅ **Local alignment** (`--local`): Always use

### Low Priority (Nice to Have)
7. Gap penalties (defaults usually fine)
8. Max alignments (only if similar sequences)

## Common 5' and 3' Sequences (Adapters)

Your reads have common adapter sequences at 5' and 3' ends. This is **already handled**:

1. **Trim Galore** (in pipeline): Automatically detects and trims adapters
   - **Recommendation**: Keep enabled (don't use `--skip-trim-galore`)
   - Handles Illumina adapters, poly-A tails, etc.
   
2. **Local alignment** (`--local`): Soft-clips any remaining adapter sequences
   - Allows reads to align even if adapters weren't fully trimmed
   - Essential for mutation tracking

3. **No special Bowtie2 settings needed**: 
   - Trim Galore handles adapter removal
   - Local alignment handles any remaining adapter sequences
   - Your mutation presets already use `--local`

**What this means**: You don't need to worry about adapters - the pipeline handles it!

## Usage Examples

### Example 1: Single Sequence
```bash
rna-map \
  --bt2-preset mutation_single \
  -fa single_ref.fasta \
  -fq1 reads_1.fastq \
  -fq2 reads_2.fastq
```

### Example 2: Few Similar Sequences
```bash
rna-map \
  --bt2-preset mutation_similar \
  -fa similar_refs.fasta \
  -fq1 reads_1.fastq \
  -fq2 reads_2.fastq
```

### Example 3: Huge Library
```bash
rna-map \
  --bt2-preset mutation_large \
  -fa huge_library.fasta \
  -fq1 reads_1.fastq \
  -fq2 reads_2.fastq \
  --bt2-threads 32  # Use more threads for large libraries
```

### Example 4: Custom Override
```bash
# Use mutation_single but with custom insert size
rna-map \
  --bt2-preset mutation_single \
  --bt2-maxins 250 \
  -fa ref.fasta \
  -fq1 r1.fastq \
  -fq2 r2.fastq
```

## Comparison with Default Preset

| Parameter | Default | Mutation Tracking | Why |
|-----------|---------|-------------------|-----|
| Seed length | 12 | 10 | Shorter = more mutation sensitivity |
| Seed mismatches | 0 | 1 | Allow mutations in seed |
| Max insert | 1000 | 200-300 | Optimized for 150bp sequences |
| Mismatch penalty | Higher | 6,2 | Lower penalty for mutations |
| Score minimum | Higher | L,0,-0.6 | Lower threshold |

## Testing Recommendations

1. **Start with `mutation_single`** for single sequence cases
2. **Check alignment rate**: Should be >90% for good data
3. **Check mutation detection**: Verify mutations are being detected
4. **Adjust if needed**: 
   - Lower `--bt2-score-min` if too many reads rejected
   - Increase `--bt2-maxins` if paired-end not aligning
   - Use `mutation_similar` if sequences are too similar

## Troubleshooting

### Problem: Low alignment rate
- **Solution**: Lower `--bt2-score-min` or increase `--bt2-seed-mismatches`
- **Check**: Are adapters being trimmed? (use Trim Galore)

### Problem: Mutations not detected
- **Solution**: Ensure `-N 1` (seed mismatches = 1)
- **Check**: Is seed length too long? Try `-L 10`

### Problem: Too slow for large libraries
- **Solution**: Use `mutation_large` preset
- **Or**: Increase threads `--bt2-threads 32`

### Problem: Similar sequences not aligning correctly
- **Solution**: Use `mutation_similar` with `-k 10`
- **Check**: Are sequences too similar? May need different approach

## Quick Reference Card

### For Your Use Case (150bp sequences, 300 cycle paired-end)

**Single Sequence:**
```bash
rna-map --bt2-preset mutation_single -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Few Similar Sequences:**
```bash
rna-map --bt2-preset mutation_similar -fa refs.fasta -fq1 r1.fastq -fq2 r2.fastq
```

**Huge Library:**
```bash
rna-map --bt2-preset mutation_large -fa huge_lib.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### Critical Parameters Summary

| Parameter | Your Value | Why |
|-----------|------------|-----|
| `-N` (seed mismatches) | **1** | ⭐ CRITICAL - allows mutations in seed |
| `-L` (seed length) | **10-12** | Shorter = more mutation sensitivity |
| `-X` (max insert) | **200-300** | Optimized for 150bp sequences |
| `--mp` (mismatch penalty) | **6,2** | Lower penalty for mutations |
| `--score-min` | **L,0,-0.6** | Lower threshold for mutations |
| `--local` | **Always** | Handles adapters and mutations |

### Parameter Priority

1. ⭐⭐⭐ **Seed Mismatches (`-N 1`)**: Most critical - without this, you'll miss mutations
2. ⭐⭐⭐ **Seed Length (`-L 10-12`)**: Very important for mutation sensitivity  
3. ⭐⭐ **Max Insert (`-X 200-300`)**: Important for your sequence length
4. ⭐⭐ **Mismatch Penalty (`--mp 6,2`)**: Important for mutation detection
5. ⭐⭐ **Score Minimum (`--score-min`)**: Important for allowing mutated reads
6. ⭐ **Local Alignment (`--local`)**: Essential for adapters
7. ⭐ **Gap Penalties**: Usually fine with defaults

### What to Monitor

1. **Alignment rate**: Should be >90% for good data
2. **Mutation detection**: Check if mutations are being found
3. **Read coverage**: Should cover most of your 150bp sequences
4. **Paired-end alignment**: Both R1 and R2 should align (check insert size if not)

