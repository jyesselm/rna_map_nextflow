# Mutation Tracking Presets - Quick Summary

## Your Use Case
- **Sequences**: ~150 bp
- **Reads**: 300 cycle paired-end (150 bp each direction)
- **Mutations**: 3-4 maximum per read
- **Adapters**: Common 5' and 3' sequences (handled automatically)

## Recommended Presets

### 🎯 Single Sequence → `mutation_single`
```bash
rna-map --bt2-preset mutation_single -fa ref.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### 🎯 Few Similar Sequences → `mutation_similar`
```bash
rna-map --bt2-preset mutation_similar -fa refs.fasta -fq1 r1.fastq -fq2 r2.fastq
```

### 🎯 Huge Libraries → `mutation_large`
```bash
rna-map --bt2-preset mutation_large -fa huge_lib.fasta -fq1 r1.fastq -fq2 r2.fastq
```

## Critical Parameters (Must Have)

### 1. Seed Mismatches (`-N 1`) ⭐⭐⭐
**MOST IMPORTANT** - Without this, mutations in seed region won't align!

### 2. Seed Length (`-L 10-12`) ⭐⭐⭐
Shorter = more mutation sensitivity

### 3. Max Insert Size (`-X 200-300`) ⭐⭐
Optimized for your 150bp sequences (default 1000 is too large)

### 4. Mismatch Penalty (`--mp 6,2`) ⭐⭐
Lower penalty = mutations don't penalize alignment as much

### 5. Score Minimum (`--score-min L,0,-0.6`) ⭐⭐
Lower threshold = allows reads with mutations to align

## What Each Preset Does

| Preset | Seed Length | Seed Mismatches | Max Insert | Max Alignments | Speed |
|--------|-------------|-----------------|------------|----------------|-------|
| `mutation_single` | 10 | 1 | 300 | 1 | Balanced |
| `mutation_similar` | 10 | 1 | 300 | 10 | Balanced |
| `mutation_large` | 12 | 1 | 300 | 1 | Faster |

## Common 5'/3' Sequences

✅ **Already handled!** 
- Trim Galore removes adapters automatically
- Local alignment soft-clips any remaining adapters
- No special settings needed

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Low alignment rate | Lower `--bt2-score-min` or check adapter trimming |
| Mutations not detected | Ensure `-N 1` (seed mismatches) |
| Too slow | Use `mutation_large` preset or increase threads |
| Similar sequences issue | Use `mutation_similar` preset |

## All Available Presets

- `default` - Standard RNA-MAP settings
- `sensitive` - More sensitive alignment
- `fast` - Faster alignment
- `barcoded` - For barcoded libraries
- `barcoded_large` - For large barcoded libraries
- **`mutation_single`** - ⭐ For single sequence mutation tracking
- **`mutation_similar`** - ⭐ For few similar sequences
- **`mutation_large`** - ⭐ For huge libraries

