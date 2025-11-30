# Massive Repository Cleanup Plan

## Overview

This plan consolidates documentation, removes duplicates, organizes the repository, and prepares optimization code for separate repository extraction.

## Phase 0: Consolidate Optimization (NEW - Do First!)

**Goal:** Move ALL optimization-related files into a single `optimization/` directory for easy extraction to separate repo later.

See `OPTIMIZATION_CONSOLIDATION_PLAN.md` for detailed steps.

**Summary:**
- Create `optimization/` directory structure
- Move all optimization scripts, docs, configs, tests into it
- Make it self-contained and ready for extraction

## Current Problems

### 1. Root Directory Clutter (12 markdown files)
- Multiple cleanup/update summaries (CLEANUP_PLAN.md, CLEANUP_SUMMARY.md, RESTRUCTURE_SUMMARY.md, NEXTFLOW_UPDATE_SUMMARY.md)
- Warning documentation spread across 3 files (WARNINGS_*.md)
- Multiple validation/setup docs at root level

### 2. Duplicate Modules
- `nextflow/modules/` contains duplicates of `modules/` files
- Should remove `nextflow/` directory entirely (already migrated to root)

### 3. Too Many README Files (7 total)
- `README.md` (root) - Main repo readme
- `docs/README.md` - Docs index
- `nextflow/README.md` - Old/obsolete (nextflow dir should be removed)
- `docs/optimization/README.md` - Optimization docs index
- `scripts/optimization/README.md` - Scripts docs
- `src/cpp/README.md` - C++ docs (keep)
- `test/nextflow/README.md` - Test docs (keep or consolidate)

### 4. Documentation Scattered
- 70+ markdown files total
- Archive directories with 20+ files
- Multiple guides for same topics

## Cleanup Strategy

### Phase 1: Remove Obsolete/Duplicate Directories

**DELETE `nextflow/` directory entirely:**
- Already migrated to root structure
- Contains duplicate modules
- Contains old test outputs
- README is obsolete

**Files to delete:**
- `nextflow/modules/join_mutation_histos.nf` (duplicate)
- `nextflow/modules/rna_map_bit_vectors.nf` (duplicate)
- `nextflow/README.md` (obsolete)
- `nextflow/environment.yml` (obsolete - use root environment.yml)
- `nextflow/setup_conda.sh` (obsolete)
- `nextflow/reports/` (old test outputs)
- `nextflow/test_*.html` (old test outputs)
- `nextflow/test_results_parallel/` (old test outputs)
- `nextflow/test_trace_parallel.txt` (old test output)

### Phase 2: Consolidate Root-Level Documentation

**Move to `docs/`:**
- `QUICKSTART.md` → `docs/QUICKSTART.md` (or merge into main README)
- `CLEAR_IDE_CACHE.md` → `docs/SETUP_IDE.md` (rename + consolidate)
- `SETUP_NEXTFLOW_LINTING.md` → Merge into `docs/SETUP_IDE.md`
- `NEXTFLOW_UPDATE_SUMMARY.md` → Archive or delete (already done)
- `NEXTFLOW_VALIDATION_RESULTS.md` → Delete (one-time validation)
- `validate_nextflow.sh` → Move to `scripts/` or delete if obsolete

**Delete obsolete cleanup docs:**
- `CLEANUP_PLAN.md` → Delete (old plan)
- `CLEANUP_SUMMARY.md` → Delete (completed cleanup)
- `RESTRUCTURE_SUMMARY.md` → Delete (completed restructure)

**Consolidate warning docs:**
- `WARNINGS_EXPLANATION.md` → Delete (one-time)
- `WARNINGS_FIXED_SUMMARY.md` → Delete (one-time)
- `WARNINGS_QUICK_SUMMARY.md` → Delete (one-time)
- Create `docs/CHANGELOG.md` for major changes like Nextflow update

### Phase 3: Consolidate README Files

**Keep:**
1. `README.md` (root) - Main repository documentation
2. `docs/README.md` - Documentation index
3. `docs/optimization/README.md` - Optimization docs index
4. `src/cpp/README.md` - C++ implementation docs

**Merge/Delete:**
- `scripts/optimization/README.md` → Merge into `docs/optimization/README.md`
- `test/nextflow/README.md` → Merge into `docs/CLUSTER_TESTING_GUIDE.md` or delete
- `nextflow/README.md` → Delete (entire directory being removed)

**Strategy:**
- Create comprehensive `README.md` that links to all relevant docs
- Use `docs/README.md` as navigation hub
- Keep specialized READMEs only where they add value

### Phase 4: Organize Documentation Structure

**Target structure:**
```
docs/
├── README.md                    # Main docs index
├── QUICKSTART.md               # Quick start guide
├── SETUP.md                    # Consolidated setup guide (IDE, environment, etc.)
├── WORKFLOW_GUIDE.md           # Main workflow usage (rename from PIPELINE_GUIDE.md)
├── CLUSTER_TESTING_GUIDE.md    # Keep as-is
├── CLUSTER_TESTING_QUICKREF.md # Keep as-is
├── CONTAINER_USAGE.md          # Keep as-is
├── optimization/               # Keep structure
│   ├── README.md
│   └── ...
├── archive/                    # Keep for historical reference
│   └── ...
└── [other specialized guides]  # Keep as needed
```

**Consolidate:**
- Merge `NEXTFLOW_LINTING.md` into `SETUP.md`
- Merge `CLUSTER_TESTING_GUIDE.md` and `CLUSTER_TESTING_QUICKREF.md` if possible
- Review and merge duplicate guides

### Phase 5: Clean Up Test Outputs & Temporary Files

**Delete:**
- `test_nextflow_output/` - Old test output directory
- `reports/` - Old execution reports (should be in .gitignore)
- `*.html` files in root (reports)
- `*.txt` trace files in root
- `test/nextflow_case2_*` directories (test outputs)

**Add to .gitignore:**
- `reports/`
- `test_*_output/`
- `*.trace.txt`
- `test_case*_*/`

### Phase 6: Update Main README

**Consolidate `README.md`:**
- Include quick start directly (or link to docs/QUICKSTART.md)
- Remove redundant sections
- Add clear navigation to docs/
- Update to reflect current structure

### Phase 7: Review and Consolidate Archive

**Review `docs/archive/`:**
- Keep only truly historical/reference files
- Move any still-relevant content to active docs
- Consider removing very old/completed migration guides

## Implementation Plan

### Step 0: Consolidate Optimization Files (Do First!)
1. Create `optimization/` directory structure
2. Move all optimization scripts (`scripts/optimize_*.py`, `scripts/optimization/*`)
3. Move all optimization docs (`docs/optimization/*`)
4. Move optimization config (`conf/slurm_optimized.config`)
5. Move optimization environment (`environment_optuna.yml`)
6. Move optimization test directories (`test/bowtie2_optimization_*`)
7. Create consolidated optimization README
8. Update references

**Result:** All optimization code in `optimization/` directory, ready for separate repo extraction.

### Step 1: Safe Deletions (No Breaking Changes)
1. Delete obsolete cleanup docs (CLEANUP_PLAN.md, etc.)
2. Delete one-time validation/summary docs
3. Delete warning documentation files
4. Move validation script or delete

### Step 2: Directory Cleanup
1. Remove entire `nextflow/` directory (after optimization consolidation)
2. Clean up test output directories (non-optimization ones)
3. Remove old reports

### Step 3: Documentation Consolidation
1. Consolidate setup docs into `docs/SETUP.md`
2. Move root-level docs to appropriate locations
3. Update all internal links

### Step 4: README Consolidation
1. Merge/update specialized READMEs
2. Update main README.md
3. Update docs/README.md index

### Step 5: Final Cleanup
1. Update .gitignore
2. Review and clean archive if needed
3. Update any broken links
4. Test that everything still works

## Expected Results

### Files to Delete: ~30-40 files
- Entire `nextflow/` directory (~15 files)
- Obsolete docs (~8 files)
- Test outputs (~10 files)
- Temporary reports (~5 files)

### Files to Move: ~5-8 files
- Root docs → `docs/`
- Scripts → appropriate locations

### Files to Consolidate: ~5-7 files
- Merge READMEs
- Consolidate setup guides
- Merge duplicate guides

### Final Structure:
- **1 main README** (comprehensive, well-organized)
- **1 docs index** (docs/README.md)
- **Consolidated setup guides**
- **No duplicate modules**
- **No obsolete directories**
- **Clean, organized structure**

## Verification

After cleanup:
1. All Nextflow workflows still work
2. All documentation is accessible
3. No broken links
4. Repository is ~30% smaller
5. Much easier to navigate

