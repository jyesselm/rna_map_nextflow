# Optimization Files Consolidation Plan

## Goal

Consolidate ALL optimization-related files into a single `optimization/` directory at the root level. This will make it easy to extract into a separate repository later.

## Current Optimization-Related Files

### Root Level Files
- `environment_optuna.yml` - Optuna optimization environment

### Scripts
- `scripts/optimize_bowtie2_params.py` - Main optimization script
- `scripts/optimize_bowtie2_params_optuna.py` - Optuna-based optimization
- `scripts/run_baseline_test.py` - Baseline testing (optimization-related)
- `scripts/optimization/` - Entire directory (17 files)

### Documentation
- `docs/optimization/` - Entire directory (all optimization docs)

### Configuration
- `conf/slurm_optimized.config` - Optimized SLURM config

### Test Directories
- `test/bowtie2_optimization_*` - Multiple test directories with optimization results

### Test Files
- Various optimization result JSON/CSV files in test directories

## Proposed Structure

```
optimization/
├── README.md                    # Main optimization README (merge existing ones)
├── environment.yml              # Rename from environment_optuna.yml
├── scripts/                     # All optimization scripts
│   ├── optimize_bowtie2_params.py
│   ├── optimize_bowtie2_params_optuna.py
│   ├── run_baseline_test.py
│   └── [all scripts/optimization/* files]
├── docs/                        # All optimization documentation
│   ├── README.md               # Main docs index
│   ├── BEST_PARAMETERS.md
│   ├── MULTIPLE_SEQUENCES_PARAMETERS.md
│   ├── TOP_100_PARAMETER_ANALYSIS.md
│   ├── archive/                # Archived optimization docs
│   ├── examples/               # Example scripts
│   └── recommended_params/     # Parameter files
├── config/                      # Optimization-specific configs
│   └── slurm_optimized.config  # Moved from conf/
├── test/                        # Optimization test directories
│   └── [all bowtie2_optimization_* directories]
└── .gitignore                  # Optimization-specific gitignore
```

## Migration Plan

### Step 1: Create Optimization Directory Structure

```bash
mkdir -p optimization/{scripts,docs,config,test}
mkdir -p optimization/docs/{archive,examples,recommended_params}
```

### Step 2: Move Scripts

**From root `scripts/`:**
- `scripts/optimize_bowtie2_params.py` → `optimization/scripts/`
- `scripts/optimize_bowtie2_params_optuna.py` → `optimization/scripts/`
- `scripts/run_baseline_test.py` → `optimization/scripts/`

**From `scripts/optimization/`:**
- Move entire contents of `scripts/optimization/` → `optimization/scripts/`
- Delete empty `scripts/optimization/` directory

### Step 3: Move Documentation

**From `docs/optimization/`:**
- Move entire `docs/optimization/` directory → `optimization/docs/`
- Delete empty `docs/optimization/` directory

### Step 4: Move Configuration

- `conf/slurm_optimized.config` → `optimization/config/slurm_optimized.config`

### Step 5: Move Environment File

- `environment_optuna.yml` → `optimization/environment.yml`

### Step 6: Move Test Directories

**From `test/`:**
- `test/bowtie2_optimization_*` → `optimization/test/`
- Only move optimization-related test directories
- Keep other test files in `test/`

### Step 7: Create Consolidated README

- Merge content from:
  - `docs/optimization/README.md`
  - `scripts/optimization/README.md`
  - Create new `optimization/README.md` with complete overview

### Step 8: Update References

- Update any imports/references in scripts
- Update documentation links
- Update main README.md to point to `optimization/` directory

## Files to Move

### Scripts (20 files)
```
scripts/optimize_bowtie2_params.py → optimization/scripts/
scripts/optimize_bowtie2_params_optuna.py → optimization/scripts/
scripts/run_baseline_test.py → optimization/scripts/
scripts/optimization/* → optimization/scripts/
```

### Documentation (11+ files)
```
docs/optimization/* → optimization/docs/
```

### Configuration (1 file)
```
conf/slurm_optimized.config → optimization/config/
```

### Environment (1 file)
```
environment_optuna.yml → optimization/environment.yml
```

### Test Directories (~15 directories)
```
test/bowtie2_optimization_* → optimization/test/
```

## After Consolidation

### Benefits
- ✅ All optimization code in one place
- ✅ Easy to extract to separate repo later
- ✅ Clean separation from main workflow
- ✅ Self-contained optimization project

### What Stays in Main Repo
- Main Nextflow workflow (`main.nf`, `modules/`, `workflows/`)
- Core Python library (`src/rna_map/`)
- Main documentation (`docs/`)
- Main configuration (`conf/` except optimized config)
- General test files (`test/` except optimization tests)

### Future Extraction
Once consolidated, extracting to separate repo is simple:
1. Copy `optimization/` directory to new repo
2. Add README, LICENSE, etc.
3. Initialize new git repo
4. Remove from main repo

## Implementation Order

1. ✅ Create directory structure
2. ✅ Move scripts first (fewer dependencies)
3. ✅ Move docs (can reference old locations initially)
4. ✅ Move config and environment
5. ✅ Move test directories
6. ✅ Create consolidated README
7. ✅ Update all references
8. ✅ Test that everything still works
9. ✅ Update main README with link to optimization/

## Notes

- This consolidation happens BEFORE the main cleanup
- Optimization directory becomes self-contained
- Can be done incrementally (test after each step)
- No breaking changes if references updated correctly

