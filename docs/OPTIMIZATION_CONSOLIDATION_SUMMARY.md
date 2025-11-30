# Optimization Consolidation - Quick Summary

## Goal
Move ALL optimization-related files into a single `optimization/` directory so it can be easily extracted to a separate repository later.

## What Will Be Moved

### Files & Directories to Consolidate

**Scripts (~20 files):**
- `scripts/optimize_bowtie2_params.py`
- `scripts/optimize_bowtie2_params_optuna.py`
- `scripts/run_baseline_test.py`
- `scripts/optimization/*` (entire directory)

**Documentation (~11 files):**
- `docs/optimization/*` (entire directory)

**Configuration:**
- `conf/slurm_optimized.config`

**Environment:**
- `environment_optuna.yml`

**Test Directories (~17 directories):**
- All `test/bowtie2_optimization_*` directories
- All `test/nextflow_case*_baseline*` directories (if optimization-related)

## Target Structure

```
optimization/
├── README.md                    # Consolidated optimization README
├── environment.yml              # Renamed from environment_optuna.yml
├── scripts/                     # All optimization scripts
├── docs/                        # All optimization documentation
├── config/                      # Optimization configs
└── test/                        # Optimization test directories
```

## Benefits

✅ **Self-contained** - All optimization code in one place
✅ **Ready for extraction** - Easy to move to separate repo
✅ **Clean separation** - Main workflow repo stays focused
✅ **No breaking changes** - Just reorganization

## Implementation

See `OPTIMIZATION_CONSOLIDATION_PLAN.md` for detailed steps.

This should be done **BEFORE** the main cleanup, as it will reduce the scope of other cleanup tasks.

