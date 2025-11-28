# Bowtie2 Argument Options - Proposal

## Current Problem
Having Bowtie2 arguments as a single string is confusing and error-prone:
- Hard to remember exact format
- No validation until runtime
- Difficult to override individual settings
- String parsing is fragile

## Proposed Solutions

### Option 1: YAML Presets + Individual Flags (Recommended)
**Best for**: Most users, clear and flexible

```yaml
# rna_map/resources/bowtie2_presets.yml
presets:
  default:
    local: true
    no_unal: true
    no_discordant: true
    no_mixed: true
    maxins: 1000
    seed_length: 12
    threads: 16
  
  sensitive:
    local: true
    no_unal: true
    no_discordant: true
    no_mixed: true
    maxins: 1000
    seed_length: 20
    threads: 16
    score_min: "G,20,15"
  
  barcoded:
    local: true
    no_unal: true
    no_discordant: true
    no_mixed: true
    maxins: 1000
    seed_length: 12
    threads: 16
    mismatch_penalty: "50,30"
    gap_penalty_read: "50,30"
    gap_penalty_ref: "50,30"
```

**CLI Usage**:
```bash
# Use preset
rna-map --bt2-preset default ...

# Override individual args
rna-map --bt2-preset default --bt2-threads 8 --bt2-maxins 2000 ...

# Or use individual flags without preset
rna-map --bt2-local --bt2-threads 8 --bt2-maxins 1000 ...
```

### Option 2: Structured YAML in Config File
**Best for**: Users who prefer config files

```yaml
# In param file or default.yml
map:
  bt2_args:
    preset: default  # or "sensitive", "barcoded", etc.
    overrides:
      threads: 8
      maxins: 2000
```

### Option 3: Individual CLI Flags Only
**Best for**: Simple, explicit control

```bash
rna-map \
  --bt2-local \
  --bt2-no-unal \
  --bt2-threads 16 \
  --bt2-maxins 1000 \
  --bt2-seed-length 12 \
  ...
```

### Option 4: Hybrid (Presets + Flags + Raw String Fallback)
**Best for**: Maximum flexibility

```bash
# Option A: Use preset
rna-map --bt2-preset default ...

# Option B: Override preset with flags
rna-map --bt2-preset default --bt2-threads 8 ...

# Option C: Use individual flags
rna-map --bt2-local --bt2-threads 8 ...

# Option D: Advanced users can still use raw string
rna-map --bt2-args "--local;--no-unal;-p 8" ...
```

## Recommendation: Option 4 (Hybrid)

This gives:
- ✅ Easy defaults for most users (presets)
- ✅ Flexibility to override (individual flags)
- ✅ Power users can still use raw strings
- ✅ Backward compatible
- ✅ Type-safe (structured data)

## Implementation Plan

1. Create `bowtie2_presets.yml` with common presets
2. Add CLI flags for common arguments:
   - `--bt2-preset` (select preset)
   - `--bt2-local` / `--bt2-end-to-end`
   - `--bt2-threads` / `--bt2-p`
   - `--bt2-maxins` / `--bt2-X`
   - `--bt2-seed-length` / `--bt2-L`
   - `--bt2-no-unal`
   - `--bt2-no-discordant`
   - `--bt2-no-mixed`
3. Keep `--bt2-alignment-args` as fallback for advanced users
4. Build final argument string from preset + overrides

