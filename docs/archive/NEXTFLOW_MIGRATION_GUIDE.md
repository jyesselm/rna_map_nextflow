# Nextflow Migration Guide

## Overview

This guide outlines the migration of the RNA MAP pipeline from Dask-based orchestration to Nextflow, while maintaining backward compatibility for local testing and development.

## Migration Strategy

### Phase 1: Current State ✅
- Nextflow workflow exists in `nextflow/` directory
- Python functions (`run_mapping`, `generate_bit_vectors`) are functional and reusable
- Validated against original pipeline (identical results)

### Phase 2: Repository Restructure ✅
- CLI migrated to use Nextflow by default
- Backward compatibility maintained with `--use-legacy-pipeline` flag
- Documentation updated to reflect Nextflow usage
- Deprecation warnings added to legacy orchestrator
- Deprecation warnings added to Dask pipeline module
- Deprecation warnings added to `rna_map.run` module
- All deprecated code marked with warnings and documentation

### Phase 2: Repository Restructure

#### Keep (Essential for Functionality)
- **Python Package** (`rna_map/`):
  - Core modules: `mapping.py`, `bit_vector.py`, `sam.py`, etc.
  - Functional APIs: `rna_map.pipeline.functions`
  - Configuration: `rna_map.core.config`
  - Input/Output: `rna_map.core.inputs`, `rna_map.core.results`
  - All analysis and processing code

- **Tests** (`test/`):
  - Unit tests for core functionality
  - Integration tests for validation
  - Test resources

- **Documentation** (`docs/`):
  - All documentation files
  - Architecture docs

#### Migrate to Nextflow
- **CLI Orchestration**:
  - `rna-map` CLI → Nextflow single sample mode
  - `rna-map-pipeline` CLI → Nextflow batch mode
  - Keep CLI as thin wrapper that calls Nextflow

- **Dask Pipeline** (`rna_map/pipeline/dask_pipeline.py`):
  - Replace with Nextflow workflow
  - Keep for backward compatibility during transition

#### Remove/Deprecate
- **Class-based Orchestrators** (optional):
  - `rna_map/pipeline/orchestrator.py` - Can be deprecated
  - `rna_map/pipeline/mapper.py` - Still used by functions, keep
  - `rna_map/pipeline/bit_vector_generator.py` - Still used by functions, keep

## File Structure After Migration

```
rna_map/
├── nextflow/                    # Nextflow workflow (PRIMARY)
│   ├── main.nf                  # Main workflow
│   ├── nextflow.config          # Configuration
│   ├── environment.yml          # Conda environment
│   ├── setup_conda.sh           # Setup script
│   └── test_*.sh                # Test scripts
│
├── rna_map/                     # Python package (CORE)
│   ├── pipeline/
│   │   ├── functions.py         # ✅ Functional APIs (used by Nextflow)
│   │   ├── mapper.py            # ✅ Used by functions
│   │   ├── bit_vector_generator.py  # ✅ Used by functions
│   │   ├── simple_pipeline.py  # ⚠️ Keep for backward compat
│   │   └── dask_pipeline.py    # ⚠️ Deprecate (replace with Nextflow)
│   │
│   ├── cli/                     # CLI (THIN WRAPPER)
│   │   ├── cli.py               # Single sample → calls Nextflow
│   │   └── pipeline.py          # Batch → calls Nextflow
│   │
│   └── [other modules]          # ✅ All core functionality
│
├── test/                        # ✅ Tests
├── docs/                        # ✅ Documentation
└── README.md                    # Update to mention Nextflow
```

## Migration Steps

### Step 1: Move Nextflow to Root ✅

```bash
# Move nextflow directory to be more prominent
mv nextflow/ workflows/nextflow/
# Or keep as nextflow/ at root
```

**Status**: Nextflow directory is at root (`nextflow/`), which is appropriate.

### Step 2: Update CLI to Use Nextflow ✅

Modify `rna_map/cli/cli.py` to call Nextflow instead of direct Python:

```python
# OLD: Direct Python call
from rna_map.pipeline import run
run(fasta, fastq1, fastq2, dot_bracket, params)

# NEW: Call Nextflow
from rna_map.cli.nextflow_wrapper import run_single_sample
run_single_sample(fasta, fastq1, fastq2, dot_bracket, ...)
```

**Status**: ✅ Completed. CLI now uses Nextflow by default with full parameter support.

### Step 3: Update Pipeline CLI ✅

Modify `rna_map/cli/pipeline.py`:

```python
# OLD: Dask-based parallel execution
from rna_map.pipeline.dask_pipeline import run_samples_parallel
results = run_samples_parallel(samples, num_workers=100)

# NEW: Nextflow batch processing
from rna_map.cli.nextflow_wrapper import run_batch
run_batch(samples_csv, output_dir, ...)
```

**Status**: ✅ Completed. Pipeline CLI now uses Nextflow for batch processing.

### Step 4: Keep Backward Compatibility ✅

Add a flag to use old pipeline during transition:

```python
# In CLI
if args.get("use_legacy_pipeline"):
    # Use old orchestrator
    from rna_map.pipeline.orchestrator import run
    run(fasta, fastq1, fastq2, dot_bracket, params)
else:
    # Use Nextflow (default)
    from rna_map.cli.nextflow_wrapper import run_single_sample
    run_single_sample(...)
```

**Status**: ✅ Completed. `--use-legacy-pipeline` flag added to CLI with deprecation warning.

### Step 5: Update Tests ⚠️

Keep tests that validate core functionality, update integration tests:

```python
# Keep: Unit tests for functions
def test_run_mapping():
    result = run_mapping(...)
    assert result.sam_path.exists()

# Update: Integration tests use Nextflow
def test_nextflow_workflow():
    subprocess.run(["nextflow", "run", "nextflow/main.nf", ...])
    assert Path("results/sample1/summary.csv").exists()
```

**Status**: ⚠️ Partially complete. Existing integration tests still use legacy orchestrator for validation. These are kept for backward compatibility testing. New tests should use Nextflow.

## What to Keep for Local Testing

### Essential Files
1. **Python Package** - All of `rna_map/` (core functionality)
2. **Tests** - All of `test/` (validation)
3. **Test Resources** - `test/resources/` (test data)
4. **Nextflow Workflow** - `nextflow/` (orchestration)

### Minimal CLI (for backward compatibility)
- Keep `rna-map` CLI as wrapper
- Keep `rna-map-pipeline` CLI as wrapper
- Both call Nextflow under the hood

## Cluster Testing Guide

See `docs/CLUSTER_TESTING_GUIDE.md` for detailed cluster testing instructions.

